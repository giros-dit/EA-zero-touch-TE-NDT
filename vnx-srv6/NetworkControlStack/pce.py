#!/usr/bin/env python3
import json
import time
import os
import threading
import networkx as nx
import re
import subprocess
import boto3
import ipaddress
import hashlib
import traceback
from kafka import KafkaConsumer
from botocore.exceptions import ClientError
from botocore.config import Config
from acrosstc32_routing import RoutingEngine

# Parámetros globales
OCCUPANCY_LIMIT = float(os.environ.get('OCCUPANCY_LIMIT', '0.8'))
ROUTER_LIMIT = float(os.environ.get('ROUTER_LIMIT', '0.95'))
NODE_TIMEOUT = float(os.environ.get('NODE_TIMEOUT', '15'))
router_state = {}
state_lock = threading.Lock()
LOOP_PERIOD = float(os.environ.get('LOOP_PERIOD', '1'))

# Configuración MinIO/S3 desde variables de entorno
S3_ENDPOINT = os.environ.get('S3_ENDPOINT')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_BUCKET = os.environ.get('S3_BUCKET')

# Modo energía: True usa valor real, False fija a 0.1
ENERGYAWARE = os.environ.get('ENERGYAWARE', 'true').lower() == 'true'

# Flag para debug de costes
DEBUG_COSTS = os.environ.get('DEBUG_COSTS', 'false').lower() == 'true'

# Variable de entorno para medir tiempos
LOGTS = os.environ.get('LOGTS', 'false').lower() == 'true'

# Configurar boto3 para path-style (no virtual host)
s3_cfg = Config(
    signature_version='s3v4',
    s3={'addressing_style': 'path'}
)

print(f"[pce] Inicializando S3 client -> endpoint={S3_ENDPOINT!r}, bucket={S3_BUCKET!r}")
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=s3_cfg,
    region_name='local'
)

# Métricas de rendimiento
metrics = {
    "routes_recalculated": 0,
    "nodes_removed": 0,
    "nodes_restored": 0,
    "flows_updated": 0,
    "quick_validations": 0,
    "full_recalculations": 0,
    "flask_triggered_recalc": 0
}

# Variables para optimización de caché
last_flows_hash = None

# Event para sincronización con Flask API
recalc_event = threading.Event()

# Inicializar el motor de enrutamiento
routing_engine = RoutingEngine(
    occupancy_limit=OCCUPANCY_LIMIT,
    router_limit=ROUTER_LIMIT,
    energyaware=ENERGYAWARE,
    debug_costs=DEBUG_COSTS
)

def ensure_bucket_exists(bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"[pce] Bucket '{bucket_name}' OK.")
    except ClientError as e:
        print(f"[pce][ERROR] El bucket {bucket_name} no existe o no se puede acceder: {e}")

ensure_bucket_exists(S3_BUCKET)

def ensure_flows_folder_exists():
    try:
        resp = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="flows/")
        if 'Contents' not in resp or not resp['Contents']:
            initial = {"flows": [], "inactive_routers": []}
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key="flows/flows_initial.json",
                Body=json.dumps(initial, indent=4).encode()
            )
            print("[pce] flows/ creado e inicializado.")
        else:
            print("[pce] Ya existe al menos un fichero en flows/.")
    except Exception as e:
        print(f"[pce][ERROR] ensure_flows_folder_exists: {e}")

ensure_flows_folder_exists()

def create_graph():
    with open("networkinfo.json") as f:
        data = json.load(f)
    G = nx.DiGraph()
    for n in data["graph"]["nodes"]:
        G.add_node(n)
    for e in data["graph"]["edges"]:
        G.add_edge(e["source"], e["target"], cost=e["cost"])
    return G

def read_flows():
    try:
        resp = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="flows/")
        if 'Contents' not in resp or not resp['Contents']:
            return [], [], None
        latest_key = max(resp['Contents'], key=lambda o: o['LastModified'])['Key']
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=latest_key)
        flows_data = json.loads(obj['Body'].read().decode())
        if isinstance(flows_data, dict):
            return (flows_data.get("flows", []),
                    flows_data.get("inactive_routers", []),
                    latest_key)
        else:
            return flows_data, [], latest_key
    except Exception as e:
        print(f"[pce][ERROR] read_flows: {e}")
        return [], [], None

def write_flows(flows, inactive):
    payload = {"flows": flows,
               "inactive_routers": inactive}
    ts = time.strftime("%Y%m%d_%H%M%S")
    key = f"flows/flows_{ts}.json"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(payload, indent=4).encode()
        )
        print(f"[pce] write_flows: guardado {key}")
        print(f"[pce] Métricas: {metrics}")
    except Exception as e:
        print(f"[pce][ERROR] write_flows: {e}")

def calculate_flows_hash(flows, inactive_routers):
    """Calcula un hash robusto de los flujos y nodos inactivos.
    Distingue entre:
      - route inexistente
      - route vacía
      - route con hops
    """
    flows_repr = []
    for f in flows:
        # Distinguir route
        route = f.get('route', '__missing__')
        if isinstance(route, list) and len(route) == 0:
            route = '__empty__'
        
        flow_data = {
            '_id': f.get('_id'),
            'route': route,
            'version': f.get('version', 1)
        }
        flows_repr.append(flow_data)

    # Ordenar para consistencia
    flows_repr.sort(key=lambda x: x['_id'])
    inactive_routers_sorted = sorted(inactive_routers)

    combined_data = {
        'flows': flows_repr,
        'inactive_routers': inactive_routers_sorted
    }

    data_str = json.dumps(combined_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()


def remove_inactive_nodes(G, flows, inactive_routers):
    """
    1. Comprobar si algún nodo inactivo ha vuelto a funcionar
    2. Comprobar si algún nodo se ha caído
    3. Gestionar flujos: quitar ruta a los que pasen por nodos inactivos
    """
    now = time.time()
    modified = False
    
    with state_lock:
        # 1. Verificar si nodos inactivos han vuelto a estar activos
        nodes_to_restore = []
        for r in inactive_routers[:]:  # Copia para poder modificar durante iteración
            if r in router_state:
                d = router_state[r]
                age = now - d.get("ts", 0)
                if age <= NODE_TIMEOUT:  # El nodo ha vuelto a estar activo
                    nodes_to_restore.append(r)
                    metrics["nodes_restored"] += 1
                    print(f"[pce] El nodo {r} ha vuelto a estar activo")
        
        # Remover nodos restaurados de la lista de inactivos
        for r in nodes_to_restore:
            inactive_routers.remove(r)
            modified = True
        
        # 2. Verificar si hay nuevos nodos inactivos
        for r, d in list(router_state.items()):
            age = now - d.get("ts", 0)
            if age > NODE_TIMEOUT and r in G and r not in inactive_routers:
                G.remove_node(r)
                inactive_routers.append(r)
                modified = True
                metrics["nodes_removed"] += 1
                print(f"[pce] El nodo {r} se ha vuelto inactivo")
    
    # 3. Gestionar flujos: revisar todos los flujos cuya ruta contenga nodos inactivos
    if inactive_routers:  # Solo si hay nodos inactivos
        inactive_nodes_set = set(inactive_routers)
        print(f"[pce] Nodos inactivos actuales: {inactive_nodes_set}")
        
        for f in flows:
            if "route" in f:
                route = f["route"]
                # Verificar si la ruta pasa por algún nodo inactivo
                if any(node in inactive_nodes_set for node in route):
                    print(f"[pce] Flujo {f.get('_id', '???')} afectado: ruta {route} pasa por nodos inactivos")
                    f.pop("route", None)  # Eliminar ruta para forzar recálculo
                    routing_engine.increment_version(f)
                    modified = True
                    metrics["flows_updated"] += 1
    
    return G, flows, inactive_routers, modified

def process_flows_optimized(G, flows, inactive_routers, flows_filename, nodes_changed):
    """
    Versión ultra-optimizada del procesamiento de flujos
    Solo procesa si hay cambios en nodos o en el hash de flujos
    CORREGIDA: Ahora preserva TODOS los flujos, no solo los que procesa
    """
    global last_flows_hash
    
    current_hash = calculate_flows_hash(flows, inactive_routers)
    
    # Verificar si necesitamos procesar
    hash_changed = current_hash != last_flows_hash
    
    # Si no hay cambios en nodos Y el hash es el mismo, no hacer nada
    if not nodes_changed and not hash_changed:
        print("[pce] Optimización: Sin cambios detectados, saltando procesamiento completo")
        metrics["quick_validations"] += 1
        return flows, False
    
    # Hay cambios, procesar
    if nodes_changed:
        print("[pce] Procesando debido a cambios en nodos")
    if hash_changed:
        print("[pce] Procesando debido a cambios en flujos")
    
    print("[pce] Ejecutando recálculo completo de rutas de menor coste")
    metrics["full_recalculations"] += 1
    
    # Asignar costes y recalcular rutas usando algoritmo de Dijkstra
    G = routing_engine.assign_node_costs(G, router_state)
    
    # CRÍTICO: Procesar flows pero preservar TODOS los flujos
    processed_flows, processing_modified = routing_engine.recalculate_routes(G, flows, inactive_routers, router_state, metrics)
    
    # GARANTIZAR que todos los flujos se mantienen
    # (la función recalculate_routes ya debería hacer esto, pero vamos a verificarlo)
    
    # Debug: verificar que no se perdieron flujos
    original_ids = set(f.get('_id') for f in flows)
    processed_ids = set(f.get('_id') for f in processed_flows)
    
    if original_ids != processed_ids:
        print(f"[pce] ERROR: Se perdieron flujos!")
        print(f"[pce] Originales: {original_ids}")
        print(f"[pce] Procesados: {processed_ids}")
        print(f"[pce] Perdidos: {original_ids - processed_ids}")
        
        # Recuperar flujos perdidos
        lost_flow_ids = original_ids - processed_ids
        for flow in flows:
            if flow.get('_id') in lost_flow_ids:
                print(f"[pce] Recuperando flujo perdido: {flow.get('_id')}")
                processed_flows.append(flow)
    
    # Actualizar cache
    last_flows_hash = calculate_flows_hash(processed_flows, inactive_routers)
    
    return processed_flows, processing_modified


def kafka_consumer_thread(router_id):
    topic = f"ML_{router_id}"
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['kafka-service:9092'],
        auto_offset_reset='latest',
        value_deserializer=lambda m: json.loads(m.decode())
    )
    for msg in consumer:
        data = msg.value
        energy = None
        raw_out = next((m for m in data.get("output_ml_metrics", [])
                        if m.get("name") == "node_network_power_consumption_variation_rate_occupation"), None)
        if raw_out:
            val = raw_out.get("value")
            if isinstance(val, list) and val:
                val = val[0]
            try:
                energy = float(val) if ENERGYAWARE else 0.1
            except Exception:
                energy = None
        usage = None
        raw_in = next((m for m in data.get("input_ml_metrics", [])
                       if m.get("name") == "node_network_router_capacity_occupation"), None)
        if raw_in:
            val = raw_in.get("value")
            if isinstance(val, list) and val:
                val = val[0]
            try:
                usage = float(val)
            except Exception:
                usage = None
        
        try:
            ts = float(data.get("epoch_timestamp"))
        except Exception:
            ts = None

        if energy is not None or usage is not None or ts is not None:
            with state_lock:
                router_state[router_id] = {"energy": energy, "usage": usage, "ts": ts}

def start_kafka_consumers():
    with open("networkinfo.json") as f:
        nodes = json.load(f)["graph"]["nodes"]
    for n in nodes:
        if re.match(r"^r\d+$", n):
            t = threading.Thread(target=kafka_consumer_thread, args=(n,))
            t.daemon = True
            t.start()

def trigger_immediate_recalc():
    """Función para que la API de Flask pueda disparar un recálculo inmediato"""
    global last_flows_hash
    print("[pce] Recálculo inmediato solicitado por API Flask")
    last_flows_hash = None  # Invalidar cache
    metrics["flask_triggered_recalc"] += 1
    recalc_event.set()

# Hacer la función disponible globalmente para que app.py pueda importarla
def get_trigger_function():
    return trigger_immediate_recalc

def main():
    print("[pce] Iniciando PCE optimizado...")
    print(f"[pce] ENERGYAWARE: {ENERGYAWARE}")
    print(f"[pce] DEBUG_COSTS: {DEBUG_COSTS}")
    print(f"[pce] LOGTS: {LOGTS}") 
    print(f"[pce] OCCUPANCY_LIMIT: {OCCUPANCY_LIMIT}")
    print(f"[pce] ROUTER_LIMIT: {ROUTER_LIMIT}")
    print("[pce] Optimización ultra-eficiente: Solo procesa si hay cambios en nodos o flujos")
    
    start_kafka_consumers()
    
    while True:
    # Esperar evento o timeout
        if recalc_event.wait(timeout=LOOP_PERIOD):
            print("[pce] Evento de recálculo recibido")
            while recalc_event.is_set():
                recalc_event.clear()

        G = create_graph()
        flows, inactive_routers, flows_filename = read_flows()

        # Debug: Ver estado del hash antes de decidir
        current_hash = calculate_flows_hash(flows, inactive_routers)
        print(f"[pce] current_hash={current_hash} last_flows_hash={last_flows_hash}")

        # Procesar nodos inactivos
        G, flows, inactive_routers, nodes_modified = remove_inactive_nodes(G, flows, inactive_routers)

        # Procesar flujos con optimización ultra-eficiente
        flows, routes_modified = process_flows_optimized(G, flows, inactive_routers, flows_filename, nodes_modified)

        if nodes_modified or routes_modified:
            write_flows(flows, inactive_routers)



if __name__ == "__main__":
    main()
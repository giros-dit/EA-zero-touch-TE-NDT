import json
import time
import os
import threading
import networkx as nx
import re
import subprocess
from kafka import KafkaConsumer

# Parámetros globales
OCCUPANCY_LIMIT = 0.8
ROUTER_LIMIT = 0.95
NODE_TIMEOUT = 15  # Si el timestamp es mayor a 15 seg, se considera que el router está caído.
router_state = {}
state_lock = threading.Lock()  # Lock para proteger router_state

def create_graph():
    with open("final_output.json") as f:
        data = json.load(f)
    G = nx.DiGraph()
    # Se accede a los nodos y aristas dentro de "graph"
    for node in data["graph"]["nodes"]:
        G.add_node(node)
    for edge in data["graph"]["edges"]:
        G.add_edge(edge["source"], edge["target"], cost=edge["cost"])
    return G

def read_flows():
    try:
        with open("flows.json", "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "flows" in data:
                return data["flows"]
            elif isinstance(data, list):
                return data
            else:
                return []
    except Exception as e:
        print(f"[mynetworkx] read_flows: Error reading flows.json: {e}")
        return []

def write_flows(flows, inactive_routers):
    data_to_write = {
        "flows": flows,
        "inactive_routers": inactive_routers,
    }
    with open("flows.json", "w") as f:
        json.dump(data_to_write, f, indent=4)

def remove_inactive_nodes(G, flows):
    now = time.time()
    removed = []
    with state_lock:
        for r, data in router_state.items():
            if (now - data.get("ts", 0)) > NODE_TIMEOUT and r in G:
                G.remove_node(r)
                removed.append(r)
    if removed:
        print(f"[mynetworkx] remove_inactive_nodes: Removed inactive routers: {removed}")
        for f in flows:
            if "route" in f and any(r in f["route"] for r in removed):
                f.pop("route", None)
                f["version"] = f.get("version", 1) + 1
    return G, flows, removed


def assign_node_costs(G):
    now = time.time()
    with state_lock:
        for u, v in G.edges():
            if v in router_state and (now - router_state[v].get("ts", 0)) <= NODE_TIMEOUT:
                G[u][v]["cost"] = router_state[v].get("energy", 9999)
            else:
                G[u][v]["cost"] = 9999
    return G

def recalc_routes(G, flows, removed):
    for f in flows:
        route = f.get("route")
        if route and not any(r in route for r in removed):
            continue
        source, target = "ru", "rg"
        if not (G.has_node(source) and G.has_node(target)):
            continue

        with state_lock:
            excluded = [n for n, data in router_state.items() if data.get("usage", 0) >= OCCUPANCY_LIMIT]
            excluded_max = [n for n, data in router_state.items() if data.get("usage", 0) >= ROUTER_LIMIT]
        G2 = G.copy()
        G2.remove_nodes_from(excluded)
        G3 = G.copy()
        G3.remove_nodes_from(excluded_max)

        try:
            path = nx.shortest_path(G2, source, target, weight="cost")
        except Exception:
            print("No se encontró ruta en el subgrafo, intentando con G completo...")
            try:
                path = nx.shortest_path(G3, source, target, weight="cost")
                if path:
                    print(f"[mynetworkx] recalc_routes: Flow {f.get('_id', '???')} usage above {OCCUPANCY_LIMIT}")
            except Exception:
                print("WARNING: No se encontró ruta.")
                continue

        print(f"[mynetworkx] recalc_routes: Assigned route {path} to flow {f.get('_id')}")
        f["route"] = path
        
        # Llamada al script tunnelmaker cuando se asigna una nueva ruta.
        try:
            # Se asume que 'f' contiene '_id' (flow id) y 'version'. Ajusta estos nombres si es necesario.
            print(f"Ejecutando tunnelmaker para el flujo {f.get('_id')} con versión {f.get('version', 1)}, ruta: {json.dumps(path)}")
            # Se ejecuta el script tunnelmaker.py con los parámetros necesarios.
            cmd = [
                "python3",
                "tunnelmaker.py",
                str(f.get("_id")),
                str(f.get("version", 1)),
                json.dumps(path)
                ]
            print("Ejecutando comando:", " ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Imprime la salida (donde tunnelmaker genera el comando)
            print(result.stdout)
        except Exception as e:
            print(f"Error al llamar a tunnelmaker: {e}")
    return flows

def routing_algorithm_loop():
    while True:
        time.sleep(5)
        G = create_graph()
        flows = read_flows()
        G, flows, removed = remove_inactive_nodes(G, flows)
        G = assign_node_costs(G)
        flows = recalc_routes(G, flows, removed)
        write_flows(flows, removed)

def kafka_consumer_thread(router_id):
    topic = f"ML_{router_id}"
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['kafka-service:9092'],
        auto_offset_reset='latest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print(f"Conectado al topic {topic}")
    for message in consumer:
        data = message.value
        energy = None
        usage = None
        for metric in data.get("output_ml_metrics", []):
            if metric.get("name") == "node_network_power_consumption_variation_rate_occupation":
                try:
                    energy = float(metric.get("value", 0))
                except (ValueError, TypeError):
                    energy = 0
                break
        for metric in data.get("input_ml_metrics", []):
            if metric.get("name") == "node_network_router_capacity_occupation":
                try:
                    usage = float(metric.get("value", 0)) / 100.0
                except (ValueError, TypeError):
                    usage = 0
                break
        if energy is not None and usage is not None:
            with state_lock:
                router_state[router_id] = {
                    "energy": energy,
                    "usage": usage,
                    "ts": time.time()
                }

def start_kafka_consumers():
    with open("final_output.json", "r") as f:
        data = json.load(f)
    # Se accede a los nodos dentro de "graph"
    all_nodes = data["graph"]["nodes"]
    routers = [node for node in all_nodes if re.match(r"^r\d$", node)]
    threads = []
    for r in routers:
        t = threading.Thread(target=kafka_consumer_thread, args=(r,))
        t.daemon = True
        t.start()
        threads.append(t)
    return threads

def main():
    start_kafka_consumers()  # Inicia los consumidores de Kafka
    routing_algorithm_loop()   # Ejecuta el algoritmo de rutas en el hilo principal

if __name__ == "__main__":
    main()

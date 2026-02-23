import json
import time
import os
import subprocess
import networkx as nx

OCCUPANCY_LIMIT = 0.8
ROUTER_LIMIT = 0.95
NODE_TIMEOUT = 15 
router_state = {}

def create_graph():
    with open("networkx_graph.json") as f:
        data = json.load(f)

    G = nx.DiGraph()
    for node in data["nodes"]:
        G.add_node(node)
    for edge in data["edges"]:
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

def write_flows(flows, inactive_routers, router_utilization):
    data_to_write = {
        "flows": flows,
        "inactive_routers": inactive_routers,
        "router_utilization": router_utilization
    }
    with open("flows.json", "w") as f:
        json.dump(data_to_write, f, indent=4)

def remove_inactive_nodes(G, flows):
    now = time.time()
    removed = []
    # Se detectan los routers cuyo timestamp no se ha actualizado en NODE_TIMEOUT segundos.
    for r, data in router_state.items():
        if (now - data.get("ts", 0)) > NODE_TIMEOUT and r in G:
            G.remove_node(r)
            removed.append(r)
    if removed:
        print(f"[mynetworkx] remove_inactive_nodes: Removed inactive routers: {removed}")
        # Para cada flujo, si su ruta contiene un router caído, se elimina la ruta y se incrementa su versión.
        for f in flows:
            if "route" in f and any(r in f["route"] for r in removed):
                f.pop("route", None)
                f["version"] = f.get("version", 1) + 1
    return G, flows, removed

def read_routers_params():
    try:
        # Comprobar si routers.json existe y no está vacío para evitar error al parsear.
        if not os.path.exists("routers.json") or os.stat("routers.json").st_size == 0:
            print("[mynetworkx] read_routers_params: routers.json is empty or does not exist.")
            return
        with open("routers.json", "r") as f:
            data = json.load(f)
        # Se espera que 'data' sea una lista de diccionarios.
        for item in data:
            r = item.get("router")
            usage = item.get("usage", 0)
            energy = item.get("energy", 700)
            ts = item.get("ts", 0)
            if r:
                router_state[r] = router_state.get(r, {})
                router_state[r]["usage"] = usage
                router_state[r]["energy"] = energy
                router_state[r]["ts"] = ts
                print(f"[mynetworkx] read_routers_params: Router {r} usage={usage}, energy={energy}, ts={ts}")
    except Exception as e:
        print(f"[mynetworkx] read_routers_params: Error reading routers.json: {e}")

def assign_node_costs(G):
    now = time.time()
    for u, v in G.edges():
        if v in router_state and (now - router_state[v].get("ts", 0)) <= NODE_TIMEOUT:
            G[u][v]["cost"] = router_state[v].get("energy", 9999)
        else:
            G[u][v]["cost"] = 9999
        print(f"[mynetworkx] assign_node_costs: Cost from {u} to {v} = {G[u][v]['cost']}")
    return G

def recalc_routes(G, flows, removed):
    for f in flows:
        route = f.get("route")
        if route and not any(r in route for r in removed):
            continue
        source, target = "ru", "rg"
        if not (G.has_node(source) and G.has_node(target)):
            continue

        
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
            print(f"[mynetworkx]Ejecutando tunnelmaker para el flujo {f.get('_id')} con versión {f.get('version', 1)}, ruta: {path}")
            # Se ejecuta el script tunnelmaker.py con los parámetros necesarios.
            result = subprocess.run(
                ["python3", "tunnelmaker.py", str(f.get("_id")), str(f.get("version", 1)), json.dumps(path)],
                capture_output=True, text=True
            )
            # Imprime la salida (donde tunnelmaker genera el comando)
            print(result.stdout)
        except Exception as e:
            print(f"Error al llamar a tunnelmaker: {e}")
    return flows

def main():
    while True:
        time.sleep(5)
        read_routers_params()  # Actualiza el estado de los routers usando el timestamp.
        G = create_graph()
        flows = read_flows()
        G, flows, removed = remove_inactive_nodes(G, flows)
        G = assign_node_costs(G)
        flows = recalc_routes(G, flows, removed)
        # Se almacena la utilización actual de cada router.
        router_utilization = {r: router_state[r].get("usage", 0.0) for r in router_state}
        write_flows(flows, removed, router_utilization)

if __name__ == "__main__":
    main()
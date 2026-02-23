import networkx as nx
from pymongo import MongoClient
import sys
import os
import subprocess
import json
import time

def create_graph():
    G = nx.DiGraph()
    nodes = ["r1", "r2", "r3", "r4", "ru", "rg"]
    for node in nodes:
        G.add_node(node)
    
    edges = [
        ("r1", "rg"), ("rg", "r1"),
        ("r3", "rg"), ("rg", "r3"),
        ("r1", "r2"), ("r2", "r1"),
        ("r3", "r4"), ("r4", "r3"),
        ("r2", "ru"), ("ru", "r2"),
        ("r4", "ru"), ("ru", "r4")
    ]
    
    for edge in edges:
        G.add_edge(*edge, cost=0, capacity=0)
    
    return G

def fetch_energy():
    client = MongoClient("mongodb://mongo:27017/")
    db = client.across
    collection = db.energy
    energy_consumption = {}
    timestamp = {}
    
    for router in ["r1", "r2", "r3", "r4", "ru", "rg"]:
        document = collection.find_one({"router": router})
        energy_consumption[router] = document.get("consumption", 0) if document else 0
        timestamp[router] = document.get("timestamp", 0) if document else 0
    
    maxtimestamp = max(timestamp.values())
    for router in energy_consumption:
        if timestamp[router] < (maxtimestamp - 15):
            energy_consumption[router] = 0  # Apagar router temporalmente
    
    return energy_consumption

def assign_costs(G, energy_consumption):
    for u, v in G.edges():
        G[u][v]["cost"] = energy_consumption.get(v, 0)
    return G

def fetch_flows():
    client = MongoClient("mongodb://mongo:27017/")
    db = client.across
    collection = db.flows
    return list(collection.find())

def assign_routes(G, flows):
    client = MongoClient("mongodb://mongo:27017/")
    db = client.across
    collection = db.flows
    
    for flow in flows:
        if "route" not in flow or not flow["route"]:
            try:
                path = nx.shortest_path(G, source="ru", target="rg", weight="cost", method="dijkstra")
                collection.update_one({"_id": flow["_id"]}, {"$set": {"route": path}})
            except nx.NetworkXNoPath:
                print(f"No path found for flow {flow['_id']}")

def check_capacity(G, flows):
    link_usage = {edge: 0 for edge in G.edges()}
    
    for flow in flows:
        for i in range(len(flow["route"]) - 1):
            link_usage[(flow["route"][i], flow["route"][i + 1])] += flow["caudal"]
    
    for (u, v), usage in link_usage.items():
        capacity = 100  # Mbps
        if usage > capacity * 0.8:
            print(f"Link {u}-{v} is over 80% capacity, pruning edge.")
            G.remove_edge(u, v)
            G.remove_edge(v, u)
        if usage > capacity:
            print(f"ALERT: Link {u}-{v} is 100% full, redirecting to least energy-consuming path.")
            G.add_edge(u, v, cost=10000)  # Penalizar alto costo energético
    
    return G

def main():
    vlan = int(sys.argv[1]) if len(sys.argv) == 2 else 1
    
    while True:
        print("Updating network state...")
        G = create_graph()
        energy_consumption = fetch_energy()
        G = assign_costs(G, energy_consumption)
        
        flows = fetch_flows()
        G = check_capacity(G, flows)
        assign_routes(G, flows)
        
        time.sleep(5)  # Esperar antes de la siguiente iteración

if __name__ == "__main__":
    main()

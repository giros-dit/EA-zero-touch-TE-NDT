import networkx as nx
import ipaddress
import json
import subprocess
import threading
import time
import os
from typing import List, Dict, Tuple, Optional, Any

class RoutingEngine:
    def __init__(self, occupancy_limit: float = 0.8, router_limit: float = 0.95, 
                 energyaware: bool = True, debug_costs: bool = False):
        self.occupancy_limit = occupancy_limit
        self.router_limit = router_limit
        self.energyaware = energyaware
        self.debug_costs = debug_costs
        self.state_lock = threading.Lock()
        self.logts = os.environ.get('LOGTS', 'false').lower() == 'true'
        
    def assign_node_costs(self, G: nx.DiGraph, router_state: Dict[str, Any]) -> nx.DiGraph:
        """Asigna costes a los nodos del grafo basado en el estado de los routers"""
        with self.state_lock:
            for u, v in G.edges():
                entry = router_state.get(v)
                if entry:
                    cost = entry.get("energy") if self.energyaware else 0.1
                else:
                    cost = 9999
                G[u][v]["cost"] = cost
        return G
    
    def choose_destination(self, dest_ip: str) -> str:
        """Determina el nodo destino basado en la IP"""
        addr = ipaddress.IPv6Address(dest_ip.split('/')[0])
        if addr in ipaddress.IPv6Network('fd00:0:2::/64'):
            return 'rg'
        if addr in ipaddress.IPv6Network('fd00:0:3::/64'):
            return 'rc'
        raise ValueError(f"Dirección IP de destino {dest_ip} no pertenece a ninguna red conocida")
    
    def is_route_valid(self, G: nx.DiGraph, route: List[str]) -> bool:
        """Verifica si una ruta sigue siendo válida en el grafo actual"""
        if not route or len(route) < 2:
            return False
        for i in range(len(route) - 1):
            if not G.has_edge(route[i], route[i + 1]):
                return False
        return True
    
    def increment_version(self, flow: Dict[str, Any]) -> int:
        """Incrementa la versión de un flujo de manera consistente"""
        flow["version"] = flow.get("version", 1) + 1
        return flow["version"]
    
    def add_timestamp_to_flow(self, flow: Dict[str, Any], event_type: str, counter: int = 1) -> None:
        """Añade timestamp al flujo si LOGTS está habilitado"""
        if not self.logts:
            return
        
        timestamp = time.time()
        base_key = f"ts_{event_type}"
        
        if counter > 1:
            key = f"{base_key}_{counter}"
        else:
            key = base_key
        
        if "timestamps" not in flow:
            flow["timestamps"] = {}
        
        flow["timestamps"][key] = timestamp
        print(f"[routing] Timestamp añadido: {key} = {timestamp} para flujo {flow.get('_id', '???')}")

    def get_next_counter_for_event(self, flow: Dict[str, Any], event_type: str) -> int:
        """Obtiene el siguiente contador para un tipo de evento"""
        if not self.logts or "timestamps" not in flow:
            return 1
        
        base_key = f"ts_{event_type}"
        existing_keys = [k for k in flow["timestamps"].keys() if k.startswith(base_key)]
        
        if not existing_keys:
            return 1
        
        # Encontrar el contador más alto
        max_counter = 1
        for key in existing_keys:
            if key == base_key:
                max_counter = max(max_counter, 1)
            elif key.startswith(f"{base_key}_"):
                try:
                    counter = int(key.split("_")[-1])
                    max_counter = max(max_counter, counter)
                except ValueError:
                    continue
        
        return max_counter + 1
    
    def calculate_lowest_cost_path(self, G: nx.DiGraph, source: str, target: str, 
                              router_state: Dict[str, Any]) -> Tuple[Optional[List[str]], bool]:
        """
        Calcula la ruta de menor coste total usando Dijkstra
        Retorna: (ruta, usando_alta_ocupacion)
        """
        # Lógica de umbrales para evitar nodos congestionados
        with self.state_lock:
            excluded = [n for n, data in router_state.items() 
                       if data.get("usage", 0) >= self.occupancy_limit]
            excluded_max = [n for n, data in router_state.items() 
                           if data.get("usage", 0) >= self.router_limit]
        
        # Crear subgrafos excluyendo nodos congestionados
        G2 = G.copy()
        G2.remove_nodes_from(excluded)
        
        G3 = G.copy()
        G3.remove_nodes_from(excluded_max)
        
        # Flag para indicar si estamos usando la ruta con nodos de ocupación entre límites
        using_high_occupancy = False
        
        # Intentar primero con el subgrafo más restrictivo
        try:
            path = nx.shortest_path(G2, source, target, weight="cost")
            total_cost = nx.shortest_path_length(G2, source, target, weight="cost")
            print(f"[routing] Ruta de menor coste encontrada: {path} (coste total: {total_cost:.4f})")
        except nx.NetworkXNoPath:
            print(f"[routing] No se encontró ruta en subgrafo con límite {self.occupancy_limit}, "
                  f"intentando con límite {self.router_limit}...")
            # Intentar con el segundo subgrafo menos restrictivo
            try:
                path = nx.shortest_path(G3, source, target, weight="cost")
                total_cost = nx.shortest_path_length(G3, source, target, weight="cost")
                if path:
                    using_high_occupancy = True
                    print(f"[routing] AVISO: Ruta usa nodos de ocupación entre "
                          f"{self.occupancy_limit} y {self.router_limit}")
                    print(f"[routing] Ruta de menor coste: {path} (coste total: {total_cost:.4f})")
            except nx.NetworkXNoPath:
                print(f"[routing] WARNING: No se encontró ruta de {source} a {target}")
                return None, False
        
        return path, using_high_occupancy
    
    def debug_route_costs(self, G: nx.DiGraph, path: List[str]) -> None:
        """Imprime información de debug sobre costes de la ruta"""
        if not self.debug_costs:
            return
            
        print("[routing] Costes de todos los enlaces en la red:")
        for u, v, data in G.edges(data=True):
            print(f"  {u} -> {v}: {data.get('cost')}")
        
        if path and len(path) > 1:
            costs = [G[u][v]["cost"] for u, v in zip(path, path[1:])]
            total_cost = sum(costs)
            print(f"[routing] Ruta seleccionada: {path}")
            print(f"[routing] Costes por enlace: {costs}")
            print(f"[routing] Coste total de la ruta: {total_cost:.4f}")
            print(f"[routing] Número de saltos: {len(path) - 1}")
    
    def execute_src_command(self, flow_id: str, path: List[str], 
                           needs_replace: bool = False, using_high_occupancy: bool = False,
                           flow_ref: Optional[Dict[str, Any]] = None) -> bool:
        """Ejecuta el comando src.py para instalar la ruta"""
        """Ejecuta el comando src.py para instalar la ruta"""
        cmd = [
            "python3", "/app/src.py",
            flow_id, json.dumps(path)
        ]
        
        # Agregar flag si ya existía una ruta (necesita replace)
        if needs_replace:
            cmd.append("--replace")
        
        # Agregar flag si estamos usando rutas con alta ocupación
        if using_high_occupancy:
            cmd.append("--high-occupancy")
        
        print(f"[routing] Ejecutando comando: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)       
            # Añadir timestamp de ejecución SSH si el comando fue exitoso
            if result.returncode == 0 and flow_ref and self.logts:
                counter = self.get_next_counter_for_event(flow_ref, "ssh_executed")
                self.add_timestamp_to_flow(flow_ref, "ssh_executed", counter)
                
                # Intentar extraer timestamp más preciso del output de src.py
                try:
                    import re
                    timestamp_match = re.search(r'ssh_success:\s*([0-9.]+)', result.stdout)
                    if timestamp_match:
                        precise_timestamp = float(timestamp_match.group(1))
                        
                        # Actualizar con timestamp más preciso
                        base_key = f"ts_ssh_executed"
                        if counter > 1:
                            key = f"{base_key}_{counter}"
                        else:
                            key = base_key
                        
                        flow_ref["timestamps"][key] = precise_timestamp
                        print(f"[routing] Timestamp SSH preciso: {key} = {precise_timestamp}")
                except (ValueError, KeyError):
                    pass  # Usar el timestamp normal si no se puede parsear
            
            if result.returncode != 0:
                print(f"[routing] Error ejecutando src.py: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"[routing] Excepción ejecutando src.py: {e}")
            return False
    
    def recalculate_routes(self, G: nx.DiGraph, flows: List[Dict[str, Any]], 
                      inactive_routers: List[str], router_state: Dict[str, Any],
                      metrics: Dict[str, int]) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Recalcula las rutas para todos los flujos que lo necesiten
        CORREGIDA: Ahora preserva TODOS los flujos, incluso los que no necesitan recálculo
        """
        modified = False
        
        # IMPORTANTE: Trabajar con una copia de la lista para preservar todos los flujos
        result_flows = flows.copy()  # Preservar TODOS los flujos
        
        # Debug de costes solo si está habilitado
        if self.debug_costs:
            print("[routing] Costes de todos los enlaces en la red:")
            for u, v, data in G.edges(data=True):
                print(f"  {u} -> {v}: {data.get('cost')}")
        
        for i, f in enumerate(result_flows):
            # Verificar si necesita recálculo
            current_route = f.get("route")
            needs_recalc = False
            
            if current_route:
                if not self.is_route_valid(G, current_route):
                    needs_recalc = True
                    print(f"[routing] Flujo {f.get('_id', '???')} necesita recálculo: "
                        f"ruta inválida {current_route}")
            else:
                needs_recalc = True
                print(f"[routing] Flujo {f.get('_id', '???')} necesita recálculo: sin ruta")
            
            # Si NO necesita recálculo, MANTENER el flujo como está
            if not needs_recalc:
                print(f"[routing] Flujo {f.get('_id', '???')} OK, manteniendo ruta actual: {current_route}")
                continue
            
            # Determinar nodos origen y destino
            try:
                source = "ru"
                target = self.choose_destination(f["_id"])
            except ValueError as e:
                print(f"[routing] Error determinando destino para {f.get('_id', '???')}: {e}")
                continue
                
            if not (G.has_node(source) and G.has_node(target)):
                print(f"[routing] Nodos {source} o {target} no disponibles en el grafo")
                continue
            
            # Calcular nueva ruta
            path, using_high_occupancy = self.calculate_lowest_cost_path(G, source, target, router_state)
            
            if path is None:
                print(f"[routing] No se pudo calcular ruta de menor coste para flujo {f.get('_id', '???')}")
                continue
            
            # Debug de ruta seleccionada
            self.debug_route_costs(G, path)
            
            print(f"[routing] Flujo {f.get('_id', '???')}: ruta de menor coste calculada {path}")
            
            # Añadir timestamp de cuando se asigna nueva ruta
            if self.logts:
                counter = self.get_next_counter_for_event(f, "route_assigned")
                self.add_timestamp_to_flow(f, "route_assigned", counter)
            
            # Determinar si necesitamos usar replace
            needs_replace = f.get("version", 1) > 1
            
            # Actualizar flujo con nueva ruta (MODIFICAR en su lugar)
            result_flows[i].update({"route": path})
            self.increment_version(result_flows[i])
            modified = True
            metrics["routes_recalculated"] += 1
            metrics["flows_updated"] += 1
            
            # Ejecutar comando src.py (pasando referencia al flujo para timestamps)
            success = self.execute_src_command(f["_id"], path, needs_replace, using_high_occupancy, result_flows[i])
            if not success:
                print(f"[routing] Error instalando ruta para flujo {f.get('_id', '???')}")
        
        # Debug final: verificar que no se perdieron flujos
        original_count = len(flows)
        result_count = len(result_flows)
        
        if original_count != result_count:
            print(f"[routing] ERROR: Se perdieron flujos! Original: {original_count}, Resultado: {result_count}")
            print(f"[routing] IDs originales: {[f.get('_id') for f in flows]}")
            print(f"[routing] IDs resultado: {[f.get('_id') for f in result_flows]}")
        else:
            print(f"[routing] Todos los flujos preservados: {result_count} flujos")
        
        return result_flows, modified
    
    def quick_validation_check(self, G: nx.DiGraph, flows: List[Dict[str, Any]], 
                              inactive_routers: List[str]) -> bool:
        """
        NOTA: Esta función ya no se usa en la versión ultra-optimizada
        Validación rápida: verifica si todas las rutas son válidas y no pasan por nodos inactivos
        Retorna True si todas las rutas son válidas, False si alguna necesita recálculo
        """
        inactive_nodes_set = set(inactive_routers)
        
        for f in flows:
            route = f.get("route")
            if not route:
                print(f"[routing] Validación rápida: Flujo {f.get('_id', '???')} sin ruta")
                return False
            
            # Verificar si la ruta es válida en el grafo
            if not self.is_route_valid(G, route):
                print(f"[routing] Validación rápida: Flujo {f.get('_id', '???')} con ruta inválida")
                return False
            
            # Verificar si la ruta pasa por nodos inactivos
            if any(node in inactive_nodes_set for node in route):
                print(f"[routing] Validación rápida: Flujo {f.get('_id', '???')} "
                      f"pasa por nodos inactivos")
                return False
        
        print("[routing] Validación rápida: Todas las rutas son válidas")
        return True
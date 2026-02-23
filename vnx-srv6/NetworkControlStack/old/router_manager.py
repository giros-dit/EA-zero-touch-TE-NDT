import json
import time
import threading
import os

router_state = {}  # Ej. {"r1": {"usage": 0.0, "energy": 5, "ts": 0.0}}
paused_routers = set()

def read_routers():
    try:
        with open("routers.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_routers(data):
    with open("routers.json", "w") as f:
        json.dump(data, f, indent=4)

def update_router_state():
    while True:
        for router, state in router_state.items():
            if router in paused_routers:
                # Saltar actualización de routers pausados
                continue
            usage = state.get("usage", 0.0)
            # Para r1 y r2: si el uso es menor al 10% la energía es 5, si es mayor al 10% es 0.1
            if router in ["r1", "r2"]:
                energy = 5 if usage < 0.1 else 0.1
            # Para r3 y r4: energía constante de 1
            elif router in ["r3", "r4"]:
                energy = 1
            else:
                # Por defecto se mantiene el valor actual
                energy = state.get("energy", 0)
            router_state[router]["energy"] = energy
            router_state[router]["ts"] = time.time()
        write_routers([
            {
                "router": r,
                "usage": s["usage"],
                "energy": s["energy"],
                "ts": s["ts"]
            }
            for r, s in router_state.items()
        ])
        time.sleep(5)

def handle_user_input():
    while True:
        try:
            user_input = input("Ingrese comando (Ej: '1 21' para establecer uso, 'p 1' para pausar, 't 1' para reactivar, 'q' para salir): ").strip()
            if user_input == 'q':
                if os.path.exists("routers.json"):
                    os.remove("routers.json")
                print("Saliendo...")
                break
            elif user_input.startswith("p "):
                parts = user_input.split()
                if len(parts) >= 2:
                    router_key = f"r{parts[1]}"
                    paused_routers.add(router_key)
                    print(f"Router {router_key} pausado.")
            elif user_input.startswith("t "):
                parts = user_input.split()
                if len(parts) >= 2:
                    router_key = f"r{parts[1]}"
                    paused_routers.discard(router_key)
                    print(f"Router {router_key} reactivado.")
            else:
                parts = user_input.split()
                if len(parts) == 2:
                    router_id = parts[0]
                    try:
                        usage_val = float(parts[1]) / 100.0
                    except ValueError:
                        print("Error: El segundo valor debe ser numérico.")
                        continue
                    router_key = f"r{router_id}"
                    if router_key not in router_state:
                        # Inicialización por defecto: para r1 y r2 energía 5, para r3 y r4 energía 1
                        if router_key in ["r1", "r2"]:
                            router_state[router_key] = {"usage": 0.0, "energy": 5, "ts": time.time()}
                        elif router_key in ["r3", "r4"]:
                            router_state[router_key] = {"usage": 0.0, "energy": 1, "ts": time.time()}
                        else:
                            router_state[router_key] = {"usage": 0.0, "energy": 0, "ts": time.time()}
                    router_state[router_key]["usage"] = usage_val
                    router_state[router_key]["ts"] = time.time()
                    print(f"Router {router_key} uso establecido a {usage_val}.")
                else:
                    print("Comando no reconocido.")
        except Exception as e:
            print(f"Error al procesar la entrada: {e}")

def main():
    # Inicializar estado de los routers: r1 y r2 con energía 5; r3 y r4 con energía 1
    for i in range(1, 5):  # r1, r2, r3, r4
        if i < 3:
            router_state[f"r{i}"] = {"usage": 0.0, "energy": 5, "ts": time.time()}
        else:
            router_state[f"r{i}"] = {"usage": 0.0, "energy": 1, "ts": time.time()}

    # Leer estado inicial desde routers.json si existe
    initial_data = read_routers()
    for item in initial_data:
        router = item.get("router")
        usage = item.get("usage", 0.0)
        if router in ["r1", "r2"]:
            energy = 5 if usage < 0.1 else 0.1
        elif router in ["r3", "r4"]:
            energy = 1
        else:
            energy = item.get("energy", 0)
        if router:
            router_state[router] = {"usage": usage, "energy": energy, "ts": time.time()}

    # Iniciar hilos para actualizar estado y manejar entrada del usuario
    threading.Thread(target=update_router_state, daemon=True).start()
    handle_user_input()

if __name__ == "__main__":
    main()

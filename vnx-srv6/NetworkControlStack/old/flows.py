import json
import sys
import os

def read_flows():
    try:
        if not os.path.exists("flows.json"):
            raise FileNotFoundError("flows.json does not exist.")
        with open("flows.json", "r") as f:
            content = f.read().strip()  # Read and strip whitespace
            if not content:  # Check if the file is empty
                return []
            data = json.loads(content)  # Parse JSON content
            # Handle SAVE_INFO structure if present
            if isinstance(data, dict) and "flows" in data:
                data = data["flows"]
            # Validate that the data is a list of dictionaries
            if not isinstance(data, list) or not all(isinstance(flow, dict) for flow in data):
                raise ValueError("Invalid flows data: Expected a list of dictionaries.")
            return data
    except FileNotFoundError:
        print("[flows] read_flows: flows.json does not exist.")
        return []
    except Exception as e:
        print(f"[flows] read_flows: Error reading flows.json: {e}")
        raise

def write_flows(flows, inactive_routers=None, router_utilization=None):
    try:
        with open("flows.json", "w") as f:
            json.dump({
                "flows": flows,
                "inactive_routers": inactive_routers or [],
                "router_utilization": router_utilization or {}
            }, f, indent=4)
    except Exception as e:
        print(f"[flows] write_flows: Error writing flows.json: {e}")

def main():
    if len(sys.argv) != 2:
        print("Uso: flows.py <id>")
        sys.exit(1)

    flow_id = sys.argv[1]
    try:
        flows = read_flows()

        # Buscar si el flujo ya existe
        existing_flow = next((f for f in flows if f.get("_id") == flow_id), None)

        if existing_flow:
            # Si existe, eliminarlo
            flows = [f for f in flows if f.get("_id") != flow_id]
            print(f"Flujo con ID {flow_id} eliminado.")
        else:
            # Si no existe, agregarlo con versión 1
            new_flow = {"_id": flow_id, "version": 1}
            flows.append(new_flow)
            print(f"Flujo con ID {flow_id} añadido con versión 1.")

        write_flows(flows)
    except Exception as e:
        print(f"[flows] main: Error processing flows: {e}")
        raise

if __name__ == "__main__":
    main()

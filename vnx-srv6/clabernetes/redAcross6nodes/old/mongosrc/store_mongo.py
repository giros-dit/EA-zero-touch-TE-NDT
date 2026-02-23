import pymongo
import sys

def main():
    def menu():
        while True:
            option = input("Seleccione una opción (v: Flows, e: Energía, q: Salir): ").lower()
            if option == 'v':
                handle_flow()
            elif option == 'e':
                handle_energy()
            elif option == 'q':
                print("Saliendo del programa.")
                sys.exit(0)
            else:
                print("Opción no válida. Intente de nuevo.")

    def handle_flow():
        client = pymongo.MongoClient("mongodb://mongo:27017/")
        db = client["across"]
        flows_col = db["flows"]

        flow_id = input("Ingrese el identificador del flujo: ").strip()
        try:
            caudal = float(input("Ingrese el caudal del flujo (en Mbps): "))
        except ValueError:
            print("El caudal debe ser un número.")
            return

        # Se guarda el flujo únicamente con id y caudal.
        flow_doc = {"_id": flow_id, "caudal": caudal}

        try:
            flows_col.insert_one(flow_doc)
            print("Flujo insertado correctamente:")
            print(flow_doc)
        except Exception as e:
            print("Error al insertar el flujo:", e)

    def handle_energy():
        client = pymongo.MongoClient("mongodb://mongo:27017/")
        db = client["across"]
        energy_col = db["energy"]

        routers = ['r1', 'r2', 'r3', 'r4']

        for router in routers:
            try:
                consumption = float(input(f"Ingrese el consumo de energía para el router {router}: "))
            except ValueError:
                print(f"El consumo de energía para el router {router} debe ser un número.")
                continue

            existing_energy = energy_col.find_one({"router": router})
            if existing_energy:
                energy_col.update_one(
                    {"router": router},
                    {"$set": {"consumption": consumption}}
                )
                print(f"Actualizado consumo de energía para el router {router}")
            else:
                energy_document = {
                    "router": router,
                    "consumption": consumption
                }
                energy_col.insert_one(energy_document)
                print(f"Insertado documento de consumo de energía para el router {router}")

    menu()

if __name__ == "__main__":
    main()

import pandas as pd
from tabulate import tabulate 

df1 = pd.read_csv("latency-test-r1-stress.csv").astype(float)
#df2 = pd.read_csv("latency-test-r2.csv").astype(float)
#df3 = pd.read_csv("latency-test-r3.csv").astype(float)
df4 = pd.read_csv("latency-test-r4-stress.csv").astype(float)

#routers = [df1, df2, df3, df4]
routers = [df1, df4]

#router_names = ["R1", "R2", "R3", "R4"]
router_names = ["R1", "R4"]

for df in routers:
    df["latency_epoch_collector"] = df["collector_timestamp"] - df["epoch_timestamp"]
    df["latency_collector_process"] = df["process_timestamp"] - df["collector_timestamp"]
    df["latency_process_ml"] = df["ml_timestamp"] - df["process_timestamp"]
    df["latency_total"] = df["ml_timestamp"] - df["epoch_timestamp"]

for i, df in enumerate(routers):
    print(f"\n--- {router_names[i]} ---")
    print("Latencia media epoch → collector:", df["latency_epoch_collector"].mean())
    print("Latencia media collector → process:", df["latency_collector_process"].mean())
    print("Latencia media process → ml:", df["latency_process_ml"].mean())
    print("Latencia total media:", df["latency_total"].mean())

tabla = []
for i, df in enumerate(routers):
    fila = [
        router_names[i],
        df["latency_epoch_collector"].mean() * 1000,
        df["latency_collector_process"].mean() * 1000,
        df["latency_process_ml"].mean() * 1000,
        df["latency_total"].mean() * 1000,
    ]
    tabla.append(fila)

all_data = pd.concat(routers)

print("\n=== Latencias globales ===")
print("Latencia media epoch → collector:", all_data["latency_epoch_collector"].mean())
print("Latencia media collector → process:", all_data["latency_collector_process"].mean())
print("Latencia media process → ml:", all_data["latency_process_ml"].mean())
print("Latencia total media:", all_data["latency_total"].mean())

tabla.append([
    "GLOBAL",
    all_data["latency_epoch_collector"].mean() * 1000,
    all_data["latency_collector_process"].mean() * 1000,
    all_data["latency_process_ml"].mean() * 1000,
    all_data["latency_total"].mean() * 1000
])

headers = ["Router", "Epoch→Collector(ms)", "Collector→Process(ms)", "Process→ML(ms)", "Total(ms)"]
tabla_str = tabulate(tabla, headers=headers, tablefmt="grid")
print(tabla_str)

#with open("latency_results_stress.txt", "w") as f:
#    f.write(tabla_str)

df_result = pd.DataFrame(tabla, columns=headers)
df_result.to_csv("latency_results_stress.csv", index=False)
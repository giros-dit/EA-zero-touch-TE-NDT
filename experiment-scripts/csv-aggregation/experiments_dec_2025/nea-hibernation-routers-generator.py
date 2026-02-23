import pandas as pd

input_file = "no-energy-aware-3-processed.csv"
output_file = "no-energy-aware-3-processed-with-standby-routers.csv"

# Routers que estarán en standby
standby_routers = ["r1", "r4", "r5", "r7", "r8"]

df = pd.read_csv(input_file)

required_columns = ["router_id", "power_consumption_watts"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"La columna '{col}' no existe en el dataset.")

# Establecer en 0 el consumo de los routers en standby
df.loc[df["router_id"].isin(standby_routers), "power_consumption_watts"] = 0.0

df.to_csv(output_file, index=False)
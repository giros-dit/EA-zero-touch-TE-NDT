import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

selected_router_ids = ["r1", "r2", "r3", "r4", "r7"]

# Dataset Energy-Aware
df_ea = pd.read_csv('energy-aware-3-processed-with-standby-routers.csv')
df_ea = df_ea[df_ea['router_id'].isin(selected_router_ids)]
df_ea.to_csv("datasets-with-selected-routers/energy-aware-3-processed-with-selected-routers.csv", index=False)

# Agrupar por router_id y luego por bloques de 12 filas dentro de cada router
df_ea_grouped = (
    df_ea.groupby('router_id', group_keys=False)
        .apply(
            lambda g: g['power_consumption_watts']
                .reset_index(drop=True)    # Reiniciar el índice para que vaya de 0 a n dentro de cada grupo
                .iloc[:len(g) // 12 * 12]  # Asegura que el número de filas sea múltiplo de 12
                .groupby(lambda x: x // 12)
                .mean()
                .reset_index(drop=True)
                .iloc[:24] 
        )
        .reset_index()
)

# Renombrar columnas numéricas
new_cols = ['router_id'] + [f"{i}" for i in range(1, len(df_ea_grouped.columns))]

df_ea_grouped.columns = new_cols

print("Energy comsumption per hour and router (EA)")
print(df_ea_grouped)
df_ea_grouped.to_csv("datasets-with-selected-routers/power_means_per_router_energy-aware.csv", index=False)

# Calcular la suma total por hora
df_ea_sum = pd.DataFrame(df_ea_grouped.drop(columns='router_id').sum()).T  # Transpuesta para fila única

print("Total energy comsumption per hour (EA)")
print(df_ea_sum)
df_ea_sum.to_csv("datasets-with-selected-routers/power_means_energy-aware.csv", index=False)

# Calcular el promedio de las 24 horas para cada router
hour_columns = [str(i) for i in range(1, 25)]

df_ea_avg_per_router = pd.DataFrame({
    "router_id": df_ea_grouped["router_id"],
    "power_avg": df_ea_grouped[hour_columns].mean(axis=1)
})

print("Average energy energy comsumption per hour during a day (EA)")
print(df_ea_avg_per_router)
df_ea_avg_per_router.to_csv("datasets-with-selected-routers/power_means_per_router_24h_avg_energy-aware.csv", index=False)

df_ea_sum_per_router = pd.DataFrame({
    "router_id": df_ea_grouped["router_id"],
    "power_sum": df_ea_grouped[hour_columns].sum(axis=1)
})

print("Sum of energy energy comsumption per hour during a day (EA)")
print(df_ea_sum_per_router)
df_ea_sum_per_router.to_csv("datasets-with-selected-routers/power_means_per_router_24h_sum_energy-aware.csv", index=False)

# Dataset No-Energy-Aware
df_nea = pd.read_csv('no-energy-aware-3-processed-with-standby-routers.csv')
df_nea = df_nea[df_nea['router_id'].isin(selected_router_ids)]
df_nea.to_csv("datasets-with-selected-routers/no-energy-aware-3-processed-with-selected-routers.csv", index=False)

# Agrupar por router_id y luego por bloques de 12 filas dentro de cada router
df_nea_grouped = (
    df_nea.groupby('router_id', group_keys=False)
        .apply(
            lambda g: g['power_consumption_watts']
                .reset_index(drop=True)    # Reiniciar el índice para que vaya de 0 a n dentro de cada grupo
                .iloc[:len(g) // 12 * 12]  # Asegura que el número de filas sea múltiplo de 12
                .groupby(lambda x: x // 12)
                .mean()
                .reset_index(drop=True)
                .iloc[:24] 
        )
        .reset_index()
)

# Renombrar columnas numéricas
new_cols = ['router_id'] + [f"{i}" for i in range(1, len(df_nea_grouped.columns))]

df_nea_grouped.columns = new_cols

print("Energy comsumption per hour and router (Non-EA)")
print(df_nea_grouped)
df_nea_grouped.to_csv("datasets-with-selected-routers/power_means_per_router_no-energy-aware.csv", index=False)

# Calcular la suma total por hora
df_nea_sum = pd.DataFrame(df_nea_grouped.drop(columns='router_id').sum()).T  # Transpuesta para fila única

print("Total energy comsumption per hour (Non-EA)")
print(df_nea_sum)
df_nea_sum.to_csv("datasets-with-selected-routers/power_means_no-energy-aware.csv", index=False)

# Calcular el promedio de las 24 horas para cada router
hour_columns = [str(i) for i in range(1, 25)]

df_nea_avg_per_router = pd.DataFrame({
    "router_id": df_nea_grouped["router_id"],
    "power_avg": df_nea_grouped[hour_columns].mean(axis=1)
})

print("Average energy energy comsumption per hour during a day (Non-EA)")
print(df_nea_avg_per_router)
df_nea_avg_per_router.to_csv("datasets-with-selected-routers/power_means_per_router_24h_avg_no-energy-aware.csv", index=False)

df_nea_sum_per_router = pd.DataFrame({
    "router_id": df_nea_grouped["router_id"],
    "power_sum": df_nea_grouped[hour_columns].sum(axis=1)
})

print("Sum of energy energy comsumption per hour during a day (Non-EA)")
print(df_nea_sum_per_router)
df_nea_sum_per_router.to_csv("datasets-with-selected-routers/power_means_per_router_24h_sum_no-energy-aware.csv", index=False)

# Extraer valores y columnas
blocks = df_ea_sum.columns
values_energy = df_ea_sum.iloc[0].values
values_no_energy = df_nea_sum.iloc[0].values
sum_energy = values_energy.sum()
sum_no_energy = values_no_energy.sum()

# Calcular la diferencia por cada hora (No-Energy-Aware - Energy-Aware)
diff_values = (values_no_energy - values_energy)/values_no_energy * 100  # Diferencia porcentual

# Crear un DataFrame con la diferencia
df_diff = pd.DataFrame([diff_values], columns=blocks)

# Guardar CSV con la diferencia
df_diff.to_csv("datasets-with-selected-routers/power_means_difference_per_hour.csv", index=False)

# Calcular la diferencia total (No-Energy-Aware - Energy-Aware)
sum_difference = (sum_no_energy - sum_energy)/sum_no_energy * 100  # Diferencia porcentual total

# Crear un DataFrame con la diferencia
df_total_diff = pd.DataFrame({
    "sum_energy_aware": [sum_energy],
    "sum_no_energy_aware": [sum_no_energy],
    "saving_ea_vs_nea": [sum_difference]
})

# Guardar CSV con la diferencia
df_total_diff.to_csv("datasets-with-selected-routers/power_means_difference_total.csv", index=False)

# Calcular la diferencia total por router (No-Energy-Aware - Energy-Aware)
router_avg_difference = (df_nea_avg_per_router["power_avg"] - df_ea_avg_per_router["power_avg"]) / df_nea_avg_per_router["power_avg"] * 100  # Diferencia porcentual total por router

# Crear un DataFrame con la diferencia
df_router_avg_diff = pd.DataFrame({
    "router_id": df_nea_avg_per_router["router_id"],
    "saving_ea_vs_nea": router_avg_difference
})

# Guardar CSV con la diferencia
df_router_avg_diff.to_csv("datasets-with-selected-routers/power_means_avg_difference_per_router.csv", index=False)

router_sum_difference = (df_nea_sum_per_router["power_sum"] - df_ea_sum_per_router["power_sum"]) / df_nea_sum_per_router["power_sum"] * 100  # Diferencia porcentual total por router

# Crear un DataFrame con la diferencia
df_router_sum_diff = pd.DataFrame({
    "router_id": df_nea_sum_per_router["router_id"],
    "saving_ea_vs_nea": router_sum_difference
})

# Guardar CSV con la diferencia
df_router_sum_diff.to_csv("datasets-with-selected-routers/power_means_sum_difference_per_router.csv", index=False)

# Calcular la diferencia total por router y por hora (No-Energy-Aware - Energy-Aware)
hour_columns = [str(i) for i in range(1, 25)]

# Crear un DataFrame con la diferencia
df_router_hourly_diff = df_ea_grouped.copy()
df_router_hourly_diff[hour_columns] = (df_nea_grouped[hour_columns] - df_ea_grouped[hour_columns]) / df_nea_grouped[hour_columns] * 100  # Diferencia porcentual por router y hora
    
# Guardar CSV con la diferencia
df_router_hourly_diff.to_csv("datasets-with-selected-routers/power_means_difference_per_router_and_hour.csv", index=False)

# Gráficas de barras comparativas
x = np.arange(len(blocks))  # posiciones de las columnas
width = 0.35  # ancho de las barras

plt.figure(figsize=(16,8))
plt.bar(x - width/2, values_energy, width, label='Energy-Aware (EA)', color='skyblue', edgecolor='navy')
plt.bar(x + width/2, values_no_energy, width, label='Non-Energy-Aware (Non-EA)', color='salmon', edgecolor='darkred')

plt.xlabel("Hour", fontsize=23)
plt.ylabel("Total Energy Consumption (Wh)", fontsize=23)
plt.title("Total Energy Consumption Comparison (EA vs. Non-EA)", fontsize=26)
plt.xticks(x, blocks, rotation=45, fontsize=22)
plt.yticks(fontsize=22)
plt.legend(fontsize=22)

# Limitar el eje Y entre 0 y 1800
plt.ylim(0, 1800)
plt.grid(True)
plt.tight_layout()

plt.savefig("graphics-with-selected-routers/comparison_total_consumption.png", dpi=300)
plt.close()

router_ids = df_ea_avg_per_router['router_id'].values
x = np.arange(len(router_ids))
width = 0.35  # ancho de barras

plt.figure(figsize=(16, 8))
plt.bar(x - width/2, df_ea_avg_per_router["power_avg"], width, label='Energy-Aware (EA)', color='skyblue', edgecolor='navy')
plt.bar(x + width/2, df_nea_avg_per_router["power_avg"], width, label='Non-Energy-Aware (Non-EA)', color='salmon', edgecolor='darkred')

plt.xlabel("Router", fontsize=23)
plt.ylabel("Average Energy Consumption (Wh)", fontsize=23)
#plt.title("Energy Consumption Comparison per Router (EA vs. Non-EA)", fontsize=26)

plt.xticks(x, router_ids, rotation=45, fontsize=22)
plt.yticks(fontsize=22)
plt.legend(fontsize=22)
plt.grid(True)
plt.tight_layout()

plt.savefig("graphics-with-selected-routers/comparison_average_consumption_per_router.png", dpi=300)
plt.close()

plt.figure(figsize=(16, 8))
plt.bar(x - width/2, df_ea_sum_per_router["power_sum"], width, label='Energy-Aware', color='skyblue', edgecolor='navy')
plt.bar(x + width/2, df_nea_sum_per_router["power_sum"], width, label='Non-Energy-Aware', color='salmon', edgecolor='darkred')

plt.xlabel("Router", fontsize=23)
plt.ylabel("Total Energy Consumption (Wh)", fontsize=23)
#plt.title("Energy Consumption Comparison per Router (EA vs. Non-EA)")

plt.xticks(x, router_ids, rotation=45, fontsize=22)
plt.yticks(fontsize=22)
plt.legend(fontsize=22)
plt.grid(True)

plt.tight_layout()

plt.savefig("graphics-with-selected-routers/comparison_total_consumption_per_router.png", dpi=300)
plt.close()

# Gráficas de barras por hora y router
hours = list(range(1, 25))

routers = df_ea_grouped['router_id'].values
num_routers = len(routers)

# X base = 24 horas
x = np.arange(len(hours))

# ancho de cada barra
bar_width = 0.8 / num_routers 

# Gráfica Energy-Aware
plt.figure(figsize=(18, 8))

# Para cada router, representamos Energy-Aware
for idx, router in enumerate(routers):

    # desplazamiento de las barras
    shift = (idx - num_routers/2) * bar_width

    # valores para el router actual
    vals = df_ea_grouped[df_ea_grouped['router_id'] == router].iloc[0, 1:].values

    # Dibujar barras
    plt.bar(
        x + shift,
        vals,
        width=bar_width,
        label=router,
        alpha=0.8
    )

plt.xticks(x, hours)
plt.xlabel("Hour")
plt.ylabel("Energy Consumption - Wh (watt-hour)")
plt.title("Energy Consumption per Router and Hour (Energy-Aware)")
plt.legend(title="Routers", ncol=4)
plt.tight_layout()

plt.savefig("graphics-with-selected-routers/consumption_by_hour_all_routers_ea.png", dpi=300)
plt.close()


# Gráfica Non-Energy-Aware
plt.figure(figsize=(18, 8))

# Para cada router, representamos Non-Energy-Aware
for idx, router in enumerate(routers):

    # desplazamiento de las barras
    shift = (idx - num_routers/2) * bar_width

    # valores para el router actual
    vals = df_nea_grouped[df_nea_grouped['router_id'] == router].iloc[0, 1:].values

    # Dibujar barras
    plt.bar(
        x + shift,
        vals,
        width=bar_width,
        label=router,
        alpha=0.8
    )

plt.xticks(x, hours)
plt.xlabel("Hour")
plt.ylabel("Energy Consumption - Wh (watt-hour)")
plt.title("Energy Consumption per Router and Hour (Non-Energy-Aware)")
plt.legend(title="Routers", ncol=4)
plt.tight_layout()

plt.savefig("graphics-with-selected-routers/consumption_by_hour_all_routers_nea.png", dpi=300)
plt.close()
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Dataset Energy-Aware
df_ea = pd.read_csv('energy-aware-1-processed.csv')

# Dataset No-Energy-Aware
df_nea = pd.read_csv('no-energy-aware-1-processed.csv')

# Concatenar ambos CSV
df_all = pd.concat([df_ea, df_nea], ignore_index=True)

# Obtener el mínimo consumo por router_id
df_min_consumption = (
    df_all.groupby("router_id")["power_consumption_watts"]
          .min()
          .reset_index(name="min_power_consumption_watts")
)

df_min_consumption.to_csv("datasets/min_consumption_per_router.csv", index=False)

# Convertir a diccionario
router_map_base_consumption = dict(zip(df_min_consumption["router_id"], df_min_consumption["min_power_consumption_watts"]))

print(router_map_base_consumption)

# Preprocesado Energy-Aware

# Agrupar por router_id y luego por bloques de 12 filas dentro de cada router
df_ea_grouped = (
    df_ea.groupby('router_id', group_keys=False)
        .apply(
            lambda g: g['power_consumption_watts']
                .reset_index(drop=True)    # Reiniciar el índice para que vaya de 0 a n dentro de cada grupo
                .iloc[:len(g) // 12 * 12]  # Asegura que el número de filas sea múltiplo de 12
                .groupby(lambda x: x // 12)
                .mean()
        )
        .reset_index()
)

# Renombrar columnas numéricas
new_cols = ['router_id'] + [f"{i}" for i in range(1, len(df_ea_grouped.columns))]

df_ea_grouped.columns = new_cols

print(df_ea_grouped)
df_ea_grouped.to_csv("datasets/power_means_per_router_energy-aware.csv", index=False)

# Calcular la suma total por hora
df_ea_sum = pd.DataFrame(df_ea_grouped.drop(columns='router_id').sum()).T  # Transpuesta para fila única

print(df_ea_sum)
df_ea_sum.to_csv("datasets/power_means_energy-aware.csv", index=False)

# Calcular el promedio de las 24 horas para cada router
hour_columns = [str(i) for i in range(1, 25)]

df_ea_avg_per_router = pd.DataFrame({
    "router_id": df_ea_grouped["router_id"],
    "power_avg": df_ea_grouped[hour_columns].mean(axis=1)
})

print(df_ea_avg_per_router)
df_ea_avg_per_router.to_csv("datasets/power_means_per_router_24h_avg_energy-aware.csv", index=False)

# Obtener el ajuste por consumo base
df_ea_aux = df_ea_grouped.copy()
value_cols = df_ea_aux.columns[df_ea_aux.columns != "router_id"]

for rid, subtract_value in router_map_base_consumption.items():
    df_ea_aux.loc[df_ea_aux['router_id'] == rid, value_cols] = (df_ea_aux.loc[df_ea_aux['router_id'] == rid, value_cols] - subtract_value).abs()

print(df_ea_aux)
df_ea_aux.to_csv("datasets/power_means_per_router_energy-aware_with_base_energy_consumption.csv", index=False)

# Calcular la suma total por hora
df_ea_aux_sum = pd.DataFrame(df_ea_aux.drop(columns='router_id').sum()).T  # Transpuesta para fila única

print(df_ea_aux_sum)
df_ea_aux_sum.to_csv("datasets/power_means_energy-aware_with_base_energy_consumption.csv", index=False)

# Calcular el promedio de las 24 horas para cada router
hour_columns = [str(i) for i in range(1, 25)]

df_ea_aux_avg_per_router = pd.DataFrame({
    "router_id": df_ea_aux["router_id"],
    "power_avg": df_ea_aux[hour_columns].mean(axis=1)
})

print(df_ea_aux_avg_per_router)
df_ea_aux_avg_per_router.to_csv("datasets/power_means_per_router_24h_avg_energy-aware_with_base_energy_consumption.csv", index=False)

# Preprocesado No-Energy-Aware

# Agrupar por router_id y luego por bloques de 12 filas dentro de cada router
df_nea_grouped = (
    df_nea.groupby('router_id', group_keys=False)
        .apply(
            lambda g: g['power_consumption_watts']
                .reset_index(drop=True)    # Reiniciar el índice para que vaya de 0 a n dentro de cada grupo
                .iloc[:len(g) // 12 * 12]  # Asegura que el número de filas sea múltiplo de 12
                .groupby(lambda x: x // 12)
                .mean()
        )
        .reset_index()
)

# Renombrar columnas numéricas
new_cols = ['router_id'] + [f"{i}" for i in range(1, len(df_nea_grouped.columns))]

df_nea_grouped.columns = new_cols

print(df_nea_grouped)
df_nea_grouped.to_csv("datasets/power_means_per_router_no-energy-aware.csv", index=False)

# Calcular la suma total por hora
df_nea_sum = pd.DataFrame(df_nea_grouped.drop(columns='router_id').sum()).T  # Transpuesta para fila única

print(df_nea_sum)
df_nea_sum.to_csv("datasets/power_means_no-energy-aware.csv", index=False)

# Calcular el promedio de las 24 horas para cada router
hour_columns = [str(i) for i in range(1, 25)]

df_nea_avg_per_router = pd.DataFrame({
    "router_id": df_nea_grouped["router_id"],
    "power_avg": df_nea_grouped[hour_columns].mean(axis=1)
})

print(df_nea_avg_per_router)
df_nea_avg_per_router.to_csv("datasets/power_means_per_router_24h_avg_no-energy-aware.csv", index=False)

# Obtener el ajuste por consumo base
df_nea_aux = df_nea_grouped.copy()
value_cols = df_nea_aux.columns[df_nea_aux.columns != "router_id"]

for rid, subtract_value in router_map_base_consumption.items():
    df_nea_aux.loc[df_nea_aux['router_id'] == rid, value_cols] = (df_nea_aux.loc[df_nea_aux['router_id'] == rid, value_cols] - subtract_value).abs()
df_nea_aux.to_csv("datasets/power_means_per_router_no-energy-aware_with_base_energy_consumption.csv", index=False)

# Calcular la suma total por hora
df_nea_aux_sum = pd.DataFrame(df_nea_aux.drop(columns='router_id').sum()).T  # Transpuesta para fila única

print(df_nea_aux_sum)
df_nea_aux_sum.to_csv("datasets/power_means_no-energy-aware_with_base_energy_consumption.csv", index=False)

# Calcular el promedio de las 24 horas para cada router
hour_columns = [str(i) for i in range(1, 25)]

df_nea_aux_avg_per_router = pd.DataFrame({
    "router_id": df_nea_aux["router_id"],
    "power_avg": df_nea_aux[hour_columns].mean(axis=1)
})

print(df_nea_aux_avg_per_router)
df_nea_aux_avg_per_router.to_csv("datasets/power_means_per_router_24h_avg_no-energy-aware_with_base_energy_consumption.csv", index=False)

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
df_diff.to_csv("datasets/power_means_difference_per_hour.csv", index=False)

# Calcular la diferencia total (No-Energy-Aware - Energy-Aware)
sum_difference = (sum_no_energy - sum_energy)/sum_no_energy * 100  # Diferencia porcentual total

# Crear un DataFrame con la diferencia
df_total_diff = pd.DataFrame({
    "sum_energy_aware": [sum_energy],
    "sum_no_energy_aware": [sum_no_energy],
    "saving_ea_vs_nea": [sum_difference]
})

# Guardar CSV con la diferencia
df_total_diff.to_csv("datasets/power_means_difference_total.csv", index=False)

# Calcular la diferencia total por router (No-Energy-Aware - Energy-Aware)
router_sum_difference = (df_nea_avg_per_router["power_avg"] - df_ea_avg_per_router["power_avg"]) / df_nea_avg_per_router["power_avg"] * 100  # Diferencia porcentual total por router

# Crear un DataFrame con la diferencia
df_router_diff = pd.DataFrame({
    "router_id": df_nea_avg_per_router["router_id"],
    "saving_ea_vs_nea": router_sum_difference
})

# Guardar CSV con la diferencia
df_router_diff.to_csv("datasets/power_means_difference_per_router.csv", index=False)

# Calcular la diferencia total por router y por hora (No-Energy-Aware - Energy-Aware)
hour_columns = [str(i) for i in range(1, 25)]

# Crear un DataFrame con la diferencia
df_router_hourly_diff = df_ea_grouped.copy()
df_router_hourly_diff[hour_columns] = (df_nea_grouped[hour_columns] - df_ea_grouped[hour_columns]) / df_nea_grouped[hour_columns] * 100  # Diferencia porcentual por router y hora
    
# Guardar CSV con la diferencia
df_router_hourly_diff.to_csv("datasets/power_means_difference_per_router_and_hour.csv", index=False)

# Gráficas de barras comparativas
x = np.arange(len(blocks))  # posiciones de las columnas
width = 0.35  # ancho de las barras

plt.figure(figsize=(14,6))
plt.bar(x - width/2, values_energy, width, label='Energy-Aware (EA)', color='skyblue')
plt.bar(x + width/2, values_no_energy, width, label='No-Energy-Aware (Non-EA)', color='salmon')

plt.xlabel("Hours")
plt.ylabel("Total Energy Consumption (watts)")
plt.title("Total Energy Consumption Comparison (EA vs. Non-EA)")
plt.xticks(x, blocks, rotation=45)
plt.legend()

# Limitar el eje Y entre 2660 y 2675
plt.ylim(2660, 2675)
plt.tight_layout()

plt.savefig("graphics/comparison_total_consumption.png", dpi=300)
plt.close()

router_ids = df_ea_avg_per_router['router_id'].values
x = np.arange(len(router_ids))
width = 0.35  # ancho de barras

plt.figure(figsize=(14, 6))
plt.bar(x - width/2, df_ea_avg_per_router["power_avg"], width, label='Energy-Aware', color='skyblue')
plt.bar(x + width/2, df_nea_avg_per_router["power_avg"], width, label='No-Energy-Aware', color='salmon')

plt.xlabel("Routers")
plt.ylabel("Average Energy Consumption (watts)")
plt.title("Energy Consumption Comparison per Router (EA vs. Non-EA)")

plt.xticks(x, router_ids, rotation=45)
plt.legend()

plt.tight_layout()

plt.savefig("graphics/comparison_total_consumption_per_router.png", dpi=300)
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
plt.ylabel("Consumption (watts)")
plt.title("Energy Consumption per Router and Hour (Energy-Aware)")
plt.legend(title="Routers", ncol=4)
plt.tight_layout()

plt.savefig("graphics/consumption_by_hour_all_routers_ea.png", dpi=300)
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
plt.ylabel("Consumption (watts)")
plt.title("Energy Consumption per Router and Hour (No-Energy-Aware)")
plt.legend(title="Routers", ncol=4)
plt.tight_layout()

plt.savefig("graphics/consumption_by_hour_all_routers_nea.png", dpi=300)
plt.close()

# Extraer valores y bloques con ajuste por consumo base
blocks = df_ea_aux_sum.columns
values_energy = df_ea_aux_sum.iloc[0].values
values_no_energy = df_nea_aux_sum.iloc[0].values
sum_energy = values_energy.sum()
sum_no_energy = values_no_energy.sum()
total_min_consumption = sum(router_map_base_consumption.values())

# Calcular la diferencia por cada hora (No-Energy-Aware - Energy-Aware)
#diff_values = ((values_no_energy - total_min_consumption)  - (values_energy - total_min_consumption))/ (values_no_energy - total_min_consumption) * 100  # Diferencia porcentual
diff_values = (values_no_energy - values_energy)/values_no_energy * 100  # Diferencia porcentual

# Crear un DataFrame con la diferencia
df_diff = pd.DataFrame([diff_values], columns=blocks)

# Guardar CSV con la diferencia
df_diff.to_csv("datasets/power_means_difference_per_hour_with_base_energy_consumption.csv", index=False)

# Calcular la diferencia total (No-Energy-Aware - Energy-Aware)
#sum_difference = ((sum_no_energy - 24*total_min_consumption) - (sum_energy - 24*total_min_consumption))/(sum_no_energy - 24*total_min_consumption) * 100  # Diferencia porcentual total
sum_difference = (sum_no_energy - sum_energy)/(sum_no_energy) * 100  # Diferencia porcentual total

# Crear un DataFrame con la diferencia
df_total_diff = pd.DataFrame({
    "sum_energy_aware": [sum_energy],
    "sum_no_energy_aware": [sum_no_energy],
    "saving_ea_vs_nea": [sum_difference]
})

# Guardar CSV con la diferencia
df_total_diff.to_csv("datasets/power_means_difference_total_with_base_energy_consumption.csv", index=False)

# Calcular la diferencia total por router (No-Energy-Aware - Energy-Aware)
#router_sum_difference = ((df_nea_aux_avg_per_router["power_avg"] - total_min_consumption) - (df_ea_aux_avg_per_router["power_avg"] - total_min_consumption)) / (df_nea_aux_avg_per_router["power_avg"] - total_min_consumption) * 100  # Diferencia porcentual total por router
router_sum_difference = (df_nea_aux_avg_per_router["power_avg"] - df_ea_aux_avg_per_router["power_avg"]) / df_nea_aux_avg_per_router["power_avg"] * 100  # Diferencia porcentual total por router

# Crear un DataFrame con la diferencia
df_router_diff = pd.DataFrame({
    "router_id": df_nea_avg_per_router["router_id"],
    "saving_ea_vs_nea": router_sum_difference
})

# Calcular la diferencia total por router y por hora (No-Energy-Aware - Energy-Aware)
hour_columns = [str(i) for i in range(1, 25)]

# Crear un DataFrame con la diferencia
df_router_hourly_diff = df_ea_aux.copy()
df_router_hourly_diff[hour_columns] = (df_nea_aux[hour_columns] - df_ea_aux[hour_columns]) / df_nea_aux[hour_columns] * 100  # Diferencia porcentual por router y hora
    
# Guardar CSV con la diferencia
df_router_hourly_diff.to_csv("datasets/power_means_difference_per_router_and_hour_with_base_energy_consumption.csv", index=False)

# Guardar CSV con la diferencia
df_router_diff.to_csv("datasets/power_means_difference_per_router_with_base_energy_consumption.csv", index=False)

# Gráficas de barras comparativa con ajuste por consumo base
x = np.arange(len(blocks))  # posiciones de las columnas
width = 0.35  # ancho de las barras

# Crear figura
plt.figure(figsize=(14,6))
plt.bar(x - width/2, values_energy, width, label='Energy-Aware (EA)', color='skyblue')
plt.bar(x + width/2, values_no_energy, width, label='No-Energy-Aware (Non-EA)', color='salmon')

# Etiquetas y título
plt.xlabel("Hours")
plt.ylabel("Increased Energy Consumption (watts)")
plt.title("Increased Energy Consumption Comparison (EA vs. Non-EA)")
plt.xticks(x, blocks, rotation=45)
plt.legend()

# Guardar en archivo de imagen
plt.savefig("graphics/comparison_increased_consumption.png", dpi=300)
plt.close()

router_ids = df_ea_avg_per_router['router_id'].values
x = np.arange(len(router_ids))
width = 0.35  # ancho de barras

plt.figure(figsize=(14, 6))
plt.bar(x - width/2, df_ea_aux_avg_per_router["power_avg"], width, label='Energy-Aware (EA)', color='skyblue')
plt.bar(x + width/2, df_nea_aux_avg_per_router["power_avg"], width, label='No-Energy-Aware (Non-EA)', color='salmon')

plt.xlabel("Routers")
plt.ylabel("Increased Average Energy Consumption (watts)")
plt.title("Increased Energy Consumption Comparison per Router (EA vs. Non-EA)")

plt.xticks(x, router_ids, rotation=45)
plt.legend()

plt.tight_layout()

plt.savefig("graphics/comparison_increased_consumption_per_router.png", dpi=300)
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
    vals = df_ea_aux[df_ea_aux['router_id'] == router].iloc[0, 1:].values

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
plt.ylabel("Increased Average Energy Consumption (watts)")
plt.title("Increased Energy Consumption per Router and Hour (Energy-Aware)")
plt.legend(title="Routers", ncol=4)
plt.tight_layout()

plt.savefig("graphics/increased_consumption_by_hour_all_routers_ea.png", dpi=300)
plt.close()


# Gráfica Non-Energy-Aware
plt.figure(figsize=(18, 8))

# Para cada router, representamos Non-Energy-Aware
for idx, router in enumerate(routers):

    # desplazamiento de las barras
    shift = (idx - num_routers/2) * bar_width

    # valores para el router actual
    vals = df_nea_aux[df_nea_aux['router_id'] == router].iloc[0, 1:].values

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
plt.ylabel("Increased Average Energy Consumption (watts)")
plt.title("Increased Energy Consumption per Router and Hour (No-Energy-Aware)")
plt.legend(title="Routers", ncol=4)
plt.tight_layout()

plt.savefig("graphics/increased_consumption_by_hour_all_routers_nea.png", dpi=300)
plt.close()
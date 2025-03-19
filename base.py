import pandas as pd
import pulp

# Leer el archivo Excel
archivo_excel = "restricciones_panaderia_Final.xlsx"

# Leer restricciones
df_restricciones = pd.read_excel(archivo_excel, sheet_name="Restricciones", index_col=0)
limite_tiempo = df_restricciones.loc["Tiempo (horas)", "Límite"]
limite_harina = df_restricciones.loc["Harina (kg)", "Límite"]
limite_espacio = df_restricciones.loc["Almacenamiento", "Límite"]

# Leer datos de los panes
df_panes = pd.read_excel(archivo_excel, sheet_name="Panes")

# Crear problema de optimización
problema = pulp.LpProblem("Maximizacion_Ganancias_Panaderia", pulp.LpMaximize)

# Variables de decisión
x = {
    row["Tipo de Pan"]: pulp.LpVariable(
        row["Tipo de Pan"],
        lowBound=row["Producción mínima"],
        upBound=row["Producción máxima"],
        cat="Integer"
    ) for _, row in df_panes.iterrows()
}

# Función objetivo (maximizar ganancias)
problema += pulp.lpSum(row["Ganancia"] * x[row["Tipo de Pan"]] for _, row in df_panes.iterrows()), "Ganancia_Total"

# Restricciones
problema += pulp.lpSum(row["Tiempo (horas)"] * x[row["Tipo de Pan"]] for _, row in df_panes.iterrows()) <= limite_tiempo, "Tiempo"
problema += pulp.lpSum(row["Harina (kg)"] * x[row["Tipo de Pan"]] for _, row in df_panes.iterrows()) <= limite_harina, "Harina"
problema += pulp.lpSum(row["Almacenamiento (espacio)"] * x[row["Tipo de Pan"]] for _, row in df_panes.iterrows()) <= limite_espacio, "Espacio"

# Resolver
problema.solve()

# Resultados
print(f"Estado: {pulp.LpStatus[problema.status]}")
print(f"Ganancia óptima: ${pulp.value(problema.objective):.2f}")
for pan in x:
    print(f"{pan}: {pulp.value(x[pan])} unidades")
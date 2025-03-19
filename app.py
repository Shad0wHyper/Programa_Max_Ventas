import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import pulp
import base64

# Inicializar la aplicación
app = dash.Dash(__name__)

# Diseño de la interfaz
app.layout = html.Div(className="container", children=[
    html.H1("Optimizador de Producción - Panadería"),

    # Sección del formulario
    html.Div(className="form-container", children=[
        # Subir archivo Excel
        dcc.Upload(
            id="upload-excel",
            children=html.Button("Subir Excel", className="btn"),
            multiple=False
        ),

        html.Br(),

        # Ajustar restricciones
        html.Div(className="input-group", children=[
            html.Label("Límite de Tiempo (horas):"),
            dcc.Input(id="input-tiempo", type="number", value=20),
        ]),

        html.Div(className="input-group", children=[
            html.Label("Límite de Harina (kg):"),
            dcc.Input(id="input-harina", type="number", value=25),
        ]),

        html.Div(className="input-group", children=[
            html.Label("Límite de Almacenamiento:"),
            dcc.Input(id="input-almacenamiento", type="number", value=50),
        ]),

        # Botón para optimizar
        html.Button("Optimizar", id="btn-optimizar", className="btn"),
    ]),

    # Sección para mostrar resultados
    html.Div(id="output-results", className="results-section")
])


# Callback para procesar el archivo y optimizar
@app.callback(
    Output("output-results", "children"),
    Input("btn-optimizar", "n_clicks"),
    State("upload-excel", "contents"),
    State("input-tiempo", "value"),
    State("input-harina", "value"),
    State("input-almacenamiento", "value")
)
def optimize_production(n_clicks, contents, tiempo, harina, almacenamiento):
    if n_clicks and contents:
        try:
            # Decodificar el archivo subido
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            # Leer el archivo Excel
            df_panes = pd.read_excel(decoded, sheet_name="Panes")

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

            # Función objetivo
            problema += pulp.lpSum(
                row["Ganancia"] * x[row["Tipo de Pan"]] for _, row in df_panes.iterrows()), "Ganancia_Total"

            # Restricciones
            problema += pulp.lpSum(
                row["Tiempo (horas)"] * x[row["Tipo de Pan"]] for _, row in df_panes.iterrows()) <= tiempo, "Tiempo"
            problema += pulp.lpSum(
                row["Harina (kg)"] * x[row["Tipo de Pan"]] for _, row in df_panes.iterrows()) <= harina, "Harina"
            problema += pulp.lpSum(row["Almacenamiento (espacio)"] * x[row["Tipo de Pan"]] for _, row in
                                   df_panes.iterrows()) <= almacenamiento, "Espacio"

            # Resolver
            problema.solve()

            # Mostrar resultados
            resultados = [
                html.H3(f"Ganancia óptima: ${pulp.value(problema.objective):.2f}"),
                html.Table(className="results-table", children=[
                    html.Thead(html.Tr([html.Th("Pan"), html.Th("Cantidad")])),
                    html.Tbody([
                        html.Tr([html.Td(pan), html.Td(f"{pulp.value(x[pan])} unidades")])
                        for pan in x
                    ])
                ])
            ]
            return resultados
        except Exception as e:
            return html.Div(f"Error: {str(e)}", style={"color": "red"})
    return "Suba un archivo Excel y ajuste las restricciones."


# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
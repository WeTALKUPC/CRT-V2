import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurar el diseño en ancho completo
st.set_page_config(layout="wide")

# Título del Dashboard
st.title("Dashboard de Cumplimiento por Feriado, Programa e Instructor")

# Cargar el archivo Excel directamente desde el repositorio
DATA_URL = "https://raw.githubusercontent.com/WeTALKUPC/CRT-V2/main/RECUPERACIONES%20FERIADOS%20V1.xlsx"
df = pd.read_excel(DATA_URL, engine="openpyxl")

# Limpiar los datos en las columnas seleccionadas
for col in df.columns[2:]:
    df[col] = df[col].str.strip().str.upper()
    df[col] = df[col].replace({
        "NO TENIA CLASES": "NO TENÍA CLASES",
        "NO TENÍA CLASES ": "NO TENÍA CLASES"
    })

# Lista de feriados
feriados = df.columns[2:-1]  # Excluir columna de observaciones
feriado = st.selectbox("Selecciona un feriado (o TODOS):", ["TODOS"] + list(feriados))

# Lista de instructores
instructores = df["INSTRUCTOR"].unique()
instructor = st.selectbox("Selecciona un instructor:", ["TODOS"] + list(instructores))

# Selector para estado de cumplimiento (TODOS, SI, NO)
estado = st.selectbox("Selecciona un estado de cumplimiento:", ["TODOS", "SI", "NO"])

# Mostrar resultados para el feriado seleccionado
if feriado != "TODOS":
    # Excluir "NO TENÍA CLASES" del cálculo
    df_feriado = df[df[feriado] != "NO TENÍA CLASES"]

    # Calcular el porcentaje de cumplimiento
    cumplimiento = df_feriado[feriado].value_counts(normalize=True) * 100
    cumplimiento = cumplimiento.reindex(["SI", "NO"], fill_value=0)

    # Crear gráfico de barras horizontal
    st.subheader(f"Porcentaje de cumplimiento para {feriado}")
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.barh(
        cumplimiento.index,
        cumplimiento.values,
        color=["#4CAF50", "#F44336"],  # Verde y rojo
        edgecolor="black",
        height=0.4
    )
    ax.set_xlabel("Porcentaje")
    ax.set_xlim(0, 100)
    ax.tick_params(axis="y", labelsize=10)
    for i, v in enumerate(cumplimiento.values):
        ax.text(v + 1, i, f"{v:.1f}%", color="black", va="center", fontsize=10)
    st.pyplot(fig)

    # Mostrar instructores que no cumplieron
    st.subheader(f"Instructores que no recuperaron clases en {feriado}")
    no_cumplieron = df_feriado[df_feriado[feriado] == "NO"]
    if not no_cumplieron.empty:
        st.table(no_cumplieron[["INSTRUCTOR", "PROGRAMA", "OBSERVACIÓN"]])
    else:
        st.write("Todos los instructores cumplieron sus clases en este feriado.")

# Mostrar cumplimiento anual por instructor
if instructor != "TODOS":
    st.subheader(f"Cumplimiento anual para el instructor: {instructor}")
    cumplimiento_anual = {"Cumplió": [], "No cumplió": [], "No tenía clases": []}
    fechas = []

    for feriado in feriados:
        df_temp = df[df["INSTRUCTOR"] == instructor]
        valores = df_temp[feriado].value_counts()
        cumplimiento_anual["Cumplió"].append(valores.get("SI", 0))
        cumplimiento_anual["No cumplió"].append(valores.get("NO", 0))
        cumplimiento_anual["No tenía clases"].append(valores.get("NO TENÍA CLASES", 0))
        fechas.append(feriado)

    # Crear un gráfico de puntos (scatter plot)
    fig, ax = plt.subplots(figsize=(10, 6))

    # Valores en el eje Y para cada categoría
    y_values = {"Cumplió": 2, "No cumplió": 1, "No tenía clases": 0}

    # Transformar datos
    for categoria, valores in cumplimiento_anual.items():
        y = [y_values[categoria]] * len(valores)
        ax.scatter(fechas, y, color="#4CAF50" if categoria == "Cumplió" else "#F44336" if categoria == "No cumplió" else "#BDBDBD",
                   label=categoria, s=100, edgecolor="black")

    # Ajustar etiquetas y formato
    ax.set_yticks(list(y_values.values()))
    ax.set_yticklabels(list(y_values.keys()), fontsize=10)
    ax.set_xticks(range(len(fechas)))
    ax.set_xticklabels(fechas, rotation=45, ha="right", fontsize=10)
    ax.set_title(f"Cumplimiento Anual por Fecha para {instructor}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Feriados", fontsize=12)
    ax.set_ylabel("Estado de Cumplimiento", fontsize=12)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    st.pyplot(fig)

# Mostrar tabla de instructores según estado seleccionado
if estado != "TODOS":
    st.subheader(f"Instructores con estado de cumplimiento: {estado}")
    resultados = df[df[feriados].apply(lambda row: row.str.contains(estado).any(), axis=1)]
    resultados = resultados.melt(
        id_vars=["INSTRUCTOR", "PROGRAMA"],
        value_vars=feriados,
        var_name="Fecha",
        value_name="Estado"
    )
    resultados = resultados[resultados["Estado"] == estado]
    resultados = resultados.rename(columns={
        "INSTRUCTOR": "Nombre",
        "PROGRAMA": "Programa",
        "Fecha": "Fecha no recuperada",
        "Estado": "Observación"
    })
    st.table(resultados[["Nombre", "Programa", "Fecha no recuperada", "Observación"]])

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

    # Layout restringido para el gráfico
    col1, col2, col3 = st.columns([1, 2, 1])  # Ajustar el espacio del gráfico al centro
    with col2:
        # Crear un gráfico de barras apiladas
        fig, ax = plt.subplots(figsize=(6, 2))  # Reducir tamaño del gráfico

        # Datos para las barras
        cumplio = cumplimiento_anual["Cumplió"]
        no_cumplio = cumplimiento_anual["No cumplió"]
        no_tenia_clases = cumplimiento_anual["No tenía clases"]

        # Crear las barras apiladas
        ax.bar(fechas, cumplio, label="Cumplió", color="#4CAF50", edgecolor="black")
        ax.bar(fechas, no_cumplio, bottom=cumplio, label="No cumplió", color="#F44336", edgecolor="black")
        ax.bar(fechas, no_tenia_clases, bottom=[cumplio[i] + no_cumplio[i] for i in range(len(cumplio))], 
               label="No tenía clases", color="#BDBDBD", edgecolor="black")

        # Eliminar eje Y
        ax.get_yaxis().set_visible(False)

        # Etiquetas y formato
        ax.set_xticks(range(len(fechas)))
        ax.set_xticklabels(fechas, rotation=45, ha="right", fontsize=8)
        ax.set_xlabel("Feriados", fontsize=10)
        ax.legend(fontsize=8, loc="upper right")

        # Mostrar el gráfico
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

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurar el diseño en ancho completo
st.set_page_config(layout="wide")

# Título del Dashboard
st.title("Sistema de seguimiento de recuperaciones de clase en feriados")

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
    fig, ax = plt.subplots(figsize=(5, 1.5))  # Ajustar el tamaño del gráfico
    ax.barh(
        cumplimiento.index,
        cumplimiento.values,
        color=["#90EE90", "#FFCCCB"],  # Verde claro y rojo claro
        edgecolor="black",
        height=0.3  # Ajustar la altura de las barras
    )
    ax.set_xlabel("Porcentaje")
    ax.set_xlim(0, 100)  # Limitar el eje X a 100%
    ax.tick_params(axis="y", labelsize=10)  # Ajustar el tamaño de las etiquetas
    for i, v in enumerate(cumplimiento.values):
        ax.text(v + 1, i, f"{v:.1f}%", color="black", va="center", fontsize=10)  # Mostrar valores al lado de las barras
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
    cumplimiento_anual = {"SI": [], "NO": [], "NO TENÍA CLASES": []}
    fechas = []

    for feriado in feriados:
        df_temp = df[df["INSTRUCTOR"] == instructor]
        valores = df_temp[feriado].value_counts()
        cumplimiento_anual["SI"].append(valores.get("SI", 0))
        cumplimiento_anual["NO"].append(valores.get("NO", 0))
        cumplimiento_anual["NO TENÍA CLASES"].append(valores.get("NO TENÍA CLASES", 0))
        fechas.append(feriado)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(fechas, cumplimiento_anual["SI"], label="Cumplió", color="#90EE90", edgecolor="black")
    ax.bar(fechas, cumplimiento_anual["NO"], bottom=cumplimiento_anual["SI"], label="No cumplió", color="#FFCCCB", edgecolor="black")
    ax.bar(fechas, cumplimiento_anual["NO TENÍA CLASES"], bottom=[cumplimiento_anual["SI"][i] + cumplimiento_anual["NO"][i] for i in range(len(fechas))], label="No tenía clases", color="#D3D3D3", edgecolor="black")
    ax.set_ylabel("Cantidad")
    ax.set_xlabel("Feriados")
    ax.set_title(f"Cumplimiento Anual de {instructor}")
    plt.xticks(rotation=45, ha="right")
    ax.legend()
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

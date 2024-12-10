import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

# Lista de programas
programas = df["PROGRAMA"].unique()
programa = st.selectbox("Selecciona un programa:", ["TODOS"] + list(programas))

# Aplicar filtro por instructor y programa
if instructor != "TODOS":
    df_filtrado = df[df["INSTRUCTOR"] == instructor]
else:
    df_filtrado = df

if programa != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["PROGRAMA"] == programa]

# Mostrar resultados para el feriado seleccionado
if feriado != "TODOS":
    # Excluir "NO TENÍA CLASES" del cálculo
    df_feriado = df_filtrado[df_filtrado[feriado] != "NO TENÍA CLASES"]

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

else:
    st.write("Selecciona un feriado específico para más detalles.")

import streamlit as st
from database.db import init_db, seed_initial_data, DB_PATH

st.set_page_config(
    page_title="Schedules",
    page_icon="📅",
    layout="wide"
)

init_db()
seed_initial_data()

st.title("📅 Schedules")
st.subheader("Planificación local de personal")

st.sidebar.title("Navegación")
section = st.sidebar.radio(
    "Ir a:",
    ["Inicio", "Empleados", "Posiciones", "Turnos", "Línea de tiempo"]
)

if section == "Inicio":
    st.markdown("## Bienvenido")
    st.write("Esta app te ayudará a planificar al personal para el día siguiente.")
    st.write("Podrás registrar empleados, posiciones, turnos y luego visualizar la cobertura.")
    st.success("Base de datos inicializada correctamente.")
    st.info(f"Base de datos local: `{DB_PATH}`")
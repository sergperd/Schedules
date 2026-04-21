import streamlit as st
from database.db import init_db, DB_PATH

st.set_page_config(
    page_title="Schedules",
    page_icon="📅",
    layout="wide"
)

init_db()

st.title("📅 Schedules")
st.subheader("Planificación local de personal")

st.sidebar.title("Navegación")
section = st.sidebar.radio(
    "Ir a:",
    ["Inicio", "Empleados", "Turnos", "Cobertura"]
)

if section == "Inicio":
    st.markdown("## Bienvenido")
    st.write("Esta app te ayudará a visualizar la cobertura del personal.")
    st.write("Podrás registrar empleados, turnos y ver un gráfico tipo schedule.")
    st.success("Base de datos inicializada correctamente.")
    st.info(f"Base de datos local: `{DB_PATH}`")

elif section == "Empleados":
    from modules.employees import render_employees_page
    render_employees_page()

elif section == "Turnos":
    from modules.schedule import render_schedule_page
    render_schedule_page()

elif section == "Cobertura":
    from modules.timeline import render_timeline_page
    render_timeline_page()
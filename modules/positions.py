import streamlit as st
from database.db import get_connection


def get_areas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM areas ORDER BY name")
    areas = cursor.fetchall()
    conn.close()
    return areas


def get_positions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT positions.id, positions.name, areas.name AS area_name
        FROM positions
        JOIN areas ON positions.area_id = areas.id
        ORDER BY areas.name, positions.name
    """)
    positions = cursor.fetchall()
    conn.close()
    return positions


def add_position(name, area_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO positions (name, area_id)
        VALUES (?, ?)
    """, (name, area_id))
    conn.commit()
    conn.close()


def render_positions_page():
    st.markdown("## Posiciones")
    st.write("Gestiona las posiciones por área.")

    areas = get_areas()

    if not areas:
        st.warning("No hay áreas registradas.")
        return

    st.markdown("### Agregar nueva posición")

    position_name = st.text_input("Nombre de la posición")

    area_options = {area["name"]: area["id"] for area in areas}
    selected_area_name = st.selectbox("Área", list(area_options.keys()))

    if st.button("Guardar posición"):
        if not position_name.strip():
            st.error("Debes escribir un nombre para la posición.")
        else:
            try:
                add_position(position_name.strip(), area_options[selected_area_name])
                st.success(f"Posición '{position_name}' agregada correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo guardar la posición: {e}")

    st.markdown("### Lista de posiciones")

    positions = get_positions()

    if positions:
        for pos in positions:
            st.write(f"- **{pos['name']}** ({pos['area_name']})")
    else:
        st.info("Todavía no hay posiciones registradas.")
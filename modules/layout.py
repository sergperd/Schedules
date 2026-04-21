import streamlit as st
import pandas as pd
from database.db import get_connection


def add_layout_position(position_number, name, area, min_required):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO layout_positions (position_number, name, area, min_required)
        VALUES (?, ?, ?, ?)
    """, (position_number, name, area, min_required))
    conn.commit()
    conn.close()


def get_layout_positions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, position_number, name, area, min_required
        FROM layout_positions
        ORDER BY position_number, name
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_layout_position(position_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM layout_positions WHERE id = ?", (position_id,))
    conn.commit()
    conn.close()


def render_layout_page():
    st.markdown("## Layout")
    st.write("Define el esquema base del piso y sus posiciones.")

    st.markdown("### Agregar posición al layout")

    position_number = st.number_input("Número en el plano", min_value=1, step=1)
    name = st.text_input("Nombre de la posición")
    area = st.selectbox("Área", ["Cocina", "Servicio"])
    min_required = st.number_input(
        "Mínimo requerido",
        min_value=1,
        step=1,
        value=1
    )

    if st.button("Guardar posición en layout"):
        if not name.strip():
            st.error("Debes escribir un nombre para la posición.")
        else:
            try:
                add_layout_position(
                    int(position_number),
                    name.strip(),
                    area,
                    int(min_required)
                )
                st.success(f"Posición '{name}' agregada al layout.")
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo guardar: {e}")

    st.markdown("### Revisión del layout")

    rows = get_layout_positions()

    if rows:
        data = []
        for row in rows:
            data.append({
                "#": row["position_number"],
                "Posición": row["name"],
                "Área": row["area"],
                "Mínimo": row["min_required"]
            })

        df = pd.DataFrame(data)

        duplicated_numbers = df[df.duplicated(subset=["#"], keep=False)]
        if not duplicated_numbers.empty:
            st.warning("⚠️ Hay números de posición duplicados:")
            st.dataframe(duplicated_numbers, use_container_width=True, hide_index=True)

        duplicated_names = df[df.duplicated(subset=["Posición"], keep=False)]
        if not duplicated_names.empty:
            st.warning("⚠️ Hay nombres de posición duplicados:")
            st.dataframe(duplicated_names, use_container_width=True, hide_index=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("### Eliminar posición")

        for row in rows:
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"#{row['position_number']} - {row['name']}")

            with col2:
                if st.button("❌", key=f"del_{row['id']}"):
                    delete_layout_position(row["id"])
                    st.rerun()

        st.markdown("### Resumen")
        st.write(f"Total de posiciones cargadas: **{len(df)}**")

        cocina_count = len(df[df["Área"] == "Cocina"])
        servicio_count = len(df[df["Área"] == "Servicio"])

        st.write(f"Cocina: **{cocina_count}**")
        st.write(f"Servicio: **{servicio_count}**")
    else:
        st.info("Todavía no hay posiciones cargadas en el layout.") 
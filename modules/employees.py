import streamlit as st
from database.db import get_connection


def render_employees_page():
    st.title("👥 Empleados")

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # ➕ FORMULARIO
    # =========================
    st.subheader("Agregar empleado")

    name = st.text_input("Nombre del empleado")

    role_type = st.selectbox(
        "Tipo de empleado",
        ["Cocina", "Servicio", "Ambos"]
    )

    if st.button("Guardar empleado"):
        if name:
            cursor.execute(
                "INSERT INTO employees (name, role_type) VALUES (?, ?)",
                (name, role_type)
            )
            conn.commit()
            st.success("Empleado guardado correctamente")
            st.rerun()
        else:
            st.warning("El nombre es obligatorio")

    st.divider()

    # =========================
    # 📋 LISTA DE EMPLEADOS
    # =========================
    st.subheader("Empleados registrados")

    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()

    if employees:
        for emp in employees:
            st.write(f"• {emp['name']} — {emp['role_type']}")
    else:
        st.info("No hay empleados registrados todavía.")

    conn.close()
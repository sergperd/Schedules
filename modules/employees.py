import streamlit as st
from database.db import get_connection


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


def get_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, notes FROM employees ORDER BY name")
    employees = cursor.fetchall()
    conn.close()
    return employees


def add_employee(name, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (name, notes)
        VALUES (?, ?)
    """, (name, notes))
    employee_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return employee_id


def add_employee_positions(employee_id, position_ids):
    conn = get_connection()
    cursor = conn.cursor()

    for pos_id in position_ids:
        cursor.execute("""
            INSERT INTO employee_positions (employee_id, position_id)
            VALUES (?, ?)
        """, (employee_id, pos_id))

    conn.commit()
    conn.close()


def get_employee_positions(employee_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT positions.name
        FROM employee_positions
        JOIN positions ON employee_positions.position_id = positions.id
        WHERE employee_positions.employee_id = ?
    """, (employee_id,))
    positions = cursor.fetchall()
    conn.close()
    return [p["name"] for p in positions]


def render_employees_page():
    st.markdown("## Empleados")
    st.write("Gestiona los empleados y sus habilidades.")

    positions = get_positions()

    if not positions:
        st.warning("Primero debes crear posiciones.")
        return

    st.markdown("### Agregar nuevo empleado")

    name = st.text_input("Nombre del empleado")
    notes = st.text_area("Notas (opcional)")

    position_options = {
        f"{p['name']} ({p['area_name']})": p["id"]
        for p in positions
    }

    selected_positions = st.multiselect(
        "Posiciones que domina",
        list(position_options.keys())
    )

    if st.button("Guardar empleado"):
        if not name.strip():
            st.error("El nombre es obligatorio.")
        else:
            try:
                employee_id = add_employee(name.strip(), notes.strip())

                selected_ids = [
                    position_options[p] for p in selected_positions
                ]

                add_employee_positions(employee_id, selected_ids)

                st.success(f"Empleado '{name}' creado correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    st.markdown("### Lista de empleados")

    employees = get_employees()

    if employees:
        for emp in employees:
            pos = get_employee_positions(emp["id"])
            pos_text = ", ".join(pos) if pos else "Sin posiciones"
            st.write(f"- **{emp['name']}** → {pos_text}")
    else:
        st.info("No hay empleados registrados.")
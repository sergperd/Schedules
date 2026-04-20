import streamlit as st
from database.db import get_connection
from datetime import date, timedelta


def get_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM employees ORDER BY name")
    employees = cursor.fetchall()
    conn.close()
    return employees


def get_positions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name FROM positions ORDER BY name
    """)
    positions = cursor.fetchall()
    conn.close()
    return positions


def add_shift(employee_id, shift_date, start_time, end_time, position_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO shifts (employee_id, shift_date, start_time, end_time, assigned_position_id)
        VALUES (?, ?, ?, ?, ?)
    """, (employee_id, shift_date, start_time, end_time, position_id))

    conn.commit()
    conn.close()


def get_shifts_for_day(shift_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT shifts.*, employees.name
        FROM shifts
        JOIN employees ON shifts.employee_id = employees.id
        WHERE shift_date = ?
        ORDER BY start_time
    """, (shift_date,))

    shifts = cursor.fetchall()
    conn.close()
    return shifts


def render_schedule_page():
    st.markdown("## Turnos")
    st.write("Planifica los turnos para el día siguiente.")

    employees = get_employees()
    positions = get_positions()

    if not employees:
        st.warning("Primero debes crear empleados.")
        return

    tomorrow = date.today() + timedelta(days=1)

    st.markdown(f"### Crear turno para {tomorrow}")

    employee_options = {emp["name"]: emp["id"] for emp in employees}
    selected_employee = st.selectbox("Empleado", list(employee_options.keys()))

    start_time = st.time_input("Hora de inicio")
    end_time = st.time_input("Hora de fin")

    position_options = {pos["name"]: pos["id"] for pos in positions}
    selected_position = st.selectbox("Posición asignada", list(position_options.keys()))

    if st.button("Guardar turno"):
        try:
            add_shift(
                employee_options[selected_employee],
                str(tomorrow),
                str(start_time),
                str(end_time),
                position_options[selected_position]
            )
            st.success("Turno guardado correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("### Turnos registrados")

    shifts = get_shifts_for_day(str(tomorrow))

    if shifts:
        for s in shifts:
            st.write(f"- {s['name']} | {s['start_time']} - {s['end_time']}")
    else:
        st.info("No hay turnos aún.")
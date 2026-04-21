import streamlit as st
from database.db import get_connection
from datetime import date, timedelta, time


def render_schedule_page():
    st.title("🕒 Turnos")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, role_type FROM employees ORDER BY name")
    employees = cursor.fetchall()

    if not employees:
        st.warning("Primero debes registrar empleados.")
        conn.close()
        return

    st.subheader("Agregar turno")

    employee_options = {
        f"{emp['name']} ({emp['role_type']})": emp["id"]
        for emp in employees
    }

    selected_employee_label = st.selectbox(
        "Empleado",
        list(employee_options.keys()),
        key="new_shift_employee"
    )

    shift_date = st.date_input(
        "Fecha del turno",
        value=date.today() + timedelta(days=1),
        key="new_shift_date"
    )

    start_time = st.time_input("Hora de entrada", key="new_shift_start")
    end_time = st.time_input("Hora de salida", key="new_shift_end")

    coverage_type = st.selectbox(
        "Tipo de cobertura en este turno",
        ["Cocina", "Servicio", "Ambos"],
        key="new_shift_coverage"
    )

    if st.button("Guardar turno"):
        try:
            cursor.execute("""
                INSERT INTO shifts (employee_id, shift_date, start_time, end_time, coverage_type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                employee_options[selected_employee_label],
                str(shift_date),
                str(start_time),
                str(end_time),
                coverage_type
            ))
            conn.commit()
            st.success("Turno guardado correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo guardar el turno: {e}")

    st.divider()
    st.subheader("Editar o borrar turnos")

    cursor.execute("""
        SELECT
            shifts.id,
            shifts.employee_id,
            employees.name,
            employees.role_type,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.coverage_type
        FROM shifts
        JOIN employees ON shifts.employee_id = employees.id
        ORDER BY shifts.shift_date, shifts.start_time, employees.name
    """)
    shifts = cursor.fetchall()

    if not shifts:
        st.info("No hay turnos registrados todavía.")
        conn.close()
        return

    employee_id_to_label = {
        emp["id"]: f"{emp['name']} ({emp['role_type']})"
        for emp in employees
    }

    label_to_employee_id = {v: k for k, v in employee_id_to_label.items()}
    employee_labels = list(employee_options.keys())

    for shift in shifts:
        with st.expander(
            f"{shift['shift_date']} | {shift['name']} | {shift['start_time']} - {shift['end_time']} | {shift['coverage_type']}"
        ):
            current_label = employee_id_to_label[shift["employee_id"]]

            edited_employee_label = st.selectbox(
                "Empleado",
                employee_labels,
                index=employee_labels.index(current_label),
                key=f"emp_{shift['id']}"
            )

            edited_date = st.date_input(
                "Fecha",
                value=date.fromisoformat(shift["shift_date"]),
                key=f"date_{shift['id']}"
            )

            edited_start = st.time_input(
                "Hora de entrada",
                value=time(
                    hour=int(shift["start_time"].split(":")[0]),
                    minute=int(shift["start_time"].split(":")[1])
                ),
                key=f"start_{shift['id']}"
            )

            edited_end = st.time_input(
                "Hora de salida",
                value=time(
                    hour=int(shift["end_time"].split(":")[0]),
                    minute=int(shift["end_time"].split(":")[1])
                ),
                key=f"end_{shift['id']}"
            )

            coverage_options = ["Cocina", "Servicio", "Ambos"]
            edited_coverage = st.selectbox(
                "Tipo de cobertura",
                coverage_options,
                index=coverage_options.index(shift["coverage_type"]),
                key=f"coverage_{shift['id']}"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Guardar cambios", key=f"save_{shift['id']}"):
                    try:
                        cursor.execute("""
                            UPDATE shifts
                            SET employee_id = ?, shift_date = ?, start_time = ?, end_time = ?, coverage_type = ?
                            WHERE id = ?
                        """, (
                            label_to_employee_id[edited_employee_label],
                            str(edited_date),
                            str(edited_start),
                            str(edited_end),
                            edited_coverage,
                            shift["id"]
                        ))
                        conn.commit()
                        st.success("Turno actualizado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo actualizar: {e}")

            with col2:
                if st.button("Borrar turno", key=f"delete_{shift['id']}"):
                    try:
                        cursor.execute("DELETE FROM shifts WHERE id = ?", (shift["id"],))
                        conn.commit()
                        st.success("Turno eliminado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo borrar: {e}")

    conn.close()
import streamlit as st
from database.db import get_connection
from datetime import date, timedelta
import pandas as pd


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


def generate_timeline(shifts):
    if not shifts:
        return {}

    start_hours = [int(shift["start_time"].split(":")[0]) for shift in shifts]
    end_hours = [int(shift["end_time"].split(":")[0]) for shift in shifts]

    min_hour = min(start_hours)
    max_hour = max(end_hours)

    timeline = {h: 0 for h in range(min_hour, max_hour + 1)}

    for shift in shifts:
        start = int(shift["start_time"].split(":")[0])
        end = int(shift["end_time"].split(":")[0])

        for h in range(start, end):
            if h in timeline:
                timeline[h] += 1

    return timeline


def render_timeline_page():
    st.markdown("## Línea de tiempo")
    st.write("Visualiza la cobertura del día.")

    tomorrow = date.today() + timedelta(days=1)

    shifts = get_shifts_for_day(str(tomorrow))

    if not shifts:
        st.warning("No hay turnos registrados para mañana.")
        return

    timeline = generate_timeline(shifts)

    st.markdown(f"### Cobertura para {tomorrow}")

    df = pd.DataFrame({
        "Hora": list(timeline.keys()),
        "Empleados": list(timeline.values())
    })

    st.bar_chart(df.set_index("Hora"))

    st.markdown("### Detalle por hora")

    for hour, count in timeline.items():
        status = "✅" if count >= 3 else "⚠️"
        st.write(f"{hour}:00 → {count} empleados {status}")
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta, datetime
from database.db import get_connection


def get_shifts_for_date(selected_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            shifts.id,
            employees.name,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.coverage_type
        FROM shifts
        JOIN employees ON shifts.employee_id = employees.id
        WHERE shifts.shift_date = ?
        ORDER BY shifts.start_time, employees.name
    """, (str(selected_date),))

    rows = cursor.fetchall()
    conn.close()
    return rows


def parse_datetime(shift_date, time_str):
    return datetime.strptime(f"{shift_date} {time_str}", "%Y-%m-%d %H:%M:%S")


def build_chart_dataframe(shifts):
    data = []

    for shift in shifts:
        start_dt = parse_datetime(shift["shift_date"], shift["start_time"])
        end_dt = parse_datetime(shift["shift_date"], shift["end_time"])

        data.append({
            "Empleado": shift["name"],
            "Inicio": start_dt,
            "Fin": end_dt,
            "Cobertura": shift["coverage_type"],
            "HoraInicio": shift["start_time"][:5],
            "HoraFin": shift["end_time"][:5]
        })

    return pd.DataFrame(data)


def count_people_by_hour_horizontal(shifts):
    if not shifts:
        return pd.DataFrame()

    start_hours = [int(s["start_time"].split(":")[0]) for s in shifts]
    end_hours = [int(s["end_time"].split(":")[0]) for s in shifts]

    min_hour = min(start_hours)
    max_hour = max(end_hours)

    cocina_row = {"Área": "Cocina"}
    servicio_row = {"Área": "Servicio"}
    ambos_row = {"Área": "Ambos"}

    for hour in range(min_hour, max_hour + 1):
        cocina = set()
        servicio = set()
        ambos = set()

        for shift in shifts:
            start = int(shift["start_time"].split(":")[0])
            end = int(shift["end_time"].split(":")[0])

            if start <= hour < end:
                name = shift["name"]
                coverage = shift["coverage_type"]

                if coverage == "Cocina":
                    cocina.add(name)
                elif coverage == "Servicio":
                    servicio.add(name)
                elif coverage == "Ambos":
                    ambos.add(name)

        col = f"{hour}:00"
        cocina_row[col] = len(cocina)
        servicio_row[col] = len(servicio)
        ambos_row[col] = len(ambos)

    return pd.DataFrame([cocina_row, servicio_row, ambos_row])


def render_timeline_page():
    st.title("📊 Cobertura")

    selected_date = st.date_input(
        "Selecciona la fecha",
        value=date.today() + timedelta(days=1)
    )

    shifts = get_shifts_for_date(selected_date)

    if not shifts:
        st.info("No hay turnos registrados para esta fecha.")
        return

    st.subheader("Resumen por hora")
    summary_df = count_people_by_hour_horizontal(shifts)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Personal activo")
    chart_df = build_chart_dataframe(shifts)

    fig = px.timeline(
        chart_df,
        x_start="Inicio",
        x_end="Fin",
        y="Empleado",
        color="Cobertura",
        color_discrete_map={
            "Cocina": "#f1c232",
            "Servicio": "#93c47d",
            "Ambos": "#6fa8dc"
        }
    )

    for _, row in chart_df.iterrows():
        fig.add_annotation(
            x=row["Inicio"],
            y=row["Empleado"],
            text=row["HoraInicio"],
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(color="black", size=12)
        )

        fig.add_annotation(
            x=row["Fin"],
            y=row["Empleado"],
            text=row["HoraFin"],
            showarrow=False,
            xanchor="right",
            yanchor="middle",
            font=dict(color="black", size=12)
        )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Hora",
        yaxis_title="Empleado",
        legend_title="Cobertura",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
import sqlite3
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "schedules.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de empleados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role_type TEXT NOT NULL CHECK(role_type IN ('Cocina', 'Servicio', 'Ambos'))
        )
    """)

    # Tabla de turnos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            shift_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            coverage_type TEXT NOT NULL CHECK(coverage_type IN ('Cocina', 'Servicio', 'Ambos')),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    # Tabla de asignaciones por hora
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shift_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            hour INTEGER NOT NULL,
            position TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    conn.commit()
    conn.close()


def reset_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS shift_assignments")
    cursor.execute("DROP TABLE IF EXISTS shifts")
    cursor.execute("DROP TABLE IF EXISTS employees")

    conn.commit()
    conn.close()

    init_db()


def assign_position(employee_id, date, hour, position):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM shift_assignments
        WHERE employee_id = ? AND date = ? AND hour = ?
    """, (employee_id, date, hour))

    cursor.execute("""
        INSERT INTO shift_assignments (employee_id, date, hour, position)
        VALUES (?, ?, ?, ?)
    """, (employee_id, date, hour, position))

    conn.commit()
    conn.close()


def get_assignments(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_id, hour, position
        FROM shift_assignments
        WHERE date = ?
    """, (date,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_employees():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM employees")

    rows = cursor.fetchall()
    conn.close()

    return rows
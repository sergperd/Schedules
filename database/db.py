import sqlite3
from pathlib import Path

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role_type TEXT NOT NULL CHECK(role_type IN ('Cocina', 'Servicio', 'Ambos'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            shift_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            coverage_type TEXT NOT NULL CHECK(coverage_type IN ('Cocina', 'Servicio', 'Ambos')),
            note TEXT DEFAULT '',
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    # Si la tabla ya existía sin la columna note, intentamos agregarla
    try:
        cursor.execute("ALTER TABLE shifts ADD COLUMN note TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def get_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role_type FROM employees ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_shifts_for_date(selected_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            shifts.id,
            shifts.employee_id,
            employees.name,
            employees.role_type,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.coverage_type,
            shifts.note
        FROM shifts
        JOIN employees ON shifts.employee_id = employees.id
        WHERE shifts.shift_date = ?
        ORDER BY shifts.start_time, employees.name
    """, (str(selected_date),))

    rows = cursor.fetchall()
    conn.close()
    return rows
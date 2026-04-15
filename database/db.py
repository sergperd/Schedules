import sqlite3
from pathlib import Path

# Ruta absoluta al archivo de base de datos
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "schedules.db"


def get_connection():
    """
    Crea y devuelve una conexión a la base de datos SQLite.
    """
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Crea las tablas principales de la app si no existen.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            area_id INTEGER NOT NULL,
            FOREIGN KEY (area_id) REFERENCES areas (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_positions (
            employee_id INTEGER NOT NULL,
            position_id INTEGER NOT NULL,
            PRIMARY KEY (employee_id, position_id),
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (position_id) REFERENCES positions (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            shift_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            break_start TEXT,
            break_end TEXT,
            assigned_position_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (assigned_position_id) REFERENCES positions (id)
        )
    """)

    conn.commit()
    conn.close()


def seed_initial_data():
    """
    Inserta las áreas base si no existen.
    """
    conn = get_connection()
    cursor = conn.cursor()

    default_areas = ["Servicio", "Cocina"]

    for area in default_areas:
        cursor.execute("""
            INSERT OR IGNORE INTO areas (name)
            VALUES (?)
        """, (area,))

    conn.commit()
    conn.close()
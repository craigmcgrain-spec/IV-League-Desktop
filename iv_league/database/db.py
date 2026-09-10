import sqlite3
import os
import sys


def _get_db_dir():
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
        else:
            base = os.path.expanduser('~')
        return os.path.join(base, '.iv_league')
    return os.path.dirname(__file__)


DB_PATH = os.path.join(_get_db_dir(), "iv_league.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT,
            mrn TEXT,
            facility_id INTEGER,
            room TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            facility_id INTEGER,
            task_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            gauge TEXT,
            side TEXT,
            location TEXT,
            notes TEXT,
            clinician_name TEXT,
            clinician_credentials TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (facility_id) REFERENCES facilities(id),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id INTEGER,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (facility_id) REFERENCES facilities(id)
        );

        CREATE TABLE IF NOT EXISTS clinicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            credentials TEXT NOT NULL,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT DEFAULT 'The IV League II',
            street TEXT,
            city TEXT,
            zip TEXT,
            phone TEXT,
            contact_name TEXT,
            contact_email TEXT
        );

        CREATE TABLE IF NOT EXISTS pricing (
            task_id INTEGER PRIMARY KEY,
            price REAL DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );
    """)

    default_tasks = [
        "IV Insertion",
        "Midline Insertion",
        "PICC Insertion",
        "Dressing Change",
        "Blood Draw",
        "Troubleshoot",
        "Port Access",
        "Supplies: IV",
        "Supplies: Midline",
        "Supplies: PICC",
        "Supplies: Port Access",
    ]
    for task in default_tasks:
        cursor.execute(
            "INSERT OR IGNORE INTO tasks (name) VALUES (?)", (task,)
        )

    cursor.execute(
        "INSERT OR IGNORE INTO clinicians (name, credentials, is_default) VALUES (?, ?, ?)",
        ("Select Clinician", "", 1)
    )

    cursor.execute(
        "DELETE FROM clinicians WHERE name = 'Select Clinician' AND id NOT IN ("
        "SELECT MIN(id) FROM clinicians WHERE name = 'Select Clinician')"
    )

    cursor.execute(
        "UPDATE clinicians SET is_default = 1 WHERE name = 'Select Clinician' "
        "AND NOT EXISTS (SELECT 1 FROM clinicians WHERE is_default = 1 AND name != 'Select Clinician')"
    )

    conn.commit()
    conn.close()
    _migrate_add_clinician_columns()
    _migrate_add_facility_details()
    _migrate_add_attempts()
    _migrate_add_company_info()


def _migrate_add_clinician_columns():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE records ADD COLUMN clinician_name TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE records ADD COLUMN clinician_credentials TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def _migrate_add_facility_details():
    conn = get_connection()
    cursor = conn.cursor()
    for col in ("address", "phone", "contact_name", "contact_email",
                "street", "city", "zip"):
        try:
            cursor.execute(f"ALTER TABLE facilities ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def _migrate_add_attempts():
    conn = get_connection()
    try:
        conn.execute("ALTER TABLE records ADD COLUMN attempts INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE records ADD COLUMN cap_change INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def _migrate_add_company_info():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT DEFAULT 'The IV League II',
            street TEXT,
            city TEXT,
            zip TEXT,
            phone TEXT,
            contact_name TEXT,
            contact_email TEXT
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO company_info (id, name) VALUES (1, 'The IV League II')
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pricing (
            task_id INTEGER PRIMARY KEY,
            price REAL DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    _migrate_add_clinician_columns()
    print(f"Database initialized at {DB_PATH}")

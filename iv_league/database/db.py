import sqlite3
import os
import sys


DB_DIR = os.path.expanduser("~/.iv_league")
DB_PATH = os.path.join(DB_DIR, "iv_league.db")

_current_connection = None


def _ensure_db_dir():
    os.makedirs(DB_DIR, exist_ok=True)


def get_connection():
    """Get a database connection with WAL mode and foreign keys enabled.
    
    Uses a module-level singleton connection for thread safety and performance.
    """
    global _current_connection
    
    if _current_connection is None:
        _ensure_db_dir()
        _current_connection = sqlite3.connect(DB_PATH, timeout=30)
        _current_connection.row_factory = sqlite3.Row
        _current_connection.execute("PRAGMA journal_mode=WAL")
        _current_connection.execute("PRAGMA foreign_keys=ON")
        _current_connection.execute("PRAGMA busy_timeout=5000")
    
    return _current_connection


def close_connection():
    """Close the shared database connection. Used for cleanup on exit."""
    global _current_connection
    if _current_connection is not None:
        try:
            _current_connection.close()
        except Exception:
            pass
        _current_connection = None


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            name TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

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

    # Track initial schema version
    cursor.execute(
        "INSERT OR IGNORE INTO schema_migrations (name) VALUES (?)",
        ("initial_schema",)
    )

    default_tasks = [
        "IV Insertion",
        "Midline Insertion",
        "PICC Insertion",
        "Dressing Change",
        "Blood Draw",
        "Troubleshoot",
        "Port Insertion",
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
    _migrate_add_clinician_columns()
    _migrate_add_facility_details()
    _migrate_add_attempts()
    _migrate_add_company_info_and_pricing()


def _migration_applied(name):
    """Check if a migration has already been applied."""
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM schema_migrations WHERE name = ?", (name,)
    ).fetchone()
    return row is not None


def _mark_migration_applied(name):
    """Mark a migration as applied."""
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO schema_migrations (name) VALUES (?)", (name,)
    )
    conn.commit()


def _migrate_add_clinician_columns():
    if _migration_applied("add_clinician_columns"):
        return
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
    _mark_migration_applied("add_clinician_columns")


def _migrate_add_facility_details():
    if _migration_applied("add_facility_details"):
        return
    conn = get_connection()
    cursor = conn.cursor()
    for col in ("address", "phone", "contact_name", "contact_email",
                "street", "city", "zip"):
        try:
            cursor.execute(f"ALTER TABLE facilities ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    _mark_migration_applied("add_facility_details")


def _migrate_add_attempts():
    if _migration_applied("add_attempts"):
        return
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
    _mark_migration_applied("add_attempts")


def _migrate_add_company_info_and_pricing():
    if _migration_applied("add_company_info_and_pricing"):
        return
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
    _mark_migration_applied("add_company_info_and_pricing")


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")

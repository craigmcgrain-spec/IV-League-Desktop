from .db import get_connection


# ---------------------------------------------------------------------------
# Facilities
# ---------------------------------------------------------------------------

def get_all_facilities():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM facilities ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_facility(name):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO facilities (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def get_facility_id(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM facilities WHERE name = ?", (name,)
    ).fetchone()
    conn.close()
    return row["id"] if row else None


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

def get_or_create_client(name, facility_id, dob=None, mrn=None, room=None):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM clients WHERE name = ? AND facility_id = ?",
        (name, facility_id),
    ).fetchone()
    if row:
        client_id = row["id"]
    else:
        cur = conn.execute(
            "INSERT INTO clients (name, facility_id, dob, mrn, room) VALUES (?, ?, ?, ?, ?)",
            (name, facility_id, dob, mrn, room),
        )
        client_id = cur.lastrowid
    conn.commit()
    conn.close()
    return client_id


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task_id(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM tasks WHERE name = ?", (name,)
    ).fetchone()
    conn.close()
    return row["id"] if row else None


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

def add_record(client_id, facility_id, task_id, date, time,
               gauge=None, side=None, location=None, notes=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO records
           (client_id, facility_id, task_id, date, time, gauge, side, location, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (client_id, facility_id, task_id, date, time, gauge, side, location, notes),
    )
    conn.commit()
    conn.close()


def search_records(facility_id=None, start_date=None, end_date=None,
                   task_id=None):
    conn = get_connection()
    query = """
        SELECT r.*, c.name AS client_name, f.name AS facility_name,
               t.name AS task_name
        FROM records r
        JOIN clients c ON r.client_id = c.id
        JOIN facilities f ON r.facility_id = f.id
        JOIN tasks t ON r.task_id = t.id
        WHERE 1=1
    """
    params = []

    if facility_id:
        query += " AND r.facility_id = ?"
        params.append(facility_id)
    if start_date:
        query += " AND r.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND r.date <= ?"
        params.append(end_date)
    if task_id:
        query += " AND r.task_id = ?"
        params.append(task_id)

    query += " ORDER BY r.date DESC, r.time DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_record(record_id):
    conn = get_connection()
    conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def get_invoice_records(facility_id, start_date, end_date):
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.name AS task_name, COUNT(*) AS qty
           FROM records r
           JOIN tasks t ON r.task_id = t.id
           WHERE r.facility_id = ? AND r.date >= ? AND r.date <= ?
           GROUP BY t.name""",
        (facility_id, start_date, end_date),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_invoice(facility_id, start_date, end_date, total):
    conn = get_connection()
    conn.execute(
        "INSERT INTO invoices (facility_id, start_date, end_date, total) VALUES (?, ?, ?, ?)",
        (facility_id, start_date, end_date, total),
    )
    conn.commit()
    conn.close()

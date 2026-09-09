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


def get_facility(facility_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM facilities WHERE id = ?", (facility_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_facility(facility_id, name=None, address=None, phone=None,
                    contact_name=None, contact_email=None,
                    street=None, city=None, zip=None):
    conn = get_connection()
    fields = []
    values = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if address is not None:
        fields.append("address = ?")
        values.append(address)
    if phone is not None:
        fields.append("phone = ?")
        values.append(phone)
    if contact_name is not None:
        fields.append("contact_name = ?")
        values.append(contact_name)
    if contact_email is not None:
        fields.append("contact_email = ?")
        values.append(contact_email)
    if street is not None:
        fields.append("street = ?")
        values.append(street)
    if city is not None:
        fields.append("city = ?")
        values.append(city)
    if zip is not None:
        fields.append("zip = ?")
        values.append(zip)
    if fields:
        values.append(facility_id)
        conn.execute(
            f"UPDATE facilities SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Clinicians
# ---------------------------------------------------------------------------

def get_all_clinicians():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clinicians ORDER BY is_default DESC, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_clinician(name, credentials, is_default=0):
    conn = get_connection()
    conn.execute(
        "INSERT INTO clinicians (name, credentials, is_default) VALUES (?, ?, ?)",
        (name, credentials, is_default),
    )
    conn.commit()
    conn.close()


def get_clinician_id(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM clinicians WHERE name = ?", (name,)
    ).fetchone()
    conn.close()
    return row["id"] if row else None


def set_default_clinician(clinician_id):
    conn = get_connection()
    conn.execute(
        "UPDATE clinicians SET is_default = CASE WHEN id = ? THEN 1 ELSE 0 END",
        (clinician_id,),
    )
    conn.commit()
    conn.close()


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

def record_exists(client_id, facility_id, task_id, date, time):
    conn = get_connection()
    row = conn.execute(
        """SELECT id FROM records
           WHERE client_id = ? AND facility_id = ? AND task_id = ?
           AND date = ? AND time = ?""",
        (client_id, facility_id, task_id, date, time),
    ).fetchone()
    conn.close()
    return row is not None


def add_record(client_id, facility_id, task_id, date, time,
               gauge=None, side=None, location=None, notes=None,
               clinician_name=None, clinician_credentials=None,
               attempts=None, cap_change=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO records
           (client_id, facility_id, task_id, date, time, gauge, side, location,
            notes, clinician_name, clinician_credentials, attempts, cap_change)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (client_id, facility_id, task_id, date, time, gauge, side, location,
         notes, clinician_name, clinician_credentials, attempts, cap_change),
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


# ---------------------------------------------------------------------------
# Company Info
# ---------------------------------------------------------------------------

def get_company_info():
    conn = get_connection()
    row = conn.execute("SELECT * FROM company_info WHERE id = 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "name": "The IV League II",
        "street": "",
        "city": "",
        "zip": "",
        "phone": "",
        "contact_name": "",
        "contact_email": "",
    }


def save_company_info(info):
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO company_info (id, name, street, city, zip, phone, contact_name, contact_email)
           VALUES (1, ?, ?, ?, ?, ?, ?, ?)""",
        (
            info.get("name", "The IV League II"),
            info.get("street", ""),
            info.get("city", ""),
            info.get("zip", ""),
            info.get("phone", ""),
            info.get("contact_name", ""),
            info.get("contact_email", ""),
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------

def get_all_pricing():
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.name AS task_name, p.task_id, p.price
           FROM pricing p
           JOIN tasks t ON p.task_id = t.id
           ORDER BY t.name"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_price(task_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT price FROM pricing WHERE task_id = ?", (task_id,)
    ).fetchone()
    conn.close()
    return row["price"] if row else 0


def set_price(task_id, price):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO pricing (task_id, price) VALUES (?, ?)",
        (task_id, price),
    )
    conn.commit()
    conn.close()


def get_invoice_records_priced(facility_id, start_date, end_date):
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.name AS task_name, COUNT(*) AS qty,
                  COALESCE(p.price, 0) AS price,
                  COUNT(*) * COALESCE(p.price, 0) AS subtotal
           FROM records r
           JOIN tasks t ON r.task_id = t.id
           LEFT JOIN pricing p ON r.task_id = p.task_id
           WHERE r.facility_id = ? AND r.date >= ? AND r.date <= ?
           GROUP BY t.name""",
        (facility_id, start_date, end_date),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice_items_dated(facility_id, start_date, end_date):
    conn = get_connection()
    rows = conn.execute(
        """SELECT r.date, r.time, c.name AS client_name, t.name AS task_name,
                  COALESCE(p.price, 0) AS price
           FROM records r
           JOIN clients c ON r.client_id = c.id
           JOIN tasks t ON r.task_id = t.id
           LEFT JOIN pricing p ON r.task_id = p.task_id
           WHERE r.facility_id = ? AND r.date >= ? AND r.date <= ?
           ORDER BY r.date, r.time""",
        (facility_id, start_date, end_date),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


SUPPLIES_MAP = {
    "IV Insertion": "Supplies: IV",
    "Midline Insertion": "Supplies: Midline",
    "PICC Insertion": "Supplies: PICC",
    "Port Access": "Supplies: Port Access",
}


def get_supplies_items(facility_id, start_date, end_date):
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.name AS task_name,
                  SUM(r.attempts - 1) AS extra_attempts
           FROM records r
           JOIN tasks t ON r.task_id = t.id
           WHERE r.facility_id = ? AND r.date >= ? AND r.date <= ?
             AND r.attempts > 1
             AND t.name IN (?, ?, ?, ?)
           GROUP BY t.name""",
        (facility_id, start_date, end_date,
         "IV Insertion", "Midline Insertion", "PICC Insertion", "Port Access"),
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        parent_task = row["task_name"]
        supplies_name = SUPPLIES_MAP.get(parent_task)
        if supplies_name:
            supplies_task_id = get_task_id(supplies_name)
            price = get_price(supplies_task_id) if supplies_task_id else 0
            result.append({
                "task_name": supplies_name,
                "qty": row["extra_attempts"],
                "price": price,
                "subtotal": row["extra_attempts"] * price,
            })
    return result

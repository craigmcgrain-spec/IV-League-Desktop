from .db import get_connection


# ---------------------------------------------------------------------------
# Facilities
# ---------------------------------------------------------------------------

def get_all_facilities():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM facilities ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def add_facility(name):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO facilities (name) VALUES (?)", (name,))
    conn.commit()


def get_facility_id(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM facilities WHERE name = ?", (name,)
    ).fetchone()
    return row["id"] if row else None


def get_facility(facility_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM facilities WHERE id = ?", (facility_id,)
    ).fetchone()
    return dict(row) if row else None


def facility_has_records(facility_id):
    """Check if a facility has any records linked to it."""
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as count FROM records WHERE facility_id = ?", (facility_id,)
    ).fetchone()
    return row["count"] > 0


def delete_facility(facility_id):
    """Delete a facility only if it has no linked records and invoices."""
    if facility_has_records(facility_id):
        return False, "Cannot delete facility with existing records."
    
    conn = get_connection()
    inv = conn.execute(
        "SELECT COUNT(*) as count FROM invoices WHERE facility_id = ?", (facility_id,)
    ).fetchone()
    if inv["count"] > 0:
        return False, "Cannot delete facility with existing invoices."

    conn.execute("DELETE FROM clients WHERE facility_id = ?", (facility_id,))
    conn.execute("DELETE FROM facilities WHERE id = ?", (facility_id,))
    conn.commit()
    return True, "Facility deleted successfully."


def update_facility(facility_id, name, phone, contact_name, contact_email,
                    street, city, zip):
    conn = get_connection()
    conn.execute(
        """UPDATE facilities SET name = ?, phone = ?, contact_name = ?,
           contact_email = ?, street = ?, city = ?, zip = ? WHERE id = ?""",
        (name, phone, contact_name, contact_email, street, city, zip, facility_id),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Clinicians
# ---------------------------------------------------------------------------

def get_all_clinicians():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clinicians ORDER BY is_default DESC, name").fetchall()
    return [dict(r) for r in rows]


def add_clinician(name, credentials, is_default=0):
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM clinicians WHERE name = ? AND credentials = ?",
        (name, credentials),
    ).fetchone()
    if existing:
        return
    conn.execute(
        "INSERT INTO clinicians (name, credentials, is_default) VALUES (?, ?, ?)",
        (name, credentials, is_default),
    )
    conn.commit()


def set_default_clinician(clinician_id):
    conn = get_connection()
    conn.execute(
        "UPDATE clinicians SET is_default = CASE WHEN id = ? THEN 1 ELSE 0 END",
        (clinician_id,),
    )
    conn.commit()


def get_clinician(clinician_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM clinicians WHERE id = ?", (clinician_id,)
    ).fetchone()
    return dict(row) if row else None


def update_clinician(clinician_id, name, credentials):
    conn = get_connection()
    conn.execute(
        "UPDATE clinicians SET name = ?, credentials = ? WHERE id = ?",
        (name, credentials, clinician_id),
    )
    conn.commit()


def delete_clinician(clinician_id):
    conn = get_connection()
    clinician = get_clinician(clinician_id)
    if not clinician:
        return False, "Clinician not found."
    if clinician["name"] == "Select Clinician":
        return False, "Cannot delete placeholder clinician."

    was_default = clinician.get("is_default", 0)
    conn.execute("DELETE FROM clinicians WHERE id = ?", (clinician_id,))

    if was_default:
        fallback = conn.execute(
            "SELECT id FROM clinicians WHERE name != 'Select Clinician' ORDER BY id LIMIT 1"
        ).fetchone()
        if fallback:
            conn.execute("UPDATE clinicians SET is_default = 1 WHERE id = ?", (fallback["id"],))
        else:
            conn.execute("UPDATE clinicians SET is_default = 1 WHERE name = 'Select Clinician'")

    conn.commit()
    return True, "Clinician deleted successfully."


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
    return client_id


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def get_task_id(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM tasks WHERE name = ?", (name,)
    ).fetchone()
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
    return row is not None


def add_record(client_id, facility_id, task_id, date, time,
               gauge=None, side=None, location=None, notes=None,
               clinician_name=None, clinician_credentials=None,
               cap_change=None, supply_values=None):
    conn = get_connection()

    if supply_values:
        supply_values = dict(supply_values)
        if "cap_change" in supply_values:
            cap_change = supply_values.pop("cap_change")

    base_cols = "client_id, facility_id, task_id, date, time, gauge, side, location, notes, clinician_name, clinician_credentials, cap_change"
    base_vals = [client_id, facility_id, task_id, date, time, gauge, side, location, notes, clinician_name, clinician_credentials, cap_change]
    
    if supply_values:
        supply_cols = ", ".join(supply_values.keys())
        supply_placeholders = ", ".join("?" * len(supply_values))
        base_cols += f", {supply_cols}"
        placeholders = ", ".join("?" * len(base_vals)) + f", {supply_placeholders}"
        base_vals.extend(supply_values.values())
    else:
        placeholders = ", ".join("?" * len(base_vals))
    
    conn.execute(
        f"INSERT INTO records ({base_cols}) VALUES ({placeholders})",
        base_vals
    )
    conn.commit()


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
    return [dict(r) for r in rows]


def delete_record(record_id):
    conn = get_connection()
    conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()


def get_record_by_id(record_id):
    conn = get_connection()
    row = conn.execute(
        """SELECT r.*, c.name AS client_name, f.name AS facility_name,
                  t.name AS task_name
           FROM records r
           JOIN clients c ON r.client_id = c.id
           JOIN facilities f ON r.facility_id = f.id
           JOIN tasks t ON r.task_id = t.id
           WHERE r.id = ?""",
        (record_id,)
    ).fetchone()
    if row:
        return dict(row)
    return None


def update_record(record_id, client_id, facility_id, task_id, date, time,
                  gauge=None, side=None, location=None, notes=None,
               clinician_name=None, clinician_credentials=None,
               cap_change=None, supply_values=None):
    conn = get_connection()

    if supply_values:
        supply_values = dict(supply_values)
        if "cap_change" in supply_values:
            cap_change = supply_values.pop("cap_change")

    base_update = """UPDATE records SET
        client_id = ?, facility_id = ?, task_id = ?,
        date = ?, time = ?, gauge = ?, side = ?, location = ?,
        notes = ?, clinician_name = ?, clinician_credentials = ?,
        cap_change = ?"""
    
    params = [client_id, facility_id, task_id,
              date, time, gauge, side, location, notes,
              clinician_name, clinician_credentials,
              cap_change]
    
    if supply_values:
        supply_sets = []
        for col_name, value in supply_values.items():
            supply_sets.append(f"{col_name} = ?")
            params.append(value)
        
        if supply_sets:
            base_update += ", " + ", ".join(supply_sets)
    
    base_update += " WHERE id = ?"
    params.append(record_id)
    
    conn.execute(base_update, params)
    conn.commit()


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def get_next_invoice_number():
    """Generate a sequential invoice number: INV-YYYY-XXXX."""
    import datetime
    conn = get_connection()
    year = datetime.datetime.now().year
    row = conn.execute("SELECT COUNT(*) as count FROM invoices").fetchone()
    count = (row["count"] or 0) + 1
    return f"INV-{year}-{count:04d}"


def save_invoice(facility_id, start_date, end_date, total, invoice_number=None):
    if not invoice_number:
        invoice_number = get_next_invoice_number()
    conn = get_connection()
    conn.execute(
        """INSERT INTO invoices (facility_id, start_date, end_date, total, invoice_number)
           VALUES (?, ?, ?, ?, ?)""",
        (facility_id, start_date, end_date, total, invoice_number),
    )
    conn.commit()
    return invoice_number


def get_all_invoices():
    """Retrieve invoice history ordered by most recent."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT i.*, f.name AS facility_name
           FROM invoices i
           JOIN facilities f ON i.facility_id = f.id
           ORDER BY i.id DESC"""
    ).fetchall()
    return [dict(r) for r in rows]


def get_cap_change_items(facility_id, start_date, end_date):
    """Billed cap changes: total quantity entered in the Cap Change field.

    Legacy records store a 0/1 flag and contribute 1 each.
    """
    conn = get_connection()
    row = conn.execute(
        """SELECT COALESCE(SUM(cap_change), 0) AS qty
           FROM records r
           WHERE r.facility_id = ? AND r.date >= ? AND r.date <= ?""",
        (facility_id, start_date, end_date),
    ).fetchone()
    
    qty = row["qty"] if row else 0
    if qty == 0:
        return []

    task_id = get_task_id("Cap Change")
    price = get_price(task_id) if task_id else 0.0
    return [{
        "task_name": "Cap Change",
        "qty": qty,
        "price": price,
        "subtotal": qty * price,
    }]


# ---------------------------------------------------------------------------
# Company Info
# ---------------------------------------------------------------------------

def get_company_info():
    conn = get_connection()
    row = conn.execute("SELECT * FROM company_info WHERE id = 1").fetchone()
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
    return [dict(r) for r in rows]


def get_price(task_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT price FROM pricing WHERE task_id = ?", (task_id,)
    ).fetchone()
    return row["price"] if row else 0


def set_price(task_id, price):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO pricing (task_id, price) VALUES (?, ?)",
        (task_id, price),
    )
    conn.commit()


def get_task_categories():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, display_order FROM task_categories ORDER BY display_order, name"
    ).fetchall()
    return [dict(r) for r in rows]


def get_tasks_by_category():
    conn = get_connection()
    rows = conn.execute(
        """SELECT t.id, t.name, t.category_id, 
                  COALESCE(tc.name, 'Uncategorized') AS category_name,
                  COALESCE(tc.display_order, 999) AS category_order
           FROM tasks t
           LEFT JOIN task_categories tc ON t.category_id = tc.id
           ORDER BY category_order, tc.name, t.name"""
    ).fetchall()
    
    result = {}
    for row in rows:
        category_name = row["category_name"]
        if category_name not in result:
            result[category_name] = []
        result[category_name].append({
            "id": row["id"],
            "name": row["name"],
            "category_id": row["category_id"]
        })
    
    return result


def get_task_category_name(task_id):
    conn = get_connection()
    row = conn.execute(
        """SELECT tc.name
           FROM tasks t
           LEFT JOIN task_categories tc ON t.category_id = tc.id
           WHERE t.id = ?""",
        (task_id,)
    ).fetchone()
    return row["name"] if row and row["name"] else None


def get_supply_columns():
    conn = get_connection()
    # Cap Change is categorized as Supplies but stores its quantity in the
    # dedicated cap_change column (billed via get_cap_change_items) — keeping
    # it out of this list prevents get_supplies_items from double-billing it.
    rows = conn.execute(
        """SELECT t.id, t.name
           FROM tasks t
           JOIN task_categories tc ON t.category_id = tc.id
           WHERE tc.name = 'Supplies' AND t.name != 'Cap Change'
           ORDER BY t.name"""
    ).fetchall()
    
    supply_columns = []
    for row in rows:
        col_name = row["name"].lower().replace(" ", "_").replace(":", "")
        supply_columns.append({
            "task_id": row["id"],
            "task_name": row["name"],
            "column_name": col_name
        })
    
    return supply_columns


def add_task(name, category_name=None):
    conn = get_connection()
    
    category_id = None
    if category_name:
        row = conn.execute(
            "SELECT id FROM task_categories WHERE name = ?", (category_name,)
        ).fetchone()
        if row:
            category_id = row["id"]
    
    cursor = conn.execute(
        "INSERT INTO tasks (name, category_id) VALUES (?, ?)",
        (name, category_id)
    )
    task_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO pricing (task_id, price) VALUES (?, 0)",
        (task_id,)
    )

    if category_name == "Supplies":
        col_name = name.lower().replace(" ", "_").replace(":", "")
        try:
            conn.execute(f"ALTER TABLE records ADD COLUMN {col_name} REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
    
    conn.commit()
    return task_id


def update_task(task_id, name):
    conn = get_connection()
    conn.execute(
        "UPDATE tasks SET name = ? WHERE id = ?",
        (name, task_id)
    )
    conn.commit()


def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()


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
    return [dict(r) for r in rows]


def get_supplies_items(facility_id, start_date, end_date):
    conn = get_connection()
    supply_cols = get_supply_columns()
    
    result = []
    for supply_col in supply_cols:
        col_name = supply_col['column_name']
        task_name = supply_col['task_name']
        task_id = supply_col['task_id']
        
        row = conn.execute(
            f"""SELECT SUM({col_name}) AS total_qty
               FROM records
               WHERE facility_id = ? AND date >= ? AND date <= ?
                 AND {col_name} IS NOT NULL AND {col_name} > 0""",
            (facility_id, start_date, end_date)
        ).fetchone()
        
        total_qty = row["total_qty"] if row and row["total_qty"] else 0
        if total_qty > 0:
            price = get_price(task_id) if task_id else 0
            result.append({
                "task_name": task_name,
                "qty": total_qty,
                "price": price,
                "subtotal": total_qty * price,
            })
    
    return result

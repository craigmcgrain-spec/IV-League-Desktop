"""Smoke check: `python smoke_test.py` (offscreen Qt, temp DB, no user data touched)."""
import os
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Redirect all runtime data to a temp dir before anything binds DB_DIR.
_tmp = tempfile.mkdtemp(prefix="iv_league_smoke_")
import iv_league.database.db as db
db.DB_DIR = _tmp
db.DB_PATH = os.path.join(_tmp, "test.db")

from PyQt6.QtWidgets import QApplication

app = QApplication([])

from iv_league.database import backup, models
from iv_league.database.db import init_db, close_connection
init_db()

# --- pricing: single table roundtrip ---
models.add_task("Smoke Task", "Procedures")
tid = models.get_task_id("Smoke Task")
assert tid is not None
models.set_price(tid, 42.5)
assert models.get_price(tid) == 42.5
assert any(p["task_id"] == tid for p in models.get_all_pricing())

# --- record form: validation and collect ---
from PyQt6.QtWidgets import QScrollArea
from iv_league.ui.data_entry import DataEntryWidget
from iv_league.ui.edit_record_dialog import EditRecordDialog
from iv_league.ui.record_form import RecordForm

w = DataEntryWidget()
f = w.form
assert isinstance(f, QScrollArea) and f.widgetResizable()

data, err = f.collect()
assert err == "Facility is required.", err

f.facility_combo.setEditText("SmokeFac")
data, err = f.collect()
assert err == "Client name is required.", err

f.name_edit.setText("Smoke Client")
f.time_edit.setText("10:30")
data, err = f.collect()
assert err is None, err
assert data["facility_id"] and data["client_id"] and data["task_id"]
assert data["date"] and data["time"] == "10:30"

# supply parsing: junk -> 0, formatted money -> float
col = next(iter(f.supply_fields))
f.supply_fields[col].setText("abc")
d2, _ = f.collect()
assert d2["supply_values"][col] == 0.0
f.supply_fields[col].setText("$1,000.50")
d2, _ = f.collect()
assert d2["supply_values"][col] == 1000.5

# --- save a record, then edit it through the shared form ---
models.add_record(
    data["client_id"], data["facility_id"], data["task_id"],
    data["date"], data["time"], "22ga", "Right", "Hand", "smoke note",
    None, None, None, {},
)
records = models.search_records(facility_id=data["facility_id"])
assert len(records) == 1
rec = records[0]

dlg = EditRecordDialog(rec)
assert dlg.form.task_combo.currentText() == rec["task_name"]
assert dlg.form.name_edit.text() == "Smoke Client"
ed, eerr = dlg.form.collect()
assert eerr is None, eerr
assert ed["task_id"] == rec["task_id"]

# Cap Change: quantity field in the Supplies group, stored in the cap_change column
assert "cap_change" in f.supply_fields and "cap_change" in dlg.form.supply_fields
f.time_edit.setText("11:45")
f.supply_fields["cap_change"].setText("2")
d3, e3 = f.collect()
assert e3 is None and d3["supply_values"]["cap_change"] == 2.0
models.add_record(
    d3["client_id"], d3["facility_id"], d3["task_id"], d3["date"], d3["time"],
    None, None, None, None, None, None, None, d3["supply_values"],
)
rec2 = next(r for r in models.search_records(facility_id=d3["facility_id"])
            if r["time"] == "11:45")
assert rec2["cap_change"] == 2
caps = models.get_cap_change_items(d3["facility_id"], d3["date"], d3["date"])
assert caps and float(caps[0]["qty"]) == 2.0, caps

# form scoped correctly: entry offers Procedures only, edit offers all
entry_tasks = {f.task_combo.itemText(i) for i in range(f.task_combo.count())}
edit_tasks = {dlg.form.task_combo.itemText(i) for i in range(dlg.form.task_combo.count())}
assert "IV Insertion" in entry_tasks and "Supplies: IV" not in entry_tasks
assert "Supplies: IV" in edit_tasks

# Cap Change lives in the Supplies category but is not a quantity supply column
by_cat = models.get_tasks_by_category()
assert any(t["name"] == "Cap Change" for t in by_cat.get("Supplies", []))
assert not any(t["name"] == "Cap Change" for t in by_cat.get("Procedures", []))
assert "Cap Change" not in entry_tasks and "Cap Change" in edit_tasks
supply_names = {s["task_name"] for s in models.get_supply_columns()}
assert "Cap Change" not in supply_names and "Supplies: IV" in supply_names

# existing-DB upgrade path: migration re-moves Cap Change when re-run
conn = db.get_connection()
conn.execute(
    "UPDATE tasks SET category_id = (SELECT id FROM task_categories WHERE name='Procedures') "
    "WHERE name='Cap Change'"
)
conn.execute("DELETE FROM schema_migrations WHERE name='cap_change_to_supplies'")
conn.commit()
init_db()
by_cat = models.get_tasks_by_category()
assert any(t["name"] == "Cap Change" for t in by_cat.get("Supplies", []))

# --- backup: create, verify, delete (temp dir) ---
path = backup.create_backup(is_auto=False)
assert os.path.exists(path)
ok, msg = backup.verify_backup(path)
assert ok, msg
backup.delete_backup(os.path.basename(path))
assert not os.path.exists(path)

# --- invoice PDF end-to-end (address helper, itemized page) ---
from iv_league.utils.invoice_generator import generate_invoice_pdf
pdf_path = os.path.join(_tmp, "smoke_invoice.pdf")
generate_invoice_pdf(
    pdf_path, "SmokeFac", data["date"], data["date"],
    [{"task_name": "IV Insertion", "qty": 1, "price": 42.5, "subtotal": 42.5}],
    facility_details={"street": "1 Main St", "city": "Springfield", "zip": "12345",
                      "phone": "555", "contact_name": "Jane", "contact_email": "j@x.io"},
    company_info={"name": "The IV League II", "street": "2 Oak Ave", "city": "Shelbyville",
                  "zip": "54321", "phone": "556", "contact_name": "Joe", "contact_email": "joe@x.io"},
    items_dated=[{"date": data["date"], "time": "10:30", "client_name": "Smoke Client",
                  "task_name": "IV Insertion", "price": 42.5}],
    supplies=[{"task_name": "Supplies: IV", "qty": 2, "price": 5.0, "subtotal": 10.0}],
    cap_changes=[{"task_name": "Cap Change", "qty": 1, "price": 3.0, "subtotal": 3.0}],
)
assert os.path.getsize(pdf_path) > 1000

# --- full main window builds offscreen ---
from iv_league.ui.main_window import MainWindow
mw = MainWindow()
assert mw.theme_btn.isCheckable()
assert mw.theme_btn.isChecked() == mw.dark_mode
mw.theme_btn.setChecked(not mw.dark_mode)  # fires toggled -> _apply_theme
assert mw.dark_mode == mw.theme_btn.isChecked()

close_connection()
print("smoke OK")

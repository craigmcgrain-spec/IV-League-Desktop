from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..database import models
from ..utils.csv_parser import parse_csv


class CsvImportDialog(QDialog):
    import_complete = pyqtSignal()
    clinicians_refreshed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import CSV")
        self.setMinimumSize(700, 500)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.info_label = QLabel("Select a CSV file to import.")
        layout.addWidget(self.info_label)

        btn_row = QHBoxLayout()
        self.open_btn = QPushButton("Open CSV...")
        self.open_btn.clicked.connect(self._open_file)
        self.import_btn = QPushButton("Import")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._do_import)
        btn_row.addStretch()
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(self.import_btn)
        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            self.rows = parse_csv(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if not self.rows:
            QMessageBox.information(self, "Empty", "No data rows found.")
            return

        headers = list(self.rows[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.rows))

        for i, row in enumerate(self.rows):
            for j, key in enumerate(headers):
                self.table.setItem(i, j, QTableWidgetItem(str(row.get(key, ""))))

        self.info_label.setText(f"Preview: {len(self.rows)} row(s) found.")
        self.import_btn.setEnabled(True)

    def _do_import(self):
        from ..database.db import get_connection
        
        conn = get_connection()
        count = 0
        skipped = 0
        errors = 0
        
        try:
            conn.execute("BEGIN")
            
            for row in self.rows:
                facility_name = row.get("facility", "").strip()
                client_name = row.get("name", "").strip()
                date_str = row.get("date", "").strip()
                time_str = row.get("time", "").strip()
                task_name = row.get("task", "").strip()

                if not all([facility_name, client_name, date_str, time_str, task_name]):
                    continue

                try:
                    models.add_facility(facility_name)
                    facility_id = models.get_facility_id(facility_name)
                    room = row.get("room") or None
                    client_id = models.get_or_create_client(
                        client_name, facility_id, room=room
                    )
                    task_id = models.get_task_id(task_name)

                    if not task_id:
                        continue

                    if models.record_exists(client_id, facility_id, task_id, date_str, time_str):
                        skipped += 1
                        continue

                    c_name = row.get("clinician_name")
                    c_cred = row.get("clinician_credentials")
                    if c_name and c_name.strip() and c_name.strip() != "Select Clinician":
                        models.add_clinician(c_name.strip(), (c_cred or "").strip())

                    models.add_record(
                        client_id, facility_id, task_id,
                        date_str, time_str,
                        row.get("gauge") or None,
                        row.get("side") or None,
                        row.get("location") or None,
                        row.get("notes") or None,
                        c_name or None,
                        c_cred or None,
                        row.get("cap_change", 0),
                    )
                    count += 1
                except Exception:
                    errors += 1

            conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Import Failed", f"An error occurred during import:\n{str(e)}")
            return

        msg = f"Imported {count} record(s)."
        if skipped:
            msg += f"\n{skipped} duplicate(s) skipped."
        if errors:
            msg += f"\n{errors} row(s) had errors and were skipped."
        QMessageBox.information(self, "Import Complete", msg)
        self.import_complete.emit()
        self.clinicians_refreshed.emit()
        self.accept()

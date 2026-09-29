from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from ..database import models
from .record_form import RecordForm


class DataEntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.form = RecordForm()
        root.addWidget(self.form, 1)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save Record")
        self.save_btn.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        root.addLayout(btn_row)

    def refresh_facilities(self):
        self.form.refresh_facilities()

    def refresh_clinicians(self):
        self.form.refresh_clinicians()

    def _refresh_tasks(self):
        self.form._refresh_tasks()

    def _save(self):
        data, error = self.form.collect()
        if error:
            QMessageBox.warning(self, "Error", error)
            return

        try:
            models.add_record(
                data["client_id"], data["facility_id"], data["task_id"],
                data["date"], data["time"],
                data["gauge"], data["side"], data["location"], data["notes"],
                data["clinician_name"], data["clinician_credentials"],
                None,
                data["supply_values"],
            )

            self.form.refresh_facilities()
            QMessageBox.information(self, "Saved", "Record saved successfully.")
            self.form.name_edit.clear()
            self.form.notes_edit.clear()
            for field in self.form.supply_fields.values():
                field.clear()
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"An error occurred while saving the record:\n{str(e)}"
            )

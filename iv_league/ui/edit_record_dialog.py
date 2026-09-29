from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
)
from ..database import models
from .record_form import RecordForm


class EditRecordDialog(QDialog):
    def __init__(self, record_data, parent=None):
        super().__init__(parent)
        self.record_data = record_data
        self.setWindowTitle("Edit Record")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        self.form = RecordForm(all_tasks=True)
        self.form.set_record(record_data)
        layout.addWidget(self.form, 1)

        btn_layout = QHBoxLayout()
        self.update_btn = QPushButton("Update Record")
        self.update_btn.clicked.connect(self._update_record)
        self.delete_btn = QPushButton("Delete Record")
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_btn.clicked.connect(self._delete_record)
        btn_layout.addStretch()
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

    def _update_record(self):
        data, error = self.form.collect()
        if error:
            QMessageBox.warning(self, "Error", error)
            return

        try:
            models.update_record(
                self.record_data["id"],
                data["client_id"], data["facility_id"], data["task_id"],
                data["date"], data["time"],
                data["gauge"], data["side"], data["location"], data["notes"],
                data["clinician_name"], data["clinician_credentials"],
                None,
                data["supply_values"],
            )
            QMessageBox.information(self, "Success", "Record updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"An error occurred while updating the record:\n{str(e)}"
            )

    def _delete_record(self):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                models.delete_record(self.record_data["id"])
                QMessageBox.information(self, "Success", "Record deleted successfully.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"An error occurred while deleting the record:\n{str(e)}"
                )

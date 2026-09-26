from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLabel, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..database import models


class ClinicianDirectoryWidget(QWidget):
    clinician_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._selected_id = None
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -- Add clinician row --
        add_row = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("New clinician name...")
        self.cred_edit = QLineEdit()
        self.cred_edit.setPlaceholderText("Credentials (e.g. RN)")
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._add)
        self.name_edit.returnPressed.connect(self._add)
        self.cred_edit.returnPressed.connect(self._add)
        add_row.addWidget(self.name_edit)
        add_row.addWidget(self.cred_edit)
        add_row.addWidget(self.add_btn)
        layout.addLayout(add_row)

        # -- Table --
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Credentials", "Default"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.currentCellChanged.connect(self._on_select)
        layout.addWidget(self.table)

        # -- Detail & Edit panel --
        detail_group = QGroupBox("Clinician Details")
        detail_form = QFormLayout()
        detail_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.detail_name = QLineEdit()
        detail_form.addRow("Name:", self.detail_name)

        self.detail_cred = QLineEdit()
        detail_form.addRow("Credentials:", self.detail_cred)

        detail_group.setLayout(detail_form)
        layout.addWidget(detail_group)

        # -- Action Buttons --
        btn_row = QHBoxLayout()
        self.default_btn = QPushButton("Set Selected as Default")
        self.default_btn.setEnabled(False)
        self.default_btn.clicked.connect(self._set_default)

        self.save_btn = QPushButton("Save Details")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_details)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_selected)

        btn_row.addWidget(self.default_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.delete_btn)
        layout.addLayout(btn_row)

    def _refresh(self):
        clinicians = [c for c in models.get_all_clinicians() if c["name"] != "Select Clinician"]
        self.table.setRowCount(len(clinicians))
        for i, c in enumerate(clinicians):
            name_item = QTableWidgetItem(c["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, c["id"])
            self.table.setItem(i, 0, name_item)

            cred_item = QTableWidgetItem(c["credentials"])
            cred_item.setData(Qt.ItemDataRole.UserRole, c["id"])
            self.table.setItem(i, 1, cred_item)

            default_mark = "✓" if c["is_default"] else ""
            def_item = QTableWidgetItem(default_mark)
            def_item.setData(Qt.ItemDataRole.UserRole, c["id"])
            def_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, def_item)

        if self._selected_id is not None:
            found = False
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == self._selected_id:
                    self.table.selectRow(row)
                    found = True
                    break
            if not found:
                self._clear_selection()
        else:
            self._clear_selection()

    def _clear_selection(self):
        self._selected_id = None
        self.detail_name.clear()
        self.detail_cred.clear()
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.default_btn.setEnabled(False)

    def _on_select(self, row, col, prev_row, prev_col):
        if row < 0 or row >= self.table.rowCount():
            self._clear_selection()
            return
        item = self.table.item(row, 0)
        if not item:
            return
        clinician_id = item.data(Qt.ItemDataRole.UserRole)
        clinician = models.get_clinician(clinician_id)
        if not clinician:
            return

        self._selected_id = clinician_id
        self.detail_name.setText(clinician["name"])
        self.detail_cred.setText(clinician.get("credentials") or "")
        self.save_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.default_btn.setEnabled(True)

    def _add(self):
        name = self.name_edit.text().strip()
        cred = self.cred_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Name is required.")
            return
        if not cred:
            QMessageBox.warning(self, "Error", "Credentials are required.")
            return

        models.add_clinician(name, cred)
        self.name_edit.clear()
        self.cred_edit.clear()
        self._refresh()
        self.clinician_added.emit()

    def _save_details(self):
        if not self._selected_id:
            return
        name = self.detail_name.text().strip()
        cred = self.detail_cred.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Name cannot be empty.")
            return

        models.update_clinician(self._selected_id, name, cred)
        self._refresh()
        self.clinician_added.emit()
        QMessageBox.information(self, "Saved", "Clinician details updated.")

    def _delete_selected(self):
        if not self._selected_id:
            QMessageBox.warning(self, "Error", "Select a clinician first.")
            return

        clinician = models.get_clinician(self._selected_id)
        name = clinician["name"] if clinician else "this clinician"

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete clinician '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            success, message = models.delete_clinician(self._selected_id)
            if success:
                self._clear_selection()
                self._refresh()
                self.clinician_added.emit()
                QMessageBox.information(self, "Deleted", message)
            else:
                QMessageBox.warning(self, "Cannot Delete", message)

    def _set_default(self):
        if not self._selected_id:
            QMessageBox.warning(self, "Error", "Select a clinician first.")
            return
        models.set_default_clinician(self._selected_id)
        self._refresh()
        self.clinician_added.emit()

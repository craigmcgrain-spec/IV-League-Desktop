from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..database import models


class ClinicianDirectoryWidget(QWidget):
    clinician_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -- Add clinician row --
        add_row = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Clinician name...")
        self.cred_edit = QLineEdit()
        self.cred_edit.setPlaceholderText("Credentials (e.g. RN)")
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._add)
        self.name_edit.returnPressed.connect(self._add)
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
        layout.addWidget(self.table)

        # -- Set Default button --
        btn_row = QHBoxLayout()
        self.default_btn = QPushButton("Set Selected as Default")
        self.default_btn.clicked.connect(self._set_default)
        btn_row.addStretch()
        btn_row.addWidget(self.default_btn)
        layout.addLayout(btn_row)

    def _refresh(self):
        clinicians = models.get_all_clinicians()
        self.table.setRowCount(len(clinicians))
        for i, c in enumerate(clinicians):
            self.table.setItem(i, 0, QTableWidgetItem(c["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(c["credentials"]))
            default_mark = "✓" if c["is_default"] else ""
            self.table.setItem(i, 2, QTableWidgetItem(default_mark))

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

    def _set_default(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Error", "Select a clinician first.")
            return
        row = rows[0].row()
        clinician_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if clinician_id is None:
            clinicians = models.get_all_clinicians()
            clinician_id = clinicians[row]["id"]
        models.set_default_clinician(clinician_id)
        self._refresh()
        self.clinician_added.emit()

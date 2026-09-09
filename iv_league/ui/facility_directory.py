from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..database import models


class FacilityDirectoryWidget(QWidget):
    facility_added = pyqtSignal()
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -- Add facility row --
        add_row = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("New facility name...")
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._add)
        self.name_edit.returnPressed.connect(self._add)
        add_row.addWidget(self.name_edit)
        add_row.addWidget(self.add_btn)
        layout.addLayout(add_row)

        # -- Table --
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Facility Name"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def _refresh(self):
        facilities = models.get_all_facilities()
        self.table.setRowCount(len(facilities))
        for i, f in enumerate(facilities):
            self.table.setItem(i, 0, QTableWidgetItem(f["name"]))

    def _add(self):
        name = self.name_edit.text().strip()
        if not name:
            return

        existing = models.get_facility_id(name)
        if existing:
            QMessageBox.warning(self, "Duplicate", "Facility already exists.")
            return

        models.add_facility(name)
        self.name_edit.clear()
        self._refresh()
        self.facility_added.emit()

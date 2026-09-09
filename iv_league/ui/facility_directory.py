from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFormLayout, QGroupBox, QLabel
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
        self.table.currentCellChanged.connect(self._on_select)
        layout.addWidget(self.table)

        # -- Detail panel --
        detail_group = QGroupBox("Facility Details")
        detail_form = QFormLayout()
        detail_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.detail_name = QLineEdit()
        detail_form.addRow("Name:", self.detail_name)

        self.detail_street = QLineEdit()
        detail_form.addRow("Street:", self.detail_street)

        self.detail_city = QLineEdit()
        detail_form.addRow("City:", self.detail_city)

        self.detail_zip = QLineEdit()
        detail_form.addRow("Zip:", self.detail_zip)

        self.detail_phone = QLineEdit()
        self.detail_phone.setInputMask("(999) 000-0000;_")
        detail_form.addRow("Phone:", self.detail_phone)

        self.detail_contact = QLineEdit()
        detail_form.addRow("Contact Name:", self.detail_contact)

        self.detail_email = QLineEdit()
        detail_form.addRow("Contact Email:", self.detail_email)

        detail_group.setLayout(detail_form)
        layout.addWidget(detail_group)

        # -- Save button --
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save Details")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_details)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

        self._selected_id = None

    def _refresh(self):
        facilities = models.get_all_facilities()
        self.table.setRowCount(len(facilities))
        for i, f in enumerate(facilities):
            self.table.setItem(i, 0, QTableWidgetItem(f["name"]))

    def _on_select(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        facilities = models.get_all_facilities()
        if row >= len(facilities):
            return
        fac = facilities[row]
        self._selected_id = fac["id"]
        self.detail_name.setText(fac["name"])
        self.detail_street.setText(fac.get("street") or "")
        self.detail_city.setText(fac.get("city") or "")
        self.detail_zip.setText(fac.get("zip") or "")
        self.detail_phone.setText(fac.get("phone") or "")
        self.detail_contact.setText(fac.get("contact_name") or "")
        self.detail_email.setText(fac.get("contact_email") or "")
        self.save_btn.setEnabled(True)

    def _save_details(self):
        if not self._selected_id:
            return
        models.update_facility(
            self._selected_id,
            name=self.detail_name.text().strip(),
            street=self.detail_street.text().strip(),
            city=self.detail_city.text().strip(),
            zip=self.detail_zip.text().strip(),
            phone=self.detail_phone.text().strip(),
            contact_name=self.detail_contact.text().strip(),
            contact_email=self.detail_email.text().strip(),
        )
        self._refresh()
        self.facility_added.emit()
        QMessageBox.information(self, "Saved", "Facility details saved.")

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

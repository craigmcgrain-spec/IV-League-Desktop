from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QLineEdit, QDateEdit,
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QCompleter, QMessageBox, QLabel
)
from PyQt6.QtCore import QDate, QTime, Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from ..database import models
from ..database.db import init_db, get_connection


TASK_OPTIONS = {
    "IV Insertion": ["22ga", "24ga"],
    "Midline Insertion": [],
    "PICC Insertion": [],
    "Dressing Change": [],
    "Blood Draw": [],
    "Troubleshoot": [],
}

SIDE_OPTIONS = ["Right", "Left"]

LOCATION_OPTIONS = {
    "IV Insertion": ["AC", "Forearm", "Wrist", "Hand"],
    "Midline Insertion": ["AC", "Upper Arm"],
    "PICC Insertion": ["Brachial", "Cephalic"],
    "Dressing Change": ["AC", "Forearm", "Wrist", "Hand"],
    "Blood Draw": [],
    "Troubleshoot": [],
}


class DataEntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh_facilities()
        self._refresh_tasks()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # -- Facility --
        fac_group = QGroupBox("Facility")
        fac_form = QFormLayout()
        self.facility_combo = QComboBox()
        self.facility_combo.setEditable(True)
        self.facility_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.facility_combo.completer().setFilterMode(
            Qt.MatchFlag.MatchContains
        )
        fac_form.addRow("Facility:", self.facility_combo)
        fac_group.setLayout(fac_form)
        root.addWidget(fac_group)

        # -- Client --
        client_group = QGroupBox("Client")
        client_form = QFormLayout()
        self.name_edit = QLineEdit()
        client_form.addRow("Name:", self.name_edit)
        client_group.setLayout(client_form)
        root.addWidget(client_group)

        # -- Date / Time --
        dt_group = QGroupBox("Date & Time")
        dt_form = QFormLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        dt_form.addRow("Date:", self.date_edit)

        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("HH:MM")
        time_validator = QRegularExpressionValidator(
            QRegularExpression(r"^([01]\d|2[0-3]):[0-5]\d$")
        )
        self.time_edit.setValidator(time_validator)
        self.time_edit.setText(QTime.currentTime().toString("HH:mm"))
        dt_form.addRow("Time:", self.time_edit)
        dt_group.setLayout(dt_form)
        root.addWidget(dt_group)

        # -- Task --
        task_group = QGroupBox("Task")
        task_form = QFormLayout()
        self.task_combo = QComboBox()
        self.task_combo.currentTextChanged.connect(self._on_task_changed)
        task_form.addRow("Task:", self.task_combo)

        self.gauge_label = QLabel("Gauge:")
        self.gauge_combo = QComboBox()
        task_form.addRow(self.gauge_label, self.gauge_combo)

        self.side_label = QLabel("Side:")
        self.side_combo = QComboBox()
        task_form.addRow(self.side_label, self.side_combo)

        self.loc_label = QLabel("Location:")
        self.loc_combo = QComboBox()
        task_form.addRow(self.loc_label, self.loc_combo)

        self.notes_label = QLabel("Notes:")
        self.notes_edit = QLineEdit()
        task_form.addRow(self.notes_label, self.notes_edit)

        task_group.setLayout(task_form)
        root.addWidget(task_group)

        # -- Save --
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save Record")
        self.save_btn.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        root.addLayout(btn_row)

        root.addStretch()
        self._on_task_changed(self.task_combo.currentText())

    def refresh_facilities(self):
        names = [f["name"] for f in models.get_all_facilities()]
        self.facility_combo.clear()
        self.facility_combo.addItems(names)

    def _refresh_tasks(self):
        names = [t["name"] for t in models.get_all_tasks()]
        self.task_combo.clear()
        self.task_combo.addItems(names)

    def _on_task_changed(self, task_name):
        gauges = TASK_OPTIONS.get(task_name, [])
        sides = SIDE_OPTIONS
        locations = LOCATION_OPTIONS.get(task_name, [])

        self.gauge_combo.clear()
        self.gauge_combo.addItems(gauges)
        self.gauge_combo.setVisible(bool(gauges))
        self.gauge_label.setVisible(bool(gauges))

        self.side_combo.clear()
        self.side_combo.addItems(sides)
        self.side_combo.setVisible(bool(sides))
        self.side_label.setVisible(bool(sides))

        self.loc_combo.clear()
        self.loc_combo.addItems(locations)
        self.loc_combo.setVisible(bool(locations))
        self.loc_label.setVisible(bool(locations))

        is_troubleshoot = task_name == "Troubleshoot"
        self.notes_edit.setVisible(is_troubleshoot)
        self.notes_label.setVisible(is_troubleshoot)

    def _save(self):
        facility_name = self.facility_combo.currentText().strip()
        client_name = self.name_edit.text().strip()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        time_str = self.time_edit.text().strip()
        task_name = self.task_combo.currentText()

        if not facility_name:
            QMessageBox.warning(self, "Error", "Facility is required.")
            return
        if not client_name:
            QMessageBox.warning(self, "Error", "Client name is required.")
            return
        if not time_str:
            QMessageBox.warning(self, "Error", "Time is required.")
            return

        models.add_facility(facility_name)
        facility_id = models.get_facility_id(facility_name)
        client_id = models.get_or_create_client(client_name, facility_id)
        task_id = models.get_task_id(task_name)

        gauge = self.gauge_combo.currentText() or None
        side = self.side_combo.currentText() or None
        location = self.loc_combo.currentText() or None
        notes = self.notes_edit.text().strip() or None

        models.add_record(
            client_id, facility_id, task_id,
            date_str, time_str,
            gauge, side, location, notes,
        )

        self.refresh_facilities()
        QMessageBox.information(self, "Saved", "Record saved successfully.")
        self.name_edit.clear()
        self.notes_edit.clear()

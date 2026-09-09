from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QDateEdit,
    QGroupBox, QHBoxLayout, QPushButton, QMessageBox, QLabel
)
from PyQt6.QtCore import QDate, QTime, Qt
from ..database import models


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
    "Blood Draw": ["Upper Arm", "AC", "Forearm", "Wrist", "Hand"],
    "Troubleshoot": [],
}


class EditRecordDialog(QDialog):
    def __init__(self, record_data, parent=None):
        super().__init__(parent)
        self.record_data = record_data
        self.setWindowTitle("Edit Record")
        self.setMinimumWidth(500)
        self._build_ui()
        self._populate_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # -- Facility --
        fac_group = QGroupBox("Facility")
        fac_form = QFormLayout()
        fac_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fac_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.facility_combo = QComboBox()
        self.facility_combo.setEditable(True)
        self.facility_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        fac_form.addRow("Facility:", self.facility_combo)
        fac_group.setLayout(fac_form)
        layout.addWidget(fac_group)

        # -- Client --
        client_group = QGroupBox("Client")
        client_form = QFormLayout()
        client_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        client_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(300)
        client_form.addRow("Name:", self.name_edit)
        client_group.setLayout(client_form)
        layout.addWidget(client_group)

        # -- Clinician --
        clinician_group = QGroupBox("Clinician")
        clinician_form = QFormLayout()
        clinician_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        clinician_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.clinician_combo = QComboBox()
        self.clinician_combo.setMinimumWidth(300)
        clinician_form.addRow("Clinician:", self.clinician_combo)
        clinician_group.setLayout(clinician_form)
        layout.addWidget(clinician_group)

        # -- Date / Time --
        dt_group = QGroupBox("Date & Time")
        dt_layout = QHBoxLayout()

        dt_left = QFormLayout()
        dt_left.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        dt_left.addRow("Date:", self.date_edit)

        dt_right = QFormLayout()
        dt_right.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("HH:MM")
        time_validator = QRegularExpressionValidator(
            QRegularExpression(r"^([01]\d|2[0-3]):[0-5]\d$")
        )
        self.time_edit.setValidator(time_validator)
        self.time_edit.setText(QTime.currentTime().toString("HH:mm"))
        dt_right.addRow("Time:", self.time_edit)

        dt_layout.addLayout(dt_left)
        dt_layout.addLayout(dt_right)
        dt_group.setLayout(dt_layout)
        layout.addWidget(dt_group)

        # -- Task --
        task_group = QGroupBox("Task")
        task_form = QFormLayout()
        task_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        task_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.task_combo = QComboBox()
        self.task_combo.setMinimumWidth(300)
        self.task_combo.currentTextChanged.connect(self._on_task_changed)
        task_form.addRow("Task:", self.task_combo)

        self.gauge_label = QLabel("Gauge:")
        self.gauge_combo = QComboBox()
        self.gauge_combo.setMinimumWidth(300)
        task_form.addRow(self.gauge_label, self.gauge_combo)

        self.side_label = QLabel("Side:")
        self.side_combo = QComboBox()
        self.side_combo.setMinimumWidth(300)
        task_form.addRow(self.side_label, self.side_combo)

        self.loc_label = QLabel("Location:")
        self.loc_combo = QComboBox()
        self.loc_combo.setMinimumWidth(300)
        task_form.addRow(self.loc_label, self.loc_combo)

        self.attempts_label = QLabel("Attempts:")
        self.attempts_edit = QLineEdit()
        self.attempts_edit.setPlaceholderText("Number of attempts")
        self.attempts_edit.setMinimumWidth(300)
        task_form.addRow(self.attempts_label, self.attempts_edit)

        self.cap_label = QLabel("Cap Change:")
        self.cap_combo = QComboBox()
        self.cap_combo.addItems(["No", "Yes"])
        self.cap_combo.setMinimumWidth(300)
        task_form.addRow(self.cap_label, self.cap_combo)

        self.notes_label = QLabel("Notes:")
        self.notes_edit = QLineEdit()
        self.notes_edit.setMinimumWidth(300)
        task_form.addRow(self.notes_label, self.notes_edit)

        task_group.setLayout(task_form)
        layout.addWidget(task_group)

        # -- Buttons --
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

        self._on_task_changed(self.task_combo.currentText())

    def _populate_data(self):
        # Load facilities
        self.facility_combo.clear()
        facilities = models.get_all_facilities()
        for f in facilities:
            self.facility_combo.addItem(f["name"], f["id"])
            if f["id"] == self.record_data["facility_id"]:
                self.facility_combo.setCurrentIndex(self.facility_combo.count() - 1)

        # Load client name (we'll need to get or create the client)
        self.name_edit.setText(self.record_data["client_name"])

        # Load clinicians
        self.clinician_combo.clear()
        clinicians = models.get_all_clinicians()
        default_index = 0
        for i, c in enumerate(clinicians):
            display = f"{c['name']}, {c['credentials']}" if c["credentials"] else c["name"]
            self.clinician_combo.addItem(display, c["id"])
            if c["is_default"]:
                default_index = i
            if c["id"] == self.record_data.get("clinician_id"):
                self.clinician_combo.setCurrentIndex(i)
        self.clinician_combo.setCurrentIndex(default_index)

        # Load date and time
        if self.record_data["date"]:
            self.date_edit.setDate(QDate.fromString(self.record_data["date"], "yyyy-MM-dd"))
        if self.record_data["time"]:
            self.time_edit.setText(self.record_data["time"])

        # Load task
        self.task_combo.clear()
        tasks = models.get_all_tasks()
        for t in tasks:
            self.task_combo.addItem(t["name"], t["id"])
            if t["id"] == self.record_data["task_id"]:
                self.task_combo.setCurrentIndex(self.task_combo.count() - 1)

        # The _on_task_changed will be called automatically when we set the task combo

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

        # Populate task-specific fields
        if self.record_data.get("gauge"):
            index = self.gauge_combo.findText(self.record_data["gauge"])
            if index >= 0:
                self.gauge_combo.setCurrentIndex(index)
        
        if self.record_data.get("side"):
            index = self.side_combo.findText(self.record_data["side"])
            if index >= 0:
                self.side_combo.setCurrentIndex(index)
                
        if self.record_data.get("location"):
            index = self.loc_combo.findText(self.record_data["location"])
            if index >= 0:
                self.loc_combo.setCurrentIndex(index)
                
        attempts = self.record_data.get("attempts")
        if attempts is not None:
            self.attempts_edit.setText(str(attempts))
        else:
            self.attempts_edit.clear()
            
        cap_change = self.record_data.get("cap_change")
        if cap_change is not None:
            self.cap_combo.setCurrentIndex(1 if cap_change == 1 else 0)
        else:
            self.cap_combo.setCurrentIndex(0)  # Default to "No"
            
        self.notes_edit.setText(self.record_data.get("notes", ""))

    def _update_record(self):
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

        # Get or create facility
        models.add_facility(facility_name)
        facility_id = models.get_facility_id(facility_name)
        
        # Get or create client (link to facility)
        client_id = models.get_or_create_client(client_name, facility_id)
        
        # Get task ID
        task_id = models.get_task_id(task_name)
        
        # Get other fields
        gauge = self.gauge_combo.currentText() or None
        side = self.side_combo.currentText() or None
        location = self.loc_combo.currentText() or None
        notes = self.notes_edit.text().strip() or None
        
        attempts_text = self.attempts_edit.text().strip()
        attempts = int(attempts_text) if attempts_text.isdigit() else None
        
        cap_change = 1 if self.cap_combo.currentText() == "Yes" else 0
        
        # Get clinician info
        clinician_id = self.clinician_combo.currentData()
        clinician_name = None
        clinician_cred = None
        if clinician_id:
            clinicians = models.get_all_clinicians()
            for c in clinicians:
                if c["id"] == clinician_id:
                    clinician_name = c["name"]
                    clinician_cred = c["credentials"]
                    break

        # Update the record
        models.update_record(
            self.record_data["id"],
            client_id, facility_id, task_id,
            date_str, time_str, gauge, side, location, notes,
            clinician_name, clinician_cred,
            attempts, cap_change
        )
        
        QMessageBox.information(self, "Success", "Record updated successfully.")
        self.accept()

    def _delete_record(self):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = models.get_connection()
            conn.execute("DELETE FROM records WHERE id = ?", (self.record_data["id"],))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Record deleted successfully.")
            self.accept()
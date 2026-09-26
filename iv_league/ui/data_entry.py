from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QLineEdit, QDateEdit,
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QCompleter, QMessageBox, QLabel
)
from PyQt6.QtCore import QDate, QTime, Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from ..database import models
from .constants import TASK_OPTIONS, SIDE_OPTIONS, LOCATION_OPTIONS


class DataEntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh_facilities()
        self.refresh_clinicians()
        self._refresh_tasks()
        self._on_task_changed(self.task_combo.currentText())

    def _build_ui(self):
        root = QVBoxLayout(self)

        # -- Facility --
        fac_group = QGroupBox("Facility")
        fac_form = QFormLayout()
        fac_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fac_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.facility_combo = QComboBox()
        self.facility_combo.setEditable(True)
        self.facility_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.facility_combo.completer().setFilterMode(
            Qt.MatchFlag.MatchContains
        )
        self.facility_combo.setMinimumWidth(300)
        fac_form.addRow("Facility:", self.facility_combo)
        fac_group.setLayout(fac_form)
        root.addWidget(fac_group)

        # -- Client --
        client_group = QGroupBox("Client")
        client_form = QFormLayout()
        client_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        client_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(300)
        client_form.addRow("Name:", self.name_edit)
        client_group.setLayout(client_form)
        root.addWidget(client_group)

        # -- Clinician --
        clinician_group = QGroupBox("Clinician")
        clinician_form = QFormLayout()
        clinician_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        clinician_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.clinician_combo = QComboBox()
        self.clinician_combo.setMinimumWidth(300)
        clinician_form.addRow("Clinician:", self.clinician_combo)
        clinician_group.setLayout(clinician_form)
        root.addWidget(clinician_group)

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
        root.addWidget(dt_group)

        # -- Task and Supplies Row --
        task_supplies_row = QHBoxLayout()
        
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

        self.notes_label = QLabel("Notes:")
        self.notes_edit = QLineEdit()
        self.notes_edit.setMinimumWidth(300)
        task_form.addRow(self.notes_label, self.notes_edit)

        task_group.setLayout(task_form)
        task_supplies_row.addWidget(task_group)

        # -- Supplies --
        supplies_group = QGroupBox("Supplies")
        supplies_form = QFormLayout()
        supplies_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        supplies_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        self.supply_fields = {}
        supply_cols = models.get_supply_columns()
        for supply_col in supply_cols:
            label = QLabel(f"{supply_col['task_name']}:")
            field = QLineEdit()
            field.setPlaceholderText("0")
            field.setMinimumWidth(300)
            supplies_form.addRow(label, field)
            self.supply_fields[supply_col['column_name']] = field
        
        supplies_group.setLayout(supplies_form)
        task_supplies_row.addWidget(supplies_group)
        
        root.addLayout(task_supplies_row)

        # -- Save --
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save Record")
        self.save_btn.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        root.addLayout(btn_row)

        root.addStretch()

    def refresh_facilities(self):
        names = [f["name"] for f in models.get_all_facilities()]
        self.facility_combo.clear()
        self.facility_combo.addItems(names)

    def refresh_clinicians(self):
        clinicians = [c for c in models.get_all_clinicians() if c["name"] != "Select Clinician"]
        self.clinician_combo.clear()
        default_index = 0
        for i, c in enumerate(clinicians):
            display = f"{c['name']}, {c['credentials']}" if c["credentials"] else c["name"]
            self.clinician_combo.addItem(display, c["id"])
            if c["is_default"]:
                default_index = i
        self.clinician_combo.setCurrentIndex(default_index)

    def _refresh_tasks(self):
        current_task = self.task_combo.currentText()
        tasks_by_category = models.get_tasks_by_category()
        procedures_tasks = tasks_by_category.get("Procedures", [])
        
        self.task_combo.clear()
        
        for task in procedures_tasks:
            self.task_combo.addItem(task["name"], task["id"])
        
        if current_task:
            for i in range(self.task_combo.count()):
                if current_task == self.task_combo.itemText(i):
                    self.task_combo.setCurrentIndex(i)
                    break
        elif self.task_combo.count() > 0:
            self.task_combo.setCurrentIndex(0)

    def _on_task_changed(self, task_name):
        task_name_only = task_name.split(" - $")[0] if " - $" in task_name else task_name
        gauges = TASK_OPTIONS.get(task_name_only, [])
        sides = SIDE_OPTIONS
        locations = LOCATION_OPTIONS.get(task_name_only, [])

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

        self.notes_edit.setVisible(True)
        self.notes_label.setVisible(True)

    def _save(self):
        try:
            facility_name = self.facility_combo.currentText().strip()
            client_name = self.name_edit.text().strip()
            date_str = self.date_edit.date().toString("yyyy-MM-dd")
            time_str = self.time_edit.text().strip()
            task_display = self.task_combo.currentText()
            task_id = self.task_combo.currentData()

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

            if task_id is None:
                QMessageBox.warning(
                    self, "Error",
                    f"Task not found in database."
                )
                return

            gauge = self.gauge_combo.currentText() or None
            side = self.side_combo.currentText() or None
            location = self.loc_combo.currentText() or None
            notes = self.notes_edit.text().strip() or None

            clinician_id = self.clinician_combo.currentData()
            clinician_name = None
            clinician_credentials = None
            if clinician_id:
                clinicians = models.get_all_clinicians()
                for c in clinicians:
                    if c["id"] == clinician_id:
                        clinician_name = c["name"]
                        clinician_credentials = c["credentials"]
                        break

            supply_values = {}
            for col_name, field in self.supply_fields.items():
                value_text = field.text().strip()
                try:
                    value = float(value_text) if value_text else 0.0
                except ValueError:
                    value = 0.0
                supply_values[col_name] = value

            models.add_record(
                client_id, facility_id, task_id,
                date_str, time_str,
                gauge, side, location, notes,
                clinician_name, clinician_credentials,
                None,
                supply_values
            )

            self.refresh_facilities()
            QMessageBox.information(self, "Saved", "Record saved successfully.")
            self.name_edit.clear()
            self.notes_edit.clear()
            for field in self.supply_fields.values():
                field.clear()
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"An error occurred while saving the record:\n{str(e)}"
            )
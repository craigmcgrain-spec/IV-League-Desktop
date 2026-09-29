from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QLineEdit, QDateEdit,
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import QDate, QTime, Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from ..database import models
from .constants import TASK_OPTIONS, SIDE_OPTIONS, LOCATION_OPTIONS


class RecordForm(QScrollArea):
    """Shared Facility/Client/Clinician/Date/Task/Supplies form for record entry and editing.

    Scroll area wrapper: the form keeps its natural size and the widget
    scrolls instead of cramming fields when the window is small.
    """

    def __init__(self, all_tasks=False):
        super().__init__()
        self._record = None
        self._all_tasks = all_tasks
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        self.setWidget(content)
        self._root = QVBoxLayout(content)
        self._build_ui()
        self.refresh_facilities()
        self.refresh_clinicians()
        self._refresh_tasks()
        self._on_task_changed(self.task_combo.currentText())

    def _build_ui(self):
        root = self._root

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

        # Cap Change is a Supplies-category task stored in the dedicated
        # cap_change column — shown here as a quantity like the other supplies.
        cap_label = QLabel("Cap Change:")
        cap_field = QLineEdit()
        cap_field.setPlaceholderText("0")
        cap_field.setMinimumWidth(300)
        supplies_form.addRow(cap_label, cap_field)
        self.supply_fields["cap_change"] = cap_field

        supplies_group.setLayout(supplies_form)
        task_supplies_row.addWidget(supplies_group)

        root.addLayout(task_supplies_row)

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
        if self._all_tasks:
            tasks = [t for group in tasks_by_category.values() for t in group]
        else:
            tasks = tasks_by_category.get("Procedures", [])

        self.task_combo.clear()

        for task in tasks:
            self.task_combo.addItem(task["name"], task["id"])

        if current_task:
            for i in range(self.task_combo.count()):
                if current_task == self.task_combo.itemText(i):
                    self.task_combo.setCurrentIndex(i)
                    break
        elif self.task_combo.count() > 0:
            self.task_combo.setCurrentIndex(0)

    def _on_task_changed(self, task_name):
        gauges = TASK_OPTIONS.get(task_name, [])
        locations = LOCATION_OPTIONS.get(task_name, [])

        self.gauge_combo.clear()
        self.gauge_combo.addItems(gauges)
        self.gauge_combo.setVisible(bool(gauges))
        self.gauge_label.setVisible(bool(gauges))

        self.side_combo.clear()
        self.side_combo.addItems(SIDE_OPTIONS)
        self.side_combo.setVisible(bool(SIDE_OPTIONS))
        self.side_label.setVisible(bool(SIDE_OPTIONS))

        self.loc_combo.clear()
        self.loc_combo.addItems(locations)
        self.loc_combo.setVisible(bool(locations))
        self.loc_label.setVisible(bool(locations))

        self.notes_edit.setVisible(True)
        self.notes_label.setVisible(True)

        if self._record:
            self._apply_record_fields()

    def _apply_record_fields(self):
        for value, combo in (
            (self._record.get("gauge"), self.gauge_combo),
            (self._record.get("side"), self.side_combo),
            (self._record.get("location"), self.loc_combo),
        ):
            if value:
                index = combo.findText(value)
                if index >= 0:
                    combo.setCurrentIndex(index)
        self.notes_edit.setText(self._record.get("notes") or "")

    def set_record(self, record):
        """Populate the form from an existing record (edit mode)."""
        self._record = record

        index = self.facility_combo.findData(record.get("facility_id"))
        if index >= 0:
            self.facility_combo.setCurrentIndex(index)

        self.name_edit.setText(record.get("client_name") or "")

        record_clinician = (record.get("clinician_name") or "").strip()
        clinician = next(
            (c for c in models.get_all_clinicians()
             if c["name"] != "Select Clinician" and c["name"] == record_clinician),
            None,
        )
        if clinician:
            index = self.clinician_combo.findData(clinician["id"])
            if index >= 0:
                self.clinician_combo.setCurrentIndex(index)

        if record.get("date"):
            self.date_edit.setDate(QDate.fromString(record["date"], "yyyy-MM-dd"))
        if record.get("time"):
            self.time_edit.setText(record["time"])

        index = self.task_combo.findData(record.get("task_id"))
        if index >= 0:
            self.task_combo.setCurrentIndex(index)
        self._on_task_changed(self.task_combo.currentText())

        for col_name, field in self.supply_fields.items():
            value = record.get(col_name, 0.0)
            if value and value > 0:
                field.setText(str(value))
            else:
                field.clear()

    def collect(self):
        """Validate the form and resolve database ids.

        Returns (data, None) on success or (None, error message) on failure.
        """
        facility_name = self.facility_combo.currentText().strip()
        client_name = self.name_edit.text().strip()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        time_str = self.time_edit.text().strip()
        task_id = self.task_combo.currentData()

        if not facility_name:
            return None, "Facility is required."
        if not client_name:
            return None, "Client name is required."
        if not time_str:
            return None, "Time is required."
        if task_id is None:
            return None, "Task not found in database."

        models.add_facility(facility_name)
        facility_id = models.get_facility_id(facility_name)
        client_id = models.get_or_create_client(client_name, facility_id)

        clinician_id = self.clinician_combo.currentData()
        clinician_name = None
        clinician_credentials = None
        if clinician_id:
            clinician = next(
                (c for c in models.get_all_clinicians() if c["id"] == clinician_id),
                None,
            )
            if clinician:
                clinician_name = clinician["name"]
                clinician_credentials = clinician["credentials"]

        supply_values = {}
        for col_name, field in self.supply_fields.items():
            text = field.text().strip().replace("$", "").replace(",", "")
            try:
                supply_values[col_name] = float(text) if text else 0.0
            except ValueError:
                supply_values[col_name] = 0.0

        return {
            "facility_id": facility_id,
            "client_id": client_id,
            "task_id": task_id,
            "date": date_str,
            "time": time_str,
            "gauge": self.gauge_combo.currentText() or None,
            "side": self.side_combo.currentText() or None,
            "location": self.loc_combo.currentText() or None,
            "notes": self.notes_edit.text().strip() or None,
            "clinician_name": clinician_name,
            "clinician_credentials": clinician_credentials,
            "supply_values": supply_values,
        }, None

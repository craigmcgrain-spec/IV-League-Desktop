from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QGroupBox
)
from PyQt6.QtCore import QDate, Qt
from ..database import models


class SearchViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # -- Filters --
        filter_group = QGroupBox("Filters")
        filter_form = QFormLayout()

        self.facility_combo = QComboBox()
        self.facility_combo.addItem("All", None)
        self._load_facilities()
        filter_form.addRow("Facility:", self.facility_combo)

        self.task_combo = QComboBox()
        self.task_combo.addItem("All", None)
        self._load_tasks()
        filter_form.addRow("Task:", self.task_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_form.addRow("From:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_form.addRow("To:", self.end_date)

        filter_group.setLayout(filter_form)
        root.addWidget(filter_group)

        # -- Buttons --
        btn_row = QHBoxLayout()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._refresh)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_row.addStretch()
        btn_row.addWidget(self.search_btn)
        btn_row.addWidget(self.delete_btn)
        root.addLayout(btn_row)

        # -- Table --
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Date", "Time", "Client", "Facility", "Task",
            "Details", "Notes", "Clinician", "Credentials"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

    def _load_facilities(self):
        for f in models.get_all_facilities():
            self.facility_combo.addItem(f["name"], f["id"])

    def _load_tasks(self):
        for t in models.get_all_tasks():
            self.task_combo.addItem(t["name"], t["id"])

    def _refresh(self):
        fac_id = self.facility_combo.currentData()
        task_id = self.task_combo.currentData()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        records = models.search_records(
            facility_id=fac_id,
            start_date=start,
            end_date=end,
            task_id=task_id,
        )

        self.table.setRowCount(len(records))
        for i, r in enumerate(records):
            details = " ".join(
                filter(None, [r.get("gauge"), r.get("side"), r.get("location")])
            )
            values = [
                r["date"], r["time"], r["client_name"],
                r["facility_name"], r["task_name"],
                details, r.get("notes", ""),
                r.get("clinician_name", ""), r.get("clinician_credentials", ""),
            ]
            for j, val in enumerate(values):
                item = QTableWidgetItem(str(val or ""))
                item.setData(Qt.ItemDataRole.UserRole, r["id"])
                self.table.setItem(i, j, item)

    def _delete_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        reply = QMessageBox.question(
            self, "Confirm",
            f"Delete {len(rows)} record(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for idx in rows:
                record_id = self.table.item(idx.row(), 0).data(
                    Qt.ItemDataRole.UserRole
                )
                models.delete_record(record_id)
            self._refresh()

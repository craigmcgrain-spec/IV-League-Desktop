from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QDate, Qt
from ..database import models
from ..utils.invoice_generator import generate_invoice_pdf


class InvoicingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._load_facilities()

    def _build_ui(self):
        root = QVBoxLayout(self)

        sel_group = QGroupBox("Invoice Parameters")
        sel_form = QFormLayout()

        self.facility_combo = QComboBox()
        sel_form.addRow("Facility:", self.facility_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        sel_form.addRow("From:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        sel_form.addRow("To:", self.end_date)

        sel_group.setLayout(sel_form)
        root.addWidget(sel_group)

        btn_row = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Invoice")
        self.generate_btn.clicked.connect(self._generate)
        btn_row.addStretch()
        btn_row.addWidget(self.generate_btn)
        root.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Task", "Quantity", "Price", "Subtotal"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        self.total_label = QLabel("Total: $0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        root.addWidget(self.total_label)

    def _load_facilities(self):
        for f in models.get_all_facilities():
            self.facility_combo.addItem(f["name"], f["id"])

    def _generate(self):
        fac_id = self.facility_combo.currentData()
        fac_name = self.facility_combo.currentText()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        if not fac_id:
            QMessageBox.warning(self, "Error", "Select a facility.")
            return

        items = models.get_invoice_records_priced(fac_id, start, end)
        items_dated = models.get_invoice_items_dated(fac_id, start, end)

        self.table.setRowCount(len(items))
        grand_total = 0
        for i, item in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(item["task_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(str(item["qty"])))

            price_item = QTableWidgetItem(f"${item['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 2, price_item)

            subtotal = item["qty"] * item["price"]
            subtotal_item = QTableWidgetItem(f"${subtotal:.2f}")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 3, subtotal_item)

            grand_total += subtotal

        self.total_label.setText(f"Total: ${grand_total:.2f}")

        if not items:
            QMessageBox.information(
                self, "No Data",
                "No records found for the selected criteria."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Invoice", f"invoice_{fac_name}.pdf", "PDF (*.pdf)"
        )
        if path:
            fac_details = models.get_facility(fac_id)
            company_info = models.get_company_info()
            generate_invoice_pdf(path, fac_name, start, end, items,
                                 facility_details=fac_details,
                                 company_info=company_info,
                                 items_dated=items_dated)
            models.save_invoice(fac_id, start, end, grand_total)
            QMessageBox.information(self, "Done", f"Invoice saved to:\n{path}")

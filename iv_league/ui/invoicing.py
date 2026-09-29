from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QLabel, QFileDialog, QMessageBox, QLineEdit,
    QTabWidget, QHeaderView
)
from PyQt6.QtCore import QDate, Qt
from ..database import models
from ..utils.invoice_generator import generate_invoice_pdf


class InvoicingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._current_display_items = []
        self._current_items_dated = []
        self._current_supplies = []
        self._current_cap_changes = []
        self._current_grand_total = 0.0
        self._build_ui()
        self._load_facilities()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ── Tab 1: Create / Preview Invoice ──────────────────
        create_widget = QWidget()
        create_layout = QVBoxLayout(create_widget)

        sel_group = QGroupBox("Invoice Parameters")
        sel_form = QFormLayout()

        self.facility_combo = QComboBox()
        self.facility_combo.currentIndexChanged.connect(self._on_facility_changed)
        sel_form.addRow("Facility:", self.facility_combo)

        # Invoice Number field (auto-generated, editable)
        self.invoice_num_edit = QLineEdit()
        self.invoice_num_edit.setPlaceholderText("e.g. INV-2026-0001")
        sel_form.addRow("Invoice #:", self.invoice_num_edit)

        # Date pickers & quick preset buttons
        dt_row = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        dt_row.addWidget(QLabel("From:"))
        dt_row.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        dt_row.addWidget(QLabel("To:"))
        dt_row.addWidget(self.end_date)

        dt_row.addSpacing(10)
        btn_this_month = QPushButton("This Month")
        btn_this_month.clicked.connect(self._set_this_month)
        btn_last_month = QPushButton("Last Month")
        btn_last_month.clicked.connect(self._set_last_month)
        btn_last_30 = QPushButton("Last 30 Days")
        btn_last_30.clicked.connect(self._set_last_30_days)

        dt_row.addWidget(btn_this_month)
        dt_row.addWidget(btn_last_month)
        dt_row.addWidget(btn_last_30)
        dt_row.addStretch()

        sel_form.addRow("Date Range:", dt_row)
        sel_group.setLayout(sel_form)
        create_layout.addWidget(sel_group)

        # Action Buttons
        btn_row = QHBoxLayout()
        self.preview_btn = QPushButton("Calculate & Preview")
        self.preview_btn.clicked.connect(self._calculate_preview)
        
        self.export_pdf_btn = QPushButton("Export PDF Invoice...")
        self.export_pdf_btn.setEnabled(False)
        self.export_pdf_btn.clicked.connect(self._export_pdf)

        btn_row.addWidget(self.preview_btn)
        btn_row.addWidget(self.export_pdf_btn)
        btn_row.addStretch()
        create_layout.addLayout(btn_row)

        # Line items preview table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Task / Item", "Quantity", "Price", "Subtotal"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        create_layout.addWidget(self.table)

        self.total_label = QLabel("Total: $0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #008A8C;")
        create_layout.addWidget(self.total_label)

        self.tabs.addTab(create_widget, "Generate Invoice")

        # ── Tab 2: Invoice History ───────────────────────────
        history_widget = QWidget()
        hist_layout = QVBoxLayout(history_widget)

        hist_btn_row = QHBoxLayout()
        self.hist_refresh_btn = QPushButton("Refresh History")
        self.hist_refresh_btn.clicked.connect(self._load_history)
        hist_btn_row.addWidget(self.hist_refresh_btn)
        hist_btn_row.addStretch()
        hist_layout.addLayout(hist_btn_row)

        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(6)
        self.hist_table.setHorizontalHeaderLabels([
            "Invoice #", "Facility", "Period Start", "Period End", "Total ($)", "Generated At"
        ])
        self.hist_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.hist_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.hist_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        hist_layout.addWidget(self.hist_table)

        self.tabs.addTab(history_widget, "Invoice History")
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, idx):
        if idx == 1:
            self._load_history()

    def _set_this_month(self):
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        self.start_date.setDate(first_day)
        self.end_date.setDate(today)

    def _set_last_month(self):
        today = QDate.currentDate()
        first_of_this = QDate(today.year(), today.month(), 1)
        last_of_prev = first_of_this.addDays(-1)
        first_of_prev = QDate(last_of_prev.year(), last_of_prev.month(), 1)
        self.start_date.setDate(first_of_prev)
        self.end_date.setDate(last_of_prev)

    def _set_last_30_days(self):
        today = QDate.currentDate()
        self.start_date.setDate(today.addDays(-30))
        self.end_date.setDate(today)

    def _on_facility_changed(self):
        if not self.invoice_num_edit.text():
            self.invoice_num_edit.setText(models.get_next_invoice_number())

    def _load_facilities(self):
        for f in models.get_all_facilities():
            self.facility_combo.addItem(f["name"], f["id"])
        self.invoice_num_edit.setText(models.get_next_invoice_number())

    def refresh_facilities(self):
        current = self.facility_combo.currentData()
        self.facility_combo.clear()
        for f in models.get_all_facilities():
            self.facility_combo.addItem(f["name"], f["id"])
        if current:
            for i in range(self.facility_combo.count()):
                if self.facility_combo.itemData(i) == current:
                    self.facility_combo.setCurrentIndex(i)
                    break

    def _refresh_pricing(self):
        """Reload pricing data when updated."""
        if self._current_display_items:
            self._calculate_preview()

    def _calculate_preview(self):
        fac_id = self.facility_combo.currentData()
        if not fac_id:
            QMessageBox.warning(self, "Error", "Please select a facility.")
            return

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        items = models.get_invoice_records_priced(fac_id, start, end)
        supplies = models.get_supplies_items(fac_id, start, end)
        cap_changes = models.get_cap_change_items(fac_id, start, end)
        items_dated = models.get_invoice_items_dated(fac_id, start, end)

        # Combined display list with supplies & cap changes
        display_items = items + supplies + cap_changes

        self.table.setRowCount(len(display_items))
        grand_total = 0.0
        for i, item in enumerate(display_items):
            is_sub = item["task_name"].startswith("Supplies: ") or item["task_name"] == "Cap Change"
            display_name = ("   ↳ " + item["task_name"]) if is_sub else item["task_name"]

            self.table.setItem(i, 0, QTableWidgetItem(display_name))
            self.table.setItem(i, 1, QTableWidgetItem(str(item["qty"])))

            price_item = QTableWidgetItem(f"${item['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 2, price_item)

            subtotal = float(item["qty"]) * float(item["price"])
            subtotal_item = QTableWidgetItem(f"${subtotal:.2f}")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 3, subtotal_item)

            grand_total += subtotal

        self._current_display_items = display_items
        self._current_items_dated = items_dated
        self._current_supplies = supplies
        self._current_cap_changes = cap_changes
        self._current_grand_total = grand_total

        self.total_label.setText(f"Total: ${grand_total:.2f}")

        if not display_items:
            self.export_pdf_btn.setEnabled(False)
            QMessageBox.information(self, "No Records", "No billable records found for the selected facility and dates.")
        else:
            self.export_pdf_btn.setEnabled(True)

    def _export_pdf(self):
        if not self._current_display_items:
            QMessageBox.warning(self, "Error", "Please calculate the invoice preview first.")
            return

        fac_id = self.facility_combo.currentData()
        fac_name = self.facility_combo.currentText()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        inv_num = self.invoice_num_edit.text().strip() or models.get_next_invoice_number()

        default_filename = f"Invoice_{inv_num}_{fac_name}.pdf".replace(" ", "_")
        path, _ = QFileDialog.getSaveFileName(self, "Save Invoice PDF", default_filename, "PDF (*.pdf)")
        if not path:
            return

        fac_details = models.get_facility(fac_id)
        company_info = models.get_company_info()

        generate_invoice_pdf(
            path, fac_name, start, end, self._current_display_items,
            facility_details=fac_details,
            company_info=company_info,
            items_dated=self._current_items_dated,
            supplies=self._current_supplies,
            invoice_number=inv_num,
            cap_changes=self._current_cap_changes
        )

        saved_num = models.save_invoice(fac_id, start, end, self._current_grand_total, invoice_number=inv_num)
        self.invoice_num_edit.setText(models.get_next_invoice_number())
        QMessageBox.information(self, "Invoice Saved", f"Invoice {saved_num} created and saved to:\n{path}")

    def _load_history(self):
        invoices = models.get_all_invoices()
        self.hist_table.setRowCount(len(invoices))
        for i, inv in enumerate(invoices):
            inv_num = inv.get("invoice_number") or f"INV-{inv['id']:04d}"
            self.hist_table.setItem(i, 0, QTableWidgetItem(inv_num))
            self.hist_table.setItem(i, 1, QTableWidgetItem(inv.get("facility_name") or ""))
            self.hist_table.setItem(i, 2, QTableWidgetItem(inv.get("start_date") or ""))
            self.hist_table.setItem(i, 3, QTableWidgetItem(inv.get("end_date") or ""))
            
            tot_item = QTableWidgetItem(f"${float(inv.get('total') or 0):.2f}")
            tot_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.hist_table.setItem(i, 4, tot_item)
            
            self.hist_table.setItem(i, 5, QTableWidgetItem(inv.get("created_at") or ""))

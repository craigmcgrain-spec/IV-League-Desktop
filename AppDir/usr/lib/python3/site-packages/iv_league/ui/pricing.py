from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from ..database import models


class PricingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._load_pricing()

    def _build_ui(self):
        root = QVBoxLayout(self)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Prices")
        save_btn.clicked.connect(self._save_prices)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Task", "Price ($)"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 150)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        root.addWidget(self.table)

    def _load_pricing(self):
        tasks = models.get_all_tasks()
        pricing = {p["task_id"]: p["price"] for p in models.get_all_pricing()}

        self.table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            name_item = QTableWidgetItem(task["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, task["id"])
            self.table.setItem(i, 0, name_item)

            price = pricing.get(task["id"], 0)
            price_item = QTableWidgetItem(f"${price:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 1, price_item)

    def _save_prices(self):
        for row in range(self.table.rowCount()):
            task_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            price_text = self.table.item(row, 1).text().strip().replace("$", "").replace(",", "")
            try:
                price = float(price_text)
            except ValueError:
                price = 0
            models.set_price(task_id, price)
        QMessageBox.information(self, "Saved", "Pricing updated.")

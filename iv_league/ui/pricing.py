from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QHeaderView, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..database import models


class PricingWidget(QWidget):
    pricing_changed = pyqtSignal()

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
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Double-click handler for price cells
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        
        root.addWidget(self.table)

    def _on_cell_double_clicked(self, row, col):
        """Open a dialog to edit the price when double-clicked."""
        try:
            if col != 1:
                return
            item = self.table.item(row, col)
            if item is None:
                return
            try:
                current_price = float(item.data(Qt.ItemDataRole.UserRole))
            except (TypeError, ValueError):
                try:
                    current_price = float(
                        item.text().strip().replace("$", "").replace(",", "") or 0.0
                    )
                except (TypeError, ValueError):
                    current_price = 0.0
            task_item = self.table.item(row, 0)
            task_name = task_item.text() if task_item else "task"

            new_price, ok = QInputDialog.getDouble(
                self, "Set Price", f"Price for {task_name} ($):",
                current_price, 0.0, 999999.99, 2,
            )
            if not ok:
                return

            item.setData(Qt.ItemDataRole.UserRole, float(new_price))
            item.setText(f"${new_price:.2f}")
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
        except Exception as e:
            QMessageBox.warning(self, "Edit failed", f"Could not edit price:\n{e}")

    def _load_pricing(self):
        tasks = models.get_all_tasks()
        pricing = {p["task_id"]: p["price"] for p in models.get_all_pricing()}

        self.table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            name_item = QTableWidgetItem(task["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, task["id"])
            self.table.setItem(i, 0, name_item)

            price = pricing.get(task["id"], 0.0)
            display_text = f"${price:.2f}"
            item = QTableWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, float(price))
            item.setText(display_text)
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(i, 1, item)

    def _save_prices(self):
        try:
            for row in range(self.table.rowCount()):
                task_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                price_item = self.table.item(row, 1)

                # Get the raw float value from UserRole (set at load/edit time)
                price = price_item.data(Qt.ItemDataRole.UserRole)
                try:
                    price = float(price)
                except (TypeError, ValueError):
                    try:
                        price_text = price_item.text().strip().replace("$", "").replace(",", "")
                        price = float(price_text)
                    except (ValueError, TypeError, AttributeError):
                        price = 0.0

                models.set_price(task_id, price)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Could not save prices:\n{e}")
            return

        self.pricing_changed.emit()
        QMessageBox.information(self, "Saved", "Pricing updated.")

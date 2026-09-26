from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QHeaderView, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..database import models


class PricingWidget(QWidget):
    pricing_changed = pyqtSignal()
    tasks_changed = pyqtSignal()
    task_pricing_changed = pyqtSignal()
    supply_pricing_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build_ui()
        self._load_pricing()

    def _build_ui(self):
        root = QVBoxLayout(self)

        btn_row = QHBoxLayout()
        
        add_task_btn = QPushButton("Add Task")
        add_task_btn.clicked.connect(self._add_task)
        btn_row.addWidget(add_task_btn)
        
        edit_task_btn = QPushButton("Edit Task")
        edit_task_btn.clicked.connect(self._edit_task)
        btn_row.addWidget(edit_task_btn)
        
        delete_task_btn = QPushButton("Delete Task")
        delete_task_btn.clicked.connect(self._delete_task)
        btn_row.addWidget(delete_task_btn)
        
        btn_row.addStretch()
        
        save_btn = QPushButton("Save Prices")
        save_btn.clicked.connect(self._save_prices)
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
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        
        root.addWidget(self.table)

    def _add_task(self):
        categories = models.get_task_categories()
        if not categories:
            QMessageBox.warning(self, "No Categories", "No task categories exist. Please restart the application.")
            return
        
        category_names = [c["name"] for c in categories]
        category_name, ok = QInputDialog.getItem(
            self, "Select Category", "Task category:", category_names, 0, False
        )
        if not ok:
            return
        
        name, ok = QInputDialog.getText(
            self, "Add Task", "Task name:"
        )
        if not ok or not name.strip():
            return
        
        try:
            models.add_task(name.strip(), category_name)
            self._load_pricing()
            self.pricing_changed.emit()
            self.tasks_changed.emit()
            if category_name == "Supplies":
                self.supply_pricing_changed.emit()
            QMessageBox.information(self, "Success", f"Task '{name}' added to {category_name}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not add task:\n{e}")

    def _edit_task(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a task to edit.")
            return
        
        task_item = self.table.item(current_row, 0)
        task_id = task_item.data(Qt.ItemDataRole.UserRole)
        
        if task_id is None:
            QMessageBox.warning(self, "Invalid Selection", "Please select a task, not a category header.")
            return
        
        current_name = task_item.text().strip()
        
        new_name, ok = QInputDialog.getText(
            self, "Edit Task", "Task name:", text=current_name
        )
        if not ok or not new_name.strip():
            return
        
        try:
            models.update_task(task_id, new_name.strip())
            self._load_pricing()
            self.pricing_changed.emit()
            self.tasks_changed.emit()
            QMessageBox.information(self, "Success", "Task updated.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not update task:\n{e}")

    def _delete_task(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a task to delete.")
            return
        
        task_item = self.table.item(current_row, 0)
        task_id = task_item.data(Qt.ItemDataRole.UserRole)
        
        if task_id is None:
            QMessageBox.warning(self, "Invalid Selection", "Please select a task, not a category header.")
            return
        
        task_name = task_item.text().strip()
        
        reply = QMessageBox.question(
            self, "Delete Task",
            f"Are you sure you want to delete '{task_name}'? This will also delete all records associated with this task.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            category_name = models.get_task_category_name(task_id)
            models.delete_task(task_id)
            self._load_pricing()
            self.pricing_changed.emit()
            self.tasks_changed.emit()
            if category_name == "Supplies":
                self.supply_pricing_changed.emit()
            QMessageBox.information(self, "Success", "Task deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete task:\n{e}")

    def _on_cell_double_clicked(self, row, col):
        try:
            if col != 1:
                return
            
            task_item = self.table.item(row, 0)
            task_id = task_item.data(Qt.ItemDataRole.UserRole)
            
            if task_id is None:
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
            
            task_name = task_item.text().strip() if task_item else "task"

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
        tasks_by_category = models.get_tasks_by_category()
        pricing = {p["task_id"]: p["price"] for p in models.get_all_pricing()}

        total_tasks = sum(len(tasks) for tasks in tasks_by_category.values())
        total_rows = total_tasks + len(tasks_by_category)
        
        self.table.setRowCount(total_rows)
        
        row_idx = 0
        for category_name in sorted(tasks_by_category.keys(), key=lambda x: (x != "Tasks", x != "Supplies", x)):
            tasks = tasks_by_category[category_name]
            
            category_item = QTableWidgetItem(category_name)
            category_font = QFont()
            category_font.setBold(True)
            category_item.setFont(category_font)
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            category_item.setBackground(Qt.GlobalColor.lightGray)
            self.table.setItem(row_idx, 0, category_item)
            
            empty_item = QTableWidgetItem("")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            empty_item.setBackground(Qt.GlobalColor.lightGray)
            self.table.setItem(row_idx, 1, empty_item)
            row_idx += 1
            
            for task in tasks:
                name_item = QTableWidgetItem(f"  {task['name']}")
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                name_item.setData(Qt.ItemDataRole.UserRole, task["id"])
                self.table.setItem(row_idx, 0, name_item)

                price = pricing.get(task["id"], 0.0)
                display_text = f"${price:.2f}"
                item = QTableWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, float(price))
                item.setText(display_text)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self.table.setItem(row_idx, 1, item)
                row_idx += 1

    def _save_prices(self):
        tasks_modified = set()
        supplies_modified = set()
        
        try:
            for row in range(self.table.rowCount()):
                name_item = self.table.item(row, 0)
                if name_item is None:
                    continue
                
                task_id = name_item.data(Qt.ItemDataRole.UserRole)
                if task_id is None:
                    continue
                
                price_item = self.table.item(row, 1)
                if price_item is None:
                    continue

                price = price_item.data(Qt.ItemDataRole.UserRole)
                try:
                    price = float(price)
                except (TypeError, ValueError):
                    try:
                        price_text = price_item.text().strip().replace("$", "").replace(",", "")
                        price = float(price_text)
                    except (ValueError, TypeError, AttributeError):
                        price = 0.0

                old_price = models.get_price(task_id)
                if old_price != price:
                    category_name = models.get_task_category_name(task_id)
                    if category_name == "Tasks":
                        tasks_modified.add(task_id)
                    elif category_name == "Supplies":
                        supplies_modified.add(task_id)
                
                models.set_price(task_id, price)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Could not save prices:\n{e}")
            return

        self.pricing_changed.emit()
        
        if tasks_modified:
            self.task_pricing_changed.emit()
        
        if supplies_modified:
            self.supply_pricing_changed.emit()
        
        QMessageBox.information(self, "Saved", "Pricing updated.")

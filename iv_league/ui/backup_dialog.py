from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QLabel, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from ..database import backup, settings

class BackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup Manager")
        self.setMinimumWidth(700)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Backups are stored in the app data folder."))

        sched_row = QHBoxLayout()
        self.scheduler_enable = QCheckBox("Enable automatic backups")
        self.scheduler_enable.setChecked(bool(settings.get("backup_automatic", False)))
        sched_row.addWidget(self.scheduler_enable)

        sched_row.addWidget(QLabel("Every"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 1440)
        self.interval_spin.setValue(int(settings.get("backup_interval_minutes", 1440)))
        self.interval_spin.setSuffix(" min")
        sched_row.addWidget(self.interval_spin)

        self.save_sched_btn = QPushButton("Save Schedule")
        self.save_sched_btn.clicked.connect(self.save_schedule)
        sched_row.addWidget(self.save_sched_btn)
        sched_row.addStretch()
        layout.addLayout(sched_row)

        btn_row = QHBoxLayout()
        self.create_btn = QPushButton("Create Backup Now")
        self.create_btn.clicked.connect(self.create_backup)
        btn_row.addWidget(self.create_btn)
        layout.addLayout(btn_row)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Filename", "Modified", "Size (KB)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        row = QHBoxLayout()
        self.restore_btn = QPushButton("Restore Selected")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_backup)
        row.addWidget(self.restore_btn)
        row.addWidget(self.delete_btn)
        row.addStretch()
        layout.addLayout(row)

    def refresh(self):
        self.table.setRowCount(0)
        for name, mtime, size in backup.list_backups():
            from datetime import datetime
            dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(dt))
            self.table.setItem(row, 2, QTableWidgetItem(f"{size // 1024}"))

    def create_backup(self):
        try:
            dst = backup.create_backup()
            QMessageBox.information(self, "Backup Created", f"Backup saved to:\n{dst}")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_schedule(self):
        enabled = self.scheduler_enable.isChecked()
        interval = int(self.interval_spin.value())
        settings.set_value("backup_automatic", enabled)
        settings.set_value("backup_interval_minutes", interval)
        QMessageBox.information(self, "Schedule Saved",
            f"Automatic backups {'enabled' if enabled else 'disabled'}.\nInterval: {interval} minutes")
        self.accept()

    def _selected(self):
        sel = self.table.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Error", "Select a backup first.")
            return None
        row = sel[0].row()
        name = self.table.item(row, 0).text()
        return name

    def restore_backup(self):
        name = self._selected()
        if not name:
            return
        reply = QMessageBox.question(self, "Confirm Restore",
            "Restoring will overwrite the current database. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            backup.restore_backup(name)
            QMessageBox.information(self, "Restored", "Database restored. Restart the app to see changes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_backup(self):
        name = self._selected()
        if not name:
            return
        reply = QMessageBox.question(self, "Confirm Delete",
            f"Delete backup {name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        backup.delete_backup(name)
        self.refresh()

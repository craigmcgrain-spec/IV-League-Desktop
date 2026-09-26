import os
import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QLabel, QSpinBox, QCheckBox,
    QComboBox, QTimeEdit, QGroupBox, QHeaderView
)
from PyQt6.QtCore import Qt, QTime
from ..database import backup, settings


class BackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup & Restore Manager")
        self.setMinimumWidth(750)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ── Automatic Schedule Group ─────────────────────────
        sched_group = QGroupBox("Automatic Backup Schedule")
        sched_layout = QVBoxLayout(sched_group)

        self.scheduler_enable = QCheckBox("Enable automatic backups")
        self.scheduler_enable.setChecked(bool(settings.get("backup_automatic", False)))
        self.scheduler_enable.toggled.connect(self._toggle_schedule_inputs)
        sched_layout.addWidget(self.scheduler_enable)

        opts_row = QHBoxLayout()
        opts_row.addWidget(QLabel("Schedule type:"))
        self.schedule_type_combo = QComboBox()
        self.schedule_type_combo.addItems([
            "Interval (every X hours/minutes)",
            "Daily at specific time",
            "Specific days of the week"
        ])
        curr_mode = settings.get("backup_schedule_mode", "interval")
        if curr_mode == "weekly_days":
            self.schedule_type_combo.setCurrentIndex(2)
        elif curr_mode == "daily_time":
            self.schedule_type_combo.setCurrentIndex(1)
        else:
            self.schedule_type_combo.setCurrentIndex(0)
        self.schedule_type_combo.currentIndexChanged.connect(self._on_schedule_type_changed)
        opts_row.addWidget(self.schedule_type_combo)

        # Interval inputs
        self.interval_container = QGroupBox()
        self.interval_container.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
        int_row = QHBoxLayout(self.interval_container)
        int_row.setContentsMargins(0, 0, 0, 0)
        int_row.addWidget(QLabel("Every:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 10080)  # 5 min up to 7 days
        self.interval_spin.setValue(int(settings.get("backup_interval_minutes", 1440)))
        self.interval_spin.setSuffix(" min")
        int_row.addWidget(self.interval_spin)
        opts_row.addWidget(self.interval_container)

        # Daily time inputs
        self.daily_container = QGroupBox()
        self.daily_container.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
        daily_row = QHBoxLayout(self.daily_container)
        daily_row.setContentsMargins(0, 0, 0, 0)
        daily_row.addWidget(QLabel("At time:"))
        self.daily_time_edit = QTimeEdit()
        curr_time_str = settings.get("backup_daily_time", "17:00")
        try:
            h, m = [int(x) for x in curr_time_str.split(":")]
            self.daily_time_edit.setTime(QTime(h, m))
        except Exception:
            self.daily_time_edit.setTime(QTime(17, 0))
        daily_row.addWidget(self.daily_time_edit)
        opts_row.addWidget(self.daily_container)

        # Retention input
        opts_row.addWidget(QLabel("Keep last:"))
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 100)
        self.retention_spin.setValue(int(settings.get("backup_max_retention", 20)))
        self.retention_spin.setSuffix(" files")
        opts_row.addWidget(self.retention_spin)

        self.save_sched_btn = QPushButton("Save Schedule")
        self.save_sched_btn.clicked.connect(self.save_schedule)
        opts_row.addWidget(self.save_sched_btn)
        opts_row.addStretch()

        sched_layout.addLayout(opts_row)

        # Weekly days of week selection container
        self.weekly_container = QGroupBox()
        self.weekly_container.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
        weekly_layout = QHBoxLayout(self.weekly_container)
        weekly_layout.setContentsMargins(0, 6, 0, 0)

        weekly_layout.addWidget(QLabel("Run on days:"))
        self.day_checkboxes = []
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        saved_days = settings.get("backup_weekly_days", [0, 1, 2, 3, 4])  # default Mon-Fri
        for idx, name in enumerate(day_names):
            cb = QCheckBox(name)
            cb.setChecked(idx in saved_days)
            weekly_layout.addWidget(cb)
            self.day_checkboxes.append(cb)

        weekly_layout.addWidget(QLabel("At time:"))
        self.weekly_time_edit = QTimeEdit()
        curr_wtime_str = settings.get("backup_weekly_time", "17:00")
        try:
            wh, wm = [int(x) for x in curr_wtime_str.split(":")]
            self.weekly_time_edit.setTime(QTime(wh, wm))
        except Exception:
            self.weekly_time_edit.setTime(QTime(17, 0))
        weekly_layout.addWidget(self.weekly_time_edit)
        weekly_layout.addStretch()

        sched_layout.addWidget(self.weekly_container)
        layout.addWidget(sched_group)

        # ── Quick Action Buttons ──────────────────────────────
        btn_row = QHBoxLayout()
        self.create_btn = QPushButton("Create Backup Now")
        self.create_btn.clicked.connect(self.create_backup)
        self.export_btn = QPushButton("Export Backup to File...")
        self.export_btn.clicked.connect(self.export_backup)
        self.import_btn = QPushButton("Restore from External File...")
        self.import_btn.clicked.connect(self.import_and_restore)

        btn_row.addWidget(self.create_btn)
        btn_row.addWidget(self.export_btn)
        btn_row.addWidget(self.import_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ── Backups Table ─────────────────────────────────────
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Filename", "Modified", "Size (KB)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # ── Table Actions ─────────────────────────────────────
        row = QHBoxLayout()
        self.verify_btn = QPushButton("Verify Integrity")
        self.verify_btn.clicked.connect(self.verify_selected)
        self.restore_btn = QPushButton("Restore Selected")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_btn.clicked.connect(self.delete_backup)

        row.addWidget(self.verify_btn)
        row.addWidget(self.restore_btn)
        row.addWidget(self.delete_btn)
        row.addStretch()
        layout.addLayout(row)

        self._on_schedule_type_changed(self.schedule_type_combo.currentIndex())
        self._toggle_schedule_inputs(self.scheduler_enable.isChecked())

    def _toggle_schedule_inputs(self, enabled):
        self.schedule_type_combo.setEnabled(enabled)
        self.interval_container.setEnabled(enabled)
        self.daily_container.setEnabled(enabled)
        self.weekly_container.setEnabled(enabled)
        self.retention_spin.setEnabled(enabled)

    def _on_schedule_type_changed(self, index):
        if index == 2:  # Weekly on specific days
            self.interval_container.setVisible(False)
            self.daily_container.setVisible(False)
            self.weekly_container.setVisible(True)
        elif index == 1:  # Daily at time
            self.interval_container.setVisible(False)
            self.daily_container.setVisible(True)
            self.weekly_container.setVisible(False)
        else:  # Interval
            self.interval_container.setVisible(True)
            self.daily_container.setVisible(False)
            self.weekly_container.setVisible(False)

    def refresh(self):
        self.table.setRowCount(0)
        for name, mtime, size in backup.list_backups():
            dt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(dt))
            self.table.setItem(row, 2, QTableWidgetItem(f"{max(1, size // 1024)}"))

    def create_backup(self):
        try:
            dst = backup.create_backup(is_auto=False)
            QMessageBox.information(self, "Backup Created", f"Online snapshot created safely:\n{dst}")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create backup:\n{e}")

    def export_backup(self):
        filename = self._selected()
        src = os.path.join(backup.BACKUP_DIR, filename) if filename else None
        
        default_name = filename or f"iv_league_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        dest_path, _ = QFileDialog.getSaveFileName(self, "Export Backup to File", default_name, "SQLite Database (*.db)")
        if not dest_path:
            return

        try:
            if src and os.path.exists(src):
                import shutil
                shutil.copy2(src, dest_path)
            else:
                backup.create_backup(filename=os.path.basename(dest_path), target_dir=os.path.dirname(dest_path))
            QMessageBox.information(self, "Exported", f"Backup exported successfully to:\n{dest_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def import_and_restore(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Backup File to Restore", "", "SQLite Database (*.db)")
        if not path:
            return

        is_valid, msg = backup.verify_backup(path)
        if not is_valid:
            QMessageBox.critical(self, "Integrity Check Failed", f"This file cannot be restored:\n{msg}")
            return

        reply = QMessageBox.question(
            self, "Confirm Restore",
            f"Restoring from:\n{path}\n\nA safety backup of your current database will be saved automatically.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            backup.restore_backup(path)
            QMessageBox.information(self, "Restored", "Database restored successfully. Please restart the app.")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", str(e))

    def save_schedule(self):
        enabled = self.scheduler_enable.isChecked()
        idx = self.schedule_type_combo.currentIndex()
        if idx == 2:
            mode = "weekly_days"
        elif idx == 1:
            mode = "daily_time"
        else:
            mode = "interval"

        interval = int(self.interval_spin.value())
        daily_time = self.daily_time_edit.time().toString("HH:mm")
        weekly_time = self.weekly_time_edit.time().toString("HH:mm")
        retention = int(self.retention_spin.value())

        selected_days = [i for i, cb in enumerate(self.day_checkboxes) if cb.isChecked()]
        if mode == "weekly_days" and not selected_days:
            QMessageBox.warning(self, "No Days Selected", "Please select at least one day of the week.")
            return

        settings.set_value("backup_automatic", enabled)
        settings.set_value("backup_schedule_mode", mode)
        settings.set_value("backup_interval_minutes", interval)
        settings.set_value("backup_daily_time", daily_time)
        settings.set_value("backup_weekly_time", weekly_time)
        settings.set_value("backup_weekly_days", selected_days)
        settings.set_value("backup_max_retention", retention)

        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        days_str = ", ".join(day_labels[d] for d in selected_days) if selected_days else "None"

        if mode == "weekly_days":
            desc = f"weekly on [{days_str}] at {weekly_time}"
        elif mode == "daily_time":
            desc = f"daily at {daily_time}"
        else:
            desc = f"every {interval} minutes"

        QMessageBox.information(
            self, "Schedule Saved",
            f"Automatic backups {'enabled' if enabled else 'disabled'} ({desc}).\nRetention: keep last {retention} files."
        )
        self.accept()

    def _selected(self):
        sel = self.table.selectedItems()
        if not sel:
            return None
        row = sel[0].row()
        item = self.table.item(row, 0)
        return item.text() if item else None

    def verify_selected(self):
        name = self._selected()
        if not name:
            QMessageBox.warning(self, "Error", "Select a backup first.")
            return
        is_valid, reason = backup.verify_backup(name)
        if is_valid:
            QMessageBox.information(self, "Integrity OK", f"Backup '{name}' passed SHA-256 and SQLite integrity checks.")
        else:
            QMessageBox.critical(self, "Integrity Error", f"Backup '{name}' failed validation:\n{reason}")

    def restore_backup(self):
        name = self._selected()
        if not name:
            QMessageBox.warning(self, "Error", "Select a backup first.")
            return

        reply = QMessageBox.question(
            self, "Confirm Restore",
            f"Restoring '{name}' will overwrite the current live database.\n\nA safety backup of your current database will be saved first.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            backup.restore_backup(name)
            QMessageBox.information(self, "Restored", "Database restored successfully. Please restart the app.")
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Restore Error", str(e))

    def delete_backup(self):
        name = self._selected()
        if not name:
            QMessageBox.warning(self, "Error", "Select a backup first.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete backup {name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        backup.delete_backup(name)
        self.refresh()

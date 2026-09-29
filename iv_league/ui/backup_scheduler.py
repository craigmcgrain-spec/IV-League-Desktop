from PyQt6.QtCore import QObject, QTimer
import datetime
from ..database import backup, settings


class BackupScheduler(QObject):
    """
    Handles automatic scheduled backups.
    Supports three modes:
    1. 'interval': every N minutes / hours
    2. 'daily_time': at a specific time of day every day (e.g. 17:00)
    3. 'weekly_days': on user-selected days of the week at a specific time
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Check timer runs every 30 seconds to evaluate schedule
        self.check_timer = QTimer(self)
        self.check_timer.setInterval(30 * 1000)
        self.check_timer.timeout.connect(self._check_and_run)

    def _check_and_run(self):
        enabled = bool(settings.get("backup_automatic", False))
        if not enabled:
            return

        mode = settings.get("backup_schedule_mode", "interval")  # 'interval' | 'daily_time' | 'weekly_days'
        now = datetime.datetime.now()
        last_run = float(settings.get("backup_last_run", 0))

        if mode == "weekly_days":
            # Check if today's day of week (0=Mon .. 6=Sun) is selected
            selected_days = settings.get("backup_weekly_days", [0, 1, 2, 3, 4])  # default weekdays
            today_weekday = now.weekday()
            if today_weekday not in selected_days:
                return

            target_time_str = settings.get("backup_weekly_time", "17:00")
            try:
                thour, tmin = [int(x) for x in target_time_str.split(":")]
            except Exception:
                thour, tmin = 17, 0

            today_target = now.replace(hour=thour, minute=tmin, second=0, microsecond=0)
            if now >= today_target and last_run < today_target.timestamp():
                self.run_backup()

        elif mode == "daily_time":
            target_time_str = settings.get("backup_daily_time", "17:00")
            try:
                thour, tmin = [int(x) for x in target_time_str.split(":")]
            except Exception:
                thour, tmin = 17, 0

            today_target = now.replace(hour=thour, minute=tmin, second=0, microsecond=0)
            if now >= today_target and last_run < today_target.timestamp():
                self.run_backup()
        else:
            # Interval mode (minutes)
            interval_min = int(settings.get("backup_interval_minutes", 1440))
            interval_sec = max(60, interval_min * 60)
            if (now.timestamp() - last_run) >= interval_sec:
                self.run_backup()

    def run_backup(self):
        try:
            max_retention = int(settings.get("backup_max_retention", 20))
            backup.create_backup(is_auto=True, max_auto_retention=max_retention)
            settings.set_value("backup_last_run", datetime.datetime.now().timestamp())
        except Exception as e:
            import sys
            print(f"Backup scheduler error: {e}", file=sys.stderr)

    def set_enabled(self, enabled):
        settings.set_value("backup_automatic", enabled)
        if enabled:
            self.check_timer.start()
        else:
            self.check_timer.stop()

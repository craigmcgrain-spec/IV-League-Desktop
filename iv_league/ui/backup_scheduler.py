from PyQt6.QtCore import QObject, QTimer
import datetime
from ..database import backup, settings

class BackupScheduler(QObject):
    def __init__(self, interval_minutes=1440, parent=None):
        super().__init__(parent)
        self.interval_ms = interval_minutes * 60 * 1000
        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self.run_backup)
        enabled = bool(settings.get("backup_automatic", False))
        if enabled:
            self.timer.start()

    def run_backup(self):
        try:
            backup.create_backup()
        except Exception:
            pass

    def set_interval_minutes(self, minutes):
        from ..database import settings
        self.interval_ms = max(1, minutes) * 60 * 1000
        self.timer.setInterval(self.interval_ms)
        settings.set_value("backup_interval_minutes", minutes)

    def set_enabled(self, enabled):
        if enabled:
            self.timer.start()
        else:
            self.timer.stop()
        settings.set_value("backup_automatic", enabled)

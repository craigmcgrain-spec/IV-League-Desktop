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
        # Timer is not started here; MainWindow controls lifecycle

    def run_backup(self):
        try:
            backup.create_backup()
            settings.set_value("backup_last_run", datetime.datetime.now().timestamp())
        except Exception as e:
            # Log error silently - in a full app, this would use proper logging
            import sys
            print(f"Backup scheduler error: {e}", file=sys.stderr)

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

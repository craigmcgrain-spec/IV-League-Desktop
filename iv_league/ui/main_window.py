from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QStatusBar, QVBoxLayout, QWidget,
    QToolButton
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import os
from .data_entry import DataEntryWidget
from .search_view import SearchViewWidget
from .invoicing import InvoicingWidget
from .facility_directory import FacilityDirectoryWidget
from .clinician_directory import ClinicianDirectoryWidget
from .csv_import import CsvImportDialog
from .company_info_dialog import CompanyInfoDialog
from .pricing import PricingWidget
from .theme import DARK_STYLE, LIGHT_STYLE
from .backup_dialog import BackupDialog
from .backup_scheduler import BackupScheduler
from ..database import settings

_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IV League")
        self.setMinimumSize(900, 600)
        self.setWindowIcon(QIcon(os.path.join(_ASSETS, "icon.svg")))

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

        import_action = file_menu.addAction("Import &CSV...")
        import_action.triggered.connect(self.open_csv_import)

        backup_action = file_menu.addAction("&Backup...")
        backup_action.triggered.connect(self.open_backup_dialog)

        file_menu.addSeparator()
        quit_action = file_menu.addAction("&Quit")
        quit_action.triggered.connect(self.close)

        edit_menu = menu.addMenu("&Edit")
        company_action = edit_menu.addAction("&Company Info...")
        company_action.triggered.connect(self.open_company_info)

        self.dark_mode = bool(settings.get("dark_mode", False))

        corner = QWidget()
        corner_layout = QVBoxLayout(corner)
        corner_layout.setContentsMargins(0, 2, 8, 2)
        self.theme_btn = QToolButton(corner)
        self.theme_btn.setToolTip("Toggle dark mode")
        self.theme_btn.setAutoRaise(True)
        self.theme_btn.setCheckable(True)
        self.theme_btn.clicked.connect(self._toggle_theme)
        corner_layout.addWidget(self.theme_btn, alignment=Qt.AlignmentFlag.AlignTop)
        menu.setCornerWidget(corner, Qt.Corner.TopRightCorner)

        self._apply_theme()
        interval = int(settings.get("backup_interval_minutes", 60*24))
        enabled = bool(settings.get("backup_automatic", False))
        if enabled:
            self.backup_scheduler = BackupScheduler(interval_minutes=interval)
            settings.set_value("backup_last_run", 0)
        else:
            self.backup_scheduler = BackupScheduler(interval_minutes=interval)
            self.backup_scheduler.timer.stop()

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        self.data_entry = DataEntryWidget()
        self.search_view = SearchViewWidget()
        self.invoicing = InvoicingWidget()
        self.facility_dir = FacilityDirectoryWidget()
        self.clinician_dir = ClinicianDirectoryWidget()
        self.pricing = PricingWidget()
        self.facility_dir.facility_added.connect(self.data_entry.refresh_facilities)
        self.facility_dir.facility_added.connect(self.invoicing.refresh_facilities)
        self.clinician_dir.clinician_added.connect(self.data_entry.refresh_clinicians)

        tabs.addTab(self.data_entry, "Data Entry")
        tabs.addTab(self.search_view, "Search Records")
        tabs.addTab(self.invoicing, "Invoicing")
        tabs.addTab(self.pricing, "Pricing")
        tabs.addTab(self.facility_dir, "Facilities")
        tabs.addTab(self.clinician_dir, "Clinicians")

        self.statusBar().showMessage("Ready")

    def open_csv_import(self):
        dlg = CsvImportDialog(self)
        dlg.exec()

    def open_company_info(self):
        dlg = CompanyInfoDialog(self)
        dlg.exec()

    def open_backup_dialog(self):
        dlg = BackupDialog(self)
        dlg.exec()

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        settings.set_value("dark_mode", self.dark_mode)
        self._apply_theme()

    def _apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet(DARK_STYLE)
            self.theme_btn.setText("☀️")
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self.theme_btn.setText("🌙")

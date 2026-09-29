from PyQt6.QtWidgets import QMainWindow, QTabWidget, QPushButton
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
from .theme import DARK_STYLE
from .backup_dialog import BackupDialog
from .backup_scheduler import BackupScheduler
from ..database import settings

_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IV League")
        self.setMinimumSize(900, 600)
        self.setWindowIcon(QIcon(os.path.join(_ASSETS, "icon.png")))

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

        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setCheckable(True)
        self.theme_btn.setChecked(self.dark_mode)
        self.theme_btn.setToolTip("Toggle dark / light mode")
        self.theme_btn.toggled.connect(self._on_theme_switch_toggled)
        menu.setCornerWidget(self.theme_btn, Qt.Corner.TopRightCorner)

        self._apply_theme()
        enabled = bool(settings.get("backup_automatic", False))
        self.backup_scheduler = BackupScheduler(self)
        if enabled:
            self.backup_scheduler.set_enabled(True)

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
        self.facility_dir.facility_added.connect(self.search_view._load_facilities)
        self.clinician_dir.clinician_added.connect(self.data_entry.refresh_clinicians)
        self.pricing.pricing_changed.connect(self.invoicing._refresh_pricing)
        self.pricing.tasks_changed.connect(self.data_entry._refresh_tasks)
        self.pricing.tasks_changed.connect(self.search_view._load_tasks)
        self.pricing.task_pricing_changed.connect(self.data_entry._refresh_tasks)
        self.pricing.supply_pricing_changed.connect(self.search_view.refresh_supply_columns)

        tabs.addTab(self.data_entry, "Data Entry")
        tabs.addTab(self.search_view, "Search Records")
        tabs.addTab(self.invoicing, "Invoicing")
        tabs.addTab(self.pricing, "Pricing")
        tabs.addTab(self.facility_dir, "Facilities")
        tabs.addTab(self.clinician_dir, "Clinicians")

        self.statusBar().showMessage("Ready")

    def open_csv_import(self):
        dlg = CsvImportDialog(self)
        dlg.import_complete.connect(self._on_csv_import_complete)
        dlg.clinicians_refreshed.connect(self._on_clinicians_refreshed)
        dlg.exec()

    def _on_csv_import_complete(self):
        self.data_entry.refresh_facilities()
        self.search_view._load_facilities()
        self.invoicing.refresh_facilities()
        self.facility_dir._refresh()

    def _on_clinicians_refreshed(self):
        self.clinician_dir._refresh()
        self.data_entry.refresh_clinicians()

    def open_company_info(self):
        dlg = CompanyInfoDialog(self)
        dlg.exec()

    def open_backup_dialog(self):
        dlg = BackupDialog(self)
        dlg.exec()

    def _on_theme_switch_toggled(self, checked):
        self.dark_mode = checked
        settings.set_value("dark_mode", self.dark_mode)
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(DARK_STYLE if self.dark_mode else "")

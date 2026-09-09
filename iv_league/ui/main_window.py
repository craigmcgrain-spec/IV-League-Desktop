from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QStatusBar, QVBoxLayout, QWidget
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

        file_menu.addSeparator()
        quit_action = file_menu.addAction("&Quit")
        quit_action.triggered.connect(self.close)

        edit_menu = menu.addMenu("&Edit")
        company_action = edit_menu.addAction("&Company Info...")
        company_action.triggered.connect(self.open_company_info)

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

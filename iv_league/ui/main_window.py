from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QStatusBar, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt
from .data_entry import DataEntryWidget
from .search_view import SearchViewWidget
from .invoicing import InvoicingWidget
from .facility_directory import FacilityDirectoryWidget
from .csv_import import CsvImportDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IV League")
        self.setMinimumSize(900, 600)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

        import_action = file_menu.addAction("Import &CSV...")
        import_action.triggered.connect(self.open_csv_import)

        file_menu.addSeparator()
        quit_action = file_menu.addAction("&Quit")
        quit_action.triggered.connect(self.close)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        self.data_entry = DataEntryWidget()
        self.search_view = SearchViewWidget()
        self.invoicing = InvoicingWidget()
        self.facility_dir = FacilityDirectoryWidget()
        self.facility_dir.facility_added.connect(self.data_entry.refresh_facilities)

        tabs.addTab(self.data_entry, "Data Entry")
        tabs.addTab(self.search_view, "Search Records")
        tabs.addTab(self.invoicing, "Invoicing")
        tabs.addTab(self.facility_dir, "Facilities")

        self.statusBar().showMessage("Ready")

    def open_csv_import(self):
        dlg = CsvImportDialog(self)
        dlg.exec()

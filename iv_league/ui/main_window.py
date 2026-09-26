from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QStatusBar, QVBoxLayout, QWidget,
    QPushButton, QAbstractButton
)
from PyQt6.QtGui import QIcon, QPainter, QColor, QBrush, QPen, QFont
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
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


class ThemeSwitch(QAbstractButton):
    """Custom toggle switch widget with sun/moon icons and animated knob."""
    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Toggle dark / light mode")
        self.setFixedSize(54, 26)
        self._thumb_position = 1.0 if checked else 0.0

        self._anim = QPropertyAnimation(self, b"thumb_position", self)
        self._anim.setDuration(160)
        self.toggled.connect(self._start_anim)

    @pyqtProperty(float)
    def thumb_position(self):
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    def _start_anim(self, checked):
        self._anim.stop()
        self._anim.setStartValue(self._thumb_position)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        radius = h / 2.0
        track_rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)

        # Interpolated track color
        if self._thumb_position > 0.5:
            # Dark mode active: deep slate track with bright teal border
            track_color = QColor("#0D1926")
            border_color = QColor("#00BFC2")
            thumb_color = QColor("#00A6A9")
            symbol_color = QColor("#FFFFFF")
        else:
            # Light mode active: pale cream track with navy border
            track_color = QColor("#F7F4ED")
            border_color = QColor("#008A8C")
            thumb_color = QColor("#008A8C")
            symbol_color = QColor("#FFFFFF")

        # Draw track background and border
        painter.setBrush(QBrush(track_color))
        painter.setPen(QPen(border_color, 1.5))
        painter.drawRoundedRect(track_rect, radius, radius)

        # Draw background icon indicator (Moon on right, Sun on left)
        font = QFont("Segoe UI Emoji, Apple Color Emoji, sans-serif", 9)
        painter.setFont(font)
        painter.setPen(QColor("#94A3B8"))
        if self._thumb_position > 0.5:
            # Sun hint on the left side
            painter.drawText(QRectF(4.0, 0.0, 20.0, h), Qt.AlignmentFlag.AlignCenter, "☀️")
        else:
            # Moon hint on the right side
            painter.drawText(QRectF(w - 24.0, 0.0, 20.0, h), Qt.AlignmentFlag.AlignCenter, "🌙")

        # Calculate thumb position
        margin = 3.0
        thumb_diameter = h - (margin * 2.0)
        x_min = margin
        x_max = w - margin - thumb_diameter
        thumb_x = x_min + (x_max - x_min) * self._thumb_position
        thumb_rect = QRectF(thumb_x, margin, thumb_diameter, thumb_diameter)

        # Draw thumb knob
        painter.setBrush(QBrush(thumb_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(thumb_rect)

        # Draw mini icon on the thumb
        mini_font = QFont("Segoe UI Emoji, Apple Color Emoji, sans-serif", 8)
        painter.setFont(mini_font)
        painter.setPen(symbol_color)
        icon_text = "🌙" if self._thumb_position > 0.5 else "☀️"
        painter.drawText(thumb_rect, Qt.AlignmentFlag.AlignCenter, icon_text)
        painter.end()


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

        corner = QWidget()
        corner_layout = QVBoxLayout(corner)
        corner_layout.setContentsMargins(0, 4, 10, 2)
        self.theme_btn = ThemeSwitch(corner, checked=self.dark_mode)
        self.theme_btn.toggled.connect(self._on_theme_switch_toggled)
        corner_layout.addWidget(self.theme_btn, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        menu.setCornerWidget(corner, Qt.Corner.TopRightCorner)

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
        if self.dark_mode:
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)
        if self.theme_btn.isChecked() != self.dark_mode:
            self.theme_btn.blockSignals(True)
            self.theme_btn.setChecked(self.dark_mode)
            self.theme_btn.blockSignals(False)

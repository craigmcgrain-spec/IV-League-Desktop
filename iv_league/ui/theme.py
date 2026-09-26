DARK_STYLE = """
/* IV League Desktop - Modern Slate & Teal Dark Theme */
/* Palette: Dark Navy #0D1926, Slate Surface #132233, Card #1B2D42, Teal Accent #00A6A9, Teal Hover #00BFC2, Text #E2E8F0 */

/* ── Global ────────────────────────────────────────────── */
QWidget {
    background-color: #0D1926;
    color: #E2E8F0;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
}

QMainWindow {
    background-color: #0D1926;
}

/* ── Tab Widget ────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #243B53;
    border-radius: 12px;
    background-color: #0D1926;
    top: -1px;
}

QTabBar::tab {
    background-color: #132233;
    color: #94A3B8;
    border: 1px solid #243B53;
    border-bottom: none;
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    margin-right: 4px;
    font-weight: 700;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #00A6A9;
    color: #FFFFFF;
    border-color: #00A6A9;
}

QTabBar::tab:hover:!selected {
    background-color: #1B2D42;
    color: #E2E8F0;
}

/* ── Group Boxes ───────────────────────────────────────── */
QGroupBox {
    background-color: #132233;
    border: 1px solid #243B53;
    border-radius: 14px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    font-weight: 700;
    font-size: 14px;
    color: #F8FAFC;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    top: 4px;
    padding: 0 6px;
    color: #00BFC2;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 0.8px;
}

/* ── Labels ────────────────────────────────────────────── */
QLabel {
    background-color: transparent;
    color: #E2E8F0;
    font-size: 14px;
}

/* ── Line Edits ────────────────────────────────────────── */
QLineEdit {
    background-color: #1B2D42;
    border: 1px solid #2B4562;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    color: #F8FAFC;
    selection-background-color: #00A6A9;
    selection-color: #FFFFFF;
}

QLineEdit:focus {
    border: 2px solid #00BFC2;
    background-color: #1F344D;
}

QLineEdit::placeholder {
    color: #64748B;
}

/* ── Combo Boxes ───────────────────────────────────────── */
QComboBox {
    background-color: #1B2D42;
    border: 1px solid #2B4562;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 14px;
    color: #F8FAFC;
    min-height: 20px;
}

QComboBox:focus {
    border: 2px solid #00BFC2;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 32px;
    border-left: 1px solid #2B4562;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    background-color: #16283C;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #1B2D42;
    color: #F8FAFC;
    border: 1px solid #2B4562;
    border-radius: 10px;
    padding: 6px;
    selection-background-color: #00A6A9;
    selection-color: #FFFFFF;
    outline: none;
}

/* ── Date / Time Edits ─────────────────────────────────── */
QDateEdit, QTimeEdit {
    background-color: #1B2D42;
    border: 1px solid #2B4562;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 14px;
    color: #F8FAFC;
    min-height: 20px;
}

QDateEdit:focus, QTimeEdit:focus {
    border: 2px solid #00BFC2;
}

QDateEdit::drop-down, QTimeEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 32px;
    border-left: 1px solid #2B4562;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    background-color: #16283C;
}

/* ── Spin Boxes ────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: #1B2D42;
    border: 1px solid #2B4562;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 14px;
    color: #F8FAFC;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #00BFC2;
}

/* ── Calendar Popup ────────────────────────────────────── */
QCalendarWidget {
    background-color: #132233;
    border: 1px solid #243B53;
    border-radius: 12px;
}

QCalendarWidget QToolButton {
    color: #F8FAFC;
    background-color: transparent;
    font-weight: 700;
}

QCalendarWidget QToolButton:hover {
    background-color: #1B2D42;
    border-radius: 6px;
}

QCalendarWidget QToolButton#qt_calendar_prevmonth,
QCalendarWidget QToolButton#qt_calendar_nextmonth {
    qproperty-icon: none;
    min-width: 28px;
}

QCalendarWidget QToolButton#qt_calendar_prevmonth { qproperty-text: "<"; }
QCalendarWidget QToolButton#qt_calendar_nextmonth { qproperty-text: ">"; }

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #00A6A9;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 6px;
}

QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {
    color: #FFFFFF;
}

QCalendarWidget QAbstractItemView {
    background-color: #132233;
    color: #E2E8F0;
    selection-background-color: #00A6A9;
    selection-color: #FFFFFF;
}

/* ── Buttons ───────────────────────────────────────────── */
QPushButton {
    background-color: #00A6A9;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-size: 14px;
    font-weight: 700;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #00BFC2;
}

QPushButton:pressed {
    background-color: #00888B;
}

QPushButton:disabled {
    background-color: #1B2D42;
    color: #64748B;
}

/* ── Table ─────────────────────────────────────────────── */
QTableWidget, QTableView {
    background-color: #132233;
    border: 1px solid #243B53;
    border-radius: 12px;
    gridline-color: #1E344D;
    selection-background-color: #00A6A9;
    selection-color: #FFFFFF;
    font-size: 13px;
    color: #E2E8F0;
}

QTableWidget::item, QTableView::item {
    padding: 8px 10px;
    border-bottom: 1px solid #182C42;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #00A6A9;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #0A1420;
    color: #F8FAFC;
    border: none;
    border-right: 1px solid #1A2E44;
    border-bottom: 1px solid #243B53;
    padding: 10px 12px;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 0.5px;
}

QHeaderView::section:last {
    border-right: none;
    border-top-right-radius: 12px;
}

QHeaderView::section:first {
    border-top-left-radius: 12px;
}

/* ── Scroll Bars ───────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #0D1926;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #243B53;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00A6A9;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: #0D1926;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #243B53;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00A6A9;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ── Menu Bar ──────────────────────────────────────────── */
QMenuBar {
    background-color: #0A1420;
    color: #E2E8F0;
    border: none;
    padding: 4px;
    font-weight: 600;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 14px;
    border-radius: 6px;
    color: #E2E8F0;
}

QMenuBar::item:selected {
    background-color: #00A6A9;
    color: #FFFFFF;
}

QMenu {
    background-color: #132233;
    border: 1px solid #243B53;
    border-radius: 10px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 6px;
    color: #E2E8F0;
}

QMenu::item:selected {
    background-color: #00A6A9;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background-color: #243B53;
    margin: 4px 12px;
}

/* ── Status Bar ────────────────────────────────────────── */
QStatusBar {
    background-color: #0A1420;
    color: #94A3B8;
    border: none;
    font-size: 12px;
    padding: 4px 12px;
}

/* ── Message Box & Dialogs ─────────────────────────────── */
QMessageBox, QDialog {
    background-color: #0D1926;
    color: #E2E8F0;
}

QMessageBox QLabel {
    color: #E2E8F0;
    font-size: 14px;
}

/* ── Tooltips ──────────────────────────────────────────── */
QToolTip {
    background-color: #1B2D42;
    color: #FFFFFF;
    border: 1px solid #00A6A9;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}

/* ── Checkboxes ────────────────────────────────────────── */
QCheckBox {
    background-color: transparent;
    color: #E2E8F0;
    font-size: 14px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #2B4562;
    background-color: #1B2D42;
}

QCheckBox::indicator:checked {
    background-color: #00A6A9;
    border-color: #00BFC2;
}
"""


LIGHT_STYLE = ""
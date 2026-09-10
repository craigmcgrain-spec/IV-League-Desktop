DARK_STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 6px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #ffffff;
}

QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background-color: #2b2b2b;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px;
    selection-background-color: #0d47a1;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #9ecbff;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #444444;
    selection-background-color: #0d47a1;
    selection-color: #ffffff;
}

QPushButton {
    background-color: #2d6a4f;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    color: #ffffff;
}

QPushButton:hover {
    background-color: #38855f;
}

QPushButton:pressed {
    background-color: #1e4d39;
}

QTableWidget, QTableView {
    background-color: #2b2b2b;
    alternate-background-color: #333333;
    gridline-color: #3a3a3a;
    border: 1px solid #444444;
    selection-background-color: #0d47a1;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #333333;
    color: #e0e0e0;
    border: none;
    border-right: 1px solid #3a3a3a;
    padding: 4px;
}

QTabWidget::pane {
    border: 1px solid #3a3a3a;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #262626;
    color: #b0b0b0;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #2b2b2b;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #303030;
}

QMenuBar {
    background-color: #1e1e1e;
    color: #ffffff;
}

QMenuBar::item {
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #333333;
}

QMenu {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #444444;
}

QMenu::item {
    color: #ffffff;
}

QMenu::item:selected {
    background-color: #0d47a1;
    color: #ffffff;
}

QMenu::item:selected {
    background-color: #0d47a1;
}

QStatusBar {
    background-color: #1e1e1e;
    color: #909090;
}

QScrollBar:vertical {
    background: #2b2b2b;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background: #555555;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QMessageBox, QDialog {
    background-color: #1e1e1e;
}

QCalendarWidget {
    background-color: #2b2b2b;
}

QCalendarWidget QToolButton {
    color: #e0e0e0;
    background-color: #333333;
}
"""


LIGHT_STYLE = ""
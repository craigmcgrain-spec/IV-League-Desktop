import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from iv_league.database.db import init_db, close_connection
from iv_league.ui.main_window import MainWindow


def load_stylesheet():
    path = os.path.join(os.path.dirname(__file__), "iv_league", "assets", "style.qss")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    print("Warning: Stylesheet not found at {path}", file=sys.stderr)
    return ""


def main():
    init_db()
    
    app = QApplication(sys.argv)
    app.setApplicationName("IV League")
    
    icon_path = os.path.join(os.path.dirname(__file__), "iv_league", "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
    
    window = MainWindow()
    window.show()
    
    exit_code = sys.exit(app.exec())
    
    # Clean up database connection on exit
    close_connection()


if __name__ == "__main__":
    main()

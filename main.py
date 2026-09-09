import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from iv_league.database.db import init_db
from iv_league.ui.main_window import MainWindow

BASE_DIR = os.path.dirname(__file__)


def load_stylesheet():
    path = os.path.join(BASE_DIR, "iv_league", "assets", "style.qss")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName("IV League")
    app.setWindowIcon(QIcon(os.path.join(BASE_DIR, "iv_league", "assets", "icon.svg")))
    app.setStyleSheet(load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from iv_league.database.db import init_db
from iv_league.ui.main_window import MainWindow

BASE_DIR = os.path.dirname(__file__)


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName("IV League")
    app.setWindowIcon(QIcon(os.path.join(BASE_DIR, "iv_league", "assets", "icon.svg")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
RSM/ANOVA ve Degisim Analizi GUI Uygulamasi
Ana giris noktasi.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui.main_window import MainWindow
from utils import get_icon_path


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Data Analysis")
    icon_path = get_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

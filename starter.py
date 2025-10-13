import sys
from windows import MainWindow
from PyQt6.QtWidgets import QApplication


def starter():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

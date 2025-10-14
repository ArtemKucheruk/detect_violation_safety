import sys
from windows import MainWindow
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.uic import loadUi
from utils import logger


class InitWindow(QDialog):
    def __init__(self):
        super(InitWindow, self).__init__()
        loadUi("ui.ui", self)

def starter():
    app = QApplication(sys.argv)
    logger.info("app was initialized")
    window = InitWindow()
    window.show()
    app.exec()

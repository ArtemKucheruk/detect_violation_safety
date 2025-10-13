import sys
from windows import MainWindow
from PyQt6.QtWidgets import QApplication
from utils import logger


def starter():
    app = QApplication(sys.argv)
    logger.info("app was initialized")
    window = MainWindow()
    window.show()
    app.exec()

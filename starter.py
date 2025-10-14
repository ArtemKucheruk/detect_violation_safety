import sys

from windows.main_window_funcs import MenuFuncs
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QFileDialog
from PyQt6.uic import loadUi
from utils import logger


class InitWindow(QDialog):
    def choose_file(self):
        file_name = MenuFuncs.choose_file()
        # print(file_name)

    def __init__(self):
        super().__init__()
        loadUi("ui.ui", self)
        self.btn_choose_file = self.findChild(QPushButton, "btn_choose_file")
        self.btn_choose_file.clicked.connect(self.choose_file)


def starter():
    app = QApplication(sys.argv)
    logger.info("app was initialized")
    window = InitWindow()
    window.show()
    app.exec()

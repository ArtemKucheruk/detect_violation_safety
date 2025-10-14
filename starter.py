import sys
from windows.main_window_funcs import MenuFuncs
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.uic import loadUi
from utils import logger


class InitWindow(QDialog):
    def __init__(self):
        super(InitWindow, self).__init__()
        loadUi("ui.ui", self)
        #self.btn_choose_file.clicked.connect(MenuFuncs.choose_file)

def starter():
    app = QApplication(sys.argv)
    logger.info("app was initialized")
    window = InitWindow()
    window.show()
    app.exec()

from PyQt6.QtWidgets import QMainWindow
from utils import logger


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        logger.info("Main window was initialized")

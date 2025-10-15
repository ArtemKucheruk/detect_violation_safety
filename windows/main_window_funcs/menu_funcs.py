from PyQt6.QtWidgets import QFileDialog
from utils import logger

class MenuFuncs:
    @staticmethod
    def choose_file():
        file_name, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="Choose an MP4 file",
            directory="",
            filter="MP4 Files (*.mp4)"
        )

        if(file_name):
            logger.info("File selected")
            return file_name
        else:
            logger.error("No file selected")
            null = "NULL"
            return null
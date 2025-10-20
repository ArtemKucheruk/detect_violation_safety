import sys
import os
import datetime

from windows.main_window_funcs import MenuFuncs
from utils import logger
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QFileDialog, QLabel, QLineEdit, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from moviepy import VideoFileClip

class InitWindow(QDialog):
    def choose_file(self):
        file_path = MenuFuncs.choose_file()

        # Show a created_at datetime
        if file_path == "NULL" or file_path == "" or file_path is None:
            if hasattr(self, "lb_date"):
                self.lb_date.setText("file is not selected")
            else:
                logger.error("lb_date not found")
            return

        # Log file address into log browser
        self.txt_logs.append(f"Selected file: " + file_path.split('\\')[-1])

        file_create = os.stat(file_path).st_mtime
        file_create = datetime.datetime.fromtimestamp(file_create)
        formatted_date = file_create.strftime("%Y-%m-%d %H:%M:%S")

        if hasattr(self, "lb_date"):
            self.lb_date.setText(formatted_date)
        else:
            logger.error("lb_date not found")
            return

        # Show a file's location
        if hasattr(self, "lb_location"):
            self.lb_location.setText(file_path.split("\\")[-1])
        else:
            logger.error("lb_location not found")
            return

        # Show a file's name
        file_name = os.path.basename(file_path)
        if hasattr(self, "lb_name"):
            self.lb_name.setText(file_name)
        else:
            logger.error("lb_name not found")
            return

        # Show a size of file
        file_size = round(os.path.getsize(file_path) / 1024, 2)
        if hasattr(self, "lb_size"):
            if file_size > 1024:
                file_size = round((file_size / 1024), 2)
                if file_size > 1024:
                    file_size = round((file_size / 1024), 2)
                    self.lb_size.setText(str(file_size) + "GB")
                else:
                    self.lb_size.setText(str(file_size) + "MB")
            else:
                self.lb_size.setText(str(file_size) + "KB")
        else:
            logger.error("lb_size not found")
            return

        # Show a video duration
        clip = VideoFileClip(file_path)
        file_duration = clip.duration
        hours = int(file_duration // 3600)
        minutes = int((file_duration % 3600) // 60)
        seconds = int(file_duration % 60)
        # Convert from seconds to HH:MM:ss
        if hours == 0:
            file_duration = f"{minutes:02d}:{seconds:02d}"

        if hasattr(self, "lb_time"):
            self.lb_time.setText(file_duration)
        else:
            logger.error("lb_time not found")
            return

    def __init__(self):
        super().__init__()
        loadUi("ui.ui", self)
        self.setWindowFlags(Qt.WindowType.Window)
        self.btn_choose_file = self.findChild(QPushButton, "btn_choose_file")
        self.btn_choose_file.clicked.connect(self.choose_file)


def starter():
    app = QApplication(sys.argv)
    logger.info("app was initialized")
    window = InitWindow()
    window.show()
    app.exec()

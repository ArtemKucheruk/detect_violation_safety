from PyQt6.QtWidgets import QDialog, QApplication, QFileDialog
import os
import datetime


class MenuFuncs:
    @staticmethod
    def choose_file():
        print("choose_file")
        file_name, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="Choose an MP4 file",
            directory="",
            filter="MP4 Files (*.mp4)"
        )

        print(file_name)
        return file_name
        # options = QFileDialog.Option.DontUseNativeDialog
        # file_name, _ = QFileDialog.getOpenFileName(
        #     None,
        #     "Choose a file",
        #     "",
        #     "All Files (*)",
        #     options=options
        # )
        # print("choose_file3")

        # QFileDialog.getOpenFileName(parent=None, caption='', directory='', filter='', options=QFileDialog.Options())



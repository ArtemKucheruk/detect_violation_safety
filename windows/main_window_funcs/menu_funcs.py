from PyQt6.QtWidgets import QDialog, QApplication, QFileDialog
import os
import datetime


class MenuFuncs(QDialog):
    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a file", "", "All Files (*)",
                                                   options=QFileDialog.Options())
        # if file_path:
        #     self.lb_adress.setText("File address: " + file_path)
        #
        #     file_size = round(os.path.getsize(file_path) / 1024, 2)
        #     if file_size > 1024:
        #         file_size = round((file_size / 1024), 2)
        #         if file_size > 1024:
        #             file_size = round((file_size / 1024), 2)
        #             self.lb_size.setText("Size: " + str(file_size) + "GB")
        #         else:
        #             self.lb_size.setText("Size: " + str(file_size) + "MB")
        #     else:
        #         self.lb_size.setText("Size: " + str(file_size) + "KB")
        #
        #     file_type = str(os.path.splitext(file_path)[1])
        #     self.lb_type.setText("Type: " + file_type)
        #
        #     file_name = os.path.basename(file_path)
        #     self.lb_name.setText("Name: " + file_name)
        #
        #     file_create = os.stat(file_path).st_ctime
        #     file_create = datetime.datetime.fromtimestamp(file_create)
        #     formatted_date = file_create.strftime("%Y-%m-%d %H:%M:%S")
        #     self.lb_date.setText(str("Created: " + formatted_date))
        #
        #     file_mod = os.stat(file_path).st_mtime
        #     file_mod = datetime.datetime.fromtimestamp(file_mod)
        #     formatted_mod = file_mod.strftime("%Y-%m-%d %H:%M:%S")
        #     self.lb_date.setText(str("Modified: " + formatted_mod))
        #
        #     return file_path
        # else:
        #     print("No file selected")

        return
import csv
from pathlib import Path


class CsvManager:
    def __init__(self) -> None:
        self.file_path: str = (
            ""  # will change later, just don't know what exectly will do with it
        )

    def set_up_report_file(self):
        self._create_report_file()
        self._write_headers()

    def _create_report_file(self) -> str:
        Path(self.file_path).touch
        return self.file_path

    def _write_headers(self) -> None:
        with open(self.file_path, "w") as f:
            headers = [""]  # will add the all the require headers
            write = csv.DictWriter(f, fieldnames=headers)

            write.writeheader()


csv_manager = CsvManager()

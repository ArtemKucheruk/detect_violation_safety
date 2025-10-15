import csv
from pathlib import Path
from datetime import datetime
from .logger import logger


class CsvManager:
    def __init__(self) -> None:
        logger.info("csv manager object was initialized")
        self.result_folder: str = "./reports"

    def set_up_report_file(self, video_name, llm_analyze_result: list[str]):
        """Initialize a CSV report file with headers."""
        self._create_report_file(video_name)
        self._write_headers()
        self._write_analyze_report(
            llm_analyze_result
        )  # need to finish this method to send right data for the report file

    def _write_analyze_report(self, violation_results: list[str]) -> None:
        with open(self.file_path, "a") as f:
            for violation_row in violation_results:
                writer = csv.writer(f)
                writer.writerow(violation_row)
                f.close()

    def _get_file_path(self, video_name: str) -> str:
        file_name: str = f"{video_name}_result_{str(datetime.now())}.csv".replace(
            " ", "_"
        )
        file_path: str = f"{self.result_folder}/{file_name}"
        logger.info(f"file path for new report: {file_path}")
        return file_path

    def _create_report_file(self, video_name: str) -> str:
        self.file_path = self._get_file_path(video_name)
        logger.info("creating report file")
        """Create an empty CSV file if it doesn’t exist."""
        path = Path(self.file_path)
        path.touch(exist_ok=True)
        return str(path)

    def _write_headers(self):
        """Write CSV headers to the file."""
        headers = [
            "filename",
            "timestamp",
            "video frame number",
            "type violation",
            "accuracy",
        ]
        logger.info(f"start writing the headers for csv report file: {headers}")
        with open(self.file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()


csv_manager = CsvManager()

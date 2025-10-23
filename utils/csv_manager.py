import csv
import os
from pathlib import Path
from datetime import datetime
from .logger import logger


class CsvManager:
    def __init__(self) -> None:
        logger.info("csv manager object was initialized")
        # keep as relative path but ensure we create it later
        self.result_folder: str = "./reports"
        self.file_path: str | None = None

    def set_up_report_file(self, video_name, llm_analyze_result: list[str]):
        """Initialize a CSV report file with headers and write results."""
        self._create_report_file(video_name)
        self._write_headers()
        self._write_analyze_report(llm_analyze_result)

    def _write_analyze_report(self, violation_results: list[list]):
        # append rows; do not close inside the loop
        if not self.file_path:
            raise RuntimeError("Report file path is not set")
        if not violation_results:
            return
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for violation_row in violation_results:
                writer.writerow(violation_row)

    def _get_file_path(self, video_name: str) -> str:
        # video_name may be a path; use basename without extension
        base = Path(video_name).stem
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{base}_result_{timestamp}.csv"
        # ensure result_folder is inside cwd (preserve relative behavior)
        reports_dir = Path(self.result_folder)
        # if user passed an absolute path in result_folder, respect it; otherwise join with cwd
        if not reports_dir.is_absolute():
            reports_dir = Path.cwd() / reports_dir
        reports_dir = reports_dir.resolve()
        file_path = reports_dir / file_name
        logger.info(f"file path for new report: {file_path}")
        return str(file_path)

    def _create_report_file(self, video_name: str) -> str:
        self.file_path = self._get_file_path(video_name)
        logger.info("creating report file")
        # Create the directory if it doesn't exist
        path = Path(self.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # create empty file (touch) if not exists
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
        if not self.file_path:
            raise RuntimeError("Report file path is not set")
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


csv_manager = CsvManager()

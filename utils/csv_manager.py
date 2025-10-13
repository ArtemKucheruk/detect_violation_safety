import csv
from pathlib import Path
from datetime import datetime
from tkinter import Tk, filedialog, messagebox


class CsvManager:
    def __init__(self) -> None:
        self.file_path: str = ""

    def set_up_report_file(self, file_path: str, headers=None):
        """Initialize a CSV report file with headers."""
        self.file_path = file_path or "violations_report.csv"
        if headers is None:
            headers = ['filename', 'timestamp', 'video frame number', 'type violation', 'accuracy']
        self._create_report_file()
        self._write_headers(headers)

    def _create_report_file(self) -> str:
        """Create an empty CSV file if it doesn’t exist."""
        path = Path(self.file_path)
        path.touch(exist_ok=True)
        return str(path)

    def _write_headers(self, headers):
        """Write CSV headers to the file."""
        with open(self.file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

    def on_save_config(self, report, file_path: str | None = None):
        """Save system-generated report to CSV. If no file_path provided, ask user for save location."""
        if not file_path:
            root = Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(
                title="Save configuration",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile="violations.csv"
            )
            root.destroy()

        # default
        if not file_path:
            file_path = "violations.csv"

        fieldnames = ['filename', 'timestamp', 'video frame number', 'type violation', 'accuracy']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in report:
                    writer.writerow({
                        'filename': row.get('filename'),
                        'timestamp': timestamp,
                        'video frame number': row.get('video frame number') or row.get('vfn'),
                        'type violation': row.get('type violation'),
                        'accuracy': row.get('accuracy')
                    })
            messagebox.showinfo("Success", f"Report saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{e}")

    def on_load_config(self, report):
        """
        Load report content (system-provided list of dicts) into screen.
        No file reading. Simply reads and displays report data.
        """
        try:
            if not report:
                messagebox.showwarning("Warning", "No report data to load.")
                return []

            rows = []
            for idx, row in enumerate(report, start=1):
                print(f"Row {idx}:")
                print(f"  Filename: {row.get('filename')}")
                print(f"  Video Frame Number: {row.get('video frame number') or row.get('vfn')}")
                print(f"  Type Violation: {row.get('type violation')}")
                print(f"  Accuracy: {row.get('accuracy')}")
                print("-" * 40)
                rows.append(row)

            messagebox.showinfo("Success", f"Loaded {len(rows)} rows from system report.")
            return rows

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load report:\n{e}")
            return []



csv_manager = CsvManager()
csv_manager.set_up_report_file("violations_report.csv")
system_report = [
    {'filename': 'cam1.mp4', 'video frame number': '123', 'type violation': 'speed', 'accuracy': 0.95},
    {'filename': 'cam2.mp4', 'video frame number': '124', 'type violation': 'lane', 'accuracy': 0.89},
]
csv_manager.on_save_config(system_report)
data = csv_manager.on_load_config(system_report)
print(data)

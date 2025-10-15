from ultralytics import YOLO
from utils import csv_manager


class LlmAnalyze:
    def __init__(self) -> None:
        self.model = YOLO("")  # change to the path of the model

    def predict(self, video_file_name):
        result = self.model.predict(
            source=video_file_name,
            project="video_results",
            name="analysis_run",
            save=True,
            conf=0.25,
            save_txt=True,
            save_conf=True,
            exist_ok=True,
        )
        return result


llm_analyze = LlmAnalyze()

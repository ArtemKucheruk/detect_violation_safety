from ultralytics import YOLO
from utils import csv_manager
import cv2


class LlmAnalyze:
    def __init__(self) -> None:
        self.model = YOLO("")  # change to the path of the model

    def process_video(self, video_file_name: str) -> list[str]:
        video_results = self._predict_results(video_file_name)
        analyzed_result = self._analyze_results(video_results, video_file_name)

        csv_manager.set_up_report_file(video_file_name, analyzed_result)
        return analyzed_result

    def _predict_results(self, video_file_name):
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

    def _analyze_results(self, video_results, video_file_name: str) -> list[str]:
        cap = cv2.VideoCapture(video_file_name)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        violations_data = []

        for frame_idx, frame_result in enumerate(video_results):
            boxes = frame_result.boxes

            if boxes is not None and len(boxes) > 0:
                for i, box in enumerate(boxes):
                    timestamp_seconds = frame_idx / fps

                    violation_info = [  # change this dict to the list
                        video_file_name,  # file_name
                        round(timestamp_seconds, 2),  # timestamp of the violation
                        frame_idx,  # violation frame
                        frame_result.names[int(box.cls[i])],  # Class name
                        float(box.conf[i]),  # Confidence score
                    ]
                    violations_data.append(violation_info)

        return violations_data


llm_analyze = LlmAnalyze()

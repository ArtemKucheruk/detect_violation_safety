from ultralytics import YOLO
from utils import csv_manager
import cv2


class LlmAnalyze:
    def __init__(self) -> None:
        self.model = YOLO("yolo/best.pt")  # change to the path of the model

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
                # iterate each detected box and read its own cls/conf robustly
                for box in boxes:
                    timestamp_seconds = frame_idx / fps

                    # box.cls and box.conf may be scalars or 1-element arrays/tensors
                    # handle both shapes safely
                    try:
                        raw_cls = box.cls
                    except Exception:
                        raw_cls = getattr(box, "cls", None)
                    try:
                        raw_conf = box.conf
                    except Exception:
                        raw_conf = getattr(box, "conf", None)

                    if hasattr(raw_cls, "__len__") and len(raw_cls) > 0:
                        cls_idx = int(raw_cls[0])
                    else:
                        cls_idx = int(raw_cls)

                    if hasattr(raw_conf, "__len__") and len(raw_conf) > 0:
                        conf_val = float(raw_conf[0])
                    else:
                        conf_val = float(raw_conf)

                    # frame_result.names is usually a dict or list mapping index -> name
                    if isinstance(frame_result.names, dict):
                        class_name = frame_result.names.get(cls_idx, str(cls_idx))
                    else:
                        class_name = frame_result.names[cls_idx]

                    violation_info = [
                        video_file_name,                 # file_name
                        round(timestamp_seconds, 2),     # timestamp
                        frame_idx,                       # frame index
                        class_name,                      # class name
                        conf_val,                        # confidence
                    ]
                    violations_data.append(violation_info)

        return violations_data


llm_analyze = LlmAnalyze()

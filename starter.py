import sys
import os
import datetime
import threading
import time
import cv2
import glob
import re
import io
from pathlib import Path
import shutil

from windows.main_window_funcs import MenuFuncs
from utils import logger
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QFileDialog, QLabel, QLineEdit, QMessageBox, QProgressDialog, QWidget, QVBoxLayout
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from moviepy import VideoFileClip
from yolo.predict import llm_analyze

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

        # store selected file for later analysis
        self.selected_file = file_path

        # Log file address into log browser
        self.txt_logs.append(f"Selected file: " + os.path.basename(file_path))

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

        # connect analyze button (expects a QPushButton named "btn_analyze" in ui.ui)
        self.btn_analyze = self.findChild(QPushButton, "btn_analyze")
        if self.btn_analyze:
            self.btn_analyze.clicked.connect(self.analyze_file)
        else:
            logger.error("btn_analyze not found")

        # connect save/download report button
        self.btn_save = self.findChild(QPushButton, "btn_save")
        if self.btn_save:
            self.btn_save.clicked.connect(self.download_report)
        else:
            logger.error("btn_save not found")

        # keep references so QThread isn't garbage-collected
        self.analysis_thread = None
        self.analysis_worker = None

        # media player + video widget (created now so it's ready to embed)
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget(self)

        # try to embed the video_widget into a named container in the UI
        container_names = ["first_container", "video_container", "video_widget", "frame_video", "frame", "widget_video"]
        embedded = False
        for name in container_names:
            container = self.findChild(QWidget, name)
            if container is not None:
                try:
                    layout = container.layout()
                    if layout is None:
                        layout = QVBoxLayout(container)
                        container.setLayout(layout)
                    layout.addWidget(self.video_widget)
                    embedded = True
                    break
                except Exception:
                    continue
        if not embedded:
            # fallback: add to main dialog layout if available
            try:
                main_layout = self.layout()
                if main_layout is not None:
                    # place at top of main layout
                    main_layout.insertWidget(0, self.video_widget)
                    embedded = True
            except Exception:
                pass

        # if still not embedded, place it as a small child widget (not ideal but functional)
        if not embedded:
            self.video_widget.setGeometry(10, 10, 480, 270)
            self.video_widget.show()

        self.media_player.setVideoOutput(self.video_widget)

    def analyze_file(self):
        # lazy import to avoid startup dependency on heavy model

        if not hasattr(self, "selected_file") or not self.selected_file:
            QMessageBox.warning(self, "No file", "Please select a file before analysis.")
            return

        self.txt_logs.append("Starting analysis...")

        class Worker(QObject):
            log = pyqtSignal(str)
            progress = pyqtSignal(int)
            finished = pyqtSignal(list)
            error = pyqtSignal(str)

            def __init__(self, file_path):
                super().__init__()
                self.file_path = file_path
                self._results = None
                self._stop_requested = False

            def run(self):
                try:
                    labels_dir = os.path.join(os.getcwd(), "video_results", "analysis_run", "labels")
                    baseline = set(os.listdir(labels_dir)) if os.path.isdir(labels_dir) else set()

                    cap = cv2.VideoCapture(self.file_path)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
                    cap.release()
                    if total_frames == 0:
                        try:
                            clip = VideoFileClip(self.file_path)
                            fps = clip.fps or 25
                            total_frames = int(clip.duration * fps)
                        except Exception:
                            total_frames = 0

                    # run the heavy work in a plain python thread so we can poll label files from this loop
                    def target():
                        # redirect stdout/stderr in this thread to emit via Worker.log,
                        # and parse percentage numbers to emit progress too
                        class StreamEmitter(io.TextIOBase):
                            def write(self, s):
                                try:
                                    if not s:
                                        return len(s)
                                    # emit every non-empty line chunk
                                    for line in s.splitlines():
                                        txt = line.strip()
                                        if not txt:
                                            continue
                                        # emit as log to GUI
                                        try:
                                            self_outer.log.emit(txt)
                                        except Exception:
                                            pass
                                        # try to parse percent like "12%" or "progress: 12 %"
                                        m = re.search(r'(\d{1,3})\s*%', txt)
                                        if m:
                                            try:
                                                pct = int(m.group(1))
                                                pct = max(0, min(100, pct))
                                                self_outer.progress.emit(pct)
                                            except Exception:
                                                pass
                                except Exception:
                                    pass
                                return len(s)

                            def flush(self):
                                return None

                        # closure references to Worker instance signals
                        self_outer = self

                        old_out, old_err = sys.stdout, sys.stderr
                        sys.stdout = StreamEmitter()
                        sys.stderr = StreamEmitter()
                        try:
                            self._results = llm_analyze.process_video(self.file_path)
                        except Exception as e:
                            # forward exception to main thread via signal
                            self.error.emit(str(e))
                        finally:
                            # restore
                            try:
                                sys.stdout = old_out
                                sys.stderr = old_err
                            except Exception:
                                pass

                    th = threading.Thread(target=target, daemon=True)
                    th.start()

                    last_emit_time = 0.0
                    last_percent = 0
                    # Poll while the worker thread is running; emit progress periodically
                    while th.is_alive() and not self._stop_requested:
                        if os.path.isdir(labels_dir):
                            try:
                                current = set(os.listdir(labels_dir))
                                new_count = len(current - baseline)
                            except Exception:
                                new_count = 0
                        else:
                            new_count = 0

                        if total_frames > 0:
                            # map label files -> percent; ensure we show at least 1% when something appears
                            percent = int(new_count / max(1, total_frames) * 100)
                            if new_count > 0 and percent == 0:
                                percent = 1
                        else:
                            # unknown total_frames: act as a spinner that increases slowly
                            percent = min(99, last_percent + 1)

                        now = time.time()
                        if now - last_emit_time >= 0.5:
                            # only emit if percent changed (or periodically to show activity)
                            if percent != last_percent or (now - last_emit_time) > 2.0:
                                # emit progress update (this will be overridden if model stdout prints percents)
                                self.progress.emit(int(percent))
                                self.log.emit(f"Analyzing... {percent}% ({new_count} label files)")
                                last_percent = percent
                                last_emit_time = now

                        time.sleep(0.2)

                    # thread finished or stop requested: final emits
                    # if nested thread already sent 100% via stdout parsing, this is harmless
                    self.progress.emit(100)
                    self.log.emit("Analysis finished (background step). Gathering results...")
                    results = self._results or []
                    self.finished.emit(results)
                except Exception as e:
                    self.error.emit(str(e))

        # create progress dialog
        progress_dialog = QProgressDialog("Analyzing video...", "Cancel", 0, 100, self)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setAutoClose(False)
        progress_dialog.setAutoReset(False)
        progress_dialog.setValue(0)
        progress_dialog.show()

        # store references on self so they aren't garbage-collected
        self.analysis_worker = Worker(self.selected_file)
        self.analysis_thread = QThread()
        self.analysis_worker.moveToThread(self.analysis_thread)

        # connect signals to instance methods so we can cleanup reliably
        self.analysis_worker.log.connect(lambda s: self.txt_logs.append(s))
        self.analysis_worker.progress.connect(lambda p: progress_dialog.setValue(p))
        self.analysis_worker.error.connect(self._on_worker_error)
        self.analysis_worker.finished.connect(lambda results: self._on_analysis_finished(results, progress_dialog))

        # start the worker when the QThread starts
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_thread.start()

        # allow user to cancel from dialog
        progress_dialog.canceled.connect(self._cancel_analysis)

    def _on_worker_error(self, err: str):
        logger.exception(err)
        QMessageBox.critical(self, "Analysis error", err)
        # try to stop the thread if it's running
        if getattr(self, "analysis_thread", None) is not None and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait(2000)

    def _cancel_analysis(self):
        self.txt_logs.append("Analysis cancel requested")
        if getattr(self, "analysis_thread", None) is not None and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait(2000)
        # also clear references so subsequent analyses start fresh
        self.analysis_thread = None
        self.analysis_worker = None

    def _on_analysis_finished(self, results, progress_dialog=None):
        try:
            self.txt_logs.append(f"Analysis finished — {len(results)} violations found.")
            for v in results[:20]:
                self.txt_logs.append(str(v))
            # play analysis video if available
            try:
                self._play_latest_analysis_video()
            except Exception as e:
                logger.exception("Failed to play analysis video: %s", e)
        finally:
            if progress_dialog:
                progress_dialog.setValue(100)
                progress_dialog.close()

            if getattr(self, "analysis_thread", None) is not None:
                self.analysis_thread.quit()
                self.analysis_thread.wait()
            self.analysis_thread = None
            self.analysis_worker = None

    def _play_latest_analysis_video(self):
        """Find the most recent mp4 under video_results/analysis_run and play it in the embedded widget."""
        analysis_dir = Path(os.path.join(os.getcwd(), "video_results", "analysis_run"))
        if not analysis_dir.exists():
            self.txt_logs.append("No analysis results folder found to play.")
            return

        # look for mp4, mkv, mov files - pick newest
        candidates = []
        for ext in ("*.mp4", "*.mkv", "*.mov", "*.avi"):
            candidates += list(analysis_dir.glob(ext))
        if not candidates:
            # also check nested project output directory
            nested = list(analysis_dir.rglob("*.mp4"))
            candidates = nested

        if not candidates:
            self.txt_logs.append("No video file found in analysis results.")
            return

        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        video_path = str(latest)
        self.txt_logs.append(f"Playing analysis video: {os.path.basename(video_path)}")

        # stop any existing playback
        if self.media_player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            try:
                self.media_player.stop()
            except Exception:
                pass

        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        # on some platforms you may want to set volume
        try:
            self.audio_output.setVolume(0.6)
        except Exception:
            pass
        self.media_player.play()

    def download_report(self):
        """Let user pick a destination and copy the latest report from ./reports there."""
        reports_dir = Path(os.path.join(os.getcwd(), "reports"))
        if not reports_dir.exists():
            QMessageBox.warning(self, "No reports", "No reports folder found.")
            self.txt_logs.append("No reports folder found.")
            return

        # find the most recently modified csv in reports
        candidates = list(reports_dir.glob("*.csv"))
        if not candidates:
            self.txt_logs.append("No CSV reports available to save.")
            QMessageBox.information(self, "No reports", "No CSV reports found in ./reports.")
            return

        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        src_path = str(latest)
        default_name = latest.name

        # ask user where to save
        dest_path, _ = QFileDialog.getSaveFileName(self, "Save report as", default_name, "CSV Files (*.csv);;All Files (*)")
        if not dest_path:
            self.txt_logs.append("Save report cancelled by user.")
            return

        try:
            # ensure destination directory exists
            dest_dir = Path(dest_path).parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            self.txt_logs.append(f"Report saved to: {dest_path}")
            QMessageBox.information(self, "Saved", f"Report saved to:\n{dest_path}")
        except Exception as e:
            logger.exception("Failed to copy report: %s", e)
            QMessageBox.critical(self, "Save error", f"Failed to save report:\n{e}")

    def closeEvent(self, event):
        # ensure analysis thread is stopped before window is destroyed
        if getattr(self, "analysis_thread", None) is not None and self.analysis_thread.isRunning():
            self.txt_logs.append("Waiting for analysis thread to stop...")
            self.analysis_thread.quit()
            self.analysis_thread.wait(3000)
        # stop media player
        try:
            if getattr(self, "media_player", None) is not None:
                self.media_player.stop()
        except Exception:
            pass
        event.accept()


def starter():
    app = QApplication(sys.argv)
    logger.info("app was initialized")
    window = InitWindow()
    window.show()
    app.exec()

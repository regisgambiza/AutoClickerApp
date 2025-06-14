import os
import platform
import time
import threading
import json
import logging
import traceback
import subprocess

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTextEdit, QApplication
from PyQt6.QtGui import QIcon, QTextCursor
from PyQt6.QtCore import pyqtSignal, QObject
from core.calibrator import CalibrationWorker
from core.clicker import scan_for_phrase_and_click, scan_for_download_phrase_with_beep
from core.logger import setup_logging, LOG_PATH, logger
from core.utils import load_settings, save_settings, tesseract_found, success_beep
from core.update_checker import check_update_loop

class AutoClickerApp(QWidget):
    def __init__(self):
        super().__init__()
        try:
            if not os.path.exists("gui.ui"):
                raise FileNotFoundError("gui.ui not found in the current directory.")
            uic.loadUi("gui.ui", self)
            self.setFixedSize(480, 320)
            if os.path.exists("assets/app_icon.ico"):
                self.setWindowIcon(QIcon("app_icon.ico"))
            self.log("✅ UI loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load UI: {e}\n{traceback.format_exc()}")
            self.log(f"🚨 UI load failed: {e}. Please ensure 'gui.ui' exists and is valid. Exiting...")
            sys.exit(1)

        self.btn_calibrate.clicked.connect(self.start_calibration)
        self.btn_start.clicked.connect(self.start_threads)
        self.btn_stop.clicked.connect(self.stop_threads)
        self.btn_open_log.clicked.connect(self.open_log_folder)

        self.thread1 = self.thread2 = None
        self.stop_event = threading.Event()
        self.running = False
        self.button_position, self.monitor = load_settings()
        if self.button_position and self.monitor:
            self.log(f"📍 Using coordinates {self.button_position} on monitor {self.monitor}")
        else:
            self.log("⚠️ Invalid or no coordinates found. Please run calibration.")
        check_update_loop(self, self.log)


    def log(self, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        logger.info(full_msg)
        self.status.append(full_msg)
        self.status.moveCursor(QTextCursor.MoveOperation.End)
        QApplication.processEvents()

    def start_calibration(self):
        if hasattr(self, 'worker') and self.worker and threading.Thread(target=self.worker.run).is_alive():
            self.log("⚠️ Calibration already in progress. Please wait...")
            return
        self.worker = CalibrationWorker()
        self.worker.log_signal.connect(self.log)
        self.worker.finished.connect(self.calibration_finished)
        threading.Thread(target=self.worker.run, daemon=True, name="CalibrationThread").start()
        self.log("▶️ Calibration process started.")

    def calibration_finished(self, pos, monitor):
        if pos:
            self.button_position, self.monitor = pos, monitor
            save_settings(pos, monitor)
            success_beep()
            self.log("✅ Calibration completed and saved successfully.")
        else:
            self.log("❌ Calibration failed. Please ensure your mouse is over a valid screen area and retry.")

    def start_threads(self):
        if self.running:
            self.log("⚠️ Automation is already running. Stop it before starting again.")
            return
        if not self.button_position or not self.monitor:
            self.log("❌ No calibration data available. Please calibrate the app first.")
            return
        if not tesseract_found:
            self.log("❌ Tesseract OCR is not detected. Install it at C:\\Program Files\\Tesseract-OCR\\tesseract.exe and restart.")
            return

        self.log(f"▶️ Starting automation threads for position {self.button_position} on monitor {self.monitor}")
        self.running = True
        self.stop_event.clear()
        self.thread1 = threading.Thread(
            target=scan_for_phrase_and_click,
            args=(self.button_position, self.monitor, "PRESS TO CONTINUE PLAYING", 10, self.log, self.stop_event),
            daemon=True,
            name="ClickScannerThread"
        )
        self.thread2 = threading.Thread(
            target=scan_for_download_phrase_with_beep,
            args=(self.monitor, "CLICK TO DOWNLOAD", 10, self.log, self.stop_event),
            daemon=True,
            name="DownloadBeepThread"
        )
        self.thread1.start()
        self.thread2.start()
        self.log("✅ Automation threads started successfully.")

    def stop_threads(self):
        if self.running:
            self.log("⏹️ Initiating thread termination...")
            self.stop_event.set()
            if self.thread1:
                self.thread1.join(timeout=5)
            if self.thread2:
                self.thread2.join(timeout=5)
            self.running = False
            self.log("✅ Threads terminated successfully.")
        else:
            self.log("⚠️ No running threads to stop.")

    def open_log_folder(self):
        folder_path = os.path.dirname(os.path.abspath(LOG_PATH))
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
            self.log("🗂️ Log folder opened successfully.")
        except Exception as e:
            self.log(f"🚨 Failed to open log folder: {e}. Check file access permissions.")
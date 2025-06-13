import time
import threading
import pyautogui
import mss
from PyQt6.QtCore import pyqtSignal, QObject
from core.logger import logger

class CalibrationWorker(QObject):
    finished = pyqtSignal(object, object)
    log_signal = pyqtSignal(str)

    def run(self):
        self.log_signal.emit("🧭 Hover over the button in 30s. Move your mouse to the target position...")
        for i in range(30):
            self.log_signal.emit(f"⏳ {30 - i}s remaining...")
            time.sleep(1)
        try:
            pos = pyautogui.position()
            self.log_signal.emit(f"📍 Mouse position captured at {pos}")
            with mss.mss() as sct:
                for idx, monitor in enumerate(sct.monitors[1:], start=1):
                    self.log_signal.emit(f"🖥️ Checking monitor {idx} boundaries: {monitor}")
                    if monitor["left"] <= pos.x <= monitor["left"] + monitor["width"] and \
                       monitor["top"] <= pos.y <= monitor["top"] + monitor["height"]:
                        self.log_signal.emit(f"✅ Mouse position confirmed on monitor {idx}")
                        self.finished.emit(pos, monitor)
                        return
                self.log_signal.emit("❌ Mouse position not within any monitor. Please try again on a valid screen.")
        except Exception as e:
            self.log_signal.emit(f"🚨 Calibration error: {e}\n{traceback.format_exc()}")
            self.log_signal.emit("⚠️ Calibration failed. Ensure your screen is detected and retry.")
        self.finished.emit(None, None)
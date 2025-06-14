import os
import platform
import json
import pytesseract
import mss
import pyautogui
from core.logger import logger

tesseract_found = True
if platform.system() == "Windows":
    t_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(t_path):
        pytesseract.pytesseract.tesseract_cmd = t_path
    else:
        tesseract_found = False
        logger.warning("❌ Tesseract not found at default path. Please install Tesseract-OCR and set the path correctly.")
        if 'window' in globals() and hasattr(window, 'log'):
            window.log("⚠️ Tesseract not detected. Install it at C:\\Program Files\\Tesseract-OCR\\tesseract.exe to enable OCR.")

SETTINGS_FILE = "settings.json"
DEFAULT_COORDS = pyautogui.Point(x=914, y=611)  # Default coordinates
DEFAULT_MONITOR_INDEX = 1  # Default to primary monitor

def validate_coords(pos, monitor):
    """Validate if coordinates are within monitor boundaries."""
    try:
        if (monitor["left"] <= pos.x <= monitor["left"] + monitor["width"] and
            monitor["top"] <= pos.y <= monitor["top"] + monitor["height"]):
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Coordinate validation failed: {e}")
        return False

def save_settings(pos, monitor):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"x": pos.x, "y": pos.y, "monitor": monitor}, f)
        logger.info(f"✅ Settings saved for position {pos} on monitor {monitor}")
    except Exception as e:
        logger.error(f"❌ Failed to save settings: {e}")
        if 'window' in globals() and hasattr(window, 'log'):
            window.log(f"🚨 Failed to save settings: {e}. Check file permissions for {SETTINGS_FILE}.")

def load_settings():
    # Try default coordinates first
    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            if DEFAULT_MONITOR_INDEX < len(monitors):
                default_monitor = monitors[DEFAULT_MONITOR_INDEX]
                if validate_coords(DEFAULT_COORDS, default_monitor):
                    logger.info(f"✅ Using default coordinates {DEFAULT_COORDS} on monitor {DEFAULT_MONITOR_INDEX}")
                    return DEFAULT_COORDS, default_monitor
                else:
                    logger.warning(f"⚠️ Default coordinates {DEFAULT_COORDS} invalid for monitor {DEFAULT_MONITOR_INDEX}")
            else:
                logger.warning(f"⚠️ Default monitor index {DEFAULT_MONITOR_INDEX} out of range")
    except Exception as e:
        logger.error(f"❌ Failed to validate default settings: {e}")

    # Fall back to saved settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
                pos = pyautogui.Point(data["x"], data["y"])
                monitor = data["monitor"]
                if validate_coords(pos, monitor):
                    logger.info(f"✅ Loaded settings: position {pos}, monitor {monitor}")
                    return pos, monitor
                else:
                    logger.warning(f"⚠️ Saved coordinates {pos} invalid for monitor {monitor}")
        except Exception as e:
            logger.error(f"❌ Failed to load settings: {e}")
            if 'window' in globals() and hasattr(window, 'log'):
                window.log(f"⚠️ Failed to load settings: {e}. Calibration required.")
            return None, None

    logger.warning("⚠️ No valid settings found, calibration required.")
    if 'window' in globals() and hasattr(window, 'log'):
        window.log("⚠️ No valid coordinates found. Please calibrate the app.")
    return None, None

if platform.system() == "Windows":
    import winsound
    def beep(): winsound.Beep(1000, 300)
    def success_beep(): winsound.Beep(1200, 500)
else:
    def beep(): print("\a")
    def success_beep(): print("\a\a")
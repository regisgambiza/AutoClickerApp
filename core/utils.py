import os
import platform
import json
import pytesseract
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
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
                logger.info(f"✅ Loaded settings: position {pyautogui.Point(data['x'], data['y'])}, monitor {data['monitor']}")
                return pyautogui.Point(data["x"], data["y"]), data["monitor"]
        except Exception as e:
            logger.error(f"❌ Failed to load settings: {e}")
            if 'window' in globals() and hasattr(window, 'log'):
                window.log(f"⚠️ Failed to load settings: {e}. Using default values.")
            return None, None
    logger.warning("⚠️ No settings file found, using default values.")
    if 'window' in globals() and hasattr(window, 'log'):
        window.log("⚠️ No previous calibration found. Please calibrate the app.")
    return None, None

if platform.system() == "Windows":
    import winsound
    def beep(): winsound.Beep(1000, 300)
    def success_beep(): winsound.Beep(1200, 500)
else:
    def beep(): print("\a")
    def success_beep(): print("\a\a")
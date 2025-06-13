import time
import pyautogui
import cv2
import numpy as np
import mss
import traceback
from PIL import Image  # Added Image import
from core.ocr import preprocess_image, get_ocr_text_and_confidence
from core.logger import logger
from core.utils import beep

def scan_for_phrase_and_click(pos, monitor, phrase, interval, log_func, stop_event):
    iteration = 0
    with mss.mss() as sct:
        log_func(f"🔎 Starting scan_for_phrase_and_click on monitor {monitor}")
        if monitor['width'] <= 0 or monitor['height'] <= 0:
            log_func(f"🚨 Invalid monitor dimensions: {monitor}. Recalibrate or check display settings.")
            return
        while not stop_event.is_set():
            iteration += 1
            start_time = time.time()
            log_func(f"📸 [Iteration {iteration}] Capturing screenshot")
            try:
                screenshot = np.array(sct.grab(monitor))
                logger.debug(f"Screenshot shape: {screenshot.shape}")
                if screenshot.size == 0 or screenshot.shape[0] <= 0 or screenshot.shape[1] <= 0:
                    log_func(f"🚨 Empty or invalid screenshot: {screenshot.shape}. Check monitor configuration.")
                    time.sleep(interval)
                    continue
                image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                processed = preprocess_image(image)
                if processed is not None:
                    text, conf = get_ocr_text_and_confidence(Image.fromarray(processed))
                    text_upper = text.upper()
                    log_func(f"📝 OCR detected: Confidence {conf:.2f}%")
                    if phrase.upper() in text_upper and conf > 50:
                        log_func(f"🖱️ Click detected phrase '{phrase}' at {pos}")
                        pyautogui.click(pos)
                        beep()
                        time.sleep(3)
                    else:
                        log_func(f"⏳ Phrase '{phrase}' not found or low confidence. Sleeping for {interval}s")
                        time.sleep(interval)
                else:
                    log_func("❌ Processed image is None, skipping iteration. Retrying next cycle.")
                    time.sleep(interval)
            except Exception as e:
                log_func(f"🚨 Exception during scan: {e}\n{traceback.format_exc()}")
                log_func("⚠️ Scan paused. Check monitor settings, Tesseract, or restart the app.")
                time.sleep(interval)
            elapsed = time.time() - start_time
            log_func(f"⏱️ Iteration {iteration} took {elapsed:.3f} seconds")
        log_func("🛑 scan_for_phrase_and_click stopped")

def scan_for_download_phrase_with_beep(monitor, phrase, interval, log_func, stop_event):
    iteration = 0
    with mss.mss() as sct:
        log_func(f"🔎 Starting scan_for_download_phrase_with_beep on monitor {monitor}")
        if monitor['width'] <= 0 or monitor['height'] <= 0:
            log_func(f"🚨 Invalid monitor dimensions: {monitor}. Recalibrate or check display settings.")
            return
        while not stop_event.is_set():
            iteration += 1
            start_time = time.time()
            try:
                screenshot = np.array(sct.grab(monitor))
                logger.debug(f"Screenshot shape: {screenshot.shape}")
                if screenshot.size == 0 or screenshot.shape[0] <= 0 or screenshot.shape[1] <= 0:
                    log_func(f"🚨 Empty or invalid screenshot: {screenshot.shape}. Check monitor configuration.")
                    time.sleep(interval)
                    continue
                image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                processed = preprocess_image(image)
                if processed is not None:
                    text, conf = get_ocr_text_and_confidence(Image.fromarray(processed))
                    text_upper = text.upper()
                    log_func(f"📝 [Iteration {iteration}] OCR detected: Confidence {conf:.2f}%")
                    if phrase.upper() in text_upper and conf > 50:
                        log_func(f"🔔 Phrase '{phrase}' detected, beeping...")
                        while phrase.upper() in text_upper and conf > 50 and not stop_event.is_set():
                            beep()
                            time.sleep(0.8)
                            screenshot = np.array(sct.grab(monitor))
                            image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                            processed = preprocess_image(image)
                            text, conf = get_ocr_text_and_confidence(Image.fromarray(processed))
                            text_upper = text.upper()
                        time.sleep(interval)
                    else:
                        log_func(f"⏳ Phrase '{phrase}' not detected or low confidence. Sleeping for {interval}s")
                        time.sleep(interval)
                else:
                    log_func("❌ Processed image is None, skipping iteration. Retrying next cycle.")
                    time.sleep(interval)
            except Exception as e:
                log_func(f"🚨 Exception during download phrase scan: {e}\n{traceback.format_exc()}")
                log_func("⚠️ Beep scan paused. Check monitor, Tesseract, or restart the app.")
                time.sleep(interval)
            elapsed = time.time() - start_time
            log_func(f"⏱️ Iteration {iteration} took {elapsed:.3f} seconds")
        log_func("🛑 scan_for_download_phrase_with_beep stopped")
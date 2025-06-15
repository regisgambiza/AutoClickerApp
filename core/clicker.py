import time
import pyautogui
import cv2
import numpy as np
import mss
import traceback
from PIL import Image
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

def find_and_handle_reference_images(log_func, stop_event, region=None, confidence=0.8):
    """
    Searches for two reference images on the screen:
    - If 'assets/continue_playing.png' is found, clicks its center.
    - If 'assets/click_download.png' is found, beeps continuously until it's gone.
    Extensive debug messages are logged to both the app console and terminal.
    """
    import time
    import traceback
    from core.logger import logger
    from core.utils import beep

    continue_img_path = "assets/continue_playing.png"
    download_img_path = "assets/click_download.png"

    log_func(f"🔎 [find_and_handle_reference_images] Starting image search loop. Continue image: {continue_img_path}, Download image: {download_img_path}, Confidence: {confidence}, Region: {region}")
    logger.debug(f"[find_and_handle_reference_images] Entered function with continue_img_path={continue_img_path}, download_img_path={download_img_path}, region={region}, confidence={confidence}")

    while not stop_event.is_set():
        try:
            # Search for "click to continue playing"
            log_func("🖼️ Searching for 'click to continue playing' image on screen...")
            logger.debug("Attempting to locate 'click to continue playing' image on screen.")
            try:
                continue_location = pyautogui.locateOnScreen(continue_img_path, confidence=confidence, region=region)
            except pyautogui.ImageNotFoundException:
                continue_location = None
                log_func("❌ 'click to continue playing' image not found.")
                logger.debug("'click to continue playing' image not found.")

            if continue_location:
                center = pyautogui.center(continue_location)
                log_func(f"✅ Found 'click to continue playing' at {continue_location}, center: {center}. Clicking...")
                logger.info(f"Found 'click to continue playing' at {continue_location}, center: {center}. Clicking now.")
                pyautogui.click(center)
                beep()
                log_func("🖱️ Clicked the center of 'click to continue playing' image.")
                logger.debug("Clicked the center of 'click to continue playing' image. Exiting function.")
                return  # Exit after clicking

            # Search for "click to download"
            log_func("🖼️ Searching for 'click to download' image on screen...")
            logger.debug("Attempting to locate 'click to download' image on screen.")
            try:
                download_location = pyautogui.locateOnScreen(download_img_path, confidence=confidence, region=region)
            except pyautogui.ImageNotFoundException:
                download_location = None
                log_func("❌ 'click to download' image not found.")
                logger.debug("'click to download' image not found.")

            if download_location:
                log_func(f"🚨 Found 'click to download' at {download_location}. Starting beep loop until image disappears.")
                logger.warning(f"Found 'click to download' at {download_location}. Beeping until gone.")
                while download_location and not stop_event.is_set():
                    beep()
                    log_func("🔔 Beeping! 'Click to download' image still present.")
                    logger.debug("Beeped for 'click to download'. Checking again in 0.5s.")
                    time.sleep(0.5)
                    try:
                        download_location = pyautogui.locateOnScreen(download_img_path, confidence=confidence, region=region)
                    except pyautogui.ImageNotFoundException:
                        download_location = None
                        log_func("✅ 'click to download' image is gone. Stopped beeping.")
                        logger.info("'click to download' image is gone. Stopped beeping.")
                        break
            else:
                log_func("🔍 Neither image found. Sleeping for 0.7s before next scan.")
                logger.debug("Neither image found. Sleeping for 0.7s.")
                time.sleep(10)
        except Exception as e:
            log_func(f"❌ Exception in find_and_handle_reference_images: {e}\n{traceback.format_exc()}")
            logger.error(f"Exception in find_and_handle_reference_images: {e}\n{traceback.format_exc()}")
            time.sleep(1)
    log_func("🛑 [find_and_handle_reference_images] Stopped by stop_event.")
    logger.info("[find_and_handle_reference_images] Stopped by stop_event.")
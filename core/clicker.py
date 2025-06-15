import time
import pyautogui
import cv2
import numpy as np
import mss
import traceback
import os
import gc
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

def resize_image_to_fit(image_path, max_width, max_height, log_func):
    """Resize image to fit within max_width and max_height while maintaining aspect ratio."""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            log_func(f"❌ Failed to load image: {image_path}")
            logger.error(f"Failed to load image: {image_path}")
            return None
        height, width = img.shape[:2]
        log_func(f"📏 Image {image_path} dimensions: {width}x{height}")
        logger.debug(f"Image {image_path} dimensions: {width}x{height}")
        
        if width <= max_width and height <= max_height:
            log_func(f"✅ Image {image_path} dimensions are valid")
            return image_path

        # Calculate scaling factor to fit within max dimensions
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        log_func(f"🔄 Resizing {image_path} from {width}x{height} to {new_width}x{new_height}")
        logger.info(f"Resizing {image_path} from {width}x{height} to {new_width}x{new_height}")

        resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        resized_path = f"assets/resized_{os.path.basename(image_path)}"
        cv2.imwrite(resized_path, resized_img)
        log_func(f"💾 Saved resized image to {resized_path}")
        logger.info(f"Saved resized image to {resized_path}")
        return resized_path
    except Exception as e:
        log_func(f"❌ Error resizing image {image_path}: {e}\n{traceback.format_exc()}")
        logger.error(f"Error resizing image {image_path}: {e}\n{traceback.format_exc()}")
        return None
    finally:
        img = None

def locate_image_on_screen(image_path, monitor, confidence, log_func):
    """Locate image on monitor using OpenCV and mss screenshot."""
    try:
        # Validate image path
        if not os.path.exists(image_path):
            log_func(f"❌ Image file does not exist: {image_path}")
            logger.error(f"Image file does not exist: {image_path}")
            return None

        # Load template image
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if template is None:
            log_func(f"❌ Failed to load template image: {image_path}")
            logger.error(f"Failed to load template image: {image_path}")
            return None
        
        if template.size == 0 or template.shape[0] <= 0 or template.shape[1] <= 0:
            log_func(f"❌ Invalid template image: {image_path}, shape: {template.shape}")
            logger.error(f"Invalid template image: {image_path}, shape: {template.shape}")
            return None

        template_height, template_width = template.shape[:2]
        log_func(f"📏 Template {image_path} dimensions: {template_width}x{template_height}")
        logger.debug(f"Template {image_path} dimensions: {template_width}x{template_height}")

        # Short delay to stabilize
        time.sleep(0.1)

        # Capture screenshot
        with mss.mss() as sct:
            screenshot = np.array(sct.grab(monitor))
            if screenshot.size == 0 or screenshot.shape[0] <= 0 or screenshot.shape[1] <= 0:
                log_func(f"🚨 Empty or invalid screenshot for monitor {monitor}")
                logger.error(f"Empty or invalid screenshot for monitor {monitor}")
                return None
            
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            screenshot_height, screenshot_width = screenshot.shape[:2]
            log_func(f"📸 Screenshot dimensions: {screenshot_width}x{screenshot_height}")
            logger.debug(f"Screenshot dimensions: {screenshot_width}x{screenshot_height}")

            # Check dimensions
            if template_width > screenshot_width or template_height > screenshot_height:
                log_func(f"❌ Template {image_path} ({template_width}x{template_height}) exceeds screenshot ({screenshot_width}x{screenshot_height})")
                logger.error(f"Template {image_path} ({template_width}x{template_height}) exceeds screenshot ({screenshot_width}x{screenshot_height})")
                return None

            # Perform template matching
            try:
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                log_func(f"🔍 Match confidence: {max_val:.3f} (threshold: {confidence})")
                logger.debug(f"Match confidence: {max_val:.3f} at location {max_loc}")

                if max_val >= confidence:
                    # Calculate center of matched region
                    center_x = monitor["left"] + max_loc[0] + template_width // 2
                    center_y = monitor["top"] + max_loc[1] + template_height // 2
                    return (center_x, center_y, template_width, template_height)
                else:
                    return None
            except cv2.error as e:
                log_func(f"❌ OpenCV error during template matching for {image_path}: {e}\n{traceback.format_exc()}")
                logger.error(f"OpenCV error during template matching for {image_path}: {e}\n{traceback.format_exc()}")
                return None
            except MemoryError:
                log_func(f"❌ Memory error during template matching for {image_path}\n{traceback.format_exc()}")
                logger.error(f"Memory error during template matching for {image_path}\n{traceback.format_exc()}")
                return None

    except Exception as e:
        log_func(f"❌ Error locating image {image_path}: {e}\n{traceback.format_exc()}")
        logger.error(f"Error locating image {image_path}: {e}\n{traceback.format_exc()}")
        return None
    finally:
        # Clean up to prevent memory leaks
        template = None
        screenshot = None
        gc.collect()

def find_and_handle_reference_images(log_func, stop_event, confidence=0.8):
    """
    Searches for two reference images on all available monitors:
    - If 'assets/continue_playing.png' is found, clicks its center and continues scanning.
    - If 'assets/click_download.png' is found, beeps continuously until it's gone.
    Extensive debug messages are logged to both the app console and terminal.
    """
    import time
    import traceback
    import mss
    import os
    import gc
    from core.logger import logger
    from core.utils import beep

    continue_img_path = "assets/continue_playing.png"
    download_img_path = "assets/click_download.png"

    log_func(f"🔎 [find_and_handle_reference_images] Starting image search loop on all monitors. Continue image: {continue_img_path}, Download image: {download_img_path}, Confidence: {confidence}")
    logger.debug(f"[find_and_handle_reference_images] Entered function with continue_img_path={continue_img_path}, download_img_path={download_img_path}, confidence={confidence}")

    with mss.mss() as sct:
        monitors = sct.monitors[1:]  # [0] is the virtual full screen, [1:] are real monitors
        log_func(f"🖥️ Detected {len(monitors)} monitors.")
        logger.debug(f"Detected {len(monitors)} monitors: {monitors}")

        while not stop_event.is_set():
            try:
                found_any = False
                for idx, monitor in enumerate(monitors):
                    max_width, max_height = monitor["width"], monitor["height"]
                    
                    log_func(f"🔍 Scanning monitor {idx+1}...")
                    logger.debug(f"Scanning monitor {idx+1} with region {monitor}")

                    # Resize images if necessary
                    continue_img = resize_image_to_fit(continue_img_path, max_width, max_height, log_func)
                    download_img = resize_image_to_fit(download_img_path, max_width, max_height, log_func)
                    
                    if not continue_img or not download_img:
                        log_func("❌ Skipping iteration due to image loading or resizing failure.")
                        time.sleep(1)
                        continue

                    # Search for "click to continue playing"
                    log_func(f"🖼️ Searching for 'click to continue playing' on monitor {idx+1} region {monitor}...")
                    logger.debug(f"Attempting to locate 'click to continue playing' on monitor {idx+1} region {monitor}.")
                    continue_location = locate_image_on_screen(continue_img, monitor, confidence, log_func)

                    if continue_location:
                        center_x, center_y, width, height = continue_location
                        log_func(f"✅ Found 'click to continue playing' on monitor {idx+1} at center ({center_x}, {center_y}). Clicking...")
                        logger.info(f"Found 'click to continue playing' on monitor {idx+1} at center ({center_x}, {center_y}). Clicking now.")
                        pyautogui.click(center_x, center_y)
                        beep()
                        log_func("🖱️ Clicked the center of 'click to continue playing' image.")
                        logger.debug("Clicked the center of 'click to continue playing' image. Continuing scan.")
                        time.sleep(1)  # Delay to allow screen update
                        found_any = True
                    else:
                        log_func(f"❌ 'click to continue playing' not found on monitor {idx+1}.")
                        logger.debug(f"'click to continue playing' not found on monitor {idx+1}.")

                    # Search for "click to download"
                    log_func(f"🖼️ Searching for 'click to download' on monitor {idx+1} region {monitor}...")
                    logger.debug(f"Attempting to locate 'click to download' on monitor {idx+1} region {monitor}.")
                    download_location = locate_image_on_screen(download_img, monitor, confidence, log_func)

                    if download_location:
                        log_func(f"🚨 Found 'click to download' on monitor {idx+1}. Starting beep loop until image disappears.")
                        logger.warning(f"Found 'click to download' on monitor {idx+1}. Beeping until gone.")
                        while download_location and not stop_event.is_set():
                            beep()
                            log_func("🔔 Beeping! 'Click to download' image still present.")
                            logger.debug("Beeped for 'click to download'. Checking again in 0.5s.")
                            time.sleep(0.5)
                            download_location = locate_image_on_screen(download_img, monitor, confidence, log_func)
                        log_func("✅ 'click to download' image is gone. Stopped beeping.")
                        logger.info("'click to download' image is gone. Stopped beeping.")
                        found_any = True
                    else:
                        log_func(f"❌ 'click to download' not found on monitor {idx+1}.")
                        logger.debug(f"'click to download' not found on monitor {idx+1}.")

                    # Short delay between monitors
                    time.sleep(0.5)

                if not found_any:
                    log_func("🔍 Neither image found on any monitor. Sleeping for 10s before next scan cycle.")
                    logger.debug("Neither image found on any monitor. Sleeping for 10s.")
                    time.sleep(10)
                gc.collect()  # Clean up memory after each cycle
            except Exception as e:
                log_func(f"❌ Exception in find_and_handle_reference_images: {e}\n{traceback.format_exc()}")
                logger.error(f"Exception in find_and_handle_reference_images: {e}\n{traceback.format_exc()}")
                time.sleep(1)
        log_func("🛑 [find_and_handle_reference_images] Stopped by stop_event.")
        logger.info("[find_and_handle_reference_images] Stopped by stop_event.")
import cv2
import numpy as np
from PIL import Image
import pytesseract
import traceback
from core.logger import logger

def preprocess_image(image):
    try:
        logger.debug(f"Preprocessing image with shape: {image.shape}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        upscaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, thresh = cv2.threshold(upscaled, 180, 255, cv2.THRESH_BINARY)
        return thresh
    except Exception as e:
        logger.error(f"❌ Image preprocessing failed: {e}\n{traceback.format_exc()}")
        if 'window' in globals() and hasattr(window, 'log'):
            window.log(f"🚨 Image processing error: {e}. Ensure OpenCV is installed and compatible.")
        return None

def get_ocr_text_and_confidence(image):
    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        texts = data.get('text', [])
        confidences = data.get('conf', [])

        valid_confidences = []
        for c in confidences:
            try:
                conf_value = float(c) if isinstance(c, (str, int)) and str(c).strip() != '-1' else None
                if conf_value is not None and conf_value >= 0:
                    valid_confidences.append(conf_value)
            except (ValueError, TypeError):
                logger.warning(f"⚠️ Invalid confidence value skipped: {c}")
                continue

        avg_conf = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 0.0
        combined_text = ' '.join([t for t in texts if t.strip() != ''])
        logger.debug(f"✅ OCR completed with text: {combined_text}, confidence: {avg_conf:.2f}%")
        return combined_text, avg_conf
    except Exception as e:
        logger.error(f"❌ OCR failed: {e}\n{traceback.format_exc()}")
        if 'window' in globals() and hasattr(window, 'log'):
            window.log(f"🚨 OCR error: {e}. Verify Tesseract installation, image data, or restart the app.")
        return "", 0.0
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    try:
        documents_path = os.path.join(os.path.expanduser("~"), "Documents", "AutoClickerLogs")
        os.makedirs(documents_path, exist_ok=True)
        log_file = os.path.join(documents_path, "autoclicker.log")
        with open(os.path.join(documents_path, "write_test.txt"), "w") as f:
            f.write("test")
    except Exception as e:
        logger.warning(f"⚠️ Logging setup failed, falling back to local log file: {e}")
        log_file = "autoclicker.log"

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] (%(threadName)s) [%(funcName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger, log_file

logger, LOG_PATH = setup_logging()

def except_hook(exctype, value, tb):
    logger.critical(f"❌ Uncaught Exception: {exctype.__name__} - {str(value)}", exc_info=(exctype, value, tb))
    if 'window' in globals() and hasattr(window, 'log'):
        window.log(f"🚨 Critical Error: {exctype.__name__} - {str(value)}. Check logs at {LOG_PATH} for details.")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = except_hook
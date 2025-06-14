import json
import threading
import time
import urllib.request
import webbrowser
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import pyqtSignal, QObject

APP_VERSION = "3.1"  # Current version of the app
UPDATE_URL = "https://raw.githubusercontent.com/regisgambiza/AutoClickerApp/refs/heads/main/update.json"  # Replace with your actual update URL

class UpdateChecker(QObject):
    update_available = pyqtSignal(str, str, str)  # Signal for version, changelog, download_url

    def __init__(self, main_window, log_func):
        super().__init__()
        self.main_window = main_window
        self.log_func = log_func
        self.update_available.connect(self.show_update_dialog)

    def check_update_loop(self):
        def check_once():
            try:
                self.log_func("⏳ Checking for updates...")
                with urllib.request.urlopen(UPDATE_URL, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    latest_version = data["latest_version"]
                    if latest_version > APP_VERSION:
                        self.log_func(f"🚨 New version v{latest_version} available.")
                        changelog = data.get("changelog", "")
                        download_url = data.get("download_url")
                        self.update_available.emit(latest_version, changelog, download_url)
                        return True  # Update found
                    else:
                        self.log_func("✅ You are using the latest version.")
            except Exception as e:
                self.log_func(f"🌐 No network or failed to check for updates: {e}")
            return False

        def update_loop():
            while True:
                updated = check_once()
                if updated:
                    break
                time.sleep(300)  # Retry every 5 minutes

        threading.Thread(target=update_loop, daemon=True).start()

    def show_update_dialog(self, version, changelog, download_url):
        msg = f"A new version (v{version}) is available!\n\nChangelog:\n{changelog}\n\nYou must update to continue."
        QMessageBox.critical(self.main_window, "Update Required", msg)
        webbrowser.open(download_url)
        self.log_func("🔒 Application is exiting until updated.")
        self.main_window.close()
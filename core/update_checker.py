
import json
import threading
import time
import urllib.request
import webbrowser
from PyQt6.QtWidgets import QMessageBox

APP_VERSION = "3.0"  # Current version of the app
UPDATE_URL = "https://yourdomain.com/update.json"  # Replace with your actual update URL

def check_update_loop(main_window, log_func):
    def check_once():
        try:
            log_func("⏳ Checking for updates...")
            with urllib.request.urlopen(UPDATE_URL, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data["latest_version"]
                if latest_version > APP_VERSION:
                    log_func(f"🚨 New version v{latest_version} available.")
                    changelog = data.get("changelog", "")
                    download_url = data.get("download_url")
                    msg = f"A new version (v{latest_version}) is available!\n\nChangelog:\n{changelog}\n\nYou must update to continue."
                    QMessageBox.critical(main_window, "Update Required", msg)
                    webbrowser.open(download_url)
                    log_func("🔒 Application is exiting until updated.")
                    main_window.close()
                    return True  # update found and app closed
                else:
                    log_func("✅ You are using the latest version.")
        except Exception as e:
            log_func(f"🌐 No network or failed to check for updates: {e}")
        return False

    def update_loop():
        while True:
            updated = check_once()
            if updated:
                break
            time.sleep(300)  # Retry every 5 minutes

    threading.Thread(target=update_loop, daemon=True).start()

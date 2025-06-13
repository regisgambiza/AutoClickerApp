import sys
from PyQt6.QtWidgets import QApplication
from ui_mainwindow import AutoClickerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoClickerApp()
    window.show()
    sys.exit(app.exec())
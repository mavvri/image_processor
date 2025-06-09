import sys
import os
from PyQt5.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Sistema de Conteo de Coches")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Computer Vision Project")
    
    # Load global stylesheet if needed
    try:
        style_path = os.path.join(os.path.dirname(__file__), "app", "ui", "assets", "styles", "modern_style.qss")
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Global stylesheet not found, MainWindow will load its own styling.")

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

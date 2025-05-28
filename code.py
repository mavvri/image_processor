import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui_components import ImageProcessingApp  # Updated import

def main():
    """
    Función principal para ejecutar la aplicación.
    """

    app = QApplication(sys.argv)
    app.setApplicationName("Procesamiento Digital de Imágenes Completo")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("IPN-ESCOM")

    # Set default font for the application
    font = QFont("Segoe UI", 10) # Or another preferred font
    app.setFont(font)

    # Crear y mostrar la ventana principal
    window = ImageProcessingApp()  # Updated class name
    window.show()

    # Ejecutar el bucle de eventos de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
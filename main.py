import sys
from PyQt6.QtWidgets import QApplication
from ui_components import ImageProcessingApp

def main():
    """
    Función principal para ejecutar la aplicación.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Procesamiento Digital de Imágenes Completo")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("IPN-ESCOM")
    
    # Crear y mostrar la ventana principal
    window = ImageProcessingApp()
    window.show()
    
    # Ejecutar el bucle de eventos de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

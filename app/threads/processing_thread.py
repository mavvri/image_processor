from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import time
from app.core.image_processor import process_image_pipeline, convert_opencv_to_qimage

class ImageProcessingWorker(QObject):
    # Update signals to include progress and step information
    finished = pyqtSignal(list, int, list)  # list of QImage, int for count, list of descriptions
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)  # progress percentage, current step description
    step_completed = pyqtSignal(int, str)  # step index, step description

    def __init__(self, image_path: str, custom_params=None):
        super().__init__()
        self.image_path = image_path
        self.custom_params = custom_params
        self._is_running = True  # Flag to allow stopping the process

    def process(self):
        """Main processing method that runs in the worker thread."""
        try:
            if not self._is_running:
                self.error.emit("Proceso cancelado antes de iniciar.")
                return

            if not self.image_path:
                self.error.emit("Ruta de imagen no proporcionada.")
                return

            # Emit initial progress
            mode_text = "MANUAL" if self.custom_params else "AUTOMÁTICO"
            self.progress.emit(0, f"Cargando imagen en modo {mode_text}...")
            
            # Load image using OpenCV
            cv_img = cv2.imread(self.image_path)
            if cv_img is None:
                self.error.emit(f"No se pudo cargar la imagen: {self.image_path}")
                return

            if not self._is_running:
                self.error.emit("Proceso cancelado.")
                return

            self.progress.emit(10, f"Iniciando procesamiento en modo {mode_text}...")
            
            # Import here to avoid circular imports
            from app.core.image_processor import process_image_pipeline, convert_opencv_to_qimage

            # Call the image processing pipeline with custom parameters
            pipeline_cv_images, car_count, step_descriptions = process_image_pipeline(
                cv_img, self.custom_params
            )
            
            if not self._is_running:
                self.error.emit("Proceso cancelado antes de finalizar.")
                return

            self.progress.emit(80, "Convirtiendo imágenes...")
            
            # Convert each OpenCV image to QImage
            pipeline_q_images = []
            total_images = len(pipeline_cv_images)
            
            for i, img_cv in enumerate(pipeline_cv_images):
                if not self._is_running:
                    self.error.emit("Proceso cancelado durante conversión de imágenes.")
                    return
                
                try:
                    q_image = convert_opencv_to_qimage(img_cv)
                    pipeline_q_images.append(q_image)
                except Exception as e:
                    print(f"Warning: Error converting image {i}: {e}")
                    # Create a placeholder QImage if conversion fails
                    from PyQt5.QtGui import QImage
                    placeholder = QImage(100, 100, QImage.Format_RGB888)
                    placeholder.fill(0)
                    pipeline_q_images.append(placeholder)
                
                # Emit step completion
                if i < len(step_descriptions):
                    self.step_completed.emit(i, step_descriptions[i])
                
                # Update progress
                conversion_progress = 80 + int((i + 1) / total_images * 20)
                self.progress.emit(conversion_progress, f"Convirtiendo imagen {i+1}/{total_images}")
            
            self.progress.emit(100, f"Procesamiento completado en modo {mode_text}")
            
            # Emit the final results
            self.finished.emit(pipeline_q_images, car_count, step_descriptions)

        except Exception as e:
            error_msg = f"Error en el procesamiento: {str(e)}"
            print(f"Processing error details: {e}")  # Debug info
            self.error.emit(error_msg)
        finally:
            self._is_running = False  # Ensure flag is reset

    def stop(self):
        """Requests the worker to stop processing."""
        self._is_running = False


class ProcessingThread(QThread):
    """
    A simple QThread subclass.
    In the current implementation, MainWindow uses QThread directly and
    moves the ImageProcessingWorker to it. This ProcessingThread class
    is provided to fulfill the requirement but might not be strictly
    necessary if the direct QThread usage pattern is preferred.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def __del__(self):
        """Ensure thread is properly terminated on destruction."""
        if self.isRunning():
            self.quit()
            self.wait(3000)  # Wait up to 3 seconds

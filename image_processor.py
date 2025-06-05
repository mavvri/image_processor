import numpy as np
import cv2
from PyQt6.QtGui import QImage
from PyQt6.QtCore import QThread, pyqtSignal
from filters import ImageFilters
from segmentation import ImageSegmentation

class ImageProcessor(QThread):
    """
    Clase para procesar imágenes en un hilo separado.
    """
    # Definimos señales para comunicarnos con la interfaz de usuario
    started = pyqtSignal()
    finished = pyqtSignal()
    image_updated = pyqtSignal(QImage)
    parameters_calculated = pyqtSignal(dict)  # Nueva señal para parámetros calculados

    def __init__(self, image_path, filter_type='none', filter_params=None, 
                 segmentation_type='none', segmentation_params=None,
                 noise_level=0, apply_noise=False, second_image_path=None,
                 operation_type='none'):
        super().__init__()
        self.image_path = image_path
        self.second_image_path = second_image_path
        self.filter_type = filter_type
        self.filter_params = filter_params or {}
        self.segmentation_type = segmentation_type
        self.segmentation_params = segmentation_params or {}
        self.noise_level = noise_level
        self.apply_noise = apply_noise
        self.operation_type = operation_type
        self.stop_processing = False
        self.calculate_auto_params = False  # Flag for auto parameter calculation

    def add_noise(self, img):
        """Agregar ruido gaussiano a la imagen"""
        if self.noise_level > 0:
            row, col, ch = img.shape
            mean = 0
            sigma = self.noise_level
            gauss = np.random.normal(mean, sigma, (row, col, ch))
            noisy = img + gauss
            return np.clip(noisy, 0, 255).astype(np.uint8)
        return img

    def apply_filter(self, img):
        """Aplicar el filtro seleccionado con parámetros correctos"""
        # Filtros que no necesitan kernel_size
        no_kernel_filters = ['robinson', 'roberts', 'prewitt', 'sobel', 'kirsch', 'laplacian']
        
        # Crear parámetros filtrados según el tipo de filtro
        params = self.filter_params.copy()
        
        if self.filter_type in no_kernel_filters:
            # Remover kernel_size para filtros que no lo necesitan
            params.pop('kernel_size', None)
        
        try:
            if self.filter_type == 'averaging':
                kernel_size = params.get('kernel_size', 5)
                return ImageFilters.apply_averaging_filter(img, kernel_size)
            elif self.filter_type == 'weighted_averaging':
                kernel_size = params.get('kernel_size', 5)
                return ImageFilters.apply_weighted_averaging_filter(img, kernel_size)
            elif self.filter_type == 'median':
                kernel_size = params.get('kernel_size', 5)
                return ImageFilters.apply_median_filter(img, kernel_size)
            elif self.filter_type == 'mode':
                kernel_size = params.get('kernel_size', 5)
                return ImageFilters.apply_mode_filter(img, kernel_size)
            elif self.filter_type == 'bilateral':
                d = params.get('d', 9)
                sigma_color = params.get('sigma_color', 75)
                sigma_space = params.get('sigma_space', 75)
                return ImageFilters.apply_bilateral_filter(img, d, sigma_color, sigma_space)
            elif self.filter_type == 'max':
                kernel_size = params.get('kernel_size', 5)
                return ImageFilters.apply_max_filter(img, kernel_size)
            elif self.filter_type == 'min':
                kernel_size = params.get('kernel_size', 5)
                return ImageFilters.apply_min_filter(img, kernel_size)
            elif self.filter_type == 'gaussian':
                kernel_size = params.get('kernel_size', 5)
                sigma = params.get('sigma', 1.0)
                return ImageFilters.apply_gaussian_filter(img, kernel_size, sigma)
            elif self.filter_type == 'robinson':
                return ImageFilters.apply_robinson_filter(img)
            elif self.filter_type == 'roberts':
                return ImageFilters.apply_roberts_filter(img)
            elif self.filter_type == 'prewitt':
                return ImageFilters.apply_prewitt_filter(img)
            elif self.filter_type == 'sobel':
                return ImageFilters.apply_sobel_filter(img)
            elif self.filter_type == 'kirsch':
                return ImageFilters.apply_kirsch_filter(img)
            elif self.filter_type == 'canny':
                low_threshold = params.get('low_threshold', 50)
                high_threshold = params.get('high_threshold', 150)
                return ImageFilters.apply_canny_filter(img, low_threshold, high_threshold)
            elif self.filter_type == 'laplacian':
                return ImageFilters.apply_laplacian_filter(img)
            else:
                return img
        except Exception as e:
            print(f"Error applying filter {self.filter_type}: {e}")
            return img

    def apply_segmentation(self, img):
        """Aplicar la segmentación seleccionada"""
        try:
            if self.segmentation_type == 'mean':
                return ImageSegmentation.threshold_mean(img)
            elif self.segmentation_type == 'otsu':
                binary, threshold = ImageSegmentation.threshold_otsu(img)
                return binary
            elif self.segmentation_type == 'multi_otsu':
                # Check the actual parameter name expected by the method
                num_classes = self.segmentation_params.get('num_thresholds', 3)
                
                # Convert to grayscale if needed for analysis
                if len(img.shape) == 3:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                else:
                    gray = img.copy()
                
                # Check if image has enough unique values
                unique_values = len(np.unique(gray))
                
                # Automatically adjust number of classes based on image content
                optimal_classes = min(num_classes, max(2, unique_values - 1))
                
                if unique_values < num_classes:
                    print(f"Info: Image has {unique_values} unique values. Adjusting classes from {num_classes} to {optimal_classes}")
                
                # If still too few unique values, fall back to regular Otsu
                if optimal_classes < 2:
                    print("Info: Using regular Otsu due to limited image variation")
                    binary, threshold = ImageSegmentation.threshold_otsu(img)
                    return binary
                
                # Try multi-Otsu with optimal number of classes
                try:
                    result, thresholds = ImageSegmentation.multi_threshold_otsu(img, optimal_classes)
                except (TypeError, ValueError) as e:
                    if "discretization" in str(e) or "different values" in str(e):
                        # Try with even fewer classes
                        try:
                            fallback_classes = max(2, optimal_classes - 1)
                            print(f"Info: Retrying multi-otsu with {fallback_classes} classes")
                            result, thresholds = ImageSegmentation.multi_threshold_otsu(img, fallback_classes)
                        except Exception:
                            # Final fallback to regular Otsu
                            print("Info: Multi-otsu failed, using regular Otsu")
                            binary, threshold = ImageSegmentation.threshold_otsu(img)
                            return binary
                    else:
                        # Try different parameter names
                        try:
                            result, thresholds = ImageSegmentation.multi_threshold_otsu(img, num_thresholds=optimal_classes)
                        except (TypeError, ValueError):
                            try:
                                result, thresholds = ImageSegmentation.multi_threshold_otsu(img, classes=optimal_classes)
                            except (TypeError, ValueError):
                                # Fallback to basic call without parameters
                                try:
                                    result, thresholds = ImageSegmentation.multi_threshold_otsu(img)
                                except Exception:
                                    # Final fallback to regular Otsu
                                    print("Info: Multi-otsu failed, using regular Otsu")
                                    binary, threshold = ImageSegmentation.threshold_otsu(img)
                                    return binary
                return result
            elif self.segmentation_type == 'kapur':
                binary, threshold = ImageSegmentation.kapur_entropy_threshold(img)
                return binary
            elif self.segmentation_type == 'band':
                low_threshold = self.segmentation_params.get('low_threshold', 100)
                high_threshold = self.segmentation_params.get('high_threshold', 200)
                return ImageSegmentation.band_threshold(img, low_threshold, high_threshold)
            elif self.segmentation_type == 'adaptive':
                block_size = self.segmentation_params.get('block_size', 11)
                # Ensure block_size is odd
                if block_size % 2 == 0:
                    block_size += 1
                try:
                    return ImageSegmentation.adaptive_threshold(img, block_size)
                except TypeError:
                    # Try with different parameter names
                    try:
                        return ImageSegmentation.adaptive_threshold(img, block_size=block_size)
                    except TypeError:
                        # Fallback to default
                        return ImageSegmentation.adaptive_threshold(img)
            elif self.segmentation_type == 'histogram_min':
                binary, threshold = ImageSegmentation.histogram_minimum_threshold(img)
                return binary
            else:
                return img
        except Exception as e:
            print(f"Error applying segmentation {self.segmentation_type}: {e}")
            return img

    def apply_two_image_operation(self, img1, img2):
        """Aplicar operaciones entre dos imágenes"""
        # Asegurar que ambas imágenes tengan el mismo tamaño
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        if h1 != h2 or w1 != w2:
            img2 = cv2.resize(img2, (w1, h1))
        
        # Convertir a float para evitar overflow
        img1_f = img1.astype(np.float32)
        img2_f = img2.astype(np.float32)
        
        if self.operation_type == 'suma':
            result = cv2.add(img1_f, img2_f)
        elif self.operation_type == 'resta':
            result = cv2.absdiff(img1_f, img2_f)
        elif self.operation_type == 'multiplicacion':
            result = cv2.multiply(img1_f, img2_f) / 255.0
        elif self.operation_type == 'division':
            result = cv2.divide(img1_f, img2_f + 1e-10) * 255.0
        elif self.operation_type == 'promedio':
            result = (img1_f + img2_f) / 2.0
        elif self.operation_type == 'diferencia':
            result = cv2.absdiff(img1_f, img2_f)
        elif self.operation_type == 'and':
            result = cv2.bitwise_and(img1.astype(np.uint8), img2.astype(np.uint8)).astype(np.float32)
        elif self.operation_type == 'or':
            result = cv2.bitwise_or(img1.astype(np.uint8), img2.astype(np.uint8)).astype(np.float32)
        elif self.operation_type == 'xor':
            result = cv2.bitwise_xor(img1.astype(np.uint8), img2.astype(np.uint8)).astype(np.float32)
        else:
            return img1
        
        return np.clip(result, 0, 255).astype(np.uint8)

    def calculate_automatic_parameters(self, img):
        """Calcular parámetros automáticos para detección de objetos"""
        # Convertir a escala de grises si es necesario
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Calcular estadísticas básicas
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        unique_values = len(np.unique(gray))
        
        # Parámetros automáticos para diferentes filtros/segmentaciones
        auto_params = {
            'canny_low': int(max(10, mean_val - std_val)),
            'canny_high': int(min(255, mean_val + std_val)),
            'adaptive_block_size': self._find_optimal_block_size(gray),
            'bilateral_d': 9,
            'bilateral_sigma_color': std_val,
            'bilateral_sigma_space': std_val,
            'gaussian_sigma': max(1, std_val / 50),
            'kernel_size': self._find_optimal_kernel_size(gray),
            'otsu_threshold': cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0],
            'optimal_multi_otsu_classes': min(5, max(2, unique_values - 1))  # Suggest optimal classes
        }
        
        return auto_params

    def _find_optimal_block_size(self, gray):
        """Encontrar tamaño de bloque óptimo para umbralización adaptativa"""
        # Usar análisis de textura para determinar el tamaño
        h, w = gray.shape
        size = min(h, w) // 20
        return max(3, size + (size % 2 == 0))  # Asegurar que sea impar

    def _find_optimal_kernel_size(self, gray):
        """Encontrar tamaño de kernel óptimo"""
        # Basado en el análisis de la imagen
        h, w = gray.shape
        base_size = min(h, w) // 100
        return max(3, base_size + (base_size % 2 == 0))

    def run(self):
        """Método principal de procesamiento"""
        try:
            self.started.emit()
            
            # Check if image_path is valid and not empty
            if not self.image_path or not self.image_path.strip():
                print("Error: Empty or invalid image path")
                return
            
            img = cv2.imread(self.image_path)
            if img is None:
                print(f"Error: Could not read image from path: {self.image_path}")
                return

            current_img = img.copy()

            # Si hay una segunda imagen y una operación, aplicar operación entre imágenes
            if self.second_image_path and self.operation_type != 'none':
                img2 = cv2.imread(self.second_image_path)
                if img2 is not None:
                    current_img = self.apply_two_image_operation(current_img, img2)

            if self.stop_processing:
                return

            # Aplicar ruido si está habilitado
            if self.apply_noise:
                current_img = self.add_noise(current_img)

            if self.stop_processing:
                return

            # Calcular parámetros automáticos si se solicita
            if self.calculate_auto_params:
                auto_params = self.calculate_automatic_parameters(current_img)
                self.parameters_calculated.emit(auto_params)

            if self.stop_processing:
                return

            # Aplicar filtro
            if self.filter_type != 'none':
                current_img = self.apply_filter(current_img)

            if self.stop_processing:
                return

            # Aplicar segmentación
            if self.segmentation_type != 'none':
                current_img = self.apply_segmentation(current_img)

            if self.stop_processing:
                return

            # Emitir imagen final
            self.emit_image(current_img)

        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Always emit finished signal
            if not self.stop_processing:
                self.finished.emit()

    def emit_image(self, img):
        """Convertir y emitir imagen"""
        if len(img.shape) == 2:
            # Imagen en escala de grises
            h, w = img.shape
            bytes_per_line = w
            q_image = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)
        else:
            # Imagen a color
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Emitimos una copia para asegurar que los datos sean válidos en el hilo principal
        self.image_updated.emit(q_image.copy())

    def stop(self):
        """Detener el procesamiento"""
        self.stop_processing = True
        # Signal the thread to quit gracefully
        self.quit()

    def __del__(self):
        """Destructor - ensure thread is stopped"""
        try:
            if hasattr(self, 'stop_processing'):
                self.stop_processing = True
            # Never wait in destructor - just signal to quit
            if hasattr(self, 'isRunning') and self.isRunning():
                self.quit()
        except (RuntimeError, AttributeError):
            # Object may already be deleted
            pass

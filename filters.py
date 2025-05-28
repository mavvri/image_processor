import numpy as np
import cv2
from scipy import ndimage
from skimage import filters

class ImageFilters:
    """
    Clase que contiene todos los filtros de procesamiento de imágenes.
    """
    
    @staticmethod
    def apply_averaging_filter(img, kernel_size=5):
        """Filtro promediador"""
        kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
        return cv2.filter2D(img, -1, kernel)
    
    @staticmethod
    def apply_weighted_averaging_filter(img, kernel_size=5):
        """Filtro promediador pesado"""
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32) / 16
        return cv2.filter2D(img, -1, kernel)
    
    @staticmethod
    def apply_median_filter(img, kernel_size=5):
        """Filtro mediana"""
        return cv2.medianBlur(img, kernel_size)
    
    @staticmethod
    def apply_mode_filter(img, kernel_size=5):
        """Filtro moda"""
        if len(img.shape) == 3:
            result = np.zeros_like(img)
            for i in range(3):
                result[:,:,i] = ndimage.generic_filter(img[:,:,i], 
                                                     lambda x: np.argmax(np.bincount(x.astype(int))), 
                                                     size=kernel_size)
            return result
        else:
            return ndimage.generic_filter(img, 
                                        lambda x: np.argmax(np.bincount(x.astype(int))), 
                                        size=kernel_size)
    
    @staticmethod
    def apply_bilateral_filter(img, d=15, sigma_color=75, sigma_space=75):
        """Filtro bilateral"""
        return cv2.bilateralFilter(img, d, sigma_color, sigma_space)
    
    @staticmethod
    def apply_max_filter(img, kernel_size=5):
        """Filtro máximo"""
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(img, kernel, iterations=1)
    
    @staticmethod
    def apply_min_filter(img, kernel_size=5):
        """Filtro mínimo"""
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(img, kernel, iterations=1)
    
    @staticmethod
    def apply_gaussian_filter(img, kernel_size=5, sigma=1.0):
        """Filtro Gaussiano"""
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), sigma)
    
    @staticmethod
    def apply_robinson_filter(img):
        """Filtro Máscaras de Robinson"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # 8 máscaras de Robinson
        robinson_masks = [
            np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]),  # 0°
            np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]]),  # 45°
            np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]),  # 90°
            np.array([[0, -1, -2], [1, 0, -1], [2, 1, 0]]),  # 135°
            np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]]),  # 180°
            np.array([[2, 1, 0], [1, 0, -1], [0, -1, -2]]),  # 225°
            np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]),  # 270°
            np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]])   # 315°
        ]
        
        responses = []
        for mask in robinson_masks:
            response = cv2.filter2D(gray, cv2.CV_32F, mask)
            responses.append(np.abs(response))
        
        result = np.maximum.reduce(responses)
        return np.uint8(np.clip(result, 0, 255))
    
    @staticmethod
    def apply_roberts_filter(img):
        """Filtro Operador de Roberts"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Máscaras de Roberts
        roberts_x = np.array([[1, 0], [0, -1]], dtype=np.float32)
        roberts_y = np.array([[0, 1], [-1, 0]], dtype=np.float32)
        
        grad_x = cv2.filter2D(gray, cv2.CV_32F, roberts_x)
        grad_y = cv2.filter2D(gray, cv2.CV_32F, roberts_y)
        
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        return np.uint8(np.clip(magnitude, 0, 255))
    
    @staticmethod
    def apply_prewitt_filter(img):
        """Filtro Operador de Prewitt"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Máscaras de Prewitt
        prewitt_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        prewitt_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
        
        grad_x = cv2.filter2D(gray, cv2.CV_32F, prewitt_x)
        grad_y = cv2.filter2D(gray, cv2.CV_32F, prewitt_y)
        
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        return np.uint8(np.clip(magnitude, 0, 255))
    
    @staticmethod
    def apply_sobel_filter(img):
        """Filtro Operador de Sobel"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        return np.uint8(np.clip(magnitude, 0, 255))
    
    @staticmethod
    def apply_kirsch_filter(img, threshold=30):
        """Filtro Compás de Kirsch"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        kirsch_kernels = [
            np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]]),  # Norte
            np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]]),  # Noreste
            np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]]),  # Este
            np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]]),  # Sureste
            np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]]),  # Sur
            np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]]),  # Suroeste
            np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]]),  # Oeste
            np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]])   # Noroeste
        ]
        
        responses = []
        for kernel in kirsch_kernels:
            response = cv2.filter2D(gray, -1, kernel)
            responses.append(response)
        
        result = np.maximum.reduce(responses)
        return result
    
    @staticmethod
    def apply_canny_filter(img, threshold1=50, threshold2=150):
        """Filtro de Canny"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        return cv2.Canny(gray, threshold1, threshold2)
    
    @staticmethod
    def apply_laplacian_filter(img):
        """Filtro Laplaciano"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        laplacian = cv2.Laplacian(gray, cv2.CV_32F)
        return np.uint8(np.clip(np.abs(laplacian), 0, 255))

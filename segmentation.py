import numpy as np
import cv2
from skimage import filters

class ImageSegmentation:
    """
    Clase que contiene todos los métodos de segmentación de imágenes.
    """
    
    @staticmethod
    def threshold_mean(img):
        """Segmentación mediante Umbral Media"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        mean_value = np.mean(gray)
        _, binary = cv2.threshold(gray, mean_value, 255, cv2.THRESH_BINARY)
        return binary
    
    @staticmethod
    def threshold_otsu(img):
        """Segmentación mediante Método de Otsu"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        threshold_value, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary, threshold_value
    
    @staticmethod
    def multi_threshold_otsu(img, num_classes=3):
        """Segmentación mediante Multiumbralización"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        thresholds = filters.threshold_multiotsu(gray, classes=num_classes)
        regions = np.digitize(gray, bins=thresholds)
        
        # Convertir a imagen de 8 bits
        result = (regions * (255 // (num_classes - 1))).astype(np.uint8)
        return result, thresholds
    
    @staticmethod
    def kapur_entropy_threshold(img):
        """Segmentación mediante Entropia de Kapur"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Calcular histograma
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist.astype(float)
        hist = hist / hist.sum()  # Normalizar
        
        def kapur_entropy(threshold):
            # Probabilidades acumuladas
            w0 = np.sum(hist[:threshold])
            w1 = np.sum(hist[threshold:])
            
            if w0 == 0 or w1 == 0:
                return 0
            
            # Entropías
            p0 = hist[:threshold] / w0
            p1 = hist[threshold:] / w1
            
            # Evitar log(0)
            p0 = p0[p0 > 0]
            p1 = p1[p1 > 0]
            
            h0 = -np.sum(p0 * np.log2(p0)) if len(p0) > 0 else 0
            h1 = -np.sum(p1 * np.log2(p1)) if len(p1) > 0 else 0
            
            return h0 + h1
        
        # Encontrar el umbral óptimo
        best_threshold = 0
        max_entropy = 0
        for t in range(1, 255):
            entropy = kapur_entropy(t)
            if entropy > max_entropy:
                max_entropy = entropy
                best_threshold = t
        
        _, binary = cv2.threshold(gray, best_threshold, 255, cv2.THRESH_BINARY)
        return binary, best_threshold
    
    @staticmethod
    def band_threshold(img, min_val=50, max_val=200):
        """Segmentación mediante umbral banda"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        _, mask_min = cv2.threshold(gray, min_val, 255, cv2.THRESH_BINARY)
        _, mask_max = cv2.threshold(gray, max_val, 255, cv2.THRESH_BINARY_INV)
        
        return cv2.bitwise_and(mask_min, mask_max)
    
    @staticmethod
    def adaptive_threshold(img, max_value=255, adaptive_method=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                          threshold_type=cv2.THRESH_BINARY, block_size=11, C=2):
        """Segmentación mediante umbral adaptativo"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        return cv2.adaptiveThreshold(gray, max_value, adaptive_method, threshold_type, block_size, C)
    
    @staticmethod
    def histogram_minimum_threshold(img):
        """Segmentación mediante Mínimo del histograma"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Calcular histograma
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        
        # Suavizar histograma
        hist_smooth = cv2.GaussianBlur(hist.reshape(-1, 1), (5, 1), 0).flatten()
        
        # Encontrar mínimos locales
        valleys = []
        for i in range(1, len(hist_smooth) - 1):
            if hist_smooth[i] < hist_smooth[i-1] and hist_smooth[i] < hist_smooth[i+1]:
                valleys.append(i)
        
        if not valleys:
            threshold = 128  # Valor por defecto
        else:
            # Tomar el valle más profundo como umbral
            threshold = min(valleys, key=lambda x: hist_smooth[x])
        
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        return binary, threshold
    
    @staticmethod
    def connected_components_analysis(binary_image):
        """Análisis de componentes conectados con ambas vecindades"""
        # Vecindad-4
        num_labels_4, labels_4 = cv2.connectedComponents(binary_image, connectivity=4)
        num_objects_4 = num_labels_4 - 1
        
        # Vecindad-8
        num_labels_8, labels_8 = cv2.connectedComponents(binary_image, connectivity=8)
        num_objects_8 = num_labels_8 - 1
        
        print(f"Número de objetos detectados con vecindad-4: {num_objects_4}")
        print(f"Número de objetos detectados con vecindad-8: {num_objects_8}")
        
        return {
            'labels_4': labels_4,
            'labels_8': labels_8,
            'num_objects_4': num_objects_4,
            'num_objects_8': num_objects_8
        }
    
    @staticmethod
    def draw_contours_and_labels(binary_image):
        """Dibujar contornos y numerar los objetos"""
        # Convertir imagen binaria a imagen en color
        image_color = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Dibujar los contornos y numerar los objetos
        for i, contour in enumerate(contours):
            # Dibujar contorno (color verde)
            cv2.drawContours(image_color, [contour], -1, (0, 255, 0), 2)
            
            # Encontrar el centro del objeto y colocar el número
            x, y, w, h = cv2.boundingRect(contour)
            cv2.putText(image_color, f'{i + 1}', (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return image_color, len(contours)
    
    @staticmethod
    def arithmetic_operations(img1, img2, operation='add'):
        """Operadores aritméticos entre dos imágenes"""
        if operation == 'add':
            return cv2.add(img1, img2)
        elif operation == 'subtract':
            return cv2.subtract(img1, img2)
        elif operation == 'multiply':
            return cv2.multiply(img1, img2)
        elif operation == 'divide':
            return cv2.divide(img1, img2)
        else:
            return img1
    
    @staticmethod
    def logical_operations(img1, img2, operation='and'):
        """Operadores lógicos entre dos imágenes"""
        if operation == 'and':
            return cv2.bitwise_and(img1, img2)
        elif operation == 'or':
            return cv2.bitwise_or(img1, img2)
        elif operation == 'xor':
            return cv2.bitwise_xor(img1, img2)
        elif operation == 'not':
            return cv2.bitwise_not(img1)
        else:
            return img1

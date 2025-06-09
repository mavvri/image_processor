import cv2
import numpy as np

def visualize_labels(labels_image):
    """Helper function to visualize a labels image from connectedComponents."""
    if np.max(labels_image) == 0:
        return np.zeros_like(labels_image)
    
    # Normalize the labels image to be in the range 0-255
    label_hue = np.uint8(179 * labels_image / np.max(labels_image))
    blank_ch = 255 * np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
    labeled_img[label_hue == 0] = 0  # Set background to black
    return labeled_img

def apply_morphological_opening(binary_image, kernel_size=3, iterations=1):
    """Apply morphological opening (erosion followed by dilation)."""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    eroded = cv2.erode(binary_image, kernel, iterations=iterations)
    opened = cv2.dilate(eroded, kernel, iterations=iterations)
    return opened

def apply_morphological_closing(binary_image, kernel_size=3, iterations=1):
    """Apply morphological closing (dilation followed by erosion)."""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated = cv2.dilate(binary_image, kernel, iterations=iterations)
    closed = cv2.erode(dilated, kernel, iterations=iterations)
    return closed

def draw_component_stats(image, stats, centroids, filtered_indices, min_area, max_area):
    """Draw component statistics and filtering visualization."""
    result_image = image.copy()
    
    for i, (stats_row, centroid) in enumerate(zip(stats[1:], centroids[1:]), 1):
        x, y, w, h, area = stats_row
        cx, cy = int(centroid[0]), int(centroid[1])
        
        # Color coding: green for valid, red for invalid
        if i in filtered_indices:
            color = (0, 255, 0)  # Green for valid components
            thickness = 3
        else:
            color = (0, 0, 255)  # Red for filtered out components
            thickness = 1
            
        # Draw bounding rectangle
        cv2.rectangle(result_image, (x, y), (x + w, y + h), color, thickness)
        
        # Draw centroid
        cv2.circle(result_image, (cx, cy), 3, color, -1)
        
        # Add area text
        area_text = f"A:{area}"
        cv2.putText(result_image, area_text, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Add aspect ratio text
        aspect_ratio = w / h if h > 0 else 0
        ar_text = f"AR:{aspect_ratio:.2f}"
        cv2.putText(result_image, ar_text, (x, y + h + 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    return result_image

def process_image_pipeline(image_opencv, custom_params=None):
    """
    Process an OpenCV image to detect and count cars, returning intermediate steps.
    
    Args:
        image_opencv: Input image as OpenCV numpy array (BGR format)
        custom_params: Optional dictionary with custom processing parameters
        
    Returns:
        tuple: (pipeline_images, car_count, step_descriptions)
            - pipeline_images: A list of OpenCV images from each processing stage
            - car_count: Number of detected cars
            - step_descriptions: List of descriptions for each step
    """
    if image_opencv is None:
        raise ValueError("Input image is None")

    # Parámetros optimizados para mejor detección de coches
    default_params = {
        'block_size': 25,  # Bloque más grande para mejor adaptación local
        'c_value': 2,      # C muy bajo para ser menos agresivo
        'open_kernel': 2,  # Kernel pequeño para preservar detalles
        'open_iterations': 1,  # Solo una iteración para no fragmentar
        'close_kernel_w': 15, # Cierre horizontal más agresivo para unir partes
        'close_kernel_h': 6,  # Cierre vertical moderado
        'min_area': 800,   # Área mínima más baja para partes de coches
        'max_area': 60000, # Área máxima más alta
        'min_aspect': 0.2, # Aspecto muy permisivo
        'max_aspect': 5.0, # Aspecto muy permisivo
        'min_width': 20,   # Ancho mínimo más bajo
        'max_width': 350,  # Ancho máximo más alto
        'extent_threshold': 0.2  # Umbral de extensión muy permisivo
    }
    
    # Use custom parameters if provided, with error handling
    if custom_params:
        try:
            params = {**default_params, **custom_params}
            # Validate parameters
            if params['block_size'] < 3:
                params['block_size'] = 3
            if params['block_size'] > 51:
                params['block_size'] = 51
            if params['min_area'] >= params['max_area']:
                params['min_area'] = params['max_area'] // 2
        except Exception as e:
            print(f"Warning: Error in custom parameters, using defaults: {e}")
            params = default_params
    else:
        params = default_params

    try:
        pipeline_images = []
        step_descriptions = []

        # 0. Original Image
        original_for_display = image_opencv.copy()
        pipeline_images.append(original_for_display)
        
        mode_text = "MANUAL" if custom_params else "AUTOMÁTICO"
        step_descriptions.append(f"Imagen original cargada para análisis - Modo: {mode_text}")
        
        # 1. Convert to grayscale
        gray_image = cv2.cvtColor(image_opencv, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
        pipeline_images.append(gray_bgr)
        step_descriptions.append("Conversión a escala de grises para simplificar el procesamiento")
        
        # 2. Filtrado más suave para preservar detalles de coches
        # Filtro bilateral más suave
        bilateral_filtered = cv2.bilateralFilter(gray_image, 9, 50, 50)
        
        # Gaussian más suave para no perder detalles
        gaussian_filtered = cv2.GaussianBlur(bilateral_filtered, (5, 5), 1.0)
        
        # Eliminar filtro mediano que puede fragmentar objetos
        filtered_bgr = cv2.cvtColor(gaussian_filtered, cv2.COLOR_GRAY2BGR)
        pipeline_images.append(filtered_bgr)
        step_descriptions.append("Filtrado suave: bilateral + gaussiano preservando detalles de coches")
        
        # 3. Umbralización más permisiva
        block_size = max(3, min(51, params['block_size']))
        if block_size % 2 == 0:
            block_size += 1
            
        # Usar umbralización menos agresiva
        binary_image = cv2.adaptiveThreshold(
            gaussian_filtered,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,  # Cambiar de vuelta a MEAN_C
            cv2.THRESH_BINARY,
            block_size,
            max(1, min(10, params['c_value']))  # C más bajo
        )
        
        # 4. Corrección de polaridad
        white_pixels = np.sum(binary_image == 255)
        total_pixels = binary_image.shape[0] * binary_image.shape[1]
        white_ratio = white_pixels / total_pixels if total_pixels > 0 else 0
        
        if white_ratio > 0.5:
            binary_corrected = cv2.bitwise_not(binary_image)
            polarity_desc = f"Umbralización adaptativa suave con inversión - Bloque:{block_size}, C:{params['c_value']} (ratio: {white_ratio:.2f})"
        else:
            binary_corrected = binary_image
            polarity_desc = f"Umbralización adaptativa suave sin inversión - Bloque:{block_size}, C:{params['c_value']} (ratio: {white_ratio:.2f})"
        
        binary_bgr = cv2.cvtColor(binary_corrected, cv2.COLOR_GRAY2BGR)
        pipeline_images.append(binary_bgr)
        step_descriptions.append(polarity_desc)
        
        # 5. Apertura muy suave para no fragmentar coches
        kernel_size = max(1, min(5, params['open_kernel']))  # Limitar tamaño máximo
        iterations = max(1, min(2, params['open_iterations']))  # Máximo 2 iteraciones
        
        # Usar kernel elíptico más suave
        kernel_opening = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        opened_image = cv2.morphologyEx(binary_corrected, cv2.MORPH_OPEN, kernel_opening, iterations=iterations)
        
        opened_bgr = cv2.cvtColor(opened_image, cv2.COLOR_GRAY2BGR)
        pipeline_images.append(opened_bgr)
        step_descriptions.append(f"Apertura morfológica suave - Kernel elíptico:{kernel_size}x{kernel_size}, Iter:{iterations}")
        
        # 6. Cierre más agresivo para unir partes de coches
        close_w = max(3, min(25, params['close_kernel_w']))
        close_h = max(2, min(12, params['close_kernel_h']))
        
        # Cierre horizontal más agresivo para unir partes de coches
        kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (close_w, close_h))
        closed_horizontal = cv2.morphologyEx(opened_image, cv2.MORPH_CLOSE, kernel_horizontal, iterations=2)
        
        # Cierre vertical adicional
        kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 8))
        cleaned_image = cv2.morphologyEx(closed_horizontal, cv2.MORPH_CLOSE, kernel_vertical, iterations=1)
        
        # Cierre diagonal para unir partes en ángulo
        kernel_diagonal = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        cleaned_image = cv2.morphologyEx(cleaned_image, cv2.MORPH_CLOSE, kernel_diagonal, iterations=1)
        
        cleaned_bgr = cv2.cvtColor(cleaned_image, cv2.COLOR_GRAY2BGR)
        pipeline_images.append(cleaned_bgr)
        step_descriptions.append(f"Cierre morfológico agresivo - Horizontal:{close_w}x{close_h}, Vertical:4x8, Diagonal:7x7")
        
        # 7. Connected components labeling
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cleaned_image, connectivity=8)
        
        labels_display = visualize_labels(labels)
        pipeline_images.append(labels_display)
        step_descriptions.append(f"Etiquetado de componentes conexas: {num_labels-1} componentes encontrados")
        
        # 8. Filtrado geométrico más permisivo para coches
        min_area = max(100, params['min_area'])
        max_area = max(min_area + 1000, params['max_area'])
        min_aspect_ratio = max(0.1, min(10.0, params['min_aspect']))
        max_aspect_ratio = max(min_aspect_ratio + 0.1, min(10.0, params['max_aspect']))
        min_width = max(10, params['min_width'])
        max_width = max(min_width + 10, params['max_width'])
        min_height = 15
        max_height = 250  # Más permisivo en altura
        extent_threshold = max(0.1, min(1.0, params['extent_threshold']))
        
        valid_components = []
        car_count = 0
        
        for i in range(1, num_labels):
            x, y, w, h, area = stats[i]
            aspect_ratio = w / h if h > 0 else 0
            extent = area / (w * h) if (w * h) > 0 else 0
            
            # Calculate additional geometric features
            height_to_width_ratio = h / w if w > 0 else 0
            perimeter = 2 * (w + h)
            compactness = (4 * np.pi * area) / (perimeter * perimeter) if perimeter > 0 else 0
            
            # Filtrado más permisivo para coches
            is_valid_car = True
            rejection_reason = ""
            
            # Filtros básicos de tamaño más permisivos
            if area < min_area:
                is_valid_car = False
                rejection_reason = "PEQUEÑO"
            elif area > max_area:
                is_valid_car = False
                rejection_reason = "GRANDE"
            
            # Filtros dimensionales más permisivos
            elif w < min_width or w > max_width:
                is_valid_car = False
                rejection_reason = "ANCHO_INVÁLIDO"
            elif h < min_height or h > max_height:
                is_valid_car = False
                rejection_reason = "ALTO_INVÁLIDO"
                
            # Filtros de forma más permisivos
            elif aspect_ratio < min_aspect_ratio:
                is_valid_car = False
                rejection_reason = "MUY_ALTO"
            elif aspect_ratio > max_aspect_ratio:
                is_valid_car = False
                rejection_reason = "MUY_ANCHO"
                
            # Detección de árboles más específica
            elif height_to_width_ratio > 4.0:  # Más restrictivo para árboles
                is_valid_car = False
                rejection_reason = "ÁRBOL"
                
            # Detección de copas más específica
            elif (0.7 <= aspect_ratio <= 1.4 and 
                  area > 25000 and  # Área mínima más alta para copas
                  compactness > 0.7):  # Compacidad más alta para copas
                is_valid_car = False
                rejection_reason = "COPA"
                
            # Filtros de calidad más permisivos
            elif extent < extent_threshold:
                is_valid_car = False
                rejection_reason = "IRREGULAR"
            elif compactness < 0.05:  # Muy permisivo para compacidad
                is_valid_car = False
                rejection_reason = "DISPERSO"
                
            # Objetos lineales muy largos
            elif aspect_ratio > 10.0:  # Más permisivo
                is_valid_car = False
                rejection_reason = "LINEAL"
            
            if is_valid_car:
                valid_components.append(i)
                car_count += 1
        
        # Enhanced visualization
        filtering_vis = draw_enhanced_component_stats(
            image_opencv, stats, centroids, valid_components, min_area, max_area
        )
        pipeline_images.append(filtering_vis)
        
        param_summary = f"Área:[{min_area}-{max_area}], Aspecto:[{min_aspect_ratio:.1f}-{max_aspect_ratio:.1f}], Ancho:[{min_width}-{max_width}]"
        step_descriptions.append(f"Filtrado geométrico permisivo: {len(valid_components)} coches de {num_labels-1} componentes - {param_summary}")
        
        # 9. Final result with enhanced visualization
        result_image = image_opencv.copy()
        for idx, component_label in enumerate(valid_components, 1):
            x, y, w, h, area = stats[component_label]
            
            # Draw thick green rectangle for detected cars
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 4)
            
            # Car label with background
            label_text = f'Coche {idx}'
            text_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            
            # Draw label background
            cv2.rectangle(result_image, (x, y - text_size[1] - 12), 
                         (x + text_size[0] + 8, y - 2), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(result_image, label_text, (x + 4, y - 6), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            
            # Additional info
            info_text = f'{w}x{h} A:{area}'
            cv2.putText(result_image, info_text, (x, y + h + 18), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        pipeline_images.append(result_image)
        final_mode = "modo manual" if custom_params else "modo automático"
        step_descriptions.append(f"Resultado final: {car_count} coches detectados en {final_mode}")
        
        return pipeline_images, car_count, step_descriptions
        
    except Exception as e:
        print(f"Error in image processing pipeline: {e}")
        return [image_opencv], 0, [f"Error en procesamiento: {str(e)}"]

def convert_opencv_to_qimage(opencv_image):
    """
    Helper function to convert OpenCV image to QImage format.
    """
    from PyQt5.QtGui import QImage
    
    if len(opencv_image.shape) == 3:  # Color image
        height, width, channel = opencv_image.shape
        bytes_per_line = 3 * width
        # OpenCV uses BGR, QImage expects RGB
        rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    elif len(opencv_image.shape) == 2:  # Grayscale image
        height, width = opencv_image.shape
        bytes_per_line = width
        q_image = QImage(opencv_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
    else:
        raise ValueError(f"Unsupported image format: {opencv_image.shape}")
    
    return q_image.copy()  # Important: create a copy for thread safety

def draw_enhanced_component_stats(image, stats, centroids, filtered_indices, min_area, max_area):
    """Draw enhanced component statistics showing why objects were filtered."""
    result_image = image.copy()
    
    for i, (stats_row, centroid) in enumerate(zip(stats[1:], centroids[1:]), 1):
        x, y, w, h, area = stats_row
        cx, cy = int(centroid[0]), int(centroid[1])
        aspect_ratio = w / h if h > 0 else 0
        height_to_width_ratio = h / w if w > 0 else 0
        extent = area / (w * h) if (w * h) > 0 else 0
        perimeter = 2 * (w + h)
        compactness = (4 * np.pi * area) / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Calculate solidity for better classification
        labels = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        labels[y:y+h, x:x+w] = 1  # Simplified for visualization
        solidity = 0.7  # Default value for visualization
        
        # Enhanced color coding and labeling
        if i in filtered_indices:
            color = (0, 255, 0)  # Green for valid cars
            thickness = 3
            label = "COCHE"
        else:
            # More accurate rejection categorization
            if area < min_area:
                color = (100, 100, 255)  # Light blue for too small
                label = "PEQUEÑO"
            elif area > max_area:
                color = (0, 0, 200)  # Dark blue for too large
                label = "GRANDE"
            elif height_to_width_ratio > 2.5:
                color = (255, 100, 0)  # Orange for tree-like
                label = "ÁRBOL"
            elif solidity < 0.6 and area > 3000:
                color = (255, 150, 0)  # Light orange for fragmented trees
                label = "ÁRBOL_FRAG"
            elif (0.8 <= aspect_ratio <= 1.25 and area > 15000 and compactness > 0.5):
                color = (255, 200, 0)  # Yellow for crowns
                label = "COPA"
            elif aspect_ratio > 3.0:
                color = (255, 0, 255)  # Magenta for very elongated
                label = "ELONGADO"
            elif extent < 0.35:
                color = (128, 128, 128)  # Gray for irregular
                label = "IRREGULAR"
            elif compactness < 0.1:
                color = (64, 64, 64)  # Dark gray for dispersed
                label = "DISPERSO"
            else:
                color = (200, 200, 200)  # Light gray for other
                label = "OTRO"
            thickness = 1
            
        # Draw bounding rectangle
        cv2.rectangle(result_image, (x, y), (x + w, y + h), color, thickness)
        
        # Draw centroid
        cv2.circle(result_image, (cx, cy), 2, color, -1)
        
        # Add classification label
        cv2.putText(result_image, label, (x, y - 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        
        # Add metrics
        metrics_text = f"A:{area} AR:{aspect_ratio:.1f}"
        cv2.putText(result_image, metrics_text, (x, y - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)
        
        # Add size
        size_text = f"{w}x{h}"
        cv2.putText(result_image, size_text, (x, y - 8), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)
        
        # Add additional debug info for rejected objects
        if i not in filtered_indices:
            debug_text = f"E:{extent:.2f} C:{compactness:.2f}"
            cv2.putText(result_image, debug_text, (x, y + h + 12), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
    
    return result_image

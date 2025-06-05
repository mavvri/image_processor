from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QPushButton,
                             QFileDialog, QHBoxLayout, QSlider, QSizePolicy,
                             QFrame, QMessageBox, QCheckBox, QGroupBox,
                             QComboBox, QSpinBox, QTabWidget, QTextEdit,
                             QScrollArea, QGridLayout, QSplitter, QStackedWidget,
                             QButtonGroup)
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize
from image_processor import ImageProcessor
from segmentation import ImageSegmentation
from presets import IntelligentPresets
import numpy as np
import cv2
import os

try:
    from PyQt6.QtWidgets import QGraphicsOpacityEffect
    
    class AnimatedWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._opacity = 1.0
            
        def get_opacity(self):
            return self._opacity
        
        def set_opacity(self, value):
            self._opacity = value
            self.update()
        
        opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    class ThemeManager:
        @staticmethod
        def get_main_theme():
            try:
                with open('ui/styles/main_theme.css', 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return """
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    font-family: "Segoe UI", Arial, sans-serif;
                    font-size: 12px;
                }
                
                #Sidebar {
                    background: #1e1e1e;
                    border-right: 1px solid #3e3e3e;
                }
                
                #ToolPanel {
                    background: #2b2b2b;
                    border: 1px solid #3e3e3e;
                    border-radius: 4px;
                    margin: 2px;
                }
                
                #PanelTitle {
                    background: #3e3e3e;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 8px;
                    border-bottom: 1px solid #5e5e5e;
                }
                
                QPushButton {
                    background: #404040;
                    border: 1px solid #5e5e5e;
                    border-radius: 3px;
                    color: white;
                    padding: 6px 12px;
                    font-size: 11px;
                }
                
                QPushButton:hover {
                    background: #505050;
                }
                
                QPushButton:pressed {
                    background: #303030;
                }
                
                #ProcessButton {
                    background: #0078d4;
                    border: none;
                    color: white;
                    font-weight: bold;
                    min-height: 32px;
                }
                
                #ProcessButton:hover {
                    background: #106ebe;
                }
                
                QComboBox {
                    background: #404040;
                    border: 1px solid #5e5e5e;
                    border-radius: 3px;
                    padding: 4px 8px;
                    color: white;
                    min-height: 20px;
                }
                
                QSpinBox {
                    background: #404040;
                    border: 1px solid #5e5e5e;
                    border-radius: 3px;
                    color: white;
                    padding: 4px;
                }
                
                QSlider::groove:horizontal {
                    background: #5e5e5e;
                    height: 4px;
                    border-radius: 2px;
                }
                
                QSlider::handle:horizontal {
                    background: #0078d4;
                    border: none;
                    width: 14px;
                    height: 14px;
                    margin: -5px 0;
                    border-radius: 7px;
                }
                
                #MainCanvas {
                    background: #3e3e3e;
                    border: 1px solid #5e5e5e;
                }
                
                #ImageDisplay {
                    background: #2b2b2b;
                    border: 2px dashed #5e5e5e;
                    color: #a0a0a0;
                }
                
                QTextEdit {
                    background: #1e1e1e;
                    border: 1px solid #3e3e3e;
                    color: #ffffff;
                    font-family: "Consolas", monospace;
                    font-size: 10px;
                }
                """
except ImportError:
    pass


class CollapsiblePanel(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("ToolPanel")
        self.setup_ui(title)
        self.is_collapsed = False
        
    def setup_ui(self, title):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header con título clickeable
        self.header = QPushButton(title)
        self.header.setObjectName("PanelTitle")
        self.header.clicked.connect(self.toggle_collapse)
        self.header.setCheckable(False)
        
        # Contenido
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(8, 4, 8, 8)
        self.content_layout.setSpacing(4)
        
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.content_widget)
        
    def add_widget(self, widget):
        self.content_layout.addWidget(widget)
        
    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)


class FilterInfoWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Información de Filtros")
        self.setGeometry(200, 150, 900, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Título
        title = QLabel("Guía de Procesamiento de Imágenes")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 16px;")
        layout.addWidget(title)

        # Contenido en tabs
        tab_widget = QTabWidget()
        
        # Tab de filtros
        filters_tab = QWidget()
        filters_layout = QVBoxLayout(filters_tab)
        
        filter_text = QTextEdit()
        filter_text.setHtml(self.get_filters_info())
        filter_text.setReadOnly(True)
        filters_layout.addWidget(filter_text)
        
        tab_widget.addTab(filters_tab, "Filtros")
        
        # Tab de segmentación
        seg_tab = QWidget()
        seg_layout = QVBoxLayout(seg_tab)
        
        seg_text = QTextEdit()
        seg_text.setHtml(self.get_segmentation_info())
        seg_text.setReadOnly(True)
        seg_layout.addWidget(seg_text)
        
        tab_widget.addTab(seg_tab, "Segmentación")
        
        # Tab de operaciones
        ops_tab = QWidget()
        ops_layout = QVBoxLayout(ops_tab)
        
        ops_text = QTextEdit()
        ops_text.setHtml(self.get_operations_info())
        ops_text.setReadOnly(True)
        ops_layout.addWidget(ops_text)
        
        tab_widget.addTab(ops_tab, "Operaciones")
        
        layout.addWidget(tab_widget)

        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        close_btn.setFixedWidth(80)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)

    def get_filters_info(self):
        return """
        <h3>Filtros de Suavizado</h3>
        <p><b>Promedio:</b> Reduce ruido mediante promedio local</p>
        <p><b>Mediana:</b> Elimina ruido impulsivo preservando bordes</p>
        <p><b>Gaussiano:</b> Suavizado natural progresivo</p>
        <p><b>Bilateral:</b> Preserva bordes mientras suaviza</p>
        
        <h3>Detección de Bordes</h3>
        <p><b>Sobel:</b> Detecta gradientes horizontales y verticales</p>
        <p><b>Canny:</b> Detector óptimo de bordes</p>
        <p><b>Laplaciano:</b> Detecta cambios de intensidad</p>
        
        <h3>Morfológicos</h3>
        <p><b>Máximo:</b> Dilatación morfológica</p>
        <p><b>Mínimo:</b> Erosión morfológica</p>
        """

    def get_segmentation_info(self):
        return """
        <h3>Métodos de Umbralización</h3>
        <p><b>Otsu:</b> Encuentra automáticamente el umbral óptimo</p>
        <p><b>Media:</b> Usa la intensidad media como umbral</p>
        <p><b>Adaptativo:</b> Umbral variable según condiciones locales</p>
        <p><b>Banda:</b> Conserva píxeles en rango específico</p>
        
        <h3>Métodos Avanzados</h3>
        <p><b>Multi-Otsu:</b> Múltiples clases automáticamente</p>
        <p><b>Kapur:</b> Basado en entropía máxima</p>
        """

    def get_operations_info(self):
        return """
        <h3>Operaciones Aritméticas</h3>
        <p><b>Suma:</b> I3 = I1 + I2</p>
        <p><b>Resta:</b> I3 = |I1 - I2|</p>
        <p><b>Multiplicación:</b> I3 = I1 × I2</p>
        <p><b>División:</b> I3 = I1 / I2</p>
        
        <h3>Operaciones Lógicas</h3>
        <p><b>AND:</b> I3 = I1 ∧ I2</p>
        <p><b>OR:</b> I3 = I1 ∨ I2</p>
        <p><b>XOR:</b> I3 = I1 ⊕ I2</p>
        <p><b>NOT:</b> I3 = ¬I1</p>
        
        <h3>Operaciones Especiales</h3>
        <p><b>Promedio:</b> I3 = (I1 + I2) / 2</p>
        <p><b>Diferencia:</b> Resalta diferencias entre imágenes</p>
        """


class ImageProcessingApp(AnimatedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing Studio")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1400, 800)
        
        # State variables
        self.image_tabs = {}  # Dictionary to store tab data
        self.current_tab_id = None
        self.tab_counter = 0
        self.image_processor = None
        self.temp_processors = []
        
        # Real-time processing optimization
        self.processing_timer = QTimer(self)
        self.processing_timer.setSingleShot(True)
        self.processing_timer.setInterval(300)
        self.processing_timer.timeout.connect(self.process_image_realtime)
        
        self.is_processing = False
        self.pending_update = False
        
        self.current_operation = "Ready"
        self.dynamic_params = {}
        
        # Load presets
        try:
            self.presets = IntelligentPresets.get_presets()
        except:
            self.presets = {}
        
        self.info_window = None
        
        self.setup_ui()
        self.apply_theme()
        self.update_ui_state()

    def update_ui_state(self):
        """Update UI state based on loaded images"""
        has_images = len(self.image_tabs) > 0
        has_multiple_images = len(self.image_tabs) > 1
        
        # Show/hide second image controls
        self.load_second_btn.setVisible(True)
        
        # Show/hide operations panel
        self.operations_widget.setVisible(has_multiple_images)
        
        # Enable/disable process button
        self.process_button.setEnabled(has_images)

    def closeEvent(self, event):
        """Handle application close event to clean up threads"""
        self.cleanup_threads()
        event.accept()

    def cleanup_threads(self):
        """Clean up all running threads before closing"""
        # Stop main processor
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                # Don't wait - just quit and let it clean up asynchronously
                self.image_processor.quit()
            self.image_processor = None
        
        # Stop all temporary processors
        for processor in self.temp_processors[:]:
            if processor:
                if processor.isRunning():
                    processor.stop()
                    processor.quit()
                # Remove from list immediately
                self.temp_processors.remove(processor)

    def apply_theme(self):
        try:
            with open('ui/styles/main_theme.css', 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except:
            # Fallback to basic dark theme
            self.setStyleSheet(ThemeManager.get_main_theme())

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel de herramientas (izquierda) - estilo Photoshop
        self.create_tools_panel(main_layout)
        
        # Área principal (centro)
        self.create_main_workspace(main_layout)
        
        # Panel de propiedades (derecha)
        self.create_properties_panel(main_layout)

    def create_tools_panel(self, parent_layout):
        """Panel de herramientas estilo Photoshop"""
        tools_panel = QFrame()
        tools_panel.setObjectName("Sidebar")
        tools_panel.setFixedWidth(280)
        
        layout = QVBoxLayout(tools_panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Scroll para herramientas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(4)
        
        # Panel de pipeline de procesamiento
        pipeline_panel = self.create_pipeline_panel()
        scroll_layout.addWidget(pipeline_panel)
        
        # Panel de archivos
        files_panel = self.create_files_panel()
        scroll_layout.addWidget(files_panel)
        
        # Panel de visualización
        visualization_panel = self.create_visualization_panel()
        scroll_layout.addWidget(visualization_panel)
        
        # Panel de detección de objetos
        object_detection_panel = self.create_object_detection_panel()
        scroll_layout.addWidget(object_detection_panel)
        
        # Panel de parámetros dinámicos
        dynamic_panel = self.create_dynamic_params_panel()
        scroll_layout.addWidget(dynamic_panel)
        
        # Panel de filtros
        filters_panel = self.create_filters_panel()
        scroll_layout.addWidget(filters_panel)
        
        # Panel de operaciones
        operations_panel = self.create_operations_panel()
        scroll_layout.addWidget(operations_panel)
        
        # Panel de segmentación
        segmentation_panel = self.create_segmentation_panel()
        scroll_layout.addWidget(segmentation_panel)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Botones de acción
        actions_layout = self.create_action_buttons()
        layout.addLayout(actions_layout)
        
        parent_layout.addWidget(tools_panel)

    def create_pipeline_panel(self):
        """Panel que muestra el pipeline de procesamiento paso a paso"""
        panel = CollapsiblePanel("🔄 Pipeline de Procesamiento")
        
        # Widget scrollable para el pipeline
        self.pipeline_scroll = QScrollArea()
        self.pipeline_scroll.setWidgetResizable(True)
        self.pipeline_scroll.setFixedHeight(150)
        self.pipeline_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.pipeline_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.pipeline_widget = QWidget()
        self.pipeline_layout = QVBoxLayout(self.pipeline_widget)
        self.pipeline_layout.setContentsMargins(8, 8, 8, 8)
        self.pipeline_layout.setSpacing(4)
        
        # Mensaje inicial
        self.pipeline_empty_label = QLabel("🔧 Selecciona filtros para ver el pipeline")
        self.pipeline_empty_label.setStyleSheet("color: #888888; font-style: italic;")
        self.pipeline_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pipeline_layout.addWidget(self.pipeline_empty_label)
        
        self.pipeline_scroll.setWidget(self.pipeline_widget)
        panel.add_widget(self.pipeline_scroll)
        
        return panel

    def update_pipeline_visualization(self):
        """Actualizar la visualización del pipeline de procesamiento"""
        # Limpiar pipeline anterior
        for i in reversed(range(self.pipeline_layout.count())):
            child = self.pipeline_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        # Obtener operaciones activas
        pipeline_steps = []
        
        # 1. Imagen original
        pipeline_steps.append(("📁", "Imagen Original", "#4CAF50"))
        
        # 2. Ruido (si está activado)
        if hasattr(self, 'noise_checkbox') and self.noise_checkbox.isChecked():
            noise_level = self.noise_slider.value()
            pipeline_steps.append(("📊", f"Ruido Gaussiano (σ={noise_level})", "#FF9800"))
        
        # 3. Filtros
        smoothing_filter = self.get_selected_filter()
        edge_filter = self.get_selected_edge_detection()
        morph_filter = self.get_selected_morphological()
        
        if smoothing_filter != "none":
            filter_name = self.smoothing_combo.currentText()
            params = self.get_filter_parameters()
            param_text = ""
            if 'kernel_size' in params:
                param_text = f" (kernel={params['kernel_size']})"
            elif 'sigma' in params:
                param_text = f" (σ={params['sigma']:.1f})"
            pipeline_steps.append(("🔧", f"Suavizado: {filter_name}{param_text}", "#2196F3"))
        
        if edge_filter != "none":
            filter_name = self.edge_combo.currentText()
            params = self.get_filter_parameters()
            param_text = ""
            if 'low_threshold' in params and 'high_threshold' in params:
                param_text = f" ({params['low_threshold']}-{params['high_threshold']})"
            pipeline_steps.append(("⚡", f"Bordes: {filter_name}{param_text}", "#E91E63"))
        
        if morph_filter != "none":
            filter_name = self.morphological_combo.currentText()
            pipeline_steps.append(("🔹", f"Morfológico: {filter_name}", "#9C27B0"))
        
        # 4. Segmentación
        seg_filter = self.get_selected_segmentation()
        if seg_filter != "none":
            seg_name = self.segmentation_combo.currentText()
            seg_params = self.get_segmentation_parameters()
            param_text = ""
            if 'num_thresholds' in seg_params:
                param_text = f" ({seg_params['num_thresholds']} clases)"
            pipeline_steps.append(("✂️", f"Segmentación: {seg_name}{param_text}", "#FF5722"))
        
        # Si no hay pasos, mostrar mensaje vacío
        if len(pipeline_steps) <= 1:
            self.pipeline_empty_label = QLabel("🔧 Selecciona filtros para ver el pipeline")
            self.pipeline_empty_label.setStyleSheet("color: #888888; font-style: italic;")
            self.pipeline_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pipeline_layout.addWidget(self.pipeline_empty_label)
        else:
            # Crear visualización de pasos
            for i, (icon, text, color) in enumerate(pipeline_steps):
                step_widget = QFrame()
                # Remove unsupported CSS properties
                step_widget.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color}20;
                        border-left: 3px solid {color};
                        border-radius: 3px;
                        margin: 2px;
                        padding: 4px;
                    }}
                """)
                
                step_layout = QHBoxLayout(step_widget)
                step_layout.setContentsMargins(8, 4, 8, 4)
                
                icon_label = QLabel(icon)
                icon_label.setFixedWidth(20)
                
                text_label = QLabel(text)
                text_label.setWordWrap(True)
                text_label.setStyleSheet("font-size: 10px;")
                
                step_layout.addWidget(icon_label)
                step_layout.addWidget(text_label)
                
                self.pipeline_layout.addWidget(step_widget)
                
                # Añadir flecha si no es el último paso
                if i < len(pipeline_steps) - 1:
                    arrow_label = QLabel("↓")
                    arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    arrow_label.setStyleSheet("color: #666666; font-weight: bold;")
                    self.pipeline_layout.addWidget(arrow_label)

    def create_files_panel(self):
        panel = CollapsiblePanel("📁 Archivos")
        
        # Imagen principal
        panel.add_widget(QLabel("Imagen Principal:"))
        self.load_btn = QPushButton("Cargar Imagen")
        self.load_btn.clicked.connect(self.load_image)
        panel.add_widget(self.load_btn)
        
        # Segunda imagen para operaciones
        panel.add_widget(QLabel("Segunda Imagen:"))
        self.load_second_btn = QPushButton("Cargar Segunda")
        self.load_second_btn.clicked.connect(self.load_second_image)
        panel.add_widget(self.load_second_btn)
        
        # Información
        info_btn = QPushButton("📖 Ayuda")
        info_btn.clicked.connect(self.show_filter_info)
        panel.add_widget(info_btn)
        
        return panel

    def create_dynamic_params_panel(self):
        """Panel para parámetros dinámicos según el filtro/segmentación seleccionado"""
        panel = CollapsiblePanel("🎛️ Parámetros Dinámicos")
        
        self.dynamic_params_widget = QWidget()
        self.dynamic_params_layout = QVBoxLayout(self.dynamic_params_widget)
        self.dynamic_params_layout.setContentsMargins(0, 0, 0, 0)
        
        # Botón para calcular parámetros automáticos
        self.auto_params_btn = QPushButton("🤖 Calcular Automático")
        self.auto_params_btn.clicked.connect(self.calculate_automatic_parameters)
        self.dynamic_params_layout.addWidget(self.auto_params_btn)
        
        panel.add_widget(self.dynamic_params_widget)
        
        return panel

    def create_filters_panel(self):
        panel = CollapsiblePanel("🔧 Filtros")
        
        # Suavizado
        panel.add_widget(QLabel("Suavizado:"))
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.addItems([
            "Ninguno", "Promedio", "Promedio Pesado", "Mediana", 
            "Moda", "Bilateral", "Gaussiano"
        ])
        self.smoothing_combo.currentTextChanged.connect(self.on_filter_changed)
        panel.add_widget(self.smoothing_combo)
        
        # Morfológicos
        panel.add_widget(QLabel("Morfológicos:"))
        self.morphological_combo = QComboBox()
        self.morphological_combo.addItems(["Ninguno", "Máximo", "Mínimo"])
        self.morphological_combo.currentTextChanged.connect(self.on_filter_changed)
        panel.add_widget(self.morphological_combo)
        
        # Detección de bordes
        panel.add_widget(QLabel("Detección de Bordes:"))
        self.edge_combo = QComboBox()
        self.edge_combo.addItems([
            "Ninguno", "Roberts", "Prewitt", "Sobel", 
            "Robinson", "Kirsch", "Canny", "Laplaciano"
        ])
        self.edge_combo.currentTextChanged.connect(self.on_filter_changed)
        panel.add_widget(self.edge_combo)
        
        return panel

    def create_operations_panel(self):
        panel = CollapsiblePanel("⚡ Operaciones entre Imágenes")
        
        # Solo mostrar si hay dos imágenes cargadas
        self.operations_widget = QWidget()
        operations_layout = QVBoxLayout(self.operations_widget)
        operations_layout.setContentsMargins(0, 0, 0, 0)
        
        # Aritméticas
        operations_layout.addWidget(QLabel("Aritméticas:"))
        self.arithmetic_combo = QComboBox()
        self.arithmetic_combo.addItems([
            "Ninguna", "Suma", "Resta", "Multiplicación", 
            "División", "Promedio", "Diferencia"
        ])
        operations_layout.addWidget(self.arithmetic_combo)
        
        # Lógicas
        operations_layout.addWidget(QLabel("Lógicas:"))
        self.logical_combo = QComboBox()
        self.logical_combo.addItems([
            "Ninguna", "AND", "OR", "XOR", "NOT"
        ])
        operations_layout.addWidget(self.logical_combo)
        
        # Botón para aplicar operación
        self.apply_operation_btn = QPushButton("Aplicar Operación")
        self.apply_operation_btn.clicked.connect(self.apply_two_image_operation)
        operations_layout.addWidget(self.apply_operation_btn)
        
        self.operations_widget.setLayout(operations_layout)
        panel.add_widget(self.operations_widget)
        
        # Inicialmente oculto
        self.operations_widget.setVisible(False)
        
        # Ruido (movido aquí)
        panel.add_widget(QLabel("Ruido Gaussiano:"))
        self.noise_checkbox = QCheckBox("Aplicar Ruido")
        self.noise_checkbox.toggled.connect(self.on_parameter_changed)  # Add this line
        panel.add_widget(self.noise_checkbox)
        
        noise_layout = QHBoxLayout()
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setRange(0, 50)
        self.noise_slider.setValue(10)
        self.noise_slider.setEnabled(False)
        
        self.noise_label = QLabel("10")
        self.noise_label.setFixedWidth(25)
        
        noise_layout.addWidget(self.noise_slider)
        noise_layout.addWidget(self.noise_label)
        
        noise_widget = QWidget()
        noise_widget.setLayout(noise_layout)
        panel.add_widget(noise_widget)
        
        # Conexiones
        self.noise_checkbox.toggled.connect(self.noise_slider.setEnabled)
        self.noise_slider.valueChanged.connect(lambda v: (
            self.noise_label.setText(str(v)),
            self.on_parameter_changed()  # Add this line
        ))
        
        return panel

    def create_segmentation_panel(self):
        panel = CollapsiblePanel("✂️ Segmentación")
        
        panel.add_widget(QLabel("Método:"))
        self.segmentation_combo = QComboBox()
        self.segmentation_combo.addItems([
            "Ninguno", "Umbral Media", "Otsu", "Multi-Otsu",
            "Entropía Kapur", "Umbral Banda", "Adaptativo", "Mín. Histograma"
        ])
        self.segmentation_combo.currentTextChanged.connect(self.on_filter_changed)
        panel.add_widget(self.segmentation_combo)
        
        return panel

    def create_action_buttons(self):
        """Crear botones de acción"""
        layout = QVBoxLayout()
        
        # Botón de procesamiento
        self.process_button = QPushButton("🚀 Procesar")
        self.process_button.setObjectName("ProcessButton")
        self.process_button.clicked.connect(self.start_processing)
        layout.addWidget(self.process_button)
        
        # Botón de parar
        self.stop_button = QPushButton("⏹️ Detener")
        self.stop_button.setObjectName("StopButton")
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        # Botón de guardar
        self.save_button = QPushButton("💾 Guardar")
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        
        return layout

    def update_dynamic_parameters(self):
        """Actualizar parámetros dinámicos según filtros seleccionados"""
        # Clear existing dynamic parameters
        for i in reversed(range(self.dynamic_params_layout.count())):
            child = self.dynamic_params_layout.takeAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        # Re-add auto params button
        self.auto_params_btn = QPushButton("🤖 Calcular Automático")
        self.auto_params_btn.clicked.connect(self.calculate_automatic_parameters)
        self.dynamic_params_layout.addWidget(self.auto_params_btn)
        
        # Add parameters based on selected filters
        self.add_filter_specific_parameters()
        self.add_segmentation_specific_parameters()

    def add_filter_specific_parameters(self):
        """Agregar parámetros específicos del filtro seleccionado"""
        filter_type = self.get_selected_filter()
        edge_type = self.get_selected_edge_detection()
        
        # Kernel size for most filters
        if filter_type in ['averaging', 'weighted_averaging', 'median', 'mode', 'gaussian', 'max', 'min']:
            self.add_kernel_size_parameter()
        
        # Gaussian sigma
        if filter_type == 'gaussian':
            self.add_gaussian_sigma_parameter()
        
        # Bilateral parameters
        if filter_type == 'bilateral':
            self.add_bilateral_parameters()
        
        # Canny parameters
        if edge_type == 'canny':
            self.add_canny_parameters()

    def add_kernel_size_parameter(self):
        """Agregar control de tamaño de kernel"""
        layout = QHBoxLayout()
        label = QLabel("Tamaño Kernel:")
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setRange(3, 15)
        self.kernel_spin.setValue(5)
        self.kernel_spin.setSingleStep(2)
        self.kernel_spin.valueChanged.connect(self.on_parameter_changed)
        
        layout.addWidget(label)
        layout.addWidget(self.kernel_spin)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.dynamic_params_layout.addWidget(widget)

    def add_gaussian_sigma_parameter(self):
        """Agregar control de sigma para Gaussiano"""
        layout = QVBoxLayout()
        label = QLabel("Sigma:")
        
        slider_layout = QHBoxLayout()
        self.gaussian_sigma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gaussian_sigma_slider.setRange(1, 50)
        self.gaussian_sigma_slider.setValue(10)
        self.gaussian_sigma_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.gaussian_sigma_label = QLabel("1.0")
        self.gaussian_sigma_slider.valueChanged.connect(
            lambda v: self.gaussian_sigma_label.setText(f"{v/10.0:.1f}")
        )
        
        slider_layout.addWidget(self.gaussian_sigma_slider)
        slider_layout.addWidget(self.gaussian_sigma_label)
        
        layout.addWidget(label)
        layout.addLayout(slider_layout)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.dynamic_params_layout.addWidget(widget)

    def add_bilateral_parameters(self):
        """Agregar parámetros para filtro bilateral"""
        # D parameter
        layout1 = QHBoxLayout()
        label1 = QLabel("Diámetro:")
        self.bilateral_d_spin = QSpinBox()
        self.bilateral_d_spin.setRange(5, 25)
        self.bilateral_d_spin.setValue(9)
        self.bilateral_d_spin.valueChanged.connect(self.on_parameter_changed)
        
        layout1.addWidget(label1)
        layout1.addWidget(self.bilateral_d_spin)
        
        widget1 = QWidget()
        widget1.setLayout(layout1)
        self.dynamic_params_layout.addWidget(widget1)
        
        # Sigma color/space
        layout2 = QVBoxLayout()
        label2 = QLabel("Sigma Color/Space:")
        
        slider_layout = QHBoxLayout()
        self.bilateral_color_slider = QSlider(Qt.Orientation.Horizontal)
        self.bilateral_color_slider.setRange(25, 150)
        self.bilateral_color_slider.setValue(75)
        self.bilateral_color_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.bilateral_color_label = QLabel("75")
        self.bilateral_color_slider.valueChanged.connect(
            lambda v: self.bilateral_color_label.setText(str(v))
        )
        
        slider_layout.addWidget(self.bilateral_color_slider)
        slider_layout.addWidget(self.bilateral_color_label)
        
        layout2.addWidget(label2)
        layout2.addLayout(slider_layout)
        
        widget2 = QWidget()
        widget2.setLayout(layout2)
        self.dynamic_params_layout.addWidget(widget2)

    def add_canny_parameters(self):
        """Agregar parámetros para Canny"""
        # Low threshold
        layout1 = QVBoxLayout()
        label1 = QLabel("Umbral Bajo:")
        
        slider_layout1 = QHBoxLayout()
        self.canny_low_slider = QSlider(Qt.Orientation.Horizontal)
        self.canny_low_slider.setRange(10, 200)
        self.canny_low_slider.setValue(50)
        self.canny_low_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.canny_low_label = QLabel("50")
        self.canny_low_slider.valueChanged.connect(
            lambda v: self.canny_low_label.setText(str(v))
        )
        
        slider_layout1.addWidget(self.canny_low_slider)
        slider_layout1.addWidget(self.canny_low_label)
        
        layout1.addWidget(label1)
        layout1.addLayout(slider_layout1)
        
        widget1 = QWidget()
        widget1.setLayout(layout1)
        self.dynamic_params_layout.addWidget(widget1)
        
        # High threshold
        layout2 = QVBoxLayout()
        label2 = QLabel("Umbral Alto:")
        
        slider_layout2 = QHBoxLayout()
        self.canny_high_slider = QSlider(Qt.Orientation.Horizontal)
        self.canny_high_slider.setRange(50, 300)
        self.canny_high_slider.setValue(150)
        self.canny_high_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.canny_high_label = QLabel("150")
        self.canny_high_slider.valueChanged.connect(
            lambda v: self.canny_high_label.setText(str(v))
        )
        
        slider_layout2.addWidget(self.canny_high_slider)
        slider_layout2.addWidget(self.canny_high_label)
        
        layout2.addWidget(label2)
        layout2.addLayout(slider_layout2)
        
        widget2 = QWidget()
        widget2.setLayout(layout2)
        self.dynamic_params_layout.addWidget(widget2)

    def add_segmentation_specific_parameters(self):
        """Agregar parámetros específicos de segmentación"""
        seg_type = self.get_selected_segmentation()
        
        if seg_type == 'multi_otsu':
            self.add_multi_otsu_parameters()
        elif seg_type == 'band':
            self.add_band_threshold_parameters()
        elif seg_type == 'adaptive':
            self.add_adaptive_parameters()

    def add_multi_otsu_parameters(self):
        """Agregar parámetros para Multi-Otsu"""
        layout = QHBoxLayout()
        label = QLabel("Núm. Clases:")
        self.num_classes_spin = QSpinBox()
        self.num_classes_spin.setRange(2, 6)
        self.num_classes_spin.setValue(3)
        self.num_classes_spin.valueChanged.connect(self.on_parameter_changed)
        
        layout.addWidget(label)
        layout.addWidget(self.num_classes_spin)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.dynamic_params_layout.addWidget(widget)

    def add_band_threshold_parameters(self):
        """Agregar parámetros para umbral banda"""
        # Low threshold
        layout1 = QVBoxLayout()
        label1 = QLabel("Umbral Bajo:")
        
        slider_layout1 = QHBoxLayout()
        self.band_low_slider = QSlider(Qt.Orientation.Horizontal)
        self.band_low_slider.setRange(0, 255)
        self.band_low_slider.setValue(50)
        self.band_low_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.band_low_label = QLabel("50")
        self.band_low_slider.valueChanged.connect(
            lambda v: self.band_low_label.setText(str(v))
        )
        
        slider_layout1.addWidget(self.band_low_slider)
        slider_layout1.addWidget(self.band_low_label)
        
        layout1.addWidget(label1)
        layout1.addLayout(slider_layout1)
        
        widget1 = QWidget()
        widget1.setLayout(layout1)
        self.dynamic_params_layout.addWidget(widget1)
        
        # High threshold
        layout2 = QVBoxLayout()
        label2 = QLabel("Umbral Alto:")
        
        slider_layout2 = QHBoxLayout()
        self.band_high_slider = QSlider(Qt.Orientation.Horizontal)
        self.band_high_slider.setRange(0, 255)
        self.band_high_slider.setValue(200)
        self.band_high_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.band_high_label = QLabel("200")
        self.band_high_slider.valueChanged.connect(
            lambda v: self.band_high_label.setText(str(v))
        )
        
        slider_layout2.addWidget(self.band_high_slider)
        slider_layout2.addWidget(self.band_high_label)
        
        layout2.addWidget(label2)
        layout2.addLayout(slider_layout2)
        
        widget2 = QWidget()
        widget2.setLayout(layout2)
        self.dynamic_params_layout.addWidget(widget2)

    def add_adaptive_parameters(self):
        """Agregar parámetros para umbralización adaptativa"""
        layout = QVBoxLayout()
        label = QLabel("Tamaño Bloque:")
        
        slider_layout = QHBoxLayout()
        self.adaptive_block_slider = QSlider(Qt.Orientation.Horizontal)
        self.adaptive_block_slider.setRange(3, 31)
        self.adaptive_block_slider.setValue(11)
        # Ensure odd values only
        self.adaptive_block_slider.valueChanged.connect(self.ensure_odd_block_size)
        
        self.adaptive_block_label = QLabel("11")
        
        slider_layout.addWidget(self.adaptive_block_slider)
        slider_layout.addWidget(self.adaptive_block_label)
        
        layout.addWidget(label)
        layout.addLayout(slider_layout)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.dynamic_params_layout.addWidget(widget)

    def ensure_odd_block_size(self, value):
        """Asegurar que el tamaño de bloque sea impar"""
        if value % 2 == 0:
            value += 1
            self.adaptive_block_slider.setValue(value)
        self.adaptive_block_label.setText(str(value))
        self.on_parameter_changed()

    def on_parameter_changed(self):
        """Called when any parameter changes"""
        self.schedule_realtime_processing()

    def process_image_realtime(self):
        """Process image in real-time with optimization for current tab"""
        current_tab = self.get_current_tab_data()
        if not current_tab or self.is_processing:
            self.pending_update = True
            return
        self.start_processing_optimized()

    def apply_theme(self):
        """Apply the organic theme"""
        from styles import ThemeManager
        try:
            self.setStyleSheet(ThemeManager.get_organic_theme())
        except:
            # Fallback to basic dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    font-family: "Segoe UI", Arial, sans-serif;
                    font-size: 12px;
                }
            """)

    def start_processing(self):
        """Start manual processing"""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        self.start_processing_optimized()

    def save_image(self):
        """Save the current processed image"""
        current_tab = self.get_current_tab_data()
        if current_tab:
            self.save_tab_image(self.current_tab_id)
        else:
            QMessageBox.information(self, "Información", "No hay imagen procesada para guardar.")

    def stop_processing(self):
        """Stop current processing"""
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            
            self.processing_finished()
            self.results_text.append("⏹️ Procesamiento detenido por el usuario")

    def processing_started(self):
        """Called when processing starts"""
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.show()
        self.operation_label.setText("Procesando...")
        self.results_text.append("🚀 Procesando imagen...")
        self.is_processing = True

    def processing_finished(self):
        """Called when processing finishes"""
        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.progress_bar.hide()
        self.operation_label.setText("Listo")
        self.results_text.append("✅ Procesamiento completado")
        self.is_processing = False
        
        if self.image_processor:
            self.image_processor.deleteLater()
            self.image_processor = None
        
        # Process pending updates
        if self.pending_update:
            self.pending_update = False
            self.schedule_realtime_processing()

    def calculate_automatic_parameters(self):
        """Calculate automatic parameters for current image"""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        self.cleanup_temp_processors()
        
        temp_processor = ImageProcessor(
            image_path=current_tab['image_path'],
            filter_type='none',
            segmentation_type='none'
        )
        temp_processor.calculate_auto_params = True
        temp_processor.parameters_calculated.connect(self.apply_automatic_parameters)
        temp_processor.finished.connect(lambda: self.cleanup_temp_processor(temp_processor))
        
        self.temp_processors.append(temp_processor)
        temp_processor.start()

    def apply_automatic_parameters(self, params):
        """Apply automatically calculated parameters"""
        old_timer_state = self.processing_timer.isActive()
        self.processing_timer.stop()
        
        try:
            if hasattr(self, 'canny_low_slider') and self.canny_low_slider:
                self.canny_low_slider.setValue(params.get('canny_low', 50))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'canny_high_slider') and self.canny_high_slider:
                self.canny_high_slider.setValue(params.get('canny_high', 150))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'kernel_spin') and self.kernel_spin:
                self.kernel_spin.setValue(params.get('kernel_size', 5))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'adaptive_block_slider') and self.adaptive_block_slider:
                self.adaptive_block_slider.setValue(params.get('adaptive_block_size', 11))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'bilateral_color_slider') and self.bilateral_color_slider:
                self.bilateral_color_slider.setValue(int(params.get('bilateral_sigma_color', 75)))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'bilateral_d_spin') and self.bilateral_d_spin:
                self.bilateral_d_spin.setValue(params.get('bilateral_d', 9))
        except RuntimeError:
            pass
        
        try:
            if hasattr(self, 'num_classes_spin') and self.num_classes_spin:
                self.num_classes_spin.setValue(params.get('optimal_multi_otsu_classes', 3))
        except RuntimeError:
            pass
        
        self.results_text.append("🤖 Parámetros calculados automáticamente")
        
        if old_timer_state or self.get_current_tab_data():
            self.schedule_realtime_processing()

    def cleanup_temp_processors(self):
        """Clean up finished temporary processors"""
        for processor in self.temp_processors[:]:
            if processor and not processor.isRunning():
                self.temp_processors.remove(processor)
                processor.deleteLater()

    def cleanup_temp_processor(self, processor):
        """Clean up a specific temporary processor"""
        if processor in self.temp_processors:
            self.temp_processors.remove(processor)
        processor.deleteLater()

    def schedule_realtime_processing(self):
        """Schedule real-time processing with debouncing"""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        self.processing_timer.stop()
        self.processing_timer.start()
        self.update_pipeline_visualization()

    def create_main_workspace(self, parent_layout):
        """Área principal de trabajo con pestañas para imágenes"""
        main_area = QFrame()
        main_area.setObjectName("MainCanvas")
        
        layout = QVBoxLayout(main_area)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Widget de pestañas para imágenes
        self.image_tab_widget = QTabWidget()
        self.image_tab_widget.setObjectName("ImageTabWidget")
        self.image_tab_widget.setTabsClosable(True)
        self.image_tab_widget.currentChanged.connect(self.on_tab_changed)
        self.image_tab_widget.tabCloseRequested.connect(self.close_image_tab)
        
        # Pestaña inicial vacía
        self.create_empty_tab()
        
        layout.addWidget(self.image_tab_widget, 1)
        
        # Panel de estado
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        self.operation_label = QLabel(self.current_operation)
        self.operation_label.setStyleSheet("font-weight: bold;")
        
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setStyleSheet("background: #0078d4;")
        self.progress_bar.hide()
        
        status_layout.addWidget(self.operation_label)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_frame)
        
        parent_layout.addWidget(main_area, 1)

    def create_empty_tab(self):
        """Crear pestaña vacía inicial"""
        empty_widget = QWidget()
        empty_widget.setObjectName("ImageTab")
        empty_layout = QVBoxLayout(empty_widget)
        
        empty_label = QLabel("Arrastra una imagen aquí o usa 'Cargar Imagen'")
        empty_label.setObjectName("ImageDisplay_Tab")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setMinimumSize(600, 400)
        empty_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        empty_layout.addWidget(empty_label)
        
        tab_index = self.image_tab_widget.addTab(empty_widget, "Sin imagen")
        self.image_tab_widget.setTabsClosable(False)  # No permitir cerrar la pestaña vacía
        return tab_index

    def create_image_tab(self, image_path, image_data, tab_name):
        """Crear nueva pestaña para una imagen"""
        # Incrementar contador de pestañas
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"
        
        # Crear widget de la pestaña
        tab_widget = QWidget()
        tab_widget.setObjectName("ImageTab")
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(4, 4, 4, 4)
        
        # Label para mostrar la imagen
        image_label = QLabel()
        image_label.setObjectName("ImageDisplay_Tab")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setMinimumSize(600, 400)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Mostrar la imagen
        self.display_image_in_label(image_data, image_label)
        
        tab_layout.addWidget(image_label)
        
        # Información de la pestaña
        info_frame = QFrame()
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 4, 8, 4)
        
        # Etiqueta de estado
        status_label = QLabel("✓ Imagen cargada")
        status_label.setObjectName("TabStatusLabel")
        
        # Botón para guardar
        save_btn = QPushButton("💾")
        save_btn.setObjectName("TabActionButton")
        save_btn.setToolTip("Guardar imagen")
        save_btn.clicked.connect(lambda: self.save_tab_image(tab_id))
        
        info_layout.addWidget(status_label)
        info_layout.addStretch()
        info_layout.addWidget(save_btn)
        
        tab_layout.addWidget(info_frame)
        
        # Quitar la pestaña vacía si existe
        if self.image_tab_widget.count() == 1 and self.image_tab_widget.tabText(0) == "Sin imagen":
            self.image_tab_widget.removeTab(0)
            self.image_tab_widget.setTabsClosable(True)
        
        # Agregar nueva pestaña
        tab_index = self.image_tab_widget.addTab(tab_widget, tab_name)
        
        # Guardar información de la pestaña
        self.image_tabs[tab_id] = {
            'tab_index': tab_index,
            'image_path': image_path,
            'original_image': image_data.copy(),
            'current_image': image_data.copy(),
            'image_label': image_label,
            'status_label': status_label,
            'tab_name': tab_name
        }
        
        # Activar la nueva pestaña
        self.image_tab_widget.setCurrentIndex(tab_index)
        self.current_tab_id = tab_id
        
        return tab_id

    def display_image_in_label(self, img, label):
        """Mostrar imagen en un QLabel específico"""
        if len(img.shape) == 2:
            h, w = img.shape
            q_image = QImage(img.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            q_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)

    def on_tab_changed(self, index):
        """Manejar cambio de pestaña activa"""
        if index < 0:
            self.current_tab_id = None
            return
            
        # Encontrar el tab_id correspondiente al índice
        for tab_id, tab_data in self.image_tabs.items():
            if tab_data['tab_index'] == index:
                self.current_tab_id = tab_id
                self.update_ui_for_current_tab()
                break

    def close_image_tab(self, index):
        """Cerrar pestaña de imagen"""
        # Encontrar el tab_id correspondiente
        tab_id_to_remove = None
        for tab_id, tab_data in self.image_tabs.items():
            if tab_data['tab_index'] == index:
                tab_id_to_remove = tab_id
                break
        
        if tab_id_to_remove:
            # Remover de diccionario
            del self.image_tabs[tab_id_to_remove]
            
            # Actualizar índices de pestañas restantes
            for tab_id, tab_data in self.image_tabs.items():
                if tab_data['tab_index'] > index:
                    tab_data['tab_index'] -= 1
        
        # Remover pestaña del widget
        self.image_tab_widget.removeTab(index)
        
        # Si no quedan pestañas, crear una vacía
        if self.image_tab_widget.count() == 0:
            self.create_empty_tab()
            self.current_tab_id = None
        
        self.update_ui_state()

    def get_current_tab_data(self):
        """Obtener datos de la pestaña activa"""
        if self.current_tab_id and self.current_tab_id in self.image_tabs:
            return self.image_tabs[self.current_tab_id]
        return None

    def update_ui_for_current_tab(self):
        """Actualizar UI para la pestaña actual"""
        tab_data = self.get_current_tab_data()
        if tab_data:
            # Actualizar información de imagen
            img = tab_data['original_image']
            h, w = img.shape[:2]
            info_text = f"Imagen: {tab_data['tab_name']}\n"
            info_text += f"Tamaño: {w} × {h}\n"
            info_text += f"Canales: {img.shape[2] if len(img.shape) > 2 else 1}"
            self.image_info_label.setText(info_text)
            
            # Procesar imagen si hay filtros activos
            self.schedule_realtime_processing()

    def save_tab_image(self, tab_id):
        """Guardar imagen de una pestaña específica"""
        if tab_id in self.image_tabs:
            tab_data = self.image_tabs[tab_id]
            current_img = tab_data['current_image']
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Imagen Procesada", f"{tab_data['tab_name']}_processed",
                "PNG (*.png);;JPEG (*.jpg);;Todos los archivos (*)"
            )
            
            if file_path:
                success = cv2.imwrite(file_path, current_img)
                if success:
                    self.results_text.append(f"💾 Imagen guardada: {os.path.basename(file_path)}")
                    tab_data['status_label'].setText("💾 Guardada")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo guardar la imagen.")

    def load_image(self):
        """Cargar imagen principal"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            image_data = cv2.imread(file_path)
            
            if image_data is not None:
                tab_name = os.path.basename(file_path)
                tab_id = self.create_image_tab(file_path, image_data, tab_name)
                
                self.results_text.append(f"✓ Imagen cargada: {tab_name}")
                self.update_ui_state()
                self.update_pipeline_visualization()

    def load_second_image(self):
        """Cargar segunda imagen"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Segunda Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            image_data = cv2.imread(file_path)
            
            if image_data is not None:
                tab_name = f"Img2_{os.path.basename(file_path)}"
                tab_id = self.create_image_tab(file_path, image_data, tab_name)
                
                self.results_text.append(f"✓ Segunda imagen: {tab_name}")
                self.update_ui_state()

    def show_filter_info(self):
        """Mostrar ventana de información de filtros"""
        if self.info_window is None:
            self.info_window = FilterInfoWindow(self)
        self.info_window.show()
        self.info_window.raise_()

    def start_processing_optimized(self):
        """Start optimized processing for current tab"""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            return
        
        # Check if image path is valid
        image_path = current_tab.get('image_path', '')
        if not image_path or not image_path.strip():
            print("Warning: No valid image path for processing")
            return
        
        # Clean up previous processor
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            self.image_processor = None

        filter_type = "none"
        filter_params = self.get_filter_parameters()
        
        edge_filter = self.get_selected_edge_detection()
        if edge_filter != "none":
            filter_type = edge_filter
        else:
            morph_filter = self.get_selected_morphological()
            if morph_filter != "none":
                filter_type = morph_filter
            else:
                smoothing_filter = self.get_selected_filter()
                if smoothing_filter != "none":
                    filter_type = smoothing_filter

        try:
            self.image_processor = ImageProcessor(
                image_path=image_path,
                operation_type='none',
                filter_type=filter_type,
                filter_params=filter_params,
                segmentation_type=self.get_selected_segmentation(),
                segmentation_params=self.get_segmentation_parameters(),
                noise_level=self.noise_slider.value() if self.noise_checkbox.isChecked() else 0,
                apply_noise=self.noise_checkbox.isChecked()
            )
            
            self.image_processor.started.connect(self.processing_started)
            self.image_processor.finished.connect(self.processing_finished)
            self.image_processor.image_updated.connect(self.on_current_tab_image_updated)
            
            self.image_processor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar procesamiento: {str(e)}")

    def on_current_tab_image_updated(self, q_image):
        """Update the current tab with processed image"""
        current_tab = self.get_current_tab_data()
        if current_tab:
            try:
                # Convert QImage to numpy array for storage
                width = q_image.width()
                height = q_image.height()
                
                # Get image format and handle different formats
                if q_image.format() == QImage.Format.Format_RGB888:
                    # RGB format - 3 channels
                    ptr = q_image.bits()
                    ptr.setsize(height * width * 3)
                    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
                    # Convert RGB to BGR for OpenCV
                    current_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                elif q_image.format() == QImage.Format.Format_ARGB32 or q_image.format() == QImage.Format.Format_RGBA8888:
                    # ARGB/RGBA format - 4 channels
                    ptr = q_image.bits()
                    ptr.setsize(height * width * 4)
                    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
                    # Convert RGBA to BGR, removing alpha channel
                    current_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
                elif q_image.format() == QImage.Format.Format_Grayscale8:
                    # Grayscale format
                    ptr = q_image.bits()
                    ptr.setsize(height * width)
                    current_img = np.frombuffer(ptr, np.uint8).reshape((height, width))
                else:
                    # Convert to RGB first if unknown format
                    q_image_rgb = q_image.convertToFormat(QImage.Format.Format_RGB888)
                    ptr = q_image_rgb.bits()
                    ptr.setsize(height * width * 3)
                    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
                    current_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                
                current_tab['current_image'] = current_img
                current_tab['status_label'].setText("🔄 Procesada")
                
                # Update display
                scaled_pixmap = QPixmap.fromImage(q_image).scaled(
                    current_tab['image_label'].size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                current_tab['image_label'].setPixmap(scaled_pixmap)
                
            except Exception as e:
                print(f"Error updating image: {e}")
                # Fallback: just update the display without storing the processed version
                scaled_pixmap = QPixmap.fromImage(q_image).scaled(
                    current_tab['image_label'].size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                current_tab['image_label'].setPixmap(scaled_pixmap)
                current_tab['status_label'].setText("⚠️ Error conversión")

    def apply_two_image_operation(self):
        """Apply operation between two images from different tabs"""
        if len(self.image_tabs) < 2:
            QMessageBox.warning(self, "Advertencia", "Se necesitan al menos 2 imágenes para realizar operaciones.")
            return
        
        # Get first two images
        tab_ids = list(self.image_tabs.keys())
        tab1_data = self.image_tabs[tab_ids[0]]
        tab2_data = self.image_tabs[tab_ids[1]]
        
        # Get selected operations
        arithmetic_op = self.arithmetic_combo.currentText()
        logical_op = self.logical_combo.currentText()
        
        operation_type = 'none'
        if arithmetic_op != "Ninguna":
            operation_map = {
                "Suma": "suma", "Resta": "resta", "Multiplicación": "multiplicacion",
                "División": "division", "Promedio": "promedio", "Diferencia": "diferencia"
            }
            operation_type = operation_map.get(arithmetic_op, 'none')
        elif logical_op != "Ninguna":
            operation_map = {
                "AND": "and", "OR": "or", "XOR": "xor", "NOT": "not"
            }
            operation_type = operation_map.get(logical_op, 'none')
        
        if operation_type != 'none':
            try:
                self.image_processor = ImageProcessor(
                    image_path=tab1_data['image_path'],
                    second_image_path=tab2_data['image_path'],
                    operation_type=operation_type,
                    filter_type='none',
                    segmentation_type='none'
                )
                
                self.image_processor.started.connect(self.processing_started)
                self.image_processor.finished.connect(self.processing_finished)
                self.image_processor.image_updated.connect(self.on_operation_result)
                
                self.image_processor.start()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error en operación: {str(e)}")

    def on_operation_result(self, q_image):
        """Create new tab with operation result"""
        try:
            # Create new tab for result
            operation_name = f"Resultado_{self.tab_counter + 1}"
            
            # Convert QImage to numpy array with proper error handling
            width = q_image.width()
            height = q_image.height()
            
            # Handle different image formats safely
            if q_image.format() == QImage.Format.Format_RGB888:
                ptr = q_image.bits()
                ptr.setsize(height * width * 3)
                arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
                result_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            elif q_image.format() == QImage.Format.Format_ARGB32 or q_image.format() == QImage.Format.Format_RGBA8888:
                ptr = q_image.bits()
                ptr.setsize(height * width * 4)
                arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
                result_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            elif q_image.format() == QImage.Format.Format_Grayscale8:
                ptr = q_image.bits()
                ptr.setsize(height * width)
                result_img = np.frombuffer(ptr, np.uint8).reshape((height, width))
            else:
                # Convert to RGB first
                q_image_rgb = q_image.convertToFormat(QImage.Format.Format_RGB888)
                ptr = q_image_rgb.bits()
                ptr.setsize(height * width * 3)
                arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
                result_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            
            # Create result tab with a placeholder path
            placeholder_path = f"temp_{operation_name}.png"
            self.create_image_tab(placeholder_path, result_img, operation_name)
            self.results_text.append(f"✅ Operación completada: {operation_name}")
            
        except Exception as e:
            print(f"Error creating operation result: {e}")
            self.results_text.append(f"❌ Error en operación: {str(e)}")

    def create_properties_panel(self, parent_layout):
        """Panel de propiedades y resultados"""
        props_panel = QFrame()
        props_panel.setObjectName("Sidebar")
        props_panel.setFixedWidth(300)
        
        layout = QVBoxLayout(props_panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Información de imagen
        info_panel = CollapsiblePanel("📊 Información")
        
        self.image_info_label = QLabel("No hay imagen cargada")
        self.image_info_label.setWordWrap(True)
        info_panel.add_widget(self.image_info_label)
        
        layout.addWidget(info_panel)
        
        # Resultados
        results_panel = CollapsiblePanel("📋 Resultados")
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setPlaceholderText("Los resultados aparecerán aquí...")
        results_panel.add_widget(self.results_text)
        
        layout.addWidget(results_panel)
        
        layout.addStretch()
        
        parent_layout.addWidget(props_panel)

    def get_selected_filter(self):
        """Get the currently selected filter type"""
        filter_map = {
            "Ninguno": "none",
            "Promedio": "averaging", 
            "Promedio Pesado": "weighted_averaging",
            "Mediana": "median",
            "Moda": "mode",
            "Bilateral": "bilateral",
            "Gaussiano": "gaussian"
        }
        return filter_map.get(self.smoothing_combo.currentText(), "none")

    def get_selected_edge_detection(self):
        """Get the currently selected edge detection type"""
        edge_map = {
            "Ninguno": "none",
            "Roberts": "roberts",
            "Prewitt": "prewitt", 
            "Sobel": "sobel",
            "Robinson": "robinson",
            "Kirsch": "kirsch",
            "Canny": "canny",
            "Laplaciano": "laplacian"
        }
        return edge_map.get(self.edge_combo.currentText(), "none")

    def get_selected_morphological(self):
        """Get the currently selected morphological operation"""
        morph_map = {
            "Ninguno": "none",
            "Máximo": "max",
            "Mínimo": "min"
        }
        return morph_map.get(self.morphological_combo.currentText(), "none")

    def get_selected_segmentation(self):
        """Get the currently selected segmentation type"""
        seg_map = {
            "Ninguno": "none",
            "Umbral Media": "mean",
            "Otsu": "otsu",
            "Multi-Otsu": "multi_otsu",
            "Entropía Kapur": "kapur", 
            "Umbral Banda": "band",
            "Adaptativo": "adaptive",
            "Mín. Histograma": "histogram_min"
        }
        return seg_map.get(self.segmentation_combo.currentText(), "none")

    def get_filter_parameters(self):
        """Obtener parámetros dinámicos actuales"""
        params = {}
        
        # Check if widgets exist and are valid before accessing them
        try:
            if hasattr(self, 'kernel_spin') and self.kernel_spin and not self.kernel_spin.isHidden():
                params['kernel_size'] = self.kernel_spin.value()
        except RuntimeError:
            pass
        
        try:
            if hasattr(self, 'canny_low_slider') and self.canny_low_slider and not self.canny_low_slider.isHidden():
                params['low_threshold'] = self.canny_low_slider.value()
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'canny_high_slider') and self.canny_high_slider and not self.canny_high_slider.isHidden():
                params['high_threshold'] = self.canny_high_slider.value()
        except RuntimeError:
            pass
        
        try:
            if hasattr(self, 'bilateral_d_spin') and self.bilateral_d_spin and not self.bilateral_d_spin.isHidden():
                params['d'] = self.bilateral_d_spin.value()
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'bilateral_color_slider') and self.bilateral_color_slider and not self.bilateral_color_slider.isHidden():
                params['sigma_color'] = self.bilateral_color_slider.value()
                params['sigma_space'] = self.bilateral_color_slider.value()
        except RuntimeError:
            pass
        
        try:
            if hasattr(self, 'gaussian_sigma_slider') and self.gaussian_sigma_slider and not self.gaussian_sigma_slider.isHidden():
                params['sigma'] = self.gaussian_sigma_slider.value() / 10.0
        except RuntimeError:
            pass
        
        return params

    def get_segmentation_parameters(self):
        """Obtener parámetros de segmentación dinámicos"""
        params = {}
        
        try:
            if hasattr(self, 'num_classes_spin') and self.num_classes_spin and not self.num_classes_spin.isHidden():
                params['num_thresholds'] = self.num_classes_spin.value()
        except RuntimeError:
            pass
        
        try:
            if hasattr(self, 'band_low_slider') and self.band_low_slider and not self.band_low_slider.isHidden():
                params['low_threshold'] = self.band_low_slider.value()
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'band_high_slider') and self.band_high_slider and not self.band_high_slider.isHidden():
                params['high_threshold'] = self.band_high_slider.value()
        except RuntimeError:
            pass
        
        try:
            if hasattr(self, 'adaptive_block_slider') and self.adaptive_block_slider and not self.adaptive_block_slider.isHidden():
                params['block_size'] = self.adaptive_block_slider.value()
        except RuntimeError:
            pass
        
        return params

    def on_filter_changed(self):
        """Called when any filter/segmentation setting changes"""
        self.update_dynamic_parameters()
        self.update_pipeline_visualization()
        self.schedule_realtime_processing()

    def create_visualization_panel(self):
        """Panel para visualización de histograma y efectos"""
        panel = CollapsiblePanel("📊 Visualización")
        
        # Botón para mostrar histograma
        self.histogram_btn = QPushButton("📈 Ver Histograma")
        self.histogram_btn.clicked.connect(self.show_histogram)
        panel.add_widget(self.histogram_btn)
        
        # Botón para mostrar negativo
        self.negative_btn = QPushButton("🔄 Ver Negativo")
        self.negative_btn.clicked.connect(self.show_negative)
        panel.add_widget(self.negative_btn)
        
        return panel

    def create_object_detection_panel(self):
        """Panel para detección de objetos conectados"""
        panel = CollapsiblePanel("🔍 Detección de Objetos")
        
        # Selector de conectividad
        panel.add_widget(QLabel("Conectividad:"))
        self.connectivity_combo = QComboBox()
        self.connectivity_combo.addItems(["Vecindad-4", "Vecindad-8"])
        panel.add_widget(self.connectivity_combo)
        
        # Umbral para binarización
        panel.add_widget(QLabel("Umbral Binarización:"))
        threshold_layout = QHBoxLayout()
        self.binary_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.binary_threshold_slider.setRange(0, 255)
        self.binary_threshold_slider.setValue(127)
        
        self.binary_threshold_label = QLabel("127")
        self.binary_threshold_slider.valueChanged.connect(
            lambda v: self.binary_threshold_label.setText(str(v))
        )
        
        threshold_layout.addWidget(self.binary_threshold_slider)
        threshold_layout.addWidget(self.binary_threshold_label)
        
        threshold_widget = QWidget()
        threshold_widget.setLayout(threshold_layout)
        panel.add_widget(threshold_widget)
        
        # Botón para detectar objetos
        self.detect_objects_btn = QPushButton("🎯 Detectar Objetos")
        self.detect_objects_btn.clicked.connect(self.detect_objects)
        panel.add_widget(self.detect_objects_btn)
        
        # Etiqueta para mostrar resultados
        self.objects_result_label = QLabel("Objetos detectados: -")
        self.objects_result_label.setWordWrap(True)
        self.objects_result_label.setStyleSheet("font-size: 10px; color: #666666;")
        panel.add_widget(self.objects_result_label)
        
        return panel

    def show_histogram(self):
        """Mostrar histograma de la imagen actual"""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            img = current_tab['current_image']
            
            # Crear ventana para histograma
            self.histogram_window = QWidget()
            self.histogram_window.setWindowTitle("Histograma de la Imagen")
            self.histogram_window.setGeometry(200, 200, 800, 600)
            
            layout = QVBoxLayout(self.histogram_window)
            
            # Calcular histograma
            if len(img.shape) == 3:  # Imagen en color
                colors = ['b', 'g', 'r']
                labels = ['Azul', 'Verde', 'Rojo']
                
                plt.figure(figsize=(10, 6))
                for i, (color, label) in enumerate(zip(colors, labels)):
                    hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                    plt.plot(hist, color=color, label=label)
                
                plt.title('Histograma RGB')
                plt.xlabel('Intensidad de Pixel')
                plt.ylabel('Frecuencia')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
            else:  # Imagen en escala de grises
                hist = cv2.calcHist([img], [0], None, [256], [0, 256])
                plt.figure(figsize=(10, 6))
                plt.plot(hist, color='black')
                plt.title('Histograma en Escala de Grises')
                plt.xlabel('Intensidad de Pixel')
                plt.ylabel('Frecuencia')
                plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            self.results_text.append("📈 Histograma mostrado")
            
        except ImportError:
            QMessageBox.warning(self, "Error", "Matplotlib no está instalado. Instala con: pip install matplotlib")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al mostrar histograma: {str(e)}")

    def show_negative(self):
        """Mostrar el negativo de la imagen actual"""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        try:
            img = current_tab['current_image'].copy()
            
            # Calcular negativo
            negative_img = 255 - img
            
            # Crear nueva pestaña con el negativo
            operation_name = f"Negativo_{self.tab_counter + 1}"
            placeholder_path = f"temp_{operation_name}.png"
            self.create_image_tab(placeholder_path, negative_img, operation_name)
            
            self.results_text.append(f"🔄 Negativo creado: {operation_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear negativo: {str(e)}")

    def detect_objects(self):
        """Detectar objetos conectados en la imagen"""
        current_tab = self.get_current_tab_data()
        if not current_tab:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        try:
            img = current_tab['current_image'].copy()
            
            # Convertir a escala de grises si es necesario
            if len(img.shape) == 3:
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray_img = img.copy()
            
            # Binarizar la imagen
            threshold_value = self.binary_threshold_slider.value()
            _, binary_img = cv2.threshold(gray_img, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Determinar conectividad
            connectivity = 4 if self.connectivity_combo.currentText() == "Vecindad-4" else 8
            
            # Etiquetar componentes conectados
            num_labels, labels = cv2.connectedComponents(binary_img, connectivity=connectivity)
            
            # Crear imagen con colores para cada objeto
            colored_labels = np.zeros((labels.shape[0], labels.shape[1], 3), dtype=np.uint8)
            
            # Asignar colores aleatorios a cada etiqueta
            np.random.seed(42)  # Para resultados reproducibles
            colors = np.random.randint(0, 255, size=(num_labels, 3), dtype=np.uint8)
            colors[0] = [0, 0, 0]  # Fondo negro
            
            for label in range(num_labels):
                colored_labels[labels == label] = colors[label]
            
            # Encontrar contornos para numeración
            contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Crear imagen con contornos y numeración
            result_img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
            
            # Dibujar contornos y números
            for i, contour in enumerate(contours):
                # Dibujar contorno
                cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 2)
                
                # Encontrar centro y colocar número
                moments = cv2.moments(contour)
                if moments["m00"] != 0:
                    cx = int(moments["m10"] / moments["m00"])
                    cy = int(moments["m01"] / moments["m00"])
                    cv2.putText(result_img, f'{i + 1}', (cx-10, cy), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Crear pestañas con los resultados
            connectivity_name = self.connectivity_combo.currentText()
            
            # Pestaña con imagen binarizada
            binary_name = f"Binaria_T{threshold_value}_{self.tab_counter + 1}"
            self.create_image_tab(f"temp_{binary_name}.png", 
                                cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR), binary_name)
            
            # Pestaña con etiquetas coloreadas
            labels_name = f"Etiquetas_{connectivity_name}_{self.tab_counter + 1}"
            self.create_image_tab(f"temp_{labels_name}.png", colored_labels, labels_name)
            
            # Pestaña con contornos numerados
            contours_name = f"Objetos_{connectivity_name}_{self.tab_counter + 1}"
            self.create_image_tab(f"temp_{contours_name}.png", result_img, contours_name)
            
            # Actualizar etiqueta de resultados
            num_objects = num_labels - 1  # Restar 1 para excluir el fondo
            self.objects_result_label.setText(
                f"Objetos detectados: {num_objects}\n"
                f"Conectividad: {connectivity_name}\n"
                f"Umbral: {threshold_value}"
            )
            
            # Actualizar panel de resultados
            self.results_text.append(f"🎯 Detección completada:")
            self.results_text.append(f"   • {num_objects} objetos con {connectivity_name}")
            self.results_text.append(f"   • Umbral: {threshold_value}")
            self.results_text.append(f"   • Pestañas creadas: {binary_name}, {labels_name}, {contours_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en detección de objetos: {str(e)}")
            import traceback
            traceback.print_exc()

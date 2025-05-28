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
        self.image_path = None
        self.second_image_path = None
        self.original_image = None
        self.second_image = None
        self.current_processed_image = None
        self.image_processor = None
        self.temp_processors = []
        
        # Real-time processing optimization
        self.processing_timer = QTimer(self)
        self.processing_timer.setSingleShot(True)
        self.processing_timer.setInterval(300)  # 300ms debounce
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
        has_primary_image = self.image_path is not None
        has_second_image = self.second_image_path is not None
        
        # Show/hide second image controls
        self.load_second_btn.setVisible(has_primary_image)
        
        # Show/hide operations panel
        self.operations_widget.setVisible(has_primary_image and has_second_image)
        
        # Enable/disable process button
        self.process_button.setEnabled(has_primary_image)

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

    def create_main_workspace(self, parent_layout):
        """Área principal de trabajo"""
        main_area = QFrame()
        main_area.setObjectName("MainCanvas")
        
        layout = QVBoxLayout(main_area)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Área de imagen
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(600, 400)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setObjectName("ImageDisplay")
        self.image_label.setText("Arrastra una imagen aquí o usa 'Cargar Imagen'")
        
        layout.addWidget(self.image_label, 1)
        
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

    def show_filter_info(self):
        if self.info_window is None:
            self.info_window = FilterInfoWindow(self)
        self.info_window.show()
        self.info_window.raise_()

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            
            if self.original_image is not None:
                self.display_image(self.original_image)
                
                # Update UI state
                self.update_ui_state()
                
                # Update information
                h, w = self.original_image.shape[:2]
                info_text = f"Imagen: {os.path.basename(file_path)}\n"
                info_text += f"Tamaño: {w} × {h}\n"
                info_text += f"Canales: {self.original_image.shape[2] if len(self.original_image.shape) > 2 else 1}"
                self.image_info_label.setText(info_text)
                
                self.results_text.append(f"✓ Imagen cargada: {os.path.basename(file_path)}")
                
                # Update pipeline visualization
                self.update_pipeline_visualization()
                
                # Start real-time processing
                self.schedule_realtime_processing()

    def load_second_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Segunda Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.second_image_path = file_path
            self.second_image = cv2.imread(file_path)
            
            if self.second_image is not None:
                # Update UI state
                self.update_ui_state()
                self.results_text.append(f"✓ Segunda imagen: {os.path.basename(file_path)}")

    def display_image(self, img):
        if len(img.shape) == 2:
            h, w = img.shape
            q_image = QImage(img.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            q_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        # Usar QPixmap para la visualización
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def create_preprocessing_menu(self):
        section = MenuSection("Preprocessing")
        
        # Noise simulation
        noise_frame = QFrame()
        noise_layout = QVBoxLayout(noise_frame)
        noise_layout.setContentsMargins(0, 0, 0, 0)
        noise_layout.setSpacing(8)
        
        self.noise_checkbox = QCheckBox("Add Gaussian Noise")
        self.noise_checkbox.setObjectName("ModernCheckbox")
        
        noise_control = QFrame()
        noise_control_layout = QHBoxLayout(noise_control)
        noise_control_layout.setContentsMargins(0, 0, 0, 0)
        noise_control_layout.setSpacing(8)
        
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setObjectName("ModernSlider")
        self.noise_slider.setRange(0, 50)
        self.noise_slider.setValue(10)
        self.noise_slider.setEnabled(False)
        
        self.noise_value_label = QLabel("10")
        self.noise_value_label.setObjectName("ValueLabel")
        self.noise_value_label.setFixedWidth(30)
        
        noise_control_layout.addWidget(self.noise_slider)
        noise_control_layout.addWidget(self.noise_value_label)
        
        self.noise_checkbox.toggled.connect(self.noise_slider.setEnabled)
        self.noise_slider.valueChanged.connect(lambda v: self.noise_value_label.setText(str(v)))
        
        noise_layout.addWidget(self.noise_checkbox)
        noise_layout.addWidget(noise_control)
        
        section.add_item(noise_frame)
        
        # Smoothing filters
        section.add_item(QLabel("Smoothing Filter"))
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.setObjectName("ModernCombo")
        self.smoothing_combo.addItems([
            "None", "Average", "Weighted Average", "Median", 
            "Mode", "Bilateral", "Gaussian"
        ])
        section.add_item(self.smoothing_combo)
        
        # Kernel size
        kernel_frame = QFrame()
        kernel_layout = QHBoxLayout(kernel_frame)
        kernel_layout.setContentsMargins(0, 0, 0, 0)
        kernel_layout.setSpacing(8)
        
        kernel_layout.addWidget(QLabel("Kernel Size"))
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setObjectName("ModernSpin")
        self.kernel_spin.setRange(3, 15)
        self.kernel_spin.setValue(5)
        self.kernel_spin.setSingleStep(2)
        kernel_layout.addWidget(self.kernel_spin)
        
        section.add_item(kernel_frame)
        
        return section

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

    def process_image_realtime(self):
        """Process image in real-time with optimization"""
        if not self.image_path or self.is_processing:
            self.pending_update = True
            return
        self.start_processing_optimized()

    def save_image(self):
        """Save the processed image"""
        if self.current_processed_image:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Imagen Procesada", "",
                "PNG (*.png);;JPEG (*.jpg);;Todos los archivos (*)"
            )
            
            if file_path:
                success = self.current_processed_image.save(file_path)
                if success:
                    self.results_text.append(f"💾 Imagen guardada: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo guardar la imagen.")
        else:
            QMessageBox.information(self, "Información", "No hay imagen procesada para guardar.")

    def processing_started(self):
        """Called when processing starts"""
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.show()
        self.operation_label.setText("Procesando...")
        self.results_text.append("🚀 Procesando imagen...")

    def processing_finished(self):
        """Called when processing finishes"""
        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.progress_bar.hide()
        self.operation_label.setText("Listo")
        self.results_text.append("✅ Procesamiento completado")
        
        if self.image_processor:
            # Use deleteLater for proper Qt cleanup
            self.image_processor.deleteLater()
            self.image_processor = None

    def on_image_updated(self, q_image):
        """Called when processed image is ready"""
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.current_processed_image = q_image

    def start_processing(self):
        """Start image processing with current settings"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        # Clean up previous processor without waiting
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
                image_path=self.image_path,
                second_image_path=self.second_image_path,
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
            self.image_processor.image_updated.connect(self.on_image_updated)
            
            self.image_processor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar procesamiento: {str(e)}")

    def stop_processing(self):
        """Stop current processing"""
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            
            self.processing_finished()
            self.results_text.append("⏹️ Procesamiento detenido por el usuario")

    def calculate_automatic_parameters(self):
        """Calcular parámetros automáticos para la imagen actual"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        self.cleanup_temp_processors()
        
        temp_processor = ImageProcessor(
            image_path=self.image_path,
            filter_type='none',
            segmentation_type='none'
        )
        temp_processor.calculate_auto_params = True
        temp_processor.parameters_calculated.connect(self.apply_automatic_parameters)
        temp_processor.finished.connect(lambda: self.cleanup_temp_processor(temp_processor))
        
        self.temp_processors.append(temp_processor)
        temp_processor.start()

    def apply_automatic_parameters(self, params):
        """Aplicar parámetros calculados automáticamente"""
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
                self.bilateral_color_slider.setValue(int(params.get('bilateral_sigma_color', 80)))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'bilateral_d_spin') and self.bilateral_d_spin:
                self.bilateral_d_spin.setValue(params.get('bilateral_d', 9))
        except RuntimeError:
            pass
        
        # Apply optimal multi-otsu classes if available
        try:
            if hasattr(self, 'num_classes_spin') and self.num_classes_spin:
                optimal_classes = params.get('optimal_multi_otsu_classes', 3)
                self.num_classes_spin.setValue(optimal_classes)
                if optimal_classes != 3:
                    self.results_text.append(f"🎯 Clases óptimas para Multi-Otsu: {optimal_classes}")
        except RuntimeError:
            pass
        
        self.results_text.append("🤖 Parámetros calculados automáticamente")
        
        if old_timer_state or self.image_path:
            self.schedule_realtime_processing()

    def cleanup_temp_processors(self):
        """Clean up finished temporary processors"""
        for processor in self.temp_processors[:]:
            if processor and not processor.isRunning():
                self.temp_processors.remove(processor)

    def cleanup_temp_processor(self, processor):
        """Clean up a specific temporary processor"""
        if processor in self.temp_processors:
            self.temp_processors.remove(processor)
        # Use deleteLater for proper Qt cleanup
        processor.deleteLater()

    def on_filter_changed(self):
        """Called when any filter/segmentation setting changes"""
        self.update_dynamic_parameters()
        self.update_pipeline_visualization()  # Add this line
        self.schedule_realtime_processing()

    def schedule_realtime_processing(self):
        """Schedule real-time processing with debouncing"""
        if not self.image_path:
            return
        self.processing_timer.stop()
        self.processing_timer.start()
        # Also update pipeline when scheduling processing
        self.update_pipeline_visualization()

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            
            if self.original_image is not None:
                self.display_image(self.original_image)
                
                # Update UI state
                self.update_ui_state()
                
                # Update information
                h, w = self.original_image.shape[:2]
                info_text = f"Imagen: {os.path.basename(file_path)}\n"
                info_text += f"Tamaño: {w} × {h}\n"
                info_text += f"Canales: {self.original_image.shape[2] if len(self.original_image.shape) > 2 else 1}"
                self.image_info_label.setText(info_text)
                
                self.results_text.append(f"✓ Imagen cargada: {os.path.basename(file_path)}")
                
                # Update pipeline visualization
                self.update_pipeline_visualization()
                
                # Start real-time processing
                self.schedule_realtime_processing()

    def load_second_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Segunda Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.second_image_path = file_path
            self.second_image = cv2.imread(file_path)
            
            if self.second_image is not None:
                # Update UI state
                self.update_ui_state()
                self.results_text.append(f"✓ Segunda imagen: {os.path.basename(file_path)}")

    def display_image(self, img):
        if len(img.shape) == 2:
            h, w = img.shape
            q_image = QImage(img.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            q_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        # Usar QPixmap para la visualización
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def create_preprocessing_menu(self):
        section = MenuSection("Preprocessing")
        
        # Noise simulation
        noise_frame = QFrame()
        noise_layout = QVBoxLayout(noise_frame)
        noise_layout.setContentsMargins(0, 0, 0, 0)
        noise_layout.setSpacing(8)
        
        self.noise_checkbox = QCheckBox("Add Gaussian Noise")
        self.noise_checkbox.setObjectName("ModernCheckbox")
        
        noise_control = QFrame()
        noise_control_layout = QHBoxLayout(noise_control)
        noise_control_layout.setContentsMargins(0, 0, 0, 0)
        noise_control_layout.setSpacing(8)
        
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setObjectName("ModernSlider")
        self.noise_slider.setRange(0, 50)
        self.noise_slider.setValue(10)
        self.noise_slider.setEnabled(False)
        
        self.noise_value_label = QLabel("10")
        self.noise_value_label.setObjectName("ValueLabel")
        self.noise_value_label.setFixedWidth(30)
        
        noise_control_layout.addWidget(self.noise_slider)
        noise_control_layout.addWidget(self.noise_value_label)
        
        self.noise_checkbox.toggled.connect(self.noise_slider.setEnabled)
        self.noise_slider.valueChanged.connect(lambda v: self.noise_value_label.setText(str(v)))
        
        noise_layout.addWidget(self.noise_checkbox)
        noise_layout.addWidget(noise_control)
        
        section.add_item(noise_frame)
        
        # Smoothing filters
        section.add_item(QLabel("Smoothing Filter"))
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.setObjectName("ModernCombo")
        self.smoothing_combo.addItems([
            "None", "Average", "Weighted Average", "Median", 
            "Mode", "Bilateral", "Gaussian"
        ])
        section.add_item(self.smoothing_combo)
        
        # Kernel size
        kernel_frame = QFrame()
        kernel_layout = QHBoxLayout(kernel_frame)
        kernel_layout.setContentsMargins(0, 0, 0, 0)
        kernel_layout.setSpacing(8)
        
        kernel_layout.addWidget(QLabel("Kernel Size"))
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setObjectName("ModernSpin")
        self.kernel_spin.setRange(3, 15)
        self.kernel_spin.setValue(5)
        self.kernel_spin.setSingleStep(2)
        kernel_layout.addWidget(self.kernel_spin)
        
        section.add_item(kernel_frame)
        
        return section

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

    def process_image_realtime(self):
        """Process image in real-time with optimization"""
        if not self.image_path or self.is_processing:
            self.pending_update = True
            return
        self.start_processing_optimized()

    def save_image(self):
        """Save the processed image"""
        if self.current_processed_image:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Imagen Procesada", "",
                "PNG (*.png);;JPEG (*.jpg);;Todos los archivos (*)"
            )
            
            if file_path:
                success = self.current_processed_image.save(file_path)
                if success:
                    self.results_text.append(f"💾 Imagen guardada: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo guardar la imagen.")
        else:
            QMessageBox.information(self, "Información", "No hay imagen procesada para guardar.")

    def processing_started(self):
        """Called when processing starts"""
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.show()
        self.operation_label.setText("Procesando...")
        self.results_text.append("🚀 Procesando imagen...")

    def processing_finished(self):
        """Called when processing finishes"""
        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.progress_bar.hide()
        self.operation_label.setText("Listo")
        self.results_text.append("✅ Procesamiento completado")
        
        if self.image_processor:
            # Use deleteLater for proper Qt cleanup
            self.image_processor.deleteLater()
            self.image_processor = None

    def on_image_updated(self, q_image):
        """Called when processed image is ready"""
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.current_processed_image = q_image

    def start_processing(self):
        """Start image processing with current settings"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        # Clean up previous processor without waiting
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
                image_path=self.image_path,
                second_image_path=self.second_image_path,
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
            self.image_processor.image_updated.connect(self.on_image_updated)
            
            self.image_processor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar procesamiento: {str(e)}")

    def stop_processing(self):
        """Stop current processing"""
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            
            self.processing_finished()
            self.results_text.append("⏹️ Procesamiento detenido por el usuario")

    def calculate_automatic_parameters(self):
        """Calcular parámetros automáticos para la imagen actual"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        self.cleanup_temp_processors()
        
        temp_processor = ImageProcessor(
            image_path=self.image_path,
            filter_type='none',
            segmentation_type='none'
        )
        temp_processor.calculate_auto_params = True
        temp_processor.parameters_calculated.connect(self.apply_automatic_parameters)
        temp_processor.finished.connect(lambda: self.cleanup_temp_processor(temp_processor))
        
        self.temp_processors.append(temp_processor)
        temp_processor.start()

    def apply_automatic_parameters(self, params):
        """Aplicar parámetros calculados automáticamente"""
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
                self.bilateral_color_slider.setValue(int(params.get('bilateral_sigma_color', 80)))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'bilateral_d_spin') and self.bilateral_d_spin:
                self.bilateral_d_spin.setValue(params.get('bilateral_d', 9))
        except RuntimeError:
            pass
        
        # Apply optimal multi-otsu classes if available
        try:
            if hasattr(self, 'num_classes_spin') and self.num_classes_spin:
                optimal_classes = params.get('optimal_multi_otsu_classes', 3)
                self.num_classes_spin.setValue(optimal_classes)
                if optimal_classes != 3:
                    self.results_text.append(f"🎯 Clases óptimas para Multi-Otsu: {optimal_classes}")
        except RuntimeError:
            pass
        
        self.results_text.append("🤖 Parámetros calculados automáticamente")
        
        if old_timer_state or self.image_path:
            self.schedule_realtime_processing()

    def cleanup_temp_processors(self):
        """Clean up finished temporary processors"""
        for processor in self.temp_processors[:]:
            if processor and not processor.isRunning():
                self.temp_processors.remove(processor)

    def cleanup_temp_processor(self, processor):
        """Clean up a specific temporary processor"""
        if processor in self.temp_processors:
            self.temp_processors.remove(processor)
        # Use deleteLater for proper Qt cleanup
        processor.deleteLater()

    def on_filter_changed(self):
        """Called when any filter/segmentation setting changes"""
        self.update_dynamic_parameters()
        self.update_pipeline_visualization()  # Add this line
        self.schedule_realtime_processing()

    def schedule_realtime_processing(self):
        """Schedule real-time processing with debouncing"""
        if not self.image_path:
            return
        self.processing_timer.stop()
        self.processing_timer.start()
        # Also update pipeline when scheduling processing
        self.update_pipeline_visualization()

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            
            if self.original_image is not None:
                self.display_image(self.original_image)
                
                # Update UI state
                self.update_ui_state()
                
                # Update information
                h, w = self.original_image.shape[:2]
                info_text = f"Imagen: {os.path.basename(file_path)}\n"
                info_text += f"Tamaño: {w} × {h}\n"
                info_text += f"Canales: {self.original_image.shape[2] if len(self.original_image.shape) > 2 else 1}"
                self.image_info_label.setText(info_text)
                
                self.results_text.append(f"✓ Imagen cargada: {os.path.basename(file_path)}")
                
                # Update pipeline visualization
                self.update_pipeline_visualization()
                
                # Start real-time processing
                self.schedule_realtime_processing()

    def load_second_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Segunda Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.second_image_path = file_path
            self.second_image = cv2.imread(file_path)
            
            if self.second_image is not None:
                # Update UI state
                self.update_ui_state()
                self.results_text.append(f"✓ Segunda imagen: {os.path.basename(file_path)}")

    def display_image(self, img):
        if len(img.shape) == 2:
            h, w = img.shape
            q_image = QImage(img.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            q_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        # Usar QPixmap para la visualización
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def create_preprocessing_menu(self):
        section = MenuSection("Preprocessing")
        
        # Noise simulation
        noise_frame = QFrame()
        noise_layout = QVBoxLayout(noise_frame)
        noise_layout.setContentsMargins(0, 0, 0, 0)
        noise_layout.setSpacing(8)
        
        self.noise_checkbox = QCheckBox("Add Gaussian Noise")
        self.noise_checkbox.setObjectName("ModernCheckbox")
        
        noise_control = QFrame()
        noise_control_layout = QHBoxLayout(noise_control)
        noise_control_layout.setContentsMargins(0, 0, 0, 0)
        noise_control_layout.setSpacing(8)
        
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setObjectName("ModernSlider")
        self.noise_slider.setRange(0, 50)
        self.noise_slider.setValue(10)
        self.noise_slider.setEnabled(False)
        
        self.noise_value_label = QLabel("10")
        self.noise_value_label.setObjectName("ValueLabel")
        self.noise_value_label.setFixedWidth(30)
        
        noise_control_layout.addWidget(self.noise_slider)
        noise_control_layout.addWidget(self.noise_value_label)
        
        self.noise_checkbox.toggled.connect(self.noise_slider.setEnabled)
        self.noise_slider.valueChanged.connect(lambda v: self.noise_value_label.setText(str(v)))
        
        noise_layout.addWidget(self.noise_checkbox)
        noise_layout.addWidget(noise_control)
        
        section.add_item(noise_frame)
        
        # Smoothing filters
        section.add_item(QLabel("Smoothing Filter"))
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.setObjectName("ModernCombo")
        self.smoothing_combo.addItems([
            "None", "Average", "Weighted Average", "Median", 
            "Mode", "Bilateral", "Gaussian"
        ])
        section.add_item(self.smoothing_combo)
        
        # Kernel size
        kernel_frame = QFrame()
        kernel_layout = QHBoxLayout(kernel_frame)
        kernel_layout.setContentsMargins(0, 0, 0, 0)
        kernel_layout.setSpacing(8)
        
        kernel_layout.addWidget(QLabel("Kernel Size"))
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setObjectName("ModernSpin")
        self.kernel_spin.setRange(3, 15)
        self.kernel_spin.setValue(5)
        self.kernel_spin.setSingleStep(2)
        kernel_layout.addWidget(self.kernel_spin)
        
        section.add_item(kernel_frame)
        
        return section

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

    def process_image_realtime(self):
        """Process image in real-time with optimization"""
        if not self.image_path or self.is_processing:
            self.pending_update = True
            return
        self.start_processing_optimized()

    def save_image(self):
        """Save the processed image"""
        if self.current_processed_image:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Imagen Procesada", "",
                "PNG (*.png);;JPEG (*.jpg);;Todos los archivos (*)"
            )
            
            if file_path:
                success = self.current_processed_image.save(file_path)
                if success:
                    self.results_text.append(f"💾 Imagen guardada: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo guardar la imagen.")
        else:
            QMessageBox.information(self, "Información", "No hay imagen procesada para guardar.")

    def processing_started(self):
        """Called when processing starts"""
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.show()
        self.operation_label.setText("Procesando...")
        self.results_text.append("🚀 Procesando imagen...")

    def processing_finished(self):
        """Called when processing finishes"""
        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.progress_bar.hide()
        self.operation_label.setText("Listo")
        self.results_text.append("✅ Procesamiento completado")
        
        if self.image_processor:
            # Use deleteLater for proper Qt cleanup
            self.image_processor.deleteLater()
            self.image_processor = None

    def on_image_updated(self, q_image):
        """Called when processed image is ready"""
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.current_processed_image = q_image

    def start_processing(self):
        """Start image processing with current settings"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        # Clean up previous processor without waiting
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
                image_path=self.image_path,
                second_image_path=self.second_image_path,
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
            self.image_processor.image_updated.connect(self.on_image_updated)
            
            self.image_processor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar procesamiento: {str(e)}")

    def stop_processing(self):
        """Stop current processing"""
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            
            self.processing_finished()
            self.results_text.append("⏹️ Procesamiento detenido por el usuario")

    def calculate_automatic_parameters(self):
        """Calcular parámetros automáticos para la imagen actual"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        self.cleanup_temp_processors()
        
        temp_processor = ImageProcessor(
            image_path=self.image_path,
            filter_type='none',
            segmentation_type='none'
        )
        temp_processor.calculate_auto_params = True
        temp_processor.parameters_calculated.connect(self.apply_automatic_parameters)
        temp_processor.finished.connect(lambda: self.cleanup_temp_processor(temp_processor))
        
        self.temp_processors.append(temp_processor)
        temp_processor.start()

    def apply_automatic_parameters(self, params):
        """Aplicar parámetros calculados automáticamente"""
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
                self.bilateral_color_slider.setValue(int(params.get('bilateral_sigma_color', 80)))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'bilateral_d_spin') and self.bilateral_d_spin:
                self.bilateral_d_spin.setValue(params.get('bilateral_d', 9))
        except RuntimeError:
            pass
        
        # Apply optimal multi-otsu classes if available
        try:
            if hasattr(self, 'num_classes_spin') and self.num_classes_spin:
                optimal_classes = params.get('optimal_multi_otsu_classes', 3)
                self.num_classes_spin.setValue(optimal_classes)
                if optimal_classes != 3:
                    self.results_text.append(f"🎯 Clases óptimas para Multi-Otsu: {optimal_classes}")
        except RuntimeError:
            pass
        
        self.results_text.append("🤖 Parámetros calculados automáticamente")
        
        if old_timer_state or self.image_path:
            self.schedule_realtime_processing()

    def cleanup_temp_processors(self):
        """Clean up finished temporary processors"""
        for processor in self.temp_processors[:]:
            if processor and not processor.isRunning():
                self.temp_processors.remove(processor)

    def cleanup_temp_processor(self, processor):
        """Clean up a specific temporary processor"""
        if processor in self.temp_processors:
            self.temp_processors.remove(processor)
        # Use deleteLater for proper Qt cleanup
        processor.deleteLater()

    def on_filter_changed(self):
        """Called when any filter/segmentation setting changes"""
        self.update_dynamic_parameters()
        self.update_pipeline_visualization()  # Add this line
        self.schedule_realtime_processing()

    def schedule_realtime_processing(self):
        """Schedule real-time processing with debouncing"""
        if not self.image_path:
            return
        self.processing_timer.stop()
        self.processing_timer.start()
        # Also update pipeline when scheduling processing
        self.update_pipeline_visualization()

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            
            if self.original_image is not None:
                self.display_image(self.original_image)
                
                # Update UI state
                self.update_ui_state()
                
                # Update information
                h, w = self.original_image.shape[:2]
                info_text = f"Imagen: {os.path.basename(file_path)}\n"
                info_text += f"Tamaño: {w} × {h}\n"
                info_text += f"Canales: {self.original_image.shape[2] if len(self.original_image.shape) > 2 else 1}"
                self.image_info_label.setText(info_text)
                
                self.results_text.append(f"✓ Imagen cargada: {os.path.basename(file_path)}")
                
                # Update pipeline visualization
                self.update_pipeline_visualization()
                
                # Start real-time processing
                self.schedule_realtime_processing()

    def load_second_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Segunda Imagen", "", 
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos (*)"
        )
        
        if file_path:
            self.second_image_path = file_path
            self.second_image = cv2.imread(file_path)
            
            if self.second_image is not None:
                # Update UI state
                self.update_ui_state()
                self.results_text.append(f"✓ Segunda imagen: {os.path.basename(file_path)}")

    def display_image(self, img):
        if len(img.shape) == 2:
            h, w = img.shape
            q_image = QImage(img.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            q_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        # Usar QPixmap para la visualización
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def create_preprocessing_menu(self):
        section = MenuSection("Preprocessing")
        
        # Noise simulation
        noise_frame = QFrame()
        noise_layout = QVBoxLayout(noise_frame)
        noise_layout.setContentsMargins(0, 0, 0, 0)
        noise_layout.setSpacing(8)
        
        self.noise_checkbox = QCheckBox("Add Gaussian Noise")
        self.noise_checkbox.setObjectName("ModernCheckbox")
        
        noise_control = QFrame()
        noise_control_layout = QHBoxLayout(noise_control)
        noise_control_layout.setContentsMargins(0, 0, 0, 0)
        noise_control_layout.setSpacing(8)
        
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setObjectName("ModernSlider")
        self.noise_slider.setRange(0, 50)
        self.noise_slider.setValue(10)
        self.noise_slider.setEnabled(False)
        
        self.noise_value_label = QLabel("10")
        self.noise_value_label.setObjectName("ValueLabel")
        self.noise_value_label.setFixedWidth(30)
        
        noise_control_layout.addWidget(self.noise_slider)
        noise_control_layout.addWidget(self.noise_value_label)
        
        self.noise_checkbox.toggled.connect(self.noise_slider.setEnabled)
        self.noise_slider.valueChanged.connect(lambda v: self.noise_value_label.setText(str(v)))
        
        noise_layout.addWidget(self.noise_checkbox)
        noise_layout.addWidget(noise_control)
        
        section.add_item(noise_frame)
        
        # Smoothing filters
        section.add_item(QLabel("Smoothing Filter"))
        self.smoothing_combo = QComboBox()
        self.smoothing_combo.setObjectName("ModernCombo")
        self.smoothing_combo.addItems([
            "None", "Average", "Weighted Average", "Median", 
            "Mode", "Bilateral", "Gaussian"
        ])
        section.add_item(self.smoothing_combo)
        
        # Kernel size
        kernel_frame = QFrame()
        kernel_layout = QHBoxLayout(kernel_frame)
        kernel_layout.setContentsMargins(0, 0, 0, 0)
        kernel_layout.setSpacing(8)
        
        kernel_layout.addWidget(QLabel("Kernel Size"))
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setObjectName("ModernSpin")
        self.kernel_spin.setRange(3, 15)
        self.kernel_spin.setValue(5)
        self.kernel_spin.setSingleStep(2)
        kernel_layout.addWidget(self.kernel_spin)
        
        section.add_item(kernel_frame)
        
        return section

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

    def process_image_realtime(self):
        """Process image in real-time with optimization"""
        if not self.image_path or self.is_processing:
            self.pending_update = True
            return
        self.start_processing_optimized()

    def save_image(self):
        """Save the processed image"""
        if self.current_processed_image:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Imagen Procesada", "",
                "PNG (*.png);;JPEG (*.jpg);;Todos los archivos (*)"
            )
            
            if file_path:
                success = self.current_processed_image.save(file_path)
                if success:
                    self.results_text.append(f"💾 Imagen guardada: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo guardar la imagen.")
        else:
            QMessageBox.information(self, "Información", "No hay imagen procesada para guardar.")

    def processing_started(self):
        """Called when processing starts"""
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.show()
        self.operation_label.setText("Procesando...")
        self.results_text.append("🚀 Procesando imagen...")

    def processing_finished(self):
        """Called when processing finishes"""
        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.progress_bar.hide()
        self.operation_label.setText("Listo")
        self.results_text.append("✅ Procesamiento completado")
        
        if self.image_processor:
            # Use deleteLater for proper Qt cleanup
            self.image_processor.deleteLater()
            self.image_processor = None

    def on_image_updated(self, q_image):
        """Called when processed image is ready"""
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.current_processed_image = q_image

    def start_processing(self):
        """Start image processing with current settings"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        # Clean up previous processor without waiting
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
                image_path=self.image_path,
                second_image_path=self.second_image_path,
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
            self.image_processor.image_updated.connect(self.on_image_updated)
            
            self.image_processor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar procesamiento: {str(e)}")

    def stop_processing(self):
        """Stop current processing"""
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            
            self.processing_finished()
            self.results_text.append("⏹️ Procesamiento detenido por el usuario")

    def calculate_automatic_parameters(self):
        """Calcular parámetros automáticos para la imagen actual"""
        if not self.image_path:
            QMessageBox.warning(self, "Advertencia", "Carga una imagen primero.")
            return
        
        self.cleanup_temp_processors()
        
        temp_processor = ImageProcessor(
            image_path=self.image_path,
            filter_type='none',
            segmentation_type='none'
        )
        temp_processor.calculate_auto_params = True
        temp_processor.parameters_calculated.connect(self.apply_automatic_parameters)
        temp_processor.finished.connect(lambda: self.cleanup_temp_processor(temp_processor))
        
        self.temp_processors.append(temp_processor)
        temp_processor.start()

    def apply_automatic_parameters(self, params):
        """Aplicar parámetros calculados automáticamente"""
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
                self.bilateral_color_slider.setValue(int(params.get('bilateral_sigma_color', 80)))
        except RuntimeError:
            pass
            
        try:
            if hasattr(self, 'bilateral_d_spin') and self.bilateral_d_spin:
                self.bilateral_d_spin.setValue(params.get('bilateral_d', 9))
        except RuntimeError:
            pass
        
        # Apply optimal multi-otsu classes if available
        try:
            if hasattr(self, 'num_classes_spin') and self.num_classes_spin:
                optimal_classes = params.get('optimal_multi_otsu_classes', 3)
                self.num_classes_spin.setValue(optimal_classes)
                if optimal_classes != 3:
                    self.results_text.append(f"🎯 Clases óptimas para Multi-Otsu: {optimal_classes}")
        except RuntimeError:
            pass
        
        self.results_text.append("🤖 Parámetros calculados automáticamente")
        
        if old_timer_state or self.image_path:
            self.schedule_realtime_processing()

    def cleanup_temp_processors(self):
        """Clean up finished temporary processors"""
        for processor in self.temp_processors[:]:
            if processor and not processor.isRunning():
                self.temp_processors.remove(processor)

    def cleanup_temp_processor(self, processor):
        """Clean up a specific temporary processor"""
        if processor in self.temp_processors:
            self.temp_processors.remove(processor)
        # Use deleteLater for proper Qt cleanup
        processor.deleteLater()

    def on_filter_changed(self):
        """Called when any filter/segmentation setting changes"""
        self.update_dynamic_parameters()
        self.update_pipeline_visualization()  # Add this line
        self.schedule_realtime_processing()

    def schedule_realtime_processing(self):
        """Schedule real-time processing with debouncing"""
        if not self.image_path:
            return
        self.processing_timer.stop()
        self.processing_timer.start()
        # Also update pipeline when scheduling processing
        self.update_pipeline_visualization()

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
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Botón principal
        self.process_button = QPushButton("🚀 Procesar")
        self.process_button.setObjectName("ProcessButton")
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setEnabled(False)
        layout.addWidget(self.process_button)
        
        # Botones secundarios
        buttons_layout = QHBoxLayout()
        
        self.stop_button = QPushButton("⏹")
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedWidth(40)
        
        self.save_button = QPushButton("💾")
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        self.save_button.setFixedWidth(40)
        
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        
        return layout

    def on_parameter_changed(self):
        """Called when any parameter changes to trigger real-time processing"""
        self.update_pipeline_visualization()
        self.schedule_realtime_processing()

    def apply_two_image_operation(self):
        """Aplicar operación entre dos imágenes"""
        if not self.image_path or not self.second_image_path:
            QMessageBox.warning(self, "Advertencia", "Necesitas cargar dos imágenes.")
            return
        
        # Clean up previous processor without waiting
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            self.image_processor = None

        operation = None
        if self.arithmetic_combo.currentText() != "Ninguna":
            operation_map = {
                "Suma": "suma",
                "Resta": "resta", 
                "Multiplicación": "multiplicacion",
                "División": "division",
                "Promedio": "promedio",
                "Diferencia": "diferencia"
            }
            operation = operation_map.get(self.arithmetic_combo.currentText())
        elif self.logical_combo.currentText() != "Ninguna":
            operation_map = {
                "AND": "and",
                "OR": "or",
                "XOR": "xor",
                "NOT": "not"
            }
            operation = operation_map.get(self.logical_combo.currentText())
        
        if not operation:
            QMessageBox.warning(self, "Advertencia", "Selecciona una operación.")
            return
        
        self.image_processor = ImageProcessor(
            image_path=self.image_path,
            second_image_path=self.second_image_path,
            operation_type=operation,
            filter_type='none',
            segmentation_type='none'
        )
        
        self.image_processor.started.connect(self.processing_started)
        self.image_processor.finished.connect(self.two_image_operation_finished)
        self.image_processor.image_updated.connect(self.on_image_updated)
        
        self.image_processor.start()

    def two_image_operation_finished(self):
        """Llamado cuando termina la operación entre dos imágenes"""
        self.processing_finished()
        
        self.operations_widget.setVisible(False)
        self.arithmetic_combo.setCurrentIndex(0)
        self.logical_combo.setCurrentIndex(0)
        
        self.second_image_path = None
        self.second_image = None
        
        self.update_ui_state()
        self.results_text.append("✓ Operación completada. Resultado como imagen principal.")

    def start_processing_optimized(self):
        """Optimized processing for real-time updates"""
        if self.is_processing:
            return
        self.is_processing = True
        
        # Clean up previous processor without waiting
        if self.image_processor:
            if self.image_processor.isRunning():
                self.image_processor.stop()
                self.image_processor.quit()
            self.image_processor = None

        # Check if we still have a valid image path
        if not self.image_path:
            self.is_processing = False
            return
        
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
            # Check if noise controls still exist before accessing
            noise_level = 0
            apply_noise = False
            try:
                if hasattr(self, 'noise_checkbox') and self.noise_checkbox and not self.noise_checkbox.isHidden():
                    apply_noise = self.noise_checkbox.isChecked()
                if hasattr(self, 'noise_slider') and self.noise_slider and not self.noise_slider.isHidden() and apply_noise:
                    noise_level = self.noise_slider.value()
            except RuntimeError:
                pass
            
            self.image_processor = ImageProcessor(
                image_path=self.image_path,
                filter_type=filter_type,
                filter_params=filter_params,
                segmentation_type=self.get_selected_segmentation(),
                segmentation_params=self.get_segmentation_parameters(),
                noise_level=noise_level,
                apply_noise=apply_noise
            )
            
            self.image_processor.finished.connect(self.realtime_processing_finished)
            self.image_processor.image_updated.connect(self.on_image_updated_realtime)
            self.image_processor.start()
            
        except Exception as e:
            print(f"Error in real-time processing: {e}")
            self.is_processing = False

    def on_image_updated_realtime(self, q_image):
        """Handle real-time image updates with optimization"""
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.current_processed_image = q_image

    def realtime_processing_finished(self):
        """Called when real-time processing finishes"""
        self.is_processing = False
        if self.image_processor:
            # Use deleteLater for proper Qt cleanup
            self.image_processor.deleteLater()
            self.image_processor = None
        if self.pending_update:
            self.pending_update = False
            # Use a short timer to avoid immediate restart
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, self.schedule_realtime_processing)

    def update_dynamic_parameters(self):
        """Actualizar parámetros dinámicos según selección"""
        # Check if the layout still exists
        if not hasattr(self, 'dynamic_params_layout') or not self.dynamic_params_layout:
            return
            
        # Limpiar parámetros anteriores
        for i in reversed(range(self.dynamic_params_layout.count())):
            if i > 0:  # Mantener el botón automático
                child = self.dynamic_params_layout.takeAt(i)
                if child.widget():
                    child.widget().deleteLater()
        
        # Obtener filtro/segmentación actual
        current_filter = self.get_selected_filter()
        current_edge = self.get_selected_edge_detection()
        current_morph = self.get_selected_morphological()
        current_seg = self.get_selected_segmentation()
        
        # Añadir parámetros según el tipo
        if current_filter in ['averaging', 'median', 'mode'] or current_morph != 'none':
            self.add_kernel_size_param()
        
        if current_filter == 'gaussian':
            self.add_kernel_size_param()
            self.add_gaussian_params()
        
        if current_filter == 'bilateral':
            self.add_bilateral_params()
        
        if current_edge == 'canny':
            self.add_canny_params()
        
        if current_seg == 'multi_otsu':
            self.add_multi_otsu_params()
        
        if current_seg == 'band':
            self.add_band_threshold_params()
        
        if current_seg == 'adaptive':
            self.add_adaptive_params()

    def add_kernel_size_param(self):
        """Añadir control de tamaño de kernel"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Kernel:"))
        
        self.kernel_spin = QSpinBox()
        self.kernel_spin.setRange(3, 15)
        self.kernel_spin.setValue(5)
        self.kernel_spin.setSingleStep(2)
        self.kernel_spin.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.kernel_spin)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.dynamic_params_layout.addWidget(widget)

    def add_bilateral_params(self):
        """Añadir parámetros para filtro bilateral"""
        # Parámetro d
        d_layout = QHBoxLayout()
        d_layout.addWidget(QLabel("Diámetro:"))
        self.bilateral_d_spin = QSpinBox()
        self.bilateral_d_spin.setRange(5, 15)
        self.bilateral_d_spin.setValue(9)
        self.bilateral_d_spin.valueChanged.connect(self.on_parameter_changed)
        d_layout.addWidget(self.bilateral_d_spin)
        
        d_widget = QWidget()
        d_widget.setLayout(d_layout)
        self.dynamic_params_layout.addWidget(d_widget)
        
        # Sigma Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Sigma Color:"))
        self.bilateral_color_slider = QSlider(Qt.Orientation.Horizontal)
        self.bilateral_color_slider.setRange(10, 200)
        self.bilateral_color_slider.setValue(80)
        self.bilateral_color_label = QLabel("80")
        color_layout.addWidget(self.bilateral_color_slider)
        color_layout.addWidget(self.bilateral_color_label)
        
        self.bilateral_color_slider.valueChanged.connect(
            lambda v: (
                self.bilateral_color_label.setText(str(v)),
                self.on_parameter_changed()
            )
        )
        
        color_widget = QWidget()
        color_widget.setLayout(color_layout)
        self.dynamic_params_layout.addWidget(color_widget)

    def add_canny_params(self):
        """Añadir parámetros para Canny"""
        # Umbral bajo
        low_layout = QHBoxLayout()
        low_layout.addWidget(QLabel("Bajo:"))
        self.canny_low_slider = QSlider(Qt.Orientation.Horizontal)
        self.canny_low_slider.setRange(10, 200)
        self.canny_low_slider.setValue(50)
        self.canny_low_label = QLabel("50")
        low_layout.addWidget(self.canny_low_slider)
        low_layout.addWidget(self.canny_low_label)
        
        self.canny_low_slider.valueChanged.connect(
            lambda v: (
                self.canny_low_label.setText(str(v)),
                self.on_parameter_changed()
            )
        )
        
        # Umbral alto
        high_layout = QHBoxLayout()
        high_layout.addWidget(QLabel("Alto:"))
        self.canny_high_slider = QSlider(Qt.Orientation.Horizontal)
        self.canny_high_slider.setRange(50, 400)
        self.canny_high_slider.setValue(150)
        self.canny_high_label = QLabel("150")
        high_layout.addWidget(self.canny_high_slider)
        high_layout.addWidget(self.canny_high_label)
        
        self.canny_high_slider.valueChanged.connect(
            lambda v: (
                self.canny_high_label.setText(str(v)),
                self.on_parameter_changed()
            )
        )
        
        low_widget = QWidget()
        low_widget.setLayout(low_layout)
        high_widget = QWidget()
        high_widget.setLayout(high_layout)
        
        self.dynamic_params_layout.addWidget(low_widget)
        self.dynamic_params_layout.addWidget(high_widget)

    def add_multi_otsu_params(self):
        """Añadir parámetros para Multi-Otsu"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Clases:"))
        self.num_classes_spin = QSpinBox()
        self.num_classes_spin.setRange(2, 5)
        self.num_classes_spin.setValue(3)
        self.num_classes_spin.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.num_classes_spin)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.dynamic_params_layout.addWidget(widget)

    def add_band_threshold_params(self):
        """Añadir parámetros para umbral de banda"""
        # Banda baja
        low_layout = QHBoxLayout()
        low_layout.addWidget(QLabel("Bajo:"))
        self.band_low_slider = QSlider(Qt.Orientation.Horizontal)
        self.band_low_slider.setRange(0, 255)
        self.band_low_slider.setValue(100)
        self.band_low_label = QLabel("100")
        low_layout.addWidget(self.band_low_slider)
        low_layout.addWidget(self.band_low_label)
        
        self.band_low_slider.valueChanged.connect(
            lambda v: (
                self.band_low_label.setText(str(v)),
                self.on_parameter_changed()
            )
        )
        
        # Banda alta
        high_layout = QHBoxLayout()
        high_layout.addWidget(QLabel("Alto:"))
        self.band_high_slider = QSlider(Qt.Orientation.Horizontal)
        self.band_high_slider.setRange(0, 255)
        self.band_high_slider.setValue(200)
        self.band_high_label = QLabel("200")
        high_layout.addWidget(self.band_high_slider)
        high_layout.addWidget(self.band_high_label)
        
        self.band_high_slider.valueChanged.connect(
            lambda v: (
                self.band_high_label.setText(str(v)),
                self.on_parameter_changed()
            )
        )
        
        low_widget = QWidget()
        low_widget.setLayout(low_layout)
        high_widget = QWidget()
        high_widget.setLayout(high_layout)
        
        self.dynamic_params_layout.addWidget(low_widget)
        self.dynamic_params_layout.addWidget(high_widget)

    def add_adaptive_params(self):
        """Añadir parámetros para umbralización adaptativa"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Tamaño Bloque:"))
        self.adaptive_block_slider = QSlider(Qt.Orientation.Horizontal)
        self.adaptive_block_slider.setRange(3, 21)
        self.adaptive_block_slider.setValue(11)
        self.adaptive_block_slider.valueChanged.connect(self.ensure_odd_block_size_realtime)
        self.adaptive_block_label = QLabel("11")
        layout.addWidget(self.adaptive_block_slider)
        layout.addWidget(self.adaptive_block_label)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.dynamic_params_layout.addWidget(widget)

    def ensure_odd_block_size_realtime(self, value):
        """Asegurar que el tamaño de bloque sea impar y trigger real-time update"""
        if value % 2 == 0:
            value += 1
            self.adaptive_block_slider.setValue(value)
        self.adaptive_block_label.setText(str(value))
        self.on_parameter_changed()

    def add_gaussian_params(self):
        """Añadir parámetros para filtro gaussiano"""
        # Sigma parameter
        sigma_layout = QHBoxLayout()
        sigma_layout.addWidget(QLabel("Sigma:"))
        self.gaussian_sigma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gaussian_sigma_slider.setRange(1, 50)
        self.gaussian_sigma_slider.setValue(10)  # Default 1.0
        self.gaussian_sigma_label = QLabel("1.0")
        sigma_layout.addWidget(self.gaussian_sigma_slider)
        sigma_layout.addWidget(self.gaussian_sigma_label)
        
        self.gaussian_sigma_slider.valueChanged.connect(
            lambda v: (
                self.gaussian_sigma_label.setText(str(v / 10.0)),
                self.on_parameter_changed()
            )
        )
        
        sigma_widget = QWidget()
        sigma_widget.setLayout(sigma_layout)
        self.dynamic_params_layout.addWidget(sigma_widget)
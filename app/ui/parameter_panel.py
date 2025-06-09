from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
                             QPushButton, QFrame, QGroupBox, QCheckBox, QSpinBox,
                             QGridLayout, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
import json
import os

class ParameterSlider(QFrame):
    """Custom slider widget with label and value display."""
    
    valueChanged = pyqtSignal(int)
    
    def __init__(self, name, min_val, max_val, default_val, unit=""):
        super().__init__()
        self.name = name
        self.unit = unit
        self.setup_ui(min_val, max_val, default_val)
        
    def setup_ui(self, min_val, max_val, default_val):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        self.label = QLabel(f"{self.name}:")
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default_val)
        self.slider.valueChanged.connect(self.on_value_changed)
        layout.addWidget(self.slider)
        
        # Value display
        self.value_label = QLabel(f"{default_val}{self.unit}")
        self.value_label.setMinimumWidth(60)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("QLabel { border: 1px solid #ccc; padding: 2px; }")
        layout.addWidget(self.value_label)
        
    def on_value_changed(self, value):
        self.value_label.setText(f"{value}{self.unit}")
        self.valueChanged.emit(value)
        
    def get_value(self):
        return self.slider.value()
        
    def set_value(self, value):
        self.slider.setValue(value)

class ParameterPanel(QFrame):
    """Panel for manual parameter adjustment."""
    
    parametersChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("parameter_panel")
        self.manual_mode = False
        self.setup_ui()
        self.load_default_parameters()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Manual mode toggle
        self.manual_checkbox = QCheckBox("Modo Manual")
        self.manual_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border: 2px solid #27ae60;
            }
        """)
        self.manual_checkbox.toggled.connect(self.toggle_manual_mode)
        header_layout.addWidget(self.manual_checkbox)
        
        header_layout.addStretch()
        
        # Control buttons
        self.reset_button = QPushButton("🔄 Resetear")
        self.reset_button.setEnabled(False)
        self.reset_button.clicked.connect(self.reset_parameters)
        
        self.save_button = QPushButton("💾 Guardar Config")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_configuration)
        
        self.load_button = QPushButton("📁 Cargar Config")
        self.load_button.clicked.connect(self.load_configuration)
        
        header_layout.addWidget(self.reset_button)
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.load_button)
        
        main_layout.addLayout(header_layout)
        
        # Parameters groups
        self.create_threshold_group(main_layout)
        self.create_morphology_group(main_layout)
        self.create_filtering_group(main_layout)
        
        # Apply button
        self.apply_button = QPushButton("✨ Aplicar Cambios")
        self.apply_button.setObjectName("process_button")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_parameters)
        main_layout.addWidget(self.apply_button)
        
        # Set initial state
        self.set_enabled(False)
        
    def create_threshold_group(self, parent_layout):
        """Create thresholding parameters group."""
        group = QGroupBox("Parámetros de Umbralización")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(group)
        
        self.block_size_slider = ParameterSlider("Tamaño Bloque", 3, 51, 21)
        self.block_size_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.block_size_slider)
        
        self.c_value_slider = ParameterSlider("Valor C", 0, 20, 8)
        self.c_value_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.c_value_slider)
        
        parent_layout.addWidget(group)
        
    def create_morphology_group(self, parent_layout):
        """Create morphological operations parameters group."""
        group = QGroupBox("Operaciones Morfológicas")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(group)
        
        self.open_kernel_slider = ParameterSlider("Kernel Apertura", 1, 9, 3, "px")
        self.open_kernel_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.open_kernel_slider)
        
        self.open_iterations_slider = ParameterSlider("Iteraciones Apertura", 1, 5, 1)
        self.open_iterations_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.open_iterations_slider)
        
        self.close_kernel_w_slider = ParameterSlider("Ancho Kernel Cierre", 1, 15, 5, "px")
        self.close_kernel_w_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.close_kernel_w_slider)
        
        self.close_kernel_h_slider = ParameterSlider("Alto Kernel Cierre", 1, 10, 2, "px")
        self.close_kernel_h_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.close_kernel_h_slider)
        
        parent_layout.addWidget(group)
        
    def create_filtering_group(self, parent_layout):
        """Create geometric filtering parameters group."""
        group = QGroupBox("Filtrado Geométrico")
        group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout = QVBoxLayout(group)
        
        self.min_area_slider = ParameterSlider("Área Mínima", 100, 5000, 1200, "px²")
        self.min_area_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.min_area_slider)
        
        self.max_area_slider = ParameterSlider("Área Máxima", 10000, 100000, 40000, "px²")
        self.max_area_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.max_area_slider)
        
        self.min_aspect_slider = ParameterSlider("Aspecto Mín", 10, 100, 40, "%")
        self.min_aspect_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.min_aspect_slider)
        
        self.max_aspect_slider = ParameterSlider("Aspecto Máx", 100, 500, 300, "%")
        self.max_aspect_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.max_aspect_slider)
        
        self.min_width_slider = ParameterSlider("Ancho Mínimo", 10, 100, 30, "px")
        self.min_width_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.min_width_slider)
        
        self.max_width_slider = ParameterSlider("Ancho Máximo", 50, 500, 200, "px")
        self.max_width_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.max_width_slider)
        
        self.extent_threshold_slider = ParameterSlider("Umbral Extensión", 10, 80, 35, "%")
        self.extent_threshold_slider.valueChanged.connect(self.on_parameter_changed)
        layout.addWidget(self.extent_threshold_slider)
        
        parent_layout.addWidget(group)
        
    def toggle_manual_mode(self, enabled):
        """Toggle manual mode on/off."""
        self.manual_mode = enabled
        self.set_enabled(enabled)
        
        if enabled:
            self.setStyleSheet("""
                QFrame#parameter_panel {
                    background-color: #e8f5e8;
                    border: 2px solid #27ae60;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#parameter_panel {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                }
            """)
            
    def set_enabled(self, enabled):
        """Enable/disable all parameter controls."""
        # Enable/disable all sliders
        self.block_size_slider.setEnabled(enabled)
        self.c_value_slider.setEnabled(enabled)
        self.open_kernel_slider.setEnabled(enabled)
        self.open_iterations_slider.setEnabled(enabled)
        self.close_kernel_w_slider.setEnabled(enabled)
        self.close_kernel_h_slider.setEnabled(enabled)
        self.min_area_slider.setEnabled(enabled)
        self.max_area_slider.setEnabled(enabled)
        self.min_aspect_slider.setEnabled(enabled)
        self.max_aspect_slider.setEnabled(enabled)
        self.min_width_slider.setEnabled(enabled)
        self.max_width_slider.setEnabled(enabled)
        self.extent_threshold_slider.setEnabled(enabled)
        
        # Enable/disable buttons
        self.reset_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.apply_button.setEnabled(enabled)
        
    def on_parameter_changed(self):
        """Handle parameter value changes."""
        if self.manual_mode:
            # Enable apply button when parameters change
            self.apply_button.setEnabled(True)
            self.apply_button.setText("✨ Aplicar Cambios*")
            
    def apply_parameters(self):
        """Apply current parameters."""
        if self.manual_mode:
            try:
                params = self.get_current_parameters()
                self.parametersChanged.emit(params)
                self.apply_button.setText("✨ Aplicar Cambios")
            except Exception as e:
                print(f"Error applying parameters: {e}")

    def get_current_parameters(self):
        """Get current parameter values."""
        return {
            'block_size': self.block_size_slider.get_value(),
            'c_value': self.c_value_slider.get_value(),
            'open_kernel': self.open_kernel_slider.get_value(),
            'open_iterations': self.open_iterations_slider.get_value(),
            'close_kernel_w': self.close_kernel_w_slider.get_value(),
            'close_kernel_h': self.close_kernel_h_slider.get_value(),
            'min_area': self.min_area_slider.get_value(),
            'max_area': self.max_area_slider.get_value(),
            'min_aspect': self.min_aspect_slider.get_value() / 100.0,  # Convert percentage
            'max_aspect': self.max_aspect_slider.get_value() / 100.0,  # Convert percentage
            'min_width': self.min_width_slider.get_value(),
            'max_width': self.max_width_slider.get_value(),
            'extent_threshold': self.extent_threshold_slider.get_value() / 100.0  # Convert percentage
        }
        
    def set_parameters(self, params):
        """Set parameter values."""
        self.block_size_slider.set_value(params.get('block_size', 21))
        self.c_value_slider.set_value(params.get('c_value', 8))
        self.open_kernel_slider.set_value(params.get('open_kernel', 3))
        self.open_iterations_slider.set_value(params.get('open_iterations', 1))
        self.close_kernel_w_slider.set_value(params.get('close_kernel_w', 5))
        self.close_kernel_h_slider.set_value(params.get('close_kernel_h', 2))
        self.min_area_slider.set_value(params.get('min_area', 1200))
        self.max_area_slider.set_value(params.get('max_area', 40000))
        self.min_aspect_slider.set_value(int(params.get('min_aspect', 0.4) * 100))
        self.max_aspect_slider.set_value(int(params.get('max_aspect', 3.0) * 100))
        self.min_width_slider.set_value(params.get('min_width', 30))
        self.max_width_slider.set_value(params.get('max_width', 200))
        self.extent_threshold_slider.set_value(int(params.get('extent_threshold', 0.35) * 100))
        
    def load_default_parameters(self):
        """Load default parameter values."""
        default_params = {
            'block_size': 21,
            'c_value': 11,
            'open_kernel': 4,
            'open_iterations': 2,
            'close_kernel_w': 7,
            'close_kernel_h': 5,
            'min_area': 1439,
            'max_area': 76620,
            'min_aspect': 0.2,  # Stored as float, converted to % for slider
            'max_aspect': 5.0,  # Stored as float, converted to % for slider
            'min_width': 20,
            'max_width': 350,
            'extent_threshold': 0.2  # Stored as float, converted to % for slider
        }
        self.set_parameters(default_params)
        
    def reset_parameters(self):
        """Reset parameters to default values."""
        reply = QMessageBox.question(self, "Confirmar Reset", 
                                     "¿Desea resetear todos los parámetros a sus valores por defecto?",
                                     QMessageBox.Yes | QMessageBox.No, 
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.load_default_parameters()
            self.on_parameter_changed()
            
    def save_configuration(self):
        """Save current configuration to file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Configuración", "", 
            "Archivos JSON (*.json);;Todos los archivos (*)",
            options=options
        )
        
        if file_path:
            try:
                config = {
                    'parameters': self.get_current_parameters(),
                    'version': '1.0',
                    'description': 'Configuración de parámetros del sistema de conteo de coches'
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(self, "Éxito", 
                                      f"Configuración guardada en:\n{file_path}")
                                      
                # Also save to cache
                self.save_to_cache(config['parameters'])
                
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Error al guardar configuración:\n{str(e)}")
                
    def load_configuration(self):
        """Load configuration from file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Cargar Configuración", "", 
            "Archivos JSON (*.json);;Todos los archivos (*)",
            options=options
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                if 'parameters' in config:
                    self.set_parameters(config['parameters'])
                    self.on_parameter_changed()
                    QMessageBox.information(self, "Éxito", 
                                          "Configuración cargada correctamente")
                else:
                    QMessageBox.warning(self, "Advertencia", 
                                      "Archivo de configuración no válido")
                                      
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"Error al cargar configuración:\n{str(e)}")
                                   
    def save_to_cache(self, params):
        """Save parameters to cache file."""
        try:
            cache_dir = os.path.join(os.path.expanduser("~"), ".car_counter_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_file = os.path.join(cache_dir, "last_config.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(params, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save to cache: {e}")
            
    def load_from_cache(self):
        """Load parameters from cache file."""
        try:
            cache_file = os.path.join(os.path.expanduser("~"), ".car_counter_cache", "last_config.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    params = json.load(f)
                return params
        except Exception as e:
            print(f"Warning: Could not load from cache: {e}")
        return None
        
    def is_manual_mode(self):
        """Check if manual mode is enabled."""
        return self.manual_mode

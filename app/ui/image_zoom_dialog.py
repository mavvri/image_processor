from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QScrollArea, QSplitter, QWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont

class ZoomableImageLabel(QLabel):
    """Enhanced image label with zoom and pan capabilities."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
            }
        """)
        
        # Initialize zoom properties
        self._scale_factor = 1.0
        self.max_scale = 5.0
        self.min_scale = 0.1
        self._original_pixmap = None
        self._opacity = 1.0
        
        # Animation setup
        self._setup_animations()
        
    def _setup_animations(self):
        """Setup zoom and fade animations."""
        try:
            self._scale_animation = QPropertyAnimation(self, b"scale_factor")
            self._scale_animation.setDuration(300)
            self._scale_animation.setEasingCurve(QEasingCurve.OutCubic)
            self._scale_animation.valueChanged.connect(self._update_display)
            
            self._fade_animation = QPropertyAnimation(self, b"opacity")
            self._fade_animation.setDuration(200)
            self._fade_animation.setEasingCurve(QEasingCurve.InOutCubic)
        except Exception as e:
            print(f"Warning: Could not setup animations: {e}")
    
    def get_scale_factor(self):
        return self._scale_factor
        
    def set_scale_factor(self, value):
        self._scale_factor = max(self.min_scale, min(self.max_scale, value))
        self._update_display()
        
    scale_factor = pyqtProperty(float, get_scale_factor, set_scale_factor)
    
    def get_opacity(self):
        return self._opacity
        
    def set_opacity(self, value):
        self._opacity = value
        self.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(44, 62, 80, {int(value * 255)});
                border: 2px solid rgba(52, 73, 94, {int(value * 255)});
                border-radius: 8px;
            }}
        """)
        
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def set_image(self, pixmap):
        """Set the image with fade-in animation."""
        try:
            if pixmap and not pixmap.isNull():
                self._original_pixmap = pixmap
                self._scale_factor = 1.0
                self._update_display()
                
                # Fade in animation if available
                if hasattr(self, '_fade_animation'):
                    self._fade_animation.setStartValue(0.0)
                    self._fade_animation.setEndValue(1.0)
                    self._fade_animation.start()
        except Exception as e:
            print(f"Error setting image: {e}")
            
    def _update_display(self):
        """Update the displayed image with current scale."""
        try:
            if self._original_pixmap:
                scaled_size = self._original_pixmap.size() * self._scale_factor
                scaled_pixmap = self._original_pixmap.scaled(
                    scaled_size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def zoom_in(self):
        """Animate zoom in."""
        try:
            target_scale = min(self._scale_factor * 1.5, self.max_scale)
            self._animate_to_scale(target_scale)
        except Exception as e:
            print(f"Error zooming in: {e}")
        
    def zoom_out(self):
        """Animate zoom out."""
        try:
            target_scale = max(self._scale_factor / 1.5, self.min_scale)
            self._animate_to_scale(target_scale)
        except Exception as e:
            print(f"Error zooming out: {e}")
        
    def fit_to_window(self):
        """Animate to fit image in window."""
        try:
            self._animate_to_scale(1.0)
        except Exception as e:
            print(f"Error fitting to window: {e}")
        
    def _animate_to_scale(self, target_scale):
        """Animate to target scale factor."""
        try:
            if hasattr(self, '_scale_animation'):
                self._scale_animation.setStartValue(self._scale_factor)
                self._scale_animation.setEndValue(target_scale)
                self._scale_animation.start()
            else:
                # Fallback: direct scale setting
                self.set_scale_factor(target_scale)
        except Exception as e:
            print(f"Error animating scale: {e}")
            # Fallback: direct scale setting
            self.set_scale_factor(target_scale)
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        try:
            # Get scroll direction
            angle_delta = event.angleDelta().y()
            if angle_delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        except Exception as e:
            print(f"Error in wheel event: {e}")

class ImageComparisonWidget(QWidget):
    """Widget for comparing two images side by side with synchronized zoom."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the comparison UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title section
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(52, 152, 219, 0.1), stop:1 rgba(46, 204, 113, 0.1));
                border-radius: 8px;
                padding: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        
        self.comparison_title = QLabel("🔍 Vista Comparativa de Imágenes")
        self.comparison_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        title_layout.addWidget(self.comparison_title)
        title_layout.addStretch()
        
        layout.addWidget(title_frame)
        
        # Image comparison section
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                width: 3px;
                border-radius: 1px;
            }
        """)
        
        # Original image section
        original_container = self._create_image_container(
            "🖼️ Imagen Original", 
            "La imagen tal como se cargó inicialmente"
        )
        self.original_image = ZoomableImageLabel()
        original_container.layout().addWidget(self.original_image)
        
        # Current step image section
        current_container = self._create_image_container(
            "🔄 Paso Actual", 
            "Resultado del procesamiento en el paso seleccionado"
        )
        self.current_image = ZoomableImageLabel()
        current_container.layout().addWidget(self.current_image)
        
        self.splitter.addWidget(original_container)
        self.splitter.addWidget(current_container)
        self.splitter.setSizes([400, 400])
        
        layout.addWidget(self.splitter)
        
        # Control buttons
        self._setup_control_buttons(layout)
        
    def _create_image_container(self, title, description):
        """Create a container for an image with title and description."""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(52, 152, 219, 0.1), stop:1 rgba(52, 152, 219, 0.05));
                border-radius: 6px;
            }
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                padding: 0px 8px;
                font-style: italic;
            }
        """)
        desc_label.setWordWrap(True)
        
        container_layout.addWidget(title_label)
        container_layout.addWidget(desc_label)
        
        return container
        
    def _setup_control_buttons(self, parent_layout):
        """Setup zoom control buttons."""
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(10)
        
        # Zoom control label
        zoom_label = QLabel("🔍 Controles de Zoom:")
        zoom_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        controls_layout.addWidget(zoom_label)
        
        # Zoom buttons
        self.zoom_in_btn = QPushButton("🔍+ Acercar")
        self.zoom_in_btn.setToolTip("Acercar imagen (Ctrl++)")
        
        self.zoom_out_btn = QPushButton("🔍- Alejar")
        self.zoom_out_btn.setToolTip("Alejar imagen (Ctrl+-)")
        
        self.fit_btn = QPushButton("📐 Ajustar")
        self.fit_btn.setToolTip("Ajustar a ventana (Ctrl+0)")
        
        self.sync_zoom_btn = QPushButton("🔗 Sincronizar Zoom")
        self.sync_zoom_btn.setCheckable(True)
        self.sync_zoom_btn.setChecked(True)
        self.sync_zoom_btn.setToolTip("Sincronizar zoom entre imágenes")
        
        # Style buttons
        button_style = """
            QPushButton {
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 6px;
                background-color: #ffffff;
                border: 2px solid #e9ecef;
            }
            QPushButton:hover {
                background-color: #3498db;
                border-color: #3498db;
                color: white;
            }
            QPushButton:checked {
                background-color: #27ae60;
                border-color: #27ae60;
                color: white;
            }
        """
        
        for btn in [self.zoom_in_btn, self.zoom_out_btn, self.fit_btn, self.sync_zoom_btn]:
            btn.setStyleSheet(button_style) # Apply generic style first
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()
        
        # Info label
        info_label = QLabel("💡 Tip: Use la rueda del mouse para zoom")
        info_label.setStyleSheet("color: #6c757d; font-style: italic;")
        controls_layout.addWidget(info_label)
        
        parent_layout.addWidget(controls_frame)

        # Specific styling for sync_zoom_btn to override parts of button_style
        # Ensure object name is set if needed for very specific global styles,
        # but direct setStyleSheet is usually sufficient here.
        # self.sync_zoom_btn.setObjectName("sync_zoom_button") 
        self.sync_zoom_btn.setStyleSheet("""
            QPushButton { /* Base style for this button (unchecked) */
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 6px;
                background-color: #e0e0e0; /* Light Grey for unchecked */
                border: 2px solid #c0c0c0;
                color: #333333;
            }
            QPushButton:hover { /* Hover for unchecked */
                background-color: #d0d0d0;
                border-color: #b0b0b0;
            }
            QPushButton:checked { /* Checked state */
                background-color: #4CAF50; /* Vibrant Green */
                border-color: #45a049;
                color: white;
            }
            QPushButton:checked:hover { /* Hover for checked */
                background-color: #3e8e41; 
                border-color: #367c39;
            }
        """)
        
        # Connect signals
        self.zoom_in_btn.clicked.connect(self._zoom_both_in)
        self.zoom_out_btn.clicked.connect(self._zoom_both_out)
        self.fit_btn.clicked.connect(self._fit_both_to_window)
        
    def set_images(self, original_pixmap, current_pixmap, step_title="Paso Actual"):
        """Set both images with fade-in animations."""
        try:
            # Update title for current step
            current_container = self.splitter.widget(1)
            if current_container:
                title_label = current_container.findChild(QLabel)
                if title_label:
                    title_label.setText(f"🔄 {step_title}")
            
            # Set images with staggered animation
            if original_pixmap:
                self.original_image.set_image(original_pixmap)
                
            # Delay setting current image for staggered effect
            if current_pixmap:
                QTimer.singleShot(150, lambda: self.current_image.set_image(current_pixmap))
                
        except Exception as e:
            print(f"Error setting images in comparison widget: {e}")
    
    def _zoom_both_in(self):
        """Zoom both images in."""
        if self.sync_zoom_btn.isChecked():
            self.original_image.zoom_in()
            QTimer.singleShot(50, self.current_image.zoom_in)  # Slight delay for effect
        else:
            # Only zoom the image that has focus or both if none has focus
            self.original_image.zoom_in()
            self.current_image.zoom_in()
    
    def _zoom_both_out(self):
        """Zoom both images out."""
        if self.sync_zoom_btn.isChecked():
            self.original_image.zoom_out()
            QTimer.singleShot(50, self.current_image.zoom_out)
        else:
            self.original_image.zoom_out()
            self.current_image.zoom_out()
    
    def _fit_both_to_window(self):
        """Fit both images to window."""
        self.original_image.fit_to_window()
        QTimer.singleShot(100, self.current_image.fit_to_window)

class ImageZoomDialog(QDialog):
    """Enhanced dialog for zooming and comparing images with smooth animations."""
    
    def __init__(self, original_pixmap, current_pixmap, step_title="Paso Actual", parent=None):
        super().__init__(parent)
        self.original_pixmap = original_pixmap
        self.current_pixmap = current_pixmap
        self.step_title = step_title
        
        self._setup_dialog()
        self._setup_animations()
        
        # Set images after dialog is set up
        QTimer.singleShot(100, self._load_images_with_animation)
        
    def _setup_dialog(self):
        """Setup the dialog window."""
        self.setWindowTitle(f"🔍 Vista Ampliada - {self.step_title}")
        self.setModal(True)
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Center on parent
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Comparison widget
        self.comparison_widget = ImageComparisonWidget()
        layout.addWidget(self.comparison_widget)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        self.close_btn = QPushButton("❌ Cerrar")
        self.close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        close_layout.addWidget(self.close_btn)
        layout.addLayout(close_layout)
        
        # Setup dialog styling
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
    def _setup_animations(self):
        """Setup dialog entrance animations."""
        # Scale animation for dramatic entrance
        self._scale_animation = QPropertyAnimation(self, b"geometry")
        self._scale_animation.setDuration(400)
        self._scale_animation.setEasingCurve(QEasingCurve.OutBack)
        
        # Opacity animation
        self.setWindowOpacity(0.0)
        self._opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self._opacity_animation.setDuration(300)
        self._opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def _load_images_with_animation(self):
        """Load images with entrance animation."""
        try:
            # Set images in comparison widget
            self.comparison_widget.set_images(
                self.original_pixmap, 
                self.current_pixmap, 
                self.step_title
            )
            
        except Exception as e:
            print(f"Error loading images in zoom dialog: {e}")
    
    def showEvent(self, event):
        """Handle show event with entrance animation."""
        super().showEvent(event)
        
        try:
            # Start entrance animations
            final_geometry = self.geometry()
            
            # Start from smaller size
            start_geometry = final_geometry.adjusted(100, 50, -100, -50)
            self.setGeometry(start_geometry)
            
            # Animate to final size
            self._scale_animation.setStartValue(start_geometry)
            self._scale_animation.setEndValue(final_geometry)
            
            # Animate opacity
            self._opacity_animation.setStartValue(0.0)
            self._opacity_animation.setEndValue(1.0)
            
            # Start both animations
            self._scale_animation.start()
            self._opacity_animation.start()
            
        except Exception as e:
            print(f"Error in show event animation: {e}")
            # Fallback: just show normally
            self.setWindowOpacity(1.0)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        try:
            # Zoom shortcuts
            if event.key() == Qt.Key_Plus or (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Equal):
                self.comparison_widget._zoom_both_in()
            elif event.key() == Qt.Key_Minus or (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Minus):
                self.comparison_widget._zoom_both_out()
            elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_0:
                self.comparison_widget._fit_both_to_window()
            elif event.key() == Qt.Key_Escape:
                self.close()
            else:
                super().keyPressEvent(event)
                
        except Exception as e:
            print(f"Error in key press event: {e}")
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event with exit animation."""
        try:
            # Ensure the animation object exists
            if not hasattr(self, '_opacity_animation'):
                event.accept()
                return

            # Disconnect any previous connection to self.accept to avoid multiple calls
            try:
                self._opacity_animation.finished.disconnect(self.accept)
            except TypeError: # No connection existed or specific connection not found
                pass 

            self._opacity_animation.setStartValue(self.windowOpacity()) # Start from current opacity
            self._opacity_animation.setEndValue(0.0)
            self._opacity_animation.setDuration(200) # Quick fade
            self._opacity_animation.finished.connect(self.accept) # Connect to self.accept()
            self._opacity_animation.start()
            
            event.ignore() # Tell the event loop to not close the dialog immediately
        except Exception as e:
            print(f"Error in close event animation: {e}")
            event.accept() # Fallback to immediate close without animation

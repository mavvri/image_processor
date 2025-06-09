import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                             QAction, QFileDialog, QMessageBox, QSizePolicy, QProgressBar, QFrame)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, pyqtSignal

from app.threads.processing_thread import ImageProcessingWorker
from app.ui.timeline_widget import TimelineWidget
from app.ui.enhanced_widgets import (AnimatedProgressBar, CelebrationWidget, 
                                   StepDescriptionWidget, ErrorFallbackWidget)
from app.ui.parameter_panel import ParameterPanel
from app.ui.image_zoom_dialog import ImageZoomDialog

class FadeLabel(QLabel):
    """Label with fade-in animation capability and click detection."""
    
    clicked = pyqtSignal()  # Add clicked signal
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opacity = 1.0
        self._is_clickable = False
        
    def get_opacity(self):
        return self._opacity
        
    def set_opacity(self, value):
        self._opacity = value
        self.setStyleSheet(f"QLabel {{ color: rgba(44, 62, 80, {int(value * 255)}); }}")
        
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def fade_in(self, duration=300):
        """Animate fade-in effect."""
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def set_clickable(self, clickable):
        """Set whether the label is clickable."""
        self._is_clickable = clickable
        if clickable:
            self.setCursor(Qt.PointingHandCursor)
            self.setToolTip("🔍 Haga clic para ver en tamaño completo")
            # Add visual indication that it's clickable
            current_style = self.styleSheet()
            if "border:" not in current_style:
                self.setStyleSheet(current_style + """
                    QLabel:hover {
                        border: 3px solid rgba(52, 152, 219, 0.7);
                        background-color: rgba(52, 152, 219, 0.05);
                    }
                """)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setToolTip("")

    def mousePressEvent(self, event):
        """Handle mouse press for click detection."""
        if self._is_clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Conteo de Coches - Procesamiento Digital de Imágenes")
        self.setGeometry(100, 100, 1600, 1000)  # Increased width for parameter panel
        self.setMinimumSize(1400, 800)

        self.image_path = None
        self.original_pixmap = None
        self.current_pipeline_step_index = 0
        self.pipeline_step_images = []
        self.step_descriptions = []
        self.current_parameters = None  # Store current manual parameters

        # Load and apply stylesheet with fallback
        self.load_stylesheet_with_fallback()
        
        # Setup UI
        self.setup_ui()
        
        # Threading related attributes
        self.processing_thread = None
        self.worker = None

    def load_stylesheet_with_fallback(self):
        """Load stylesheet with fallback error handling."""
        try:
            style_path = os.path.join(os.path.dirname(__file__), "assets", "styles", "modern_style.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found, using fallback styling.")
            self.apply_fallback_styling()
        except Exception as e:
            print(f"Error loading stylesheet: {e}, using fallback.")
            self.apply_fallback_styling()
            
    def apply_fallback_styling(self):
        """Apply basic fallback styling."""
        fallback_qss = """
            QMainWindow { background-color: #f0f0f0; }
            QPushButton { 
                background-color: #ffffff; 
                border: 1px solid #cccccc; 
                padding: 8px 16px; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton:disabled { background-color: #f8f8f8; color: #aaaaaa; }
        """
        self.setStyleSheet(fallback_qss)

    def setup_ui(self):
        """Setup the main UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - horizontal to accommodate parameter panel
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left side: Main processing interface
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # Top section: Image display
        self.setup_image_section(left_layout)
        
        # Middle section: Timeline
        self.setup_timeline_section(left_layout)
        
        # Bottom section: Controls and status
        self.setup_controls_section(left_layout)
        
        main_layout.addWidget(left_panel, 3)  # 3/4 of the width
        
        # Right side: Parameter panel
        self.parameter_panel = ParameterPanel()
        self.parameter_panel.parametersChanged.connect(self.on_parameters_changed)
        main_layout.addWidget(self.parameter_panel, 1)  # 1/4 of the width
        
        # Setup menu
        self.setup_menu()
        
        # Load cached parameters if available
        self.load_cached_parameters()

    def setup_image_section(self, parent_layout):
        """Setup the main image display area."""
        image_frame = QFrame()
        image_frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; }")
        image_layout = QVBoxLayout(image_frame)
        
        # Image label with fade capability and click detection
        self.image_label = FadeLabel("Cargue una imagen para comenzar el análisis")
        self.image_label.setObjectName("image_label")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumSize(600, 400)
        
        # Connect click signal to zoom function
        self.image_label.clicked.connect(self.open_image_zoom)
        
        image_layout.addWidget(self.image_label)
        parent_layout.addWidget(image_frame, 1)

    def setup_timeline_section(self, parent_layout):
        """Setup the processing timeline."""
        self.timeline = TimelineWidget()
        # Connect timeline step selection to navigation
        self.timeline.step_selected.connect(self.navigate_to_step)
        parent_layout.addWidget(self.timeline)

    def setup_controls_section(self, parent_layout):
        """Setup control buttons and status."""
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        
        # Main action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.load_button = QPushButton("📁 Cargar Imagen")
        self.load_button.setMinimumHeight(40)
        
        self.process_button = QPushButton("▶️ Procesar Imagen")
        self.process_button.setObjectName("process_button")
        self.process_button.setMinimumHeight(40)
        self.process_button.setEnabled(False)
        
        # Cancel button
        self.cancel_button = QPushButton("⏹️ Cancelar")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #c0392b;
            }
        """)
        
        # Navigation buttons
        self.prev_button = QPushButton("⬅️ Anterior")
        self.prev_button.setEnabled(False)
        
        self.next_button = QPushButton("➡️ Siguiente")
        self.next_button.setEnabled(False)
        
        self.save_button = QPushButton("💾 Guardar")
        self.save_button.setEnabled(False)
        
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.process_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.prev_button)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.save_button)
        
        controls_layout.addLayout(buttons_layout)
        
        # Enhanced progress bar
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        # Step description widget
        self.step_description = StepDescriptionWidget()
        controls_layout.addWidget(self.step_description)
        
        # Status and count section
        status_layout = QHBoxLayout()
        
        self.count_label = QLabel("Coches Contados: 0")
        self.count_label.setObjectName("count_label")
        
        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")
        
        status_layout.addWidget(self.count_label)
        status_layout.addStretch()
        status_layout.addWidget(self.status_label)
        
        controls_layout.addLayout(status_layout)
        
        # Error display widget
        self.error_widget = ErrorFallbackWidget()
        controls_layout.addWidget(self.error_widget)
        
        parent_layout.addWidget(controls_frame)
        
        # Celebration widget (overlay)
        self.celebration = CelebrationWidget(self)
        
        # Connect signals
        self.load_button.clicked.connect(self.open_image_dialog)
        self.process_button.clicked.connect(self.start_image_processing)
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.prev_button.clicked.connect(self.previous_step)
        self.next_button.clicked.connect(self.next_step)
        self.save_button.clicked.connect(self.save_results)

    def setup_menu(self):
        """Setup the application menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 Archivo")
        
        open_action = QAction("Abrir Imagen...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)
        
        save_action = QAction("Guardar Resultados...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_results)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Ayuda")
        
        about_action = QAction("Acerca de...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_image_dialog(self):
        """Open file dialog to select an image."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos los archivos (*)",
            options=options
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Load and display an image with fade-in animation."""
        try:
            # Check if user wants to save current manual parameters
            if (self.parameter_panel.is_manual_mode() and 
                self.current_parameters is not None):
                reply = QMessageBox.question(
                    self, "Guardar Configuración", 
                    "¿Desea guardar la configuración manual actual antes de cargar una nueva imagen?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Cancel:
                    return
                elif reply == QMessageBox.Yes:
                    self.parameter_panel.save_to_cache(self.current_parameters)
            
            # EXC001: Validate file exists
            if not os.path.exists(file_path):
                self.show_error_animation("El archivo no existe")
                return
                
            self.image_path = file_path
            
            # Load with QPixmap
            pixmap = QPixmap(self.image_path)
            if pixmap.isNull():
                self.show_error_animation("No se pudo cargar la imagen")
                return

            # Reset pipeline state
            self.reset_pipeline()
            
            # Store original and display with fade-in
            self.original_pixmap = pixmap
            self.pipeline_step_images = [pixmap]  # Initialize with original
            self.current_pipeline_step_index = 0
            self.display_image_with_animation(pixmap)
            
            # Make image clickable for zoom
            self.image_label.set_clickable(True)
            
            # Update UI state
            self.process_button.setEnabled(True)
            self.count_label.setText("Coches Contados: 0")
            filename = os.path.basename(file_path)
            self.status_label.setText(f"✅ Imagen cargada: {filename}")
            
            # Set first step in timeline
            self.timeline.set_step_active(0)
            self.timeline.set_step_thumbnail(0, pixmap.scaled(120, 80, Qt.KeepAspectRatio))
            self.update_navigation_buttons()
            
            # Reset current parameters for new image
            self.current_parameters = None
            
        except Exception as e:
            self.show_error_animation(f"Error al cargar la imagen: {str(e)}")

    def display_image_with_animation(self, pixmap):
        """Display image with fade-in animation."""
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.fade_in(500)  # 500ms fade-in
            
            # Ensure image remains clickable when updated
            self.image_label.set_clickable(True)

    def show_error_animation(self, message):
        """Show error message with warning animation."""
        QMessageBox.warning(self, "⚠️ Error", message)
        
        # Flash the image label red briefly
        original_style = self.image_label.styleSheet()
        self.image_label.setStyleSheet(original_style + "border: 3px solid #e74c3c;")
        
        # Reset after animation
        QTimer.singleShot(1000, lambda: self.image_label.setStyleSheet(original_style))

    def reset_pipeline(self):
        """Reset the processing pipeline state."""
        self.current_pipeline_step_index = 0
        self.pipeline_step_images = []
        self.timeline.reset()
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.save_button.setEnabled(False)
        
        # Reset image clickability
        self.image_label.set_clickable(False)

    def start_image_processing(self):
        """Start the image processing pipeline."""
        if not self.image_path:
            QMessageBox.warning(self, "⚠️ Advertencia", "Por favor, cargue una imagen primero.")
            return

        # Update UI for processing state
        self.process_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Determine processing mode
        if self.parameter_panel.is_manual_mode():
            self.current_parameters = self.parameter_panel.get_current_parameters()
            self.status_label.setText("🔄 Iniciando procesamiento en modo MANUAL...")
        else:
            self.current_parameters = None
            self.status_label.setText("🔄 Iniciando procesamiento en modo AUTOMÁTICO...")
        
        # Clear previous results
        self.step_descriptions = []
        
        # Set timeline to first processing step
        self.timeline.set_step_active(1)

        # Clean up previous thread
        self._cleanup_worker()

        # Start worker thread with current parameters
        self.worker = ImageProcessingWorker(self.image_path, self.current_parameters)
        self.processing_thread = QThread()
        
        self.worker.moveToThread(self.processing_thread)
        
        # Connect signals
        self.processing_thread.started.connect(self.worker.process)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.step_completed.connect(self.on_step_completed)
        
        # Cleanup connections
        self.worker.finished.connect(self.processing_thread.quit)
        self.worker.error.connect(self.processing_thread.quit)
        self.processing_thread.finished.connect(self._cleanup_worker_thread_finished)

        self.processing_thread.start()

    def on_parameters_changed(self, params):
        """Handle parameter changes from the parameter panel."""
        self.current_parameters = params
        
        # If an image is loaded, enable reprocessing
        if self.image_path:
            self.process_button.setEnabled(True)
            mode_indicator = "🔧 MANUAL" if self.parameter_panel.is_manual_mode() else "🤖 AUTO"
            self.status_label.setText(f"{mode_indicator} Parámetros actualizados - Listo para procesar")

    def load_cached_parameters(self):
        """Load cached parameters on startup."""
        try:
            cached_params = self.parameter_panel.load_from_cache()
            if cached_params:
                reply = QMessageBox.question(
                    self, "Cargar Configuración Previa", 
                    "Se encontró una configuración guardada previamente.\n¿Desea cargarla?",
                    QMessageBox.Yes | QMessageBox.No, 
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.parameter_panel.set_parameters(cached_params)
        except Exception as e:
            print(f"Warning: Could not load cached parameters: {e}")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "Acerca de", 
                         "Sistema de Conteo de Coches v1.0\n\n"
                         "Desarrollado con técnicas de procesamiento digital de imágenes\n"
                         "utilizando OpenCV y PyQt5.\n\n"
                         "© 2024 - Proyecto de Visión por Computadora")

    def closeEvent(self, event):
        thread_running = False
        try:
            if self.processing_thread is not None and hasattr(self.processing_thread, 'isRunning'): # Check attribute
                thread_running = self.processing_thread.isRunning()
        except RuntimeError: # Catches "wrapped C/C++ object of type QThread has been deleted"
            thread_running = False
            self.processing_thread = None # Ensure it's None if deleted

        if thread_running:
            reply = QMessageBox.question(self, 'Salir',
                                           "El procesamiento está en curso. ¿Está seguro de que desea salir?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.worker:
                    self.worker.stop() # Request worker to stop
                
                # Gracefully quit and wait for the thread
                if self.processing_thread:
                    self.processing_thread.quit()
                    if not self.processing_thread.wait(3000): # Wait up to 3 seconds
                        # If wait times out, thread might be stuck.
                        # Consider more forceful termination if necessary, but usually not recommended.
                        print("Advertencia: El hilo de procesamiento no terminó correctamente.")
                
                self._cleanup_worker_thread_finished() # Ensure cleanup
                event.accept()
            else:
                event.ignore()
        else:
            # Ensure cleanup even if thread was not perceived as running but objects exist
            self._cleanup_worker_thread_finished()
            event.accept()

    def cancel_processing(self):
        """Cancel the current processing operation."""
        if self.worker:
            self.worker.stop()
            self.status_label.setText("🛑 Cancelando procesamiento...")
            self.cancel_button.setEnabled(False)

    def on_progress_update(self, percentage, message):
        """Handle progress updates from worker."""
        self.progress_bar.animate_to_value(percentage)
        self.status_label.setText(f"🔄 {message}")

    def on_step_completed(self, step_index, description):
        """Handle step completion updates."""
        step_titles = [
            "Imagen Original", "Escala de Grises", "Filtrado Avanzado", 
            "Umbralización Mejorada", "Apertura Suave", "Cierre Selectivo",
            "Etiquetado de Componentes", "Filtro Anti-Árbol", "Resultado Final"
        ]
        
        if step_index < len(step_titles):
            self.step_description.update_step(step_index, step_titles[step_index], description)
            
            # Update timeline to show progress during processing
            if step_index < self.timeline.get_total_steps():
                self.timeline.set_step_active(step_index)

    def on_processing_finished(self, pipeline_q_images_list, count, descriptions):
        """Handle successful processing completion."""
        try:
            self.progress_bar.setVisible(False)
            self.cancel_button.setEnabled(False)
            
            if isinstance(pipeline_q_images_list, list) and pipeline_q_images_list:
                # Store descriptions
                self.step_descriptions = descriptions
                
                # Convert QImages to QPixmaps and store them
                self.pipeline_step_images = []
                for q_img in pipeline_q_images_list:
                    if q_img and not q_img.isNull():
                        self.pipeline_step_images.append(QPixmap.fromImage(q_img))
                    else:
                        self.pipeline_step_images.append(self.original_pixmap if self.original_pixmap else QPixmap())

                # Update timeline thumbnails for all steps
                for i, q_pixmap in enumerate(self.pipeline_step_images):
                    if i < self.timeline.get_total_steps():
                        self.timeline.set_step_thumbnail(i, q_pixmap.scaled(120, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
                # Set to the FINAL step (last image in the pipeline)
                if self.pipeline_step_images:
                    final_step_index = len(self.pipeline_step_images) - 1
                    self.current_pipeline_step_index = final_step_index
                    
                    # Display the final processed image
                    final_processed_pixmap = self.pipeline_step_images[final_step_index]
                    self.display_image_with_animation(final_processed_pixmap)
                    
                    # Set timeline to show the final step as active
                    if final_step_index < self.timeline.get_total_steps():
                        self.timeline.set_step_active(final_step_index)
                    
                    # Update step description for final step
                    if (self.step_descriptions and 
                        final_step_index < len(self.step_descriptions)):
                        
                        step_titles = [
                            "Imagen Original", "Escala de Grises", "Filtrado Avanzado", 
                            "Umbralización Mejorada", "Apertura Suave", "Cierre Selectivo",
                            "Etiquetado de Componentes", "Filtro Anti-Árbol", "Resultado Final"
                        ]
                        
                        final_title = step_titles[final_step_index] if final_step_index < len(step_titles) else "Resultado Final"
                        final_description = self.step_descriptions[final_step_index]
                        
                        self.step_description.update_step(final_step_index, final_title, final_description)
                
                self.save_button.setEnabled(True)
                
                # Show celebration for successful completion
                if count > 0:
                    QTimer.singleShot(800, lambda: self.celebration.show_celebration(count))
                
            else:
                self.error_widget.show_error("Procesamiento finalizado, pero resultados inválidos", "processing")
                if self.original_pixmap:
                    self.pipeline_step_images = [self.original_pixmap]
                    self.current_pipeline_step_index = 0

            self.count_label.setText(f"Coches Contados: {count}")
            self.status_label.setText("✅ Procesamiento completado.")
            
        except Exception as e:
            self.error_widget.show_error(f"Error al mostrar resultados: {str(e)}", "general")
            if self.original_pixmap:
                self.pipeline_step_images = [self.original_pixmap]
                self.current_pipeline_step_index = 0
        finally:
            self.process_button.setEnabled(True)
            self.update_navigation_buttons()

    def on_processing_error(self, error_message):
        """Handle processing errors."""
        self.progress_bar.setVisible(False)
        self.cancel_button.setEnabled(False)
        self.error_widget.show_error(error_message, "processing")
        self.status_label.setText(f"❌ Error en procesamiento")
        self.process_button.setEnabled(True)

    def update_step_display(self):
        """Update the display for current pipeline step."""
        if not self.pipeline_step_images or not (0 <= self.current_pipeline_step_index < len(self.pipeline_step_images)):
            if self.original_pixmap:
                self.display_image_with_animation(self.original_pixmap)
            else:
                self.image_label.clear()
                self.image_label.setText("Cargue una imagen para comenzar el análisis")
            self.timeline.set_step_active(0)
            self.update_navigation_buttons()
            return

        # Display the image for the current step
        current_step_pixmap = self.pipeline_step_images[self.current_pipeline_step_index]
        self.display_image_with_animation(current_step_pixmap)
        
        # Update timeline
        self.timeline.set_step_active(self.current_pipeline_step_index)
        
        # Update step description if available
        if (self.step_descriptions and 
            0 <= self.current_pipeline_step_index < len(self.step_descriptions)):
            
            step_titles = [
                "Imagen Original", "Escala de Grises", "Filtrado Avanzado", 
                "Umbralización Mejorada", "Apertura Suave", "Cierre Selectivo",
                "Etiquetado de Componentes", "Filtro Anti-Árbol", "Resultado Final"
            ]
            
            title = step_titles[self.current_pipeline_step_index] if self.current_pipeline_step_index < len(step_titles) else "Procesamiento"
            description = self.step_descriptions[self.current_pipeline_step_index]
            
            self.step_description.update_step(self.current_pipeline_step_index, title, description)
        
        # Update navigation buttons
        self.update_navigation_buttons()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize celebration widget to cover the main window
        if hasattr(self, 'celebration'):
            self.celebration.resize(self.size())
            
        # Update image display
        if self.pipeline_step_images and 0 <= self.current_pipeline_step_index < len(self.pipeline_step_images):
            current_pixmap_to_display = self.pipeline_step_images[self.current_pipeline_step_index]
            if current_pixmap_to_display and not current_pixmap_to_display.isNull():
                 self.display_image_with_animation(current_pixmap_to_display)
        elif self.original_pixmap:
            self.display_image_with_animation(self.original_pixmap)

    def _cleanup_worker(self):
        """Clean up worker resources. Called after thread signals it's done with the worker."""
        if self.worker:
            # Disconnect all signals to prevent issues if not already done by moveToThread(None)
            try:
                self.worker.finished.disconnect()
            except TypeError: pass # Already disconnected or never connected
            try:
                self.worker.error.disconnect()
            except TypeError: pass # Already disconnected or never connected
            
            self.worker.deleteLater()
            self.worker = None
            
    def _cleanup_worker_thread_finished(self):
        """Slot connected to QThread.finished. Cleans up worker and then the thread itself."""
        self._cleanup_worker() # Clean up the worker first
        if self.processing_thread:
            # The thread is already finished, so we just schedule it for deletion
            self.processing_thread.deleteLater()
            self.processing_thread = None

    def previous_step(self):
        """Navigate to previous pipeline step."""
        if self.current_pipeline_step_index > 0:
            self.current_pipeline_step_index -= 1
            self.update_step_display()

    def next_step(self):
        """Navigate to next pipeline step."""
        if self.pipeline_step_images and self.current_pipeline_step_index < len(self.pipeline_step_images) - 1:
            self.current_pipeline_step_index += 1
            self.update_step_display()

    def update_navigation_buttons(self):
        """Enable/disable previous/next buttons based on current step."""
        num_steps = len(self.pipeline_step_images)
        if num_steps > 0:
            self.prev_button.setEnabled(self.current_pipeline_step_index > 0)
            self.next_button.setEnabled(self.current_pipeline_step_index < num_steps - 1)
        else:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

    def save_results(self):
        """Save processing results."""
        if not self.pipeline_step_images or not (0 <= self.current_pipeline_step_index < len(self.pipeline_step_images)):
            QMessageBox.information(self, "ℹ️ Información", "No hay resultados para guardar.")
            return
            
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Resultados", "", 
            "Imágenes (*.png *.jpg);;Todos los archivos (*)",
            options=options
        )
        
        if file_path:
            try:
                # Save the currently displayed step
                image_to_save = self.pipeline_step_images[self.current_pipeline_step_index]
                if image_to_save:
                    image_to_save.save(file_path)
                    self.status_label.setText(f"💾 Resultados guardados: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "⚠️ Advertencia", "No hay imagen para guardar en este paso.")
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", f"Error al guardar: {str(e)}")

    def open_image_zoom(self):
        """Open the image zoom dialog with current and original images."""
        try:
            # Validate that we have images to show
            if not self.original_pixmap:
                self.error_widget.show_error("No hay imagen original para mostrar", "general")
                return
            
            # Get current step image
            current_pixmap = None
            step_title = "Imagen Original"
            
            if (self.pipeline_step_images and 
                0 <= self.current_pipeline_step_index < len(self.pipeline_step_images)):
                current_pixmap = self.pipeline_step_images[self.current_pipeline_step_index]
                
                # Get step title
                step_titles = [
                    "Imagen Original", "Escala de Grises", "Filtrado Avanzado", 
                    "Umbralización Mejorada", "Apertura Suave", "Cierre Selectivo",
                    "Etiquetado de Componentes", "Filtro Anti-Árbol", "Resultado Final"
                ]
                
                if self.current_pipeline_step_index < len(step_titles):
                    step_title = step_titles[self.current_pipeline_step_index]
                else:
                    step_title = f"Paso {self.current_pipeline_step_index + 1}"
            else:
                current_pixmap = self.original_pixmap
            
            # Create and show zoom dialog
            zoom_dialog = ImageZoomDialog(
                self.original_pixmap,
                current_pixmap, 
                step_title,
                self
            )
            
            # Show dialog
            zoom_dialog.exec_()
            
        except Exception as e:
            # Use error widget to show the error
            self.error_widget.show_error(
                f"Error al abrir vista ampliada: {str(e)}", 
                "general"
            )
            print(f"Error opening image zoom: {e}")

    def navigate_to_step(self, step_index):
        """Navigate to a specific pipeline step from timeline click."""
        try:
            # Validate step index
            if not (0 <= step_index < len(self.pipeline_step_images)):
                print(f"Invalid step index: {step_index}")
                return
            
            # Update current step index
            self.current_pipeline_step_index = step_index
            
            # Update the display
            self.update_step_display()
            
        except Exception as e:
            print(f"Error navigating to step {step_index}: {e}")
            self.error_widget.show_error(
                f"Error al navegar al paso {step_index + 1}", 
                "general"
            )

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QVBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from app.utils.logger import logger

class TimelineStep(QLabel):
    """
    Enhanced timeline step widget with improved animations and state management.
    Represents a single step in the image processing pipeline.
    """
    
    step_clicked = pyqtSignal(int)  # Signal when step is clicked
    
    def __init__(self, step_index: int, title: str, description: str = ""):
        super().__init__()
        self.step_index = step_index
        self.title = title
        self.description = description
        self.state = "pending"  # pending, active, completed
        self._thumbnail_pixmap = None
        
        self._setup_ui()
        self._setup_animations()
        
        logger.debug(
            "TimelineStep created",
            step_index=step_index,
            title=title
        )
        
    def _setup_ui(self):
        """Setup the UI appearance and interactions."""
        self.setProperty("class", "timeline_step")
        self.setText(f"{self.title}\n{self.description}")
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumSize(100, 80)
        self.setMaximumSize(140, 100)
        
        # Enable mouse interaction
        self.setCursor(Qt.PointingHandCursor)
        
        # Animation properties
        self._glow_opacity = 0.0
        self._scale_factor = 1.0
        
    def _setup_animations(self):
        """Setup animation objects for smooth transitions."""
        # Glow animation for active state
        self._glow_animation = QPropertyAnimation(self, b"glow_opacity")
        self._glow_animation.setDuration(1000)
        self._glow_animation.setStartValue(0.0)
        self._glow_animation.setEndValue(1.0)
        self._glow_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        # Scale animation for hover/click effects
        self._scale_animation = QPropertyAnimation(self, b"scale_factor")
        self._scale_animation.setDuration(200)
        self._scale_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def get_glow_opacity(self):
        """Get current glow opacity for animation."""
        return self._glow_opacity
        
    def set_glow_opacity(self, value):
        """Set glow opacity and trigger repaint."""
        self._glow_opacity = value
        self.update()  # Trigger repaint
        
    glow_opacity = pyqtProperty(float, get_glow_opacity, set_glow_opacity)
    
    def get_scale_factor(self):
        """Get current scale factor for animation."""
        return self._scale_factor
        
    def set_scale_factor(self, value):
        """Set scale factor and trigger resize."""
        self._scale_factor = value
        self.update()
        
    scale_factor = pyqtProperty(float, get_scale_factor, set_scale_factor)
    
    def set_state(self, state: str):
        """
        Set the state of the timeline step with animated transition.
        
        Args:
            state: New state (pending, active, completed)
        """
        try:
            old_state = self.state
            self.state = state
            
            # Apply appropriate styling
            if state == "active":
                self.setProperty("class", "timeline_step_active")
                self._start_glow_animation()
            elif state == "completed":
                self.setProperty("class", "timeline_step_completed")
                self._stop_glow_animation()
            else:  # pending
                self.setProperty("class", "timeline_step")
                self._stop_glow_animation()
            
            # Refresh styling
            self.style().unpolish(self)
            self.style().polish(self)
            
            logger.debug(
                "Timeline step state changed",
                step_index=self.step_index,
                old_state=old_state,
                new_state=state
            )
            
        except Exception as e:
            logger.error(f"Error setting timeline step state: {e}")
    
    def set_thumbnail(self, pixmap: QPixmap):
        """
        Set a thumbnail image for this step with fade-in animation.
        
        Args:
            pixmap: QPixmap to display as thumbnail
        """
        try:
            if pixmap and not pixmap.isNull():
                # Scale pixmap to fit the step
                scaled_pixmap = pixmap.scaled(
                    80, 50, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self._thumbnail_pixmap = scaled_pixmap
                self.setPixmap(scaled_pixmap)
                self.setText(self.title)  # Show only title when thumbnail is present
                
                logger.debug(
                    "Thumbnail set for timeline step",
                    step_index=self.step_index,
                    pixmap_size=f"{pixmap.width()}x{pixmap.height()}"
                )
            
        except Exception as e:
            logger.error(f"Error setting thumbnail: {e}")
    
    def _start_glow_animation(self):
        """Start the glow animation for active state."""
        try:
            self._glow_animation.setLoopCount(-1)  # Infinite loop
            self._glow_animation.setDirection(QPropertyAnimation.Forward)
            self._glow_animation.start()
            
        except Exception as e:
            logger.error(f"Error starting glow animation: {e}")
    
    def _stop_glow_animation(self):
        """Stop the glow animation."""
        try:
            self._glow_animation.stop()
            self._glow_opacity = 0.0
            self.update()
            
        except Exception as e:
            logger.error(f"Error stopping glow animation: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse press with scale animation."""
        try:
            if event.button() == Qt.LeftButton:
                # Scale down animation
                self._scale_animation.setStartValue(1.0)
                self._scale_animation.setEndValue(0.95)
                self._scale_animation.start()
                
                # Emit signal after short delay
                QTimer.singleShot(100, lambda: self.step_clicked.emit(self.step_index))
                
                logger.log_ui_action(
                    "timeline_step_clicked",
                    "TimelineStep",
                    step_index=self.step_index,
                    step_title=self.title
                )
                
        except Exception as e:
            logger.error(f"Error handling mouse press: {e}")
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release with scale animation."""
        try:
            # Scale back to normal
            self._scale_animation.setStartValue(0.95)
            self._scale_animation.setEndValue(1.0)
            self._scale_animation.start()
            
        except Exception as e:
            logger.error(f"Error handling mouse release: {e}")
    
    def enterEvent(self, event):
        """Handle mouse enter with subtle scale animation."""
        try:
            if self.state != "active":  # Don't interfere with active state
                self._scale_animation.setStartValue(1.0)
                self._scale_animation.setEndValue(1.05)
                self._scale_animation.start()
                
        except Exception as e:
            logger.error(f"Error handling mouse enter: {e}")
    
    def leaveEvent(self, event):
        """Handle mouse leave with scale animation."""
        try:
            if self.state != "active":
                self._scale_animation.setStartValue(1.05)
                self._scale_animation.setEndValue(1.0)
                self._scale_animation.start()
                
        except Exception as e:
            logger.error(f"Error handling mouse leave: {e}")
    
    def clear_thumbnail(self):
        """Clear the thumbnail and restore text display."""
        try:
            self._thumbnail_pixmap = None
            self.clear()
            self.setText(f"{self.title}\n{self.description}")
            
        except Exception as e:
            logger.error(f"Error clearing thumbnail: {e}")

class TimelineWidget(QFrame):
    """
    Enhanced timeline widget with improved animations and better pipeline integration.
    Shows the complete image processing pipeline with interactive steps.
    """
    
    step_selected = pyqtSignal(int)  # Signal when a step is selected
    
    def __init__(self):
        super().__init__()
        self.setObjectName("timeline_frame")
        self._setup_ui()
        self.current_step = 0
        self._step_transitions = {}  # Track step transition animations
        
        logger.debug("TimelineWidget initialized")
        
    def _setup_ui(self):
        """Setup the enhanced timeline UI with better layout and styling."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Enhanced title with better styling
        title_label = QLabel("🔄 Pipeline de Procesamiento de Imágenes")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px; 
                font-weight: bold; 
                color: #2c3e50; 
                margin-bottom: 10px;
                padding: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(52, 152, 219, 0.1), stop:1 rgba(52, 152, 219, 0.05));
                border-radius: 8px;
            }
        """)
        layout.addWidget(title_label)
        
        # Timeline steps container with scroll support
        steps_container = QFrame()
        steps_layout = QHBoxLayout(steps_container)
        steps_layout.setSpacing(10)
        steps_layout.setContentsMargins(5, 5, 5, 5)
        
        # Define processing steps with enhanced descriptions
        step_definitions = [
            ("Original", "Imagen cargada"),
            ("Escala Grises", "Conversión B&W"),
            ("Filtrado Suave", "Bilateral+Gaussiano"),
            ("Umbralización", "Adaptativa optimizada"),
            ("Apertura", "Limpieza morfológica"),
            ("Cierre", "Unión de componentes"),
            ("Componentes", "Análisis conexo"),
            ("Filtro Geométrico", "Detección inteligente"),
            ("Resultado Final", "Coches identificados")
        ]
        
        self.steps = []
        for index, (title, description) in enumerate(step_definitions):
            try:
                step = TimelineStep(index, title, description)
                step.step_clicked.connect(self._on_step_clicked)
                self.steps.append(step)
                steps_layout.addWidget(step)
                
            except Exception as e:
                logger.error(f"Error creating timeline step {index}: {e}")
                # Create a fallback step
                fallback_step = QLabel(f"Step {index + 1}")
                steps_layout.addWidget(fallback_step)
                self.steps.append(fallback_step)
            
        steps_layout.addStretch()
        layout.addWidget(steps_container)
        
        # Enhanced navigation info with better styling
        nav_label = QLabel("💡 Tip: Haga clic en cualquier paso para navegar directamente")
        nav_label.setStyleSheet("""
            QLabel {
                font-size: 12px; 
                color: #6c757d; 
                margin-top: 5px;
                padding: 5px;
                background-color: rgba(108, 117, 125, 0.1);
                border-radius: 5px;
                font-style: italic;
            }
        """)
        layout.addWidget(nav_label)
        
    def _on_step_clicked(self, step_index: int):
        """
        Handle step click with validation and animation.
        
        Args:
            step_index: Index of the clicked step
        """
        try:
            # Validate step index
            if 0 <= step_index < len(self.steps):
                logger.log_ui_action(
                    "timeline_step_navigation",
                    "TimelineWidget",
                    step_index=step_index,
                    current_step=self.current_step
                )
                
                self.step_selected.emit(step_index)
            else:
                logger.warning(f"Invalid step index clicked: {step_index}")
                
        except Exception as e:
            logger.error(f"Error handling step click: {e}")
            
    def set_step_active(self, step_index: int):
        """
        Set a specific step as active with smooth transition animations.
        
        Args:
            step_index: Index of the step to make active
        """
        try:
            if not (0 <= step_index < len(self.steps)):
                logger.warning(f"Invalid step index for activation: {step_index}")
                return
            
            old_step = self.current_step
            
            # Update all step states with proper transitions
            for i, step in enumerate(self.steps):
                if hasattr(step, 'set_state'):  # Check if it's a proper TimelineStep
                    if i < step_index:
                        step.set_state("completed")
                    elif i == step_index:
                        step.set_state("active")
                    else:
                        step.set_state("pending")
            
            self.current_step = step_index
            
            logger.debug(
                "Timeline step activated",
                old_step=old_step,
                new_step=step_index,
                total_steps=len(self.steps)
            )
            
        except Exception as e:
            logger.error(f"Error setting active step: {e}")
            
    def set_step_thumbnail(self, step_index: int, pixmap: QPixmap):
        """
        Set thumbnail for a specific step with error handling.
        
        Args:
            step_index: Index of the step
            pixmap: QPixmap to set as thumbnail
        """
        try:
            if 0 <= step_index < len(self.steps):
                step = self.steps[step_index]
                if hasattr(step, 'set_thumbnail'):
                    step.set_thumbnail(pixmap)
                    
                    logger.debug(
                        "Thumbnail set for step",
                        step_index=step_index,
                        has_pixmap=pixmap is not None and not pixmap.isNull()
                    )
                else:
                    logger.warning(f"Step {step_index} does not support thumbnails")
            else:
                logger.warning(f"Invalid step index for thumbnail: {step_index}")
                
        except Exception as e:
            logger.error(f"Error setting step thumbnail: {e}")
            
    def get_current_step(self) -> int:
        """Get the current active step index."""
        return self.current_step
        
    def get_total_steps(self) -> int:
        """Get total number of steps in the timeline."""
        return len(self.steps)
        
    def reset(self):
        """Reset all steps to pending state with smooth animations."""
        try:
            for step in self.steps:
                if hasattr(step, 'set_state'):
                    step.set_state("pending")
                if hasattr(step, 'clear_thumbnail'):
                    step.clear_thumbnail()
                elif hasattr(step, 'clear'):
                    step.clear()
                    if hasattr(step, 'setText'):
                        # Restore text for fallback steps
                        index = self.steps.index(step)
                        step.setText(f"Step {index + 1}")
            
            self.current_step = 0
            
            logger.debug("Timeline reset to initial state")
            
        except Exception as e:
            logger.error(f"Error resetting timeline: {e}")
    
    def highlight_step_briefly(self, step_index: int, duration: int = 1000):
        """
        Briefly highlight a step to draw attention.
        
        Args:
            step_index: Index of step to highlight
            duration: Duration of highlight in milliseconds
        """
        try:
            if 0 <= step_index < len(self.steps):
                step = self.steps[step_index]
                if hasattr(step, '_scale_animation'):
                    # Brief scale animation
                    step._scale_animation.setDuration(duration // 2)
                    step._scale_animation.setStartValue(1.0)
                    step._scale_animation.setEndValue(1.1)
                    step._scale_animation.finished.connect(
                        lambda: self._restore_step_scale(step)
                    )
                    step._scale_animation.start()
                    
                    logger.debug(f"Step {step_index} highlighted briefly")
                    
        except Exception as e:
            logger.error(f"Error highlighting step: {e}")
    
    def _restore_step_scale(self, step):
        """Restore step to normal scale after highlight."""
        try:
            if hasattr(step, '_scale_animation'):
                step._scale_animation.setStartValue(1.1)
                step._scale_animation.setEndValue(1.0)
                step._scale_animation.start()
                
        except Exception as e:
            logger.error(f"Error restoring step scale: {e}")

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QFrame, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, pyqtSignal, QSequentialAnimationGroup
from PyQt5.QtGui import QFont, QPalette, QColor
from app.utils.logger import logger

class AnimatedProgressBar(QProgressBar):
    """Enhanced progress bar with smooth animations and better visual feedback."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styling()
        self._current_animation = None
        try:
            logger.debug("AnimatedProgressBar initialized")
        except Exception:
            print("AnimatedProgressBar initialized")
        
    def _setup_styling(self):
        """Setup enhanced styling for the progress bar."""
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                background-color: #f8f9fa;
                text-align: center;
                font-weight: 600;
                color: #495057;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #5dade2, stop:1 #3498db);
                border-radius: 6px;
                margin: 1px;
            }
        """)
        
    def animate_to_value(self, target_value: int, duration: int = 500):
        """
        Animate progress bar to target value with improved error handling.
        
        Args:
            target_value: Target percentage (0-100)
            duration: Animation duration in milliseconds
        """
        try:
            # Stop any existing animation
            if self._current_animation:
                self._current_animation.stop()
                
            # Validate target value
            target_value = max(0, min(100, target_value))
            
            self._current_animation = QPropertyAnimation(self, b"value")
            self._current_animation.setDuration(duration)
            self._current_animation.setStartValue(self.value())
            self._current_animation.setEndValue(target_value)
            self._current_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # Log animation start
            try:
                logger.debug("Progress bar animation started", 
                           from_value=self.value(), to_value=target_value, duration=duration)
            except Exception:
                print(f"Progress bar animation: {self.value()} -> {target_value}")
            
            self._current_animation.start()
            
        except Exception as e:
            try:
                logger.error(f"Error animating progress bar: {e}")
            except Exception:
                print(f"Error animating progress bar: {e}")
            # Fallback to direct value setting
            self.setValue(target_value)

class CelebrationWidget(QWidget):
    """
    Enhanced celebration widget with improved animations and error handling.
    Shows animated celebration when car counting is complete.
    """
    
    celebration_finished = pyqtSignal()  # Signal when celebration completes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._animation_group = None
        self._auto_hide_timer = None
        self.hide()
        logger.debug("CelebrationWidget initialized")
        
    def _setup_ui(self):
        """Setup the celebration UI with enhanced styling."""
        self.setObjectName("celebration_widget")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Main celebration message
        self.celebration_label = QLabel("🎉 ¡Análisis Completado! 🎉")
        self.celebration_label.setAlignment(Qt.AlignCenter)
        self.celebration_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #27ae60;
                background-color: rgba(255, 255, 255, 0.95);
                border: 3px solid rgba(39, 174, 96, 0.8);
                border-radius: 20px;
                padding: 30px;
                margin: 20px;
            }
        """)
        
        # Secondary message
        self.detail_label = QLabel("Procesamiento completado exitosamente")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #2c3e50;
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }
        """)
        
        layout.addWidget(self.celebration_label)
        layout.addWidget(self.detail_label)
        
        # Setup opacity effect for animations
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
    def show_celebration(self, car_count: int):
        """
        Show celebration animation with car count and enhanced visual effects.
        
        Args:
            car_count: Number of cars detected
        """
        try:
            # Update text with car count
            self.celebration_label.setText(f"🎉 ¡{car_count} Coches Detectados! 🎉")
            self.detail_label.setText(f"Análisis completado con {car_count} vehículos identificados")
            
            # Make widget visible and bring to front
            self.show()
            self.raise_()
            
            # Stop any existing animations
            if self._animation_group:
                self._animation_group.stop()
            
            if self._auto_hide_timer:
                self._auto_hide_timer.stop()
            
            # Create enhanced animation sequence
            self._animation_group = QSequentialAnimationGroup()
            
            # Fade in animation
            fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
            fade_in.setDuration(800)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.OutBounce)
            
            # Hold animation
            hold = QPropertyAnimation(self.opacity_effect, b"opacity")
            hold.setDuration(2000)
            hold.setStartValue(1.0)
            hold.setEndValue(1.0)
            
            self._animation_group.addAnimation(fade_in)
            self._animation_group.addAnimation(hold)
            
            # Connect completion signal
            self._animation_group.finished.connect(self._on_animation_finished)
            
            self._animation_group.start()
            
            # Setup auto-hide timer as backup
            self._auto_hide_timer = QTimer()
            self._auto_hide_timer.setSingleShot(True)
            self._auto_hide_timer.timeout.connect(self.hide_celebration)
            self._auto_hide_timer.start(4000)  # 4 seconds total display time
            
            logger.log_ui_action("show_celebration", "CelebrationWidget", car_count=car_count)
            
        except Exception as e:
            logger.error(f"Error showing celebration: {e}")
            # Fallback: simple show without animation
            self.show()
            QTimer.singleShot(3000, self.hide)
    
    def _on_animation_finished(self):
        """Handle animation completion."""
        try:
            QTimer.singleShot(500, self.hide_celebration)  # Small delay before hiding
        except Exception as e:
            logger.error(f"Error in animation finished handler: {e}")
            self.hide()
        
    def hide_celebration(self):
        """Hide celebration with smooth fade out animation."""
        try:
            if self._auto_hide_timer:
                self._auto_hide_timer.stop()
            
            # Fade out animation
            self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_out.setDuration(500)
            self.fade_out.setStartValue(1.0)
            self.fade_out.setEndValue(0.0)
            self.fade_out.setEasingCurve(QEasingCurve.InCubic)
            self.fade_out.finished.connect(self._complete_hide)
            self.fade_out.start()
            
            logger.log_ui_action("hide_celebration", "CelebrationWidget")
            
        except Exception as e:
            logger.error(f"Error hiding celebration: {e}")
            self.hide()
    
    def _complete_hide(self):
        """Complete the hide process and emit signal."""
        self.hide()
        self.celebration_finished.emit()

class StepDescriptionWidget(QFrame):
    """
    Enhanced widget for showing animated step descriptions with better error handling.
    Provides smooth transitions between processing steps.
    """
    
    step_changed = pyqtSignal(int, str)  # Signal when step changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_animation = None
        self._pending_update = None
        logger.debug("StepDescriptionWidget initialized")
        
    def _setup_ui(self):
        """Setup the UI with enhanced styling and layout."""
        self.setObjectName("step_description_frame")
        self.setStyleSheet("""
            QFrame#step_description_frame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Step title with enhanced styling
        self.step_title = QLabel("Paso 1: Imagen Original")
        self.step_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
                padding: 5px;
            }
        """)
        
        # Step description with better formatting
        self.step_description = QLabel("Preparando análisis de imagen...")
        self.step_description.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
                line-height: 1.5;
                padding: 8px;
                background-color: rgba(108, 117, 125, 0.1);
                border-radius: 6px;
            }
        """)
        self.step_description.setWordWrap(True)
        self.step_description.setMinimumHeight(60)
        
        layout.addWidget(self.step_title)
        layout.addWidget(self.step_description)
        
        # Animation effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
    def update_step(self, step_index: int, title: str, description: str):
        """
        Update step information with smooth animation and error handling.
        
        Args:
            step_index: Index of the current step
            title: Title of the step
            description: Detailed description of the step
        """
        try:
            # Store pending update if animation is running
            if self._current_animation and self._current_animation.state() == QPropertyAnimation.Running:
                self._pending_update = (step_index, title, description)
                logger.debug("Step update queued", step_index=step_index)
                return
            
            # Validate inputs
            step_index = max(0, step_index)
            title = title or f"Paso {step_index + 1}"
            description = description or "Procesando..."
            
            # Start fade out animation
            self._current_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self._current_animation.setDuration(200)
            self._current_animation.setStartValue(1.0)
            self._current_animation.setEndValue(0.3)
            self._current_animation.finished.connect(
                lambda: self._update_content(step_index, title, description)
            )
            self._current_animation.start()
            
            logger.debug(
                "Step description update started",
                step_index=step_index,
                title=title
            )
            
        except Exception as e:
            logger.error(f"Error updating step description: {e}")
            # Fallback: direct update without animation
            self._update_content_direct(step_index, title, description)
        
    def _update_content(self, step_index: int, title: str, description: str):
        """Update content and fade back in with error handling."""
        try:
            self._update_content_direct(step_index, title, description)
            
            # Fade in animation
            fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
            fade_in.setDuration(300)
            fade_in.setStartValue(0.3)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.OutCubic)
            fade_in.finished.connect(self._check_pending_updates)
            
            self._current_animation = fade_in
            fade_in.start()
            
        except Exception as e:
            logger.error(f"Error in content update animation: {e}")
            self._update_content_direct(step_index, title, description)
    
    def _update_content_direct(self, step_index: int, title: str, description: str):
        """Update content directly without animation."""
        self.step_title.setText(f"Paso {step_index + 1}: {title}")
        self.step_description.setText(description)
        self.step_changed.emit(step_index, title)
    
    def _check_pending_updates(self):
        """Check and process any pending updates."""
        if self._pending_update:
            step_index, title, description = self._pending_update
            self._pending_update = None
            self.update_step(step_index, title, description)

class ErrorFallbackWidget(QLabel):
    """
    Enhanced error widget with improved animations and structured error handling.
    Provides better visual feedback for different error types.
    """
    
    error_dismissed = pyqtSignal(str)  # Signal when error is dismissed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styling()
        self._flash_timer = None
        self._auto_hide_timer = None
        self._current_error_type = None
        self.hide()
        try:
            logger.debug("ErrorFallbackWidget initialized")
        except Exception:
            print("ErrorFallbackWidget initialized")
        
    def _setup_styling(self):
        """Setup enhanced fallback styling with error type support."""
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.hide()
        
    def show_error(self, message: str, error_type: str = "general", auto_hide: bool = True):
        """
        Show error message with appropriate styling and animation.
        
        Args:
            message: Error message to display
            error_type: Type of error (general, processing, io, resource)
            auto_hide: Whether to auto-hide the error after a delay
        """
        try:
            self._current_error_type = error_type
            
            # Stop any existing timers
            if self._flash_timer:
                self._flash_timer.stop()
            if self._auto_hide_timer:
                self._auto_hide_timer.stop()
            
            # Get icon and styling for error type
            icon_map = {
                "resource": ("⚠️", "#f39c12", "#fef9e7"),      # Orange - warning
                "processing": ("❌", "#e74c3c", "#fdedec"),    # Red - error
                "io": ("📁", "#9b59b6", "#f4ecf7"),            # Purple - file issues
                "general": ("⚠️", "#f39c12", "#fef9e7"),       # Orange - general warning
                "network": ("🌐", "#3498db", "#ebf3fd"),       # Blue - network issues
                "validation": ("🔍", "#e67e22", "#fdf2e9")     # Orange - validation errors
            }
            
            icon, border_color, bg_color = icon_map.get(error_type, icon_map["general"])
            
            # Enhanced styling based on error type
            error_style = f"""
                QLabel {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {bg_color}, stop:1 rgba(255, 255, 255, 0.8));
                    color: #2c3e50;
                    border: 2px solid {border_color};
                    border-radius: 10px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 14px;
                    margin: 5px;
                }}
            """
            
            self.setStyleSheet(error_style)
            self.setText(f"{icon} {message}")
            self.show()
            
            # Enhanced flash animation
            self._start_flash_animation()
            
            # Auto-hide timer
            if auto_hide:
                self._auto_hide_timer = QTimer()
                self._auto_hide_timer.setSingleShot(True)
                self._auto_hide_timer.timeout.connect(self._auto_hide)
                
                # Different timeouts based on error severity
                timeout_map = {
                    "processing": 5000,  # 5 seconds for processing errors
                    "resource": 4000,    # 4 seconds for resource errors
                    "io": 4000,          # 4 seconds for I/O errors
                    "general": 3000      # 3 seconds for general errors
                }
                timeout = timeout_map.get(error_type, 3000)
                self._auto_hide_timer.start(timeout)
            
            # Log error display
            try:
                logger.info(f"Error displayed: {error_type} - {message[:50]}")
            except Exception:
                print(f"Error displayed: {error_type} - {message[:50]}")
            
        except Exception as e:
            try:
                logger.error(f"Error showing error widget: {e}")
            except Exception:
                print(f"Error showing error widget: {e}")
            # Minimal fallback
            self.setText(f"⚠️ {message}")
            self.show()

    def _start_flash_animation(self):
        """Start enhanced flash animation with fade effect."""
        try:
            self._flash_count = 0
            self._flash_timer = QTimer()
            self._flash_timer.timeout.connect(self._flash_step)
            self._flash_timer.start(300)  # Flash every 300ms
            
        except Exception as e:
            logger.error(f"Error starting flash animation: {e}")
        
    def _flash_step(self):
        """Execute one step of the flash animation."""
        try:
            self._flash_count += 1
            
            if self._flash_count <= 6:  # Flash 3 times (6 steps)
                self.setVisible(not self.isVisible())
            else:
                self._flash_timer.stop()
                self.show()  # Ensure it's visible after flashing
                
        except Exception as e:
            logger.error(f"Error in flash step: {e}")
            if self._flash_timer:
                self._flash_timer.stop()
            self.show()
    
    def _auto_hide(self):
        """Auto-hide the error message."""
        try:
            self.hide()
            if self._current_error_type:
                self.error_dismissed.emit(self._current_error_type)
                
        except Exception as e:
            logger.error(f"Error in auto-hide: {e}")
            self.hide()
    
    def dismiss_error(self):
        """Manually dismiss the current error."""
        if self._auto_hide_timer:
            self._auto_hide_timer.stop()
        if self._flash_timer:
            self._flash_timer.stop()
        self._auto_hide()

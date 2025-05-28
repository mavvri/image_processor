from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect

class AnimationManager:
    """
    Manages smooth animations for UI components
    """
    
    @staticmethod
    def fade_in(widget, duration=300):
        """Fade in animation"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        return animation
    
    @staticmethod
    def fade_out(widget, duration=300):
        """Fade out animation"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        return animation
    
    @staticmethod
    def slide_in(widget, duration=400):
        """Slide in from top animation"""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        start_pos = widget.pos()
        start_pos.setY(start_pos.y() - 50)
        animation.setStartValue(start_pos)
        animation.setEndValue(widget.pos())
        
        return animation
    
    @staticmethod
    def bounce_in(widget, duration=600):
        """Bounce in animation"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        return animation
    
    @staticmethod
    def create_loading_animation(widget):
        """Create a pulsing loading animation"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(1000)
        animation.setStartValue(0.3)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        animation.setLoopCount(-1)  # Infinite loop
        
        return animation

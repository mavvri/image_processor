import os
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtWidgets import QWidget

class ThemeManager:
    """
    Modern minimalist theme manager with navy blue palette
    """
    
    @staticmethod
    def get_main_theme():
        """Load main application theme from CSS file"""
        css_path = os.path.join(os.path.dirname(__file__), 'main_theme.css')
        try:
            with open(css_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return ThemeManager._get_fallback_theme()
    
    @staticmethod
    def _get_fallback_theme():
        """Fallback theme if CSS file is not found"""
        return """
            /* Fallback Theme - Navy Blue Minimalist */
            QWidget {
                background-color: #f8fafc;
                color: #1e293b;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
                font-size: 13px;
                font-weight: 400;
            }
            
            #Header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e3a8a, stop:1 #3730a3);
                border: none;
                border-radius: 0px;
            }
            
            #AppTitle {
                color: white;
                font-size: 20px;
                font-weight: 600;
                letter-spacing: -0.02em;
            }
        """

class AnimatedWidget(QWidget):
    """Base widget with animation support"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)

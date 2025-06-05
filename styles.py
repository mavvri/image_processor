from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtWidgets import QWidget

class ThemeManager:
    """
    Gestor de temas minimalista y orgánico.
    """
    
    @staticmethod
    def get_organic_theme():
        return """
            /* Reset y base */
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 250, 255, 1), 
                    stop:1 rgba(255, 255, 255, 1));
                color: #2c3e50;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 400;
                line-height: 1.5;
                selection-background-color: rgba(102, 126, 234, 0.3);
            }
            
            /* Sidebar principal */
            #Sidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 255, 255, 0.95), 
                    stop:1 rgba(248, 250, 255, 0.98));
                border: none;
                border-right: 1px solid rgba(102, 126, 234, 0.1);
                border-radius: 0;
                min-width: 280px;
                max-width: 320px;
            }
            
            /* Header Orgánico */
            #Header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 0px;
            }
            
            #AppTitle {
                color: white;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: -0.025em;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #AppSubtitle {
                color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
                font-weight: 400;
                letter-spacing: 0.01em;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Botones Principales Orgánicos */
            #PrimaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #5a67d8);
                border: none;
                border-radius: 16px;
                color: white;
                font-weight: 600;
                font-size: 14px;
                padding: 12px 24px;
                min-width: 120px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #PrimaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c83f2, stop:1 #667eea);
                transform: translateY(-1px);
            }
            
            #PrimaryButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #4c63d2);
            }
            
            /* Paneles Orgánicos */
            #LeftPanel, #RightPanel {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(102, 126, 234, 0.1);
                border-radius: 24px;
                margin: 8px;
            }
            
            /* Contenedor de Imagen */
            #ImageContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8faff, stop:1 #f0f4ff);
                border: 2px dashed rgba(102, 126, 234, 0.3);
                border-radius: 20px;
                min-height: 400px;
            }
            
            #ImageDisplay {
                color: #667eea;
                font-size: 16px;
                font-weight: 500;
                line-height: 1.6;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Panel de Estado */
            #StatusPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(240, 244, 255, 0.9), stop:1 rgba(248, 250, 255, 0.9));
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 16px;
                margin: 8px 0;
            }
            
            #OperationLabel {
                color: #4c63d2;
                font-weight: 500;
                font-size: 14px;
                letter-spacing: 0.01em;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #ProgressIndicator {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 2px;
            }
            
            #CardTitle {
                color: #2c3e50;
                font-weight: 700;
                font-size: 15px;
                margin-bottom: 8px;
                letter-spacing: -0.015em;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #SectionHeader {
                color: #667eea;
                font-weight: 700;
                font-size: 16px;
                margin-bottom: 12px;
                letter-spacing: -0.015em;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Sección de Presets */
            #PresetsSection {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(240, 244, 255, 0.9), stop:1 rgba(248, 250, 255, 0.9));
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 16px;
            }
            
            #PresetDescription {
                color: #4a5568;
                font-size: 12px;
                line-height: 1.6;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                padding: 12px;
                margin-top: 8px;
                border: 1px solid rgba(102, 126, 234, 0.1);
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Controles Modernos */
            QComboBox {
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 20px;
                color: #2c3e50;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            QComboBox:hover {
                border-color: rgba(102, 126, 234, 0.4);
                background: white;
            }
            
            QComboBox:focus {
                border-color: #667eea;
                outline: none;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: rgba(102, 126, 234, 0.2);
                border-left-style: solid;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
                background: rgba(102, 126, 234, 0.05);
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #667eea;
                width: 0;
                height: 0;
            }
            
            /* Sliders Orgánicos */
            QSlider::groove:horizontal {
                background: rgba(102, 126, 234, 0.15);
                height: 6px;
                border-radius: 3px;
                border: none;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #5a67d8);
                border: none;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c83f2, stop:1 #667eea);
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }
            
            #ParamLabel {
                color: #4a5568;
                font-weight: 500;
                font-size: 12px;
                margin: 6px 0;
                letter-spacing: 0.01em;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Botón de Procesamiento */
            #ProcessButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #48bb78, stop:1 #38a169);
                border: none;
                border-radius: 18px;
                color: white;
                font-weight: 700;
                font-size: 15px;
                letter-spacing: 0.01em;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #ProcessButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #68d391, stop:1 #48bb78);
            }
            
            #ProcessButton:disabled {
                background: #e2e8f0;
                color: #a0aec0;
            }
            
            /* Botones Secundarios */
            #SecondaryButton {
                background: rgba(248, 250, 252, 0.95);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 12px;
                color: #2c3e50;
                font-weight: 600;
                padding: 10px 16px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #SecondaryButton:hover {
                background: white;
                border-color: rgba(102, 126, 234, 0.3);
            }
            
            /* Botones de Acción */
            #TertiaryButton, #StopButton, #SaveButton, #InfoButton {
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 10px;
                color: #4a5568;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #TertiaryButton:hover, #StopButton:hover, #SaveButton:hover, #InfoButton:hover {
                background: white;
                border-color: #667eea;
                color: #667eea;
            }
            
            #StopButton {
                background: rgba(255, 107, 107, 0.1);
                border-color: rgba(255, 107, 107, 0.3);
                color: #e53e3e;
            }
            
            #StopButton:hover {
                background: rgba(255, 107, 107, 0.2);
                border-color: #e53e3e;
            }
            
            #SaveButton {
                background: rgba(237, 137, 54, 0.1);
                border-color: rgba(237, 137, 54, 0.3);
                color: #dd6b20;
            }
            
            #SaveButton:hover {
                background: rgba(237, 137, 54, 0.2);
                border-color: #dd6b20;
            }
            
            /* Barra de Estado */
            #StatusBar {
                background: rgba(248, 250, 252, 0.95);
                border-top: 1px solid rgba(102, 126, 234, 0.1);
            }
            
            #StatusLabel {
                color: #4a5568;
                font-size: 12px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Contenedor de Resultados */
            #ResultsContainer {
                background: rgba(248, 250, 252, 0.95);
                border: 1px solid rgba(102, 126, 234, 0.15);
                border-radius: 16px;
            }
            
            #ResultsText {
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(102, 126, 234, 0.1);
                border-radius: 12px;
                color: #2c3e50;
                font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.6;
                padding: 12px;
            }
            
            /* Pestañas Orgánicas */
            QTabWidget::pane {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(102, 126, 234, 0.15);
                border-radius: 16px;
                top: -1px;
            }
            
            QTabWidget::tab-bar {
                left: 12px;
            }
            
            QTabBar::tab {
                background: rgba(248, 250, 252, 0.9);
                border: 1px solid rgba(102, 126, 234, 0.15);
                color: #4a5568;
                font-weight: 600;
                margin-right: 4px;
                padding: 12px 20px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: none;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 0.95);
                color: #667eea;
                border-color: rgba(102, 126, 234, 0.2);
                border-bottom: 2px solid #667eea;
            }
            
            QTabBar::tab:hover {
                background: rgba(255, 255, 255, 0.95);
                color: #2c3e50;
            }
            
            /* Checkbox Orgánico */
            QCheckBox {
                color: #2c3e50;
                font-weight: 500;
                spacing: 8px;
                font-size: 13px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 6px;
                background: rgba(255, 255, 255, 0.95);
            }
            
            QCheckBox::indicator:checked {
                background: #667eea;
                border-color: #667eea;
            }
            
            QCheckBox::indicator:hover {
                border-color: #667eea;
            }
            
            /* SpinBox Orgánico */
            QSpinBox {
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 10px;
                color: #2c3e50;
                font-size: 13px;
                padding: 6px 10px;
                min-height: 18px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            QSpinBox:hover {
                border-color: rgba(102, 126, 234, 0.4);
                background: white;
            }
            
            QSpinBox:focus {
                border-color: #667eea;
                outline: none;
            }
            
            /* === VENTANA DE INFORMACIÓN REDISEÑADA === */
            
            /* Ventana Principal de Información */
            #InfoWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.98), 
                    stop:1 rgba(248, 250, 255, 0.98));
                border: 1px solid rgba(102, 126, 234, 0.15);
                border-radius: 24px;
                padding: 0px;
            }
            
            /* Header de la Ventana de Información */
            #InfoHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 24px 24px 0px 0px;
                padding: 20px 24px;
                border: none;
            }
            
            /* Título Principal */
            #InfoTitle {
                color: white;
                font-size: 20px;
                font-weight: 700;
                letter-spacing: -0.02em;
                margin: 0px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Subtítulo */
            #InfoSubtitle {
                color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
                font-weight: 400;
                letter-spacing: 0.005em;
                margin-top: 4px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Botón de Cerrar */
            #CloseButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                color: white;
                font-size: 18px;
                font-weight: 700;
                padding: 6px;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #CloseButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.4);
                transform: scale(1.05);
            }
            
            #CloseButton:pressed {
                background: rgba(255, 255, 255, 0.1);
                transform: scale(0.95);
            }
            
            /* === TABS DE IMÁGENES === */
            
            /* Contenedor principal de tabs de imagen */
            #ImageTabWidget {
                background: transparent;
                border: none;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #ImageTabWidget::pane {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8faff, stop:1 #f0f4ff);
                border: 2px dashed rgba(102, 126, 234, 0.3);
                border-radius: 20px;
                top: -1px;
                padding: 4px;
                margin-top: 20px;
            }
            
            #ImageTabWidget::tab-bar {
                left: 8px;
                top: 8px;
            }
            
            /* Pestañas de imagen */
            #ImageTabWidget QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9), 
                    stop:1 rgba(248, 250, 255, 0.9));
                border: 1px solid rgba(102, 126, 234, 0.2);
                color: #4a5568;
                font-weight: 600;
                font-size: 12px;
                margin-right: 2px;
                padding: 8px 16px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: none;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
                min-width: 100px;
                max-width: 200px;
            }
            
            #ImageTabWidget QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 white, 
                    stop:1 rgba(255, 255, 255, 0.95));
                color: #667eea;
                border-color: rgba(102, 126, 234, 0.3);
                border-bottom: 2px solid #667eea;
                font-weight: 700;
                margin-top: -2px;
                z-index: 1;
            }
            
            #ImageTabWidget QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95), 
                    stop:1 rgba(248, 250, 255, 0.95));
                color: #2c3e50;
                border-color: rgba(102, 126, 234, 0.3);
            }
            
            /* Botón de cerrar en las pestañas */
            #ImageTabWidget QTabBar::close-button {
                background: rgba(255, 107, 107, 0.2);
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: 8px;
                width: 16px;
                height: 16px;
                margin: 2px 4px 2px 8px;
                subcontrol-position: right;
            }
            
            #ImageTabWidget QTabBar::close-button:hover {
                background: rgba(255, 107, 107, 0.4);
                border-color: #e53e3e;
            }
            
            /* Contenido de cada pestaña de imagen */
            #ImageTab {
                background: transparent;
                border: none;
                border-radius: 16px;
                margin: 4px;
            }
            
            /* Display de imagen individual */
            #ImageDisplay_Tab {
                background: transparent;
                border: none;
                border-radius: 16px;
                color: #667eea;
                font-size: 16px;
                font-weight: 500;
                line-height: 1.6;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
                min-height: 350px;
            }
            
            /* Etiquetas de estado de pestaña */
            #TabStatusLabel {
                color: #667eea;
                font-size: 11px;
                font-weight: 600;
                background: rgba(102, 126, 234, 0.1);
                border-radius: 8px;
                padding: 4px 8px;
                margin: 4px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            /* Botones de acción en pestañas */
            #TabActionButton {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 8px;
                color: #4a5568;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 8px;
                margin: 2px;
                min-width: 24px;
                max-width: 24px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
            
            #TabActionButton:hover {
                background: white;
                border-color: #667eea;
                color: #667eea;
            }
            
            /* Tooltip personalizado para pestañas */
            QToolTip {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.98), 
                    stop:1 rgba(248, 250, 255, 0.98));
                border: 1px solid rgba(102, 126, 234, 0.2);
                border-radius: 8px;
                color: #2c3e50;
                font-size: 11px;
                font-weight: 500;
                padding: 6px 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            }
        """

class AnimatedWidget(QWidget):
    """Widget con soporte para animaciones suaves"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)

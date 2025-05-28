from .formula_renderer import FormulaRenderer

class FilterInfoTemplates:
    """
    HTML templates for filter information with mathematical formulas
    """
    
    @staticmethod
    def get_base_template():
        """Get base HTML template with styling"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            {FormulaRenderer.get_formula_css()}
            <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
                line-height: 1.6;
                color: #1e293b;
                background: #f8fafc;
                margin: 0;
                padding: 20px;
            }}
            
            .filter-category {{
                margin: 24px 0;
                padding: 20px;
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }}
            
            .category-title {{
                color: #1d4ed8;
                font-size: 20px;
                font-weight: 700;
                margin-bottom: 20px;
                padding-bottom: 8px;
                border-bottom: 2px solid #1d4ed8;
            }}
            
            .filter-item {{
                margin: 16px 0;
                padding: 16px;
                background: #f8fafc;
                border-radius: 12px;
                border-left: 4px solid #64748b;
            }}
            
            .filter-name {{
                color: #1e40af;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 12px;
            }}
            
            .filter-description {{
                color: #475569;
                font-size: 14px;
                margin: 8px 0;
                line-height: 1.6;
            }}
            
            .applications {{
                background: rgba(29, 78, 216, 0.05);
                padding: 12px;
                border-radius: 8px;
                margin-top: 12px;
                border: 1px solid rgba(29, 78, 216, 0.1);
            }}
            
            .applications-title {{
                color: #1d4ed8;
                font-weight: 600;
                font-size: 13px;
                margin-bottom: 8px;
            }}
            
            .applications-list {{
                color: #64748b;
                font-size: 12px;
                line-height: 1.5;
            }}
            
            .complexity-badge {{
                display: inline-block;
                padding: 4px 8px;
                background: #fef3c7;
                color: #92400e;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                margin-left: 8px;
            }}
            </style>
        </head>
        <body>
            {{content}}
        </body>
        </html>
        """
    
    @staticmethod
    def get_preprocessing_filters():
        """Get preprocessing filters information"""
        filters = {
            "Promediador": {
                "formula": "H(x,y) = <div class='fraction'><span class='numerator'>1</span><span class='denominator'>n²</span></div> <span class='sigma'>Σ</span><sub>i,j</sub> I(x+i, y+j)",
                "description": "Reduce el ruido mediante el promedio local de píxeles en una ventana de tamaño n×n. Es efectivo contra ruido gaussiano pero puede difuminar bordes.",
                "complexity": "O(n²)",
                "applications": [
                    "Reducción de ruido en fotografías digitales",
                    "Preprocesamiento para sistemas de OCR",
                    "Suavizado de texturas en imágenes naturales",
                    "Mejora de imágenes con ruido de sensor"
                ]
            },
            "Promediador Pesado": {
                "formula": "W = <div class='fraction'><span class='numerator'>1</span><span class='denominator'>16</span></div> × [1,2,1; 2,4,2; 1,2,1]",
                "description": "Aplicación de un kernel gaussiano discreto que asigna mayor peso al píxel central. Preserva mejor los bordes que el promedio simple.",
                "complexity": "O(1)",
                "applications": [
                    "Suavizado selectivo manteniendo detalles",
                    "Reducción de ruido con preservación de bordes",
                    "Preprocesamiento de imágenes médicas",
                    "Mejora de calidad en imágenes de baja resolución"
                ]
            },
            "Mediana": {
                "formula": "I<sub>out</sub>(x,y) = median{I(x+i,y+j) | (i,j) ∈ W}",
                "description": "Reemplaza cada píxel por la mediana de su vecindario. Excelente para eliminar ruido impulsivo (sal y pimienta) mientras preserva bordes.",
                "complexity": "O(n² log n)",
                "applications": [
                    "Eliminación de ruido sal y pimienta",
                    "Preservación de bordes en imágenes ruidosas",
                    "Limpieza de imágenes binarias",
                    "Restauración de imágenes dañadas"
                ]
            },
            "Bilateral": {
                "formula": "G(x,y) = exp(-<div class='fraction'><span class='numerator'>||x-y||²</span><span class='denominator'>2σ<sub>s</sub>²</span></div>) × exp(-<div class='fraction'><span class='numerator'>||I(x)-I(y)||²</span><span class='denominator'>2σ<sub>r</sub>²</span></div>)",
                "description": "Combina filtrado espacial y radiométrico. Preserva bordes mientras suaviza áreas homogéneas, considerando tanto la distancia espacial como la similitud de intensidad.",
                "complexity": "O(n²)",
                "applications": [
                    "Reducción de ruido con preservación de bordes",
                    "Preprocesamiento para segmentación",
                    "Mejora de imágenes naturales",
                    "Suavizado selectivo en fotografía"
                ]
            },
            "Gaussiano": {
                "formula": "G(x,y) = <div class='fraction'><span class='numerator'>1</span><span class='denominator'>2πσ²</span></div> exp(-<div class='fraction'><span class='numerator'>x²+y²</span><span class='denominator'>2σ²</span></div>)",
                "description": "Filtro basado en la distribución gaussiana. Proporciona suavizado natural y progresivo, ampliamente usado como paso previo a la detección de bordes.",
                "complexity": "O(n²)",
                "applications": [
                    "Desenfoques artísticos controlados",
                    "Reducción de ruido de alta frecuencia",
                    "Preparación para detección de bordes Canny",
                    "Creación de pirámides gaussianas"
                ]
            }
        }
        
        return FilterInfoTemplates._format_filter_category("🔧 Filtros de Preprocesamiento", filters)
    
    @staticmethod
    def get_edge_detection_filters():
        """Get edge detection filters information"""
        filters = {
            "Roberts": {
                "formula": "|∇I| = √[(I(x,y)-I(x+1,y+1))² + (I(x+1,y)-I(x,y+1))²]",
                "description": "Operador 2×2 simple y computacionalmente eficiente. Detecta bordes diagonales mediante gradientes cruzados.",
                "complexity": "O(1)",
                "applications": [
                    "Detección rápida de bordes en tiempo real",
                    "Aplicaciones embebidas con recursos limitados",
                    "Análisis básico de formas geométricas",
                    "Preprocesamiento para algoritmos de seguimiento"
                ]
            },
            "Prewitt": {
                "formula": "G<sub>x</sub> = [-1,0,1; -1,0,1; -1,0,1], G<sub>y</sub> = [-1,-1,-1; 0,0,0; 1,1,1]",
                "description": "Detecta gradientes horizontales y verticales asignando igual peso a todos los píxeles del borde del kernel.",
                "complexity": "O(1)",
                "applications": [
                    "Detección de bordes en imágenes ruidosas",
                    "Análisis de texturas direccionales",
                    "Segmentación básica de objetos",
                    "Extracción de características geométricas"
                ]
            },
            "Sobel": {
                "formula": "G<sub>x</sub> = [-1,0,1; -2,0,2; -1,0,1], G<sub>y</sub> = [-1,-2,-1; 0,0,0; 1,2,1]",
                "description": "Versión mejorada del operador Prewitt con mayor peso en el píxel central, proporcionando mejor detección de bordes.",
                "complexity": "O(1)",
                "applications": [
                    "Detección robusta de bordes",
                    "Análisis de formas y contornos",
                    "Preprocesamiento para segmentación",
                    "Extracción de características en visión artificial"
                ]
            },
            "Kirsch": {
                "formula": "R = max|K<sub>i</sub> * I| para i=1..8 direcciones",
                "description": "Detecta bordes en 8 direcciones diferentes usando kernels direccionales. Muy sensible a la orientación de los bordes.",
                "complexity": "O(8)",
                "applications": [
                    "Detección direccional de bordes",
                    "Análisis de texturas orientadas",
                    "Reconocimiento de patrones direccionales",
                    "Clasificación de orientación de objetos"
                ]
            },
            "Canny": {
                "formula": "∇I = √[(∂I/∂x)² + (∂I/∂y)²] + supresión no-máxima + histéresis",
                "description": "Algoritmo multi-etapa considerado óptimo. Incluye suavizado gaussiano, cálculo de gradientes, supresión no-máxima e histéresis.",
                "complexity": "O(n²)",
                "applications": [
                    "Detección óptima de bordes",
                    "Visión por computador avanzada",
                    "Análisis de formas complejas",
                    "Sistemas de navegación autónoma"
                ]
            },
            "Laplaciano": {
                "formula": "∇²I = ∂²I/∂x² + ∂²I/∂y²",
                "description": "Operador de segunda derivada que detecta cambios de intensidad en todas las direcciones simultáneamente.",
                "complexity": "O(1)",
                "applications": [
                    "Detección de bordes finos",
                    "Realce de detalles en imágenes",
                    "Análisis de texturas isotrópicas",
                    "Detección de puntos de interés"
                ]
            }
        }
        
        return FilterInfoTemplates._format_filter_category("🎯 Filtros de Detección de Bordes", filters)
    
    @staticmethod
    def get_segmentation_methods():
        """Get segmentation methods information"""
        methods = {
            "Umbral Media": {
                "formula": "T = <div class='fraction'><span class='numerator'>1</span><span class='denominator'>MN</span></div> <span class='sigma'>Σ</span><sub>x=0</sub><sup>M-1</sup> <span class='sigma'>Σ</span><sub>y=0</sub><sup>N-1</sup> I(x,y)",
                "description": "Método de umbralización más simple que usa la intensidad media de toda la imagen como umbral de separación.",
                "complexity": "O(MN)",
                "applications": [
                    "Segmentación básica en imágenes bimodales",
                    "Binarización rápida para análisis inicial",
                    "Separación fondo-objeto simple",
                    "Preprocesamiento para algoritmos más complejos"
                ]
            },
            "Método de Otsu": {
                "formula": "σ²<sub>w</sub>(t) = w<sub>1</sub>(t)σ²<sub>1</sub>(t) + w<sub>2</sub>(t)σ²<sub>2</sub>(t)",
                "description": "Maximiza la varianza inter-clase para encontrar automáticamente el umbral óptimo. Asume distribución bimodal del histograma.",
                "complexity": "O(L×MN)",
                "applications": [
                    "Segmentación automática sin parámetros",
                    "Binarización adaptativa de documentos",
                    "Análisis de imágenes médicas",
                    "Control de calidad industrial"
                ]
            },
            "Multiumbralización": {
                "formula": "Minimiza <span class='sigma'>Σ</span><sub>i=1</sub><sup>k</sup> w<sub>i</sub>σ<sub>i</sub>² para k clases",
                "description": "Extensión del método de Otsu para múltiples clases, encontrando varios umbrales óptimos simultáneamente.",
                "complexity": "O(L^k×MN)",
                "applications": [
                    "Segmentación de múltiples objetos",
                    "Análisis de imágenes complejas",
                    "Clasificación automática de tejidos",
                    "Segmentación de imágenes satelitales"
                ]
            },
            "Entropía de Kapur": {
                "formula": "H = -<span class='sigma'>Σ</span><sub>i</sub> p<sub>i</sub> log<sub>2</sub>(p<sub>i</sub>), maximiza H<sub>total</sub>",
                "description": "Selecciona el umbral que maximiza la entropía total de las regiones segmentadas, útil para imágenes complejas.",
                "complexity": "O(L×MN)",
                "applications": [
                    "Imágenes con múltiples intensidades",
                    "Segmentación de texturas complejas",
                    "Análisis biomédico avanzado",
                    "Procesamiento de imágenes naturales"
                ]
            },
            "Umbral Adaptativo": {
                "formula": "T(x,y) = μ(x,y) - C",
                "description": "Umbral variable que se adapta a las condiciones locales de iluminación en cada región de la imagen.",
                "complexity": "O(w²×MN)",
                "applications": [
                    "Documentos con iluminación irregular",
                    "Imágenes con sombras variables",
                    "OCR robusto en condiciones adversas",
                    "Análisis de imágenes históricas"
                ]
            }
        }
        
        return FilterInfoTemplates._format_filter_category("✂️ Métodos de Segmentación", methods)
    
    @staticmethod
    def _format_filter_category(title, filters):
        """Format a category of filters into HTML"""
        content = f'<div class="filter-category"><h2 class="category-title">{title}</h2>'
        
        for name, info in filters.items():
            formula_html = FormulaRenderer.render_formula(
                FormulaRenderer.convert_latex_to_html(info['formula']),
                f"Complejidad: {info['complexity']}"
            )
            
            applications_html = '<br>'.join([f"• {app}" for app in info['applications']])
            
            content += f"""
            <div class="filter-item">
                <div class="filter-name">
                    🔹 {name}
                    <span class="complexity-badge">{info['complexity']}</span>
                </div>
                {formula_html}
                <div class="filter-description">{info['description']}</div>
                <div class="applications">
                    <div class="applications-title">🎯 Aplicaciones:</div>
                    <div class="applications-list">{applications_html}</div>
                </div>
            </div>
            """
        
        content += '</div>'
        return content
    
    @staticmethod
    def get_complete_info():
        """Get complete filter information"""
        preprocessing = FilterInfoTemplates.get_preprocessing_filters()
        edge_detection = FilterInfoTemplates.get_edge_detection_filters()
        segmentation = FilterInfoTemplates.get_segmentation_methods()
        
        complete_content = f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1d4ed8; font-size: 24px; font-weight: 800; margin-bottom: 8px;">
                📚 Guía Completa de Procesamiento Digital de Imágenes
            </h1>
            <p style="color: #64748b; font-size: 14px; font-weight: 500;">
                Fundamentos Matemáticos y Aplicaciones Prácticas • Versión 3.2
            </p>
        </div>
        {preprocessing}
        {edge_detection}
        {segmentation}
        """
        
        return FilterInfoTemplates.get_base_template().format(content=complete_content)

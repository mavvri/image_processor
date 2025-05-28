class IntelligentPresets:
    """
    Presets inteligentes con fundamentos matemáticos y aplicaciones específicas.
    """
    
    @staticmethod
    def get_presets():
        """Obtener todos los presets con sus explicaciones matemáticas"""
        return {
            "📄 Documentos y Texto": {
                "description": "Optimizado para documentos escaneados y texto",
                "math_explanation": """
                📐 Fundamento Matemático:
                • Filtro Bilateral: G(x,y) = exp(-||x-y||²/2σs²) × exp(-||I(x)-I(y)||²/2σr²)
                  Preserva bordes del texto mientras reduce ruido de fondo
                • Canny: ∇I = √[(∂I/∂x)² + (∂I/∂y)²] con supresión no-máxima
                  Detecta contornos precisos de caracteres
                • Umbral Adaptativo: T(x,y) = μ(x,y) - C
                  Se adapta a variaciones de iluminación en el documento
                
                🎯 Aplicación: OCR, digitalización de libros, análisis de formularios
                """,
                "filters": {
                    "preprocess": "Bilateral",
                    "edge": "Canny", 
                    "segmentation": "Umbral Adaptativo"
                },
                "params": {
                    "sigma_color": 50,
                    "sigma_space": 50,
                    "threshold1": 50,
                    "threshold2": 150,
                    "block_size": 11,
                    "C": 2
                }
            },
            
            "🔴 Objetos Circulares": {
                "description": "Ideal para monedas, células, partículas, botones",
                "math_explanation": """
                📐 Fundamento Matemático:
                • Gaussiano: G(x,y) = (1/2πσ²)exp(-(x²+y²)/2σ²)
                  Reduce ruido preservando estructuras circulares
                • Kirsch: R = max|Ki * I| para i=1..8 direcciones
                  Detecta contornos circulares uniformemente en todas direcciones
                • Otsu: σ²w(t) = w₁(t)σ²₁(t) + w₂(t)σ²₂(t)
                  Maximiza varianza inter-clase para separación automática
                
                🎯 Aplicación: Conteo de monedas, análisis celular, QC industrial
                """,
                "filters": {
                    "preprocess": "Gaussiano",
                    "edge": "Kirsch",
                    "segmentation": "Método de Otsu"
                },
                "params": {
                    "kernel_size": 5,
                    "sigma": 1.0,
                    "threshold": 30
                }
            },
            
            "🧬 Análisis Biomédico": {
                "description": "Muestras biológicas, células, tejidos",
                "math_explanation": """
                📐 Fundamento Matemático:
                • Bilateral: Combina dominio espacial y radiométrico
                  Preserva membranas celulares y estructuras delicadas
                • Laplaciano: ∇²I = ∂²I/∂x² + ∂²I/∂y²
                  Resalta bordes finos y detalles internos celulares
                • Kapur: H = -Σpi log₂(pi), maximiza entropía total
                  Óptimo para muestras con múltiples intensidades
                
                🎯 Aplicación: Histología, citología, análisis de tejidos
                """,
                "filters": {
                    "preprocess": "Bilateral",
                    "edge": "Laplaciano",
                    "segmentation": "Entropía de Kapur"
                },
                "params": {
                    "sigma_color": 40,
                    "sigma_space": 40
                }
            },
            
            "🏭 Control de Calidad": {
                "description": "Defectos en productos manufacturados",
                "math_explanation": """
                📐 Fundamento Matemático:
                • Promediador: H(x,y) = (1/n²)Σᵢⱼ I(x+i,y+j)
                  Estabiliza iluminación industrial variable
                • Roberts: |∇I| = √[(I(x,y)-I(x+1,y+1))² + (I(x+1,y)-I(x,y+1))²]
                  Detecta defectos con gradientes mínimos y precisos
                • Umbral Banda: Tₘᵢₙ ≤ I(x,y) ≤ Tₘₐₓ
                  Selecciona rangos específicos de defectos conocidos
                
                🎯 Aplicación: Inspección automática, detección de grietas, QA
                """,
                "filters": {
                    "preprocess": "Promediador",
                    "edge": "Roberts",
                    "segmentation": "Umbral Banda"
                },
                "params": {
                    "kernel_size": 7,
                    "band_min": 60,
                    "band_max": 180
                }
            },
            
            "🎨 Texturas Complejas": {
                "description": "Materiales, superficies, patrones",
                "math_explanation": """
                📐 Fundamento Matemático:
                • Mediana: Iₒᵤₜ(x,y) = median{I(x+i,y+j) | (i,j) ∈ W}
                  Elimina ruido impulsivo preservando texturas
                • Sobel: Gₓ = [-1,0,1; -2,0,2; -1,0,1], Gᵧ = [-1,-2,-1; 0,0,0; 1,2,1]
                  Detecta gradientes direccionales en texturas complejas
                • Multi-Otsu: Minimiza Σwᵢσᵢ² para múltiples clases
                  Segmenta diferentes regiones texturales automáticamente
                
                🎯 Aplicación: Análisis de materiales, clasificación de superficies
                """,
                "filters": {
                    "preprocess": "Mediana",
                    "edge": "Sobel", 
                    "segmentation": "Multiumbralización"
                },
                "params": {
                    "kernel_size": 5,
                    "num_classes": 4
                }
            },
            
            "🔬 Microscopía Avanzada": {
                "description": "Imágenes de alta resolución, estructuras finas",
                "math_explanation": """
                📐 Fundamento Matemático:
                • Promediador Pesado: W = [1,2,1; 2,4,2; 1,2,1]/16
                  Suavizado direccional que preserva estructuras microscópicas
                • Prewitt: Combina gradientes horizontales y verticales
                  Óptimo para estructuras lineales y fibrilares
                • Mínimo Histograma: Encuentra valles en h(i)
                  Identifica separaciones naturales en intensidades
                
                🎯 Aplicación: Microscopía electrónica, análisis de nanomateriales
                """,
                "filters": {
                    "preprocess": "Promediador Pesado",
                    "edge": "Prewitt",
                    "segmentation": "Mínimo del Histograma"
                },
                "params": {
                    "kernel_size": 3
                }
            },
            
            "⚡ Procesamiento Rápido": {
                "description": "Análisis en tiempo real, aplicaciones móviles",
                "math_explanation": """
                📐 Fundamento Matemático:
                • Sin preprocesamiento: Minimiza tiempo computacional
                • Roberts: Operador 2×2 más eficiente O(n²) vs O(9n²)
                • Umbral Media: T = (1/MN)ΣΣI(x,y)
                  Cálculo directo sin iteraciones, óptimo para velocidad
                
                🎯 Aplicación: Apps móviles, sistemas embebidos, tiempo real
                """,
                "filters": {
                    "preprocess": "Ninguno",
                    "edge": "Roberts",
                    "segmentation": "Umbral Media"
                },
                "params": {}
            }
        }

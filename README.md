# Sistema de Conteo de Coches

Sistema de escritorio para detectar y contar coches en imágenes estáticas utilizando técnicas de procesamiento digital de imágenes.

## Requisitos del Sistema

- Windows 10 o superior
- Python 3.7 o superior
- Al menos 4GB de RAM
- 500MB de espacio libre en disco

## Instalación

1. **Configurar el entorno virtual y dependencias:**
   ```
   setup_venv.bat
   ```
   Este script creará un entorno virtual e instalará todas las dependencias necesarias.

2. **Ejecutar la aplicación:**
   ```
   run_app.bat
   ```
   Este script activará el entorno virtual y ejecutará la aplicación.

## Uso

1. Ejecute `run_app.bat` para iniciar la aplicación
2. Use "Cargar Imagen" o el menú "Archivo > Abrir Imagen..." para seleccionar una imagen
3. Haga clic en "Procesar Imagen" para iniciar el análisis
4. El resultado mostrará la imagen procesada y el conteo de coches

## Formatos de Imagen Soportados

- JPEG (.jpg, .jpeg)
- PNG (.png)

## Estructura del Proyecto

```
final_project/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── threads/
│   │   ├── __init__.py
│   │   └── processing_thread.py
│   └── ui/
│       ├── __init__.py
│       ├── assets/
│       │   └── styles/
│       └── main_window.py
├── venv/                    # Entorno virtual (creado por setup_venv.bat)
├── main.py
├── setup_venv.bat          # Script de configuración
├── run_app.bat             # Script de ejecución
├── requirements.txt        # Dependencias
└── README.md
```

## Resolución de Problemas

- Si Python no es reconocido, asegúrese de que esté instalado y agregado al PATH
- Si hay errores de dependencias, ejecute nuevamente `setup_venv.bat`
- Para problemas de permisos, ejecute los scripts como administrador
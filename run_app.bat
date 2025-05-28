@echo off
REM Batch file para ejecutar la aplicación de Procesamiento Digital de Imágenes
REM Activa el entorno virtual y ejecuta la aplicación

echo ========================================
echo  Procesamiento Digital de Imágenes
echo  Sistema Orgánico Minimalista v3.1
echo ========================================
echo.

REM Verificar si existe el directorio del entorno virtual
if not exist "venv" (
    echo [ERROR] No se encontró el entorno virtual 'venv'
    echo Por favor, asegúrate de que el entorno virtual esté creado en este directorio.
    echo.
    echo Para crear el entorno virtual, ejecuta:
    echo python -m venv venv
    echo venv\Scripts\activate
    echo pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Verificar si existe el archivo de activación
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] El entorno virtual parece estar corrupto
    echo No se encontró venv\Scripts\activate.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar que la activación fue exitosa
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo [INFO] Entorno virtual activado correctamente
echo.

REM Verificar si existe el archivo principal de la aplicación
if not exist "code.py" (
    echo [ERROR] No se encontró el archivo principal 'code.py'
    echo Asegúrate de que todos los archivos estén en el directorio correcto.
    echo.
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...
python -c "import PyQt6, numpy, cv2" 2>nul
if errorlevel 1 (
    echo [WARNING] Algunas dependencias pueden estar faltando
    echo Instalando dependencias requeridas...
    echo.
    pip install PyQt6 numpy opencv-python
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo [INFO] Dependencias verificadas
echo.

echo [INFO] Iniciando aplicación...
echo ========================================
echo.

REM Ejecutar la aplicación
python code.py

REM Verificar si hubo algún error al ejecutar la aplicación
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] La aplicación terminó con errores
    echo Revisa los mensajes anteriores para más información
    echo ========================================
) else (
    echo.
    echo ========================================
    echo [INFO] Aplicación cerrada correctamente
    echo ========================================
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul

REM Desactivar el entorno virtual al salir
deactivate

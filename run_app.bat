
@echo off
setlocal

set PROJECT_DIR=""
set VENV_NAME=venv

echo Starting Car Counting System...

cd /D "%PROJECT_DIR%"
if errorlevel 1 (
    echo Failed to change directory to %PROJECT_DIR%.
    echo Error Code: %errorlevel%
    echo Please ensure the project directory exists.
    pause
    exit /b 1
)

if not exist "%VENV_NAME%\Scripts\activate.bat" (
    echo Virtual environment not found.
    echo Error Code: 2
    echo Please run setup_venv.bat first to create the virtual environment.
    pause
    exit /b 2
)

if not exist "main.py" (
    echo main.py not found.
    echo Error Code: 3
    echo Please ensure the project files are in place.
    pause
    exit /b 3
)

echo Activating virtual environment...
call "%VENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    echo Error Code: %errorlevel%
    pause
    exit /b 4
)

echo Running application...
echo Debug: Checking Python version...
python --version
echo Debug: Checking if modules are available...
python -c "import sys; print('Python path:', sys.executable)"
python -c "try: import PyQt5; print('PyQt5: OK'); except ImportError: print('PyQt5: MISSING')"
python -c "try: import cv2; print('OpenCV: OK'); except ImportError: print('OpenCV: MISSING')"
echo Debug: Starting main.py...
python main.py
set APP_EXIT_CODE=%errorlevel%
echo Debug: Python application exit code: %APP_EXIT_CODE%
if %APP_EXIT_CODE% neq 0 (
    echo.
    echo ============================================
    echo APPLICATION ERROR DETECTED
    echo ============================================
    echo Application exited with error code: %APP_EXIT_CODE%
    echo.
    if %APP_EXIT_CODE% equ 1 (
        echo Possible causes:
        echo - Python syntax error in the code
        echo - Missing dependencies
        echo - Import errors
    ) else if %APP_EXIT_CODE% equ 2 (
        echo Possible causes:
        echo - KeyboardInterrupt ^(Ctrl+C^)
        echo - User terminated the application
    ) else (
        echo Unexpected error occurred
        echo Check the error messages above for details
    )
    echo.
    echo ============================================
    pause
    exit /b %APP_EXIT_CODE%
) else (
    echo Application closed normally.
    echo Press any key to close this window...
    pause >nul
)

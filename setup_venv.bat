@echo off
setlocal

set PROJECT_DIR=
set VENV_NAME=venv

echo Setting up virtual environment for Car Counting System...
cd /D "%PROJECT_DIR%"
if errorlevel 1 (
    echo Failed to change directory to %PROJECT_DIR%.
    echo Please ensure the project directory exists.
    pause
    exit /b 1
)

echo Checking if Python is installed...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7+ and add it to your PATH.
    pause
    exit /b 1
)

echo Creating virtual environment...
if exist "%VENV_NAME%" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q "%VENV_NAME%"
)

python -m venv %VENV_NAME%
if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call "%VENV_NAME%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
echo Installing PyQt5...
pip install PyQt5
if errorlevel 1 (
    echo Failed to install PyQt5.
    pause
    exit /b 1
)

echo Installing OpenCV...
pip install opencv-python
if errorlevel 1 (
    echo Failed to install OpenCV.
    pause
    exit /b 1
)

echo Installing NumPy...
pip install numpy
if errorlevel 1 (
    echo Failed to install NumPy.
    pause
    exit /b 1
)

echo Installing additional dependencies...
pip install Pillow
if errorlevel 1 (
    echo Warning: Failed to install Pillow, but continuing...
)

echo.
echo Creating requirements.txt file...
pip freeze > requirements.txt

echo.
echo Virtual environment setup complete!
echo Location: %PROJECT_DIR%\%VENV_NAME%
echo.
echo Dependencies installed:
pip list | findstr -i "pyqt5 opencv numpy pillow"
echo.
echo You can now run the application using run_app.bat
pause

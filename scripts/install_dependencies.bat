@echo off
echo Z-Waifu Launcher Dependency Installer
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking project structure...
echo.

REM Check if we're in the right directory structure
if not exist "..\zwaifu_launcher_gui.py" (
    echo ERROR: zwaifu_launcher_gui.py not found in parent directory
    echo Please run this script from the scripts directory
    pause
    exit /b 1
)

if not exist "..\config\requirements.txt" (
    echo ERROR: config\requirements.txt not found
    echo Please ensure the project structure is correct
    pause
    exit /b 1
)

echo Project structure looks good!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

REM Install dependencies from requirements.txt
echo.
echo Installing dependencies from requirements.txt...
python -m pip install -r "..\config\requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo You may need to install them manually
    pause
    exit /b 1
)

echo.
echo Testing imports...
python -c "import psutil, PIL, pystray, flask, flask_socketio, flask_cors, matplotlib, numpy, requests, qrcode; print('All imports successful!')"
if errorlevel 1 (
    echo WARNING: Some imports failed, but the launcher may still work
    echo You can try running the launcher anyway
) else (
    echo All dependencies installed and tested successfully!
)

echo.
echo Installation completed!
echo You can now run the launcher:
echo 1. python ..\zwaifu_launcher_gui.py
echo 2. python ..\launch_launcher.py
echo 3. Double-click ..\launch_launcher.bat
echo.
pause 
@echo off
echo Z-Waifu Launcher
echo ================
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

REM Check if required files exist
if not exist "zwaifu_launcher_gui.py" (
    echo ERROR: zwaifu_launcher_gui.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "config\requirements.txt" (
    echo ERROR: config\requirements.txt not found
    echo Please ensure the project structure is correct
    pause
    exit /b 1
)

if not exist "launch_launcher.py" (
    echo ERROR: launch_launcher.py not found
    echo Please ensure the project structure is correct
    pause
    exit /b 1
)

echo Project structure looks good!
echo.

REM Run the launch script which will handle everything automatically
echo Starting Z-Waifu Launcher with automatic setup...
echo This will:
echo - Check Python version
echo - Create virtual environment if needed
echo - Install dependencies automatically
echo - Launch the GUI
echo.

python launch_launcher.py

REM Check if the launcher script ran successfully
if errorlevel 1 (
    echo.
    echo ERROR: Launcher failed to start properly
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo Z-Waifu Launcher has exited.
pause 
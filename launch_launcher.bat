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

echo Python found. Starting launcher...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo Using existing virtual environment...
    call venv\Scripts\activate.bat
    python zwaifu_launcher_gui.py
) else (
    echo No virtual environment found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r config\requirements.txt
    echo Starting launcher...
    python zwaifu_launcher_gui.py
)

echo.
echo Launcher finished.
pause 
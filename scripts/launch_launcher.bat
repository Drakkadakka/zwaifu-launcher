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

REM Try to run the smart launcher first
if exist "launch_launcher.py" (
    python launch_launcher.py
    goto :end
)

REM Fallback to direct launcher
if exist "zwaifu_launcher_gui.py" (
    python zwaifu_launcher_gui.py
    goto :end
)

REM Check in scripts directory
if exist "scripts\zwaifu_launcher_gui.py" (
    python scripts\zwaifu_launcher_gui.py
    goto :end
)

echo ERROR: Launcher file not found!
echo Expected: zwaifu_launcher_gui.py or launch_launcher.py
pause
exit /b 1

:end
echo.
echo Launcher finished.
pause 
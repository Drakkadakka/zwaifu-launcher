@echo off
title Z-Waifu Launcher - Distribution Creator
echo Z-Waifu Launcher GUI - Distribution Creator
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Creating distribution package...
echo.

REM Run the distribution creator
python create_distribution.py

echo.
echo Distribution creation completed!
echo Check the generated zip file in the current directory.
echo.
pause 
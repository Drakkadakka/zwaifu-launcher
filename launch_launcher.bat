@echo off
title Z-Waifu Launcher GUI
echo Starting Z-Waifu Launcher GUI...
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

REM Run the launcher
echo Launching launcher...
python launch_launcher.py

REM If there was an error, pause to show the message
if errorlevel 1 (
    echo.
    echo Launcher exited with an error. Check the messages above.
    pause
) 
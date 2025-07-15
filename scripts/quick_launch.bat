@echo off
chcp 65001 >nul
title Z-Waifu Launcher - Quick Launch

echo.
echo ========================================
echo 🚀 Z-Waifu Launcher - Quick Launch
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH
    echo Please install Python 3.8+ and add it to your PATH
    echo.
    pause
    exit /b 1
)

:: Get the script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

:: Change to project root
cd /d "%PROJECT_ROOT%"

echo 📁 Project Root: %PROJECT_ROOT%
echo.

:: Check if main launcher exists
if not exist "zwaifu_launcher_gui.py" (
    echo ❌ Main launcher file not found!
    echo Expected: zwaifu_launcher_gui.py
    echo.
    pause
    exit /b 1
)

echo ✅ Main launcher file found
echo.

:: Menu for launch options
:menu
echo Choose launch option:
echo.
echo 1. 🚀 Quick Launch (Basic)
echo 2. 🔧 Setup & Launch (Recommended)
echo 3. 🔍 Diagnostic Check
echo 4. 📦 Install Dependencies Only
echo 5. ❌ Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto quick_launch
if "%choice%"=="2" goto setup_launch
if "%choice%"=="3" goto diagnostic
if "%choice%"=="4" goto install_deps
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
goto menu

:quick_launch
echo.
echo 🚀 Starting Quick Launch...
python zwaifu_launcher_gui.py
goto end

:setup_launch
echo.
echo 🔧 Running Setup & Launch...
if exist "scripts\setup_and_launch.py" (
    python scripts\setup_and_launch.py
) else (
    echo ❌ Setup script not found, falling back to quick launch...
    python zwaifu_launcher_gui.py
)
goto end

:diagnostic
echo.
echo 🔍 Running Diagnostic Check...
if exist "scripts\diagnostic_tool.py" (
    python scripts\diagnostic_tool.py
    echo.
    set /p continue="Press Enter to continue to menu..."
) else (
    echo ❌ Diagnostic tool not found!
    echo.
    pause
)
goto menu

:install_deps
echo.
echo 📦 Installing Dependencies...
if exist "scripts\install_dependencies.py" (
    python scripts\install_dependencies.py
) else (
    echo ❌ Install script not found!
    echo Trying to install from requirements.txt...
    if exist "config\requirements.txt" (
        python -m pip install -r config\requirements.txt
    ) else (
        echo ❌ requirements.txt not found!
    )
)
echo.
set /p continue="Press Enter to continue to menu..."
goto menu

:exit
echo.
echo 👋 Goodbye!
exit /b 0

:end
echo.
echo 🎯 Launcher finished.
pause 
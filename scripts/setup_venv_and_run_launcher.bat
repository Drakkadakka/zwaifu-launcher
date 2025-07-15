@echo off
setlocal

REM Change to the project root directory (parent of scripts)
cd /d %~dp0..

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Upgrade pip
venv\Scripts\python.exe -m pip install --upgrade pip

REM Install requirements from config directory
venv\Scripts\pip install -r config\requirements.txt

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the launcher in the venv context
python zwaifu_launcher_gui.py

endlocal
pause 
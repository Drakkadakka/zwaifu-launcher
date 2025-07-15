#!/bin/bash

# Z-Waifu Launcher for Linux
# =========================

echo "Z-Waifu Launcher"
echo "================"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Arch Linux: sudo pacman -S python python-pip"
    echo "  Or download from https://python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python found. Checking project structure..."
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Check if required files exist
if [ ! -f "zwaifu_launcher_gui.py" ]; then
    echo "ERROR: zwaifu_launcher_gui.py not found"
    echo "Please run this script from the project root directory"
    read -p "Press Enter to exit..."
    exit 1
fi

if [ ! -f "config/requirements.txt" ]; then
    echo "ERROR: config/requirements.txt not found"
    echo "Please ensure the project structure is correct"
    read -p "Press Enter to exit..."
    exit 1
fi

if [ ! -f "launch_launcher.py" ]; then
    echo "ERROR: launch_launcher.py not found"
    echo "Please ensure the project structure is correct"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Project structure looks good!"
echo

# Check for system dependencies
echo "Checking system dependencies..."

# Check for tkinter (required for GUI)
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "WARNING: tkinter not found. Installing system dependencies..."
    if command_exists apt; then
        echo "Installing tkinter for Ubuntu/Debian..."
        sudo apt update && sudo apt install -y python3-tk
    elif command_exists yum; then
        echo "Installing tkinter for CentOS/RHEL..."
        sudo yum install -y tkinter
    elif command_exists pacman; then
        echo "Installing tkinter for Arch Linux..."
        sudo pacman -S tk
    else
        echo "Please install tkinter manually for your distribution"
        echo "Ubuntu/Debian: sudo apt install python3-tk"
        echo "CentOS/RHEL: sudo yum install tkinter"
        echo "Arch Linux: sudo pacman -S tk"
    fi
fi

# Check for other system dependencies
if ! command_exists xdg-open; then
    echo "WARNING: xdg-open not found. Installing xdg-utils..."
    if command_exists apt; then
        sudo apt install -y xdg-utils
    elif command_exists yum; then
        sudo yum install -y xdg-utils
    elif command_exists pacman; then
        sudo pacman -S xdg-utils
    fi
fi

echo "System dependencies check complete!"
echo

# Run the launch script which will handle everything automatically
echo "Starting Z-Waifu Launcher with automatic setup..."
echo "This will:"
echo "- Check Python version"
echo "- Create virtual environment if needed"
echo "- Install dependencies automatically"
echo "- Launch the GUI"
echo

python3 launch_launcher.py

# Check if the launcher script ran successfully
if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Launcher failed to start properly"
    echo "Please check the error messages above"
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "Z-Waifu Launcher has exited."
read -p "Press Enter to exit..." 
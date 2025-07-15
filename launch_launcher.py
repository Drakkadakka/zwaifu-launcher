#!/usr/bin/env python3
"""
Z-Waifu Launcher Setup and Runner
This script handles virtual environment setup, dependency installation, and launches the main GUI.
Updated to work with the correct project structure and automatically install dependencies.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = PROJECT_ROOT / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            venv.create(venv_path, with_pip=True)
            print("Virtual environment created successfully!")
            return True
        except Exception as e:
            print(f"Failed to create virtual environment: {e}")
            return False
    return True

def get_venv_python():
    """Get the Python executable path for the virtual environment"""
    if sys.platform == "win32":
        return PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
    else:
        return PROJECT_ROOT / "venv" / "bin" / "python"

def get_venv_pip():
    """Get the pip executable path for the virtual environment"""
    if sys.platform == "win32":
        return PROJECT_ROOT / "venv" / "Scripts" / "pip.exe"
    else:
        return PROJECT_ROOT / "venv" / "bin" / "pip"

def check_dependencies():
    """Check if required dependencies are installed"""
    venv_python = get_venv_python()
    if not venv_python.exists():
        return False
    
    try:
        # Check for key dependencies
        result = subprocess.run([
            str(venv_python), "-c", 
            "import tkinter, json, threading, subprocess, socket, time, os, sys, glob, re, sqlite3, datetime, webbrowser, pystray, PIL, psutil"
        ], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def install_dependencies():
    """Install dependencies using the install_dependencies script"""
    print("Installing dependencies...")
    
    # Check if install_dependencies.py exists
    install_script = PROJECT_ROOT / "scripts" / "install_dependencies.py"
    if not install_script.exists():
        print("ERROR: install_dependencies.py not found!")
        return False
    
    try:
        # Run the install dependencies script
        result = subprocess.run([sys.executable, str(install_script)], 
                              cwd=PROJECT_ROOT, 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("Dependencies installed successfully!")
            return True
        else:
            print(f"Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running install dependencies script: {e}")
        return False

def run_launcher():
    """Run the main launcher GUI"""
    print("Starting Z-Waifu Launcher...")
    
    launcher_script = PROJECT_ROOT / "zwaifu_launcher_gui.py"
    if not launcher_script.exists():
        print("ERROR: zwaifu_launcher_gui.py not found!")
        return False
    
    try:
        # Use the virtual environment Python to run the launcher
        venv_python = get_venv_python()
        if venv_python.exists():
            subprocess.run([str(venv_python), str(launcher_script)], cwd=PROJECT_ROOT)
        else:
            # Fallback to system Python if venv not available
            subprocess.run([sys.executable, str(launcher_script)], cwd=PROJECT_ROOT)
        return True
    except Exception as e:
        print(f"Error running launcher: {e}")
        return False

def main():
    """Main setup and launch function"""
    print("Z-Waifu Launcher Setup and Runner")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return 1
    
    # Check project structure
    if not (PROJECT_ROOT / "zwaifu_launcher_gui.py").exists():
        print("ERROR: zwaifu_launcher_gui.py not found in project root!")
        print("Please run this script from the project root directory.")
        input("Press Enter to exit...")
        return 1
    
    if not (PROJECT_ROOT / "config" / "requirements.txt").exists():
        print("ERROR: config/requirements.txt not found!")
        print("Please ensure the project structure is correct.")
        input("Press Enter to exit...")
        return 1
    
    print("Project structure looks good!")
    
    # Create virtual environment
    if not create_virtual_environment():
        print("Failed to create virtual environment. Continuing with system Python...")
    
    # Check if dependencies are installed
    if not check_dependencies():
        print("Dependencies not found. Installing...")
        if not install_dependencies():
            print("Failed to install dependencies!")
            print("You can try running the install script manually:")
            print(f"  python {PROJECT_ROOT / 'scripts' / 'install_dependencies.py'}")
            input("Press Enter to exit...")
            return 1
    else:
        print("Dependencies are already installed!")
    
    # Run the launcher
    print("\nLaunching Z-Waifu Launcher...")
    if not run_launcher():
        print("Failed to start launcher!")
        input("Press Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
Z-Waifu Launcher Setup and Runner
This script handles virtual environment setup and launches the main GUI.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            venv.create("venv", with_pip=True)
            print("Virtual environment created successfully!")
            return True
        except Exception as e:
            print(f"ERROR: Failed to create virtual environment: {e}")
            return False
    return True

def get_venv_python():
    """Get the path to the virtual environment Python executable"""
    if os.name == 'nt':  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # Unix/Linux/Mac
        return Path("venv/bin/python")

def install_dependencies():
    """Install dependencies from requirements.txt"""
    venv_python = get_venv_python()
    requirements_file = Path("config/requirements.txt")
    
    if not venv_python.exists():
        print("ERROR: Virtual environment Python not found!")
        return False
    
    if not requirements_file.exists():
        print("ERROR: requirements.txt not found!")
        return False
    
    print("Installing dependencies...")
    try:
        # Upgrade pip first
        subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True, text=True)
        
        # Install requirements
        subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)], 
                      check=True, capture_output=True, text=True)
        
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def run_launcher():
    """Run the main launcher GUI"""
    venv_python = get_venv_python()
    launcher_file = Path("zwaifu_launcher_gui.py")
    
    if not launcher_file.exists():
        print("ERROR: zwaifu_launcher_gui.py not found!")
        return False
    
    print("Starting Z-Waifu Launcher...")
    try:
        subprocess.run([str(venv_python), str(launcher_file)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Launcher failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\nLauncher stopped by user.")
        return True

def main():
    """Main function"""
    print("Z-Waifu Launcher Setup")
    print("======================")
    print()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return 1
    
    # Create virtual environment
    if not create_virtual_environment():
        input("Press Enter to exit...")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        input("Press Enter to exit...")
        return 1
    
    # Run launcher
    if not run_launcher():
        input("Press Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
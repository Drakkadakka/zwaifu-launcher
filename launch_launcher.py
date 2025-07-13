#!/usr/bin/env python3
"""
Z-Waifu Launcher GUI - Launcher Script
This script handles dependencies and starts the main launcher GUI.
"""

import sys
import os
import subprocess
import importlib.util

def check_dependency(module_name, package_name=None):
    """Check if a dependency is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def install_dependency(package_name):
    """Install a missing dependency"""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}")
        return False

def main():
    """Main launcher function"""
    print("Z-Waifu Launcher GUI")
    print("=" * 40)
    
    # Check and install dependencies
    dependencies = [
        ("psutil", "psutil"),
        ("PIL", "Pillow"),
        ("pystray", "pystray")
    ]
    
    missing_deps = []
    for module_name, package_name in dependencies:
        if not check_dependency(module_name):
            missing_deps.append((module_name, package_name))
    
    if missing_deps:
        print("Missing dependencies detected:")
        for module_name, package_name in missing_deps:
            print(f"  - {module_name} ({package_name})")
        
        print("\nInstalling missing dependencies...")
        for module_name, package_name in missing_deps:
            if not install_dependency(package_name):
                print(f"Failed to install {package_name}. Please install it manually:")
                print(f"  pip install {package_name}")
                return 1
        
        print("Dependencies installed successfully!")
    
    # Import and run the launcher
    try:
        from zwaifu_launcher_gui import LauncherGUI
        import tkinter as tk
        
        print("Starting launcher GUI...")
        root = tk.Tk()
        app = LauncherGUI(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"Error importing launcher: {e}")
        print("Make sure zwaifu_launcher_gui.py is in the same directory.")
        return 1
    except Exception as e:
        print(f"Error starting launcher: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
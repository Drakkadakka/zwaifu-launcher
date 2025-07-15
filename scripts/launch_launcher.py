#!/usr/bin/env python3
"""
Z-Waifu Launcher - Smart Launcher Script
Automatically checks dependencies and launches the main application.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        'psutil',
        'PIL',
        'pystray'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_modules.append(module)
    
    return missing_modules

def install_dependencies():
    """Install missing dependencies"""
    print("\n🔧 Installing missing dependencies...")
    
    try:
        # Check if requirements.txt exists
        requirements_file = Path("config/requirements.txt")
        if not requirements_file.exists():
            requirements_file = Path("requirements.txt")
        
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True)
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ requirements.txt not found")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def find_main_launcher():
    """Find the main launcher file"""
    # List of possible launcher file locations
    launcher_files = [
        "../zwaifu_launcher_gui.py",  # From scripts directory
        "zwaifu_launcher_gui.py",     # From root directory
        "scripts/zwaifu_launcher_gui.py",
        "src/zwaifu_launcher_gui.py"
    ]
    
    for path in launcher_files:
        if os.path.exists(path):
            return path
    
    return None

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "config",
        "data", 
        "logs",
        "plugins",
        "templates",
        "static/css",
        "static/js", 
        "static/images",
        "ai_tools/oobabooga",
        "ai_tools/zwaifu",
        "ai_tools/ollama",
        "ai_tools/rvc"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main launcher function"""
    print("🚀 Z-Waifu Launcher - Smart Launcher")
    print("=" * 40)
    
    # Create necessary directories
    create_directories()
    
    # Check dependencies
    print("📦 Checking dependencies...")
    missing_modules = check_dependencies()
    
    if missing_modules:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing_modules)}")
        response = input("Would you like to install them automatically? (y/n): ")
        
        if response.lower() in ['y', 'yes']:
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install them manually.")
                return False
        else:
            print("❌ Please install the missing dependencies manually.")
            return False
    
    # Find main launcher file
    launcher_file = find_main_launcher()
    if not launcher_file:
        print("❌ Main launcher file not found!")
        print("Expected: zwaifu_launcher_gui.py")
        return False
    
    print(f"✅ Found launcher: {launcher_file}")
    
    # Launch the application
    print("\n🎯 Starting Z-Waifu Launcher...")
    try:
        subprocess.run([sys.executable, launcher_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start launcher: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
        return True
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
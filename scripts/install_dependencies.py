#!/usr/bin/env python3
"""
Z-Waifu Launcher Dependency Installer
Automatically installs all required dependencies for the advanced features.
Updated to work with the correct project structure.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add parent directory to path so we can find the project files
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

def run_command(command):
    """Run a command and return success status"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("\n🔧 Upgrading pip...")
    return run_command(f"{sys.executable} -m pip install --upgrade pip")

def install_from_requirements():
    """Install dependencies from requirements.txt"""
    print("\n📦 Installing dependencies from requirements.txt...")
    requirements_file = PROJECT_ROOT / "config" / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print(f"Using requirements file: {requirements_file}")
    return run_command(f"{sys.executable} -m pip install -r {requirements_file}")

def install_core_dependencies():
    """Install core dependencies"""
    print("\n📦 Installing core dependencies...")
    core_deps = [
        "psutil>=5.9.0",
        "pillow>=10.0.0", 
        "pystray>=0.19.0",
        "python-dotenv>=1.0.0"
    ]
    
    success = True
    for dep in core_deps:
        if not run_command(f"{sys.executable} -m pip install {dep}"):
            success = False
    
    return success

def install_web_dependencies():
    """Install web interface dependencies"""
    print("\n🌐 Installing web interface dependencies...")
    web_deps = [
        "flask>=3.0.0",
        "flask-socketio>=5.3.0",
        "flask-cors>=4.0.0",
        "flask-limiter>=3.5.0",
        "pyjwt>=2.8.0",
        "python-engineio>=4.7.0",
        "python-socketio>=5.9.0",
        "blinker>=1.7.0",
        "itsdangerous>=2.1.0",
        "jinja2>=3.1.0",
        "markupsafe>=2.1.0",
        "werkzeug>=3.0.0",
        "click>=8.1.0"
    ]
    
    success = True
    for dep in web_deps:
        if not run_command(f"{sys.executable} -m pip install {dep}"):
            success = False
    
    return success

def install_analytics_dependencies():
    """Install analytics dependencies"""
    print("\n📊 Installing analytics dependencies...")
    analytics_deps = [
        "matplotlib>=3.7.0",
        "numpy>=1.24.0",
        "six>=1.16.0",
        "python-dateutil>=2.8.0",
        "cycler>=0.11.0",
        "kiwisolver>=1.4.0",
        "pyparsing>=3.0.0",
        "packaging>=23.0",
        "fonttools>=4.40.0",
        "contourpy>=1.1.0"
    ]
    
    success = True
    for dep in analytics_deps:
        if not run_command(f"{sys.executable} -m pip install {dep}"):
            success = False
    
    return success

def install_utility_dependencies():
    """Install utility dependencies"""
    print("\n🔧 Installing utility dependencies...")
    utility_deps = [
        "requests>=2.31.0",
        "qrcode[pil]>=7.4.0",
        "certifi>=2023.0.0",
        "charset-normalizer>=3.0.0",
        "idna>=3.4",
        "urllib3>=2.0.0"
    ]
    
    success = True
    for dep in utility_deps:
        if not run_command(f"{sys.executable} -m pip install {dep}"):
            success = False
    
    return success

def install_security_dependencies():
    """Install security dependencies"""
    print("\n🔒 Installing security dependencies...")
    security_deps = [
        "cryptography>=41.0.0",
        "bcrypt>=4.0.0"
    ]
    
    success = True
    for dep in security_deps:
        if not run_command(f"{sys.executable} -m pip install {dep}"):
            success = False
    
    return success

def test_imports():
    """Test if all dependencies can be imported"""
    print("\n🧪 Testing imports...")
    
    test_modules = [
        ("psutil", "psutil"),
        ("PIL", "pillow"),
        ("pystray", "pystray"),
        ("dotenv", "python-dotenv"),
        ("flask", "flask"),
        ("flask_socketio", "flask-socketio"),
        ("flask_cors", "flask-cors"),
        ("flask_limiter", "flask-limiter"),
        ("jwt", "pyjwt"),
        ("matplotlib", "matplotlib"),
        ("numpy", "numpy"),
        ("requests", "requests"),
        ("qrcode", "qrcode"),
        ("cryptography", "cryptography")
    ]
    
    failed_imports = []
    
    for module_name, package_name in test_modules:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            failed_imports.append(package_name)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        return False
    else:
        print("\n🎉 All imports successful!")
        return True

def check_project_structure():
    """Check if the project structure is correct"""
    print("\n📁 Checking project structure...")
    
    required_files = [
        PROJECT_ROOT / "zwaifu_launcher_gui.py",
        PROJECT_ROOT / "launch_launcher.py",
        PROJECT_ROOT / "launch_launcher.bat",
        PROJECT_ROOT / "config" / "requirements.txt",
        PROJECT_ROOT / "utils" / "__init__.py",
        PROJECT_ROOT / "utils" / "analytics_system.py",
        PROJECT_ROOT / "utils" / "api_server.py",
        PROJECT_ROOT / "utils" / "mobile_app.py",
        PROJECT_ROOT / "utils" / "plugin_system.py",
        PROJECT_ROOT / "utils" / "web_interface.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path.relative_to(PROJECT_ROOT)))
        else:
            print(f"✅ {file_path.relative_to(PROJECT_ROOT)}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Project structure is correct!")
    return True

def main():
    """Main installation function"""
    print("Z-Waifu Launcher Dependency Installer")
    print("=" * 50)
    print(f"Project root: {PROJECT_ROOT}")
    print()
    
    # Check project structure
    if not check_project_structure():
        print("❌ Project structure check failed")
        return False
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip
    upgrade_pip()
    
    # Try to install from requirements.txt first
    print("\n📦 Attempting to install from requirements.txt...")
    if install_from_requirements():
        print("✅ Successfully installed from requirements.txt")
    else:
        print("⚠️  Failed to install from requirements.txt, trying individual packages...")
        
        # Install dependencies individually
        success = True
        
        if not install_core_dependencies():
            print("❌ Core dependencies installation failed")
            success = False
        
        if not install_web_dependencies():
            print("❌ Web dependencies installation failed")
            success = False
        
        if not install_analytics_dependencies():
            print("❌ Analytics dependencies installation failed")
            success = False
        
        if not install_utility_dependencies():
            print("❌ Utility dependencies installation failed")
            success = False
        
        if not install_security_dependencies():
            print("❌ Security dependencies installation failed")
            success = False
        
        if not success:
            return False
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed")
        return False
    
    print("\n" + "="*60)
    print("✅ Installation completed successfully!")
    print("="*60)
    print("\nYou can now run the launcher:")
    print(f"1. From the project root: python {PROJECT_ROOT}/zwaifu_launcher_gui.py")
    print(f"2. Or use the launcher script: python {PROJECT_ROOT}/launch_launcher.py")
    print(f"3. Or double-click: {PROJECT_ROOT}/launch_launcher.bat")
    print("\nThe launcher will automatically detect and configure your AI tools.")
    print("For detailed instructions, see docs/INSTALLATION_GUIDE.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Z-Waifu Launcher - Complete Setup and Launch Script
Handles dependency installation, environment setup, and launcher startup.
"""

import os
import sys
import subprocess
import importlib.util
import json
import shutil
from pathlib import Path
import platform

class ZWaifuSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.plugins_dir = self.project_root / "plugins"
        self.templates_dir = self.project_root / "templates"
        self.static_dir = self.project_root / "static"
        self.ai_tools_dir = self.project_root / "ai_tools"
        
    def print_banner(self):
        """Print setup banner"""
        print("=" * 60)
        print("🚀 Z-Waifu Launcher - Complete Setup & Launch")
        print("=" * 60)
        print(f"Project Root: {self.project_root}")
        print(f"Python Version: {sys.version}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print("=" * 60)
    
    def create_directories(self):
        """Create all necessary directories"""
        print("\n📁 Creating project directories...")
        
        directories = [
            self.config_dir,
            self.data_dir,
            self.logs_dir,
            self.plugins_dir,
            self.templates_dir,
            self.static_dir / "css",
            self.static_dir / "js",
            self.static_dir / "images",
            self.ai_tools_dir / "oobabooga",
            self.ai_tools_dir / "zwaifu",
            self.ai_tools_dir / "ollama",
            self.ai_tools_dir / "rvc"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}")
    
    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8 or higher is required")
            print(f"Current version: {version.major}.{version.minor}.{version.micro}")
            return False
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("\n📦 Checking dependencies...")
        
        required_modules = [
            ('psutil', 'psutil'),
            ('PIL', 'pillow'),
            ('pystray', 'pystray')
        ]
        
        optional_modules = [
            ('flask', 'flask'),
            ('flask_socketio', 'flask-socketio'),
            ('flask_cors', 'flask-cors'),
            ('flask_limiter', 'flask-limiter'),
            ('jwt', 'pyjwt'),
            ('matplotlib', 'matplotlib'),
            ('numpy', 'numpy'),
            ('requests', 'requests'),
            ('qrcode', 'qrcode')
        ]
        
        missing_required = []
        missing_optional = []
        
        # Check required modules
        for module_name, package_name in required_modules:
            try:
                importlib.import_module(module_name)
                print(f"✅ {package_name} (required)")
            except ImportError:
                print(f"❌ {package_name} (required)")
                missing_required.append(package_name)
        
        # Check optional modules
        for module_name, package_name in optional_modules:
            try:
                importlib.import_module(module_name)
                print(f"✅ {package_name} (optional)")
            except ImportError:
                print(f"⚠️ {package_name} (optional)")
                missing_optional.append(package_name)
        
        return missing_required, missing_optional
    
    def install_dependencies(self, missing_required, missing_optional):
        """Install missing dependencies"""
        print("\n🔧 Installing dependencies...")
        
        # Upgrade pip first
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            print("✅ Pip upgraded")
        except subprocess.CalledProcessError:
            print("⚠️ Failed to upgrade pip, continuing...")
        
        # Install required dependencies
        if missing_required:
            print(f"\n📦 Installing required dependencies: {', '.join(missing_required)}")
            requirements_file = self.config_dir / "requirements.txt"
            
            if requirements_file.exists():
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                                 check=True)
                    print("✅ Required dependencies installed")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install required dependencies: {e}")
                    return False
            else:
                print("❌ requirements.txt not found")
                return False
        
        # Install optional dependencies if user wants
        if missing_optional:
            print(f"\n⚠️ Optional dependencies missing: {', '.join(missing_optional)}")
            response = input("Install optional dependencies for full functionality? (y/n): ")
            
            if response.lower() in ['y', 'yes']:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install"] + missing_optional, 
                                 check=True)
                    print("✅ Optional dependencies installed")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ Some optional dependencies failed to install: {e}")
        
        return True
    
    def create_default_config(self):
        """Create default configuration if it doesn't exist"""
        config_file = self.config_dir / "launcher_config.json"
        
        if not config_file.exists():
            print("\n⚙️ Creating default configuration...")
            
            default_config = {
                "ooba_bat": None,
                "zwaifu_bat": None,
                "ollama_enabled": False,
                "ollama_bat": None,
                "rvc_enabled": False,
                "rvc_host": "127.0.0.1",
                "rvc_port": "7897",
                "rvc_model": "default",
                "rvc_speaker": "0",
                "rvc_pitch": "0.0",
                "rvc_speed": "1.0",
                "rvc_bat": None,
                "theme": "light",
                "port": "5000",
                "auto_start_ooba": False,
                "auto_start_zwaifu": False,
                "auto_start_ollama": False,
                "auto_start_rvc": False,
                "ooba_port": "7860",
                "zwaifu_port": "5000"
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print("✅ Default configuration created")
    
    def auto_detect_batch_files(self):
        """Auto-detect batch files in the project"""
        print("\n🔍 Auto-detecting batch files...")
        
        config_file = self.config_dir / "launcher_config.json"
        if not config_file.exists():
            return
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Look for common batch file patterns
        batch_patterns = [
            "start_windows.bat",
            "startup.bat", 
            "launch.bat",
            "run.bat"
        ]
        
        found_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.lower() in [pattern.lower() for pattern in batch_patterns]:
                    file_path = Path(root) / file
                    found_files.append(str(file_path))
        
        if found_files:
            print("✅ Found batch files:")
            for file in found_files:
                print(f"   📄 {file}")
        else:
            print("⚠️ No batch files found")
    
    def validate_environment(self):
        """Validate the environment is ready"""
        print("\n🔍 Validating environment...")
        
        # Check if main launcher exists
        launcher_file = self.project_root / "zwaifu_launcher_gui.py"
        if not launcher_file.exists():
            print("❌ Main launcher file not found!")
            return False
        
        print("✅ Main launcher file found")
        
        # Check if config exists
        config_file = self.config_dir / "launcher_config.json"
        if not config_file.exists():
            print("❌ Configuration file not found!")
            return False
        
        print("✅ Configuration file found")
        
        # Check if directories exist
        required_dirs = [self.config_dir, self.data_dir, self.logs_dir]
        for directory in required_dirs:
            if not directory.exists():
                print(f"❌ Required directory not found: {directory}")
                return False
        
        print("✅ All required directories exist")
        return True
    
    def launch_application(self):
        """Launch the main application"""
        print("\n🎯 Launching Z-Waifu Launcher...")
        
        launcher_file = self.project_root / "zwaifu_launcher_gui.py"
        
        try:
            # Change to project root directory
            os.chdir(self.project_root)
            
            # Launch the application
            subprocess.run([sys.executable, str(launcher_file)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start launcher: {e}")
            return False
        except KeyboardInterrupt:
            print("\n👋 Launcher stopped by user")
            return True
    
    def run(self):
        """Run the complete setup and launch process"""
        self.print_banner()
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Create directories
        self.create_directories()
        
        # Check dependencies
        missing_required, missing_optional = self.check_dependencies()
        
        # Install dependencies if needed
        if missing_required:
            if not self.install_dependencies(missing_required, missing_optional):
                return False
        
        # Create default config
        self.create_default_config()
        
        # Auto-detect batch files
        self.auto_detect_batch_files()
        
        # Validate environment
        if not self.validate_environment():
            return False
        
        # Launch application
        return self.launch_application()

def main():
    """Main function"""
    setup = ZWaifuSetup()
    success = setup.run()
    
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")

if __name__ == "__main__":
    main() 
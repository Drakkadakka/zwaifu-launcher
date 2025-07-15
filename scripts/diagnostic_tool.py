#!/usr/bin/env python3
"""
Z-Waifu Launcher Diagnostic Tool
Comprehensive diagnostic and troubleshooting utility.
"""

import os
import sys
import subprocess
import importlib.util
import json
import platform
import psutil
import socket
from pathlib import Path
from datetime import datetime

class ZWaifuDiagnostic:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.warnings = []
        self.recommendations = []
        
    def print_banner(self):
        """Print diagnostic banner"""
        print("=" * 70)
        print("🔍 Z-Waifu Launcher - Diagnostic Tool")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project Root: {self.project_root}")
        print("=" * 70)
    
    def check_system_info(self):
        """Check system information"""
        print("\n💻 System Information:")
        print(f"   OS: {platform.system()} {platform.release()}")
        print(f"   Architecture: {platform.machine()}")
        print(f"   Python: {sys.version}")
        print(f"   CPU Cores: {psutil.cpu_count()}")
        print(f"   Memory: {psutil.virtual_memory().total // (1024**3)} GB")
        
        # Check available disk space
        try:
            disk_usage = psutil.disk_usage(self.project_root)
            free_gb = disk_usage.free // (1024**3)
            print(f"   Free Disk Space: {free_gb} GB")
            
            if free_gb < 1:
                self.warnings.append("Low disk space (< 1 GB)")
        except Exception as e:
            self.warnings.append(f"Cannot check disk space: {e}")
    
    def check_python_environment(self):
        """Check Python environment"""
        print("\n🐍 Python Environment:")
        
        # Check Python version
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.issues.append(f"Python version too old: {version.major}.{version.minor}.{version.micro}")
            print(f"   ❌ Python version: {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        else:
            print(f"   ✅ Python version: {version.major}.{version.minor}.{version.micro}")
        
        # Check pip
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"   ✅ Pip: {result.stdout.strip()}")
        except Exception as e:
            self.issues.append(f"Pip not available: {e}")
            print(f"   ❌ Pip: Not available")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("   ✅ Virtual environment detected")
        else:
            print("   ⚠️ No virtual environment detected")
            self.recommendations.append("Consider using a virtual environment")
    
    def check_dependencies(self):
        """Check all dependencies"""
        print("\n📦 Dependency Check:")
        
        dependencies = {
            'required': [
                ('psutil', 'psutil'),
                ('PIL', 'pillow'),
                ('pystray', 'pystray')
            ],
            'optional': [
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
        }
        
        missing_required = []
        missing_optional = []
        
        # Check required dependencies
        for module_name, package_name in dependencies['required']:
            try:
                importlib.import_module(module_name)
                print(f"   ✅ {package_name} (required)")
            except ImportError:
                print(f"   ❌ {package_name} (required)")
                missing_required.append(package_name)
        
        # Check optional dependencies
        for module_name, package_name in dependencies['optional']:
            try:
                importlib.import_module(module_name)
                print(f"   ✅ {package_name} (optional)")
            except ImportError:
                print(f"   ⚠️ {package_name} (optional)")
                missing_optional.append(package_name)
        
        if missing_required:
            self.issues.append(f"Missing required dependencies: {', '.join(missing_required)}")
        
        if missing_optional:
            self.warnings.append(f"Missing optional dependencies: {', '.join(missing_optional)}")
    
    def check_project_structure(self):
        """Check project structure and files"""
        print("\n📁 Project Structure:")
        
        required_files = [
            "zwaifu_launcher_gui.py",
            "config/launcher_config.json",
            "config/requirements.txt"
        ]
        
        required_dirs = [
            "config",
            "data",
            "logs",
            "plugins",
            "templates",
            "static",
            "ai_tools"
        ]
        
        # Check required files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}")
                self.issues.append(f"Missing required file: {file_path}")
        
        # Check required directories
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"   ✅ {dir_path}/")
            else:
                print(f"   ❌ {dir_path}/")
                self.issues.append(f"Missing required directory: {dir_path}")
    
    def check_configuration(self):
        """Check configuration files"""
        print("\n⚙️ Configuration Check:")
        
        config_file = self.project_root / "config" / "launcher_config.json"
        
        if not config_file.exists():
            self.issues.append("Configuration file not found")
            print("   ❌ launcher_config.json not found")
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("   ✅ launcher_config.json loaded successfully")
            
            # Check for required config keys
            required_keys = [
                "ooba_bat", "zwaifu_bat", "theme", "port",
                "ooba_port", "zwaifu_port"
            ]
            
            for key in required_keys:
                if key in config:
                    print(f"   ✅ {key}: {config[key]}")
                else:
                    print(f"   ❌ Missing config key: {key}")
                    self.issues.append(f"Missing configuration key: {key}")
            
            # Check if batch files exist
            if config.get("ooba_bat") and os.path.exists(config["ooba_bat"]):
                print(f"   ✅ Oobabooga batch file exists")
            elif config.get("ooba_bat"):
                print(f"   ❌ Oobabooga batch file not found: {config['ooba_bat']}")
                self.warnings.append("Oobabooga batch file not found")
            
            if config.get("zwaifu_bat") and os.path.exists(config["zwaifu_bat"]):
                print(f"   ✅ Z-Waifu batch file exists")
            elif config.get("zwaifu_bat"):
                print(f"   ❌ Z-Waifu batch file not found: {config['zwaifu_bat']}")
                self.warnings.append("Z-Waifu batch file not found")
                
        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in configuration: {e}")
            print(f"   ❌ Invalid JSON in configuration: {e}")
        except Exception as e:
            self.issues.append(f"Error reading configuration: {e}")
            print(f"   ❌ Error reading configuration: {e}")
    
    def check_network_ports(self):
        """Check if required ports are available"""
        print("\n🌐 Network Port Check:")
        
        ports_to_check = [5000, 7860, 8080, 8081, 8082, 7897]
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        print(f"   ⚠️ Port {port} is in use")
                        self.warnings.append(f"Port {port} is already in use")
                    else:
                        print(f"   ✅ Port {port} is available")
            except Exception as e:
                print(f"   ❌ Cannot check port {port}: {e}")
    
    def check_processes(self):
        """Check for running processes"""
        print("\n🔄 Process Check:")
        
        # Check for Python processes that might be the launcher
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('zwaifu' in arg.lower() for arg in cmdline):
                        python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            print("   ⚠️ Found running Z-Waifu processes:")
            for proc in python_processes:
                print(f"      PID {proc['pid']}: {' '.join(proc['cmdline'])}")
            self.warnings.append("Z-Waifu processes are already running")
        else:
            print("   ✅ No Z-Waifu processes running")
    
    def check_permissions(self):
        """Check file and directory permissions"""
        print("\n🔐 Permission Check:")
        
        try:
            # Test write permissions
            test_file = self.project_root / "data" / "test_write.tmp"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_file, 'w') as f:
                f.write("test")
            
            test_file.unlink()
            print("   ✅ Write permissions OK")
        except Exception as e:
            self.issues.append(f"Permission issues: {e}")
            print(f"   ❌ Permission issues: {e}")
    
    def generate_report(self):
        """Generate diagnostic report"""
        print("\n" + "=" * 70)
        print("📋 DIAGNOSTIC REPORT")
        print("=" * 70)
        
        if self.issues:
            print("\n❌ ISSUES FOUND:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ No critical issues found")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if self.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "=" * 70)
        
        # Save report to file
        report_file = self.project_root / "data" / f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write("Z-Waifu Launcher Diagnostic Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if self.issues:
                f.write("ISSUES:\n")
                for issue in self.issues:
                    f.write(f"- {issue}\n")
                f.write("\n")
            
            if self.warnings:
                f.write("WARNINGS:\n")
                for warning in self.warnings:
                    f.write(f"- {warning}\n")
                f.write("\n")
            
            if self.recommendations:
                f.write("RECOMMENDATIONS:\n")
                for rec in self.recommendations:
                    f.write(f"- {rec}\n")
        
        print(f"📄 Report saved to: {report_file}")
    
    def run(self):
        """Run complete diagnostic"""
        self.print_banner()
        
        self.check_system_info()
        self.check_python_environment()
        self.check_dependencies()
        self.check_project_structure()
        self.check_configuration()
        self.check_network_ports()
        self.check_processes()
        self.check_permissions()
        
        self.generate_report()
        
        return len(self.issues) == 0

def main():
    """Main function"""
    diagnostic = ZWaifuDiagnostic()
    success = diagnostic.run()
    
    if success:
        print("\n✅ Diagnostic completed - No critical issues found!")
        print("You can now run the launcher safely.")
    else:
        print("\n❌ Diagnostic completed - Issues found!")
        print("Please address the issues above before running the launcher.")
    
    return success

if __name__ == "__main__":
    main() 
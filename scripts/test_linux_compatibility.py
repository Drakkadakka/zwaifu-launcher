#!/usr/bin/env python3
"""
Linux Compatibility Test for Z-Waifu Launcher
This script tests if the launcher will work properly on Linux systems.
"""

import os
import sys
import subprocess
import importlib
import platform
from pathlib import Path

def print_status(message, status="INFO"):
    """Print a status message with color coding"""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
    }
    color = colors.get(status, "\033[0m")
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def test_python_version():
    """Test Python version compatibility"""
    print_status("Testing Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+", "ERROR")
        return False

def test_platform():
    """Test platform compatibility"""
    print_status("Testing platform...")
    
    system = platform.system()
    if system == "Linux":
        print_status(f"Platform: {system} - OK", "SUCCESS")
        return True
    elif system == "Windows":
        print_status(f"Platform: {system} - This is a Windows system", "WARNING")
        return True
    else:
        print_status(f"Platform: {system} - May have compatibility issues", "WARNING")
        return True

def test_required_modules():
    """Test if required Python modules are available"""
    print_status("Testing required Python modules...")
    
    required_modules = [
        "tkinter",
        "json",
        "threading",
        "subprocess",
        "socket",
        "time",
        "os",
        "sys",
        "glob",
        "re",
        "sqlite3",
        "datetime",
        "webbrowser",
        "pathlib"
    ]
    
    optional_modules = [
        "pystray",
        "PIL",
        "psutil",
        "matplotlib",
        "numpy",
        "requests",
        "qrcode",
        "flask",
        "flask_socketio",
        "flask_cors",
        "flask_limiter",
        "jwt",
        "secrets"
    ]
    
    all_good = True
    
    # Test required modules
    for module in required_modules:
        try:
            importlib.import_module(module)
            print_status(f"  {module} - OK", "SUCCESS")
        except ImportError:
            print_status(f"  {module} - MISSING", "ERROR")
            all_good = False
    
    # Test optional modules
    print_status("Testing optional modules...")
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print_status(f"  {module} - OK", "SUCCESS")
        except ImportError:
            print_status(f"  {module} - MISSING (optional)", "WARNING")
    
    return all_good

def test_tkinter():
    """Test tkinter specifically"""
    print_status("Testing tkinter GUI framework...")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print_status("tkinter - OK", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"tkinter - ERROR: {e}", "ERROR")
        return False

def test_file_permissions():
    """Test file permissions and accessibility"""
    print_status("Testing file permissions...")
    
    current_dir = Path.cwd()
    test_file = current_dir / "test_permissions.tmp"
    
    try:
        # Test write permission
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Test read permission
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Clean up
        test_file.unlink()
        
        print_status("File permissions - OK", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"File permissions - ERROR: {e}", "ERROR")
        return False

def test_subprocess():
    """Test subprocess functionality"""
    print_status("Testing subprocess functionality...")
    
    try:
        # Test basic command execution
        result = subprocess.run(["echo", "test"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == "test":
            print_status("subprocess - OK", "SUCCESS")
            return True
        else:
            print_status("subprocess - Unexpected output", "ERROR")
            return False
    except Exception as e:
        print_status(f"subprocess - ERROR: {e}", "ERROR")
        return False

def test_network():
    """Test network functionality"""
    print_status("Testing network functionality...")
    
    try:
        import socket
        # Test socket creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.close()
        print_status("Network sockets - OK", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Network sockets - ERROR: {e}", "ERROR")
        return False

def test_project_structure():
    """Test if required project files exist"""
    print_status("Testing project structure...")
    
    required_files = [
        "zwaifu_launcher_gui.py",
        "launch_launcher.py",
        "config/requirements.txt"
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_status(f"  {file_path} - OK", "SUCCESS")
        else:
            print_status(f"  {file_path} - MISSING", "ERROR")
            all_good = False
    
    return all_good

def test_linux_specific():
    """Test Linux-specific functionality"""
    print_status("Testing Linux-specific functionality...")
    
    if platform.system() != "Linux":
        print_status("Not a Linux system, skipping Linux-specific tests", "INFO")
        return True
    
    # Test if we can execute shell commands
    try:
        result = subprocess.run(["which", "python3"], capture_output=True, text=True)
        if result.returncode == 0:
            print_status("python3 command - OK", "SUCCESS")
        else:
            print_status("python3 command - NOT FOUND", "WARNING")
    except Exception as e:
        print_status(f"python3 command - ERROR: {e}", "WARNING")
    
    # Test if we can create virtual environments
    try:
        import venv
        print_status("venv module - OK", "SUCCESS")
    except ImportError:
        print_status("venv module - MISSING", "ERROR")
        return False
    
    return True

def test_launcher_script():
    """Test if the launcher script can be executed"""
    print_status("Testing launcher script...")
    
    launcher_script = Path("launch_launcher.py")
    if not launcher_script.exists():
        print_status("launch_launcher.py - MISSING", "ERROR")
        return False
    
    try:
        # Test if the script can be imported (syntax check)
        spec = importlib.util.spec_from_file_location("launch_launcher", launcher_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print_status("launch_launcher.py - Syntax OK", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"launch_launcher.py - Syntax ERROR: {e}", "ERROR")
        return False

def main():
    """Run all compatibility tests"""
    print("Z-Waifu Launcher Linux Compatibility Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Python Version", test_python_version),
        ("Platform", test_platform),
        ("Required Modules", test_required_modules),
        ("Tkinter GUI", test_tkinter),
        ("File Permissions", test_file_permissions),
        ("Subprocess", test_subprocess),
        ("Network", test_network),
        ("Project Structure", test_project_structure),
        ("Linux Specific", test_linux_specific),
        ("Launcher Script", test_launcher_script),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Test failed with exception: {e}", "ERROR")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("COMPATIBILITY TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print_status("All tests passed! The launcher should work on this system.", "SUCCESS")
        return 0
    elif passed >= total * 0.8:
        print_status("Most tests passed. The launcher should work with minor issues.", "WARNING")
        return 1
    else:
        print_status("Many tests failed. The launcher may not work properly.", "ERROR")
        return 2

if __name__ == "__main__":
    sys.exit(main()) 
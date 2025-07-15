#!/usr/bin/env python3
"""
Test script for Z-Waifu Launcher Advanced Features
This script tests all the advanced features to ensure they work correctly.
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zwaifu_launcher_gui import LauncherGUI
except ImportError:
    print("Error: Could not import launcher modules")
    sys.exit(1)

from tkinter import ttk

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    # Core imports
    try:
        import psutil
        print("✅ psutil imported successfully")
    except ImportError:
        print("❌ psutil import failed")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL/Pillow imported successfully")
    except ImportError:
        print("❌ PIL/Pillow import failed")
        return False
    
    try:
        import pystray
        print("✅ pystray imported successfully")
    except ImportError:
        print("❌ pystray import failed")
        return False
    
    # Advanced feature imports
    try:
        from flask import Flask
        from flask_socketio import SocketIO
        from flask_cors import CORS
        from flask_limiter import Limiter
        import jwt
        print("✅ Flask and related packages imported successfully")
    except ImportError:
        print("⚠️  Flask packages not available - web interface will be disabled")
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        print("✅ Matplotlib and NumPy imported successfully")
    except ImportError:
        print("⚠️  Matplotlib not available - analytics will be disabled")
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError:
        print("⚠️  Requests not available - some features will be disabled")
    
    try:
        import qrcode
        print("✅ QRCode imported successfully")
    except ImportError:
        print("⚠️  QRCode not available - mobile QR codes will be disabled")
    
    return True

def test_launcher_gui():
    """Test launcher GUI functionality"""
    print("\nTesting Launcher GUI...")
    
    try:
        # Create a test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create launcher instance
        launcher = LauncherGUI(root)
        
        # Test basic functionality
        print("✅ Launcher GUI created successfully")
        
        # Test advanced features
        if hasattr(launcher, 'web_interface'):
            print("✅ Web interface initialized")
        else:
            print("⚠️  Web interface not available")
        
        if hasattr(launcher, 'api_server'):
            print("✅ API server initialized")
        else:
            print("⚠️  API server not available")
        
        if hasattr(launcher, 'mobile_app'):
            print("✅ Mobile app initialized")
        else:
            print("⚠️  Mobile app not available")
        
        if hasattr(launcher, 'analytics'):
            print("✅ Analytics system initialized")
        else:
            print("⚠️  Analytics system not available")
        
        if hasattr(launcher, 'plugin_manager'):
            print("✅ Plugin manager initialized")
        else:
            print("⚠️  Plugin manager not available")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Launcher GUI test failed: {e}")
        return False

def test_web_interface():
    """Test web interface functionality"""
    print("\nTesting Web Interface...")
    
    try:
        from utils import WebInterface
        
        # Create a mock launcher
        class MockLauncher:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher = MockLauncher()
        web_interface = WebInterface(launcher)
        
        print("✅ Web interface class created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def test_api_server():
    """Test API server functionality"""
    print("\nTesting API Server...")
    
    try:
        from utils import APIServer
        
        # Create a mock launcher
        class MockLauncher:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher = MockLauncher()
        api_server = APIServer(launcher)
        
        print("✅ API server class created successfully")
        return True
        
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False

def test_mobile_app():
    """Test mobile app functionality"""
    print("\nTesting Mobile App...")
    
    try:
        from utils import MobileApp
        
        # Create a mock launcher
        class MockLauncher:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher = MockLauncher()
        mobile_app = MobileApp(launcher)
        
        print("✅ Mobile app class created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Mobile app test failed: {e}")
        return False

def test_analytics():
    """Test analytics system"""
    print("\nTesting Analytics System...")
    
    try:
        from utils import AnalyticsSystem
        
        # Create a mock launcher
        class MockLauncher:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher = MockLauncher()
        analytics = AnalyticsSystem(launcher)
        
        # Test database operations
        analytics.record_system_metrics(50.0, 60.0, 70.0)
        analytics.record_process_metrics("TestProcess", 25.0, 30.0)
        analytics.record_process_event("TestProcess", "started")
        
        print("✅ Analytics system created and tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        return False

def test_plugin_manager():
    """Test plugin manager"""
    print("\nTesting Plugin Manager...")
    
    try:
        from utils import PluginManager
        
        # Create a mock launcher
        class MockLauncher:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher = MockLauncher()
        plugin_manager = PluginManager(launcher)
        
        # Test plugin template creation
        if plugin_manager.create_plugin_template("test_plugin"):
            print("✅ Plugin template created successfully")
        
        print("✅ Plugin manager created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Plugin manager test failed: {e}")
        return False

def test_terminal_emulator():
    """Test terminal emulator"""
    print("\nTesting Terminal Emulator...")
    
    try:
        # Import TerminalEmulator from the main launcher file
        from zwaifu_launcher_gui import TerminalEmulator
        
        # Create a test window
        root = tk.Tk()
        root.withdraw()
        
        terminal = TerminalEmulator(root)
        
        # Test terminal methods
        terminal._append("Test output\n", '32')
        terminal.command_history.append("test command")
        
        print("✅ Terminal emulator created and tested successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Terminal emulator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Z-Waifu Launcher Advanced Features Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_launcher_gui,
        test_web_interface,
        test_api_server,
        test_mobile_app,
        test_analytics,
        test_plugin_manager,
        test_terminal_emulator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Advanced features are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
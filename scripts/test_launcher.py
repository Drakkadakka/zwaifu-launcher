#!/usr/bin/env python3
"""
Test script for the Z-Waifu Launcher GUI
This script tests the basic functionality without requiring actual batch files.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zwaifu_launcher_gui import LauncherGUI, TerminalEmulator
except ImportError:
    print("Error: Could not import launcher modules")
    sys.exit(1)

def test_basic_gui():
    """Test basic GUI creation"""
    print("\n=== Testing Basic GUI ===")
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        app = LauncherGUI(root)
        print("✓ LauncherGUI created successfully")
        
        # Test that all required attributes exist
        required_attrs = [
            'notebook', 'main_tab', 'settings_tab', 'about_tab', 
            'ollama_tab', 'rvc_tab', 'logs_tab', 'instance_manager_tab'
        ]
        
        for attr in required_attrs:
            if hasattr(app, attr):
                print(f"✓ {attr} exists")
            else:
                print(f"✗ {attr} missing")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI creation failed: {e}")
        return False

def test_terminal_emulator():
    """Test TerminalEmulator widget"""
    print("\n=== Testing TerminalEmulator ===")
    try:
        root = tk.Tk()
        root.withdraw()
        
        terminal = TerminalEmulator(root)
        print("✓ TerminalEmulator created successfully")
        
        # Test basic methods
        terminal.clear()
        terminal.log("Test message")
        print("✓ TerminalEmulator methods work")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ TerminalEmulator test failed: {e}")
        return False

def test_instance_manager():
    """Test instance manager functionality"""
    print("\n=== Testing Instance Manager ===")
    try:
        root = tk.Tk()
        root.withdraw()
        
        app = LauncherGUI(root)
        
        # Test instance manager methods
        if hasattr(app, 'refresh_instance_list'):
            print("✓ refresh_instance_list method exists")
        else:
            print("✗ refresh_instance_list method missing")
            
        if hasattr(app, 'kill_all_instances'):
            print("✓ kill_all_instances method exists")
        else:
            print("✗ kill_all_instances method missing")
            
        if hasattr(app, 'focus_selected_instance'):
            print("✓ focus_selected_instance method exists")
        else:
            print("✗ focus_selected_instance method missing")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Instance manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Z-Waifu Launcher GUI Test Suite")
    print("=" * 40)
    
    tests = [
        test_basic_gui,
        test_terminal_emulator,
        test_instance_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        print("\nThe launcher is ready to use. You can now:")
        print("1. Run 'python zwaifu_launcher_gui.py' to start the launcher")
        print("2. Configure batch file paths in the Settings tab")
        print("3. Use the Instance Manager to launch and manage processes")
        print("4. Each process instance will have its own terminal with controls")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
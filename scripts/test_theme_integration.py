#!/usr/bin/env python3
"""
Test script for ThemeManager integration in Z-Waifu Launcher GUI
Verifies that ThemeManager is properly integrated and functional.
"""

import os
import sys
import tempfile
import tkinter as tk
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_theme_manager_import():
    """Test that ThemeManager can be imported"""
    print("Testing ThemeManager import...")
    
    try:
        from utils import ThemeManager
        print("✅ ThemeManager imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing ThemeManager: {e}")
        return False

def test_theme_manager_creation():
    """Test that ThemeManager can be created"""
    print("\nTesting ThemeManager creation...")
    
    try:
        from utils import ThemeManager
        
        # Create a mock launcher GUI
        class MockLauncherGUI:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher_gui = MockLauncherGUI()
        theme_manager = ThemeManager(launcher_gui)
        
        print(f"✅ ThemeManager created: {theme_manager}")
        print(f"✅ Available themes: {list(theme_manager.get_all_themes().keys())}")
        return True
    except Exception as e:
        print(f"❌ Error creating ThemeManager: {e}")
        return False

def test_theme_application():
    """Test that themes can be applied"""
    print("\nTesting theme application...")
    
    try:
        from utils import ThemeManager
        
        # Create a mock launcher GUI
        class MockLauncherGUI:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher_gui = MockLauncherGUI()
        theme_manager = ThemeManager(launcher_gui)
        
        # Test applying light theme
        light_theme = theme_manager.get_theme('light')
        if light_theme:
            print(f"✅ Light theme loaded: {light_theme['name']}")
            print(f"   Background: {light_theme['bg']}")
            print(f"   Foreground: {light_theme['fg']}")
        else:
            print("❌ Light theme not found")
            return False
        
        # Test applying dark theme
        dark_theme = theme_manager.get_theme('dark')
        if dark_theme:
            print(f"✅ Dark theme loaded: {dark_theme['name']}")
            print(f"   Background: {dark_theme['bg']}")
            print(f"   Foreground: {dark_theme['fg']}")
        else:
            print("❌ Dark theme not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing theme application: {e}")
        return False

def test_gui_integration():
    """Test that GUI can import ThemeManager"""
    print("\nTesting GUI integration...")
    
    try:
        # Test importing the main GUI file
        import zwaifu_launcher_gui
        
        # Check if ThemeManager is used in the LauncherGUI class
        if hasattr(zwaifu_launcher_gui, 'LauncherGUI'):
            launcher_class = zwaifu_launcher_gui.LauncherGUI
            # Check if theme_manager is initialized in the class
            if hasattr(launcher_class, '__init__'):
                init_source = launcher_class.__init__.__code__.co_names
                if 'theme_manager' in init_source:
                    print("✅ ThemeManager is initialized in LauncherGUI")
                else:
                    print("❌ ThemeManager not initialized in LauncherGUI")
                    return False
            else:
                print("❌ LauncherGUI __init__ method not found")
                return False
        else:
            print("❌ LauncherGUI class not found")
            return False
        
        # Check if theme-related methods exist
        theme_methods = ['set_dark_mode', 'set_light_mode', 'get_current_theme_colors']
        for method in theme_methods:
            if hasattr(launcher_class, method):
                print(f"✅ Theme method found: {method}")
            else:
                print(f"❌ Theme method missing: {method}")
                return False
        
        print("✅ GUI integration test passed")
        return True
    except Exception as e:
        print(f"❌ Error testing GUI integration: {e}")
        return False

def test_theme_preferences():
    """Test theme preference saving and loading"""
    print("\nTesting theme preferences...")
    
    try:
        from utils import ThemeManager
        
        # Create a mock launcher GUI
        class MockLauncherGUI:
            def log(self, msg):
                print(f"LOG: {msg}")
        
        launcher_gui = MockLauncherGUI()
        theme_manager = ThemeManager(launcher_gui)
        
        # Test saving theme preference
        test_theme = 'dark'
        success = theme_manager.save_theme_preference(test_theme)
        if success:
            print(f"✅ Theme preference saved: {test_theme}")
        else:
            print(f"❌ Failed to save theme preference: {test_theme}")
            return False
        
        # Test loading theme preference
        loaded_theme = theme_manager.load_theme_preference()
        if loaded_theme == test_theme:
            print(f"✅ Theme preference loaded correctly: {loaded_theme}")
        else:
            print(f"❌ Theme preference mismatch: expected {test_theme}, got {loaded_theme}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing theme preferences: {e}")
        return False

def main():
    """Run all theme integration tests"""
    print("🎨 Z-Waifu Launcher ThemeManager Integration Tests")
    print("=" * 60)
    
    tests = [
        ("ThemeManager Import", test_theme_manager_import),
        ("ThemeManager Creation", test_theme_manager_creation),
        ("Theme Application", test_theme_application),
        ("GUI Integration", test_gui_integration),
        ("Theme Preferences", test_theme_preferences),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ThemeManager integration is working correctly.")
        print("\n✨ Features available:")
        print("   • Dark and light mode support")
        print("   • Theme editor window")
        print("   • Custom theme creation")
        print("   • Theme preference persistence")
        print("   • Centralized theme management")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the ThemeManager integration.")
        return 1

if __name__ == "__main__":
    exit(main()) 
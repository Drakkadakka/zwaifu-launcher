#!/usr/bin/env python3
"""
Simple test for plugin marketplace theme responsiveness
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the parent directory to the path to import the main modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_theme_responsiveness():
    """Test the theme responsiveness functionality"""
    print("🧪 Testing Plugin Marketplace Theme Responsiveness...")
    
    try:
        # Test 1: Import modules
        print("1. Testing module imports...")
        from utils.plugin_marketplace import PluginMarketplace
        print("   ✅ PluginMarketplace imported successfully")
        
        # Test 2: Create minimal launcher GUI
        print("2. Creating minimal launcher GUI...")
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create a simple launcher GUI mock
        class MockLauncherGUI:
            def __init__(self):
                self._dark_mode = True
                self.current_theme = 'dark'
                self.TAB_THEMES = {
                    'plugin_manager': {
                        'bg': '#1a1a1a',
                        'fg': '#ff99cc',
                        'entry_bg': '#222222',
                        'entry_fg': '#ff99cc',
                        'accent': '#cc6699'
                    }
                }
                self.LIGHT_TAB_THEMES = {
                    'plugin_manager': {
                        'bg': '#f8f9fa',
                        'fg': '#721c24',
                        'entry_bg': '#ffffff',
                        'entry_fg': '#721c24',
                        'accent': '#dc3545'
                    }
                }
            
            def log(self, message):
                print(f"   [LOG] {message}")
            
            def toggle_theme(self):
                self._dark_mode = not self._dark_mode
                self.current_theme = 'dark' if self._dark_mode else 'light'
                self.log(f"Theme toggled to: {self.current_theme}")
        
        launcher_gui = MockLauncherGUI()
        print("   ✅ Mock launcher GUI created")
        
        # Test 3: Create plugin marketplace
        print("3. Creating plugin marketplace...")
        marketplace = PluginMarketplace(launcher_gui)
        print("   ✅ Plugin marketplace created")
        
        # Test 4: Test theme getting
        print("4. Testing theme retrieval...")
        theme = marketplace._get_current_theme()
        print(f"   ✅ Current theme: {theme['bg']} (background)")
        
        # Test 5: Test theme refresh
        print("5. Testing theme refresh...")
        marketplace.refresh_theme()
        print("   ✅ Theme refresh completed")
        
        # Test 6: Toggle theme and test again
        print("6. Testing theme toggle...")
        launcher_gui.toggle_theme()
        marketplace.refresh_theme()
        new_theme = marketplace._get_current_theme()
        print(f"   ✅ New theme: {new_theme['bg']} (background)")
        
        # Test 7: Verify theme changed
        if theme['bg'] != new_theme['bg']:
            print("   ✅ Theme change detected successfully")
        else:
            print("   ❌ Theme change not detected")
            return False
        
        # Cleanup
        root.destroy()
        
        print("\n🎉 All tests passed! Theme responsiveness is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_marketplace_window_creation():
    """Test marketplace window creation"""
    print("\n🧪 Testing Marketplace Window Creation...")
    
    try:
        from utils.plugin_marketplace import PluginMarketplace
        
        root = tk.Tk()
        root.withdraw()
        
        class MockLauncherGUI:
            def __init__(self):
                self._dark_mode = True
                self.current_theme = 'dark'
                self.TAB_THEMES = {
                    'plugin_manager': {
                        'bg': '#1a1a1a',
                        'fg': '#ff99cc',
                        'entry_bg': '#222222',
                        'entry_fg': '#ff99cc',
                        'accent': '#cc6699'
                    }
                }
                self.LIGHT_TAB_THEMES = {
                    'plugin_manager': {
                        'bg': '#f8f9fa',
                        'fg': '#721c24',
                        'entry_bg': '#ffffff',
                        'entry_fg': '#721c24',
                        'accent': '#dc3545'
                    }
                }
            
            def log(self, message):
                print(f"   [LOG] {message}")
            
            def register_theme_window(self, window):
                print("   [LOG] Window registered for theme updates")
        
        launcher_gui = MockLauncherGUI()
        marketplace = PluginMarketplace(launcher_gui)
        
        # Create marketplace window
        marketplace.create_marketplace_window()
        print("   ✅ Marketplace window created")
        
        # Test theme refresh on window
        marketplace.refresh_theme()
        print("   ✅ Window theme refresh completed")
        
        # Close window
        if hasattr(marketplace, 'marketplace_window') and marketplace.marketplace_window:
            marketplace.marketplace_window.window.destroy()
        
        root.destroy()
        print("   ✅ Window cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Window creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Simple Theme Responsiveness Tests...\n")
    
    # Run tests
    test1_passed = test_theme_responsiveness()
    test2_passed = test_marketplace_window_creation()
    
    print(f"\n📊 Test Results:")
    print(f"   Theme Responsiveness: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Window Creation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Theme responsiveness is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
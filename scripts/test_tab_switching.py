#!/usr/bin/env python3
"""
Test script to verify that tab switching works correctly
and that there are no duplicate tabs for Oobabooga and Z-Waifu.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import time

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zwaifu_launcher_gui import LauncherGUI
except ImportError:
    print("Error: Could not import launcher modules")
    sys.exit(1)

def test_tab_switching():
    """Test that tab switching works correctly without duplicates"""
    print("\n🧪 Testing Tab Switching")
    print("=" * 50)
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide the window during testing
    
    try:
        # Create launcher instance
        print("Creating launcher instance...")
        launcher = LauncherGUI(root)
        
        # Get all tab names
        tab_names = []
        for i in range(launcher.notebook.index('end')):
            tab_name = launcher.notebook.tab(i, 'text')
            tab_names.append(tab_name)
        
        print(f"Found {len(tab_names)} tabs:")
        for i, name in enumerate(tab_names):
            print(f"  {i+1}. {name}")
        
        # Check for duplicate tabs
        duplicates = []
        seen = set()
        for name in tab_names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        
        if duplicates:
            print(f"❌ Found duplicate tabs: {duplicates}")
            return False
        else:
            print("✅ No duplicate tabs found")
        
        # Check for specific tabs
        expected_tabs = ["Main", "CMD Flags", "Settings", "About", "Ollama", "RVC", "Logs", "Instance Manager", "Oobabooga", "Z-Waifu", "Advanced Features"]
        
        missing_tabs = []
        for expected in expected_tabs:
            if expected not in tab_names:
                missing_tabs.append(expected)
        
        if missing_tabs:
            print(f"❌ Missing expected tabs: {missing_tabs}")
            return False
        else:
            print("✅ All expected tabs are present")
        
        # Test tab switching
        print("\nTesting tab switching...")
        for i, name in enumerate(tab_names):
            try:
                launcher.notebook.select(i)
                current_tab = launcher.notebook.select()
                current_name = launcher.notebook.tab(current_tab, 'text')
                if current_name == name:
                    print(f"✅ Tab {i+1} ({name}) switches correctly")
                else:
                    print(f"❌ Tab {i+1} ({name}) switching failed - got {current_name}")
                    return False
            except Exception as e:
                print(f"❌ Error switching to tab {i+1} ({name}): {e}")
                return False
        
        print("✅ All tab switching tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        # Clean up
        try:
            root.destroy()
        except:
            pass

def main():
    """Main test function"""
    print("🧪 Tab Switching Test Suite")
    print("=" * 50)
    
    success = test_tab_switching()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tab switching tests passed!")
        print("The launcher should now work correctly without tab switching issues.")
    else:
        print("❌ Some tab switching tests failed.")
        print("There may still be issues with tab creation or switching.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
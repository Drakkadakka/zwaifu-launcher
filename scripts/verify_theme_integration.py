#!/usr/bin/env python3
"""
Verification script for theme integration with main GUI launcher
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
import time

# Add the parent directory to the path to import the main modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

# Diagnostic print
print('sys.path for import:', sys.path)

try:
    from utils.plugin_marketplace import PluginMarketplace
    print('✅ Imported PluginMarketplace')
except Exception as e:
    print('❌ Failed to import PluginMarketplace:', e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from zwaifu_launcher_gui import LauncherGUI
    print('✅ Imported LauncherGUI')
except Exception as e:
    print('❌ Failed to import LauncherGUI:', e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

def verify_theme_integration():
    """Verify that theme integration works with the main GUI"""
    print("🔍 Verifying Theme Integration with Main GUI...")
    
    try:
        # Import the main GUI
        # try:
        #     from zwaifu_launcher_gui import LauncherGUI
        #     from utils.plugin_marketplace import PluginMarketplace
        # except ImportError as e:
        #     print(f"Error: Could not import launcher modules: {e}")
        #     import traceback
        #     traceback.print_exc()
        #     print("sys.path:", sys.path)
        #     print("Make sure you're running this from the project root directory")
        #     return False
        
        print("✅ Main GUI and Plugin Marketplace imported successfully")
        
        # Create root window
        root = tk.Tk()
        root.title("Theme Integration Verification")
        root.geometry("400x300")
        
        # Create launcher GUI
        launcher_gui = LauncherGUI(root)
        print("✅ Launcher GUI created successfully")
        
        # Create plugin marketplace
        marketplace = PluginMarketplace(launcher_gui)
        print("✅ Plugin Marketplace created successfully")
        
        # Test current theme
        current_theme = marketplace._get_current_theme()
        print(f"✅ Current theme background: {current_theme['bg']}")
        
        # Create a simple test interface
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Theme Integration Verification", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status
        status_var = tk.StringVar(value="Ready to test theme integration")
        status_label = ttk.Label(main_frame, textvariable=status_var)
        status_label.pack(pady=(0, 20))
        
        # Test buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def test_theme_toggle():
            """Test theme toggle functionality"""
            try:
                status_var.set("🔄 Toggling theme...")
                root.update()
                
                # Toggle theme
                launcher_gui.toggle_theme()
                
                # Wait a moment for theme to apply
                time.sleep(0.5)
                
                # Check if marketplace theme updated
                new_theme = marketplace._get_current_theme()
                status_var.set(f"✅ Theme toggled! New background: {new_theme['bg']}")
                
                print(f"✅ Theme toggled successfully. New background: {new_theme['bg']}")
                
            except Exception as e:
                status_var.set(f"❌ Error: {e}")
                print(f"❌ Theme toggle failed: {e}")
        
        def test_marketplace_window():
            """Test marketplace window creation"""
            try:
                status_var.set("🛒 Opening marketplace...")
                root.update()
                
                # Create marketplace window
                marketplace.create_marketplace_window()
                
                status_var.set("✅ Marketplace opened! Try toggling theme now.")
                print("✅ Marketplace window created successfully")
                
            except Exception as e:
                status_var.set(f"❌ Error: {e}")
                print(f"❌ Marketplace window creation failed: {e}")
        
        # Theme toggle button
        toggle_btn = ttk.Button(button_frame, text="🌙 Toggle Theme", command=test_theme_toggle)
        toggle_btn.pack(side=tk.LEFT, padx=5)
        
        # Marketplace button
        marketplace_btn = ttk.Button(button_frame, text="🛒 Open Marketplace", command=test_marketplace_window)
        marketplace_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = ttk.Button(button_frame, text="✖ Close", command=root.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = ttk.Label(main_frame, text="1. Click 'Toggle Theme' to test theme switching\n2. Click 'Open Marketplace' to test window creation\n3. Observe theme changes in real-time", 
                               justify=tk.LEFT)
        instructions.pack(pady=20)
        
        print("✅ Test interface created successfully")
        print("🎯 Ready for manual testing!")
        
        # Start the GUI
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Starting Theme Integration Verification...\n")
    
    success = verify_theme_integration()
    
    if success:
        print("\n🎉 Theme integration verification completed successfully!")
    else:
        print("\n❌ Theme integration verification failed!")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 
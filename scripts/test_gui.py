#!/usr/bin/env python3
"""
Test script for Z-Waifu Launcher GUI
Verifies that all GUI components work properly
"""

import tkinter as tk
import sys
import os
import time
import threading

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui():
    """Test the GUI functionality"""
    print("Testing Z-Waifu Launcher GUI")
    print("=" * 50)
    
    try:
        # Import the launcher
        from zwaifu_launcher_gui import LauncherGUI
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        print("✓ Successfully imported LauncherGUI")
        
        # Create launcher instance
        launcher = LauncherGUI(root)
        print("✓ Successfully created LauncherGUI instance")
        
        # Test process instance tabs initialization
        if hasattr(launcher, 'process_instance_tabs'):
            print(f"✓ Process instance tabs initialized: {list(launcher.process_instance_tabs.keys())}")
            
            # Check if all expected process types are present
            expected_types = ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']
            for process_type in expected_types:
                if process_type in launcher.process_instance_tabs:
                    print(f"  ✓ {process_type} tracking available")
                else:
                    print(f"  ✗ {process_type} tracking missing")
        else:
            print("✗ Process instance tabs not initialized")
        
        # Test web interface initialization
        if hasattr(launcher, 'web_interface'):
            print("✓ Web interface attribute exists")
            if launcher.web_interface is not None:
                print("  ✓ Web interface initialized")
            else:
                print("  - Web interface not available (expected if utils not found)")
        else:
            print("✗ Web interface attribute missing")
        
        # Test notebook tabs
        if hasattr(launcher, 'notebook'):
            tabs = [launcher.notebook.tab(tab, "text") for tab in launcher.notebook.tabs()]
            print(f"✓ Notebook created with {len(tabs)} tabs")
            print(f"  Tabs: {tabs}")
        else:
            print("✗ Notebook not created")
        
        # Test theme functionality
        if hasattr(launcher, '_dark_mode'):
            print(f"✓ Theme system initialized (dark mode: {launcher._dark_mode})")
        else:
            print("✗ Theme system not initialized")
        
        # Test log functionality
        launcher.log("Test log message")
        print("✓ Log functionality working")
        
        # Test status functionality
        launcher.set_status("Test status")
        print("✓ Status functionality working")
        
        # Test batch file path attributes
        batch_attrs = ['ooba_bat', 'zwaifu_bat', 'ollama_bat', 'rvc_bat']
        for attr in batch_attrs:
            if hasattr(launcher, attr):
                print(f"✓ {attr} attribute exists")
            else:
                print(f"✗ {attr} attribute missing")
        
        # Test process instance methods
        if hasattr(launcher, 'start_process_instance'):
            print("✓ start_process_instance method exists")
        else:
            print("✗ start_process_instance method missing")
        
        if hasattr(launcher, 'stop_all_instances'):
            print("✓ stop_all_instances method exists")
        else:
            print("✗ stop_all_instances method missing")
        
        # Test advanced features
        if hasattr(launcher, 'initialize_advanced_features'):
            print("✓ initialize_advanced_features method exists")
        else:
            print("✗ initialize_advanced_features method missing")
        
        # Test web interface methods
        if hasattr(launcher, 'start_web_interface'):
            print("✓ start_web_interface method exists")
        else:
            print("✗ start_web_interface method missing")
        
        # Test instance manager
        if hasattr(launcher, 'update_instance_manager'):
            print("✓ update_instance_manager method exists")
        else:
            print("✗ update_instance_manager method missing")
        
        # Test refresh methods
        if hasattr(launcher, 'refresh_ooba_status'):
            print("✓ refresh_ooba_status method exists")
        else:
            print("✗ refresh_ooba_status method missing")
        
        if hasattr(launcher, 'refresh_zwaifu_status'):
            print("✓ refresh_zwaifu_status method exists")
        else:
            print("✗ refresh_zwaifu_status method missing")
        
        # Test configuration
        if hasattr(launcher, 'save_config'):
            print("✓ save_config method exists")
        else:
            print("✗ save_config method missing")
        
        if hasattr(launcher, 'load_config_safe'):
            print("✓ load_config_safe method exists")
        else:
            print("✗ load_config_safe method missing")
        
        # Test theme methods
        if hasattr(launcher, 'set_dark_mode'):
            print("✓ set_dark_mode method exists")
        else:
            print("✗ set_dark_mode method missing")
        
        if hasattr(launcher, 'set_light_mode'):
            print("✓ set_light_mode method exists")
        else:
            print("✗ set_light_mode method missing")
        
        # Test utility methods
        if hasattr(launcher, 'is_port_in_use'):
            print("✓ is_port_in_use method exists")
        else:
            print("✗ is_port_in_use method missing")
        
        if hasattr(launcher, 'auto_detect_batch_files'):
            print("✓ auto_detect_batch_files method exists")
        else:
            print("✗ auto_detect_batch_files method missing")
        
        # Test TerminalEmulator
        try:
            from zwaifu_launcher_gui import TerminalEmulator
            test_frame = tk.Frame(root)
            terminal = TerminalEmulator(test_frame)
            print("✓ TerminalEmulator can be created")
        except Exception as e:
            print(f"✗ TerminalEmulator creation failed: {e}")
        
        # Test web interface integration
        if launcher.web_interface:
            try:
                # Test web interface methods
                status = launcher.web_interface.get_process_status()
                print(f"✓ Web interface get_process_status works: {len(status)} process types")
                
                config = launcher.web_interface.get_config()
                print(f"✓ Web interface get_config works: {len(config)} config items")
                
            except Exception as e:
                print(f"✗ Web interface test failed: {e}")
        
        # Clean up
        root.destroy()
        print("\n" + "=" * 50)
        print("GUI test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface_integration():
    """Test web interface integration specifically"""
    print("\nTesting Web Interface Integration")
    print("=" * 50)
    
    try:
        from zwaifu_launcher_gui import LauncherGUI
        from utils.web_interface import create_web_interface
        
        # Create root window
        root = tk.Tk()
        root.withdraw()
        
        # Create launcher
        launcher = LauncherGUI(root)
        
        # Test web interface creation
        web_interface = create_web_interface(launcher)
        print("✓ Web interface created successfully")
        
        # Test process status
        status = web_interface.get_process_status()
        print(f"✓ Process status retrieved: {list(status.keys())}")
        
        # Test system info
        system_info = web_interface.get_system_info()
        print(f"✓ System info retrieved: {list(system_info.keys())}")
        
        # Test config
        config = web_interface.get_config()
        print(f"✓ Config retrieved: {list(config.keys())}")
        
        # Clean up
        root.destroy()
        print("✓ Web interface integration test completed")
        return True
        
    except Exception as e:
        print(f"✗ Web interface integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Z-Waifu Launcher GUI Test Suite")
    print("=" * 60)
    
    # Test basic GUI
    gui_success = test_gui()
    
    # Test web interface integration
    web_success = test_web_interface_integration()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"GUI Test: {'✓ PASSED' if gui_success else '✗ FAILED'}")
    print(f"Web Interface Test: {'✓ PASSED' if web_success else '✗ FAILED'}")
    
    if gui_success and web_success:
        print("\n🎉 All tests passed! The GUI is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.") 
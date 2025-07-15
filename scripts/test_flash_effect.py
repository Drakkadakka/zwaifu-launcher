#!/usr/bin/env python3
"""
Test script to verify the enhanced flash effect is working correctly.
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

def test_flash_effect():
    """Test the enhanced flash effect"""
    print("\n🧪 Testing Enhanced Flash Effect")
    
    # Create root window
    root = tk.Tk()
    root.title("Flash Effect Test")
    root.geometry("800x600")
    
    # Create launcher instance
    launcher = LauncherGUI(root)
    
    # Create a notebook for testing
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create test tabs
    test_tabs = []
    for i in range(4):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=f"Test Tab {i+1}")
        test_tabs.append(tab)
    
    # Test flash effect for each process type
    process_types = ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']
    
    def test_flash(process_type):
        """Test flash effect for a specific process type"""
        tab_id = notebook.index('end') - 1
        print(f"  🔄 Testing flash effect for {process_type}...")
        launcher.flash_tab(tab_id, process_type)
        
        # Schedule next test
        if process_types:
            next_type = process_types.pop(0)
            root.after(1000, lambda: test_flash(next_type))
        else:
            print("  ✅ All flash tests completed!")
            root.after(2000, root.destroy)
    
    # Start testing
    if process_types:
        first_type = process_types.pop(0)
        root.after(500, lambda: test_flash(first_type))
    
    print("  🎨 Flash effect test started - watch the tabs pulse with different colors!")
    print("  📝 Process colors:")
    print("    - Oobabooga: Red-orange (#ff6b6b)")
    print("    - Z-Waifu: Teal (#4ecdc4)")
    print("    - Ollama: Blue (#45b7d1)")
    print("    - RVC: Mint green (#96ceb4)")
    
    root.mainloop()
    print("✅ Flash effect test completed successfully!")

if __name__ == "__main__":
    test_flash_effect() 
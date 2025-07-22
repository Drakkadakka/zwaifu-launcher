#!/usr/bin/env python3
"""
Test script for Instance Manager tab theme functionality
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_instance_manager_theme():
    """Test the Instance Manager tab theme functionality"""
    print("Testing Instance Manager tab theme...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Instance Manager Theme Test")
    root.geometry("800x600")
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create instance manager tab
    instance_tab = ttk.Frame(notebook)
    notebook.add(instance_tab, text="Instance Manager")
    
    # Test enhanced widgets import
    try:
        from utils.enhanced_widgets import EnhancedScrollableFrame, create_enhanced_treeview
        print("✅ Enhanced widgets imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced widgets: {e}")
        return False
    
    # Create enhanced scrollable frame
    try:
        scrollable_frame_widget = EnhancedScrollableFrame(instance_tab)
        scrollable_frame = scrollable_frame_widget.get_scrollable_frame()
        print("✅ Enhanced scrollable frame created successfully")
    except Exception as e:
        print(f"❌ Failed to create enhanced scrollable frame: {e}")
        return False
    
    # Store canvas and scrollable frame references
    instance_canvas = scrollable_frame_widget.canvas
    instance_scrollable_frame = scrollable_frame
    
    # Create header
    header_frame = ttk.Frame(scrollable_frame)
    header_frame.pack(padx=10, pady=10, fill=tk.X)
    
    ttk.Label(header_frame, text="Instance Manager", font=("Arial", 14, "bold")).pack(anchor=tk.W)
    ttk.Label(header_frame, text="Centralized management of all running process instances").pack(anchor=tk.W)
    
    # Create control buttons
    control_frame = ttk.Frame(scrollable_frame)
    control_frame.pack(padx=10, pady=(0,10), fill=tk.X)
    
    ttk.Button(control_frame, text="Kill All Instances").pack(side=tk.LEFT, padx=(0,5))
    ttk.Button(control_frame, text="Refresh").pack(side=tk.LEFT, padx=5)
    
    # Create instance list
    list_frame = ttk.LabelFrame(scrollable_frame, text="Running Instances")
    list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Create enhanced treeview
    try:
        columns = ('Process', 'Instance', 'Status', 'PID', 'Uptime', 'CPU %', 'Memory %')
        tree_frame, instance_tree = create_enhanced_treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            instance_tree.heading(col, text=col)
            instance_tree.column(col, width=100, minwidth=80)
        
        tree_frame.pack(fill=tk.BOTH, expand=True)
        print("✅ Enhanced treeview created successfully")
    except Exception as e:
        print(f"❌ Failed to create enhanced treeview: {e}")
        return False
    
    # Add some test data
    test_data = [
        ('Oobabooga', 'Instance 1', 'Running', '1234', '00:05:30', '15.2', '8.5'),
        ('Z-Waifu', 'Instance 1', 'Running', '5678', '00:02:15', '12.8', '6.2'),
        ('Ollama', 'Instance 1', 'Stopped', '9012', '00:00:00', '0.0', '0.0'),
    ]
    
    for item in test_data:
        instance_tree.insert('', tk.END, values=item)
    
    # Create instance controls
    instance_control_frame = ttk.Frame(scrollable_frame)
    instance_control_frame.pack(padx=10, pady=(0,10), fill=tk.X)
    
    ttk.Button(instance_control_frame, text="Stop Selected").pack(side=tk.LEFT, padx=(0,5))
    ttk.Button(instance_control_frame, text="Restart Selected").pack(side=tk.LEFT, padx=5)
    ttk.Button(instance_control_frame, text="Kill Selected").pack(side=tk.LEFT, padx=5)
    
    # Pack the scrollable frame widget
    scrollable_frame_widget.pack(fill="both", expand=True)
    
    # Test theme switching
    def test_dark_theme():
        """Test dark theme application"""
        try:
            # Apply dark theme to canvas and scrollable frame
            instance_canvas.config(bg='#1e1e2e')
            instance_scrollable_frame.config(bg='#1e1e2e')
            
            # Apply dark theme to treeview
            style = ttk.Style()
            style.configure("Treeview",
                background='#2d2d2d',
                foreground='#ffffff',
                fieldbackground='#2d2d2d',
                bordercolor='#404040',
                rowheight=25
            )
            style.map("Treeview",
                background=[('selected', '#0078d4')],
                foreground=[('selected', '#ffffff')]
            )
            style.configure("Treeview.Heading",
                background='#1e1e2e',
                foreground='#ffffff',
                bordercolor='#404040'
            )
            
            print("✅ Dark theme applied successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to apply dark theme: {e}")
            return False
    
    def test_light_theme():
        """Test light theme application"""
        try:
            # Apply light theme to canvas and scrollable frame
            instance_canvas.config(bg='#fafafa')
            instance_scrollable_frame.config(bg='#fafafa')
            
            # Apply light theme to treeview
            style = ttk.Style()
            style.configure("Treeview",
                background='#ffffff',
                foreground='#000000',
                fieldbackground='#ffffff',
                bordercolor='#e0e0e0',
                rowheight=25
            )
            style.map("Treeview",
                background=[('selected', '#0078d4')],
                foreground=[('selected', '#ffffff')]
            )
            style.configure("Treeview.Heading",
                background='#f8f9fa',
                foreground='#000000',
                bordercolor='#e0e0e0'
            )
            
            print("✅ Light theme applied successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to apply light theme: {e}")
            return False
    
    # Create theme test buttons
    test_frame = ttk.Frame(root)
    test_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Button(test_frame, text="Test Dark Theme", command=test_dark_theme).pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Light Theme", command=test_light_theme).pack(side=tk.LEFT, padx=5)
    
    # Test both themes
    print("\nTesting theme switching...")
    dark_success = test_dark_theme()
    light_success = test_light_theme()
    
    if dark_success and light_success:
        print("✅ All theme tests passed!")
        result = True
    else:
        print("❌ Some theme tests failed!")
        result = False
    
    # Show the window
    root.mainloop()
    
    return result

if __name__ == "__main__":
    print("Instance Manager Theme Test")
    print("=" * 40)
    
    success = test_instance_manager_theme()
    
    if success:
        print("\n🎉 All tests passed! Instance Manager theme is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed! Please check the implementation.")
        sys.exit(1) 
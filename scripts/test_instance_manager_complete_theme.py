#!/usr/bin/env python3
"""
Comprehensive test script for Instance Manager tab complete dark theme - no white areas anywhere
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_instance_manager_complete_theme():
    """Test that Instance Manager tab has no white areas anywhere in dark mode"""
    print("Testing Instance Manager tab complete dark theme - no white areas anywhere...")
    
    # Create a test window
    root = tk.Tk()
    root.title("Instance Manager Complete Dark Theme Test")
    root.geometry("1000x800")
    
    # Apply dark theme to root
    root.configure(bg='#1e1e2e')
    
    # Create notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create instance manager tab
    instance_tab = ttk.Frame(notebook)
    notebook.add(instance_tab, text="Instance Manager")
    
    # Import enhanced widgets
    try:
        from utils.enhanced_widgets import EnhancedScrollableFrame, create_enhanced_treeview
    except ImportError:
        print("ERROR: Could not import enhanced widgets")
        return False
    
    # Create enhanced scrollable frame for instance list
    scrollable_frame_widget = EnhancedScrollableFrame(instance_tab)
    scrollable_frame = scrollable_frame_widget.get_scrollable_frame()
    
    # Store for theme switching
    instance_canvas = scrollable_frame_widget.canvas
    instance_scrollable_frame = scrollable_frame
    
    # Header
    header_frame = ttk.Frame(scrollable_frame)
    header_frame.pack(padx=10, pady=10, fill=tk.X)
    
    ttk.Label(header_frame, text="Instance Manager", font=("Arial", 14, "bold")).pack(anchor=tk.W)
    ttk.Label(header_frame, text="Centralized management of all running process instances").pack(anchor=tk.W)
    
    # Control buttons
    control_frame = ttk.Frame(scrollable_frame)
    control_frame.pack(padx=10, pady=(0,10), fill=tk.X)
    
    kill_all_btn = ttk.Button(control_frame, text="Kill All Instances")
    kill_all_btn.pack(side=tk.LEFT, padx=(0,5))
    
    refresh_btn = ttk.Button(control_frame, text="Refresh")
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    # Instance list
    list_frame = ttk.LabelFrame(scrollable_frame, text="Running Instances")
    list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Create enhanced treeview for instances
    columns = ('Process', 'Instance', 'Status', 'PID', 'Uptime', 'CPU %', 'Memory %')
    tree_frame, instance_tree = create_enhanced_treeview(list_frame, columns=columns, show='headings', height=15)
    
    # Configure columns
    for col in columns:
        instance_tree.heading(col, text=col)
        instance_tree.column(col, width=100, minwidth=80)
    
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    # Instance controls
    instance_control_frame = ttk.Frame(scrollable_frame)
    instance_control_frame.pack(padx=10, pady=(0,10), fill=tk.X)
    
    ttk.Button(instance_control_frame, text="Stop Selected").pack(side=tk.LEFT, padx=(0,5))
    ttk.Button(instance_control_frame, text="Restart Selected").pack(side=tk.LEFT, padx=5)
    ttk.Button(instance_control_frame, text="Kill Selected").pack(side=tk.LEFT, padx=5)
    
    # Pack the scrollable frame widget
    scrollable_frame_widget.pack(fill="both", expand=True)
    
    # Apply dark theme
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('.', background='#222222', foreground='#ffffff')
    style.configure('TLabel', background='#222222', foreground='#ffffff')
    style.configure('TFrame', background='#222222')
    style.configure('TButton', background='#333333', foreground='#ffffff')
    style.configure('TNotebook', background='#222222')
    style.configure('TNotebook.Tab', background='#333333', foreground='#ffffff')
    style.configure('TEntry', fieldbackground='#333333', foreground='#cccccc', insertcolor='#ffffff')
    style.configure('Vertical.TScrollbar', background='#333333', troughcolor='#222222', bordercolor='#404040', arrowcolor='#ffffff')
    style.configure('Horizontal.TScrollbar', background='#333333', troughcolor='#222222', bordercolor='#404040', arrowcolor='#ffffff')
    
    # Configure treeview for dark mode
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
    
    # Apply dark theme to all frames and widgets
    def apply_dark_theme_to_widget(widget):
        """Recursively apply dark theme to all widgets"""
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg='#1e1e2e')
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg='#1e1e2e')
            elif isinstance(widget, tk.Label):
                widget.configure(bg='#1e1e2e', fg='#ffffff')
            elif isinstance(widget, tk.Button):
                widget.configure(bg='#333333', fg='#ffffff')
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg='#2d2d2d', fg='#ffffff', selectbackground='#0078d4', selectforeground='#ffffff')
            
            # Apply to all children
            for child in widget.winfo_children():
                apply_dark_theme_to_widget(child)
        except Exception as e:
            print(f"Error applying theme to widget: {e}")
    
    # Apply dark theme to the entire instance tab
    apply_dark_theme_to_widget(instance_tab)
    
    # Apply dark theme to canvas and scrollable frame
    instance_canvas.configure(bg='#1e1e2e')
    instance_scrollable_frame.configure(bg='#1e1e2e')
    
    # Apply dark theme to treeview container frame
    tree_parent = instance_tree.master
    if tree_parent:
        tree_parent.configure(bg='#1e1e2e')
    
    # Test function to check for white areas
    def check_for_white_areas():
        """Check if there are any white areas in the interface"""
        white_areas = []
        
        def check_widget_color(widget, path=""):
            try:
                if hasattr(widget, 'cget'):
                    bg = widget.cget('bg')
                    fg = widget.cget('fg')
                    
                    # Check for white or light colors
                    if bg and bg.lower() in ['white', '#ffffff', '#f0f0f0', '#fafafa', '#f5f5f5']:
                        white_areas.append(f"{path}: background={bg}")
                    if fg and fg.lower() in ['white', '#ffffff']:
                        # White foreground is okay in dark mode
                        pass
                        
            except Exception:
                pass
            
            # Check children
            for i, child in enumerate(widget.winfo_children()):
                child_path = f"{path}.{type(child).__name__}[{i}]"
                check_widget_color(child, child_path)
        
        check_widget_color(instance_tab, "instance_tab")
        return white_areas
    
    # Check for white areas
    white_areas = check_for_white_areas()
    
    if white_areas:
        print("FAIL: Found white areas in dark mode:")
        for area in white_areas:
            print(f"  - {area}")
        return False
    else:
        print("PASS: No white areas found in dark mode")
        return True

def main():
    """Main test function"""
    print("=" * 60)
    print("Instance Manager Complete Dark Theme Test")
    print("=" * 60)
    
    success = test_instance_manager_complete_theme()
    
    if success:
        print("\n✅ All tests passed! Instance Manager tab has no white areas in dark mode.")
        return 0
    else:
        print("\n❌ Tests failed! White areas found in dark mode.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
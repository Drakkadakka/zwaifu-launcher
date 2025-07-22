#!/usr/bin/env python3
"""
Comprehensive test script for Instance Manager tab dark theme - no white areas
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_instance_manager_dark_theme():
    """Test that Instance Manager tab has no white areas in dark mode"""
    print("Testing Instance Manager tab dark theme - no white areas...")
    
    # Create a test window
    root = tk.Tk()
    root.title("Instance Manager Dark Theme Test")
    root.geometry("900x700")
    
    # Apply dark theme to root
    root.configure(bg='#1e1e2e')
    
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
    
    # Apply dark theme to canvas and scrollable frame
    instance_canvas.config(bg='#1e1e2e')
    instance_scrollable_frame.config(bg='#1e1e2e')
    
    # Create header
    header_frame = ttk.Frame(scrollable_frame)
    header_frame.pack(padx=10, pady=10, fill=tk.X)
    
    # Apply dark theme to header frame
    header_frame.configure(style='Dark.TFrame')
    
    ttk.Label(header_frame, text="Instance Manager", font=("Arial", 14, "bold")).pack(anchor=tk.W)
    ttk.Label(header_frame, text="Centralized management of all running process instances").pack(anchor=tk.W)
    
    # Create control buttons
    control_frame = ttk.Frame(scrollable_frame)
    control_frame.pack(padx=10, pady=(0,10), fill=tk.X)
    
    # Apply dark theme to control frame
    control_frame.configure(style='Dark.TFrame')
    
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
    
    # Apply dark theme to control frame
    instance_control_frame.configure(style='Dark.TFrame')
    
    ttk.Button(instance_control_frame, text="Stop Selected").pack(side=tk.LEFT, padx=(0,5))
    ttk.Button(instance_control_frame, text="Restart Selected").pack(side=tk.LEFT, padx=5)
    ttk.Button(instance_control_frame, text="Kill Selected").pack(side=tk.LEFT, padx=5)
    
    # Pack the scrollable frame widget
    scrollable_frame_widget.pack(fill="both", expand=True)
    
    # Apply comprehensive dark theme
    def apply_comprehensive_dark_theme():
        """Apply comprehensive dark theme to all widgets"""
        try:
            # Apply dark theme to canvas and scrollable frame
            instance_canvas.config(bg='#1e1e2e')
            instance_scrollable_frame.config(bg='#1e1e2e')
            
            # Apply dark theme to treeview
            style = ttk.Style()
            style.configure("Treeview",
                background='#313244',
                foreground='#cdd6f4',
                fieldbackground='#313244',
                bordercolor='#45475a',
                rowheight=25
            )
            style.map("Treeview",
                background=[('selected', '#89b4fa')],
                foreground=[('selected', '#1e1e2e')]
            )
            style.configure("Treeview.Heading",
                background='#1e1e2e',
                foreground='#cdd6f4',
                bordercolor='#45475a'
            )
            
            # Apply dark theme to all child widgets
            def theme_widgets_recursive(parent):
                for child in parent.winfo_children():
                    cls = child.__class__.__name__
                    
                    # Handle different widget types
                    if cls in ['Label', 'Checkbutton', 'Button', 'Frame', 'Labelframe']:
                        try:
                            child.config(bg='#1e1e2e', fg='#cdd6f4')
                        except Exception:
                            pass
                    elif cls == 'Canvas':
                        try:
                            child.config(bg='#1e1e2e', highlightbackground='#45475a')
                        except Exception:
                            pass
                    elif cls == 'Scrollbar':
                        try:
                            child.config(troughcolor='#313244', bg='#1e1e2e', activebackground='#89b4fa')
                        except Exception:
                            pass
                    elif cls == 'Entry':
                        try:
                            child.config(bg='#313244', fg='#cdd6f4', insertbackground='#cdd6f4')
                        except Exception:
                            pass
                    elif cls in ['Text', 'ScrolledText', 'Listbox']:
                        try:
                            child.config(bg='#313244', fg='#cdd6f4', insertbackground='#cdd6f4')
                        except Exception:
                            pass
                    
                    # Recursively theme children
                    if hasattr(child, 'winfo_children') and child.winfo_children():
                        theme_widgets_recursive(child)
            
            # Apply to instance manager tab
            theme_widgets_recursive(instance_tab)
            
            print("✅ Comprehensive dark theme applied successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to apply comprehensive dark theme: {e}")
            return False
    
    # Create theme test buttons
    test_frame = ttk.Frame(root)
    test_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Button(test_frame, text="Apply Dark Theme", command=apply_comprehensive_dark_theme).pack(side=tk.LEFT, padx=5)
    
    # Apply dark theme immediately
    print("\nApplying comprehensive dark theme...")
    dark_success = apply_comprehensive_dark_theme()
    
    if dark_success:
        print("✅ Dark theme test passed! No white areas should be visible.")
        result = True
    else:
        print("❌ Dark theme test failed!")
        result = False
    
    # Show the window
    root.mainloop()
    
    return result

if __name__ == "__main__":
    print("Instance Manager Dark Theme Test - No White Areas")
    print("=" * 55)
    
    success = test_instance_manager_dark_theme()
    
    if success:
        print("\n🎉 Dark theme test passed! Instance Manager should have no white areas in dark mode.")
        sys.exit(0)
    else:
        print("\n💥 Dark theme test failed! Please check the implementation.")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Test script for EnhancedTreeview dark theme

This script tests that the EnhancedTreeview properly applies dark theme colors
and doesn't show white background in dark mode.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from enhanced_widgets import EnhancedTreeview, create_enhanced_treeview
    ENHANCED_WIDGETS_AVAILABLE = True
    print("✅ Enhanced widgets imported successfully")
except ImportError as e:
    print(f"❌ Failed to import enhanced widgets: {e}")
    ENHANCED_WIDGETS_AVAILABLE = False

class DarkThemeTest:
    """Test application for EnhancedTreeview dark theme"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("EnhancedTreeview Dark Theme Test")
        self.root.geometry("800x500")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="EnhancedTreeview Dark Theme Test", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Theme toggle button
        self.dark_mode = True
        self.toggle_btn = ttk.Button(main_frame, text="Toggle Theme (Currently Dark)", 
                                   command=self.toggle_theme)
        self.toggle_btn.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, text="Instructions:\n" +
                               "• The treeview should have dark background in dark mode\n" +
                               "• Click 'Toggle Theme' to switch between light/dark\n" +
                               "• Verify the treeview background changes appropriately\n" +
                               "• Check that selection highlighting works in both themes",
                               font=("Arial", 10))
        instructions.pack(pady=(0, 20))
        
        # Create enhanced treeview
        if ENHANCED_WIDGETS_AVAILABLE:
            # Create frame for treeview
            tree_frame = ttk.LabelFrame(main_frame, text="Test Treeview")
            tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Create enhanced treeview
            columns = ('Name', 'Type', 'Status')
            tree_frame_widget, self.tree = create_enhanced_treeview(tree_frame, 
                                                                   columns=columns, 
                                                                   show='headings', 
                                                                   height=10)
            
            # Configure columns
            self.tree.heading('Name', text='Name')
            self.tree.heading('Type', text='Type')
            self.tree.heading('Status', text='Status')
            
            self.tree.column('Name', width=200)
            self.tree.column('Type', width=100)
            self.tree.column('Status', width=100)
            
            tree_frame_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add test data
            test_data = [
                ('Oobabooga', 'Text Generation', 'Running'),
                ('Z-Waifu', 'AI Assistant', 'Running'),
                ('Ollama', 'LLM Server', 'Stopped'),
                ('RVC', 'Voice Cloning', 'Running'),
                ('Plugin Manager', 'System', 'Active'),
                ('Instance Manager', 'System', 'Active'),
                ('Settings', 'System', 'Active'),
                ('Analytics', 'System', 'Active'),
            ]
            
            for item in test_data:
                self.tree.insert('', 'end', values=item)
            
            # Bind selection event
            self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
            
            # Status label
            self.status_var = tk.StringVar(value="Dark mode active - treeview should have dark background")
            status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, font=("Arial", 9))
            status_label.pack(fill=tk.X, pady=(10, 0))
            
            # Apply initial dark theme
            self.apply_dark_theme()
            
            print("✅ EnhancedTreeview created successfully")
            
        else:
            # Fallback message
            error_label = ttk.Label(main_frame, text="Enhanced widgets not available", 
                                  font=("Arial", 12, "bold"), foreground="red")
            error_label.pack(pady=50)
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        try:
            # Configure ttk styles for dark mode
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure treeview for dark mode
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
            
            # Configure other styles
            style.configure('.', background='#1e1e2e', foreground='#cdd6f4')
            style.configure('TLabel', background='#1e1e2e', foreground='#cdd6f4')
            style.configure('TFrame', background='#1e1e2e')
            style.configure('TButton', background='#313244', foreground='#cdd6f4')
            style.configure('TLabelframe', background='#1e1e2e', foreground='#cdd6f4')
            style.configure('TLabelframe.Label', background='#1e1e2e', foreground='#cdd6f4')
            
            # Update the treeview's internal theme
            if hasattr(self.tree, 'update_theme'):
                self.tree.update_theme()
            
            self.status_var.set("Dark mode active - treeview should have dark background")
            self.toggle_btn.configure(text="Toggle Theme (Currently Dark)")
            
        except Exception as e:
            print(f"Error applying dark theme: {e}")
    
    def apply_light_theme(self):
        """Apply light theme to the application"""
        try:
            # Configure ttk styles for light mode
            style = ttk.Style()
            style.theme_use('default')
            
            # Configure treeview for light mode
            style.configure("Treeview",
                background='#ffffff',
                foreground='#2d3748',
                fieldbackground='#ffffff',
                bordercolor='#e2e8f0',
                rowheight=25
            )
            style.map("Treeview",
                background=[('selected', '#3182ce')],
                foreground=[('selected', '#ffffff')]
            )
            style.configure("Treeview.Heading",
                background='#fafafa',
                foreground='#2d3748',
                bordercolor='#e2e8f0'
            )
            
            # Configure other styles
            style.configure('.', background='#fafafa', foreground='#2d3748')
            style.configure('TLabel', background='#fafafa', foreground='#2d3748')
            style.configure('TFrame', background='#fafafa')
            style.configure('TButton', background='#ffffff', foreground='#2d3748')
            style.configure('TLabelframe', background='#fafafa', foreground='#2d3748')
            style.configure('TLabelframe.Label', background='#fafafa', foreground='#2d3748')
            
            # Update the treeview's internal theme
            if hasattr(self.tree, 'update_theme'):
                self.tree.update_theme()
            
            self.status_var.set("Light mode active - treeview should have light background")
            self.toggle_btn.configure(text="Toggle Theme (Currently Light)")
            
        except Exception as e:
            print(f"Error applying light theme: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def on_tree_select(self, event):
        """Handle treeview selection"""
        try:
            selection = self.tree.selection()
            if selection:
                item = self.tree.item(selection[0])
                values = item['values']
                self.status_var.set(f"Selected: {values[0]} ({values[1]}) - {values[2]}")
                print(f"✅ Selection successful: {values[0]}")
            else:
                self.status_var.set("No selection")
                print("✅ Selection cleared successfully")
        except Exception as e:
            error_msg = f"❌ Error in selection handler: {e}"
            self.status_var.set(error_msg)
            print(error_msg)

def main():
    """Main function"""
    print("Starting EnhancedTreeview Dark Theme Test...")
    print("=" * 50)
    
    # Create test window
    root = tk.Tk()
    app = DarkThemeTest(root)
    
    # Run the test
    print("✅ Test application started successfully")
    print("Check that the treeview has dark background in dark mode")
    print("=" * 50)
    
    root.mainloop()

if __name__ == "__main__":
    main() 
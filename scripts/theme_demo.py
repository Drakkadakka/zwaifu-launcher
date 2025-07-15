#!/usr/bin/env python3
"""
Theme System Demonstration for Z-Waifu Launcher
Shows the theme system in action with a simple GUI demo.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import json

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class ThemeDemo:
    """Simple demonstration of the theme system"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Z-Waifu Launcher Theme Demo")
        self.root.geometry("800x600")
        
        # Initialize theme manager
        try:
            from utils import ThemeManager
            self.theme_manager = ThemeManager(self)
            self.current_theme = 'light'
            self._dark_mode = False
        except Exception as e:
            print(f"Failed to initialize ThemeManager: {e}")
            self.theme_manager = None
        
        self.create_interface()
        self.apply_theme('light')
        
    def create_interface(self):
        """Create the demo interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Z-Waifu Launcher Theme System Demo", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Theme selection frame
        theme_frame = ttk.LabelFrame(main_frame, text="Theme Selection")
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Theme buttons
        themes = [
            ('Light', 'light'),
            ('Dark', 'dark'),
            ('Dark Blue', 'dark_blue'),
            ('Dark Green', 'dark_green'),
            ('Dark Purple', 'dark_purple'),
            ('High Contrast', 'high_contrast')
        ]
        
        button_frame = ttk.Frame(theme_frame)
        button_frame.pack(padx=10, pady=10)
        
        for i, (name, theme_id) in enumerate(themes):
            btn = ttk.Button(button_frame, text=name, 
                           command=lambda t=theme_id: self.apply_theme(t))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
        
        # Demo widgets frame
        demo_frame = ttk.LabelFrame(main_frame, text="Demo Widgets")
        demo_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create various widgets to demonstrate theming
        self.create_demo_widgets(demo_frame)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Theme editor button
        if self.theme_manager:
            editor_btn = ttk.Button(status_frame, text="Open Theme Editor", 
                                  command=self.open_theme_editor)
            editor_btn.pack(side=tk.RIGHT)
        
    def create_demo_widgets(self, parent):
        """Create demo widgets to show theming"""
        # Left column
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Entry widgets
        entry_frame = ttk.LabelFrame(left_frame, text="Entry Widgets")
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(entry_frame, text="Text Entry:").pack(anchor=tk.W, padx=5, pady=2)
        self.text_entry = ttk.Entry(entry_frame)
        self.text_entry.pack(fill=tk.X, padx=5, pady=2)
        self.text_entry.insert(0, "Sample text entry")
        
        ttk.Label(entry_frame, text="Password Entry:").pack(anchor=tk.W, padx=5, pady=2)
        self.pass_entry = ttk.Entry(entry_frame, show="*")
        self.pass_entry.pack(fill=tk.X, padx=5, pady=2)
        self.pass_entry.insert(0, "password123")
        
        # Buttons
        button_frame = ttk.LabelFrame(left_frame, text="Buttons")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Primary Button", 
                  command=self.button_click).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(button_frame, text="Secondary Button", 
                  command=self.button_click).pack(fill=tk.X, padx=5, pady=2)
        
        # Checkboxes and radio buttons
        control_frame = ttk.LabelFrame(left_frame, text="Controls")
        control_frame.pack(fill=tk.X)
        
        self.check_var = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="Enable feature", 
                       variable=self.check_var).pack(anchor=tk.W, padx=5, pady=2)
        
        self.radio_var = tk.StringVar(value="option1")
        ttk.Radiobutton(control_frame, text="Option 1", 
                       variable=self.radio_var, value="option1").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(control_frame, text="Option 2", 
                       variable=self.radio_var, value="option2").pack(anchor=tk.W, padx=5, pady=2)
        
        # Right column
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Text widget
        text_frame = ttk.LabelFrame(right_frame, text="Text Widget")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text_widget = tk.Text(text_frame, height=8, width=30)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_widget.insert(tk.END, "This is a sample text widget.\n\nIt demonstrates how text widgets are themed in different color schemes.\n\nYou can type here to see the cursor and selection colors.")
        
        # Listbox
        list_frame = ttk.LabelFrame(right_frame, text="List Widget")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(list_frame, height=6)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add some sample items
        items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6"]
        for item in items:
            self.listbox.insert(tk.END, item)
        
    def apply_theme(self, theme_name):
        """Apply a theme to the demo"""
        if self.theme_manager:
            success = self.theme_manager.apply_theme(theme_name)
            if success:
                self.current_theme = theme_name
                self._dark_mode = theme_name != 'light'
                self.status_label.config(text=f"Theme applied: {theme_name}")
                print(f"Theme applied: {theme_name}")
            else:
                self.status_label.config(text=f"Failed to apply theme: {theme_name}")
                print(f"Failed to apply theme: {theme_name}")
        else:
            # Fallback theming
            if theme_name == 'light':
                self.root.configure(bg='#f0f0f0')
                self._dark_mode = False
            else:
                self.root.configure(bg='#222222')
                self._dark_mode = True
            self.current_theme = theme_name
            self.status_label.config(text=f"Basic theme applied: {theme_name}")
    
    def button_click(self):
        """Handle button clicks"""
        messagebox.showinfo("Button Click", "Button clicked! Theme system is working.")
    
    def open_theme_editor(self):
        """Open the theme editor"""
        if self.theme_manager:
            try:
                self.theme_manager.create_theme_editor_window()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open theme editor: {e}")
        else:
            messagebox.showwarning("Warning", "Theme manager not available")
    
    def run(self):
        """Run the demo"""
        self.root.mainloop()

def main():
    """Main function"""
    print("🎨 Starting Z-Waifu Launcher Theme Demo")
    print("This demo shows the theme system in action.")
    print("Try different themes to see how the interface changes.")
    print()
    
    demo = ThemeDemo()
    demo.run()

if __name__ == "__main__":
    main() 
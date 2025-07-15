#!/usr/bin/env python3
"""
Test script to verify theme toggle functionality
"""

import tkinter as tk
from tkinter import ttk
import json
import os

# Mock the launcher GUI class with just the theme functionality
class TestLauncherGUI:
    def __init__(self, root):
        self.root = root
        root.title("Theme Toggle Test")
        root.geometry("400x300")
        
        # Track current theme state
        self._dark_mode = False
        self.current_theme = "light"
        
        # Create theme toggle button
        self.theme_toggle_btn = ttk.Button(root, text="☀️ ", width=3, command=self.toggle_theme)
        self.theme_toggle_btn.place(relx=1.0, y=2, anchor="ne")
        
        # Create some test widgets
        test_frame = ttk.Frame(root)
        test_frame.pack(padx=20, pady=50, fill=tk.BOTH, expand=True)
        
        ttk.Label(test_frame, text="Theme Toggle Test").pack(pady=10)
        ttk.Button(test_frame, text="Test Button").pack(pady=5)
        ttk.Entry(test_frame).pack(pady=5)
        
        # Apply initial theme
        self.load_theme()
    
    def toggle_theme(self):
        """
        Toggles between dark and light themes.
        """
        if self._dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()
    
    def set_dark_mode(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background='#222222', foreground='#ffffff')
        style.configure('TLabel', background='#222222', foreground='#ffffff')
        style.configure('TFrame', background='#222222')
        style.configure('TButton', background='#333333', foreground='#ffffff')
        style.configure('TEntry', fieldbackground='#333333', foreground='#cccccc', insertcolor='#ffffff')
        self.root.configure(bg='#222222')
        self.current_theme = 'dark'
        self._dark_mode = True
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.config(text=" 🌙")
        print("Dark mode applied")
    
    def set_light_mode(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('.', background='#f0f0f0', foreground='#000000')
        style.configure('TLabel', background='#f0f0f0', foreground='#000000')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', background='#e0e0e0', foreground='#000000')
        style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000', insertcolor='#000000')
        self.root.configure(bg='#f0f0f0')
        self.current_theme = 'light'
        self._dark_mode = False
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.config(text="☀️ ")
        print("Light mode applied")
    
    def load_theme(self):
        """
        Load and apply the saved theme from config.
        """
        if hasattr(self, 'current_theme'):
            if self.current_theme == 'dark':
                self.set_dark_mode()
                self._dark_mode = True
                if hasattr(self, 'theme_toggle_btn'):
                    self.theme_toggle_btn.config(text=" 🌙")
            else:
                self.set_light_mode()
                self._dark_mode = False
                if hasattr(self, 'theme_toggle_btn'):
                    self.theme_toggle_btn.config(text="☀️ ")
        else:
            # Default to light theme
            self.set_light_mode()
            self._dark_mode = False
            if hasattr(self, 'theme_toggle_btn'):
                self.theme_toggle_btn.config(text="☀️ ")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestLauncherGUI(root)
    print("Theme toggle test started. Click the sun/moon button in the top-right corner to toggle themes.")
    root.mainloop() 
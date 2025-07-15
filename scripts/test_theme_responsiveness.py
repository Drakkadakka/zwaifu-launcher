#!/usr/bin/env python3
"""
Test script for plugin marketplace theme responsiveness
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the parent directory to the path to import the main modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.plugin_marketplace import PluginMarketplace
    from zwaifu_launcher_gui import LauncherGUI
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the scripts directory")
    sys.exit(1)

class ThemeResponsivenessTest:
    """Test class for theme responsiveness"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Theme Responsiveness Test")
        self.root.geometry("800x600")
        
        # Create a minimal launcher GUI for testing
        self.launcher_gui = LauncherGUI(self.root)
        
        # Create plugin marketplace
        self.marketplace = PluginMarketplace(self.launcher_gui)
        
        self.create_test_interface()
        
    def create_test_interface(self):
        """Create the test interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Plugin Marketplace Theme Responsiveness Test", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame, text="This test verifies that the plugin marketplace window updates its theme immediately when the main GUI theme changes.", 
                               wraplength=600)
        instructions.pack(pady=(0, 20))
        
        # Test buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Open marketplace button
        open_marketplace_btn = ttk.Button(button_frame, text="🛒 Open Plugin Marketplace", 
                                        command=self.open_marketplace)
        open_marketplace_btn.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(button_frame, text="🌙 Switch to Light Mode", 
                                   command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        # Test results frame
        results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Results text
        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready for testing")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Update theme button text
        self.update_theme_button()
        
    def open_marketplace(self):
        """Open the plugin marketplace"""
        try:
            self.log("Opening plugin marketplace...")
            self.marketplace.create_marketplace_window()
            self.log("✅ Plugin marketplace opened successfully")
            self.status_var.set("Plugin marketplace opened - try toggling theme")
        except Exception as e:
            self.log(f"❌ Error opening plugin marketplace: {e}")
            self.status_var.set("Error opening plugin marketplace")
    
    def toggle_theme(self):
        """Toggle the theme"""
        try:
            self.log("🔄 Toggling theme...")
            self.launcher_gui.toggle_theme()
            self.update_theme_button()
            self.log("✅ Theme toggled successfully")
            self.status_var.set("Theme toggled - check if marketplace window updated")
        except Exception as e:
            self.log(f"❌ Error toggling theme: {e}")
            self.status_var.set("Error toggling theme")
    
    def update_theme_button(self):
        """Update the theme button text"""
        if self.launcher_gui._dark_mode:
            self.theme_btn.config(text="☀️ Switch to Light Mode")
        else:
            self.theme_btn.config(text="🌙 Switch to Dark Mode")
    
    def log(self, message):
        """Log a message to the results text"""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.results_text.configure(state=tk.DISABLED)
        print(message)
    
    def run(self):
        """Run the test"""
        self.log("🚀 Theme Responsiveness Test Started")
        self.log("Current theme: " + ("Dark" if self.launcher_gui._dark_mode else "Light"))
        self.log("")
        self.log("Instructions:")
        self.log("1. Click 'Open Plugin Marketplace' to open the marketplace window")
        self.log("2. Click 'Toggle Theme' to switch between light and dark modes")
        self.log("3. Observe if the marketplace window updates its theme immediately")
        self.log("4. Check the logs below for any errors")
        self.log("")
        
        self.root.mainloop()

def main():
    """Main function"""
    print("Starting Theme Responsiveness Test...")
    
    try:
        test = ThemeResponsivenessTest()
        test.run()
    except Exception as e:
        print(f"Error running test: {e}")
        messagebox.showerror("Test Error", f"Failed to run test:\n{e}")

if __name__ == "__main__":
    main() 
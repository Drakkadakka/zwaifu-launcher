#!/usr/bin/env python3
"""
Test script for enhanced widgets functionality

This script demonstrates the enhanced widget features including:
- Single-click selection and highlighting
- Enhanced scrolling with mouse wheel support
- Improved visual feedback
- Keyboard navigation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from enhanced_widgets import EnhancedTreeview, EnhancedListbox, create_enhanced_treeview, create_enhanced_listbox
    ENHANCED_WIDGETS_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced widgets not available: {e}")
    ENHANCED_WIDGETS_AVAILABLE = False

class EnhancedWidgetsDemo:
    """Demo application for enhanced widgets"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Widgets Demo")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhanced Widgets Demo", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for different demos
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create demo tabs
        self.create_treeview_demo()
        self.create_listbox_demo()
        self.create_scrolling_demo()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def create_treeview_demo(self):
        """Create treeview demo tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Enhanced Treeview")
        
        # Instructions
        instructions = ttk.Label(tab, text="Enhanced Treeview Features:\n" +
                               "• Single-click to select items\n" +
                               "• Mouse wheel scrolling\n" +
                               "• Arrow key navigation\n" +
                               "• Visual highlighting\n" +
                               "• Home/End key support",
                               font=("Arial", 10))
        instructions.pack(pady=10)
        
        # Create enhanced treeview
        if ENHANCED_WIDGETS_AVAILABLE:
            tree_frame, self.tree = create_enhanced_treeview(tab, columns=('Name', 'Type', 'Size'), 
                                                           show='headings', height=10)
            
            # Configure columns
            self.tree.heading('Name', text='Name')
            self.tree.heading('Type', text='Type')
            self.tree.heading('Size', text='Size')
            
            self.tree.column('Name', width=200)
            self.tree.column('Type', width=100)
            self.tree.column('Size', width=100)
            
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add sample data
            sample_data = [
                ('Document 1', 'PDF', '2.5 MB'),
                ('Image 1', 'PNG', '1.2 MB'),
                ('Video 1', 'MP4', '15.7 MB'),
                ('Audio 1', 'MP3', '3.8 MB'),
                ('Archive 1', 'ZIP', '8.9 MB'),
                ('Document 2', 'DOCX', '1.1 MB'),
                ('Image 2', 'JPG', '856 KB'),
                ('Video 2', 'AVI', '22.3 MB'),
                ('Audio 2', 'WAV', '12.4 MB'),
                ('Archive 2', 'RAR', '5.6 MB'),
                ('Document 3', 'TXT', '45 KB'),
                ('Image 3', 'GIF', '2.1 MB'),
                ('Video 3', 'MOV', '18.9 MB'),
                ('Audio 3', 'FLAC', '25.7 MB'),
                ('Archive 3', '7Z', '3.2 MB'),
            ]
            
            for item in sample_data:
                self.tree.insert('', 'end', values=item)
            
            # Bind selection event
            self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
            
        else:
            # Fallback to regular treeview
            self.tree = ttk.Treeview(tab, columns=('Name', 'Type', 'Size'), show='headings', height=10)
            self.tree.heading('Name', text='Name')
            self.tree.heading('Type', text='Type')
            self.tree.heading('Size', text='Size')
            
            self.tree.column('Name', width=200)
            self.tree.column('Type', width=100)
            self.tree.column('Size', width=100)
            
            self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add sample data
            sample_data = [
                ('Document 1', 'PDF', '2.5 MB'),
                ('Image 1', 'PNG', '1.2 MB'),
                ('Video 1', 'MP4', '15.7 MB'),
            ]
            
            for item in sample_data:
                self.tree.insert('', 'end', values=item)
    
    def create_listbox_demo(self):
        """Create listbox demo tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Enhanced Listbox")
        
        # Instructions
        instructions = ttk.Label(tab, text="Enhanced Listbox Features:\n" +
                               "• Single-click to select items\n" +
                               "• Mouse wheel scrolling\n" +
                               "• Arrow key navigation\n" +
                               "• Visual highlighting\n" +
                               "• Home/End key support",
                               font=("Arial", 10))
        instructions.pack(pady=10)
        
        # Create enhanced listbox
        if ENHANCED_WIDGETS_AVAILABLE:
            listbox_frame, self.listbox = create_enhanced_listbox(tab, height=15)
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add sample data
            sample_items = [
                "Apple", "Banana", "Cherry", "Date", "Elderberry",
                "Fig", "Grape", "Honeydew", "Kiwi", "Lemon",
                "Mango", "Nectarine", "Orange", "Papaya", "Quince",
                "Raspberry", "Strawberry", "Tangerine", "Ugli fruit", "Vanilla"
            ]
            
            for item in sample_items:
                self.listbox.insert(tk.END, item)
            
            # Bind selection event
            self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
            
        else:
            # Fallback to regular listbox
            self.listbox = tk.Listbox(tab, height=15)
            self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add sample data
            sample_items = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
            
            for item in sample_items:
                self.listbox.insert(tk.END, item)
    
    def create_scrolling_demo(self):
        """Create scrolling demo tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Enhanced Scrolling")
        
        # Instructions
        instructions = ttk.Label(tab, text="Enhanced Scrolling Features:\n" +
                               "• Mouse wheel scrolling\n" +
                               "• Smooth scrolling\n" +
                               "• Cross-platform support",
                               font=("Arial", 10))
        instructions.pack(pady=10)
        
        # Create scrollable text area
        text_frame = ttk.Frame(tab)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_area = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add sample content
        sample_text = """Enhanced Widgets Demo

This is a demonstration of the enhanced widget functionality that has been added to the Z-Waifu Launcher GUI.

Features Demonstrated:

1. Single-Click Selection
   - Click once to select and highlight items
   - No need for double-clicking
   - Visual feedback with highlighting

2. Enhanced Scrolling
   - Mouse wheel support for all scrollable widgets
   - Smooth scrolling behavior
   - Cross-platform compatibility (Windows, Linux, macOS)

3. Keyboard Navigation
   - Arrow keys for navigation
   - Home/End keys for quick navigation
   - Improved accessibility

4. Visual Improvements
   - Better highlighting colors
   - Consistent theming
   - Modern appearance

5. Performance Optimizations
   - Efficient event handling
   - Reduced memory usage
   - Smooth animations

The enhanced widgets provide a much better user experience compared to standard Tkinter widgets. Users can now:
- Navigate more efficiently with single clicks
- Scroll smoothly with mouse wheel
- Use keyboard shortcuts for quick navigation
- Enjoy consistent visual feedback

This enhancement makes the Z-Waifu Launcher more user-friendly and professional-looking.

Technical Implementation:
- Custom widget classes that inherit from standard Tkinter widgets
- Event binding for mouse and keyboard interactions
- Theme-aware styling
- Cross-platform compatibility
- Graceful fallback to standard widgets if enhanced widgets are not available

The implementation is modular and can be easily extended with additional features in the future.
"""
        
        self.text_area.insert(tk.END, sample_text)
        self.text_area.config(state=tk.DISABLED)
        
        # Apply enhanced scrolling if available
        if ENHANCED_WIDGETS_AVAILABLE:
            try:
                from enhanced_widgets import apply_enhanced_scrolling
                apply_enhanced_scrolling(self.text_area)
                self.status_var.set("Enhanced scrolling applied to text area")
            except Exception as e:
                self.status_var.set(f"Failed to apply enhanced scrolling: {e}")
    
    def on_tree_select(self, event):
        """Handle treeview selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.status_var.set(f"Selected: {values[0]} ({values[1]}) - {values[2]}")
    
    def on_listbox_select(self, event):
        """Handle listbox selection"""
        selection = self.listbox.curselection()
        if selection:
            item = self.listbox.get(selection[0])
            self.status_var.set(f"Selected: {item}")

def main():
    """Main function"""
    root = tk.Tk()
    
    # Set theme if available
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except:
        pass
    
    app = EnhancedWidgetsDemo(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 
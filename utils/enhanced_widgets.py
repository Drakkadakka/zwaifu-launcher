"""
Enhanced Widget Utilities for Z-Waifu Launcher

This module provides enhanced functionality for GUI widgets including:
- Single-click selection and highlighting
- Enhanced scrolling with mouse wheel support
- Improved visual feedback
- Keyboard navigation
"""

import tkinter as tk
from tkinter import ttk
import platform


class EnhancedTreeview(ttk.Treeview):
    """Enhanced Treeview with single-click selection and improved scrolling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_enhanced_features()
    
    def _setup_enhanced_features(self):
        """Setup enhanced features for the treeview"""
        # Bind single-click selection
        self.bind('<Button-1>', self._on_single_click)
        
        # Bind mouse wheel scrolling
        self.bind('<MouseWheel>', self._on_mousewheel)
        self.bind('<Button-4>', self._on_mousewheel)  # Linux scroll up
        self.bind('<Button-5>', self._on_mousewheel)  # Linux scroll down
        
        # Bind keyboard navigation
        self.bind('<Up>', self._on_arrow_key)
        self.bind('<Down>', self._on_arrow_key)
        self.bind('<Home>', self._on_home_end)
        self.bind('<End>', self._on_home_end)
        
        # Bind selection highlighting
        self.bind('<<TreeviewSelect>>', self._on_selection_change)
        
        # Store selection state
        self._last_selection = None
        self._highlight_tag = 'highlighted'
        
        # Configure highlight tag
        self.tag_configure(self._highlight_tag, background='#0078d4', foreground='white')
    
    def _on_single_click(self, event):
        """Handle single-click selection"""
        try:
            # Get the item under the cursor
            item = self.identify_row(event.y)
            if item:
                # Clear previous selection
                self.selection_remove(self.selection())
                # Select the clicked item
                self.selection_add(item)
                # Ensure the item is visible
                self.see(item)
                # Focus on the treeview
                self.focus_set()
                # Trigger selection event
                self.event_generate('<<TreeviewSelect>>')
        except Exception as e:
            print(f"Error in single click handler: {e}")
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        try:
            # Determine scroll direction and amount
            if platform.system() == "Windows":
                delta = int(event.delta / 120)
            elif event.num == 4:  # Linux scroll up
                delta = -1
            elif event.num == 5:  # Linux scroll down
                delta = 1
            else:
                delta = 0
            
            # Scroll the treeview
            self.yview_scroll(delta, "units")
            
            # Prevent event propagation
            return "break"
        except Exception as e:
            print(f"Error in mousewheel handler: {e}")
    
    def _on_arrow_key(self, event):
        """Handle arrow key navigation"""
        try:
            current_selection = self.selection()
            if not current_selection:
                # If nothing is selected, select the first item
                children = self.get_children()
                if children:
                    self.selection_set(children[0])
                    self.see(children[0])
                return "break"
            
            current_item = current_selection[0]
            children = self.get_children()
            
            if not children:
                return "break"
            
            try:
                current_index = children.index(current_item)
            except ValueError:
                current_index = 0
            
            if event.keysym == 'Up':
                if current_index > 0:
                    new_item = children[current_index - 1]
                    self.selection_set(new_item)
                    self.see(new_item)
            elif event.keysym == 'Down':
                if current_index < len(children) - 1:
                    new_item = children[current_index + 1]
                    self.selection_set(new_item)
                    self.see(new_item)
            
            return "break"
        except Exception as e:
            print(f"Error in arrow key handler: {e}")
    
    def _on_home_end(self, event):
        """Handle Home/End key navigation"""
        try:
            children = self.get_children()
            if not children:
                return "break"
            
            if event.keysym == 'Home':
                self.selection_set(children[0])
                self.see(children[0])
            elif event.keysym == 'End':
                self.selection_set(children[-1])
                self.see(children[-1])
            
            return "break"
        except Exception as e:
            print(f"Error in home/end handler: {e}")
    
    def _on_selection_change(self, event):
        """Handle selection change with visual feedback"""
        try:
            # Remove highlight from previous selection
            if self._last_selection:
                self.tag_remove(self._highlight_tag, self._last_selection)
            
            # Add highlight to current selection
            current_selection = self.selection()
            if current_selection:
                self._last_selection = current_selection[0]
                self.tag_add(self._highlight_tag, self._last_selection)
        except Exception as e:
            print(f"Error in selection change handler: {e}")
    
    def clear_selection(self):
        """Clear selection and remove highlighting"""
        self.selection_remove(self.selection())
        if self._last_selection:
            self.tag_remove(self._highlight_tag, self._last_selection)
            self._last_selection = None


class EnhancedListbox(tk.Listbox):
    """Enhanced Listbox with single-click selection and improved scrolling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_enhanced_features()
    
    def _setup_enhanced_features(self):
        """Setup enhanced features for the listbox"""
        # Bind single-click selection
        self.bind('<Button-1>', self._on_single_click)
        
        # Bind mouse wheel scrolling
        self.bind('<MouseWheel>', self._on_mousewheel)
        self.bind('<Button-4>', self._on_mousewheel)  # Linux scroll up
        self.bind('<Button-5>', self._on_mousewheel)  # Linux scroll down
        
        # Bind keyboard navigation
        self.bind('<Up>', self._on_arrow_key)
        self.bind('<Down>', self._on_arrow_key)
        self.bind('<Home>', self._on_home_end)
        self.bind('<End>', self._on_home_end)
        
        # Bind selection highlighting
        self.bind('<<ListboxSelect>>', self._on_selection_change)
        
        # Store selection state
        self._last_selection = None
        self._highlight_tag = 'highlighted'
        
        # Configure highlight tag
        self.tag_configure(self._highlight_tag, background='#0078d4', foreground='white')
    
    def _on_single_click(self, event):
        """Handle single-click selection"""
        try:
            # Get the index under the cursor
            index = self.nearest(event.y)
            if index >= 0:
                # Clear previous selection
                self.selection_clear(0, tk.END)
                # Select the clicked item
                self.selection_set(index)
                # Ensure the item is visible
                self.see(index)
                # Focus on the listbox
                self.focus_set()
                # Trigger selection event
                self.event_generate('<<ListboxSelect>>')
        except Exception as e:
            print(f"Error in single click handler: {e}")
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        try:
            # Determine scroll direction and amount
            if platform.system() == "Windows":
                delta = int(event.delta / 120)
            elif event.num == 4:  # Linux scroll up
                delta = -1
            elif event.num == 5:  # Linux scroll down
                delta = 1
            else:
                delta = 0
            
            # Scroll the listbox
            self.yview_scroll(delta, "units")
            
            # Prevent event propagation
            return "break"
        except Exception as e:
            print(f"Error in mousewheel handler: {e}")
    
    def _on_arrow_key(self, event):
        """Handle arrow key navigation"""
        try:
            current_selection = self.curselection()
            if not current_selection:
                # If nothing is selected, select the first item
                if self.size() > 0:
                    self.selection_set(0)
                    self.see(0)
                return "break"
            
            current_index = current_selection[0]
            
            if event.keysym == 'Up':
                if current_index > 0:
                    self.selection_clear(0, tk.END)
                    self.selection_set(current_index - 1)
                    self.see(current_index - 1)
            elif event.keysym == 'Down':
                if current_index < self.size() - 1:
                    self.selection_clear(0, tk.END)
                    self.selection_set(current_index + 1)
                    self.see(current_index + 1)
            
            return "break"
        except Exception as e:
            print(f"Error in arrow key handler: {e}")
    
    def _on_home_end(self, event):
        """Handle Home/End key navigation"""
        try:
            if self.size() == 0:
                return "break"
            
            if event.keysym == 'Home':
                self.selection_clear(0, tk.END)
                self.selection_set(0)
                self.see(0)
            elif event.keysym == 'End':
                self.selection_clear(0, tk.END)
                self.selection_set(self.size() - 1)
                self.see(self.size() - 1)
            
            return "break"
        except Exception as e:
            print(f"Error in home/end handler: {e}")
    
    def _on_selection_change(self, event):
        """Handle selection change with visual feedback"""
        try:
            # Remove highlight from previous selection
            if self._last_selection is not None:
                self.tag_remove(self._highlight_tag, self._last_selection)
            
            # Add highlight to current selection
            current_selection = self.curselection()
            if current_selection:
                self._last_selection = current_selection[0]
                self.tag_add(self._highlight_tag, self._last_selection)
        except Exception as e:
            print(f"Error in selection change handler: {e}")
    
    def clear_selection(self):
        """Clear selection and remove highlighting"""
        self.selection_clear(0, tk.END)
        if self._last_selection is not None:
            self.tag_remove(self._highlight_tag, self._last_selection)
            self._last_selection = None


class EnhancedScrollableFrame(tk.Frame):
    """Enhanced scrollable frame with improved scrolling behavior"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_scrollable_frame()
    
    def _setup_scrollable_frame(self):
        """Setup the scrollable frame with canvas and scrollbar"""
        # Create canvas
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mouse wheel to canvas
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', self._on_mousewheel)  # Linux scroll up
        self.canvas.bind('<Button-5>', self._on_mousewheel)  # Linux scroll down
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        try:
            # Determine scroll direction and amount
            if platform.system() == "Windows":
                delta = int(event.delta / 120)
            elif event.num == 4:  # Linux scroll up
                delta = -1
            elif event.num == 5:  # Linux scroll down
                delta = 1
            else:
                delta = 0
            
            # Scroll the canvas
            self.canvas.yview_scroll(delta, "units")
            
            # Prevent event propagation
            return "break"
        except Exception as e:
            print(f"Error in mousewheel handler: {e}")
    
    def get_scrollable_frame(self):
        """Get the scrollable frame for adding widgets"""
        return self.scrollable_frame


def create_enhanced_treeview(parent, **kwargs):
    """Create an enhanced treeview with scrollbar"""
    # Create frame to hold treeview and scrollbar
    frame = tk.Frame(parent)
    
    # Create enhanced treeview
    treeview = EnhancedTreeview(frame, **kwargs)
    
    # Create scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=treeview.yview)
    treeview.configure(yscrollcommand=scrollbar.set)
    
    # Pack treeview and scrollbar
    treeview.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return frame, treeview


def create_enhanced_listbox(parent, **kwargs):
    """Create an enhanced listbox with scrollbar"""
    # Create frame to hold listbox and scrollbar
    frame = tk.Frame(parent)
    
    # Create enhanced listbox
    listbox = EnhancedListbox(frame, **kwargs)
    
    # Create scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    
    # Pack listbox and scrollbar
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return frame, listbox


def apply_enhanced_scrolling(widget):
    """Apply enhanced scrolling to an existing widget"""
    try:
        # Bind mouse wheel events
        widget.bind('<MouseWheel>', lambda e: _handle_mousewheel(e, widget))
        widget.bind('<Button-4>', lambda e: _handle_mousewheel(e, widget))  # Linux scroll up
        widget.bind('<Button-5>', lambda e: _handle_mousewheel(e, widget))  # Linux scroll down
    except Exception as e:
        print(f"Error applying enhanced scrolling: {e}")


def _handle_mousewheel(event, widget):
    """Handle mouse wheel scrolling for any widget"""
    try:
        # Determine scroll direction and amount
        if platform.system() == "Windows":
            delta = int(event.delta / 120)
        elif event.num == 4:  # Linux scroll up
            delta = -1
        elif event.num == 5:  # Linux scroll down
            delta = 1
        else:
            delta = 0
        
        # Scroll the widget
        if hasattr(widget, 'yview_scroll'):
            widget.yview_scroll(delta, "units")
        
        # Prevent event propagation
        return "break"
    except Exception as e:
        print(f"Error in mousewheel handler: {e}")


def setup_enhanced_selection(widget, callback=None):
    """Setup enhanced selection for any widget"""
    try:
        if isinstance(widget, ttk.Treeview):
            # For treeviews, bind single-click selection
            widget.bind('<Button-1>', lambda e: _handle_single_click(e, widget, callback))
        elif isinstance(widget, tk.Listbox):
            # For listboxes, bind single-click selection
            widget.bind('<Button-1>', lambda e: _handle_single_click(e, widget, callback))
    except Exception as e:
        print(f"Error setting up enhanced selection: {e}")


def _handle_single_click(event, widget, callback=None):
    """Handle single-click selection for any widget"""
    try:
        if isinstance(widget, ttk.Treeview):
            # Get the item under the cursor
            item = widget.identify_row(event.y)
            if item:
                # Clear previous selection
                widget.selection_remove(widget.selection())
                # Select the clicked item
                widget.selection_add(item)
                # Ensure the item is visible
                widget.see(item)
                # Focus on the widget
                widget.focus_set()
                # Trigger selection event
                widget.event_generate('<<TreeviewSelect>>')
                # Call callback if provided
                if callback:
                    callback(event)
        
        elif isinstance(widget, tk.Listbox):
            # Get the index under the cursor
            index = widget.nearest(event.y)
            if index >= 0:
                # Clear previous selection
                widget.selection_clear(0, tk.END)
                # Select the clicked item
                widget.selection_set(index)
                # Ensure the item is visible
                widget.see(index)
                # Focus on the widget
                widget.focus_set()
                # Trigger selection event
                widget.event_generate('<<ListboxSelect>>')
                # Call callback if provided
                if callback:
                    callback(event)
    except Exception as e:
        print(f"Error in single click handler: {e}") 
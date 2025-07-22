#!/usr/bin/env python3
"""
Test script to verify terminal auto-population fix
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import sys
import os

# Standalone TerminalEmulator class for testing
class TestTerminalEmulator(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Process tracking
        self.process = None
        self.start_time = None
        self.command_history = []
        self.history_index = 0
        
        # Enhanced output capture
        self.output_buffer = []
        self.max_buffer_size = 10000
        self.output_log_file = None
        self.logging_enabled = True
        
        # Search and filter functionality
        self.search_text = ""
        self.filter_pattern = ""
        self.show_only_errors = False
        self.show_only_warnings = False
        
        # Performance monitoring
        self.line_count = 0
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 0.5
        
        # Initial population tracking
        self.initial_population_complete = False
        
        # Create interface
        self.create_terminal_interface()
        self.create_toolbar()
        
    def create_terminal_interface(self):
        """Create the enhanced terminal interface"""
        # Create toolbar frame
        self.toolbar_frame = tk.Frame(self)
        self.toolbar_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Create terminal display
        self.terminal_frame = tk.Frame(self)
        self.terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create terminal
        self.terminal = scrolledtext.ScrolledText(
            self.terminal_frame, 
            font=("Consolas", 9), 
            bg='#1e1e1e',
            fg='#00ff00',
            insertbackground='#ffffff',
            selectbackground='#0078d4',
            selectforeground='#ffffff',
            wrap=tk.WORD,
            undo=True,
            maxundo=1000
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # Configure color tags
        self.terminal.tag_configure('error', foreground='#ff6b6b')
        self.terminal.tag_configure('warning', foreground='#ffd93d')
        self.terminal.tag_configure('success', foreground='#6bcf7f')
        self.terminal.tag_configure('info', foreground='#4dabf7')
        self.terminal.tag_configure('debug', foreground='#adb5bd')
        self.terminal.tag_configure('command', foreground='#ffa500')

    def create_toolbar(self):
        """Create toolbar with filter controls"""
        # Control buttons frame
        control_frame = tk.Frame(self.toolbar_frame)
        control_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Error/Warning toggles
        self.error_only_var = tk.BooleanVar(value=False)
        self.error_only_cb = tk.Checkbutton(control_frame, text="Errors Only", variable=self.error_only_var, 
                                          command=self.toggle_error_filter, bg='black', fg='white', selectcolor='darkred')
        self.error_only_cb.pack(side=tk.LEFT, padx=2)
        
        self.warning_only_var = tk.BooleanVar(value=False)
        self.warning_only_cb = tk.Checkbutton(control_frame, text="Warnings Only", variable=self.warning_only_var,
                                            command=self.toggle_warning_filter, bg='black', fg='white', selectcolor='darkorange')
        self.warning_only_cb.pack(side=tk.LEFT, padx=2)
        
        # Performance info
        self.perf_label = tk.Label(control_frame, text="Lines: 0", fg='cyan', bg='black', font=("Consolas", 8))
        self.perf_label.pack(side=tk.LEFT, padx=5)

    def _should_display_line(self, line):
        """Check if line should be displayed based on filters"""
        # Allow initial population - only apply filters after initial population is complete
        if not self.initial_population_complete:
            return True
        
        # Error filter
        if self.show_only_errors and 'error' not in line.lower() and '[err]' not in line.lower():
            return False
        
        # Warning filter
        if self.show_only_warnings and 'warning' not in line.lower() and 'warn' not in line.lower():
            return False
        
        return True

    def _get_line_color(self, line):
        """Get color code for line based on content"""
        line_lower = line.lower()
        
        if 'error' in line_lower or '[err]' in line_lower:
            return '31'  # Red
        elif 'warning' in line_lower or 'warn' in line_lower:
            return '33'  # Yellow
        elif 'success' in line_lower or 'ok' in line_lower:
            return '32'  # Green
        elif 'info' in line_lower:
            return '36'  # Cyan
        else:
            return '37'  # White

    def _append(self, text, color_code):
        """Append text to terminal with color support"""
        try:
            self.terminal.config(state='normal')
            
            # Apply color tags
            tag_name = f"color_{color_code}"
            if not self.terminal.tag_exists(tag_name):
                color_map = {
                    '31': '#ff6b6b',  # Red
                    '32': '#6bcf7f',  # Green
                    '33': '#ffd93d',  # Yellow
                    '36': '#4dabf7',  # Cyan
                    '37': '#ffffff'   # White
                }
                self.terminal.tag_configure(tag_name, foreground=color_map.get(color_code, '#ffffff'))
            
            # Insert text with color
            start_pos = self.terminal.index(tk.END)
            self.terminal.insert(tk.END, text)
            end_pos = self.terminal.index(tk.END)
            self.terminal.tag_add(tag_name, start_pos, end_pos)
            
            self.terminal.see(tk.END)
            self.terminal.config(state='disabled')
            
        except Exception as e:
            pass

    def _refresh_display(self):
        """Refresh terminal display with current filters"""
        try:
            self.terminal.config(state='normal')
            self.terminal.delete('1.0', tk.END)
            
            # If initial population is not complete, show all lines
            if not self.initial_population_complete:
                for entry in self.output_buffer:
                    self.terminal.insert(tk.END, entry['line'])
            else:
                # Apply filters after initial population
                for entry in self.output_buffer:
                    if self._should_display_line(entry['line']):
                        self.terminal.insert(tk.END, entry['line'])
            
            self.terminal.see(tk.END)
            self.terminal.config(state='disabled')
            
        except Exception as e:
            pass

    def toggle_error_filter(self):
        """Toggle error-only filter"""
        self.show_only_errors = self.error_only_var.get()
        if self.show_only_errors:
            self.warning_only_var.set(False)
            self.show_only_warnings = False
        self._refresh_display()

    def toggle_warning_filter(self):
        """Toggle warning-only filter"""
        self.show_only_warnings = self.warning_only_var.get()
        if self.show_only_warnings:
            self.error_only_var.set(False)
            self.show_only_errors = False
        self._refresh_display()

    def reset_initial_population(self):
        """Reset initial population state to allow all lines to show again"""
        self.initial_population_complete = False
        self._refresh_display()

    def update_performance_info(self):
        """Update performance information"""
        try:
            self.perf_label.config(text=f"Lines: {self.line_count} | Buffer: {len(self.output_buffer)}")
        except Exception as e:
            pass

def test_terminal_auto_population():
    """Test that terminal auto-populates correctly with filters"""
    
    # Create test window
    root = tk.Tk()
    root.title("Terminal Auto-Population Test")
    root.geometry("800x600")
    
    # Create terminal
    terminal = TestTerminalEmulator(root)
    terminal.pack(fill=tk.BOTH, expand=True)
    
    # Test function to simulate process output
    def simulate_output():
        """Simulate process output with various message types"""
        messages = [
            "Starting application...",
            "Loading configuration...",
            "Warning: Deprecated feature used",
            "Connecting to database...",
            "Error: Failed to connect to database",
            "Retrying connection...",
            "Success: Connected to database",
            "Loading models...",
            "Warning: Model version mismatch",
            "Processing data...",
            "Info: Processing complete",
            "Ready for requests"
        ]
        
        for i, msg in enumerate(messages):
            # Simulate the line processing
            processed_line = f"[{time.strftime('%H:%M:%S')}] {msg}\n"
            
            # Add to buffer
            terminal.output_buffer.append({
                'timestamp': time.time(),
                'line': processed_line,
                'stream': 'stdout',
                'original': msg
            })
            
            # Apply filters and display
            if terminal._should_display_line(processed_line):
                terminal.after(0, terminal._append, processed_line, terminal._get_line_color(processed_line))
            
            # Update line count
            terminal.line_count += 1
            
            # Mark initial population as complete after first line
            if terminal.line_count == 1:
                terminal.initial_population_complete = True
            
            # Update performance info
            terminal.after(0, terminal.update_performance_info)
            
            time.sleep(0.5)  # Simulate real-time output
    
    # Start simulation in background
    threading.Thread(target=simulate_output, daemon=True).start()
    
    # Add test controls
    control_frame = tk.Frame(root)
    control_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def test_warning_filter():
        """Test warning filter toggle"""
        terminal.warning_only_var.set(True)
        terminal.toggle_warning_filter()
        print("Warning filter enabled - should only show warning lines")
    
    def test_error_filter():
        """Test error filter toggle"""
        terminal.error_only_var.set(True)
        terminal.toggle_error_filter()
        print("Error filter enabled - should only show error lines")
    
    def test_reset_filters():
        """Reset all filters"""
        terminal.warning_only_var.set(False)
        terminal.error_only_var.set(False)
        terminal.show_only_errors = False
        terminal.show_only_warnings = False
        terminal._refresh_display()
        print("Filters reset - should show all lines")
    
    def test_reset_population():
        """Reset initial population state"""
        terminal.reset_initial_population()
        print("Initial population reset - should show all lines again")
    
    tk.Button(control_frame, text="Enable Warning Filter", command=test_warning_filter).pack(side=tk.LEFT, padx=2)
    tk.Button(control_frame, text="Enable Error Filter", command=test_error_filter).pack(side=tk.LEFT, padx=2)
    tk.Button(control_frame, text="Reset Filters", command=test_reset_filters).pack(side=tk.LEFT, padx=2)
    tk.Button(control_frame, text="Reset Population", command=test_reset_population).pack(side=tk.LEFT, padx=2)
    
    # Instructions
    instructions = tk.Label(root, text="Watch the terminal auto-populate with all lines initially, then test filters", 
                          fg="blue", font=("Arial", 10))
    instructions.pack(pady=5)
    
    print("Test started!")
    print("1. Terminal should auto-populate with ALL lines initially")
    print("2. After first line, filters should work normally")
    print("3. Use buttons to test different filter states")
    
    root.mainloop()

if __name__ == "__main__":
    test_terminal_auto_population() 
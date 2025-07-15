"""
Terminal Emulator Module
Provides a terminal-like interface for process output
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import time
import re
import os
from typing import Optional, Dict, Any, List
from datetime import datetime


class TerminalEmulator(tk.Frame):
    """Advanced terminal emulator with search, filtering, and logging capabilities"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Process tracking
        self.process = None
        self.command = None
        self.start_time = None
        
        # Output management
        self.output_buffer = []
        self.line_count = 0
        self.max_buffer_size = 10000
        
        # Search and filtering
        self.search_text = ""
        self.filter_pattern = ""
        self.show_only_errors = False
        self.show_only_warnings = False
        
        # Command history
        self.command_history = []
        self.history_index = 0
        
        # Logging
        self.logging_enabled = True
        self.output_log_file = None
        
        # Performance monitoring
        self.performance_thread = None
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        
        # Create interface
        self.create_terminal_interface()
        self.create_toolbar()
        self.create_input_controls()
        self.create_context_menu()
        self.bind_terminal_events()
        self.init_logging()
        self.start_performance_monitor()

    def create_terminal_interface(self):
        """Create the main terminal display"""
        try:
            # Terminal output area
            self.terminal = scrolledtext.ScrolledText(
                self,
                wrap=tk.WORD,
                state='disabled',
                font=('Consolas', 10),
                bg='#1e1e1e',
                fg='#ffffff',
                insertbackground='#ffffff',
                selectbackground='#0078d4',
                selectforeground='#ffffff'
            )
            self.terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Configure tags for colored output
            self.terminal.tag_configure('error', foreground='#ff6b6b')
            self.terminal.tag_configure('warning', foreground='#ffd93d')
            self.terminal.tag_configure('success', foreground='#6bcf7f')
            self.terminal.tag_configure('info', foreground='#4dabf7')
            self.terminal.tag_configure('debug', foreground='#adb5bd')
        except Exception as e:
            print(f"Error creating terminal interface: {e}")

    def create_toolbar(self):
        """Create toolbar with controls"""
        try:
            toolbar = tk.Frame(self)
            toolbar.pack(fill=tk.X, padx=5, pady=2)
            
            # Search frame
            search_frame = tk.LabelFrame(toolbar, text="Search", padx=5, pady=2)
            search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.search_var = tk.StringVar()
            self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=20)
            self.search_entry.pack(side=tk.LEFT, padx=2)
            
            tk.Button(search_frame, text="Find Next", command=self.find_next).pack(side=tk.LEFT, padx=2)
            tk.Button(search_frame, text="Find Prev", command=self.find_previous).pack(side=tk.LEFT, padx=2)
            
            # Filter frame
            filter_frame = tk.LabelFrame(toolbar, text="Filter", padx=5, pady=2)
            filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
            
            self.filter_var = tk.StringVar()
            self.filter_entry = tk.Entry(filter_frame, textvariable=self.filter_var, width=15)
            self.filter_entry.pack(side=tk.LEFT, padx=2)
            
            self.error_filter_var = tk.BooleanVar()
            tk.Checkbutton(filter_frame, text="Errors", variable=self.error_filter_var, 
                          command=self.toggle_error_filter).pack(side=tk.LEFT, padx=2)
            
            self.warning_filter_var = tk.BooleanVar()
            tk.Checkbutton(filter_frame, text="Warnings", variable=self.warning_filter_var, 
                          command=self.toggle_warning_filter).pack(side=tk.LEFT, padx=2)
            
            # Control frame
            control_frame = tk.LabelFrame(toolbar, text="Controls", padx=5, pady=2)
            control_frame.pack(side=tk.RIGHT, padx=(10, 0))
            
            tk.Button(control_frame, text="Clear", command=self.clear_terminal).pack(side=tk.LEFT, padx=2)
            tk.Button(control_frame, text="Copy All", command=self.copy_all).pack(side=tk.LEFT, padx=2)
            tk.Button(control_frame, text="Save", command=self.save_output).pack(side=tk.LEFT, padx=2)
            tk.Button(control_frame, text="Stats", command=self.show_statistics).pack(side=tk.LEFT, padx=2)
            
            # Performance info
            self.performance_label = tk.Label(control_frame, text="CPU: 0% | RAM: 0MB")
            self.performance_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error creating toolbar: {e}")

    def create_input_controls(self):
        """Create input controls for sending commands"""
        try:
            input_frame = tk.Frame(self)
            input_frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(input_frame, text="Command:").pack(side=tk.LEFT)
            
            self.input_var = tk.StringVar()
            self.input_entry = tk.Entry(input_frame, textvariable=self.input_var, width=50)
            self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            tk.Button(input_frame, text="Send", command=self.send_input).pack(side=tk.LEFT, padx=2)
            tk.Button(input_frame, text="Kill Process", command=self.kill_process).pack(side=tk.LEFT, padx=2)
        except Exception as e:
            print(f"Error creating input controls: {e}")

    def create_context_menu(self):
        """Create right-click context menu"""
        try:
            self.context_menu = tk.Menu(self, tearoff=0)
            self.context_menu.add_command(label="Copy Selection", command=self.copy_selection)
            self.context_menu.add_command(label="Copy All", command=self.copy_all)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Clear Terminal", command=self.clear_terminal)
            self.context_menu.add_command(label="Save Output", command=self.save_output)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Show Statistics", command=self.show_statistics)
        except Exception as e:
            print(f"Error creating context menu: {e}")

    def bind_terminal_events(self):
        """Bind keyboard and mouse events"""
        try:
            self.terminal.bind("<Button-3>", self.show_context_menu)
            self.input_entry.bind("<Return>", self.send_input)
            self.input_entry.bind("<Up>", self.history_up)
            self.input_entry.bind("<Down>", self.history_down)
            self.search_entry.bind("<KeyRelease>", self.on_search_change)
            self.filter_entry.bind("<KeyRelease>", self.on_filter_change)
            
            # Bind Ctrl+F to focus search
            self.terminal.bind("<Control-f>", self.focus_search)
            self.terminal.bind("<Control-g>", self.find_next)
            self.terminal.bind("<Control-Shift-g>", self.find_previous)
        except Exception as e:
            print(f"Error binding terminal events: {e}")

    def init_logging(self):
        """Initialize logging to file"""
        try:
            if self.logging_enabled:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
                os.makedirs(log_dir, exist_ok=True)
                self.output_log_file = os.path.join(log_dir, f"terminal_{timestamp}.log")
        except Exception as e:
            print(f"Error initializing logging: {e}")

    def start_performance_monitor(self):
        """Start performance monitoring thread"""
        try:
            def monitor():
                while True:
                    if self.process and self.process.poll() is None:
                        try:
                            import psutil
                            proc = psutil.Process(self.process.pid)
                            self.cpu_usage = proc.cpu_percent()
                            self.memory_usage = proc.memory_info().rss / 1024 / 1024  # MB
                            self.update_performance_info()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    time.sleep(2)
            
            self.performance_thread = threading.Thread(target=monitor, daemon=True)
            self.performance_thread.start()
        except Exception as e:
            print(f"Error starting performance monitor: {e}")

    def update_performance_info(self):
        """Update performance display"""
        try:
            self.performance_label.config(text=f"CPU: {self.cpu_usage:.1f}% | RAM: {self.memory_usage:.1f}MB")
        except Exception as e:
            print(f"Error updating performance info: {e}")

    def attach_process(self, process, command):
        """Attach a process to the terminal"""
        try:
            self.process = process
            self.command = command
            self.start_time = time.time()
            
            # Start reading output
            self._read_output_enhanced()
        except Exception as e:
            print(f"Error attaching process: {e}")

    def _read_output_enhanced(self):
        """Enhanced output reading with error handling"""
        try:
            if self.process and self.process.poll() is None:
                # Read stdout
                if self.process.stdout:
                    threading.Thread(target=self._read_stream, 
                                   args=(self.process.stdout, 'stdout'), 
                                   daemon=True).start()
                
                # Read stderr
                if self.process.stderr:
                    threading.Thread(target=self._read_stream, 
                                   args=(self.process.stderr, 'stderr'), 
                                   daemon=True).start()
        except Exception as e:
            print(f"Error reading output: {e}")

    def _read_stream(self, stream, stream_type):
        """Read from a stream"""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    self._process_output_line(line.strip(), stream_type)
        except Exception as e:
            print(f"Error reading stream {stream_type}: {e}")

    def _process_output_line(self, line, stream_type):
        """Process a line of output"""
        try:
            # Add to buffer
            self.output_buffer.append({
                'line': line,
                'timestamp': time.time(),
                'stream': stream_type
            })
            
            # Keep buffer size manageable
            if len(self.output_buffer) > self.max_buffer_size:
                self.output_buffer.pop(0)
            
            # Check if we should display this line
            if self._should_display_line(line):
                # Determine color
                color_tag = self._get_line_color(line)
                
                # Add to terminal
                self._append(line + '\n', color_tag)
                
                # Log to file
                self._log_line(line, stream_type)
        except Exception as e:
            print(f"Error processing output line: {e}")

    def _should_display_line(self, line):
        """Check if line should be displayed based on filters"""
        try:
            # Check search filter
            if self.search_text and self.search_text.lower() not in line.lower():
                return False
            
            # Check pattern filter
            if self.filter_pattern and not re.search(self.filter_pattern, line, re.IGNORECASE):
                return False
            
            # Check error filter
            if self.show_only_errors and not any(error_word in line.lower() for error_word in ['error', 'exception', 'failed', 'failure']):
                return False
            
            # Check warning filter
            if self.show_only_warnings and not any(warning_word in line.lower() for warning_word in ['warning', 'warn', 'deprecated']):
                return False
            
            return True
        except Exception as e:
            print(f"Error checking line display: {e}")
            return True

    def _get_line_color(self, line):
        """Get color tag for a line"""
        try:
            line_lower = line.lower()
            
            if any(error_word in line_lower for error_word in ['error', 'exception', 'failed', 'failure']):
                return 'error'
            elif any(warning_word in line_lower for warning_word in ['warning', 'warn', 'deprecated']):
                return 'warning'
            elif any(success_word in line_lower for success_word in ['success', 'completed', 'done', 'ready']):
                return 'success'
            elif any(info_word in line_lower for info_word in ['info', 'information', 'note']):
                return 'info'
            else:
                return 'debug'
        except Exception as e:
            print(f"Error getting line color: {e}")
            return 'debug'

    def _log_line(self, line, stream_type):
        """Log line to file"""
        try:
            if self.logging_enabled and self.output_log_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.output_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] [{stream_type.upper()}] {line}\n")
        except Exception as e:
            print(f"Error logging line: {e}")

    def _smart_cleanup(self):
        """Smart cleanup of terminal display"""
        try:
            # Remove old lines if terminal is getting too large
            current_lines = int(self.terminal.index('end-1c').split('.')[0])
            if current_lines > 1000:
                self._cleanup_display()
        except Exception as e:
            print(f"Error in smart cleanup: {e}")

    def _cleanup_display(self):
        """Clean up terminal display"""
        try:
            # Keep only last 500 lines
            lines = self.terminal.get('1.0', 'end-1c').split('\n')
            if len(lines) > 500:
                self.terminal.config(state='normal')
                self.terminal.delete('1.0', 'end')
                self.terminal.insert('1.0', '\n'.join(lines[-500:]) + '\n')
                self.terminal.config(state='disabled')
                self.terminal.see('end')
        except Exception as e:
            print(f"Error cleaning up display: {e}")

    def on_search_change(self, event=None):
        """Handle search text change"""
        try:
            self.search_text = self.search_var.get()
            self._refresh_display()
        except Exception as e:
            print(f"Error handling search change: {e}")

    def on_filter_change(self, event=None):
        """Handle filter text change"""
        try:
            self.filter_pattern = self.filter_var.get()
            self._refresh_display()
        except Exception as e:
            print(f"Error handling filter change: {e}")

    def toggle_error_filter(self):
        """Toggle error-only filter"""
        try:
            self.show_only_errors = self.error_filter_var.get()
            self._refresh_display()
        except Exception as e:
            print(f"Error toggling error filter: {e}")

    def toggle_warning_filter(self):
        """Toggle warning-only filter"""
        try:
            self.show_only_warnings = self.warning_filter_var.get()
            self._refresh_display()
        except Exception as e:
            print(f"Error toggling warning filter: {e}")

    def toggle_logging(self):
        """Toggle logging on/off"""
        try:
            self.logging_enabled = not self.logging_enabled
        except Exception as e:
            print(f"Error toggling logging: {e}")

    def _refresh_display(self):
        """Refresh the terminal display with current filters"""
        try:
            self.terminal.config(state='normal')
            self.terminal.delete('1.0', 'end')
            
            for entry in self.output_buffer:
                if self._should_display_line(entry['line']):
                    color_tag = self._get_line_color(entry['line'])
                    self.terminal.insert('end', entry['line'] + '\n', color_tag)
            
            self.terminal.config(state='disabled')
            self.terminal.see('end')
        except Exception as e:
            print(f"Error refreshing display: {e}")

    def focus_search(self, event=None):
        """Focus the search entry"""
        try:
            self.search_entry.focus_set()
        except Exception as e:
            print(f"Error focusing search: {e}")

    def find_next(self, event=None):
        """Find next occurrence of search text"""
        try:
            search_text = self.search_var.get()
            if not search_text:
                return
            
            # Remove existing highlights
            self.terminal.tag_remove('search_highlight', '1.0', 'end')
            
            # Find next occurrence
            start_pos = self.terminal.index('insert')
            pos = self.terminal.search(search_text, start_pos, 'end', nocase=True)
            
            if not pos:
                # Wrap around to beginning
                pos = self.terminal.search(search_text, '1.0', 'end', nocase=True)
            
            if pos:
                end_pos = f"{pos}+{len(search_text)}c"
                self.terminal.tag_add('search_highlight', pos, end_pos)
                self.terminal.tag_config('search_highlight', background='yellow', foreground='black')
                self.terminal.see(pos)
                self.terminal.mark_set('insert', pos)
        except Exception as e:
            print(f"Error finding next: {e}")

    def find_previous(self, event=None):
        """Find previous occurrence of search text"""
        try:
            search_text = self.search_var.get()
            if not search_text:
                return
            
            # Remove existing highlights
            self.terminal.tag_remove('search_highlight', '1.0', 'end')
            
            # Find previous occurrence
            start_pos = self.terminal.index('insert')
            pos = self.terminal.search(search_text, '1.0', start_pos, backwards=True, nocase=True)
            
            if not pos:
                # Wrap around to end
                pos = self.terminal.search(search_text, '1.0', 'end', backwards=True, nocase=True)
            
            if pos:
                end_pos = f"{pos}+{len(search_text)}c"
                self.terminal.tag_add('search_highlight', pos, end_pos)
                self.terminal.tag_config('search_highlight', background='yellow', foreground='black')
                self.terminal.see(pos)
                self.terminal.mark_set('insert', pos)
        except Exception as e:
            print(f"Error finding previous: {e}")

    def auto_complete(self, event=None):
        """Auto-complete command"""
        try:
            # Basic auto-complete implementation
            pass
        except Exception as e:
            print(f"Error in auto complete: {e}")

    def copy_selection(self, event=None):
        """Copy selected text"""
        try:
            try:
                selected_text = self.terminal.get('sel.first', 'sel.last')
                self.clipboard_clear()
                self.clipboard_append(selected_text)
            except tk.TclError:
                # No selection
                pass
        except Exception as e:
            print(f"Error copying selection: {e}")

    def copy_all(self):
        """Copy all terminal content"""
        try:
            all_text = self.terminal.get('1.0', 'end-1c')
            self.clipboard_clear()
            self.clipboard_append(all_text)
        except Exception as e:
            print(f"Error copying all: {e}")

    def save_output(self):
        """Save terminal output to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                all_text = self.terminal.get('1.0', 'end-1c')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(all_text)
        except Exception as e:
            print(f"Error saving output: {e}")

    def show_statistics(self):
        """Show terminal statistics"""
        try:
            stats = {
                'Total Lines': len(self.output_buffer),
                'Error Lines': len([e for e in self.output_buffer if 'error' in e['line'].lower()]),
                'Warning Lines': len([e for e in self.output_buffer if 'warning' in e['line'].lower()]),
                'Uptime': self.get_uptime(),
                'Process Status': 'Running' if self.process and self.process.poll() is None else 'Stopped'
            }
            
            stats_text = '\n'.join([f"{k}: {v}" for k, v in stats.items()])
            messagebox.showinfo("Terminal Statistics", stats_text)
        except Exception as e:
            print(f"Error showing statistics: {e}")

    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def _append(self, text, color_code):
        """Append text to terminal with color"""
        try:
            self.terminal.config(state='normal')
            self.terminal.insert('end', text, color_code)
            self.terminal.config(state='disabled')
            self.terminal.see('end')
            
            # Smart cleanup
            self._smart_cleanup()
        except Exception as e:
            print(f"Error appending text: {e}")

    def _get_color_name(self, color_code):
        """Get color name from ANSI color code"""
        try:
            color_map = {
                '30': 'black', '31': 'red', '32': 'green', '33': 'yellow',
                '34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white',
                '90': 'gray', '91': 'bright_red', '92': 'bright_green',
                '93': 'bright_yellow', '94': 'bright_blue', '95': 'bright_magenta',
                '96': 'bright_cyan', '97': 'bright_white'
            }
            return color_map.get(color_code, 'white')
        except Exception as e:
            print(f"Error getting color name: {e}")
            return 'white'

    def _parse_ansi_colors(self, text):
        """Parse ANSI color codes in text"""
        try:
            # Basic ANSI color parsing
            return text
        except Exception as e:
            print(f"Error parsing ANSI colors: {e}")
            return text

    def send_input(self, event=None):
        """Send input to process"""
        try:
            command = self.input_var.get().strip()
            if command and self.process and self.process.poll() is None:
                # Add to history
                if command not in self.command_history:
                    self.command_history.append(command)
                    if len(self.command_history) > 100:
                        self.command_history.pop(0)
                
                # Send to process
                try:
                    self.process.stdin.write(command + '\n')
                    self.process.stdin.flush()
                except (IOError, OSError):
                    pass
                
                # Clear input
                self.input_var.set('')
                self.history_index = 0
        except Exception as e:
            print(f"Error sending input: {e}")

    def history_up(self, event):
        """Navigate up in command history"""
        try:
            if self.command_history and self.history_index < len(self.command_history):
                self.history_index += 1
                self.input_var.set(self.command_history[-self.history_index])
        except Exception as e:
            print(f"Error navigating history up: {e}")

    def history_down(self, event):
        """Navigate down in command history"""
        try:
            if self.history_index > 0:
                self.history_index -= 1
                if self.history_index == 0:
                    self.input_var.set('')
                else:
                    self.input_var.set(self.command_history[-self.history_index])
        except Exception as e:
            print(f"Error navigating history down: {e}")

    def on_key_press(self, event):
        """Handle key press events"""
        try:
            # Handle special keys
            pass
        except Exception as e:
            print(f"Error handling key press: {e}")

    def clear_terminal(self):
        """Clear terminal display"""
        try:
            self.terminal.config(state='normal')
            self.terminal.delete('1.0', 'end')
            self.terminal.config(state='disabled')
        except Exception as e:
            print(f"Error clearing terminal: {e}")

    def kill_process(self):
        """Kill the attached process"""
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
        except Exception as e:
            print(f"Error killing process: {e}")

    def get_uptime(self):
        """Get process uptime"""
        try:
            if self.start_time:
                uptime = time.time() - self.start_time
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                seconds = int(uptime % 60)
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return "00:00:00"
        except Exception as e:
            print(f"Error getting uptime: {e}")
            return "00:00:00"

    def get_status(self):
        """Get terminal status"""
        try:
            return {
                'process_running': self.process and self.process.poll() is None,
                'uptime': self.get_uptime(),
                'line_count': len(self.output_buffer),
                'cpu_usage': self.cpu_usage,
                'memory_usage': self.memory_usage
            }
        except Exception as e:
            print(f"Error getting status: {e}")
            return {}

    def get_output_buffer(self):
        """Get output buffer"""
        try:
            return self.output_buffer.copy()
        except Exception as e:
            print(f"Error getting output buffer: {e}")
            return []

    def get_filtered_output(self, filter_func=None):
        """Get filtered output"""
        try:
            if filter_func:
                return [entry for entry in self.output_buffer if filter_func(entry)]
            return self.output_buffer.copy()
        except Exception as e:
            print(f"Error getting filtered output: {e}")
            return []

    def export_output(self, filename=None, format='txt'):
        """Export output to file"""
        try:
            if not filename:
                filename = f"terminal_output_{time.strftime('%Y%m%d_%H%M%S')}.{format}"
            
            if format == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    for entry in self.output_buffer:
                        timestamp = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"[{timestamp}] [{entry['stream'].upper()}] {entry['line']}\n")
            
            return filename
        except Exception as e:
            print(f"Error exporting output: {e}")
            return None 
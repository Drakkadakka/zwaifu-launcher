"""
Enhanced Error Handling System
Provides detailed error reporting with stack traces, error dialogs, log links, and copy-to-clipboard functionality.
"""

import os
import sys
import traceback
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import psutil
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
import webbrowser
import subprocess
import platform


class ErrorHandler:
    """Enhanced error handling system with detailed reporting and user interface"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.error_log_file = os.path.join("data", "error_log.txt")
        self.crash_log_file = os.path.join("data", "crash_log.txt")
        self.error_count = 0
        self.last_error_time = 0
        self.error_callbacks = []
        
        # Ensure log directories exist
        os.makedirs(os.path.dirname(self.error_log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.crash_log_file), exist_ok=True)
        
        # Load error reporting settings
        self.error_settings = self._load_error_settings()
        
    def _load_error_settings(self) -> Dict[str, Any]:
        """Load error reporting configuration"""
        default_settings = {
            "error_reporting_verbosity": "detailed",  # basic, detailed, verbose
            "show_error_dialogs": True,
            "log_errors_to_file": True,
            "include_system_info": True,
            "include_stack_traces": True,
            "max_error_dialog_size": 800,
            "error_dialog_timeout": 30,  # seconds
            "suppress_repeated_errors": True,
            "repeated_error_threshold": 5,  # max repeated errors before suppression
            "repeated_error_window": 300,  # seconds
            "auto_copy_to_clipboard": False,
            "show_log_file_links": True,
            "error_notification_sound": True
        }
        
        if self.config_manager:
            try:
                config = self.config_manager.load_config()
                return config.get("error_reporting", default_settings)
            except Exception:
                pass
        
        return default_settings
    
    def handle_error(self, error: Exception, context: str = "", show_dialog: bool = None) -> Dict[str, Any]:
        """
        Handle an error with detailed reporting and optional user interface
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            show_dialog: Override settings for showing error dialog
            
        Returns:
            Dict containing error information and handling results
        """
        try:
            # Check if we should suppress repeated errors
            if self._should_suppress_error(error, context):
                return {"suppressed": True, "reason": "repeated_error"}
            
            # Collect error information
            error_info = self._collect_error_info(error, context)
            
            # Log the error
            if self.error_settings.get("log_errors_to_file", True):
                self._log_error(error_info)
            
            # Show error dialog if enabled
            if show_dialog is None:
                show_dialog = self.error_settings.get("show_error_dialogs", True)
            
            if show_dialog:
                self._show_error_dialog(error_info)
            
            # Copy to clipboard if enabled
            if self.error_settings.get("auto_copy_to_clipboard", False):
                self._copy_error_to_clipboard(error_info)
            
            # Trigger error callbacks
            self._trigger_error_callbacks(error_info)
            
            return {
                "success": True,
                "error_info": error_info,
                "logged": self.error_settings.get("log_errors_to_file", True),
                "dialog_shown": show_dialog
            }
            
        except Exception as e:
            # Fallback error handling
            print(f"Error in error handler: {e}")
            return {"success": False, "fallback_error": str(e)}
    
    def _should_suppress_error(self, error: Exception, context: str) -> bool:
        """Check if this error should be suppressed due to repetition"""
        if not self.error_settings.get("suppress_repeated_errors", True):
            return False
        
        current_time = time.time()
        error_key = f"{type(error).__name__}:{str(error)[:100]}:{context}"
        
        # Simple repetition detection (in production, use a more sophisticated approach)
        if current_time - self.last_error_time < self.error_settings.get("repeated_error_window", 300):
            self.error_count += 1
        else:
            self.error_count = 1
        
        self.last_error_time = current_time
        
        return self.error_count > self.error_settings.get("repeated_error_threshold", 5)
    
    def _collect_error_info(self, error: Exception, context: str) -> Dict[str, Any]:
        """Collect comprehensive error information"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": None,
            "system_info": None,
            "process_info": None,
            "log_files": []
        }
        
        # Add stack trace if enabled
        if self.error_settings.get("include_stack_traces", True):
            error_info["traceback"] = traceback.format_exc()
        
        # Add system information if enabled
        if self.error_settings.get("include_system_info", True):
            error_info["system_info"] = self._get_system_info()
            error_info["process_info"] = self._get_process_info()
        
        # Add log file information
        error_info["log_files"] = self._get_log_files()
        
        return error_info
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "disk_usage": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {e}"}
    
    def _get_process_info(self) -> Dict[str, Any]:
        """Get current process information"""
        try:
            process = psutil.Process()
            return {
                "pid": process.pid,
                "name": process.name(),
                "memory_info": {
                    "rss": process.memory_info().rss,
                    "vms": process.memory_info().vms
                },
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "create_time": process.create_time()
            }
        except Exception as e:
            return {"error": f"Failed to get process info: {e}"}
    
    def _get_log_files(self) -> List[Dict[str, str]]:
        """Get available log files with their paths"""
        log_files = []
        log_dirs = ["data", "logs", "."]
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith(('.log', '.txt')) and 'log' in file.lower():
                        file_path = os.path.join(log_dir, file)
                        try:
                            stat = os.stat(file_path)
                            log_files.append({
                                "name": file,
                                "path": file_path,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
                        except Exception:
                            pass
        
        return log_files
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error information to file"""
        try:
            log_entry = {
                "timestamp": error_info["timestamp"],
                "error_type": error_info["error_type"],
                "error_message": error_info["error_message"],
                "context": error_info["context"]
            }
            
            if error_info.get("traceback"):
                log_entry["traceback"] = error_info["traceback"]
            
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, indent=2) + "\n" + "-" * 80 + "\n")
                
        except Exception as e:
            print(f"Failed to log error: {e}")
    
    def _show_error_dialog(self, error_info: Dict[str, Any]):
        """Show detailed error dialog to user"""
        try:
            # Create error dialog in a separate thread to avoid blocking
            threading.Thread(target=self._create_error_dialog, args=(error_info,), daemon=True).start()
        except Exception as e:
            print(f"Failed to show error dialog: {e}")
    
    def _create_error_dialog(self, error_info: Dict[str, Any]):
        """Create and show the error dialog"""
        try:
            # Create dialog window
            dialog = tk.Toplevel()
            dialog.title(f"Error: {error_info['error_type']}")
            dialog.geometry("800x600")
            dialog.resizable(True, True)
            
            # Center the dialog
            dialog.transient()
            dialog.grab_set()
            
            # Create main frame
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Error summary
            summary_frame = ttk.LabelFrame(main_frame, text="Error Summary", padding="5")
            summary_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(summary_frame, text=f"Type: {error_info['error_type']}", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            ttk.Label(summary_frame, text=f"Message: {error_info['error_message']}", wraplength=700).pack(anchor=tk.W)
            if error_info.get('context'):
                ttk.Label(summary_frame, text=f"Context: {error_info['context']}", wraplength=700).pack(anchor=tk.W)
            
            # Create notebook for different error details
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Stack trace tab
            if error_info.get("traceback"):
                traceback_frame = ttk.Frame(notebook)
                notebook.add(traceback_frame, text="Stack Trace")
                
                traceback_text = scrolledtext.ScrolledText(traceback_frame, wrap=tk.WORD, height=15)
                traceback_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                traceback_text.insert(tk.END, error_info["traceback"])
                traceback_text.config(state=tk.DISABLED)
            
            # System info tab
            if error_info.get("system_info"):
                system_frame = ttk.Frame(notebook)
                notebook.add(system_frame, text="System Info")
                
                system_text = scrolledtext.ScrolledText(system_frame, wrap=tk.WORD, height=15)
                system_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                system_text.insert(tk.END, json.dumps(error_info["system_info"], indent=2))
                system_text.config(state=tk.DISABLED)
            
            # Log files tab
            if error_info.get("log_files"):
                logs_frame = ttk.Frame(notebook)
                notebook.add(logs_frame, text="Log Files")
                
                logs_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, height=15)
                logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                for log_file in error_info["log_files"]:
                    logs_text.insert(tk.END, f"File: {log_file['name']}\n")
                    logs_text.insert(tk.END, f"Path: {log_file['path']}\n")
                    logs_text.insert(tk.END, f"Size: {log_file['size']} bytes\n")
                    logs_text.insert(tk.END, f"Modified: {log_file['modified']}\n")
                    logs_text.insert(tk.END, "-" * 50 + "\n")
                
                logs_text.config(state=tk.DISABLED)
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Copy to clipboard button
            def copy_error():
                try:
                    error_text = f"Error: {error_info['error_type']}\n"
                    error_text += f"Message: {error_info['error_message']}\n"
                    error_text += f"Context: {error_info.get('context', 'N/A')}\n"
                    if error_info.get('traceback'):
                        error_text += f"\nStack Trace:\n{error_info['traceback']}"
                    
                    dialog.clipboard_clear()
                    dialog.clipboard_append(error_text)
                    messagebox.showinfo("Copied", "Error details copied to clipboard!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")
            
            ttk.Button(button_frame, text="Copy to Clipboard", command=copy_error).pack(side=tk.LEFT, padx=(0, 5))
            
            # Open log file button
            def open_log_file():
                try:
                    if os.path.exists(self.error_log_file):
                        if platform.system() == "Windows":
                            os.startfile(self.error_log_file)
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.run(["open", self.error_log_file])
                        else:  # Linux
                            subprocess.run(["xdg-open", self.error_log_file])
                    else:
                        messagebox.showwarning("Warning", "Log file not found!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open log file: {e}")
            
            ttk.Button(button_frame, text="Open Log File", command=open_log_file).pack(side=tk.LEFT, padx=(0, 5))
            
            # Close button
            ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)
            
            # Auto-close after timeout
            if self.error_settings.get("error_dialog_timeout", 30) > 0:
                dialog.after(self.error_settings["error_dialog_timeout"] * 1000, dialog.destroy)
            
            # Focus the dialog
            dialog.focus_set()
            dialog.wait_window()
            
        except Exception as e:
            print(f"Failed to create error dialog: {e}")
            # Fallback to simple message box
            messagebox.showerror("Error", f"An error occurred: {error_info['error_message']}")
    
    def _copy_error_to_clipboard(self, error_info: Dict[str, Any]):
        """Copy error information to clipboard"""
        try:
            error_text = f"Error: {error_info['error_type']}\n"
            error_text += f"Message: {error_info['error_message']}\n"
            error_text += f"Context: {error_info.get('context', 'N/A')}\n"
            if error_info.get('traceback'):
                error_text += f"\nStack Trace:\n{error_info['traceback']}"
            
            # Use tkinter clipboard
            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.clipboard_clear()
            root.clipboard_append(error_text)
            root.destroy()
            
        except Exception as e:
            print(f"Failed to copy error to clipboard: {e}")
    
    def _trigger_error_callbacks(self, error_info: Dict[str, Any]):
        """Trigger registered error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                print(f"Error in error callback: {e}")
    
    def register_error_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback function to be called when errors occur"""
        self.error_callbacks.append(callback)
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update error handling settings"""
        self.error_settings.update(new_settings)
        
        # Save to config if config manager is available
        if self.config_manager:
            try:
                config = self.config_manager.load_config()
                config["error_reporting"] = self.error_settings
                self.config_manager.save_config(config)
            except Exception as e:
                print(f"Failed to save error settings: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of recent errors"""
        try:
            if not os.path.exists(self.error_log_file):
                return {"total_errors": 0, "recent_errors": []}
            
            with open(self.error_log_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple parsing of error log
            error_entries = content.split("-" * 80)
            recent_errors = []
            
            for entry in error_entries[-10:]:  # Last 10 errors
                if entry.strip():
                    try:
                        error_data = json.loads(entry.strip())
                        recent_errors.append({
                            "timestamp": error_data.get("timestamp"),
                            "error_type": error_data.get("error_type"),
                            "error_message": error_data.get("error_message", "")[:100] + "..."
                        })
                    except Exception:
                        pass
            
            return {
                "total_errors": len(error_entries) - 1,
                "recent_errors": recent_errors
            }
            
        except Exception as e:
            return {"error": f"Failed to get error summary: {e}"}


# Global error handler instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def setup_error_handler(config_manager=None) -> ErrorHandler:
    """Setup and return the global error handler"""
    global _error_handler
    _error_handler = ErrorHandler(config_manager)
    return _error_handler

def handle_error(error: Exception, context: str = "", show_dialog: bool = None) -> Dict[str, Any]:
    """Global error handling function"""
    return get_error_handler().handle_error(error, context, show_dialog) 
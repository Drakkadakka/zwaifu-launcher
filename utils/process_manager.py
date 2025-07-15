"""
Process Manager Module
Handles process creation, monitoring, and management
"""

import subprocess
import threading
import tkinter as tk
import time
import socket
import psutil
from typing import Optional, Dict, Any


class Process:
    """Manages a single process instance with output capture"""
    
    def __init__(self, name: str, command: list, cwd: str, output_widget: tk.Text):
        self.name = name
        self.command = command
        self.cwd = cwd
        self.output_widget = output_widget
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.start_time = None
        self.pid = None

    def start(self):
        """Start the process in a separate thread"""
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def _run(self):
        """Internal method to run the process and capture output"""
        try:
            self.process = subprocess.Popen(
                self.command, 
                cwd=self.cwd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.start_time = time.time()
            self.pid = self.process.pid
            
            # Read output line by line
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_widget.insert(tk.END, line)
                    self.output_widget.see(tk.END)
                    self.output_widget.update_idletasks()
                    
        except Exception as e:
            error_msg = f"Error running {self.name}: {e}\n"
            self.output_widget.insert(tk.END, error_msg)
            self.output_widget.see(tk.END)

    def stop(self):
        """Stop the process gracefully"""
        if self.process:
            try:
                self.process.terminate()
                # Wait a bit for graceful shutdown
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
                self.pid = None
                
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
            self.thread = None

    def is_running(self) -> bool:
        """Check if the process is currently running"""
        if self.process:
            return self.process.poll() is None
        return False

    def get_pid(self) -> Optional[int]:
        """Get the process ID"""
        return self.pid

    def get_uptime(self) -> float:
        """Get process uptime in seconds"""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0

    def get_memory_usage(self) -> Optional[float]:
        """Get memory usage in MB"""
        if self.pid:
            try:
                process = psutil.Process(self.pid)
                return process.memory_info().rss / 1024 / 1024  # Convert to MB
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None
        return None

    def get_cpu_usage(self) -> Optional[float]:
        """Get CPU usage percentage"""
        if self.pid:
            try:
                process = psutil.Process(self.pid)
                return process.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None
        return None


def wait_for_port(port: int, log_func, timeout: int = 120) -> bool:
    """Wait for a port to become available"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except (socket.timeout, ConnectionRefusedError):
            pass
        log_func(f"Waiting for service on port {port}...")
        time.sleep(1)
    return False


def is_port_in_use(port: int) -> bool:
    """Check if a port is currently in use"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False


def find_batch_file(filename: str, project_root: str) -> Optional[str]:
    """Find a batch file in the project, excluding installer and venv directories"""
    import os
    
    for root, dirs, files in os.walk(project_root):
        # Skip installer directories and venv directories
        dirs[:] = [d for d in dirs if d not in ['installer_files', 'venv', '__pycache__', '.git']]
        
        if filename in files:
            file_path = os.path.join(root, filename)
            # Additional check to avoid installer files
            if 'installer_files' not in file_path and 'venv' not in file_path:
                return file_path
    return None


def beep():
    """Play a beep sound (Windows only)"""
    try:
        import winsound
        winsound.Beep(800, 200)
        time.sleep(0.1)
        winsound.Beep(1200, 200)
        time.sleep(0.1)
        winsound.Beep(1000, 400)
    except ImportError:
        print("Beep not supported on this OS.")


def kill_process_tree(pid: int) -> bool:
    """Kill a process and all its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Kill children first
        for child in children:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
                
        # Kill parent
        parent.kill()
        return True
    except psutil.NoSuchProcess:
        return False
    except psutil.AccessDenied:
        return False 
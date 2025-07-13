import os
import sys
import subprocess
import threading
import time
import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import pystray
from PIL import Image, ImageTk
from datetime import datetime
import webbrowser
import glob
import psutil
import re

# Remove venv creation, install_requirements, and activate_virtual_env functions and their calls.
# The script should now start directly with the GUI logic and not attempt to manage virtual environments.

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(PROJECT_ROOT, "launcher_config.json")
ICON_FILE = os.path.join(PROJECT_ROOT, "launcher_icon.png")
CMD_FLAGS_FILE = os.path.join(PROJECT_ROOT, "text-generation-webui-main", "CMD_FLAGS.txt")
LOG_FILE = os.path.join(PROJECT_ROOT, "launcher_log.txt")

# Auto-detect batch files
def find_batch_file(filename):
    """
    Find a batch file in the project, excluding installer and venv directories.
    """
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip installer directories and venv directories
        dirs[:] = [d for d in dirs if d not in ['installer_files', 'venv', '__pycache__', '.git']]
        
        if filename in files:
            file_path = os.path.join(root, filename)
            # Additional check to avoid installer files
            if 'installer_files' not in file_path and 'venv' not in file_path:
                return file_path
    return None

def beep():
    try:
        import winsound
        winsound.Beep(800, 200)
        time.sleep(0.1)
        winsound.Beep(1200, 200)
        time.sleep(0.1)
        winsound.Beep(1000, 400)
    except ImportError:
        print("Beep not supported on this OS.")

def wait_for_port(port, log, timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except (socket.timeout, ConnectionRefusedError):
            pass
        log(f"Waiting for Oobabooga on port {port}...")
        time.sleep(1)
    return False

def save_config(ooba_path, zwaifu_path):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"ooba_bat": ooba_path, "zwaifu_bat": zwaifu_path}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                data = json.load(f)
                return data.get("ooba_bat"), data.get("zwaifu_bat")
            except Exception:
                return None, None
    return None, None

class Process:
    def __init__(self, name, command, cwd, output_widget):
        self.name = name
        self.command = command
        self.cwd = cwd
        self.output_widget = output_widget
        self.process = None
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        try:
            self.process = subprocess.Popen(self.command, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in self.process.stdout:
                self.output_widget.insert(tk.END, line)
                self.output_widget.see(tk.END)
        except Exception as e:
            self.output_widget.insert(tk.END, f"Error running {self.name}: {e}\n")
            self.output_widget.see(tk.END)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
        if self.thread:
            self.thread.join()
            self.thread = None

    def is_running(self):
        return self.process is not None

# Place this after imports at the top of the file
TAB_THEMES = {
    'main_tab':      {'bg': '#23272e', 'fg': '#e6e6e6', 'entry_bg': '#2c2f36', 'entry_fg': '#e6e6e6'},
    'settings_tab':  {'bg': '#222222', 'fg': '#ffffff', 'entry_bg': '#333333', 'entry_fg': '#cccccc'},
    'about_tab':     {'bg': '#1a1a1a', 'fg': '#ffcc00', 'entry_bg': '#222222', 'entry_fg': '#ffcc00'},
    'ollama_tab':    {'bg': '#1e232b', 'fg': '#00ffcc', 'entry_bg': '#23272e', 'entry_fg': '#00ffcc'},
    'rvc_tab':       {'bg': '#23272e', 'fg': '#ff99cc', 'entry_bg': '#2c2f36', 'entry_fg': '#ff99cc'},
    'logs_tab':      {'bg': '#181818', 'fg': '#00ff00', 'entry_bg': '#232323', 'entry_fg': '#00ff00'},
}

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        root.title("Z Launcher")
        root.geometry("1000x800")
        root.minsize(800, 600)
        root.resizable(True, True)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.status_var = tk.StringVar(value="")
        status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize batch file paths first
        self.ooba_bat = None
        self.zwaifu_bat = None
        self.ollama_bat = None
        self.rvc_bat = None

        # Initialize RVC variables
        self.rvc_host = tk.StringVar(value="127.0.0.1")
        self.rvc_port = tk.StringVar(value="7897")
        self.rvc_model = tk.StringVar(value="default")
        self.rvc_speaker = tk.StringVar(value="0")
        self.rvc_pitch = tk.StringVar(value="0.0")
        self.rvc_speed = tk.StringVar(value="1.0")

        # Initialize boolean variables
        self.ollama_enabled = tk.BooleanVar(value=False)
        self.rvc_enabled = tk.BooleanVar(value=False)

        # Initialize processes dictionary
        self.processes = {}

        # Track current theme state
        self._dark_mode = False

        # Load config and icon first
        self.load_config()
        self.load_icon()
                         

        # Header frame to hold only the notebook (not the button)
        self.notebook_frame = ttk.Frame(root)
        self.notebook_frame.pack(fill=tk.X)

        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill=tk.X, expand=True)

        # Ensure the launcher icon exists on startup
        if not os.path.exists(ICON_FILE):
            try:
                subprocess.run([sys.executable, 'create_launcher_icon.py'], check=True)
            except Exception as e:
                print(f"Failed to generate launcher_icon.png: {e}")

        self.auto_detect_batch_files()
        
        self.create_main_tab()
        self.create_cmd_flags_tab()
        self.create_settings_tab()
        self.create_about_tab()
        self.create_ollama_tab()
        self.create_rvc_tab()
        self.create_logs_tab()
        self.create_instance_manager_tab()  # Add instance manager tab
        self.setup_process_tabs() # Call setup_process_tabs here

        # Create theme toggle button after all tabs are created
        self.theme_toggle_btn = ttk.Button(root, text="☽", width=3, command=self.toggle_theme)
        self.theme_toggle_btn.place(relx=1.0, y=2, anchor="ne")
        
        # Set initial theme state - start in light mode
        self._dark_mode = False
        self.set_light_mode()
        self.load_theme()  # Apply saved theme

        # Start periodic status updates
        self.root.after(1000, self.update_process_status)  # Start after 1 second
        self.root.after(2000, self.update_instance_manager)  # Update instance manager every 2 seconds

        # System tray icon removed as requested

    def log(self, msg):
        # Ensure log file exists
        try:
            if not os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.write("")
        except Exception:
            pass
        print(msg)  # Always print to CMD window
        if hasattr(self, 'main_log') and self.main_log:
            self.main_log.config(state='normal')
            self.main_log.insert(tk.END, msg + "\n")
            self.main_log.see(tk.END)
            self.main_log.config(state='disabled')

    def set_status(self, msg, color="blue"):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def browse_ooba(self):
        path = filedialog.askopenfilename(title="Select Oobabooga batch file", filetypes=[("Batch files", "*.bat")])
        if path:
            self.ooba_bat = path
            self.ooba_path_var.set(path)
            print(f"Selected Oobabooga batch: {path}")

    def browse_zwaifu(self):
        path = filedialog.askopenfilename(title="Select Z-Waifu batch file", filetypes=[("Batch files", "*.bat")])
        if path:
            self.zwaifu_bat = path
            self.zwaifu_path_var.set(path)
            print(f"Selected Z-Waifu batch: {path}")

    def save_ooba(self):
        save_config(self.ooba_bat, self.zwaifu_bat)
        self.log(f"[Oobabooga] Saved as default: {self.ooba_bat}")

    def save_zwaifu(self):
        save_config(self.ooba_bat, self.zwaifu_bat)
        self.log(f"[Z-Waifu] Saved as default: {self.zwaifu_bat}")

    def is_port_in_use(self, port):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def launch(self):
        # Launch both Oobabooga and Z-Waifu if batch files are set, else prompt user
        if not self.ooba_bat or not os.path.exists(self.ooba_bat):
            messagebox.showerror("Error", "Oobabooga batch file not set! Please browse and select it in Settings.")
            return
        if not self.zwaifu_bat or not os.path.exists(self.zwaifu_bat):
            messagebox.showerror("Error", "Z-Waifu batch file not set! Please browse and select it in Settings.")
            return
        try:
            ooba_port = int(self.ooba_port_var.get())
            zwaifu_port = int(self.zwaifu_port_var.get())
        except Exception:
            messagebox.showerror("Invalid Port", "Both ports must be numbers.")
            return
        if self.is_port_in_use(ooba_port):
            messagebox.showerror("Port In Use", f"Oobabooga port {ooba_port} is already in use. Please choose another port or stop the process using it.")
            return
        if self.is_port_in_use(zwaifu_port):
            messagebox.showerror("Port In Use", f"Z-Waifu port {zwaifu_port} is already in use. Please choose another port or stop the process using it.")
            return
        self.start_btn.config(state='disabled')
        self.stop_all_btn.config(state='normal')  # Always allow stop
        self.set_status("Launching Oobabooga and Z-Waifu...", "green")
        self._stop_requested = False
        threading.Thread(target=self._launch_thread, args=(ooba_port, zwaifu_port), daemon=True).start()

    def _launch_thread(self, ooba_port, zwaifu_port):
        try:
            # Start Oobabooga
            self.log(f"[Oobabooga] Starting: {self.ooba_bat}")
            self.ooba_proc = subprocess.Popen([self.ooba_bat], cwd=os.path.dirname(self.ooba_bat), shell=True)
            self.set_status(f"Waiting for Oobabooga on port {ooba_port}...", "orange")
            # Wait for port, but allow interruption
            start = time.time()
            while time.time() - start < 120:
                if self._stop_requested:
                    if self.ooba_proc: self.ooba_proc.kill()
                    self.set_status("Oobabooga launch stopped by user.", "red")
                    self.log("[Oobabooga] Launch stopped by user.")
                    self.start_btn.config(state='normal')
                    self.stop_all_btn.config(state='disabled')
                    return
                try:
                    with socket.create_connection(("127.0.0.1", ooba_port), timeout=1):
                        break
                except (socket.timeout, ConnectionRefusedError):
                    pass
                self.log(f"Waiting for Oobabooga on port {ooba_port}...")
                time.sleep(1)
            else:
                self.set_status("Timeout waiting for Oobabooga!", "red")
                self.log("[ERROR] Timeout waiting for Oobabooga. Killing process.")
                if self.ooba_proc: self.ooba_proc.kill()
                self.start_btn.config(state='normal')
                self.stop_all_btn.config(state='disabled')
                return
            self.set_status("Oobabooga is up. Launching Z-Waifu...", "green")
            # Start Z-Waifu
            self.log(f"[Z-Waifu] Starting: {self.zwaifu_bat}")
            self.zwaifu_proc = subprocess.Popen([self.zwaifu_bat], cwd=os.path.dirname(self.zwaifu_bat), shell=True)
            # Wait for Z-Waifu port, allow interruption
            start = time.time()
            while time.time() - start < 120:
                if self._stop_requested:
                    if self.zwaifu_proc: self.zwaifu_proc.kill()
                    self.set_status("Z-Waifu launch stopped by user.", "red")
                    self.log("[Z-Waifu] Launch stopped by user.")
                    self.start_btn.config(state='normal')
                    self.stop_all_btn.config(state='disabled')
                    return
                try:
                    with socket.create_connection(("127.0.0.1", zwaifu_port), timeout=1):
                        break
                except (socket.timeout, ConnectionRefusedError):
                    pass
                self.log(f"Waiting for Z-Waifu on port {zwaifu_port}...")
                time.sleep(1)
            else:
                self.set_status("Timeout waiting for Z-Waifu!", "red")
                self.log("[ERROR] Timeout waiting for Z-Waifu. Killing process.")
                if self.zwaifu_proc: self.zwaifu_proc.kill()
                self.start_btn.config(state='normal')
                self.stop_all_btn.config(state='disabled')
                return
            self.set_status("Both Oobabooga and Z-Waifu started!", "green")
            self.log("Both Oobabooga and Z-Waifu started successfully.")
            self.log(f"Oobabooga batch: {self.ooba_bat}")
            self.log(f"Z-Waifu batch:   {self.zwaifu_bat}")
        except Exception as e:
            self.set_status(f"Error: {e}", "red")
            self.log(f"[ERROR] {e}")
            if hasattr(self, 'ooba_proc') and self.ooba_proc: self.ooba_proc.kill()
            if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc: self.zwaifu_proc.kill()
            self.start_btn.config(state='normal')
            self.stop_all_btn.config(state='disabled')

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    config_data = json.load(f)
                    self.ooba_bat = config_data.get("ooba_bat")
                    self.zwaifu_bat = config_data.get("zwaifu_bat")
                    print(f"Loaded from config: Oobabooga={self.ooba_bat}, Z-Waifu={self.zwaifu_bat}")
                    self.ollama_enabled.set(config_data.get("ollama_enabled", False))
                    self.ollama_bat = config_data.get("ollama_bat")
                    self.rvc_enabled.set(config_data.get("rvc_enabled", False))
                    self.rvc_host.set(config_data.get("rvc_host", "127.0.0.1"))
                    self.rvc_port.set(config_data.get("rvc_port", "7897"))
                    self.rvc_model.set(config_data.get("rvc_model", "default"))
                    self.rvc_speaker.set(config_data.get("rvc_speaker", "0"))
                    self.rvc_pitch.set(config_data.get("rvc_pitch", "0.0"))
                    self.rvc_speed.set(config_data.get("rvc_speed", "1.0"))
                    self.rvc_bat = config_data.get("rvc_bat")
                    self.current_theme = config_data.get("theme", "light")
                    self.last_port = config_data.get("port", "5000")
                    
                    # Load auto-start settings
                    if hasattr(self, 'auto_start_ooba'):
                        self.auto_start_ooba.set(config_data.get("auto_start_ooba", False))
                    if hasattr(self, 'auto_start_zwaifu'):
                        self.auto_start_zwaifu.set(config_data.get("auto_start_zwaifu", False))
                    if hasattr(self, 'auto_start_ollama'):
                        self.auto_start_ollama.set(config_data.get("auto_start_ollama", False))
                    if hasattr(self, 'auto_start_rvc'):
                        self.auto_start_rvc.set(config_data.get("auto_start_rvc", False))
                    
                    # Load port settings
                    if hasattr(self, 'ooba_port_var'):
                        self.ooba_port_var.set(config_data.get("ooba_port", "7860"))
                    if hasattr(self, 'zwaifu_port_var'):
                        self.zwaifu_port_var.set(config_data.get("zwaifu_port", "5000"))
                except Exception:
                    self.ooba_bat = None
                    self.zwaifu_bat = None
                    self.ollama_enabled.set(False)
                    self.ollama_bat = None
                    self.rvc_enabled.set(False)
                    self.rvc_host.set("127.0.0.1")
                    self.rvc_port.set("7897")
                    self.rvc_model.set("default")
                    self.rvc_speaker.set("0")
                    self.rvc_pitch.set("0.0")
                    self.rvc_speed.set("1.0")
                    self.rvc_bat = None
                    self.current_theme = "light"
                    self.last_port = "5000"
        else:
            self.current_theme = "light"
            self.last_port = "5000"

    def save_config(self):
        config_data = {
            "ooba_bat": self.ooba_bat,
            "zwaifu_bat": self.zwaifu_bat,
            "ollama_enabled": self.ollama_enabled.get(),
            "ollama_bat": self.ollama_bat,
            "rvc_enabled": self.rvc_enabled.get(),
            "rvc_host": self.rvc_host.get(),
            "rvc_port": self.rvc_port.get(),
            "rvc_model": self.rvc_model.get(),
            "rvc_speaker": self.rvc_speaker.get(),
            "rvc_pitch": self.rvc_pitch.get(),
            "rvc_speed": self.rvc_speed.get(),
            "rvc_bat": self.rvc_bat,
            "theme": getattr(self, 'current_theme', 'light'),
            "port": getattr(self, 'last_port', '5000'),
            "auto_start_ooba": getattr(self, 'auto_start_ooba', tk.BooleanVar(value=False)).get(),
            "auto_start_zwaifu": getattr(self, 'auto_start_zwaifu', tk.BooleanVar(value=False)).get(),
            "auto_start_ollama": getattr(self, 'auto_start_ollama', tk.BooleanVar(value=False)).get(),
            "auto_start_rvc": getattr(self, 'auto_start_rvc', tk.BooleanVar(value=False)).get(),
            "ooba_port": getattr(self, 'ooba_port_var', tk.StringVar(value="7860")).get(),
            "zwaifu_port": getattr(self, 'zwaifu_port_var', tk.StringVar(value="5000")).get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)

    def load_icon(self):
        if os.path.exists(ICON_FILE):
            self.icon = tk.PhotoImage(file=ICON_FILE)
            self.root.iconphoto(True, self.icon)
            from io import BytesIO
            with open(ICON_FILE, "rb") as f:
                self.tray_icon = Image.open(BytesIO(f.read()))
        else:
            self.icon = None
            # Fallback: create a blank icon for pystray
            self.tray_icon = Image.new("RGBA", (64, 64), (255, 255, 255, 0))

    def load_theme(self):
        """
        Load and apply the saved theme from config.
        """
        if hasattr(self, 'current_theme'):
            if self.current_theme == 'dark':
                self.set_dark_mode()
                self._dark_mode = True
            else:
                self.set_light_mode()
                self._dark_mode = False
        else:
            # Default to light theme
            self.set_light_mode()
            self._dark_mode = False
        
        # Update button if it exists
        if hasattr(self, 'theme_toggle_btn'):
            # Show the opposite emoji of current theme (what you'll switch to)
            emoji = "☀" if self._dark_mode else "☽"
            self.theme_toggle_btn.config(text=emoji)

    def create_main_tab(self):
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Main")
        # Start/Stop All Controls
        control_frame = ttk.Frame(main_tab)
        control_frame.pack(padx=10, pady=10, fill=tk.X)
        self.start_btn = ttk.Button(control_frame, text="Start All", command=self.launch)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_all_btn = ttk.Button(control_frame, text="Stop All", command=self.stop_all_processes)
        self.stop_all_btn.pack(side=tk.LEFT, padx=5)
        self.launch_main_btn = ttk.Button(control_frame, text="Launch Main Program", command=self.launch_main_program)
        self.launch_main_btn.pack(side=tk.LEFT, padx=5)
        # Main log area
        log_frame = ttk.LabelFrame(main_tab, text="Log")
        log_frame.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)
        self.main_log = scrolledtext.ScrolledText(log_frame, state='disabled', font=("Consolas", 9))
        self.main_log.pack(fill=tk.BOTH, expand=True)
        # Main program output area
        main_prog_frame = ttk.LabelFrame(main_tab, text="Main Program Output")
        main_prog_frame.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)
        self.main_program_output = scrolledtext.ScrolledText(main_prog_frame, state='disabled', font=("Consolas", 9))
        self.main_program_output.pack(in_=main_prog_frame, fill=tk.BOTH, expand=True)
        self.main_tab = main_tab # Assign for styling
        self.style_widgets(main_tab, '#f0f0f0', '#000000', '#ffffff', '#000000') # Style main tab

        self.add_demo_buttons()

    def create_cmd_flags_tab(self):
        """Create CMD_FLAGS.txt editor tab"""
        cmd_flags_tab = ttk.Frame(self.notebook)
        self.notebook.add(cmd_flags_tab, text="CMD Flags")
        
        # Title and description
        title_frame = ttk.Frame(cmd_flags_tab)
        title_frame.pack(fill=tk.X, padx=10, pady=(10,5))
        ttk.Label(title_frame, text="CMD_FLAGS.txt Editor", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(title_frame, text="Edit Oobabooga command line flags", font=("Arial", 9)).pack(anchor=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(cmd_flags_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        ttk.Button(control_frame, text="Load File", command=self.load_cmd_flags).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(control_frame, text="Save File", command=self.save_cmd_flags).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reset to Default", command=self.reset_cmd_flags).pack(side=tk.LEFT, padx=5)
        
        # Text editor
        editor_frame = ttk.LabelFrame(cmd_flags_tab, text="CMD_FLAGS.txt Content")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        self.cmd_flags_text = scrolledtext.ScrolledText(editor_frame, font=("Consolas", 10), wrap=tk.NONE)
        self.cmd_flags_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.cmd_flags_status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(cmd_flags_tab, textvariable=self.cmd_flags_status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0,10))
        
        # Load initial content
        self.load_cmd_flags()
        
        self.style_widgets(cmd_flags_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.cmd_flags_tab = cmd_flags_tab

    def load_cmd_flags(self):
        """Load CMD_FLAGS.txt content into the editor"""
        try:
            if os.path.exists(CMD_FLAGS_FILE):
                with open(CMD_FLAGS_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.cmd_flags_text.delete('1.0', tk.END)
                self.cmd_flags_text.insert('1.0', content)
                self.cmd_flags_status_var.set(f"Loaded: {CMD_FLAGS_FILE}")
                self.log(f"[CMD Flags] Loaded file: {CMD_FLAGS_FILE}")
            else:
                # Create default content
                default_content = """# Oobabooga CMD Flags
# Add your command line flags here
# Example:
# --listen
# --port 7860
# --api
# --extensions api
"""
                self.cmd_flags_text.delete('1.0', tk.END)
                self.cmd_flags_text.insert('1.0', default_content)
                self.cmd_flags_status_var.set("Created default content (file not found)")
                self.log("[CMD Flags] File not found, created default content")
        except Exception as e:
            self.cmd_flags_status_var.set(f"Error loading file: {e}")
            self.log(f"[CMD Flags] Error loading file: {e}")

    def save_cmd_flags(self):
        """Save CMD_FLAGS.txt content from the editor"""
        try:
            content = self.cmd_flags_text.get('1.0', tk.END)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(CMD_FLAGS_FILE), exist_ok=True)
            
            with open(CMD_FLAGS_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.cmd_flags_status_var.set(f"Saved: {CMD_FLAGS_FILE}")
            self.log(f"[CMD Flags] Saved file: {CMD_FLAGS_FILE}")
            messagebox.showinfo("Success", "CMD_FLAGS.txt has been saved successfully!")
        except Exception as e:
            self.cmd_flags_status_var.set(f"Error saving file: {e}")
            self.log(f"[CMD Flags] Error saving file: {e}")
            messagebox.showerror("Error", f"Failed to save CMD_FLAGS.txt: {e}")

    def reset_cmd_flags(self):
        """Reset CMD_FLAGS.txt to default content"""
        if messagebox.askyesno("Reset CMD Flags", "Are you sure you want to reset CMD_FLAGS.txt to default content?"):
            default_content = """# Oobabooga CMD Flags
# Add your command line flags here
# Example:
# --listen
# --port 7860
# --api
# --extensions api
"""
            self.cmd_flags_text.delete('1.0', tk.END)
            self.cmd_flags_text.insert('1.0', default_content)
            self.cmd_flags_status_var.set("Reset to default content")
            self.log("[CMD Flags] Reset to default content")

    def create_settings_tab(self):
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Settings")

        # Create a scrollable frame for settings
        canvas = tk.Canvas(settings_tab)
        scrollbar = ttk.Scrollbar(settings_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)  # Use tk.Frame so bg can be set

        # Store for theme switching
        self.settings_canvas = canvas
        self.settings_scrollable_frame = scrollable_frame

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Preferences and options
        prefs_frame = ttk.LabelFrame(scrollable_frame, text="Preferences")
        prefs_frame.pack(padx=10, pady=10, fill=tk.X)

        # Auto-start options
        auto_frame = ttk.LabelFrame(scrollable_frame, text="Auto-Start Options")
        auto_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.auto_start_ooba = tk.BooleanVar(value=False)
        self.auto_start_zwaifu = tk.BooleanVar(value=False)
        self.auto_start_ollama = tk.BooleanVar(value=False)
        self.auto_start_rvc = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(auto_frame, text="Auto-start Oobabooga", variable=self.auto_start_ooba).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(auto_frame, text="Auto-start Z-Waifu", variable=self.auto_start_zwaifu).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(auto_frame, text="Auto-start Ollama", variable=self.auto_start_ollama).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Checkbutton(auto_frame, text="Auto-start RVC", variable=self.auto_start_rvc).pack(anchor=tk.W, padx=5, pady=2)

        # Port settings
        port_frame = ttk.LabelFrame(scrollable_frame, text="Port Settings")
        port_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(port_frame, text="Oobabooga Port:").pack(anchor=tk.W, padx=5, pady=2)
        self.ooba_port_var = tk.StringVar(value="7860")
        ttk.Entry(port_frame, textvariable=self.ooba_port_var, width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(port_frame, text="Z-Waifu Port:").pack(anchor=tk.W, padx=5, pady=2)
        self.zwaifu_port_var = tk.StringVar(value="5000")
        ttk.Entry(port_frame, textvariable=self.zwaifu_port_var, width=10).pack(anchor=tk.W, padx=5, pady=2)

        # Batch file settings
        batch_frame = ttk.LabelFrame(scrollable_frame, text="Batch File Settings")
        batch_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Oobabooga batch
        ttk.Label(batch_frame, text="Oobabooga Batch File:").pack(anchor=tk.W, padx=5, pady=2)
        self.ooba_path_var = tk.StringVar(value=self.ooba_bat or "Not set")
        ttk.Entry(batch_frame, textvariable=self.ooba_path_var, state='readonly').pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(batch_frame, text="Browse Oobabooga", command=self.browse_ooba).pack(anchor=tk.W, padx=5, pady=2)
        
        # Z-Waifu batch
        ttk.Label(batch_frame, text="Z-Waifu Batch File:").pack(anchor=tk.W, padx=5, pady=2)
        self.zwaifu_path_var = tk.StringVar(value=self.zwaifu_bat or "Not set")
        ttk.Entry(batch_frame, textvariable=self.zwaifu_path_var, state='readonly').pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(batch_frame, text="Browse Z-Waifu", command=self.browse_zwaifu).pack(anchor=tk.W, padx=5, pady=2)

        # Theme settings
        theme_frame = ttk.LabelFrame(scrollable_frame, text="Theme")
        theme_frame.pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(theme_frame, text="Dark Mode", command=self.set_dark_mode_from_settings).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(theme_frame, text="Light Mode", command=self.set_light_mode_from_settings).pack(side=tk.LEFT, padx=5, pady=5)

        # Save settings button
        save_btn = ttk.Button(scrollable_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(padx=10, pady=10)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.settings_tab = settings_tab # Assign for styling
        self.style_widgets(settings_tab, '#f0f0f0', '#000000', '#ffffff', '#000000') # Style settings tab
        
    def save_settings(self):
        """
        Save all settings to config file.
        """
        try:
            self.save_config()
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            self.log("[Settings] Configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.log(f"[Settings] Error saving configuration: {e}")

    def style_widgets(self, parent, bg_color, fg_color, entry_bg, entry_fg):
        for child in parent.winfo_children():
            cls = child.__class__.__name__
            if cls in ['Label', 'Checkbutton', 'Button', 'Frame', 'Labelframe']:
                try:
                    child.config(bg=bg_color, fg=fg_color)
                except Exception:
                    pass
            elif cls == 'Entry':
                try:
                    child.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
                except Exception:
                    pass
            elif cls in ['Text', 'ScrolledText', 'Listbox']:
                try:
                    child.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
                except Exception:
                    pass
            elif cls == 'Radiobutton':
                try:
                    child.config(bg=bg_color, fg=fg_color, selectcolor=entry_bg)
                except Exception:
                    pass
            elif cls == 'Scale':
                try:
                    child.config(bg=bg_color, fg=fg_color, troughcolor=entry_bg)
                except Exception:
                    pass
            elif cls == 'Spinbox':
                try:
                    child.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)
                except Exception:
                    pass
            # Recursively style children
            if hasattr(child, 'winfo_children') and child.winfo_children():
                self.style_widgets(child, bg_color, fg_color, entry_bg, entry_fg)

    def set_dark_mode(self):
        style = ttk.Style()
        # Use 'clam' as a base for dark mode
        style.theme_use('clam')
        style.configure('.', background='#222222', foreground='#ffffff')
        style.configure('TLabel', background='#222222', foreground='#ffffff')
        style.configure('TFrame', background='#222222')
        style.configure('TButton', background='#333333', foreground='#ffffff')
        style.configure('TNotebook', background='#222222')
        style.configure('TNotebook.Tab', background='#333333', foreground='#ffffff')
        style.configure('TEntry', fieldbackground='#333333', foreground='#cccccc', insertcolor='#ffffff')
        self.root.configure(bg='#222222')
        self.current_theme = 'dark'
        self._dark_mode = True
        if hasattr(self, 'settings_canvas'):
            self.settings_canvas.config(bg='#222222')
        if hasattr(self, 'settings_scrollable_frame'):
            self.settings_scrollable_frame.config(bg='#222222')
            self.style_widgets(self.settings_scrollable_frame, '#222222', '#ffffff', '#333333', '#cccccc')
        for tab_attr in ['main_tab', 'settings_tab', 'about_tab', 'ollama_tab', 'rvc_tab', 'logs_tab', 'ooba_tab', 'zwaifu_tab']:
            if hasattr(self, tab_attr):
                theme = TAB_THEMES.get(tab_attr, {'bg': '#222222', 'fg': '#ffffff', 'entry_bg': '#333333', 'entry_fg': '#cccccc'})
                self.style_widgets(getattr(self, tab_attr), theme['bg'], theme['fg'], theme['entry_bg'], theme['entry_fg'])
        self.save_config()

    def set_light_mode(self):
        style = ttk.Style()
        # Use 'default' as a base for light mode
        style.theme_use('default')
        style.configure('.', background='#f0f0f0', foreground='#000000')
        style.configure('TLabel', background='#f0f0f0', foreground='#000000')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', background='#e0e0e0', foreground='#000000')
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', background='#e0e0e0', foreground='#000000')
        style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000', insertcolor='#000000')
        self.root.configure(bg='#f0f0f0')
        self.current_theme = 'light'
        self._dark_mode = False
        if hasattr(self, 'settings_canvas'):
            self.settings_canvas.config(bg='#f0f0f0')
        if hasattr(self, 'settings_scrollable_frame'):
            self.settings_scrollable_frame.config(bg='#f0f0f0')
            self.style_widgets(self.settings_scrollable_frame, '#f0f0f0', '#000000', '#ffffff', '#000000')
        for tab_attr in ['main_tab', 'settings_tab', 'about_tab', 'ollama_tab', 'rvc_tab', 'logs_tab', 'ooba_tab', 'zwaifu_tab']:
            if hasattr(self, tab_attr):
                # Use a light version of the custom theme, or fallback
                theme = TAB_THEMES.get(tab_attr, {'bg': '#f0f0f0', 'fg': '#000000', 'entry_bg': '#ffffff', 'entry_fg': '#000000'})
                # For demo, just use the fallback for all tabs in light mode, or you can define light themes per tab
                self.style_widgets(getattr(self, tab_attr), theme['bg'], theme['fg'], theme['entry_bg'], theme['entry_fg'])
        self.save_config()

    def set_dark_mode_from_settings(self):
        """Set dark mode and update the theme toggle button"""
        self.set_dark_mode()
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.config(text="☀")  # Show sun to switch to light mode

    def set_light_mode_from_settings(self):
        """Set light mode and update the theme toggle button"""
        self.set_light_mode()
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.config(text="☽")  # Show moon to switch to dark mode

    def create_about_tab(self):
        about_tab = ttk.Frame(self.notebook)
        self.notebook.add(about_tab, text="About")

        # About and help information
        about_text = scrolledtext.ScrolledText(about_tab, wrap=tk.WORD, font=("Arial", 11))
        about_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        about_text.insert(tk.END, "Z Launcher\n\n")
        about_text.insert(tk.END, "Version: 1.0.0\n")
        about_text.insert(tk.END, "Author: Drakkadakka\n")
        about_text.insert(tk.END, "GitHub: https://github.com/Drakkadakka\n")
        about_text.insert(tk.END, "Email: Drakkadakka@users.noreply.github.com\n\n")
        about_text.insert(tk.END, "A powerful launcher for managing Oobabooga, Z-Waifu, Ooba-LLaMA, and RVC processes.\n\n")
        about_text.insert(tk.END, "For more information and updates, visit:\n")
        about_text.insert(tk.END, "https://github.com/Drakkadakka/zwaifu-launcher\n\n")
        about_text.insert(tk.END, "If you encounter any issues or have feature requests, please open an issue on GitHub or contact the author directly.\n")
        about_text.configure(state='disabled')
        self.about_tab = about_tab # Assign for styling
        self.style_widgets(about_tab, '#f0f0f0', '#000000', '#ffffff', '#000000') # Style about tab

    def create_ollama_tab(self):
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {}
        if 'Ollama' not in self.process_instance_tabs:
            self.process_instance_tabs['Ollama'] = []

        ollama_tab = ttk.Frame(self.notebook)
        self.notebook.add(ollama_tab, text="Ollama")

        # Batch file selection
        ttk.Label(ollama_tab, text="Ollama batch:").pack(anchor=tk.W, padx=10, pady=(10,0))
        self.ollama_path_var = tk.StringVar(value=self.ollama_bat if self.ollama_bat else "NOT FOUND")
        ttk.Entry(ollama_tab, textvariable=self.ollama_path_var, state='readonly').pack(fill=tk.X, padx=10, expand=True)
        ttk.Button(ollama_tab, text="Browse...", command=self.browse_ollama).pack(anchor=tk.E, padx=10, pady=(0,10))

        # Launch new instance button
        def launch_ollama_instance():
            bat_path = self.ollama_path_var.get()
            if not bat_path or not os.path.exists(bat_path):
                self.log("Ollama batch file not set or does not exist.")
                return
            # Create a new tab for this instance
            instance_tab = ttk.Frame(self.notebook)
            self.notebook.add(instance_tab, text=f"Ollama Instance {len(self.process_instance_tabs['Ollama'])+1}")
            self.notebook.select(instance_tab)
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc, bat_path)
                self.log(f"Ollama instance launched: {bat_path}")
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start Ollama: {e}\n", '31')
                self.log(f"[ERROR] Failed to start Ollama: {e}")
            self.process_instance_tabs['Ollama'].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc})

        ttk.Button(ollama_tab, text="Launch Ollama Instance", command=launch_ollama_instance).pack(padx=10, pady=(0, 10), anchor="w")
        self.style_widgets(ollama_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.ollama_tab = ollama_tab

    def create_rvc_tab(self):
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {}
        if 'RVC' not in self.process_instance_tabs:
            self.process_instance_tabs['RVC'] = []

        rvc_tab = ttk.Frame(self.notebook)
        self.notebook.add(rvc_tab, text="RVC")

        # Batch file selection
        ttk.Label(rvc_tab, text="RVC batch:").pack(anchor=tk.W, padx=10, pady=(10,0))
        self.rvc_path_var = tk.StringVar(value=self.rvc_bat if self.rvc_bat else "NOT FOUND")
        ttk.Entry(rvc_tab, textvariable=self.rvc_path_var, state='readonly').pack(fill=tk.X, padx=10, expand=True)
        ttk.Button(rvc_tab, text="Browse...", command=self.browse_rvc).pack(anchor=tk.E, padx=10, pady=(0,10))

        # Launch new instance button
        def launch_rvc_instance():
            bat_path = self.rvc_path_var.get()
            if not bat_path or not os.path.exists(bat_path):
                self.log("RVC batch file not set or does not exist.")
                return
            # Create a new tab for this instance
            instance_tab = ttk.Frame(self.notebook)
            self.notebook.add(instance_tab, text=f"RVC Instance {len(self.process_instance_tabs['RVC'])+1}")
            self.notebook.select(instance_tab)
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc)
                self.log(f"RVC instance launched: {bat_path}")
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start RVC: {e}\n", '31')
                self.log(f"[ERROR] Failed to start RVC: {e}")
            self.process_instance_tabs['RVC'].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc})

        ttk.Button(rvc_tab, text="Launch RVC Instance", command=launch_rvc_instance).pack(padx=10, pady=(0, 10), anchor="w")
        self.style_widgets(rvc_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.rvc_tab = rvc_tab

    def browse_ollama(self):
        path = filedialog.askopenfilename(title="Select Ollama batch file", filetypes=[("Batch files", "*.bat")])
        if path:
            self.ollama_bat = path
            self.ollama_path_var.set(path)

    def launch_ollama(self):
        import threading, time
        self.stop_ollama()
        bat_path = self.ollama_path_var.get()
        args = self.ollama_args_var.get().strip()
        if not bat_path or not os.path.exists(bat_path):
            self.log("Ollama batch file not set or does not exist.")
            if hasattr(self, 'ollama_status_var'):
                self.ollama_status_var.set("Error: Batch not set")
                self.ollama_status_label.config(foreground="red")
            return
        try:
            self.ollama_output.config(state='normal')
            self.ollama_output.delete('1.0', tk.END)
            self.ollama_output.config(state='disabled')
            # Launch in visible CMD window with output capture
            if args:
                full_cmd = f'"{bat_path}" {args}'
            else:
                full_cmd = f'"{bat_path}"'
            
            # Create a wrapper script that captures output while showing CMD window
            wrapper_script = f'''@echo off
title Ollama - Launcher Output
echo Starting Ollama...
echo Command: {full_cmd}
echo.
{full_cmd}
echo.
echo Ollama process ended.
pause
'''
            
            # Write wrapper script to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
                f.write(wrapper_script)
                wrapper_path = f.name
            
            # Launch the wrapper script in visible CMD window
            self.ollama_proc = subprocess.Popen(
                ['cmd.exe', '/c', 'start', 'cmd.exe', '/k', wrapper_path],
                cwd=os.path.dirname(bat_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.ollama_start_time = time.time()
            self.ollama_monitoring = True
            self.log(f"Ollama launched: {' '.join(cmd)}")
            
            # Update status
            if hasattr(self, 'ollama_status_var'):
                self.ollama_status_var.set("Running")
                self.ollama_status_label.config(foreground="green")
            if hasattr(self, 'ollama_pid_var'):
                self.ollama_pid_var.set(f"PID: {self.ollama_proc.pid}")
            
            # Add initial status to GUI
            self.ollama_output.config(state='normal')
            self.ollama_output.insert(tk.END, f"Starting Ollama...\n")
            self.ollama_output.insert(tk.END, f"Command: {full_cmd}\n")
            self.ollama_output.insert(tk.END, f"PID: {self.ollama_proc.pid}\n")
            self.ollama_output.insert(tk.END, f"CMD window opened with title: Ollama - Launcher Output\n")
            self.ollama_output.insert(tk.END, f"Process is running in visible CMD window.\n")
            self.ollama_output.insert(tk.END, f"Check the CMD window for detailed output.\n\n")
            self.ollama_output.see(tk.END)
            self.ollama_output.config(state='disabled')
            
            # Print to console for debugging
            print(f"[Ollama] Starting Ollama...")
            print(f"[Ollama] Command: {full_cmd}")
            print(f"[Ollama] PID: {self.ollama_proc.pid}")
            print(f"[Ollama] CMD window opened with title: Ollama - Launcher Output")
            print(f"[Ollama] Process is running in visible CMD window.")
            print(f"[Ollama] Check the CMD window for detailed output.")
            
            def monitor_process():
                try:
                    while self.ollama_proc.poll() is None:
                        time.sleep(1)
                    
                    # Process ended
                    self.ollama_monitoring = False
                    if hasattr(self, 'ollama_status_var'):
                        self.ollama_status_var.set("Stopped")
                        self.ollama_status_label.config(foreground="red")
                    if hasattr(self, 'ollama_pid_var'):
                        self.ollama_pid_var.set("PID: -")
                    if hasattr(self, 'ollama_cpu_var'):
                        self.ollama_cpu_var.set("CPU: -%")
                    if hasattr(self, 'ollama_mem_var'):
                        self.ollama_mem_var.set("Mem: - MB")
                    
                    # Add final status to GUI
                    self.ollama_output.config(state='normal')
                    self.ollama_output.insert(tk.END, f"Ollama process ended.\n")
                    self.ollama_output.see(tk.END)
                    self.ollama_output.config(state='disabled')
                    
                    print(f"[Ollama] Process ended.")
                    self.log("Ollama process exited")
                    
                    # Auto-restart if enabled
                    if hasattr(self, 'ollama_auto_restart') and self.ollama_auto_restart.get():
                        self.log("Ollama exited unexpectedly. Auto-restarting...")
                        messagebox.showinfo("Ollama Auto-Restart", "Ollama exited unexpectedly. Auto-restarting...")
                        self.launch_ollama()
                        
                except Exception as e:
                    self.log(f"Error monitoring Ollama: {e}")
                    self.ollama_monitoring = False
            
            threading.Thread(target=monitor_process, daemon=True).start()
            
            def update_monitor():
                try:
                    p = psutil.Process(self.ollama_proc.pid)
                except Exception:
                    p = None
                
                while self.ollama_monitoring and self.ollama_proc.poll() is None:
                    elapsed = int(time.time() - self.ollama_start_time)
                    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                    if hasattr(self, 'ollama_uptime_var'):
                        self.ollama_uptime_var.set(f"Uptime: {h:02}:{m:02}:{s:02}")
                    
                    if p:
                        try:
                            cpu = p.cpu_percent(interval=0.5)
                            mem = p.memory_info().rss / (1024*1024)
                            if hasattr(self, 'ollama_cpu_var'):
                                self.ollama_cpu_var.set(f"CPU: {cpu:.1f}%")
                            if hasattr(self, 'ollama_mem_var'):
                                self.ollama_mem_var.set(f"Mem: {mem:.1f} MB")
                        except Exception:
                            if hasattr(self, 'ollama_cpu_var'):
                                self.ollama_cpu_var.set("CPU: -%")
                            if hasattr(self, 'ollama_mem_var'):
                                self.ollama_mem_var.set("Mem: - MB")
                    
                    time.sleep(0.5)
                
                if hasattr(self, 'ollama_uptime_var'):
                    self.ollama_uptime_var.set("Uptime: 00:00:00")
                if hasattr(self, 'ollama_cpu_var'):
                    self.ollama_cpu_var.set("CPU: -%")
                if hasattr(self, 'ollama_mem_var'):
                    self.ollama_mem_var.set("Mem: - MB")
            
            threading.Thread(target=update_monitor, daemon=True).start()
            
        except Exception as e:
            self.log(f"Error launching Ollama: {e}")
            if hasattr(self, 'ollama_status_var'):
                self.ollama_status_var.set("Error")
                self.ollama_status_label.config(foreground="red")
            if hasattr(self, 'ollama_pid_var'):
                self.ollama_pid_var.set("PID: -")
            if hasattr(self, 'ollama_cpu_var'):
                self.ollama_cpu_var.set("CPU: -%")
            if hasattr(self, 'ollama_mem_var'):
                self.ollama_mem_var.set("Mem: - MB")

    def stop_ollama(self):
        self.ollama_monitoring = False
        if hasattr(self, 'ollama_proc') and self.ollama_proc:
            try:
                # Get the process and all its children
                parent = psutil.Process(self.ollama_proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Killed Ollama child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to kill Ollama child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Killed Ollama parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill Ollama parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    self.ollama_proc.kill()
                    self.log("Killed Ollama wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill Ollama wrapper process: {e}")
                
                self.log("Ollama stopped.")
            except Exception as e:
                self.log(f"Error stopping Ollama: {e}")
            self.ollama_proc = None
        
        # Update status variables
        if hasattr(self, 'ollama_status_var'):
            self.ollama_status_var.set("Stopped")
            self.ollama_status_label.config(foreground="red")
        if hasattr(self, 'ollama_pid_var'):
            self.ollama_pid_var.set("PID: -")
        if hasattr(self, 'ollama_uptime_var'):
            self.ollama_uptime_var.set("Uptime: 00:00:00")
        if hasattr(self, 'ollama_cpu_var'):
            self.ollama_cpu_var.set("CPU: -%")
        if hasattr(self, 'ollama_mem_var'):
            self.ollama_mem_var.set("Mem: - MB")

    def restart_ollama(self):
        self.stop_ollama()
        self.launch_ollama()

    def force_kill_ollama(self):
        """Force kill Ollama and all its child processes"""
        self.ollama_monitoring = False
        if hasattr(self, 'ollama_proc') and self.ollama_proc:
            try:
                # Get the process and all its children
                parent = psutil.Process(self.ollama_proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Force killed Ollama child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to force kill Ollama child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Force killed Ollama parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to force kill Ollama parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    self.ollama_proc.kill()
                    self.log("Force killed Ollama wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to force kill Ollama wrapper process: {e}")
                
                self.log("Ollama force killed.")
            except Exception as e:
                self.log(f"Error force killing Ollama: {e}")
            self.ollama_proc = None
        if hasattr(self, 'ollama_uptime_var'):
            self.ollama_uptime_var.set("Uptime: 00:00:00")
        if hasattr(self, 'ollama_status_var'):
            self.ollama_status_var.set("Stopped")
            self.ollama_status_label.config(foreground="red")
        if hasattr(self, 'ollama_pid_var'):
            self.ollama_pid_var.set("PID: -")
        if hasattr(self, 'ollama_cpu_var'):
            self.ollama_cpu_var.set("CPU: -%")
        if hasattr(self, 'ollama_mem_var'):
            self.ollama_mem_var.set("Mem: - MB")

    def launch_ooba(self):
        import threading, time
        self.stop_ooba()  # Ensure previous process is killed
        if not hasattr(self, 'ooba_bat') or not self.ooba_bat or not os.path.exists(self.ooba_bat):
            self.log("Oobabooga batch file not set or does not exist.")
            if hasattr(self, 'process_status_vars') and 'Oobabooga' in self.process_status_vars:
                self.process_status_vars['Oobabooga'].set("Error")
            return
        try:
            self.ooba_proc = subprocess.Popen([self.ooba_bat], cwd=os.path.dirname(self.ooba_bat), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.ooba_start_time = time.time()
            self.ooba_monitoring = True
            self.log(f"Oobabooga launched: {self.ooba_bat}")
            if hasattr(self, 'process_status_vars') and 'Oobabooga' in self.process_status_vars:
                self.process_status_vars['Oobabooga'].set("Running")
            
            def read_output():
                try:
                    for line in self.ooba_proc.stdout:
                        if hasattr(self, 'ooba_output'):
                            self.ooba_output.config(state='normal')
                            self.ooba_output.insert(tk.END, line)
                            self.ooba_output.see(tk.END)
                            self.ooba_output.config(state='disabled')
                except Exception as e:
                    self.log(f"Error reading Oobabooga output: {e}")
                finally:
                    self.ooba_monitoring = False
                    if self.ooba_proc and self.ooba_proc.poll() is not None:
                        if hasattr(self, 'process_status_vars') and 'Oobabooga' in self.process_status_vars:
                            self.process_status_vars['Oobabooga'].set("Stopped")
                        self.log("Oobabooga process exited")
            
            threading.Thread(target=read_output, daemon=True).start()
            
            def update_uptime():
                while self.ooba_monitoring and hasattr(self, 'ooba_start_time'):
                    elapsed = int(time.time() - self.ooba_start_time)
                    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                    if hasattr(self, 'ooba_uptime_var'):
                        self.ooba_uptime_var.set(f"Uptime: {h:02}:{m:02}:{s:02}")
                    time.sleep(1)
            
            threading.Thread(target=update_uptime, daemon=True).start()
            
        except Exception as e:
            self.log(f"Error launching Oobabooga: {e}")
            if hasattr(self, 'process_status_vars') and 'Oobabooga' in self.process_status_vars:
                self.process_status_vars['Oobabooga'].set("Error")

    def stop_ooba(self):
        self.ooba_monitoring = False
        if hasattr(self, 'ooba_proc') and self.ooba_proc:
            try:
                # Get the process and all its children
                parent = psutil.Process(self.ooba_proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Killed Oobabooga child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to kill Oobabooga child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Killed Oobabooga parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill Oobabooga parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    self.ooba_proc.kill()
                    self.log("Killed Oobabooga wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill Oobabooga wrapper process: {e}")
                
                self.log("Oobabooga stopped.")
            except Exception as e:
                self.log(f"Error stopping Oobabooga: {e}")
            self.ooba_proc = None
        if hasattr(self, 'process_status_vars') and 'Oobabooga' in self.process_status_vars:
            self.process_status_vars['Oobabooga'].set("Stopped")
        if hasattr(self, 'ooba_uptime_var'):
            self.ooba_uptime_var.set("Uptime: 00:00:00")

    def launch_zwaifu(self):
        import threading, time
        self.stop_zwaifu()  # Ensure previous process is killed
        if not hasattr(self, 'zwaifu_bat') or not self.zwaifu_bat or not os.path.exists(self.zwaifu_bat):
            self.log("Z-Waifu batch file not set or does not exist.")
            if hasattr(self, 'process_status_vars') and 'Z-Waifu' in self.process_status_vars:
                self.process_status_vars['Z-Waifu'].set("Error")
            return
        try:
            self.zwaifu_proc = subprocess.Popen([self.zwaifu_bat], cwd=os.path.dirname(self.zwaifu_bat), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.zwaifu_start_time = time.time()
            self.zwaifu_monitoring = True
            self.log(f"Z-Waifu launched: {self.zwaifu_bat}")
            if hasattr(self, 'process_status_vars') and 'Z-Waifu' in self.process_status_vars:
                self.process_status_vars['Z-Waifu'].set("Running")
            
            def read_output():
                try:
                    for line in self.zwaifu_proc.stdout:
                        if hasattr(self, 'zwaifu_output'):
                            self.zwaifu_output.config(state='normal')
                            self.zwaifu_output.insert(tk.END, line)
                            self.zwaifu_output.see(tk.END)
                            self.zwaifu_output.config(state='disabled')
                except Exception as e:
                    self.log(f"Error reading Z-Waifu output: {e}")
                finally:
                    self.zwaifu_monitoring = False
                    if self.zwaifu_proc and self.zwaifu_proc.poll() is not None:
                        if hasattr(self, 'process_status_vars') and 'Z-Waifu' in self.process_status_vars:
                            self.process_status_vars['Z-Waifu'].set("Stopped")
                        self.log("Z-Waifu process exited")
            
            threading.Thread(target=read_output, daemon=True).start()
            
            def update_uptime():
                while self.zwaifu_monitoring and hasattr(self, 'zwaifu_start_time'):
                    elapsed = int(time.time() - self.zwaifu_start_time)
                    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                    if hasattr(self, 'zwaifu_uptime_var'):
                        self.zwaifu_uptime_var.set(f"Uptime: {h:02}:{m:02}:{s:02}")
                    time.sleep(1)
            
            threading.Thread(target=update_uptime, daemon=True).start()
            
        except Exception as e:
            self.log(f"Error launching Z-Waifu: {e}")
            if hasattr(self, 'process_status_vars') and 'Z-Waifu' in self.process_status_vars:
                self.process_status_vars['Z-Waifu'].set("Error")

    def stop_zwaifu(self):
        self.zwaifu_monitoring = False
        if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc:
            try:
                # Get the process and all its children
                parent = psutil.Process(self.zwaifu_proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Killed Z-Waifu child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to kill Z-Waifu child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Killed Z-Waifu parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill Z-Waifu parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    self.zwaifu_proc.kill()
                    self.log("Killed Z-Waifu wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill Z-Waifu wrapper process: {e}")
                
                self.log("Z-Waifu stopped.")
            except Exception as e:
                self.log(f"Error stopping Z-Waifu: {e}")
            self.zwaifu_proc = None
        if hasattr(self, 'process_status_vars') and 'Z-Waifu' in self.process_status_vars:
            self.process_status_vars['Z-Waifu'].set("Stopped")
        if hasattr(self, 'zwaifu_uptime_var'):
            self.zwaifu_uptime_var.set("Uptime: 00:00:00")

    def launch_rvc(self):
        self.stop_rvc()
        if not self.rvc_bat or not os.path.exists(self.rvc_bat):
            self.log("RVC batch file not set or does not exist.")
            return
        try:
            self.rvc_proc = subprocess.Popen([self.rvc_bat], cwd=os.path.dirname(self.rvc_bat), shell=True)
            self.log(f"RVC launched: {self.rvc_bat}")
        except Exception as e:
            self.log(f"Error launching RVC: {e}")

    def stop_rvc(self):
        if hasattr(self, 'rvc_proc') and self.rvc_proc:
            try:
                self.rvc_proc.terminate()
                self.rvc_proc.wait(timeout=5)
                self.log("RVC stopped.")
            except Exception as e:
                self.log(f"Error stopping RVC: {e}")
            self.rvc_proc = None

    def restart_rvc(self):
        self.stop_rvc()
        self.launch_rvc()

    def create_logs_tab(self):
        logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(logs_tab, text="Logs")

        # Log display
        self.logs_text = scrolledtext.ScrolledText(logs_tab, state='disabled', font=("Consolas", 9))
        self.logs_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.logs_tab = logs_tab # Assign for styling
        self.style_widgets(logs_tab, '#f0f0f0', '#000000', '#ffffff', '#000000') # Style logs tab

    def refresh_logs(self):
        try:
            if not os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.write("")
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        # Show only the last 200 lines
        last_lines = lines[-200:] if len(lines) > 200 else lines
        logs = ''.join(last_lines)
        self.logs_text.configure(state='normal')
        self.logs_text.delete('1.0', tk.END)
        self.logs_text.insert(tk.END, logs)
        self.logs_text.see(tk.END)
        self.logs_text.configure(state='disabled')

    def clear_logs(self):
        try:
            if not os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.write("")
            with open(LOG_FILE, "w") as f:
                f.write("")
        except Exception:
            pass
        self.logs_text.configure(state='normal')
        self.logs_text.delete('1.0', tk.END)
        self.logs_text.configure(state='disabled')

    def open_log_file(self):
        try:
            if not os.path.exists(LOG_FILE):
                with open(LOG_FILE, "w") as f:
                    f.write("")
            os.startfile(LOG_FILE)
        except Exception as e:
            self.log(f"Error opening log file: {e}")

    def start_process(self, process):
        if not process.is_running():
            process.start()
            process.status_var.set("Running")
            process.start_btn.configure(state='disabled')
            process.stop_btn.configure(state='normal')
            process.restart_btn.configure(state='normal')
            self.log(f"Started {process.name}")

    def stop_process(self, process):
        if process.is_running():
            process.stop()
            process.status_var.set("Stopped")
            process.start_btn.configure(state='normal')
            process.stop_btn.configure(state='disabled')
            process.restart_btn.configure(state='disabled')
            self.log(f"Stopped {process.name}")

    def restart_process(self, process):
        self.stop_process(process)
        self.start_process(process)

    def start_all_processes(self):
        # This function is not used in the current implementation
        # The individual process controls are used instead
        pass

    def stop_all_processes(self):
        # Stop all running processes using the per-process controls
        self._stop_requested = True
        if hasattr(self, 'ooba_proc') and self.ooba_proc:
            try:
                self.ooba_proc.kill()
            except Exception:
                pass
            self.ooba_proc = None
        if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc:
            try:
                self.zwaifu_proc.kill()
            except Exception:
                pass
            self.zwaifu_proc = None
        self.set_status("All processes stopped.", "red")
        self.start_btn.config(state='normal')
        self.stop_all_btn.config(state='disabled')

    def on_close(self):
        # Check if any process is running
        running = any(
            status.get() == "Running" for status in getattr(self, 'process_status_vars', {}).values()
        )
        if running:
            if not messagebox.askyesno("Exit", "Some processes are still running. Stop all and exit?"):
                return
            self.stop_all_processes()
        self.root.quit()

    def browse_rvc(self):
        path = filedialog.askopenfilename(title="Select RVC batch file", filetypes=[("Batch files", "*.bat")])
        if path:
            self.rvc_bat = path
            self.rvc_path_var.set(path)
            print(f"Selected RVC batch: {path}")

    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()

    def hide_window(self, icon=None, item=None):
        self.root.withdraw()

    def log_error(self, error_message):
        try:
            with open('launcher_error.log', 'a') as log_file:
                log_file.write(f'{datetime.now()} - {error_message}\n')
        except Exception:
            pass

    # Example: wrap process start/stop in try/except
    def create_process_tab(self, name, bat_var, output_widget, status_var):
        # Refactored: now supports multiple instances with TerminalEmulator
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {}
        if name not in self.process_instance_tabs:
            self.process_instance_tabs[name] = []

        def launch_instance():
            bat_path = bat_var.get()
            if not bat_path or not os.path.exists(bat_path):
                self.log(f"{name} batch file not set or does not exist.")
                return
            args = ''  # Optionally add args support
            # Create a new tab for this instance
            instance_tab = ttk.Frame(self.notebook)
            self.notebook.add(instance_tab, text=f"{name} Instance {len(self.process_instance_tabs[name])+1}")
            self.notebook.select(instance_tab)
            # Terminal emulator
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            # Launch process
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc, bat_path)
                self.log(f"{name} instance launched: {bat_path}")
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start {name}: {e}\n", '31')
                self.log(f"[ERROR] Failed to start {name}: {e}")
            # Track instance
            self.process_instance_tabs[name].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc})

        # Main process tab for launching new instances
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=name)
        # Batch file entry and browse
        entry = ttk.Entry(tab, textvariable=bat_var, width=50)
        entry.pack(padx=10, pady=(10, 0), fill=tk.X, expand=True)
        browse_btn = ttk.Button(tab, text="Browse...", command=lambda: self.browse_batch_file(name))
        browse_btn.pack(padx=10, pady=(0, 10), anchor="w")
        # Launch new instance button
        launch_btn = ttk.Button(tab, text=f"Launch {name} Instance", command=launch_instance)
        launch_btn.pack(padx=10, pady=(0, 10), anchor="w")
        # Optionally: list running instances and allow closing them
        # ...
        self.style_widgets(tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        return tab

    def force_kill_process_by_name(self, name):
        proc = self.process_handles.get(name)
        if proc and proc.poll() is None:
            try:
                # Get the process and all its children
                parent = psutil.Process(proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Force killed child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to kill child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Force killed parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    proc.kill()
                    self.log(f"Force killed wrapper process for {name}")
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill wrapper process: {e}")
                
                self.log(f"Force killed {name} and all child processes")
            except Exception as e:
                self.log(f"[ERROR] Failed to force kill {name}: {e}")
        self.process_status_vars[name].set("Stopped")
        self.process_controls[name][0].config(state='normal')
        self.process_controls[name][1].config(state='disabled')
        self.process_controls[name][2].config(state='disabled')
        self.process_controls[name][3].config(state='disabled')
        self.process_handles[name] = None

    def force_kill_all_processes(self):
        for name in self.process_handles:
            self.force_kill_process_by_name(name)
        
        # Also kill any remaining processes by name patterns
        self.force_kill_by_name_patterns()
        
        self.set_status("All processes force killed.", "red")
        self.start_btn.config(state='normal')
        self.stop_all_btn.config(state='disabled')

    def force_kill_by_name_patterns(self):
        """Kill processes by name patterns for common AI/ML applications"""
        patterns = [
            'python.exe', 'pythonw.exe', 'conda.exe', 'pip.exe',
            'nvidia-smi.exe', 'cuda.exe', 'tensorrt.exe',
            'ollama.exe', 'ollama',
            'node.exe', 'npm.exe', 'yarn.exe',
            'java.exe', 'javaw.exe',
            'gradio', 'streamlit', 'flask', 'django',
            'oobabooga', 'text-generation-webui',
            'z-waif', 'zwaifu', 'waifu',
            'rvc', 'voice', 'tts', 'stt'
        ]
        
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                
                for pattern in patterns:
                    if pattern.lower() in proc_name or pattern.lower() in cmdline:
                        try:
                            proc.kill()
                            self.log(f"Force killed process by pattern: {proc.info['name']} (PID: {proc.info['pid']})")
                            killed_count += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if killed_count > 0:
            self.log(f"Force killed {killed_count} additional processes by name patterns")

    def setup_process_tabs(self):
        # Create output widgets, status vars, and process handles for each process
        self.ooba_output = scrolledtext.ScrolledText(self.notebook, state='disabled', font=("Consolas", 9))
        self.zwaifu_output = scrolledtext.ScrolledText(self.notebook, state='disabled', font=("Consolas", 9))
        self.ollama_output = scrolledtext.ScrolledText(self.notebook, state='disabled', font=("Consolas", 9))
        self.rvc_output = scrolledtext.ScrolledText(self.notebook, state='disabled', font=("Consolas", 9))
        self.process_status_vars = {
            "Oobabooga": tk.StringVar(value="Stopped"),
            "Z-Waifu": tk.StringVar(value="Stopped"),
            # "RVC": tk.StringVar(value="Stopped")  # Remove generic RVC process tab
        }
        self.process_bat_vars = {
            "Oobabooga": tk.StringVar(value=self.ooba_bat or ""),
            "Z-Waifu": tk.StringVar(value=self.zwaifu_bat or ""),
            # "RVC": tk.StringVar(value=self.rvc_bat or "")  # Remove generic RVC process tab
        }
        self.process_controls = {}
        self.process_handles = {"Oobabooga": None, "Z-Waifu": None}  # Remove RVC from generic process handles
        # Create tabs for each process
        self.create_process_tab("Oobabooga", self.process_bat_vars["Oobabooga"], self.ooba_output, self.process_status_vars["Oobabooga"])
        self.create_process_tab("Z-Waifu", self.process_bat_vars["Z-Waifu"], self.zwaifu_output, self.process_status_vars["Z-Waifu"])
        # self.create_process_tab("RVC", self.process_bat_vars["RVC"], self.rvc_output, self.process_status_vars["RVC"])  # Remove this line

    def start_process_advanced(self, name, bat_var, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget):
        import threading, time
        
        # Ensure name is a string, not a StringVar
        if hasattr(name, 'get'):
            name = name.get()
        elif not isinstance(name, str):
            name = str(name)
        
        # Create a local copy to avoid modifying the original parameter
        process_name = name
        
        self.stop_process_advanced(process_name, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var)
        
        bat_path = bat_var.get()
        args = args_var.get().strip()
        
        if not bat_path or not os.path.exists(bat_path):
            status_var.set("Error: Batch not set")
            status_label.config(foreground="red")
            self.log(f"{process_name} batch file not set or does not exist.")
            return
        
        try:
            output_widget.config(state='normal')
            output_widget.delete('1.0', tk.END)
            output_widget.config(state='disabled')
            
            # Launch in visible CMD window with output capture
            if args:
                full_cmd = f'"{bat_path}" {args}'
            else:
                full_cmd = f'"{bat_path}"'
            
            # Create a wrapper script that captures output while showing CMD window
            wrapper_script = f'''@echo off
title {process_name} - Launcher Output
echo Starting {process_name}...
echo Command: {full_cmd}
echo.
{full_cmd}
echo.
echo {process_name} process ended.
pause
'''
            
            # Write wrapper script to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
                f.write(wrapper_script)
                wrapper_path = f.name
            
            # Launch the wrapper script in visible CMD window
            proc = subprocess.Popen(
                ['cmd.exe', '/c', 'start', 'cmd.exe', '/k', wrapper_path],
                cwd=os.path.dirname(bat_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            setattr(self, f"{process_name.lower()}_proc", proc)
            
            status_var.set("Running")
            status_label.config(foreground="green")
            pid_var.set(f"PID: {proc.pid}")
            
            start_time = time.time()
            self.log(f"{process_name} launched: {' '.join(cmd)}")
            
            monitoring = {'active': True}
            
            # Add initial status to GUI
            output_widget.config(state='normal')
            output_widget.insert(tk.END, f"Starting {process_name}...\n")
            output_widget.insert(tk.END, f"Command: {full_cmd}\n")
            output_widget.insert(tk.END, f"PID: {proc.pid}\n")
            output_widget.insert(tk.END, f"CMD window opened with title: {process_name} - Launcher Output\n")
            output_widget.insert(tk.END, f"Process is running in visible CMD window.\n")
            output_widget.insert(tk.END, f"Check the CMD window for detailed output.\n\n")
            output_widget.see(tk.END)
            output_widget.config(state='disabled')
            
            # Print to console for debugging
            print(f"[{process_name}] Starting {process_name}...")
            print(f"[{process_name}] Command: {full_cmd}")
            print(f"[{process_name}] PID: {proc.pid}")
            print(f"[{process_name}] CMD window opened with title: {process_name} - Launcher Output")
            print(f"[{process_name}] Process is running in visible CMD window.")
            print(f"[{process_name}] Check the CMD window for detailed output.")
            
            def monitor_process():
                try:
                    while proc.poll() is None:
                        time.sleep(1)
                    
                    # Process ended
                    monitoring['active'] = False
                    status_var.set("Stopped")
                    status_label.config(foreground="red")
                    pid_var.set("PID: -")
                    cpu_var.set("CPU: -%")
                    mem_var.set("Mem: - MB")
                    
                    # Add final status to GUI
                    output_widget.config(state='normal')
                    output_widget.insert(tk.END, f"{process_name} process ended.\n")
                    output_widget.see(tk.END)
                    output_widget.config(state='disabled')
                    
                    print(f"[{process_name}] Process ended.")
                    
                    if auto_restart_var.get():
                        self.log(f"{process_name} exited unexpectedly. Auto-restarting...")
                        messagebox.showinfo(f"{process_name} Auto-Restart", f"{process_name} exited unexpectedly. Auto-restarting...")
                        self.start_process_advanced(process_name, bat_var, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget)
                        
                except Exception as e:
                    self.log(f"Error monitoring {process_name}: {e}")
                    monitoring['active'] = False
            
            threading.Thread(target=monitor_process, daemon=True).start()
            
            def update_monitor():
                try:
                    p = psutil.Process(proc.pid)
                except Exception:
                    p = None
                
                while monitoring['active'] and proc.poll() is None:
                    elapsed = int(time.time() - start_time)
                    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                    uptime_var.set(f"Uptime: {h:02}:{m:02}:{s:02}")
                    
                    if p:
                        try:
                            cpu = p.cpu_percent(interval=0.5)
                            mem = p.memory_info().rss / (1024*1024)
                            cpu_var.set(f"CPU: {cpu:.1f}%")
                            mem_var.set(f"Mem: {mem:.1f} MB")
                        except Exception:
                            cpu_var.set("CPU: -%")
                            mem_var.set("Mem: - MB")
                    
                    time.sleep(0.5)
                
                uptime_var.set("Uptime: 00:00:00")
                cpu_var.set("CPU: -%")
                mem_var.set("Mem: - MB")
            
            threading.Thread(target=update_monitor, daemon=True).start()
            
        except Exception as e:
            status_var.set("Error")
            status_label.config(foreground="red")
            pid_var.set("PID: -")
            cpu_var.set("CPU: -%")
            mem_var.set("Mem: - MB")
            self.log(f"Error launching {process_name}: {e}")

    def stop_process_advanced(self, name, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var):
        # Ensure name is a string, not a StringVar
        if hasattr(name, 'get'):
            name = name.get()
        elif not isinstance(name, str):
            name = str(name)
        
        proc = getattr(self, f"{name.lower()}_proc", None)
        if proc:
            try:
                # Kill the wrapper process and all its children
                parent = psutil.Process(proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Killed {name} child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to kill {name} child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Killed {name} parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill {name} parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    proc.kill()
                    self.log(f"Killed {name} wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill {name} wrapper process: {e}")
                
                self.log(f"{name} stopped.")
            except Exception as e:
                self.log(f"Error stopping {name}: {e}")
            setattr(self, f"{name.lower()}_proc", None)
        
        status_var.set("Stopped")
        status_label.config(foreground="red")
        pid_var.set("PID: -")
        uptime_var.set("Uptime: 00:00:00")
        cpu_var.set("CPU: -%")
        mem_var.set("Mem: - MB")

    def restart_process_advanced(self, name, bat_var, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget):
        # Ensure name is a string, not a StringVar
        if hasattr(name, 'get'):
            name = name.get()
        elif not isinstance(name, str):
            name = str(name)
        
        # Create a local copy to avoid modifying the original parameter
        process_name = name
        
        self.stop_process_advanced(process_name, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var)
        self.start_process_advanced(process_name, bat_var, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget)

    def force_kill_process_advanced(self, name, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var):
        """Force kill process and all its child processes"""
        # Ensure name is a string, not a StringVar
        if hasattr(name, 'get'):
            name = name.get()
        elif not isinstance(name, str):
            name = str(name)
        
        proc = getattr(self, f"{name.lower()}_proc", None)
        if proc and proc.poll() is None:
            try:
                # Get the process and all its children
                parent = psutil.Process(proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Force killed {name} child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to force kill {name} child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Force killed {name} parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to force kill {name} parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    proc.kill()
                    self.log(f"Force killed {name} wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to force kill {name} wrapper process: {e}")
                
                self.log(f"Force killed {name} and all child processes")
            except Exception as e:
                self.log(f"[ERROR] Failed to force kill {name}: {e}")
        
        setattr(self, f"{name.lower()}_proc", None)
        status_var.set("Stopped")
        status_label.config(foreground="red")
        pid_var.set("PID: -")
        uptime_var.set("Uptime: 00:00:00")
        cpu_var.set("CPU: -%")
        mem_var.set("Mem: - MB")

    def start_process_by_name(self, name):
        """Legacy function for backward compatibility"""
        try:
            # Prevent duplicate launches
            if self.process_handles.get(name) and self.process_handles[name].poll() is None:
                messagebox.showinfo("Already Running", f"{name} is already running.")
                return
            bat_path = self.process_bat_vars[name].get()
            if not bat_path or not os.path.exists(bat_path):
                messagebox.showerror("Batch File Not Found", f"Please select a valid batch file for {name}.")
                return
            output_widget = {
                "Oobabooga": self.ooba_output,
                "Z-Waifu": self.zwaifu_output,
                "Ooba-LLaMA": self.ollama_output,
                "RVC": self.rvc_output
            }[name]
            output_widget.configure(state='normal')
            output_widget.delete(1.0, tk.END)
            output_widget.configure(state='disabled')
            
            import subprocess, threading
            def run_proc():
                try:
                    # Execute batch file in visible CMD window
                    cmd = ["cmd.exe", "/c", "start", "cmd.exe", "/k", bat_path]
                    proc = subprocess.Popen(
                        cmd,
                        cwd=os.path.dirname(bat_path),
                        # Don't capture output - let it run in visible window
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    self.process_handles[name] = proc
                    self.process_status_vars[name].set("Running")
                    
                    # Store additional process info for better tracking
                    if not hasattr(self, 'process_info'):
                        self.process_info = {}
                    self.process_info[name] = {
                        'wrapper_pid': proc.pid,
                        'start_time': time.time(),
                        'bat_path': bat_path
                    }
                    
                    # Monitor process status without blocking
                    import time
                    start_time = time.time()
                    timeout = 300  # 5 minutes timeout
                    
                    while proc.poll() is None:
                        # Check for timeout
                        if time.time() - start_time > timeout:
                            proc.terminate()
                            self.process_status_vars[name].set("Timeout")
                            self.process_handles[name] = None
                            output_widget.configure(state='normal')
                            output_widget.insert(tk.END, f"\n[ERROR] {name} startup timed out after {timeout} seconds\n")
                            output_widget.configure(state='disabled')
                            return
                        time.sleep(1)  # Check every second
                    
                    # Process finished
                    return_code = proc.returncode
                    if return_code == 0:
                        self.process_status_vars[name].set("Stopped")
                        output_widget.configure(state='normal')
                        output_widget.insert(tk.END, f"\n[{name}] Process completed successfully\n")
                        output_widget.configure(state='disabled')
                    else:
                        self.process_status_vars[name].set("Error")
                        output_widget.configure(state='normal')
                        output_widget.insert(tk.END, f"\n[{name}] Process failed with return code {return_code}\n")
                        output_widget.configure(state='disabled')
                    
                    self.process_handles[name] = None
                    
                except Exception as e:
                    self.process_status_vars[name].set("Error")
                    self.process_handles[name] = None
                    output_widget.configure(state='normal')
                    output_widget.insert(tk.END, f"\n[ERROR] Failed to start {name}: {e}\n")
                    output_widget.configure(state='disabled')
                    messagebox.showerror("Process Error", f"Failed to start {name}: {e}")
                    self.log_error(str(e))
            
            threading.Thread(target=run_proc, daemon=True).start()
            self.process_controls[name][0].config(state='disabled')
            self.process_controls[name][1].config(state='normal')
            self.process_controls[name][2].config(state='normal')
            self.process_controls[name][3].config(state='normal') # Enable force kill
            self.log(f"Started {name}")
        except Exception as e:
            self.process_status_vars[name].set("Error")
            messagebox.showerror("Process Error", f"Failed to start {name}: {e}")
            self.log_error(str(e))

    def stop_process_by_name(self, name):
        try:
            proc = self.process_handles.get(name)
            if proc and proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
                self.log(f"Stopped {name}")
            self.process_status_vars[name].set("Stopped")
            self.process_controls[name][0].config(state='normal')
            self.process_controls[name][1].config(state='disabled')
            self.process_controls[name][2].config(state='disabled')
            self.process_controls[name][3].config(state='disabled') # Disable force kill
            self.process_handles[name] = None
        except Exception as e:
            self.process_status_vars[name].set("Error")
            messagebox.showerror("Process Error", f"Failed to stop {name}: {e}")
            self.log_error(str(e))

    def restart_process_by_name(self, name):
        self.stop_process_by_name(name)
        self.start_process_by_name(name)

    def stop_all_processes(self):
        # Stop all running processes using the per-process controls
        self._stop_requested = True
        if hasattr(self, 'ooba_proc') and self.ooba_proc:
            try:
                self.ooba_proc.kill()
            except Exception:
                pass
            self.ooba_proc = None
        if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc:
            try:
                self.zwaifu_proc.kill()
            except Exception:
                pass
            self.zwaifu_proc = None
            
        # Also force kill any processes managed by the process tabs
        for name in self.process_status_vars:
            if self.process_status_vars[name].get() == "Running":
                self.force_kill_process_by_name(name)
        
        # Kill any remaining processes by name patterns
        self.force_kill_by_name_patterns()
        
        self.set_status("All processes stopped.", "red")
        self.start_btn.config(state='normal')
        self.stop_all_btn.config(state='disabled')

    def on_close(self):
        running = any(
            self.process_status_vars[name].get() == "Running" for name in self.process_status_vars
        )
        if running:
            if not messagebox.askyesno("Exit", "Some processes are still running. Stop all and exit?"):
                return
            self.stop_all_processes()
        self.root.quit()

    def browse_batch_file(self, name):
        path = filedialog.askopenfilename(title=f"Select {name} batch file", filetypes=[("Batch files", "*.bat")])
        if path:
            self.process_bat_vars[name].set(path)
            print(f"Selected {name} batch: {path}")

    def auto_detect_batch_files(self):
        """
        Auto-detect default batch files for Oobabooga, Z-Waifu, Ollama, and RVC if not already set.
        Also scan the project root for .bat files and offer them as options if found.
        Sets the corresponding attributes and updates GUI variables if found.
        """
        # Scan project root for .bat files
        root_bats = glob.glob(os.path.join(PROJECT_ROOT, '*.bat'))

        # Oobabooga - look for start_windows.bat in text-generation-webui-main
        if not self.ooba_bat:
            ooba_path = find_batch_file("start_windows.bat")
            if not ooba_path and root_bats:
                ooba_path = None  # No popup, user sets in settings
            if ooba_path:
                self.ooba_bat = ooba_path
                if hasattr(self, 'ooba_path_var') and self.ooba_path_var:
                    self.ooba_path_var.set(ooba_path)
                self.log(f"[Auto-Detect] Oobabooga batch found: {ooba_path}")
            else:
                self.log("[Auto-Detect] Oobabooga batch not found.")
        
        # Z-Waifu - look for startup.bat in z-waif-1.14-R4
        if not self.zwaifu_bat:
            zwaifu_path = find_batch_file("startup.bat")
            if not zwaifu_path and root_bats:
                zwaifu_path = None  # No popup, user sets in settings
            if zwaifu_path:
                self.zwaifu_bat = zwaifu_path
                if hasattr(self, 'zwaifu_path_var') and self.zwaifu_path_var:
                    self.zwaifu_path_var.set(zwaifu_path)
                self.log(f"[Auto-Detect] Z-Waifu batch found: {zwaifu_path}")
            else:
                self.log("[Auto-Detect] Z-Waifu batch not found.")
        
        # Ollama - look for various possible batch files
        if not self.ollama_bat:
            ollama_names = ["ollama.bat", "start_ollama.bat", "launch_ollama.bat"]
            ollama_path = None
            for name in ollama_names:
                ollama_path = find_batch_file(name)
                if ollama_path:
                    break
            if not ollama_path and root_bats:
                ollama_path = None  # No popup, user sets in settings
            if ollama_path:
                self.ollama_bat = ollama_path
                if hasattr(self, 'ollama_path_var') and self.ollama_path_var:
                    self.ollama_path_var.set(ollama_path)
                self.log(f"[Auto-Detect] Ollama batch found: {ollama_path}")
            else:
                self.log("[Auto-Detect] Ollama batch not found.")
        
        # RVC - look for various possible batch files
        if not self.rvc_bat:
            rvc_names = ["rvc.bat", "start_rvc.bat", "launch_rvc.bat", "rvc_server.bat"]
            rvc_path = None
            for name in rvc_names:
                rvc_path = find_batch_file(name)
                if rvc_path:
                    break
            if not rvc_path and root_bats:
                rvc_path = None  # No popup, user sets in settings
            if rvc_path:
                self.rvc_bat = rvc_path
                if hasattr(self, 'rvc_path_var') and self.rvc_path_var:
                    self.rvc_path_var.set(rvc_path)
                self.log(f"[Auto-Detect] RVC batch found: {rvc_path}")
            else:
                self.log("[Auto-Detect] RVC batch not found.")
        
        # Additional batch files that might be useful
        additional_batches = {
            "launch_ooba_zwaifu.bat": "Combined Launcher",
            "setup_venv_and_run_launcher.bat": "Setup Script",
            "quick-message.bat": "Quick Message",
            "startup-Install.bat": "Z-Waifu Install"
        }
        
        for batch_name, description in additional_batches.items():
            batch_path = find_batch_file(batch_name)
            if batch_path:
                self.log(f"[Auto-Detect] {description} batch found: {batch_path}")

    def launch_main_program(self):
        """
        Open a file dialog to select a Python script, run it, and display output in the main_program_output widget.
        """
        path = filedialog.askopenfilename(title="Select Python script to run", filetypes=[("Python files", "*.py")])
        if not path:
            return
        try:
            if hasattr(self, 'main_program_output') and self.main_program_output:
                self.main_program_output.config(state='normal')
                self.main_program_output.delete(1.0, tk.END)
            proc = subprocess.Popen([sys.executable, path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                if hasattr(self, 'main_program_output') and self.main_program_output:
                    self.main_program_output.insert(tk.END, line)
                    self.main_program_output.see(tk.END)
                else:
                    print(line, end="")
            if hasattr(self, 'main_program_output') and self.main_program_output:
                self.main_program_output.config(state='disabled')
        except Exception as e:
            msg = f"Error running main program: {e}"
            if hasattr(self, 'main_program_output') and self.main_program_output:
                self.main_program_output.config(state='normal')
                self.main_program_output.insert(tk.END, msg + "\n")
                self.main_program_output.config(state='disabled')
            else:
                print(msg)

    def check_oobabooga_status(self):
        """
        Check if Oobabooga is running and accessible on its expected port.
        Returns True if accessible, False otherwise.
        """
        try:
            # Try common Oobabooga ports
            ports = [7860, 5000, 8080]
            for port in ports:
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=2):
                        return True
                except (socket.timeout, ConnectionRefusedError):
                    continue
            return False
        except Exception:
            return False

    def update_process_status(self):
        """
        Periodically update process status based on actual running state.
        """
        if hasattr(self, 'process_status_vars'):
            for name, status_var in self.process_status_vars.items():
                if name == "Oobabooga" and status_var.get() == "Running":
                    if not self.check_oobabooga_status():
                        # Oobabooga shows as running but isn't accessible
                        status_var.set("Starting...")
                # Add similar checks for other processes as needed
        # Schedule next update
        self.root.after(5000, self.update_process_status)  # Check every 5 seconds

    def toggle_theme(self):
        if self._dark_mode:
            # Currently in dark mode, switch to light mode
            self.set_light_mode()
            # Show moon emoji (indicating you can click to go to dark mode)
            self.theme_toggle_btn.config(text="☽")
        else:
            # Currently in light mode, switch to dark mode
            self.set_dark_mode()
            # Show sun emoji (indicating you can click to go to light mode)
            self.theme_toggle_btn.config(text="☀")

        self._dark_mode = not self._dark_mode

    def create_rvc_tab(self):
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {}
        if 'RVC' not in self.process_instance_tabs:
            self.process_instance_tabs['RVC'] = []

        rvc_tab = ttk.Frame(self.notebook)
        self.notebook.add(rvc_tab, text="RVC")

        # Batch file selection
        ttk.Label(rvc_tab, text="RVC batch:").pack(anchor=tk.W, padx=10, pady=(10,0))
        self.rvc_path_var = tk.StringVar(value=self.rvc_bat if self.rvc_bat else "NOT FOUND")
        ttk.Entry(rvc_tab, textvariable=self.rvc_path_var, state='readonly').pack(fill=tk.X, padx=10, expand=True)
        ttk.Button(rvc_tab, text="Browse...", command=self.browse_rvc).pack(anchor=tk.E, padx=10, pady=(0,10))

        # Launch new instance button
        def launch_rvc_instance():
            bat_path = self.rvc_path_var.get()
            if not bat_path or not os.path.exists(bat_path):
                self.log("RVC batch file not set or does not exist.")
                return
            # Create a new tab for this instance
            instance_tab = ttk.Frame(self.notebook)
            self.notebook.add(instance_tab, text=f"RVC Instance {len(self.process_instance_tabs['RVC'])+1}")
            self.notebook.select(instance_tab)
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc)
                self.log(f"RVC instance launched: {bat_path}")
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start RVC: {e}\n", '31')
                self.log(f"[ERROR] Failed to start RVC: {e}")
            self.process_instance_tabs['RVC'].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc})

        ttk.Button(rvc_tab, text="Launch RVC Instance", command=launch_rvc_instance).pack(padx=10, pady=(0, 10), anchor="w")
        self.style_widgets(rvc_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.rvc_tab = rvc_tab

    def launch_rvc_tab(self):
        import threading, time
        self.stop_rvc_tab()
        bat_path = self.rvc_path_var.get()
        args = self.rvc_args_var.get().strip()
        if not bat_path or not os.path.exists(bat_path):
            self.rvc_status_var.set("Error: Batch not set")
            self.rvc_status_label.config(foreground="red")
            self.log("RVC batch file not set or does not exist.")
            return
        try:
            self.rvc_output.config(state='normal')
            self.rvc_output.delete('1.0', tk.END)
            self.rvc_output.config(state='disabled')
            # Launch in visible CMD window with output capture
            if args:
                full_cmd = f'"{bat_path}" {args}'
            else:
                full_cmd = f'"{bat_path}"'
            
            # Create a wrapper script that captures output while showing CMD window
            wrapper_script = f'''@echo off
title RVC - Launcher Output
echo Starting RVC...
echo Command: {full_cmd}
echo.
{full_cmd}
echo.
echo RVC process ended.
pause
'''
            
            # Write wrapper script to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
                f.write(wrapper_script)
                wrapper_path = f.name
            
            # Launch the wrapper script in visible CMD window
            self.rvc_proc = subprocess.Popen(
                ['cmd.exe', '/c', 'start', 'cmd.exe', '/k', wrapper_path],
                cwd=os.path.dirname(bat_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.rvc_status_var.set("Running")
            self.rvc_status_label.config(foreground="green")
            self.rvc_pid_var.set(f"PID: {self.rvc_proc.pid}")
            self._rvc_start_time = time.time()
            self._rvc_monitoring = True
            self.log(f"RVC launched: {' '.join(cmd)}")
            
            # Add initial status to GUI
            self.rvc_output.config(state='normal')
            self.rvc_output.insert(tk.END, f"Starting RVC...\n")
            self.rvc_output.insert(tk.END, f"Command: {full_cmd}\n")
            self.rvc_output.insert(tk.END, f"PID: {self.rvc_proc.pid}\n")
            self.rvc_output.insert(tk.END, f"CMD window opened with title: RVC - Launcher Output\n")
            self.rvc_output.insert(tk.END, f"Process is running in visible CMD window.\n")
            self.rvc_output.insert(tk.END, f"Check the CMD window for detailed output.\n\n")
            self.rvc_output.see(tk.END)
            self.rvc_output.config(state='disabled')
            
            # Print to console for debugging
            print(f"[RVC] Starting RVC...")
            print(f"[RVC] Command: {full_cmd}")
            print(f"[RVC] PID: {self.rvc_proc.pid}")
            print(f"[RVC] CMD window opened with title: RVC - Launcher Output")
            print(f"[RVC] Process is running in visible CMD window.")
            print(f"[RVC] Check the CMD window for detailed output.")
            
            def monitor_process():
                try:
                    while self.rvc_proc.poll() is None:
                        time.sleep(1)
                    
                    # Process ended
                    self._rvc_monitoring = False
                    self.rvc_status_var.set("Stopped")
                    self.rvc_status_label.config(foreground="red")
                    self.rvc_pid_var.set("PID: -")
                    self.rvc_cpu_var.set("CPU: -%")
                    self.rvc_mem_var.set("Mem: - MB")
                    
                    # Add final status to GUI
                    self.rvc_output.config(state='normal')
                    self.rvc_output.insert(tk.END, f"RVC process ended.\n")
                    self.rvc_output.see(tk.END)
                    self.rvc_output.config(state='disabled')
                    
                    print(f"[RVC] Process ended.")
                    
                    if self.rvc_auto_restart.get():
                        self.log("RVC exited unexpectedly. Auto-restarting...")
                        messagebox.showinfo("RVC Auto-Restart", "RVC exited unexpectedly. Auto-restarting...")
                        self.launch_rvc_tab()
                        
                except Exception as e:
                    self.log(f"Error monitoring RVC: {e}")
                    self._rvc_monitoring = False
            
            threading.Thread(target=monitor_process, daemon=True).start()
            
            def update_monitor():
                try:
                    p = psutil.Process(self.rvc_proc.pid)
                except Exception:
                    p = None
                
                while self._rvc_monitoring and self._rvc_start_time and self.rvc_proc.poll() is None:
                    elapsed = int(time.time() - self._rvc_start_time)
                    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                    self.rvc_uptime_var.set(f"Uptime: {h:02}:{m:02}:{s:02}")
                    
                    if p:
                        try:
                            cpu = p.cpu_percent(interval=0.5)
                            mem = p.memory_info().rss / (1024*1024)
                            self.rvc_cpu_var.set(f"CPU: {cpu:.1f}%")
                            self.rvc_mem_var.set(f"Mem: {mem:.1f} MB")
                        except Exception:
                            self.rvc_cpu_var.set("CPU: -%")
                            self.rvc_mem_var.set("Mem: - MB")
                    
                    time.sleep(0.5)
                
                self.rvc_uptime_var.set("Uptime: 00:00:00")
                self.rvc_cpu_var.set("CPU: -%")
                self.rvc_mem_var.set("Mem: - MB")
            
            threading.Thread(target=update_monitor, daemon=True).start()
            
        except Exception as e:
            self.rvc_status_var.set("Error")
            self.rvc_status_label.config(foreground="red")
            self.rvc_pid_var.set("PID: -")
            self.rvc_cpu_var.set("CPU: -%")
            self.rvc_mem_var.set("Mem: - MB")
            self.log(f"Error launching RVC: {e}")

    def stop_rvc_tab(self):
        self._rvc_monitoring = False
        if hasattr(self, 'rvc_proc') and self.rvc_proc:
            try:
                # Kill the wrapper process and all its children
                parent = psutil.Process(self.rvc_proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Killed RVC child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to kill RVC child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Killed RVC parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill RVC parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    self.rvc_proc.kill()
                    self.log(f"Killed RVC wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to kill RVC wrapper process: {e}")
                
                self.log("RVC stopped.")
            except Exception as e:
                self.log(f"Error stopping RVC: {e}")
            self.rvc_proc = None
        self.rvc_status_var.set("Stopped")
        self.rvc_status_label.config(foreground="red")
        self.rvc_pid_var.set("PID: -")
        self.rvc_uptime_var.set("Uptime: 00:00:00")
        self.rvc_cpu_var.set("CPU: -%")
        self.rvc_mem_var.set("Mem: - MB")

    def restart_rvc_tab(self):
        self.stop_rvc_tab()
        self.launch_rvc_tab()

    def force_kill_rvc_tab(self):
        """Force kill RVC and all its child processes"""
        self._rvc_monitoring = False
        if hasattr(self, 'rvc_proc') and self.rvc_proc:
            try:
                # Get the process and all its children
                parent = psutil.Process(self.rvc_proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                        self.log(f"Force killed RVC child process {child.pid} ({child.name()})")
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        self.log(f"[ERROR] Failed to force kill RVC child process {child.pid}: {e}")
                
                # Kill the parent process
                try:
                    parent.kill()
                    self.log(f"Force killed RVC parent process {parent.pid} ({parent.name()})")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:
                    self.log(f"[ERROR] Failed to force kill RVC parent process {parent.pid}: {e}")
                
                # Also kill the wrapper process
                try:
                    self.rvc_proc.kill()
                    self.log("Force killed RVC wrapper process")
                except Exception as e:
                    self.log(f"[ERROR] Failed to force kill RVC wrapper process: {e}")
                
                self.log("RVC force killed.")
            except Exception as e:
                self.log(f"Error force killing RVC: {e}")
            self.rvc_proc = None
        
        self.rvc_status_var.set("Stopped")
        self.rvc_status_label.config(foreground="red")
        self.rvc_pid_var.set("PID: -")
        self.rvc_uptime_var.set("Uptime: 00:00:00")
        self.rvc_cpu_var.set("CPU: -%")
        self.rvc_mem_var.set("Mem: - MB")

    def create_process_tab_advanced(self, name, bat_var, output_widget, status_var):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=name)
        # Batch file entry and browse
        entry = ttk.Entry(tab, textvariable=bat_var, width=50)
        entry.pack(padx=10, pady=(10, 0), fill=tk.X, expand=True)
        browse_btn = ttk.Button(tab, text="Browse...", command=lambda: self.browse_batch_file(name))
        browse_btn.pack(padx=10, pady=(0, 10), anchor="w")
        # Custom arguments
        args_var = tk.StringVar()
        ttk.Label(tab, text="Custom arguments:").pack(anchor=tk.W, padx=10, pady=(5,0))
        ttk.Entry(tab, textvariable=args_var).pack(fill=tk.X, padx=10, expand=True)
        # Auto-restart checkbox
        auto_restart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text="Auto-Restart on Crash/Exit", variable=auto_restart_var).pack(anchor=tk.W, padx=10, pady=(0,5))
        # Status label
        status_label = ttk.Label(tab, textvariable=status_var, foreground="red")
        status_label.pack(anchor=tk.W, padx=10, pady=(0,5))
        # Process monitoring
        monitor_frame = ttk.Frame(tab)
        monitor_frame.pack(anchor=tk.W, padx=10, pady=(0,5))
        pid_var = tk.StringVar(value="PID: -")
        uptime_var = tk.StringVar(value="Uptime: 00:00:00")
        cpu_var = tk.StringVar(value="CPU: -%")
        mem_var = tk.StringVar(value="Mem: - MB")
        ttk.Label(monitor_frame, textvariable=pid_var).pack(side=tk.LEFT, padx=(0,10))
        ttk.Label(monitor_frame, textvariable=uptime_var).pack(side=tk.LEFT, padx=(0,10))
        ttk.Label(monitor_frame, textvariable=cpu_var).pack(side=tk.LEFT, padx=(0,10))
        ttk.Label(monitor_frame, textvariable=mem_var).pack(side=tk.LEFT)
        # Process control
        control_frame = ttk.Frame(tab)
        control_frame.pack(padx=10, pady=10)
        ttk.Button(control_frame, text="Start", command=lambda: launch_fn(args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget, name)).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(control_frame, text="Stop", command=lambda: stop_fn(status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Restart", command=lambda: restart_fn(args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget, name)).pack(side=tk.LEFT, padx=(5,0))
        # Output log
        output_widget.pack(in_=tab, padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        self.style_widgets(tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        return tab

    def launch_process_advanced(self, bat_var, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget, name):
        import threading, time
        
        # Ensure name is a string, not a StringVar
        if hasattr(name, 'get'):
            name = name.get()
        elif not isinstance(name, str):
            name = str(name)
        
        # Create a local copy to avoid modifying the original parameter
        process_name = name
        
        self.stop_process_advanced(process_name, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var)
        bat_path = bat_var.get()
        args = args_var.get().strip()
        if not bat_path or not os.path.exists(bat_path):
            status_var.set("Error: Batch not set")
            status_label.config(foreground="red")
            self.log(f"{process_name} batch file not set or does not exist.")
            return
        try:
            output_widget.config(state='normal')
            output_widget.delete(1.0, tk.END)
            output_widget.config(state='disabled')
            # Launch in visible CMD window with output capture
            if args:
                full_cmd = f'"{bat_path}" {args}'
            else:
                full_cmd = f'"{bat_path}"'
            
            # Create a wrapper script that captures output while showing CMD window
            wrapper_script = f'''@echo off
title {process_name} - Launcher Output
echo Starting {process_name}...
echo Command: {full_cmd}
echo.
{full_cmd}
echo.
echo {process_name} process ended.
pause
'''
            
            # Write wrapper script to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
                f.write(wrapper_script)
                wrapper_path = f.name
            
            # Launch the wrapper script in visible CMD window
            proc = subprocess.Popen(
                ['cmd.exe', '/c', 'start', 'cmd.exe', '/k', wrapper_path],
                cwd=os.path.dirname(bat_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            setattr(self, f"{process_name.lower()}_proc", proc)
            status_var.set("Running")
            status_label.config(foreground="green")
            pid_var.set(f"PID: {proc.pid}")
            start_time = time.time()
            self.log(f"{process_name} launched: {full_cmd}")
            monitoring = {'active': True}
            # Add initial status to GUI
            output_widget.config(state='normal')
            output_widget.insert(tk.END, f"Starting {process_name}...\n")
            output_widget.insert(tk.END, f"Command: {full_cmd}\n")
            output_widget.insert(tk.END, f"PID: {proc.pid}\n")
            output_widget.insert(tk.END, f"CMD window opened with title: {process_name} - Launcher Output\n")
            output_widget.insert(tk.END, f"Process is running in visible CMD window.\n")
            output_widget.insert(tk.END, f"Check the CMD window for detailed output.\n\n")
            output_widget.see(tk.END)
            output_widget.config(state='disabled')
            
            # Print to console for debugging
            print(f"[{process_name}] Starting {process_name}...")
            print(f"[{process_name}] Command: {full_cmd}")
            print(f"[{process_name}] PID: {proc.pid}")
            print(f"[{process_name}] CMD window opened with title: {process_name} - Launcher Output")
            print(f"[{process_name}] Process is running in visible CMD window.")
            print(f"[{process_name}] Check the CMD window for detailed output.")
            
            def monitor_process():
                try:
                    while proc.poll() is None:
                        time.sleep(1)
                    
                    # Process ended
                    monitoring['active'] = False
                    status_var.set("Stopped")
                    status_label.config(foreground="red")
                    pid_var.set("PID: -")
                    cpu_var.set("CPU: -%")
                    mem_var.set("Mem: - MB")
                    
                    # Add final status to GUI
                    output_widget.config(state='normal')
                    output_widget.insert(tk.END, f"{process_name} process ended.\n")
                    output_widget.see(tk.END)
                    output_widget.config(state='disabled')
                    
                    print(f"[{process_name}] Process ended.")
                    
                    if auto_restart_var.get():
                        self.log(f"{process_name} exited unexpectedly. Auto-restarting...")
                        messagebox.showinfo(f"{process_name} Auto-Restart", f"{process_name} exited unexpectedly. Auto-restarting...")
                        self.launch_process_advanced(bat_var, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget, process_name)
                        
                except Exception as e:
                    self.log(f"Error monitoring {process_name}: {e}")
                    monitoring['active'] = False
            
            threading.Thread(target=monitor_process, daemon=True).start()
            def update_monitor():
                try:
                    p = psutil.Process(proc.pid)
                except Exception:
                    p = None
                while monitoring['active'] and proc.poll() is None:
                    elapsed = int(time.time() - start_time)
                    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                    uptime_var.set(f"Uptime: {h:02}:{m:02}:{s:02}")
                    if p:
                        try:
                            cpu = p.cpu_percent(interval=0.5)
                            mem = p.memory_info().rss / (1024*1024)
                            cpu_var.set(f"CPU: {cpu:.1f}%")
                            mem_var.set(f"Mem: {mem:.1f} MB")
                        except Exception:
                            cpu_var.set("CPU: -%")
                            mem_var.set("Mem: - MB")
                    time.sleep(0.5)
                uptime_var.set("Uptime: 00:00:00")
                cpu_var.set("CPU: -%")
                mem_var.set("Mem: - MB")
            threading.Thread(target=update_monitor, daemon=True).start()
        except Exception as e:
            status_var.set("Error")
            status_label.config(foreground="red")
            pid_var.set("PID: -")
            cpu_var.set("CPU: -%")
            mem_var.set("Mem: - MB")
            self.log(f"Error launching {process_name}: {e}")



    def restart_process_advanced(self, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget, name):
        # Ensure name is a string, not a StringVar
        if hasattr(name, 'get'):
            name = name.get()
        elif not isinstance(name, str):
            name = str(name)
        
        # Create a local copy to avoid modifying the original parameter
        process_name = name
        
        self.stop_process_advanced(process_name, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var)
        bat_var = self.process_bat_vars[process_name]
        self.launch_process_advanced(bat_var, args_var, auto_restart_var, status_var, status_label, pid_var, uptime_var, cpu_var, mem_var, output_widget, process_name)

    def show_tray_icon(self):
        # Show a system tray icon with a menu to restore or quit
        def on_restore(icon, item):
            self.root.after(0, self.root.deiconify)
        def on_quit(icon, item):
            icon.stop()
            self.root.after(0, self.root.quit)
        image = Image.new("RGB", (64, 64), "purple")
        menu = pystray.Menu(
            pystray.MenuItem("Restore", on_restore),
            pystray.MenuItem("Quit", on_quit)
        )
        self.tray_icon = pystray.Icon("ZLauncher", image, "ZLauncher", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_sample_image(self):
        img = Image.new("RGB", (64, 64), "purple")
        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(self.root, image=tk_img)
        label.image = tk_img  # Keep a reference!
        label.pack()
        self.log("Sample image displayed.")

    def open_github(self):
        webbrowser.open("https://github.com/Drakkadakka/zwaifu-launcher")
        self.log("Opened GitHub page.")

    def list_bat_files(self):
        files = glob.glob("*.bat")
        self.log(f"Batch files in project root: {files}")

    def list_running_processes(self):
        """List all running processes for debugging"""
        self.log("=== Running Processes ===")
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'] if proc.info['name'] else 'Unknown'
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                self.log(f"PID: {proc.info['pid']}, Name: {proc_name}, Cmd: {cmdline[:100]}...")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self.log("=== End Process List ===")

    def prompt_custom_input(self):
        from tkinter import simpledialog
        user_input = simpledialog.askstring("Custom Input", "Enter a command or message:")
        if user_input:
            self.log(f"User input: {user_input}")

    def add_demo_buttons(self):
        # Add demo buttons to the main tab for all advanced features
        if hasattr(self, 'main_tab'):
            frame = ttk.Frame(self.main_tab)
            frame.pack(padx=10, pady=10, anchor="w")
            ttk.Button(frame, text="Show Tray Icon", command=self.show_tray_icon).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="Show Sample Image", command=self.show_sample_image).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="Open GitHub", command=self.open_github).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="List .bat Files", command=self.list_bat_files).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="List Running Processes", command=self.list_running_processes).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="Send Custom Input", command=self.prompt_custom_input).pack(side=tk.LEFT, padx=5)

    # Call self.add_demo_buttons() at the end of create_main_tab

    def create_ooba_tab(self):
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {}
        if 'Oobabooga' not in self.process_instance_tabs:
            self.process_instance_tabs['Oobabooga'] = []

        ooba_tab = ttk.Frame(self.notebook)
        self.notebook.add(ooba_tab, text="Oobabooga")

        # Batch file selection
        ttk.Label(ooba_tab, text="Oobabooga batch:").pack(anchor=tk.W, padx=10, pady=(10,0))
        self.ooba_path_var = tk.StringVar(value=self.ooba_bat if self.ooba_bat else "NOT FOUND")
        ttk.Entry(ooba_tab, textvariable=self.ooba_path_var, state='readonly').pack(fill=tk.X, padx=10, expand=True)
        ttk.Button(ooba_tab, text="Browse...", command=self.browse_ooba).pack(anchor=tk.E, padx=10, pady=(0,10))

        # Launch new instance button
        def launch_ooba_instance():
            bat_path = self.ooba_path_var.get()
            if not bat_path or not os.path.exists(bat_path):
                self.log("Oobabooga batch file not set or does not exist.")
                return
            # Create a new tab for this instance
            instance_tab = ttk.Frame(self.notebook)
            self.notebook.add(instance_tab, text=f"Oobabooga Instance {len(self.process_instance_tabs['Oobabooga'])+1}")
            self.notebook.select(instance_tab)
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc)
                self.log(f"Oobabooga instance launched: {bat_path}")
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start Oobabooga: {e}\n", '31')
                self.log(f"[ERROR] Failed to start Oobabooga: {e}")
            self.process_instance_tabs['Oobabooga'].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc})

        ttk.Button(ooba_tab, text="Launch Oobabooga Instance", command=launch_ooba_instance).pack(padx=10, pady=(0, 10), anchor="w")
        self.style_widgets(ooba_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.ooba_tab = ooba_tab

    def create_zwaifu_tab(self):
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {}
        if 'Z-Waifu' not in self.process_instance_tabs:
            self.process_instance_tabs['Z-Waifu'] = []

        zwaifu_tab = ttk.Frame(self.notebook)
        self.notebook.add(zwaifu_tab, text="Z-Waifu")

        # Batch file selection
        ttk.Label(zwaifu_tab, text="Z-Waifu batch:").pack(anchor=tk.W, padx=10, pady=(10,0))
        self.zwaifu_path_var = tk.StringVar(value=self.zwaifu_bat if self.zwaifu_bat else "NOT FOUND")
        ttk.Entry(zwaifu_tab, textvariable=self.zwaifu_path_var, state='readonly').pack(fill=tk.X, padx=10, expand=True)
        ttk.Button(zwaifu_tab, text="Browse...", command=self.browse_zwaifu).pack(anchor=tk.E, padx=10, pady=(0,10))

        # Launch new instance button
        def launch_zwaifu_instance():
            bat_path = self.zwaifu_path_var.get()
            if not bat_path or not os.path.exists(bat_path):
                self.log("Z-Waifu batch file not set or does not exist.")
                return
            # Create a new tab for this instance
            instance_tab = ttk.Frame(self.notebook)
            self.notebook.add(instance_tab, text=f"Z-Waifu Instance {len(self.process_instance_tabs['Z-Waifu'])+1}")
            self.notebook.select(instance_tab)
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc, bat_path)
                self.log(f"Z-Waifu instance launched: {bat_path}")
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start Z-Waifu: {e}\n", '31')
                self.log(f"[ERROR] Failed to start Z-Waifu: {e}")
            self.process_instance_tabs['Z-Waifu'].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc})

        ttk.Button(zwaifu_tab, text="Launch Z-Waifu Instance", command=launch_zwaifu_instance).pack(padx=10, pady=(0, 10), anchor="w")
        self.style_widgets(zwaifu_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.zwaifu_tab = zwaifu_tab

    def create_instance_manager_tab(self):
        """Create a tab to manage all running instances"""
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {}
        
        instance_tab = ttk.Frame(self.notebook)
        self.notebook.add(instance_tab, text="Instance Manager")
        
        # Title and description
        title_frame = ttk.Frame(instance_tab)
        title_frame.pack(fill=tk.X, padx=10, pady=(10,5))
        ttk.Label(title_frame, text="Running Instances", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(title_frame, text="Manage all running process instances", font=("Arial", 9)).pack(anchor=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(instance_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        ttk.Button(control_frame, text="Refresh", command=self.refresh_instance_list).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(control_frame, text="Kill All", command=self.kill_all_instances).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Focus Selected", command=self.focus_selected_instance).pack(side=tk.LEFT, padx=5)
        
        # Instance list
        list_frame = ttk.LabelFrame(instance_tab, text="Running Instances")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        # Create Treeview for instance list
        columns = ('Type', 'Instance', 'Status', 'PID', 'Uptime', 'Actions')
        self.instance_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        self.instance_tree.heading('Type', text='Process Type')
        self.instance_tree.heading('Instance', text='Instance Name')
        self.instance_tree.heading('Status', text='Status')
        self.instance_tree.heading('PID', text='PID')
        self.instance_tree.heading('Uptime', text='Uptime')
        self.instance_tree.heading('Actions', text='Actions')
        
        self.instance_tree.column('Type', width=100)
        self.instance_tree.column('Instance', width=150)
        self.instance_tree.column('Status', width=80)
        self.instance_tree.column('PID', width=80)
        self.instance_tree.column('Uptime', width=100)
        self.instance_tree.column('Actions', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.instance_tree.yview)
        self.instance_tree.configure(yscrollcommand=scrollbar.set)
        
        self.instance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to focus instance
        self.instance_tree.bind('<Double-1>', self.focus_selected_instance)
        
        # Status bar
        self.instance_status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(instance_tab, textvariable=self.instance_status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0,10))
        
        self.style_widgets(instance_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.instance_manager_tab = instance_tab

    def refresh_instance_list(self):
        """Refresh the instance list"""
        # Clear existing items
        for item in self.instance_tree.get_children():
            self.instance_tree.delete(item)
        
        total_instances = 0
        
        # Iterate through all process types
        for process_type, instances in self.process_instance_tabs.items():
            for i, instance_data in enumerate(instances):
                tab = instance_data.get('tab')
                terminal = instance_data.get('terminal')
                proc = instance_data.get('proc')
                
                if proc and proc.poll() is None:
                    # Process is running
                    status = "Running"
                    try:
                        pid = proc.pid
                        # Calculate uptime
                        uptime = "Unknown"
                        if hasattr(terminal, 'start_time'):
                            elapsed = int(time.time() - terminal.start_time)
                            h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
                            uptime = f"{h:02}:{m:02}:{s:02}"
                    except Exception:
                        pid = "Unknown"
                        uptime = "Unknown"
                    
                    # Create action buttons frame
                    action_frame = ttk.Frame(self.instance_tree)
                    stop_btn = ttk.Button(action_frame, text="Stop", width=6,
                                        command=lambda p=proc, t=terminal: self.stop_instance(p, t))
                    restart_btn = ttk.Button(action_frame, text="Restart", width=6,
                                           command=lambda p=proc, t=terminal, pt=process_type, idx=i: self.restart_instance(p, t, pt, idx))
                    kill_btn = ttk.Button(action_frame, text="Kill", width=6,
                                        command=lambda p=proc, t=terminal: self.kill_instance(p, t))
                    
                    stop_btn.pack(side=tk.LEFT, padx=1)
                    restart_btn.pack(side=tk.LEFT, padx=1)
                    kill_btn.pack(side=tk.LEFT, padx=1)
                    
                    # Insert into tree
                    item = self.instance_tree.insert('', 'end', values=(
                        process_type,
                        f"{process_type} Instance {i+1}",
                        status,
                        pid,
                        uptime,
                        ""  # Actions column will be handled by button frame
                    ))
                    
                    # Store reference to action frame
                    self.instance_tree.set(item, 'Actions', '')
                    total_instances += 1
                else:
                    # Process is not running
                    status = "Stopped"
                    pid = "N/A"
                    uptime = "N/A"
                    
                    # Insert into tree
                    item = self.instance_tree.insert('', 'end', values=(
                        process_type,
                        f"{process_type} Instance {i+1}",
                        status,
                        pid,
                        uptime,
                        "Remove"
                    ))
        
        self.instance_status_var.set(f"Total instances: {total_instances}")

    def focus_selected_instance(self, event=None):
        """Focus the selected instance tab"""
        selection = self.instance_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.instance_tree.item(item, 'values')
        if not values:
            return
        
        process_type = values[0]
        instance_name = values[1]
        
        # Extract instance number
        try:
            instance_num = int(instance_name.split()[-1]) - 1
        except (ValueError, IndexError):
            return
        
        # Find the corresponding tab
        if process_type in self.process_instance_tabs:
            instances = self.process_instance_tabs[process_type]
            if 0 <= instance_num < len(instances):
                tab = instances[instance_num]['tab']
                self.notebook.select(tab)
                self.instance_status_var.set(f"Focused: {instance_name}")

    def stop_instance(self, proc, terminal):
        """Stop a specific instance"""
        try:
            if proc and proc.poll() is None:
                proc.terminate()
                self.log(f"Stopped instance (PID: {proc.pid})")
                self.instance_status_var.set("Instance stopped")
                self.refresh_instance_list()
        except Exception as e:
            self.log(f"Error stopping instance: {e}")
            self.instance_status_var.set(f"Error: {e}")

    def restart_instance(self, proc, terminal, process_type, instance_index):
        """Restart a specific instance"""
        try:
            # Stop current instance
            if proc and proc.poll() is None:
                proc.terminate()
                time.sleep(1)  # Give it time to stop
            
            # Get the batch file path
            batch_path = None
            if process_type == "Oobabooga":
                batch_path = self.ooba_bat
            elif process_type == "Z-Waifu":
                batch_path = self.zwaifu_bat
            elif process_type == "Ollama":
                batch_path = self.ollama_bat
            elif process_type == "RVC":
                batch_path = self.rvc_bat
            
            if not batch_path or not os.path.exists(batch_path):
                self.instance_status_var.set("Error: Batch file not found")
                return
            
            # Start new process
            new_proc = subprocess.Popen([batch_path], cwd=os.path.dirname(batch_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Update the instance data
            if process_type in self.process_instance_tabs:
                instances = self.process_instance_tabs[process_type]
                if 0 <= instance_index < len(instances):
                    instances[instance_index]['proc'] = new_proc
                    terminal = instances[instance_index]['terminal']
                    terminal.attach_process(new_proc)
                    terminal.start_time = time.time()
            
            self.log(f"Restarted {process_type} instance")
            self.instance_status_var.set(f"Restarted: {process_type} Instance {instance_index+1}")
            self.refresh_instance_list()
            
        except Exception as e:
            self.log(f"Error restarting instance: {e}")
            self.instance_status_var.set(f"Error: {e}")

    def kill_instance(self, proc, terminal):
        """Force kill a specific instance"""
        try:
            if proc and proc.poll() is None:
                # Kill the process and all its children
                parent = psutil.Process(proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Kill the parent process
                try:
                    parent.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Also kill the wrapper process
                try:
                    proc.kill()
                except Exception:
                    pass
                
                self.log(f"Force killed instance (PID: {proc.pid})")
                self.instance_status_var.set("Instance force killed")
                self.refresh_instance_list()
        except Exception as e:
            self.log(f"Error killing instance: {e}")
            self.instance_status_var.set(f"Error: {e}")

    def kill_all_instances(self):
        """Kill all running instances"""
        if not messagebox.askyesno("Confirm", "Are you sure you want to kill all running instances?"):
            return
        
        killed_count = 0
        for process_type, instances in self.process_instance_tabs.items():
            for instance_data in instances:
                proc = instance_data.get('proc')
                if proc and proc.poll() is None:
                    try:
                        # Kill the process and all its children
                        parent = psutil.Process(proc.pid)
                        children = parent.children(recursive=True)
                        
                        for child in children:
                            try:
                                child.kill()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        
                        try:
                            parent.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        
                        try:
                            proc.kill()
                        except Exception:
                            pass
                        
                        killed_count += 1
                    except Exception as e:
                        self.log(f"Error killing {process_type} instance: {e}")
        
        self.log(f"Killed {killed_count} instances")
        self.instance_status_var.set(f"Killed {killed_count} instances")
        self.refresh_instance_list()

    def update_instance_manager(self):
        """Periodically update the instance manager"""
        if hasattr(self, 'instance_tree'):
            self.refresh_instance_list()
        # Schedule next update
        self.root.after(5000, self.update_instance_manager)  # Update every 5 seconds


class TerminalEmulator(tk.Frame):
    """
    A robust terminal emulator widget for Tkinter:
    - Real-time output (with ANSI color support)
    - Input box for stdin
    - Command history (up/down)
    - Attach to subprocess.Popen
    - Per-instance controls
    """
    ANSI_COLORS = {
        '30': '#000000', '31': '#ff0000', '32': '#00ff00', '33': '#ffff00',
        '34': '#0000ff', '35': '#ff00ff', '36': '#00ffff', '37': '#ffffff',
        '90': '#888888', '91': '#ff5555', '92': '#55ff55', '93': '#ffff55',
        '94': '#5555ff', '95': '#ff55ff', '96': '#55ffff', '97': '#ffffff',
    }
    ANSI_RE = re.compile(r'\x1b\[(\d+)(;(\d+))*m')

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Control panel at the top
        self.control_panel = ttk.Frame(self)
        self.control_panel.pack(fill=tk.X, padx=2, pady=(2,0))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.control_panel, textvariable=self.status_var, font=("Arial", 9))
        self.status_label.pack(side=tk.LEFT, padx=(0,10))
        
        # Control buttons
        self.stop_btn = ttk.Button(self.control_panel, text="Stop", width=6, command=self.stop_process)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.restart_btn = ttk.Button(self.control_panel, text="Restart", width=6, command=self.restart_process)
        self.restart_btn.pack(side=tk.LEFT, padx=2)
        
        self.kill_btn = ttk.Button(self.control_panel, text="Kill", width=6, command=self.kill_process)
        self.kill_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = ttk.Button(self.control_panel, text="Clear", width=6, command=self.clear)
        self.clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Initially disable control buttons
        self.stop_btn.config(state='disabled')
        self.restart_btn.config(state='disabled')
        self.kill_btn.config(state='disabled')
        
        # Terminal output
        self.output = scrolledtext.ScrolledText(self, state='disabled', font=("Consolas", 10), wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2,0))
        
        # Input area
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=2, pady=(0,2))
        
        ttk.Label(input_frame, text="Input:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0,5))
        self.input = tk.Entry(input_frame, font=("Consolas", 10))
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input.bind('<Return>', self._on_enter)
        self.input.bind('<Up>', self._on_up)
        self.input.bind('<Down>', self._on_down)
        
        # Process management
        self.proc = None
        self._thread = None
        self._history = []
        self._history_index = 0
        self._current_input = ''
        self._ansi_tags = {}
        self._setup_tags()
        self._stdin_lock = threading.Lock()
        self.start_time = None
        self.batch_path = None

    def _setup_tags(self):
        for code, color in self.ANSI_COLORS.items():
            tag = f'ansi_fg_{code}'
            self.output.tag_configure(tag, foreground=color)
            self._ansi_tags[code] = tag

    def attach_process(self, proc: subprocess.Popen, batch_path=None):
        self.proc = proc
        self.batch_path = batch_path
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._read_output, daemon=True)
        self._thread.start()
        self.input.config(state='normal')
        self.input.focus_set()
        
        # Enable control buttons
        self.stop_btn.config(state='normal')
        self.restart_btn.config(state='normal')
        self.kill_btn.config(state='normal')
        
        # Update status
        self.status_var.set("Running")
        self.status_label.config(foreground="green")

    def stop_process(self):
        """Stop the process gracefully"""
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.status_var.set("Stopping...")
                self.status_label.config(foreground="orange")
                self.log("Process stop requested")
            except Exception as e:
                self.log(f"Error stopping process: {e}")

    def restart_process(self):
        """Restart the process"""
        if not self.batch_path or not os.path.exists(self.batch_path):
            self.log("Cannot restart: batch file not available")
            return
        
        try:
            # Stop current process
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                time.sleep(1)  # Give it time to stop
            
            # Start new process
            new_proc = subprocess.Popen([self.batch_path], cwd=os.path.dirname(self.batch_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Clear output
            self.clear()
            
            # Attach new process
            self.attach_process(new_proc, self.batch_path)
            
            self.log("Process restarted")
            
        except Exception as e:
            self.log(f"Error restarting process: {e}")

    def kill_process(self):
        """Force kill the process"""
        if self.proc and self.proc.poll() is None:
            try:
                # Kill the process and all its children
                parent = psutil.Process(self.proc.pid)
                children = parent.children(recursive=True)
                
                # Kill all child processes first
                for child in children:
                    try:
                        child.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Kill the parent process
                try:
                    parent.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Also kill the wrapper process
                try:
                    self.proc.kill()
                except Exception:
                    pass
                
                self.status_var.set("Killed")
                self.status_label.config(foreground="red")
                self.log("Process force killed")
                
                # Disable control buttons
                self.stop_btn.config(state='disabled')
                self.restart_btn.config(state='disabled')
                self.kill_btn.config(state='disabled')
                
            except Exception as e:
                self.log(f"Error killing process: {e}")

    def _read_output(self):
        try:
            for line in self.proc.stdout:
                self._append_ansi(line)
        except Exception as e:
            self._append(f"[Terminal Error] {e}\n", '31')
        finally:
            self.input.config(state='disabled')
            self.status_var.set("Stopped")
            self.status_label.config(foreground="red")
            
            # Disable control buttons
            self.stop_btn.config(state='disabled')
            self.restart_btn.config(state='disabled')
            self.kill_btn.config(state='disabled')

    def _append(self, text, color_code=None):
        self.output.config(state='normal')
        if color_code and color_code in self._ansi_tags:
            self.output.insert(tk.END, text, self._ansi_tags[color_code])
        else:
            self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state='disabled')

    def _append_ansi(self, text):
        # Parse ANSI color codes and apply tags
        pos = 0
        last_fg = None
        for match in self.ANSI_RE.finditer(text):
            start, end = match.span()
            if start > pos:
                self._append(text[pos:start], last_fg)
            fg = match.group(1)
            if fg in self.ANSI_COLORS:
                last_fg = fg
            pos = end
        if pos < len(text):
            self._append(text[pos:], last_fg)

    def _on_enter(self, event):
        cmd = self.input.get()
        if not cmd or not self.proc or self.proc.poll() is not None:
            return
        self._history.append(cmd)
        self._history_index = len(self._history)
        self._current_input = ''
        self.input.delete(0, tk.END)
        try:
            with self._stdin_lock:
                self.proc.stdin.write(cmd + '\n')
                self.proc.stdin.flush()
        except Exception as e:
            self._append(f"[Input Error] {e}\n", '31')

    def _on_up(self, event):
        if self._history and self._history_index > 0:
            if self._history_index == len(self._history):
                self._current_input = self.input.get()
            self._history_index -= 1
            self.input.delete(0, tk.END)
            self.input.insert(0, self._history[self._history_index])
        return 'break'

    def _on_down(self, event):
        if self._history and self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.input.delete(0, tk.END)
            self.input.insert(0, self._history[self._history_index])
        elif self._history_index == len(self._history) - 1:
            self._history_index += 1
            self.input.delete(0, tk.END)
            self.input.insert(0, self._current_input)
        return 'break'

    def clear(self):
        self.output.config(state='normal')
        self.output.delete('1.0', tk.END)
        self.output.config(state='disabled')
        self.input.delete(0, tk.END)
        self._history = []
        self._history_index = 0
        self._current_input = ''

    def log(self, message):
        """Add a log message to the terminal"""
        timestamp = time.strftime("%H:%M:%S")
        self._append(f"[{timestamp}] {message}\n", '36')


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = LauncherGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error running launcher: {e}")
        import traceback
        traceback.print_exc() 
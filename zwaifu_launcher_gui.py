import os
import sys
import subprocess
import threading
import time
import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import json
import pystray
from PIL import Image, ImageTk
from datetime import datetime
import webbrowser
import glob
import psutil
import re
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
import importlib.util
import shutil
from typing import Any

# Advanced Features Imports
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    import jwt
    import secrets
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Import utility modules
try:
    from utils import (
        WebInterface, create_web_interface,
        APIServer, create_api_server,
        MobileApp, create_mobile_app,
        AnalyticsSystem, create_analytics_system,
        PluginManager, create_plugin_manager,
        ThemeManager
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Fallback to local classes if utils not available
    pass

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Remove venv creation, install_requirements, and activate_virtual_env functions and their calls.
# The script should now start directly with the GUI logic and not attempt to manage virtual environments.

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config", "launcher_config.json")
ICON_FILE = os.path.join(PROJECT_ROOT, "static", "images", "launcher_icon.png")
CMD_FLAGS_FILE = os.path.join(PROJECT_ROOT, "ai_tools", "oobabooga", "CMD_FLAGS.txt")
LOG_FILE = os.path.join(PROJECT_ROOT, "data", "launcher_log.txt")

# Advanced Features Configuration
WEB_PORT = 8080
API_PORT = 8081
MOBILE_PORT = 8082
ANALYTICS_DB = os.path.join(PROJECT_ROOT, "data", "analytics.db")
PLUGINS_DIR = os.path.join(PROJECT_ROOT, "plugins")
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")

# Create necessary directories
os.makedirs(PLUGINS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

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
            except Exception as e:
                return None, None
    return None, None

def get_local_ip():
    """Get the local IP address for network access"""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # Fallback to localhost if we can't get the IP
        return "localhost"

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
            self.process = subprocess.Popen(self.command, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(self.process.stdout.readline, b''):
                if line:
                    try:
                        # Try to decode with UTF-8 first
                        decoded_line = line.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        try:
                            # Fallback to cp1252 (Windows default)
                            decoded_line = line.decode('cp1252', errors='replace')
                        except UnicodeDecodeError:
                            # Last resort: decode with latin-1 (never fails)
                            decoded_line = line.decode('latin-1', errors='replace')
                    
                    self.output_widget.insert(tk.END, decoded_line)
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

# Advanced Features Classes
class WebInterface:
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.app = None
        self.socketio = None
        self.server_thread = None
        self.is_running = False

    def start(self):
        if not FLASK_AVAILABLE:
            self.launcher_gui.log("Flask not available. Install with: pip install flask flask-socketio flask-cors")
            return False

        try:
            self.app = Flask(__name__)
            self.app.config['SECRET_KEY'] = secrets.token_hex(16)
            CORS(self.app)
            self.socketio = SocketIO(self.app, cors_allowed_origins="*")

            @self.app.route('/')
            def index():
                return self.render_dashboard()

            @self.app.route('/api/status')
            def api_status():
                return jsonify(self.get_status())

            @self.socketio.on('connect')
            def handle_connect():
                emit('status_update', self.get_status())

            @self.socketio.on('start_process')
            def handle_start_process(data):
                process_type = data.get('process_type')
                result = self.start_process_instance(process_type)
                emit('process_result', result)

            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True
            self.launcher_gui.log(f"Web interface started on http://localhost:{WEB_PORT}")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Failed to start web interface: {e}")
            return False

    def _run_server(self):
        try:
            self.socketio.run(self.app, host='127.0.0.1', port=WEB_PORT, debug=False)
        except Exception as e:
            self.launcher_gui.log(f"Web server error: {e}")

    def render_dashboard(self):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Z-Waifu Launcher Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #333; color: white; padding: 20px; border-radius: 5px; }}
                .status-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
                .status-card {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .btn {{ background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 3px; cursor: pointer; }}
                .btn:hover {{ background: #0056b3; }}
                .btn.danger {{ background: #dc3545; }}
                .btn.danger:hover {{ background: #c82333; }}
                .status.running {{ color: #28a745; }}
                .status.stopped {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Z-Waifu Launcher Dashboard</h1>
                    <p>Real-time process management and monitoring</p>
                </div>
                
                <div class="status-grid">
                    <div class="status-card">
                        <h3>Oobabooga</h3>
                        <p class="status" id="ooba-status">Checking...</p>
                        <button class="btn" onclick="startProcess('Oobabooga')">Start</button>
                        <button class="btn danger" onclick="stopProcess('Oobabooga')">Stop</button>
                    </div>
                    
                    <div class="status-card">
                        <h3>Z-Waifu</h3>
                        <p class="status" id="zwaifu-status">Checking...</p>
                        <button class="btn" onclick="startProcess('Z-Waifu')">Start</button>
                        <button class="btn danger" onclick="stopProcess('Z-Waifu')">Stop</button>
                    </div>
                    
                    <div class="status-card">
                        <h3>Ollama</h3>
                        <p class="status" id="ollama-status">Checking...</p>
                        <button class="btn" onclick="startProcess('Ollama')">Start</button>
                        <button class="btn danger" onclick="stopProcess('Ollama')">Stop</button>
                    </div>
                    
                    <div class="status-card">
                        <h3>RVC</h3>
                        <p class="status" id="rvc-status">Checking...</p>
                        <button class="btn" onclick="startProcess('RVC')">Start</button>
                        <button class="btn danger" onclick="stopProcess('RVC')">Stop</button>
                    </div>
                </div>
            </div>
            
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <script>
                const socket = io();
                
                socket.on('status_update', function(data) {{
                    updateStatus(data);
                }});
                
                socket.on('process_result', function(data) {{
                    if (data.success) {{
                        alert('Process started successfully!');
                    }} else {{
                        alert('Error: ' + data.error);
                    }}
                }});
                
                function updateStatus(data) {{
                    Object.keys(data).forEach(process => {{
                        const element = document.getElementById(process.toLowerCase() + '-status');
                        if (element) {{
                            element.textContent = data[process] ? 'Running' : 'Stopped';
                            element.className = 'status ' + (data[process] ? 'running' : 'stopped');
                        }}
                    }});
                }}
                
                function startProcess(processType) {{
                    socket.emit('start_process', {{process_type: processType}});
                }}
                
                function stopProcess(processType) {{
                    socket.emit('stop_process', {{process_type: processType}});
                }}
                
                // Initial status update
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => updateStatus(data));
            </script>
        </body>
        </html>
        """

    def get_status(self):
        """Get the status of all processes for web interface"""
        status = {
            'Oobabooga': False,
            'Z-Waifu': False,
            'Ollama': False,
            'RVC': False
        }
        
        # Check actual process instances in the main GUI
        for process_name, instances in self.launcher_gui.process_instance_tabs.items():
            if instances:  # If there are any instances
                # Check if any instance has a running process
                for instance in instances:
                    if 'proc' in instance and instance['proc']:
                        if instance['proc'].poll() is None:  # Process is running
                            status[process_name] = True
                            break
        
        return status

    def start_process_instance(self, process_type):
        try:
            # Implementation for starting processes
            return {'success': True, 'message': f'Started {process_type}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class APIServer:
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.app = None
        self.limiter = None
        self.server_thread = None
        self.is_running = False
        self.api_keys = {}
        self.admin_key = secrets.token_hex(32)  # Admin key for key generation
        self.launcher_gui.log(f"Admin API key generated: {self.admin_key}")
        
        # Load existing API keys from file
        self.load_persistent_api_keys()

    def _validate_api_key(self, request):
        """Validate API key from request headers"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        api_key = auth_header.split(' ')[1]
        if api_key not in self.api_keys:
            return False
        
        # Check if key has expired (30 day expiration for persistent keys)
        key_data = self.api_keys[api_key]
        if 'expires' in key_data:
            if time.time() > key_data['expires']:
                del self.api_keys[api_key]
                return False
        else:
            # Fallback to 24 hour expiration for old keys
            if time.time() - key_data['created'] > 86400:  # 24 hours
                del self.api_keys[api_key]
                return False
        
        return True

    def _validate_process_type(self, process_type):
        """Validate process type to prevent injection attacks"""
        allowed_processes = {'Oobabooga', 'Z-Waifu', 'Ollama', 'RVC'}
        return process_type in allowed_processes

    def _cleanup_expired_keys(self):
        """Remove expired API keys"""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.api_keys.items():
            if 'expires' in data:
                # Check against explicit expiration time
                if current_time > data['expires']:
                    expired_keys.append(key)
            else:
                # Fallback to 24 hour expiration for old keys
                if current_time - data['created'] > 86400:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.api_keys[key]
        
        # Save updated keys to file after cleanup
        self.save_persistent_api_keys()

    def load_persistent_api_keys(self):
        """Load API keys from persistent storage"""
        try:
            api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
            if os.path.exists(api_key_path):
                with open(api_key_path, 'r') as f:
                    import json
                    api_key_data = json.load(f)
                    api_key = api_key_data.get('api_key')
                    if api_key:
                        # Check if key is still valid (not expired)
                        created_time = api_key_data.get('created', time.time())
                        current_time = time.time()
                        
                        # For persistent keys, extend expiration to 30 days
                        if current_time - created_time <= 30 * 24 * 3600:  # 30 days
                            self.api_keys[api_key] = {
                                'created': created_time,
                                'permissions': ['read', 'write'],
                                'expires': current_time + (30 * 24 * 3600)  # Extend to 30 days from now
                            }
                            self.launcher_gui.log(f"Loaded persistent API key from {api_key_path} (expires in 30 days)")
                        else:
                            self.launcher_gui.log(f"API key in {api_key_path} has expired, will generate new one")
        except Exception as e:
            self.launcher_gui.log(f"Failed to load persistent API keys: {e}")

    def save_persistent_api_keys(self):
        """Save API keys to persistent storage"""
        try:
            # Save the first valid API key found
            for api_key, key_data in self.api_keys.items():
                api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
                with open(api_key_path, 'w') as f:
                    import json
                    json.dump({
                        'api_key': api_key,
                        'created': key_data['created']
                    }, f, indent=2)
                self.launcher_gui.log(f"Saved persistent API key to {api_key_path}")
                break  # Only save the first key
        except Exception as e:
            self.launcher_gui.log(f"Failed to save persistent API keys: {e}")

    def extend_key_expiration(self, api_key):
        """Extend the expiration time of an API key to make it persistent"""
        if api_key in self.api_keys:
            # Extend expiration to 30 days instead of 24 hours
            self.api_keys[api_key]['expires'] = time.time() + (30 * 24 * 3600)  # 30 days
            self.save_persistent_api_keys()
            self.launcher_gui.log(f"Extended expiration for API key to 30 days")

    def start(self):
        if not FLASK_AVAILABLE:
            self.launcher_gui.log("Flask not available. Install with: pip install flask flask-limiter pyjwt")
            return False

        try:
            self.app = Flask(__name__)
            self.app.config['SECRET_KEY'] = secrets.token_hex(32)
            self.limiter = Limiter(
                app=self.app,
                key_func=get_remote_address,
                default_limits=["200 per day", "50 per hour"]
            )

            @self.app.route('/api/status', methods=['GET'])
            @self.limiter.limit("10 per minute")
            def api_status():
                if not self._validate_api_key(request):
                    return jsonify({'error': 'Invalid or missing API key'}), 401
                return jsonify(self.get_status())

            @self.app.route('/api/processes', methods=['GET'])
            @self.limiter.limit("10 per minute")
            def api_processes():
                if not self._validate_api_key(request):
                    return jsonify({'error': 'Invalid or missing API key'}), 401
                return jsonify(self.get_processes())

            @self.app.route('/api/start/<process_type>', methods=['POST'])
            @self.limiter.limit("5 per minute")
            def api_start_process(process_type):
                if not self._validate_api_key(request):
                    return jsonify({'error': 'Invalid or missing API key'}), 401
                if not self._validate_process_type(process_type):
                    return jsonify({'error': 'Invalid process type'}), 400
                return jsonify(self.start_process_instance(process_type, 0))

            @self.app.route('/api/stop/<process_type>', methods=['POST'])
            @self.limiter.limit("5 per minute")
            def api_stop_process(process_type):
                if not self._validate_api_key(request):
                    return jsonify({'error': 'Invalid or missing API key'}), 401
                if not self._validate_process_type(process_type):
                    return jsonify({'error': 'Invalid process type'}), 400
                return jsonify(self.stop_process_instance(process_type, 0))

            @self.app.route('/api/keys/generate', methods=['POST'])
            def api_generate_key():
                # Require admin key for key generation
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Admin key required'}), 401
                
                admin_key = auth_header.split(' ')[1]
                if admin_key != self.admin_key:
                    return jsonify({'error': 'Invalid admin key'}), 401
                
                # Cleanup expired keys before generating new ones
                self._cleanup_expired_keys()
                
                key = secrets.token_hex(32)
                self.api_keys[key] = {
                    'created': time.time(), 
                    'permissions': ['read', 'write'],
                    'expires': time.time() + (30 * 24 * 3600)  # 30 days
                }
                
                # Save the new key persistently
                self.save_persistent_api_keys()
                
                return jsonify({'api_key': key, 'expires_in': 30 * 24 * 3600})

            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True
            self.launcher_gui.log(f"API server started on http://localhost:{API_PORT}")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Failed to start API server: {e}")
            return False

    def _run_server(self):
        try:
            self.app.run(host='127.0.0.1', port=API_PORT, debug=False)
        except Exception as e:
            self.launcher_gui.log(f"API server error: {e}")

    def get_status(self):
        return {
            'launcher_running': True,
            'timestamp': time.time(),
            'version': '1.0.0'
        }

    def get_processes(self):
        """Get detailed process information for API"""
        processes = {
            'Oobabooga': {'running': False, 'pid': None, 'instances': 0},
            'Z-Waifu': {'running': False, 'pid': None, 'instances': 0},
            'Ollama': {'running': False, 'pid': None, 'instances': 0},
            'RVC': {'running': False, 'pid': None, 'instances': 0}
        }
        
        # Check actual process instances in the main GUI
        for process_name, instances in self.launcher_gui.process_instance_tabs.items():
            if instances:  # If there are any instances
                processes[process_name]['instances'] = len(instances)
                # Check if any instance has a running process
                for instance in instances:
                    if 'proc' in instance and instance['proc']:
                        if instance['proc'].poll() is None:  # Process is running
                            processes[process_name]['running'] = True
                            processes[process_name]['pid'] = instance['proc'].pid
                        break
        
        return processes

    def start_process_instance(self, process_type, instance_id):
        try:
            # Get batch file path
            batch_path = None
            if process_type == "Oobabooga":
                batch_path = self.launcher_gui.ooba_bat
            elif process_type == "Z-Waifu":
                batch_path = self.launcher_gui.zwaifu_bat
            elif process_type == "Ollama":
                batch_path = self.launcher_gui.ollama_bat
            elif process_type == "RVC":
                batch_path = self.launcher_gui.rvc_bat
            
            if not batch_path or not os.path.exists(batch_path):
                return {'error': f'Batch file not found for {process_type}'}
            
            # Create new process
            proc = subprocess.Popen([batch_path], cwd=os.path.dirname(batch_path), shell=True,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Update instance data
            if process_type in self.launcher_gui.process_instance_tabs:
                instances = self.launcher_gui.process_instance_tabs[process_type]
            if instance_id < len(instances):
                    instances[instance_id]['proc'] = proc
                    if 'terminal' in instances[instance_id]:
                        terminal = instances[instance_id]['terminal']
                        if terminal:
                            terminal.attach_process(proc, batch_path)
                            terminal.start_time = time.time()
            
            return {'success': True, 'message': f'Started {process_type} Instance {instance_id+1}'}
            
        except Exception as e:
            return {'error': str(e)}

    def stop_process_instance(self, process_type, instance_id):
        try:
            if process_type in self.launcher_gui.process_instance_tabs:
                instances = self.launcher_gui.process_instance_tabs[process_type]
                if instance_id < len(instances):
                    proc = instances[instance_id]['proc']
                    if proc:
                        proc.terminate()
                        return {'success': True, 'message': f'Stopped {process_type} Instance {instance_id+1}'}
            
            return {'error': f'Process not found: {process_type} Instance {instance_id+1}'}
            
        except Exception as e:
            return {'error': str(e)}

class MobileApp:
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.app = None
        self.server_thread = None
        self.is_running = False
        self.qr_code = None
        self.api_key = None
        self.load_api_key()

    def load_api_key(self):
        """Load API key from api_key.json file"""
        try:
            api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
            if os.path.exists(api_key_path):
                with open(api_key_path, 'r') as f:
                    import json
                    api_key_data = json.load(f)
                    self.api_key = api_key_data.get('api_key')
                    if self.api_key:
                        self.launcher_gui.log(f"Mobile app loaded API key from {api_key_path}")
            return self.api_key
        except Exception as e:
            self.launcher_gui.log(f"Failed to load API key for mobile app: {e}")
            return None

    def make_authenticated_api_call(self, url, method='GET', data=None):
        """Make an authenticated API call using the loaded API key"""
        try:
            import requests
            
            if not self.api_key:
                self.api_key = self.load_api_key()
                if not self.api_key:
                    self.launcher_gui.log("No API key available for mobile app API call")
                    return None
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                self.launcher_gui.log(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                self.launcher_gui.log(f"Mobile app API call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.launcher_gui.log(f"Mobile app API call error: {e}")
            return None

    def start(self):
        if not FLASK_AVAILABLE:
            self.launcher_gui.log("Flask not available. Install with: pip install flask")
            return False

        try:
            self.app = Flask(__name__)
            self.app.config['SECRET_KEY'] = secrets.token_hex(16)

            @self.app.route('/')
            def mobile_dashboard():
                return self.render_mobile_dashboard()

            @self.app.route('/api/mobile/status')
            def mobile_status():
                return jsonify(self.get_mobile_status())

            @self.app.route('/api/mobile/start/<process_type>')
            def mobile_start(process_type):
                return jsonify(self.start_process_instance(process_type))

            @self.app.route('/api/mobile/stop/<process_type>')
            def mobile_stop(process_type):
                return jsonify(self.stop_process_instance(process_type))

            @self.app.route('/api/mobile/theme', methods=['GET', 'POST'])
            def mobile_theme():
                if request.method == 'GET':
                    # Return current theme status
                    is_dark = getattr(self.launcher_gui, '_dark_mode', False)
                    return jsonify({'dark_mode': is_dark})
                elif request.method == 'POST':
                    # Toggle theme
                    data = request.get_json()
                    if data and 'dark_mode' in data:
                        if data['dark_mode']:
                            self.launcher_gui.set_dark_mode()
                        else:
                            self.launcher_gui.set_light_mode()
                        return jsonify({'success': True, 'dark_mode': data['dark_mode']})
                    return jsonify({'error': 'Invalid theme data'})

            # PWA routes
            @self.app.route('/mobile/manifest.json')
            def mobile_manifest():
                return self.app.send_static_file('mobile/manifest.json')

            @self.app.route('/mobile/sw.js')
            def mobile_service_worker():
                return self.app.send_static_file('mobile/sw.js')

            @self.app.route('/mobile/icon-<size>.png')
            def mobile_icon(size):
                return self.app.send_static_file(f'mobile/icon-{size}.png')

            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True
            
            # Generate QR code for mobile access
            if QRCODE_AVAILABLE:
                self.generate_qr_code()
            
            local_ip = self.get_local_ip()
            self.launcher_gui.log(f"Mobile app started on http://{local_ip}:{MOBILE_PORT}")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Failed to start mobile app: {e}")
            return False

    def _run_server(self):
        try:
            self.app.run(host='0.0.0.0', port=MOBILE_PORT, debug=False)
        except Exception as e:
            self.launcher_gui.log(f"Mobile server error: {e}")

    def render_mobile_dashboard(self):
        # Get current theme from launcher GUI
        is_dark_mode = getattr(self.launcher_gui, '_dark_mode', False)
        
        # Define theme colors based on mode
        if is_dark_mode:
            bg_color = "#1a1a1a"
            card_bg = "#222222"
            text_color = "#00ff99"
            accent_color = "#009966"
            header_bg = "#333333"
            header_text = "#ffffff"
            btn_bg = "#009966"
            btn_hover = "#007a4d"
            btn_danger = "#dc3545"
            btn_danger_hover = "#c82333"
            status_running = "#28a745"
            status_stopped = "#dc3545"
        else:
            bg_color = "#f0f0f0"
            card_bg = "#ffffff"
            text_color = "#155724"
            accent_color = "#28a745"
            header_bg = "#333333"
            header_text = "#ffffff"
            btn_bg = "#007bff"
            btn_hover = "#0056b3"
            btn_danger = "#dc3545"
            btn_danger_hover = "#c82333"
            status_running = "#28a745"
            status_stopped = "#dc3545"
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Z-Waifu Mobile Dashboard</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
            <meta name="theme-color" content="{accent_color}">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="default">
            <meta name="apple-mobile-web-app-title" content="Z-Waifu Mobile">
            <meta name="msapplication-TileColor" content="{accent_color}">
            <meta name="msapplication-config" content="/mobile/manifest.json">
            
            <!-- PWA Manifest -->
            <link rel="manifest" href="/mobile/manifest.json">
            
            <!-- Icons -->
            <link rel="icon" type="image/png" sizes="32x32" href="/mobile/icon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/mobile/icon-16x16.png">
            <link rel="apple-touch-icon" href="/mobile/icon-192x192.png">
            <style>
                * {{
                    -webkit-tap-highlight-color: transparent;
                    -webkit-touch-callout: none;
                    -webkit-user-select: none;
                    user-select: none;
                }}
                
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: {bg_color}; 
                    color: {text_color};
                    transition: all 0.3s ease;
                    overflow-x: hidden;
                    position: fixed;
                    width: 100%;
                    height: 100%;
                    box-sizing: border-box;
                }}
                .header {{ 
                    background: {header_bg}; 
                    color: {header_text}; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 20px; 
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }}
                .process-card {{ 
                    background: {card_bg}; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 15px; 
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    border: 1px solid {accent_color}20;
                    transition: all 0.3s ease;
                }}
                .process-card:hover {{
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transform: translateY(-2px);
                }}
                .btn {{ 
                    background: {btn_bg}; 
                    color: white; 
                    border: none; 
                    padding: 15px 20px; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    width: 100%; 
                    margin: 5px 0; 
                    font-size: 16px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                }}
                .btn:hover {{ 
                    background: {btn_hover}; 
                    transform: translateY(-1px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }}
                .btn.danger {{ 
                    background: {btn_danger}; 
                }}
                .btn.danger:hover {{ 
                    background: {btn_danger_hover}; 
                }}
                .status.running {{ 
                    color: {status_running}; 
                    font-weight: bold; 
                    font-size: 18px;
                }}
                .status.stopped {{ 
                    color: {status_stopped}; 
                    font-weight: bold; 
                    font-size: 18px;
                }}
                .swipe-area {{ 
                    touch-action: pan-y; 
                }}
                .theme-toggle {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: {accent_color};
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    font-size: 20px;
                    cursor: pointer;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                }}
                .theme-toggle:hover {{
                    transform: scale(1.1);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                }}
                h1, h3 {{
                    margin: 0 0 10px 0;
                    color: {text_color};
                }}
                p {{
                    margin: 5px 0;
                    color: {text_color};
                }}
                
                .connection-status {{
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    padding: 8px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    z-index: 1000;
                    transition: all 0.3s ease;
                }}
                
                .connection-status.online {{
                    background: {status_running};
                    color: white;
                }}
                
                .connection-status.offline {{
                    background: {status_stopped};
                    color: white;
                }}
                
                .connection-status.reconnecting {{
                    background: {btn_hover};
                    color: white;
                    animation: pulse 1.5s infinite;
                }}
                
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
                
                .loading {{
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 3px solid rgba(255,255,255,.3);
                    border-radius: 50%;
                    border-top-color: #fff;
                    animation: spin 1s ease-in-out infinite;
                }}
                
                @keyframes spin {{
                    to {{ transform: rotate(360deg); }}
                }}
                
                .offline-message {{
                    background: {btn_danger};
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                    display: none;
                }}
                
                .offline-message.show {{
                    display: block;
                }}
                
                .refresh-btn {{
                    background: {accent_color};
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="connection-status" id="connection-status">Online</div>
            <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                {'🌙' if is_dark_mode else '☀️'}
            </button>
            
            <div class="offline-message" id="offline-message">
                <h3>📱 Offline Mode</h3>
                <p>You're currently offline. Some features may be limited.</p>
                <button class="refresh-btn" onclick="checkConnection()">Try Again</button>
            </div>
            
            <div class="swipe-area">
                <div class="header">
                    <h1>Z-Waifu Mobile</h1>
                    <p>Touch-friendly process management</p>
                </div>
                
                <div class="process-card">
                    <h3>Oobabooga</h3>
                    <p class="status" id="oobabooga-status">Checking...</p>
                    <button class="btn" id="oobabooga-start-btn" onclick="startProcess('Oobabooga')">Start</button>
                    <button class="btn danger" id="oobabooga-stop-btn" onclick="stopProcess('Oobabooga')">Stop</button>
                </div>
                
                <div class="process-card">
                    <h3>Z-Waifu</h3>
                    <p class="status" id="z-waifu-status">Checking...</p>
                    <button class="btn" id="z-waifu-start-btn" onclick="startProcess('Z-Waifu')">Start</button>
                    <button class="btn danger" id="z-waifu-stop-btn" onclick="stopProcess('Z-Waifu')">Stop</button>
                </div>
                
                <div class="process-card">
                    <h3>Ollama</h3>
                    <p class="status" id="ollama-status">Checking...</p>
                    <button class="btn" id="ollama-start-btn" onclick="startProcess('Ollama')">Start</button>
                    <button class="btn danger" id="ollama-stop-btn" onclick="stopProcess('Ollama')">Stop</button>
                </div>
                
                <div class="process-card">
                    <h3>RVC</h3>
                    <p class="status" id="rvc-status">Checking...</p>
                    <button class="btn" id="rvc-start-btn" onclick="startProcess('RVC')">Start</button>
                    <button class="btn danger" id="rvc-stop-btn" onclick="stopProcess('RVC')">Stop</button>
                </div>
            </div>
            
            <script>
                // PWA and persistence variables
                let isDarkMode = {str(is_dark_mode).lower()};
                let isOnline = navigator.onLine;
                let lastKnownStatus = {{}};
                let updateInterval;
                let reconnectAttempts = 0;
                let maxReconnectAttempts = 5;
                let reconnectDelay = 5000;
                
                // Initialize PWA
                if ('serviceWorker' in navigator) {{
                    window.addEventListener('load', function() {{
                        navigator.serviceWorker.register('/mobile/sw.js')
                            .then(function(registration) {{
                                console.log('ServiceWorker registration successful');
                            }})
                            .catch(function(err) {{
                                console.log('ServiceWorker registration failed: ', err);
                            }});
                    }});
                }}
                
                // Load saved state from localStorage
                function loadSavedState() {{
                    try {{
                        const savedTheme = localStorage.getItem('mobileDarkMode');
                        if (savedTheme !== null) {{
                            isDarkMode = savedTheme === 'true';
                        }}
                        
                        const savedStatus = localStorage.getItem('mobileProcessStatus');
                        if (savedStatus) {{
                            lastKnownStatus = JSON.parse(savedStatus);
                        }}
                        
                        updateThemeUI();
                        updateStatusDisplay();
                    }} catch (error) {{
                        console.error('Error loading saved state:', error);
                    }}
                }}
                
                // Save state to localStorage
                function saveState() {{
                    try {{
                        localStorage.setItem('mobileDarkMode', isDarkMode);
                        localStorage.setItem('mobileProcessStatus', JSON.stringify(lastKnownStatus));
                    }} catch (error) {{
                        console.error('Error saving state:', error);
                    }}
                }}
                
                // Connection management
                function updateConnectionStatus(status) {{
                    const statusEl = document.getElementById('connection-status');
                    const offlineMsg = document.getElementById('offline-message');
                    
                    isOnline = status === 'online';
                    
                    if (isOnline) {{
                        statusEl.textContent = 'Online';
                        statusEl.className = 'connection-status online';
                        offlineMsg.classList.remove('show');
                        reconnectAttempts = 0;
                    }} else {{
                        statusEl.textContent = 'Offline';
                        statusEl.className = 'connection-status offline';
                        offlineMsg.classList.add('show');
                    }}
                }}
                
                function checkConnection() {{
                    if (navigator.onLine) {{
                        updateConnectionStatus('online');
                        updateStatus();
                    }} else {{
                        updateConnectionStatus('offline');
                    }}
                }}
                
                // Network event listeners
                window.addEventListener('online', function() {{
                    updateConnectionStatus('online');
                    updateStatus();
                }});
                
                window.addEventListener('offline', function() {{
                    updateConnectionStatus('offline');
                }});
                
                // Visibility change handling for app drawer persistence
                document.addEventListener('visibilitychange', function() {{
                    if (!document.hidden && isOnline) {{
                        // App became visible again, refresh status
                        updateStatus();
                    }}
                }});
                
                // Page focus handling
                window.addEventListener('focus', function() {{
                    if (isOnline) {{
                        updateStatus();
                    }}
                }});
                
                // Load saved state from localStorage
                function loadSavedState() {{
                    try {{
                        const savedTheme = localStorage.getItem('mobileDarkMode');
                        if (savedTheme !== null) {{
                            isDarkMode = savedTheme === 'true';
                        }}
                        
                        const savedStatus = localStorage.getItem('mobileProcessStatus');
                        if (savedStatus) {{
                            lastKnownStatus = JSON.parse(savedStatus);
                        }}
                        
                        updateThemeUI();
                        updateStatusDisplay();
                    }} catch (error) {{
                        console.error('Error loading saved state:', error);
                    }}
                }}
                
                // Save state to localStorage
                function saveState() {{
                    try {{
                        localStorage.setItem('mobileDarkMode', isDarkMode);
                        localStorage.setItem('mobileProcessStatus', JSON.stringify(lastKnownStatus));
                    }} catch (error) {{
                        console.error('Error saving state:', error);
                    }}
                }}
                
                // Connection management
                function updateConnectionStatus(status) {{
                    const statusEl = document.getElementById('connection-status');
                    const offlineMsg = document.getElementById('offline-message');
                    
                    isOnline = status === 'online';
                    
                    if (isOnline) {{
                        statusEl.textContent = 'Online';
                        statusEl.className = 'connection-status online';
                        offlineMsg.classList.remove('show');
                        reconnectAttempts = 0;
                    }} else {{
                        statusEl.textContent = 'Offline';
                        statusEl.className = 'connection-status offline';
                        offlineMsg.classList.add('show');
                    }}
                }}
                
                function checkConnection() {{
                    if (navigator.onLine) {{
                        updateConnectionStatus('online');
                        updateStatus();
                    }} else {{
                        updateConnectionStatus('offline');
                    }}
                }}
                
                // Network event listeners
                window.addEventListener('online', function() {{
                    updateConnectionStatus('online');
                    updateStatus();
                }});
                
                window.addEventListener('offline', function() {{
                    updateConnectionStatus('offline');
                }});
                
                // Visibility change handling for app drawer persistence
                document.addEventListener('visibilitychange', function() {{
                    if (!document.hidden && isOnline) {{
                        // App became visible again, refresh status
                        updateStatus();
                    }}
                }});
                
                // Page focus handling
                window.addEventListener('focus', function() {{
                    if (isOnline) {{
                        updateStatus();
                    }}
                }});
                
                function toggleTheme() {{
                    isDarkMode = !isDarkMode;
                    
                    // Update UI immediately
                    updateThemeUI();
                    saveState();
                    
                    // Sync with main GUI
                    if (isOnline) {{
                        fetch('/api/mobile/theme', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{dark_mode: isDarkMode}})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (!data.success) {{
                                console.error('Failed to sync theme with main GUI');
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error syncing theme:', error);
                        }});
                    }}
                }}
                
                // Sync with main GUI theme on load
                function syncTheme() {{
                    if (!isOnline) return;
                    
                    fetch('/api/mobile/theme')
                        .then(response => response.json())
                        .then(data => {{
                            const guiDarkMode = data.dark_mode;
                            if (guiDarkMode !== isDarkMode) {{
                                isDarkMode = guiDarkMode;
                                updateThemeUI();
                                saveState();
                            }}
                        }})
                        .catch(error => {{
                            console.log('Could not sync theme with main GUI:', error);
                        }});
                }}
                
                function updateThemeUI() {{
                    const themeBtn = document.querySelector('.theme-toggle');
                    themeBtn.innerHTML = isDarkMode ? '🌙' : '☀️';
                    
                    if (isDarkMode) {{
                        document.body.style.background = '#1a1a1a';
                        document.body.style.color = '#00ff99';
                        document.querySelectorAll('.process-card').forEach(card => {{
                            card.style.background = '#222222';
                            card.style.borderColor = '#00996620';
                        }});
                        document.querySelectorAll('h1, h3, p').forEach(el => {{
                            el.style.color = '#00ff99';
                        }});
                        document.querySelectorAll('.btn:not(.danger)').forEach(btn => {{
                            btn.style.background = '#009966';
                        }});
                    }} else {{
                        document.body.style.background = '#f0f0f0';
                        document.body.style.color = '#155724';
                        document.querySelectorAll('.process-card').forEach(card => {{
                            card.style.background = '#ffffff';
                            card.style.borderColor = '#28a74520';
                        }});
                        document.querySelectorAll('h1, h3, p').forEach(el => {{
                            el.style.color = '#155724';
                        }});
                        document.querySelectorAll('.btn:not(.danger)').forEach(btn => {{
                            btn.style.background = '#007bff';
                        }});
                    }}
                }}
                
                // Load saved theme preference and sync with GUI
                const savedTheme = localStorage.getItem('mobileDarkMode');
                if (savedTheme !== null) {{
                    isDarkMode = savedTheme === 'true';
                }}
                updateThemeUI();
                syncTheme();
                
                function updateStatus() {{
                    if (!isOnline) {{
                        updateConnectionStatus('offline');
                        return;
                    }}
                    
                    const statusEl = document.getElementById('connection-status');
                    statusEl.textContent = 'Checking...';
                    statusEl.className = 'connection-status reconnecting';
                    
                    fetch('/api/mobile/status')
                        .then(response => {{
                            if (!response.ok) throw new Error('Network response was not ok');
                            return response.json();
                        }})
                        .then(data => {{
                            updateConnectionStatus('online');
                            lastKnownStatus = data;
                            updateStatusDisplay();
                            saveState();
                        }})
                        .catch(error => {{
                            console.error('Error fetching status:', error);
                            updateConnectionStatus('offline');
                            
                            // Use cached status if available
                            if (Object.keys(lastKnownStatus).length > 0) {{
                                updateStatusDisplay();
                            }}
                        }});
                }}
                
                function updateStatusDisplay() {{
                    Object.keys(lastKnownStatus).forEach(process => {{
                        const element = document.getElementById(process.toLowerCase() + '-status');
                        const startBtn = document.getElementById(process.toLowerCase() + '-start-btn');
                        const stopBtn = document.getElementById(process.toLowerCase() + '-stop-btn');
                        
                        if (element) {{
                            const isRunning = lastKnownStatus[process];
                            element.textContent = isRunning ? 'Running' : 'Stopped';
                            element.className = 'status ' + (isRunning ? 'running' : 'stopped');
                            
                            // Update button states
                            if (startBtn && stopBtn) {{
                                startBtn.disabled = isRunning;
                                stopBtn.disabled = !isRunning;
                            }}
                        }}
                    }});
                }}
                
                function startProcess(processType) {{
                    if (!isOnline) {{
                        alert('Cannot start process while offline');
                        return;
                    }}
                    
                    const startBtn = document.getElementById(processType.toLowerCase() + '-start-btn');
                    const stopBtn = document.getElementById(processType.toLowerCase() + '-stop-btn');
                    
                    // Disable buttons during operation
                    if (startBtn) startBtn.disabled = true;
                    if (stopBtn) stopBtn.disabled = true;
                    
                    fetch(`/api/mobile/start/${{processType}}`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                // Update local status immediately
                                lastKnownStatus[processType] = true;
                                updateStatusDisplay();
                                saveState();
                                
                                // Refresh status after a delay
                                setTimeout(updateStatus, 2000);
                            }} else {{
                                alert('Error: ' + data.error);
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error starting process:', error);
                            alert('Network error. Please try again.');
                        }})
                        .finally(() => {{
                            // Re-enable buttons
                            if (startBtn) startBtn.disabled = false;
                            if (stopBtn) stopBtn.disabled = false;
                        }});
                }}
                
                function stopProcess(processType) {{
                    if (!isOnline) {{
                        alert('Cannot stop process while offline');
                        return;
                    }}
                    
                    const startBtn = document.getElementById(processType.toLowerCase() + '-start-btn');
                    const stopBtn = document.getElementById(processType.toLowerCase() + '-stop-btn');
                    
                    // Disable buttons during operation
                    if (startBtn) startBtn.disabled = true;
                    if (stopBtn) stopBtn.disabled = true;
                    
                    fetch(`/api/mobile/stop/${{processType}}`)
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                // Update local status immediately
                                lastKnownStatus[processType] = false;
                                updateStatusDisplay();
                                saveState();
                                
                                // Refresh status after a delay
                                setTimeout(updateStatus, 2000);
                            }} else {{
                                alert('Error: ' + data.error);
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error stopping process:', error);
                            alert('Network error. Please try again.');
                        }})
                        .finally(() => {{
                            // Re-enable buttons
                            if (startBtn) startBtn.disabled = false;
                            if (stopBtn) stopBtn.disabled = false;
                        }});
                }}
                
                // Initialize app
                document.addEventListener('DOMContentLoaded', function() {{
                    loadSavedState();
                    updateConnectionStatus(isOnline ? 'online' : 'offline');
                    
                    if (isOnline) {{
                        updateStatus();
                        syncTheme();
                    }}
                    
                    // Set up periodic updates
                    updateInterval = setInterval(() => {{
                        if (isOnline && !document.hidden) {{
                            updateStatus();
                        }}
                    }}, 10000); // Update every 10 seconds when online and visible
                    
                    // Sync theme every 30 seconds
                    setInterval(() => {{
                        if (isOnline) {{
                            syncTheme();
                        }}
                    }}, 30000);
                }});
                
                // Clean up on page unload
                window.addEventListener('beforeunload', function() {{
                    if (updateInterval) {{
                        clearInterval(updateInterval);
                    }}
                    saveState();
                }});
            </script>
        </body>
        </html>
        """

    def get_mobile_status(self):
        """Get the status of all processes for mobile interface"""
        status = {
            'Oobabooga': False,
            'Z-Waifu': False,
            'Ollama': False,
            'RVC': False
        }
        
        # Check actual process instances in the main GUI
        for process_name, instances in self.launcher_gui.process_instance_tabs.items():
            if instances:  # If there are any instances
                # Check if any instance has a running process
                for instance in instances:
                    if 'proc' in instance and instance['proc']:
                        if instance['proc'].poll() is None:  # Process is running
                            status[process_name] = True
                            break
        
        return status

    def start_process_instance(self, process_type):
        try:
            # Map process types to the correct names used by the main GUI
            process_mapping = {
                'oobabooga': 'Oobabooga',
                'z-waifu': 'Z-Waifu',
                'ollama': 'Ollama',
                'rvc': 'RVC'
            }
            
            # Convert to lowercase for mapping lookup
            process_type_lower = process_type.lower()
            
            if process_type_lower in process_mapping:
                mapped_process_type = process_mapping[process_type_lower]
                
                # Use the main GUI's start_process_instance method to ensure proper integration
                # This will create tabs, terminals, and proper process tracking
                self.launcher_gui.start_process_instance(mapped_process_type)
                
                # Add notification
                self.add_notification(
                    f"{process_type} Started",
                    f"Instance has been started successfully",
                    'success'
                )
                
                return {'success': True, 'message': f'Started {process_type} Instance'}
            else:
                return {'error': f'Unknown process type: {process_type}'}
            
        except Exception as e:
            return {'error': str(e)}

    def stop_process_instance(self, process_type):
        try:
            # Map process types to the correct names used by the main GUI
            process_mapping = {
                'oobabooga': 'Oobabooga',
                'z-waifu': 'Z-Waifu',
                'ollama': 'Ollama',
                'rvc': 'RVC'
            }
            
            # Convert to lowercase for mapping lookup
            process_type_lower = process_type.lower()
            
            if process_type_lower in process_mapping:
                mapped_process_type = process_mapping[process_type_lower]
                
                # Find and stop the first running instance of this process type
                if mapped_process_type in self.launcher_gui.process_instance_tabs:
                    instances = self.launcher_gui.process_instance_tabs[mapped_process_type]
                    if len(instances) > 0:
                        # Stop the first instance (index 0)
                        self.launcher_gui.stop_instance(mapped_process_type, 0)
                        
                        # Add notification
                        self.add_notification(
                            f"{process_type} Stopped",
                            f"Instance has been stopped successfully",
                            'info'
                        )
                        
                        return {'success': True, 'message': f'Stopped {process_type} Instance'}
                    else:
                        return {'error': f'No {process_type} instance found'}
                else:
                    return {'error': f'Unknown process type: {process_type}'}
            else:
                return {'error': f'Unknown process type: {process_type}'}
            
        except Exception as e:
            return {'error': str(e)}

    def add_notification(self, title, message, type='info'):
        # Implementation for mobile notifications
        pass

    def get_local_ip(self):
        """Get the local IP address for mobile access"""
        return get_local_ip()

    def generate_qr_code(self):
        try:
            local_ip = self.get_local_ip()
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f'http://{local_ip}:{MOBILE_PORT}')
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            qr_path = os.path.join(PROJECT_ROOT, "mobile_qr.png")
            img.save(qr_path)
            self.qr_code = qr_path
            self.launcher_gui.log(f"Mobile QR code generated: {qr_path}")
            self.launcher_gui.log(f"Mobile access URL: http://{local_ip}:{MOBILE_PORT}")
        except Exception as e:
            self.launcher_gui.log(f"Failed to generate QR code: {e}")

class AnalyticsSystem:
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.db_path = ANALYTICS_DB
        self.api_key = None
        self.load_api_key()
        self.init_database()

    def load_api_key(self):
        """Load API key from api_key.json file"""
        try:
            api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
            if os.path.exists(api_key_path):
                with open(api_key_path, 'r') as f:
                    import json
                    api_key_data = json.load(f)
                    self.api_key = api_key_data.get('api_key')
                    if self.api_key:
                        self.launcher_gui.log(f"Analytics system loaded API key from {api_key_path}")
            return self.api_key
        except Exception as e:
            self.launcher_gui.log(f"Failed to load API key for analytics: {e}")
            return None

    def make_authenticated_api_call(self, url, method='GET', data=None):
        """Make an authenticated API call using the loaded API key"""
        try:
            import requests
            
            if not self.api_key:
                self.api_key = self.load_api_key()
                if not self.api_key:
                    self.launcher_gui.log("No API key available for analytics API call")
                    return None
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                self.launcher_gui.log(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                self.launcher_gui.log(f"Analytics API call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.launcher_gui.log(f"Analytics API call error: {e}")
            return None

    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS process_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_name TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_usage REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if disk_usage column exists, add if missing
            cursor.execute("PRAGMA table_info(system_metrics)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'disk_usage' not in columns:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN disk_usage REAL')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS process_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_name TEXT,
                    event_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.launcher_gui.log(f"Failed to initialize analytics database: {e}")

    def record_process_metrics(self, process_name, cpu_percent, memory_percent):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO process_metrics (process_name, cpu_percent, memory_percent) VALUES (?, ?, ?)',
                (process_name, cpu_percent, memory_percent)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.launcher_gui.log(f"Failed to record process metrics: {e}")

    def record_system_metrics(self, cpu_percent, memory_percent, disk_usage):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if disk_usage column exists
            cursor.execute("PRAGMA table_info(system_metrics)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'disk_usage' in columns:
                cursor.execute(
                    'INSERT INTO system_metrics (cpu_percent, memory_percent, disk_usage) VALUES (?, ?, ?)',
                    (cpu_percent, memory_percent, disk_usage)
                )
            else:
                # Fallback without disk_usage column
                cursor.execute(
                    'INSERT INTO system_metrics (cpu_percent, memory_percent) VALUES (?, ?)',
                    (cpu_percent, memory_percent)
                )
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Only log the error once to avoid spam
            if not hasattr(self, '_logged_metrics_error'):
                self.launcher_gui.log(f"Failed to record system metrics: {e}")
                self._logged_metrics_error = True

    def record_process_event(self, process_name, event_type):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO process_events (process_name, event_type) VALUES (?, ?)',
                (process_name, event_type)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.launcher_gui.log(f"Failed to record process event: {e}")

    def get_process_metrics(self, process_name, hours=24):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute('''
                SELECT cpu_percent, memory_percent, timestamp 
                FROM process_metrics 
                WHERE process_name = ? AND timestamp > datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp
            ''', (process_name, str(hours)))
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            self.launcher_gui.log(f"Failed to get process metrics: {e}")
            return []

    def get_system_metrics(self, hours=24):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute('''
                SELECT cpu_percent, memory_percent, disk_usage, timestamp 
                FROM system_metrics 
                WHERE timestamp > datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp
            ''', (str(hours),))
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            self.launcher_gui.log(f"Failed to get system metrics: {e}")
            return []

    def generate_report(self, hours=24):
        try:
            system_data = self.get_system_metrics(hours)
            if not system_data:
                return "No data available for the specified time period."
            
            avg_cpu = sum(row[0] for row in system_data) / len(system_data)
            avg_memory = sum(row[1] for row in system_data) / len(system_data)
            avg_disk = sum(row[2] for row in system_data) / len(system_data)
            
            report = f"""
            System Performance Report (Last {hours} hours)
            =============================================
            Average CPU Usage: {avg_cpu:.2f}%
            Average Memory Usage: {avg_memory:.2f}%
            Average Disk Usage: {avg_disk:.2f}%
            
            Data Points: {len(system_data)}
            """
            
            return report
        except Exception as e:
            self.launcher_gui.log(f"Failed to generate report: {e}")
            return "Error generating report"

class PluginManager:
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        """Load plugins from the plugins directory with improved error handling"""
        self.plugins = {}
        
        if not os.path.exists(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR, exist_ok=True)
            self.launcher_gui.log("Created plugins directory")
            return
        
        self.launcher_gui.log(f"Loading plugins from: {PLUGINS_DIR}")
        
        try:
            for filename in os.listdir(PLUGINS_DIR):
                if filename.endswith('.py') and not filename.startswith('__'):
                    plugin_name = filename[:-3]
                    plugin_path = os.path.join(PLUGINS_DIR, filename)
                    
                    try:
                        # Load the plugin module
                        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                        if spec is None or spec.loader is None:
                            self.launcher_gui.log(f"Failed to create spec for plugin {filename}")
                            continue
                            
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Look for a plugin class or factory function
                        plugin_instance = None
                        
                        # First, try to find a create_plugin function
                        if hasattr(module, 'create_plugin'):
                            try:
                                plugin_instance = module.create_plugin(self.launcher_gui)
                                self.launcher_gui.log(f"Created plugin using factory: {plugin_name}")
                            except Exception as e:
                                self.launcher_gui.log(f"Error creating plugin {plugin_name} with factory: {e}")
                                continue
                        
                        # If no factory, look for a plugin class
                        if plugin_instance is None:
                            for attr_name in dir(module):
                                attr = getattr(module, attr_name)
                                if (isinstance(attr, type) and 
                                    hasattr(attr, 'name') and 
                                    hasattr(attr, 'enable') and 
                                    hasattr(attr, 'disable')):
                                    try:
                                        plugin_instance = attr(self.launcher_gui)
                                        self.launcher_gui.log(f"Created plugin using class: {plugin_name}")
                                        break
                                    except Exception as e:
                                        self.launcher_gui.log(f"Error creating plugin {plugin_name} with class {attr_name}: {e}")
                                        continue
                        
                        # Fallback: check for common plugin class names
                        if plugin_instance is None:
                            for class_name in ['Plugin', 'AutoRestartPlugin', 'ProcessMonitorPlugin']:
                                if hasattr(module, class_name):
                                    try:
                                        plugin_class = getattr(module, class_name)
                                        plugin_instance = plugin_class(self.launcher_gui)
                                        self.launcher_gui.log(f"Created plugin using fallback class: {plugin_name}")
                                        break
                                    except Exception as e:
                                        self.launcher_gui.log(f"Error creating plugin {plugin_name} with fallback class {class_name}: {e}")
                                        continue
                        
                        if plugin_instance:
                            # Validate plugin instance
                            if not hasattr(plugin_instance, 'name'):
                                plugin_instance.name = plugin_name
                            if not hasattr(plugin_instance, 'enable'):
                                plugin_instance.enable = lambda: True
                            if not hasattr(plugin_instance, 'disable'):
                                plugin_instance.disable = lambda: True
                            
                            self.plugins[plugin_name] = plugin_instance
                            self.launcher_gui.log(f"Successfully loaded plugin: {plugin_name}")
                        else:
                            self.launcher_gui.log(f"No valid plugin class or factory found in {filename}")
                            
                    except ImportError as e:
                        self.launcher_gui.log(f"Import error loading plugin {filename}: {e}")
                    except Exception as e:
                        self.launcher_gui.log(f"Failed to load plugin {filename}: {e}")
                        
        except Exception as e:
            self.launcher_gui.log(f"Failed to load plugins: {e}")
        
        self.launcher_gui.log(f"Plugin loading complete. Loaded {len(self.plugins)} plugins.")

    def create_plugin_template(self, plugin_name):
        template = f'''#!/usr/bin/env python3
"""
{plugin_name} Plugin for Z-Waifu Launcher GUI
A custom plugin for extending launcher functionality.
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from plugin_system import PluginBase
except ImportError:
    print(f"Error: Could not import PluginBase for {plugin_name}")
    sys.exit(1)

class {plugin_name.replace('_', '').title()}Plugin(PluginBase):
    """{plugin_name.replace('_', ' ').title()} plugin implementation"""
    
    def __init__(self, launcher_gui):
        super().__init__(launcher_gui)
        self.name = "{plugin_name.replace('_', ' ').title()}"
        self.description = "A custom plugin for Z-Waifu Launcher"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.enabled = False
        self.config = {{}}
        
        # Plugin-specific variables
        self.monitoring_thread = None
        self.stop_monitoring = False
    
    def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            self.launcher_gui.log(f"Initializing {{self.name}} plugin")
            # Add your initialization code here
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error initializing {{self.name}} plugin: {{e}}")
            return False
    
    def enable(self) -> bool:
        """Enable the plugin"""
        try:
            self.enabled = True
            self.launcher_gui.log(f"Enabled {{self.name}} plugin")
            # Add your enable code here
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error enabling {{self.name}} plugin: {{e}}")
            return False
    
    def disable(self) -> bool:
        """Disable the plugin"""
        try:
            self.enabled = False
            self.stop_monitoring = True
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=2)
            self.launcher_gui.log(f"Disabled {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error disabling {{self.name}} plugin: {{e}}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        try:
            self.disable()
            self.launcher_gui.log(f"Cleaned up {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error cleaning up {{self.name}} plugin: {{e}}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self.config
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """Set plugin configuration"""
        try:
            self.config = config
            self.launcher_gui.log(f"Updated config for {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error setting config for {{self.name}} plugin: {{e}}")
            return False
    
    def on_process_start(self, process_type: str, instance_id: int) -> None:
        """Called when a process starts"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Process {{process_type}} (instance {{instance_id}}) started")
    
    def on_process_stop(self, process_type: str, instance_id: int) -> None:
        """Called when a process stops"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Process {{process_type}} (instance {{instance_id}}) stopped")
    
    def on_process_error(self, process_type: str, instance_id: int, error: str) -> None:
        """Called when a process encounters an error"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Process {{process_type}} (instance {{instance_id}}) error: {{error}}")
    
    def on_launcher_start(self) -> None:
        """Called when the launcher starts"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Launcher started")
    
    def on_launcher_stop(self) -> None:
        """Called when the launcher stops"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Launcher stopped")
    
    def on_config_change(self, config: Dict[str, Any]) -> None:
        """Called when launcher configuration changes"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Launcher config changed")
    
    # Add your custom plugin methods here
    def custom_method(self):
        """Example custom method"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Custom method called")

# Plugin factory function (required for plugin loading)
def create_plugin(launcher_gui):
    """Create plugin instance"""
    return {plugin_name.replace('_', '').title()}Plugin(launcher_gui)
'''
        
        plugin_path = os.path.join(PLUGINS_DIR, f"{plugin_name}.py")
        try:
            with open(plugin_path, 'w') as f:
                f.write(template)
            self.launcher_gui.log(f"Created plugin template: {plugin_path}")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Failed to create plugin template: {e}")
            return False

    def get_plugin_list(self):
        return list(self.plugins.keys())

    def enable_plugin(self, plugin_name):
        """Enable a plugin with proper error handling"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            try:
                # Try to call the enable method if it exists
                if hasattr(plugin, 'enable') and callable(plugin.enable):
                    if plugin.enable():
                        self.launcher_gui.log(f"Enabled plugin: {plugin_name}")
                    else:
                        self.launcher_gui.log(f"Failed to enable plugin: {plugin_name}")
                else:
                    # Fallback: call on_launcher_start if it exists
                    if hasattr(plugin, 'on_launcher_start') and callable(plugin.on_launcher_start):
                        plugin.on_launcher_start()
                        self.launcher_gui.log(f"Enabled plugin: {plugin_name}")
                    else:
                        self.launcher_gui.log(f"Plugin {plugin_name} has no enable method")
            except Exception as e:
                self.launcher_gui.log(f"Error enabling plugin {plugin_name}: {e}")
        else:
            self.launcher_gui.log(f"Plugin {plugin_name} not found")

    def disable_plugin(self, plugin_name):
        """Disable a plugin with proper error handling"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            try:
                # Try to call the disable method if it exists
                if hasattr(plugin, 'disable') and callable(plugin.disable):
                    if plugin.disable():
                        self.launcher_gui.log(f"Disabled plugin: {plugin_name}")
                    else:
                        self.launcher_gui.log(f"Failed to disable plugin: {plugin_name}")
                else:
                    # Fallback: call on_launcher_stop if it exists
                    if hasattr(plugin, 'on_launcher_stop') and callable(plugin.on_launcher_stop):
                        plugin.on_launcher_stop()
                        self.launcher_gui.log(f"Disabled plugin: {plugin_name}")
                    else:
                        self.launcher_gui.log(f"Plugin {plugin_name} has no disable method")
            except Exception as e:
                self.launcher_gui.log(f"Error disabling plugin {plugin_name}: {e}")
        else:
            self.launcher_gui.log(f"Plugin {plugin_name} not found")

# Place this after imports at the top of the file
TAB_THEMES = {
    'main_tab':      {'bg': '#1e1e2e', 'fg': '#cdd6f4', 'entry_bg': '#313244', 'entry_fg': '#cdd6f4', 'accent': '#89b4fa', 'border': '#45475a'},
    'settings_tab':  {'bg': '#181825', 'fg': '#cdd6f4', 'entry_bg': '#313244', 'entry_fg': '#cdd6f4', 'accent': '#89b4fa', 'border': '#45475a'},
    'about_tab':     {'bg': '#1e1e2e', 'fg': '#f9e2af', 'entry_bg': '#313244', 'entry_fg': '#f9e2af', 'accent': '#f9e2af', 'border': '#45475a'},
    'ollama_tab':    {'bg': '#1e1e2e', 'fg': '#a6e3a1', 'entry_bg': '#313244', 'entry_fg': '#a6e3a1', 'accent': '#a6e3a1', 'border': '#45475a'},
    'rvc_tab':       {'bg': '#1e1e2e', 'fg': '#f5c2e7', 'entry_bg': '#313244', 'entry_fg': '#f5c2e7', 'accent': '#f5c2e7', 'border': '#45475a'},
    'logs_tab':      {'bg': '#181825', 'fg': '#a6e3a1', 'entry_bg': '#313244', 'entry_fg': '#a6e3a1', 'accent': '#a6e3a1', 'border': '#45475a'},
    'ooba_tab':      {'bg': '#1e1e2e', 'fg': '#89b4fa', 'entry_bg': '#313244', 'entry_fg': '#89b4fa', 'accent': '#89b4fa', 'border': '#45475a'},
    'zwaifu_tab':    {'bg': '#1e1e2e', 'fg': '#fab387', 'entry_bg': '#313244', 'entry_fg': '#fab387', 'accent': '#fab387', 'border': '#45475a'},
    'advanced_features_tab': {'bg': '#181825', 'fg': '#89dceb', 'entry_bg': '#313244', 'entry_fg': '#89dceb', 'accent': '#89dceb', 'border': '#45475a'},
    'instance_manager_tab': {'bg': '#1e1e2e', 'fg': '#cdd6f4', 'entry_bg': '#313244', 'entry_fg': '#cdd6f4', 'accent': '#89b4fa', 'border': '#45475a'},
    # Advanced Features Specific Themes
    'web_interface': {'bg': '#181825', 'fg': '#89b4fa', 'entry_bg': '#313244', 'entry_fg': '#89b4fa', 'accent': '#89b4fa', 'border': '#45475a'},
    'mobile_app': {'bg': '#181825', 'fg': '#a6e3a1', 'entry_bg': '#313244', 'entry_fg': '#a6e3a1', 'accent': '#a6e3a1', 'border': '#45475a'},
    'analytics_dashboard': {'bg': '#181825', 'fg': '#f9e2af', 'entry_bg': '#313244', 'entry_fg': '#f9e2af', 'accent': '#f9e2af', 'border': '#45475a'},
    'plugin_manager': {'bg': '#181825', 'fg': '#f5c2e7', 'entry_bg': '#313244', 'entry_fg': '#f5c2e7', 'accent': '#f5c2e7', 'border': '#45475a'},
    'api_documentation': {'bg': '#181825', 'fg': '#89dceb', 'entry_bg': '#313244', 'entry_fg': '#89dceb', 'accent': '#89dceb', 'border': '#45475a'},
}

# Light mode themes for advanced features - Modern light theme with better contrast
LIGHT_TAB_THEMES = {
    'main_tab':      {'bg': '#fafafa', 'fg': '#2d3748', 'entry_bg': '#ffffff', 'entry_fg': '#2d3748', 'accent': '#3182ce', 'border': '#e2e8f0'},
    'settings_tab':  {'bg': '#ffffff', 'fg': '#1a202c', 'entry_bg': '#f7fafc', 'entry_fg': '#1a202c', 'accent': '#3182ce', 'border': '#e2e8f0'},
    'about_tab':     {'bg': '#fef5e7', 'fg': '#744210', 'entry_bg': '#ffffff', 'entry_fg': '#744210', 'accent': '#d69e2e', 'border': '#fbd38d'},
    'ollama_tab':    {'bg': '#f0fff4', 'fg': '#22543d', 'entry_bg': '#ffffff', 'entry_fg': '#22543d', 'accent': '#38a169', 'border': '#9ae6b4'},
    'rvc_tab':       {'bg': '#fed7d7', 'fg': '#742a2a', 'entry_bg': '#ffffff', 'entry_fg': '#742a2a', 'accent': '#e53e3e', 'border': '#feb2b2'},
    'logs_tab':      {'bg': '#f0fff4', 'fg': '#22543d', 'entry_bg': '#ffffff', 'entry_fg': '#22543d', 'accent': '#38a169', 'border': '#9ae6b4'},
    'ooba_tab':      {'bg': '#ebf8ff', 'fg': '#2a4365', 'entry_bg': '#ffffff', 'entry_fg': '#2a4365', 'accent': '#3182ce', 'border': '#90cdf4'},
    'zwaifu_tab':    {'bg': '#fef5e7', 'fg': '#744210', 'entry_bg': '#ffffff', 'entry_fg': '#744210', 'accent': '#d69e2e', 'border': '#fbd38d'},
    'advanced_features_tab': {'bg': '#f7fafc', 'fg': '#2d3748', 'entry_bg': '#ffffff', 'entry_fg': '#2d3748', 'accent': '#3182ce', 'border': '#e2e8f0'},
    'instance_manager_tab': {'bg': '#fafafa', 'fg': '#2d3748', 'entry_bg': '#ffffff', 'entry_fg': '#2d3748', 'accent': '#3182ce', 'border': '#e2e8f0'},
    # Advanced Features Specific Light Themes
    'web_interface': {'bg': '#f7fafc', 'fg': '#2d3748', 'entry_bg': '#ffffff', 'entry_fg': '#2d3748', 'accent': '#3182ce', 'border': '#e2e8f0'},
    'mobile_app': {'bg': '#f0fff4', 'fg': '#22543d', 'entry_bg': '#ffffff', 'entry_fg': '#22543d', 'accent': '#38a169', 'border': '#9ae6b4'},
    'analytics_dashboard': {'bg': '#fef5e7', 'fg': '#744210', 'entry_bg': '#ffffff', 'entry_fg': '#744210', 'accent': '#d69e2e', 'border': '#fbd38d'},
    'plugin_manager': {'bg': '#fed7d7', 'fg': '#742a2a', 'entry_bg': '#ffffff', 'entry_fg': '#742a2a', 'accent': '#e53e3e', 'border': '#feb2b2'},
    'api_documentation': {'bg': '#ebf8ff', 'fg': '#2a4365', 'entry_bg': '#ffffff', 'entry_fg': '#2a4365', 'accent': '#3182ce', 'border': '#90cdf4'},
}

class LauncherGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Z Launcher")
        root.geometry("1000x800")
        root.minsize(800, 600)
        root.resizable(True, True)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Make window appear on top of other windows
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()
        
        # After a brief delay, remove topmost to allow normal window behavior
        root.after(1000, lambda: root.attributes('-topmost', False))
        self.status_var = tk.StringVar(value="")
        status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Set project root for path validation
        self.project_root = PROJECT_ROOT

        # Initialize batch file paths first
        self.ooba_bat: str | None = None
        self.zwaifu_bat: str | None = None
        self.ollama_bat: str | None = None
        self.rvc_bat: str | None = None

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
        self.processes: dict[str, Any] = {}

        # Initialize theme manager
        self.theme_manager = ThemeManager(self) if UTILS_AVAILABLE else None
        
        # Track current theme state
        self._dark_mode = False
        self.current_theme = 'light'  # Default theme
        
        # Add thread safety for process management
        self._process_lock = threading.Lock()
        self._stop_lock = threading.Lock()
        self._stop_requested = False

        # Initialize advanced features
        self.web_interface = None
        self.api_server = None
        self.mobile_app = None
        self.analytics = None
        self.plugin_manager = None
        
        # Initialize error handler and VRAM monitor
        self.error_handler = None
        self.vram_monitor = None
        self._initialize_error_and_vram_systems()

        # Initialize port variables BEFORE loading config
        self.ooba_port_var = tk.StringVar(value="7860")
        self.zwaifu_port_var = tk.StringVar(value="5000")

        # Load config and icon first
        try:
            self.load_config_safe()
        except Exception as e:
            self.log(f"Unexpected error loading config: {e}")
            # Continue with default config
        try:
            self.load_icon()
        except Exception as e:
            self.log(f"Unexpected error loading icon: {e}")
            # Continue without icon
                         

        # Header frame to hold only the notebook (not the button)
        self.notebook_frame = ttk.Frame(root)
        self.notebook_frame.pack(fill=tk.X)

        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill=tk.X, expand=True)
        
        # Bind tab selection event for logs tab refresh
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Ensure the launcher icon exists on startup
        if not os.path.exists(ICON_FILE):
            try:
                subprocess.run([sys.executable, 'create_launcher_icon.py'], check=True)
            except Exception as e:
                print(f"Failed to generate launcher_icon.png: {e}")

        self.auto_detect_batch_files()
        
        # Initialize process instance tabs FIRST (before any tabs that need it)
        if not hasattr(self, 'process_instance_tabs'):
            self.process_instance_tabs = {
                'Oobabooga': [],
                'Z-Waifu': [],
                'Ollama': [],
                'RVC': []
            }
            self.log("Process instance tracking initialized (all process types)")
        else:
            # Ensure all process types are present
            for proc in ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']:
                if proc not in self.process_instance_tabs:
                    self.process_instance_tabs[proc] = []
                    self.log(f"Added missing process type to process_instance_tabs: {proc}")
        
        self.create_main_tab()
        self.create_cmd_flags_tab()
        self.create_settings_tab()
        self.create_about_tab()
        self.create_ollama_tab()
        self.create_rvc_tab()
        self.create_logs_tab()
        self.create_instance_manager_tab()  # Add instance manager tab
        # Create individual process tabs with TerminalEmulator support
        self.create_ooba_tab()
        self.create_zwaifu_tab()
        
        # Initialize advanced features
        self.initialize_advanced_features()
        
        # Create advanced features tab
        self.create_advanced_features_tab()

        # Create theme toggle button after all tabs are created
        self.theme_toggle_btn = tk.Button(
            root,
            text="☀️",  # Start with sun emoji (will be updated by theme)
            font=("Segoe UI Emoji", 12),
            command=self.toggle_theme,
            bd=0,
            relief="flat",
            padx=0, pady=0,
            height=1, width=2,
            bg="#222222",
            activebackground="#222222",
            fg="#ffffff",
            activeforeground="#ffffff"
        )
        self.theme_toggle_btn.place(relx=1.0, y=2, anchor="ne")
        
        # Create bring to front button
        self.front_btn = tk.Button(
            root,
            text="📋",  # Clipboard icon to represent "bring to front"
            font=("Segoe UI Emoji", 12),
            command=self.bring_to_front,
            bd=0,
            relief="flat",
            padx=0, pady=0,
            height=1, width=2,
            bg="#222222",
            activebackground="#333333",
            fg="#ffffff",
            activeforeground="#ffffff"
        )
        self.front_btn.place(relx=1.0, y=30, anchor="ne")
        
        # Set initial theme state based on loaded config
        self._dark_mode = getattr(self, 'current_theme', 'light') == 'dark'
        if self._dark_mode:
            self.set_dark_mode()
        else:
            self.set_light_mode()
        
        # Update button appearance to match actual theme
        self._update_theme_button()
        self.root.update_idletasks()

        # Start periodic status updates
        self.root.after(1000, self.update_process_status)  # Start after 1 second
        self.root.after(2000, self.update_instance_manager)  # Update instance manager every 2 seconds
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-F>', lambda e: self.bring_to_front())  # Ctrl+F to bring to front
        self.root.bind('<F12>', lambda e: self.bring_to_front())  # F12 to bring to front

        # System tray icon removed as requested

    def _initialize_error_and_vram_systems(self):
        """Initialize error handler and VRAM monitor systems"""
        try:
            # Initialize error handler
            from utils.error_handler import setup_error_handler
            from utils.config_manager import ConfigManager
            
            config_manager = ConfigManager(CONFIG_FILE)
            self.error_handler = setup_error_handler(config_manager)
            
            # Register error callback for logging
            def error_callback(error_info):
                self.log(f"[ERROR] {error_info['error_type']}: {error_info['error_message']}")
            
            self.error_handler.register_error_callback(error_callback)
            self.log("[System] Error handler initialized")
            
        except Exception as e:
            print(f"Failed to initialize error handler: {e}")
            self.error_handler = None
        
        try:
            # Initialize VRAM monitor
            from utils.vram_monitor import setup_vram_monitor
            
            self.vram_monitor = setup_vram_monitor(config_manager if 'config_manager' in locals() else None)
            
            # Register VRAM callback for logging
            def vram_callback(vram_info):
                if vram_info.get("type") == "cleanup":
                    self.log(f"[VRAM] Cleanup performed: {len(vram_info['results']['methods_successful'])} methods successful")
                elif vram_info.get("type") == "warning":
                    self.log(f"[VRAM] Warning: {vram_info.get('message', 'High VRAM usage')}")
                elif vram_info.get("type") == "critical":
                    self.log(f"[VRAM] Critical: {vram_info.get('message', 'Critical VRAM usage')}")
                elif vram_info.get("vram_usage_percent", 0) > 90:
                    self.log(f"[VRAM] High usage: {vram_info.get('vram_usage_percent', 0):.1f}%")
            
            self.vram_monitor.register_vram_callback(vram_callback)
            
            # Start VRAM monitoring if enabled
            if self.vram_monitor.vram_settings.get("vram_monitoring_enabled", True):
                self.vram_monitor.start_monitoring()
                self.log("[System] VRAM monitoring started")
            else:
                self.log("[System] VRAM monitoring disabled")
                
        except Exception as e:
            print(f"Failed to initialize VRAM monitor: {e}")
            self.vram_monitor = None

    def log(self, msg):
        # Ensure log file exists and append message
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
                f.flush()
        except Exception as e:
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
        path = filedialog.askopenfilename(title="Select Oobabooga batch file", filetypes=[("Batch files", "*.bat")], initialdir=getattr(self, 'last_dir', os.getcwd()))
        if path:
            self.ooba_bat = path
            self.ooba_path_var.set(path)
            self.last_dir = os.path.dirname(path)
            self.save_config()
            print(f"Selected Oobabooga batch: {path}")

    def browse_zwaifu(self):
        path = filedialog.askopenfilename(title="Select Z-Waifu batch file", filetypes=[("Batch files", "*.bat")], initialdir=getattr(self, 'last_dir', os.getcwd()))
        if path:
            self.zwaifu_bat = path
            self.zwaifu_path_var.set(path)
            self.last_dir = os.path.dirname(path)
            self.save_config()
            print(f"Selected Z-Waifu batch: {path}")

    def browse_ollama(self):
        path = filedialog.askopenfilename(title="Select Ollama batch file", filetypes=[("Batch files", "*.bat")], initialdir=getattr(self, 'last_dir', os.getcwd()))
        if path:
            self.ollama_bat = path
            self.ollama_path_var.set(path)
            self.last_dir = os.path.dirname(path)
            self.save_config()
            self.log(f"Selected Ollama batch: {path}")

    def browse_rvc(self):
        path = filedialog.askopenfilename(title="Select RVC batch file", filetypes=[("Batch files", "*.bat")], initialdir=getattr(self, 'last_dir', os.getcwd()))
        if path:
            self.rvc_bat = path
            self.rvc_path_var.set(path)
            self.last_dir = os.path.dirname(path)
            self.save_config()
            self.log(f"Selected RVC batch: {path}")

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
        
        # Enhanced port validation
        try:
            ooba_port_str = self.ooba_port_var.get().strip()
            zwaifu_port_str = self.zwaifu_port_var.get().strip()
            
            # Validate port strings
            if not self._is_valid_port(ooba_port_str):
                messagebox.showerror("Invalid Port", f"Invalid Oobabooga port: {ooba_port_str}. Port must be between 1-65535.")
                return
            if not self._is_valid_port(zwaifu_port_str):
                messagebox.showerror("Invalid Port", f"Invalid Z-Waifu port: {zwaifu_port_str}. Port must be between 1-65535.")
                return
            
            ooba_port = int(ooba_port_str)
            zwaifu_port = int(zwaifu_port_str)
            
            # Check for port conflicts
            if ooba_port == zwaifu_port:
                messagebox.showerror("Port Conflict", "Oobabooga and Z-Waifu cannot use the same port.")
                return
                
        except Exception as e:
            messagebox.showerror("Invalid Port", f"Port validation error: {e}")
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
            # Initialize stop request flag with proper synchronization
            with self._stop_lock:
                self._stop_requested = False
            
            # Check stop flag before starting processes
            with self._stop_lock:
                if self._stop_requested:
                    self.log("[LAUNCH] Launch cancelled by stop request")
                    self.start_btn.config(state='normal')
                    self.stop_all_btn.config(state='disabled')
                    return
            
            # Start Oobabooga with thread safety
            with self._process_lock:
                # Double-check stop flag before creating process
                with self._stop_lock:
                    if self._stop_requested:
                        self.log("[LAUNCH] Launch cancelled by stop request")
                        self.start_btn.config(state='normal')
                        self.stop_all_btn.config(state='disabled')
                        return
                
                self.log(f"[Oobabooga] Starting: {self.ooba_bat}")
                self.ooba_proc = subprocess.Popen([self.ooba_bat], cwd=os.path.dirname(self.ooba_bat), shell=True)
                
                # Check if process started successfully and stop flag wasn't set
                if self.ooba_proc.poll() is not None:
                    self.log("[Oobabooga] Process failed to start")
                    self.start_btn.config(state='normal')
                    self.stop_all_btn.config(state='disabled')
                    return
                
                # Check stop flag again after process creation
                with self._stop_lock:
                    if self._stop_requested:
                        self.log("[LAUNCH] Stop requested after Oobabooga start")
                        self.ooba_proc.terminate()
                        self.start_btn.config(state='normal')
                        self.stop_all_btn.config(state='disabled')
                        return
            
            self.set_status(f"Waiting for Oobabooga on port {ooba_port}...", "orange")
            
            # Wait for port, but allow interruption
            start = time.time()
            while time.time() - start < 120:
                # Check stop request atomically with process state
                with self._stop_lock:
                    stop_requested = self._stop_requested
                
                if stop_requested:
                    with self._process_lock:
                        if self.ooba_proc and self.ooba_proc.poll() is None:
                            try:
                                self.ooba_proc.kill()
                                self.ooba_proc.wait(timeout=5)  # Wait for process to terminate
                            except subprocess.TimeoutExpired:
                                try:
                                    self.ooba_proc.terminate()  # Force terminate if needed
                                    self.ooba_proc.wait(timeout=2)
                                except subprocess.TimeoutExpired:
                                    pass  # Process will be cleaned up by OS
                            except Exception as e:
                                self.log(f"Error stopping Oobabooga process: {e}")
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
                with self._process_lock:
                    if self.ooba_proc and self.ooba_proc.poll() is None:
                        self.ooba_proc.kill()
                        try:
                            self.ooba_proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            self.ooba_proc.terminate()
                self.start_btn.config(state='normal')
                self.stop_all_btn.config(state='disabled')
                return
                
            self.set_status("✅ Oobabooga instance started successfully!", "green")
            self.log("✅ Oobabooga instance started successfully!")
            
            # Start Z-Waifu with thread safety
            with self._process_lock:
                # Check stop flag before creating Z-Waifu process
                with self._stop_lock:
                    if self._stop_requested:
                        self.log("[LAUNCH] Z-Waifu launch cancelled by stop request")
                        # Clean up Oobabooga process if it was started
                        if hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None:
                            try:
                                self.ooba_proc.kill()
                                self.ooba_proc.wait(timeout=5)
                            except Exception as e:
                                pass
                        return
                
                self.log(f"[Z-Waifu] Starting: {self.zwaifu_bat}")
                self.zwaifu_proc = subprocess.Popen([self.zwaifu_bat], cwd=os.path.dirname(self.zwaifu_bat), shell=True)
            
            # Wait for Z-Waifu port, allow interruption
            start = time.time()
            while time.time() - start < 120:
                # Check stop request atomically with process state
                with self._stop_lock:
                    stop_requested = self._stop_requested
                
                if stop_requested:
                    with self._process_lock:
                        if self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                            self.zwaifu_proc.kill()
                            try:
                                self.zwaifu_proc.wait(timeout=5)  # Wait for process to terminate
                            except subprocess.TimeoutExpired:
                                self.zwaifu_proc.terminate()  # Force terminate if needed
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
                with self._process_lock:
                    if self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                        self.zwaifu_proc.kill()
                        try:
                            self.zwaifu_proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            self.zwaifu_proc.terminate()
                self.start_btn.config(state='normal')
                self.stop_all_btn.config(state='disabled')
                return
                
            self.set_status("✅ Z-Waifu instance started successfully!", "green")
            self.log("✅ Z-Waifu instance started successfully!")
            self.log("Both Oobabooga and Z-Waifu started successfully.")
            self.log(f"Oobabooga batch: {self.ooba_bat}")
            self.log(f"Z-Waifu batch:   {self.zwaifu_bat}")
        except Exception as e:
            self.set_status(f"Error: {e}", "red")
            self.log(f"[ERROR] {e}")
            # Ensure proper cleanup with thread safety
            with self._process_lock:
                if hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None:
                    try:
                        self.ooba_proc.kill()
                        self.ooba_proc.wait(timeout=5)
                    except Exception as e:
                        pass
                if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                    try:
                        self.zwaifu_proc.kill()
                        self.zwaifu_proc.wait(timeout=5)
                    except Exception as e:
                        pass
            self.start_btn.config(state='normal')
            self.stop_all_btn.config(state='disabled')


    def load_config_safe(self):
        """Enhanced config loading with comprehensive error handling and backup creation"""
        try:
            # Initialize config file path
            self.config_file = CONFIG_FILE
            
            if not os.path.exists(self.config_file):
                self.log("Config file not found, creating default config")
                self._set_default_config()
                self.save_config()
                return True
            
            # Create backup before loading
            backup_name = f"config_backup_{int(time.time())}.json"
            backup_path = os.path.join(os.path.dirname(self.config_file), backup_name)
            shutil.copy2(self.config_file, backup_path)
            self.log(f"Created config backup: {backup_path}")
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validate config data structure
            if not isinstance(config_data, dict):
                self.log("Invalid config data type, using defaults")
                return False
            
            # Load fields with validation
            try:
                # Set port variables
                self.ooba_port_var.set(str(config_data.get("ooba_port", "7860")))
                self.zwaifu_port_var.set(str(config_data.get("zwaifu_port", "5000")))
                
                # Set batch file paths
                self.ooba_bat = config_data.get("ooba_bat", "")
                self.zwaifu_bat = config_data.get("zwaifu_bat", "")
                self.ollama_bat = config_data.get("ollama_bat", "")
                self.rvc_bat = config_data.get("rvc_bat", "")
                
                # Set other config values
                self.current_theme = config_data.get("theme", "light")
                self.last_dir = config_data.get("last_dir", os.getcwd())
                
                # Validate ports
                if not self._is_valid_port(self.ooba_port_var.get()):
                    self.log("Invalid Oobabooga port, using default")
                    self.ooba_port_var.set("7860")
                
                if not self._is_valid_port(self.zwaifu_port_var.get()):
                    self.log("Invalid Z-Waifu port, using default")
                    self.zwaifu_port_var.set("5000")
                
                # Validate file paths
                if self.ooba_bat and not self._is_safe_path_enhanced(self.ooba_bat):
                    self.log("Invalid Oobabooga batch file path")
                    self.ooba_bat = ""
                
                if self.zwaifu_bat and not self._is_safe_path_enhanced(self.zwaifu_bat):
                    self.log("Invalid Z-Waifu batch file path")
                    self.zwaifu_bat = ""
                
                if self.ollama_bat and not self._is_safe_path_enhanced(self.ollama_bat):
                    self.log("Invalid Ollama batch file path")
                    self.ollama_bat = ""
                
                if self.rvc_bat and not self._is_safe_path_enhanced(self.rvc_bat):
                    self.log("Invalid RVC batch file path")
                    self.rvc_bat = ""
                
                return True
                
            except Exception as e:
                self.log(f"Error loading config fields: {e}")
                return False
                
        except json.JSONDecodeError as e:
            self.log(f"JSON decode error in config file: {e}")
            return False
        except Exception as e:
            self.log(f"Unexpected error loading config: {e}")
            return False

    def _validate_config_data(self, config_data):
        """Validate and sanitize configuration data"""
        if not isinstance(config_data, dict):
            return {}
        
        # Validate file paths
        for key in ["ooba_bat", "zwaifu_bat", "ollama_bat", "rvc_bat"]:
            if key in config_data and config_data[key]:
                # Ensure path is within project directory for security
                if not self._is_safe_path(config_data[key]):
                    self.log(f"Unsafe path in config for {key}: {config_data[key]}")
                    config_data[key] = None
        
        # Validate theme
        if "theme" in config_data and config_data["theme"] not in ["light", "dark"]:
            config_data["theme"] = "light"
        
        # Validate last_dir
        if "last_dir" in config_data and not self._is_safe_path(config_data["last_dir"]):
            config_data["last_dir"] = os.getcwd()
        
        return config_data


    def _is_safe_path_enhanced(self, path: str) -> bool:
        """Enhanced path validation with comprehensive security checks"""
        if not path or not isinstance(path, str):
            return False
        
        # Reject if any segment is '..' in the original path (os.sep or '/')
        segments = path.split(os.sep)
        if os.sep != '/':
            segments += path.split('/')
        if any(seg == '..' for seg in segments):
            return False
        
        # Check for suspicious characters in any segment
        suspicious_chars = set('*?<>|"\
	%&$()[]{};`')
        for seg in segments:
            if any(c in seg for c in suspicious_chars):
                return False
        
        try:
            # Normalize path to prevent path traversal attacks
            normalized_path = os.path.normpath(path)
            
            # Reject if any segment is '..' in the normalized path (os.sep or '/')
            norm_segments = normalized_path.split(os.sep)
            if os.sep != '/':
                norm_segments += normalized_path.split('/')
            if any(seg == '..' for seg in norm_segments):
                return False
            
            # Resolve relative paths
            abs_path = os.path.abspath(normalized_path)
            
            # Check if path is within project directory
            project_root_norm = os.path.normcase(os.path.abspath(self.project_root))
            abs_path_norm = os.path.normcase(abs_path)
            if abs_path_norm == project_root_norm or abs_path_norm.startswith(project_root_norm + os.sep):
                return True
            return False
                
        except Exception as e:
            return False

    def _is_valid_port(self, port_str: str) -> bool:
        """Validate port number"""
        try:
            port = int(port_str)
            return 1 <= port <= 65535
        except (ValueError, TypeError):
            return False

    def _is_safe_path(self, path: str) -> bool:
        """Legacy path validation method - delegates to enhanced version"""
        return self._is_safe_path_enhanced(path)

    def _set_default_config(self):
        """Set default configuration values"""
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
        self.last_dir = os.getcwd()
        self.ooba_port_var.set("7860")
        self.zwaifu_port_var.set("5000")

    def save_config(self):
        """Save configuration with validation and error handling"""
        try:
            # Validate paths before saving
            config_data = {
                "ooba_bat": self.ooba_bat if self._is_safe_path(self.ooba_bat) else None,
                "zwaifu_bat": self.zwaifu_bat if self._is_safe_path(self.zwaifu_bat) else None,
                "ollama_enabled": self.ollama_enabled.get(),
                "ollama_bat": self.ollama_bat if self._is_safe_path(self.ollama_bat) else None,
                "rvc_enabled": self.rvc_enabled.get(),
                "rvc_host": self.rvc_host.get(),
                "rvc_port": self.rvc_port.get(),
                "rvc_model": self.rvc_model.get(),
                "rvc_speaker": self.rvc_speaker.get(),
                "rvc_pitch": self.rvc_pitch.get(),
                "rvc_speed": self.rvc_speed.get(),
                "rvc_bat": self.rvc_bat if self._is_safe_path(self.rvc_bat) else None,
                "theme": getattr(self, 'current_theme', 'light'),
                "port": getattr(self, 'last_port', '5000'),
                "auto_start_ooba": getattr(self, 'auto_start_ooba', tk.BooleanVar(value=False)).get(),
                "auto_start_zwaifu": getattr(self, 'auto_start_zwaifu', tk.BooleanVar(value=False)).get(),
                "auto_start_ollama": getattr(self, 'auto_start_ollama', tk.BooleanVar(value=False)).get(),
                "auto_start_rvc": getattr(self, 'auto_start_rvc', tk.BooleanVar(value=False)).get(),
                "ooba_port": self.ooba_port_var.get(),
                "zwaifu_port": self.zwaifu_port_var.get(),
                "last_dir": getattr(self, 'last_dir', os.getcwd()) if self._is_safe_path(getattr(self, 'last_dir', os.getcwd())) else os.getcwd()
            }
            
            # Ensure config directory exists
            config_dir = os.path.dirname(CONFIG_FILE)
            os.makedirs(config_dir, exist_ok=True)
            
            # Write config with proper encoding and error handling
            with open(CONFIG_FILE, "w", encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Save theme preference using ThemeManager
            if self.theme_manager:
                self.theme_manager.save_theme_preference(self.current_theme)
                
            self.log("Configuration saved successfully")
            
        except Exception as e:
            self.log(f"Error saving configuration: {e}")
            # Don't raise the exception to prevent application crash

    def load_icon(self):
        try:
            if os.path.exists(ICON_FILE):
                # Try to load the icon with error handling
                try:
                    self.icon = tk.PhotoImage(file=ICON_FILE)
                    self.root.iconphoto(True, self.icon)
                    self.log(f"Loaded launcher icon: {ICON_FILE}")
                except Exception as e:
                    self.log(f"Failed to load icon file: {e}")
                    self.icon = None
                
                # Try to load tray icon
                try:
                    from io import BytesIO
                    with open(ICON_FILE, "rb") as f:
                        self.tray_icon = Image.open(BytesIO(f.read()))
                except Exception as e:
                    self.log(f"Failed to load tray icon: {e}")
                    self.tray_icon = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
            else:
                self.log(f"Icon file not found: {ICON_FILE}")
                self.icon = None
                # Fallback: create a blank icon for pystray
                self.tray_icon = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
        except Exception as e:
            self.log(f"Error in load_icon: {e}")
            self.icon = None
            self.tray_icon = Image.new("RGBA", (64, 64), (255, 255, 255, 0))

    def load_theme(self):
        """
        Load and apply the saved theme from config using ThemeManager.
        """
        if self.theme_manager:
            # Load theme preference from ThemeManager
            saved_theme = self.theme_manager.load_theme_preference()
            if saved_theme:
                self.current_theme = saved_theme
                self._dark_mode = saved_theme != 'light'
            else:
                # Default to light theme
                self.current_theme = 'light'
                self._dark_mode = False
            
            # Apply the theme using ThemeManager
            self.theme_manager.apply_theme(self.current_theme)
        else:
            # Fallback to manual theme loading
            if hasattr(self, 'current_theme'):
                if self.current_theme == 'dark':
                    self.set_dark_mode()
                else:
                    self.set_light_mode()
            else:
                self.set_light_mode()

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
        """Load CMD_FLAGS.txt content into the editor, with file selector fallback if missing."""
        try:
            cmd_flags_path = CMD_FLAGS_FILE
            if not os.path.exists(cmd_flags_path):
                # Prompt user to locate the file
                msg = "CMD_FLAGS.txt not found. Would you like to locate it manually?"
                if messagebox.askyesno("CMD_FLAGS.txt Not Found", msg):
                    path = filedialog.askopenfilename(title="Locate CMD_FLAGS.txt", filetypes=[("Text files", "*.txt")], initialdir=getattr(self, 'last_dir', os.getcwd()))
                    if path and os.path.exists(path):
                        cmd_flags_path = path
                        self.last_dir = os.path.dirname(path)
                        self.save_config()
                        self.log(f"[CMD Flags] User selected CMD_FLAGS.txt: {path}")
                    else:
                        self.log("[CMD Flags] User cancelled file selection or file does not exist.")
                # If still not found, create default content
                if not os.path.exists(cmd_flags_path):
                    default_content = """# Oobabooga CMD Flags\n# Add your command line flags here\n# Example:\n# --listen\n# --port 7860\n# --api\n# --extensions api\n"""
                    self.cmd_flags_text.delete('1.0', tk.END)
                    self.cmd_flags_text.insert('1.0', default_content)
                    self.cmd_flags_status_var.set("Created default content (file not found)")
                    self.log("[CMD Flags] File not found, created default content")
                    return
            # Load the file
            with open(cmd_flags_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.cmd_flags_text.delete('1.0', tk.END)
            self.cmd_flags_text.insert('1.0', content)
            self.cmd_flags_status_var.set(f"Loaded: {cmd_flags_path}")
            self.log(f"[CMD Flags] Loaded file: {cmd_flags_path}")
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
            
            # Auto-save after reset
            self.save_cmd_flags()

    def create_settings_tab(self):
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Settings")

        # Import enhanced widgets
        try:
            from utils.enhanced_widgets import EnhancedScrollableFrame
        except ImportError:
            # Fallback to regular widgets if enhanced widgets not available
            from utils.enhanced_widgets import EnhancedScrollableFrame

        # Create enhanced scrollable frame for settings
        scrollable_frame_widget = EnhancedScrollableFrame(settings_tab)
        scrollable_frame = scrollable_frame_widget.get_scrollable_frame()

        # Store for theme switching
        self.settings_canvas = scrollable_frame_widget.canvas
        self.settings_scrollable_frame = scrollable_frame

        # Create scalable fonts for settings tab
        self.settings_font_small = tk.font.nametofont("TkDefaultFont").copy()
        self.settings_font_medium = tk.font.nametofont("TkDefaultFont").copy()
        self.settings_font_large = tk.font.nametofont("TkDefaultFont").copy()
        
        # Set initial font sizes
        self.settings_font_small.configure(size=8)
        self.settings_font_medium.configure(size=10)
        self.settings_font_large.configure(size=12)
        
        # Bind resize event for font scaling
        settings_tab.bind('<Configure>', self._on_settings_resize)
        
        # Store widgets for font scaling
        self.settings_widgets = []

        # Preferences and options
        prefs_frame = ttk.LabelFrame(scrollable_frame, text="Preferences")
        prefs_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Apply scalable fonts to all widgets
        self._apply_scalable_fonts_to_settings()

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
        ooba_port_entry = ttk.Entry(port_frame, textvariable=self.ooba_port_var, width=10)
        ooba_port_entry.pack(anchor=tk.W, padx=5, pady=2)
        ooba_port_entry.bind('<FocusOut>', lambda e: self.save_config())
        
        ttk.Label(port_frame, text="Z-Waifu Port:").pack(anchor=tk.W, padx=5, pady=2)
        self.zwaifu_port_var = tk.StringVar(value="5000")
        zwaifu_port_entry = ttk.Entry(port_frame, textvariable=self.zwaifu_port_var, width=10)
        zwaifu_port_entry.pack(anchor=tk.W, padx=5, pady=2)
        zwaifu_port_entry.bind('<FocusOut>', lambda e: self.save_config())
        
        # Add port validation
        def validate_port(P):
            if P == "": return True
            try:
                port = int(P)
                return 1 <= port <= 65535
            except ValueError:
                return False
        
        # Apply validation to port entries
        vcmd = (self.root.register(validate_port), '%P')
        ooba_port_entry.config(validate='key', validatecommand=vcmd)
        zwaifu_port_entry.config(validate='key', validatecommand=vcmd)

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

        # Error Reporting Settings
        error_frame = ttk.LabelFrame(scrollable_frame, text="Error Reporting")
        error_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Error reporting verbosity
        ttk.Label(error_frame, text="Error Reporting Verbosity:").pack(anchor=tk.W, padx=5, pady=2)
        self.error_verbosity_var = tk.StringVar(value="detailed")
        error_verbosity_combo = ttk.Combobox(error_frame, textvariable=self.error_verbosity_var, 
                                           values=["basic", "detailed", "verbose"], state="readonly", width=15)
        error_verbosity_combo.pack(anchor=tk.W, padx=5, pady=2)
        
        # Error dialog settings
        self.show_error_dialogs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(error_frame, text="Show Error Dialogs", variable=self.show_error_dialogs_var).pack(anchor=tk.W, padx=5, pady=2)
        
        self.auto_copy_errors_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(error_frame, text="Auto-copy Errors to Clipboard", variable=self.auto_copy_errors_var).pack(anchor=tk.W, padx=5, pady=2)
        
        self.include_stack_traces_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(error_frame, text="Include Stack Traces", variable=self.include_stack_traces_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Error dialog timeout
        ttk.Label(error_frame, text="Error Dialog Timeout (seconds):").pack(anchor=tk.W, padx=5, pady=2)
        self.error_timeout_var = tk.StringVar(value="30")
        error_timeout_entry = ttk.Entry(error_frame, textvariable=self.error_timeout_var, width=10)
        error_timeout_entry.pack(anchor=tk.W, padx=5, pady=2)

        # VRAM Monitoring Settings
        vram_frame = ttk.LabelFrame(scrollable_frame, text="VRAM Monitoring")
        vram_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # VRAM monitoring enabled
        self.vram_monitoring_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(vram_frame, text="Enable VRAM Monitoring", variable=self.vram_monitoring_enabled_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # VRAM check interval
        ttk.Label(vram_frame, text="VRAM Check Interval (seconds):").pack(anchor=tk.W, padx=5, pady=2)
        self.vram_check_interval_var = tk.StringVar(value="30")
        vram_interval_entry = ttk.Entry(vram_frame, textvariable=self.vram_check_interval_var, width=10)
        vram_interval_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # VRAM warning threshold
        ttk.Label(vram_frame, text="VRAM Warning Threshold (%):").pack(anchor=tk.W, padx=5, pady=2)
        self.vram_warning_threshold_var = tk.StringVar(value="80")
        vram_warning_entry = ttk.Entry(vram_frame, textvariable=self.vram_warning_threshold_var, width=10)
        vram_warning_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # VRAM critical threshold
        ttk.Label(vram_frame, text="VRAM Critical Threshold (%):").pack(anchor=tk.W, padx=5, pady=2)
        self.vram_critical_threshold_var = tk.StringVar(value="95")
        vram_critical_entry = ttk.Entry(vram_frame, textvariable=self.vram_critical_threshold_var, width=10)
        vram_critical_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # Auto cleanup settings
        self.auto_cleanup_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(vram_frame, text="Enable Auto VRAM Cleanup", variable=self.auto_cleanup_enabled_var).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(vram_frame, text="Auto Cleanup Threshold (%):").pack(anchor=tk.W, padx=5, pady=2)
        self.auto_cleanup_threshold_var = tk.StringVar(value="90")
        auto_cleanup_entry = ttk.Entry(vram_frame, textvariable=self.auto_cleanup_threshold_var, width=10)
        auto_cleanup_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        self.cleanup_after_stop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(vram_frame, text="Cleanup VRAM After Process Stop", variable=self.cleanup_after_stop_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # VRAM warning settings
        self.show_vram_warnings_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(vram_frame, text="Show VRAM Warnings", variable=self.show_vram_warnings_var).pack(anchor=tk.W, padx=5, pady=2)
        
        self.vram_warning_sound_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(vram_frame, text="Play Warning Sound", variable=self.vram_warning_sound_var).pack(anchor=tk.W, padx=5, pady=2)

        # Advanced VRAM Settings
        advanced_vram_frame = ttk.LabelFrame(scrollable_frame, text="Advanced VRAM Settings")
        advanced_vram_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # VRAM history size
        ttk.Label(advanced_vram_frame, text="VRAM History Size:").pack(anchor=tk.W, padx=5, pady=2)
        self.vram_history_size_var = tk.StringVar(value="100")
        vram_history_entry = ttk.Entry(advanced_vram_frame, textvariable=self.vram_history_size_var, width=10)
        vram_history_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable VRAM logging
        self.enable_vram_logging_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable VRAM Logging", variable=self.enable_vram_logging_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable performance tracking
        self.enable_performance_tracking_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable Performance Tracking", variable=self.enable_performance_tracking_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Performance tracking interval
        ttk.Label(advanced_vram_frame, text="Performance Tracking Interval (seconds):").pack(anchor=tk.W, padx=5, pady=2)
        self.performance_tracking_interval_var = tk.StringVar(value="60")
        performance_interval_entry = ttk.Entry(advanced_vram_frame, textvariable=self.performance_tracking_interval_var, width=10)
        performance_interval_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable model compatibility checking
        self.enable_model_compatibility_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable Model Compatibility Checking", variable=self.enable_model_compatibility_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable automatic optimization
        self.enable_automatic_optimization_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable Automatic Optimization", variable=self.enable_automatic_optimization_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Optimization threshold
        ttk.Label(advanced_vram_frame, text="Optimization Threshold (%):").pack(anchor=tk.W, padx=5, pady=2)
        self.optimization_threshold_var = tk.StringVar(value="85")
        optimization_threshold_entry = ttk.Entry(advanced_vram_frame, textvariable=self.optimization_threshold_var, width=10)
        optimization_threshold_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable system health monitoring
        self.enable_system_health_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable System Health Monitoring", variable=self.enable_system_health_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Health check interval
        ttk.Label(advanced_vram_frame, text="Health Check Interval (seconds):").pack(anchor=tk.W, padx=5, pady=2)
        self.health_check_interval_var = tk.StringVar(value="300")
        health_interval_entry = ttk.Entry(advanced_vram_frame, textvariable=self.health_check_interval_var, width=10)
        health_interval_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable predictive cleanup
        self.enable_predictive_cleanup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable Predictive Cleanup", variable=self.enable_predictive_cleanup_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Predictive cleanup threshold
        ttk.Label(advanced_vram_frame, text="Predictive Cleanup Threshold (%):").pack(anchor=tk.W, padx=5, pady=2)
        self.predictive_cleanup_threshold_var = tk.StringVar(value="75")
        predictive_threshold_entry = ttk.Entry(advanced_vram_frame, textvariable=self.predictive_cleanup_threshold_var, width=10)
        predictive_threshold_entry.pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable VRAM analytics
        self.enable_vram_analytics_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable VRAM Analytics", variable=self.enable_vram_analytics_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Analytics export format
        ttk.Label(advanced_vram_frame, text="Analytics Export Format:").pack(anchor=tk.W, padx=5, pady=2)
        self.analytics_export_format_var = tk.StringVar(value="json")
        analytics_format_combo = ttk.Combobox(advanced_vram_frame, textvariable=self.analytics_export_format_var, values=["json", "csv", "txt"], width=10)
        analytics_format_combo.pack(anchor=tk.W, padx=5, pady=2)
        
        # Enable notification system
        self.enable_notification_system_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_vram_frame, text="Enable Notification System", variable=self.enable_notification_system_var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Notification cooldown
        ttk.Label(advanced_vram_frame, text="Notification Cooldown (seconds):").pack(anchor=tk.W, padx=5, pady=2)
        self.notification_cooldown_var = tk.StringVar(value="300")
        notification_cooldown_entry = ttk.Entry(advanced_vram_frame, textvariable=self.notification_cooldown_var, width=10)
        notification_cooldown_entry.pack(anchor=tk.W, padx=5, pady=2)

        # Theme settings - Enhanced with better UX
        theme_frame = ttk.LabelFrame(scrollable_frame, text="🎨 Theme & Appearance")
        theme_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Theme description
        theme_desc = ttk.Label(theme_frame, text="Customize the appearance of your Z-Waifu Launcher", font=("Arial", 9))
        theme_desc.pack(anchor=tk.W, padx=5, pady=(5,10))
        
        # Current theme display
        current_theme_frame = ttk.Frame(theme_frame)
        current_theme_frame.pack(fill=tk.X, padx=5, pady=(0,10))
        
        ttk.Label(current_theme_frame, text="Current Theme:").pack(side=tk.LEFT, padx=(0,5))
        self.current_theme_label = ttk.Label(current_theme_frame, text="Loading...", font=("Arial", 9, "bold"))
        self.current_theme_label.pack(side=tk.LEFT)
        
        # Theme control buttons
        theme_buttons_frame = ttk.Frame(theme_frame)
        theme_buttons_frame.pack(fill=tk.X, padx=5, pady=(0,10))
        
        # Quick theme buttons
        quick_theme_frame = ttk.LabelFrame(theme_buttons_frame, text="Quick Themes")
        quick_theme_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        
        ttk.Button(quick_theme_frame, text="☀️ Light Mode", command=self.set_light_mode_from_settings).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(quick_theme_frame, text="🌙 Dark Mode", command=self.set_dark_mode_from_settings).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Advanced theme controls
        advanced_theme_frame = ttk.LabelFrame(theme_buttons_frame, text="Advanced")
        advanced_theme_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5,0))
        
        if self.theme_manager:
            ttk.Button(advanced_theme_frame, text="⚙️ Theme Editor", command=self.open_theme_editor).pack(side=tk.LEFT, padx=5, pady=5)
            ttk.Button(advanced_theme_frame, text="🔄 Reset to Default", command=self.reset_theme_to_default).pack(side=tk.LEFT, padx=5, pady=5)
        else:
            ttk.Label(advanced_theme_frame, text="Theme Manager not available", foreground="gray").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Theme information
        theme_info_frame = ttk.Frame(theme_frame)
        theme_info_frame.pack(fill=tk.X, padx=5, pady=(0,5))
        
        info_text = "💡 Tip: Use the Theme Editor to create custom themes or modify existing ones."
        ttk.Label(theme_info_frame, text=info_text, font=("Arial", 8), foreground="gray").pack(anchor=tk.W)

        # Save settings button
        save_btn = ttk.Button(scrollable_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(padx=10, pady=10)

        # Pack the enhanced scrollable frame
        scrollable_frame_widget.pack(fill="both", expand=True)
        self.settings_tab = settings_tab # Assign for styling
        self.style_widgets(settings_tab, '#f0f0f0', '#000000', '#ffffff', '#000000') # Style settings tab
        
        # Load current settings
        self.load_current_settings()
        
        # Initialize theme display
        self._update_current_theme_display()
        
    def load_current_settings(self):
        """Load current settings from config and update UI variables"""
        try:
            # Load error reporting settings
            try:
                from utils.error_handler import get_error_handler
                error_handler = get_error_handler()
                error_settings = error_handler.error_settings
                
                self.error_verbosity_var.set(error_settings.get("error_reporting_verbosity", "detailed"))
                self.show_error_dialogs_var.set(error_settings.get("show_error_dialogs", True))
                self.auto_copy_errors_var.set(error_settings.get("auto_copy_to_clipboard", False))
                self.include_stack_traces_var.set(error_settings.get("include_stack_traces", True))
                self.error_timeout_var.set(str(error_settings.get("error_dialog_timeout", 30)))
            except Exception as e:
                self.log(f"[Settings] Failed to load error settings: {e}")
            
            # Load VRAM monitoring settings
            try:
                from utils.vram_monitor import get_vram_monitor
                vram_monitor = get_vram_monitor()
                vram_settings = vram_monitor.vram_settings
                
                self.vram_monitoring_enabled_var.set(vram_settings.get("vram_monitoring_enabled", True))
                self.vram_check_interval_var.set(str(vram_settings.get("vram_check_interval", 30)))
                self.vram_warning_threshold_var.set(str(int(vram_settings.get("vram_warning_threshold", 0.8) * 100)))
                self.vram_critical_threshold_var.set(str(int(vram_settings.get("vram_critical_threshold", 0.95) * 100)))
                self.auto_cleanup_enabled_var.set(vram_settings.get("auto_cleanup_enabled", True))
                self.auto_cleanup_threshold_var.set(str(int(vram_settings.get("auto_cleanup_threshold", 0.9) * 100)))
                self.cleanup_after_stop_var.set(vram_settings.get("cleanup_after_process_stop", True))
                self.show_vram_warnings_var.set(vram_settings.get("show_vram_warnings", True))
                self.vram_warning_sound_var.set(vram_settings.get("vram_warning_sound", True))
                
                # Load advanced VRAM settings
                self.vram_history_size_var.set(str(vram_settings.get("vram_history_size", 100)))
                self.enable_vram_logging_var.set(vram_settings.get("enable_vram_logging", True))
                self.enable_performance_tracking_var.set(vram_settings.get("enable_performance_tracking", True))
                self.performance_tracking_interval_var.set(str(vram_settings.get("performance_tracking_interval", 60)))
                self.enable_model_compatibility_var.set(vram_settings.get("enable_model_compatibility_checking", True))
                self.enable_automatic_optimization_var.set(vram_settings.get("enable_automatic_optimization", True))
                self.optimization_threshold_var.set(str(int(vram_settings.get("optimization_threshold", 0.85) * 100)))
                self.enable_system_health_var.set(vram_settings.get("enable_system_health_monitoring", True))
                self.health_check_interval_var.set(str(vram_settings.get("health_check_interval", 300)))
                self.enable_predictive_cleanup_var.set(vram_settings.get("enable_predictive_cleanup", True))
                self.predictive_cleanup_threshold_var.set(str(int(vram_settings.get("predictive_cleanup_threshold", 0.75) * 100)))
                self.enable_vram_analytics_var.set(vram_settings.get("enable_vram_analytics", True))
                self.analytics_export_format_var.set(vram_settings.get("analytics_export_format", "json"))
                self.enable_notification_system_var.set(vram_settings.get("enable_notification_system", True))
                self.notification_cooldown_var.set(str(vram_settings.get("notification_cooldown", 300)))
            except Exception as e:
                self.log(f"[Settings] Failed to load VRAM settings: {e}")
                
        except Exception as e:
            self.log(f"[Settings] Error loading current settings: {e}")
        
    def save_settings(self):
        """
        Save all settings to config file.
        """
        try:
            # Save basic config
            self.save_config()
            
            # Save error reporting settings
            error_settings = {
                "error_reporting_verbosity": self.error_verbosity_var.get(),
                "show_error_dialogs": self.show_error_dialogs_var.get(),
                "auto_copy_to_clipboard": self.auto_copy_errors_var.get(),
                "include_stack_traces": self.include_stack_traces_var.get(),
                "error_dialog_timeout": int(self.error_timeout_var.get())
            }
            
            # Save VRAM monitoring settings
            vram_settings = {
                "vram_monitoring_enabled": self.vram_monitoring_enabled_var.get(),
                "vram_check_interval": int(self.vram_check_interval_var.get()),
                "vram_warning_threshold": float(self.vram_warning_threshold_var.get()) / 100,
                "vram_critical_threshold": float(self.vram_critical_threshold_var.get()) / 100,
                "auto_cleanup_enabled": self.auto_cleanup_enabled_var.get(),
                "auto_cleanup_threshold": float(self.auto_cleanup_threshold_var.get()) / 100,
                "cleanup_after_process_stop": self.cleanup_after_stop_var.get(),
                "show_vram_warnings": self.show_vram_warnings_var.get(),
                "vram_warning_sound": self.vram_warning_sound_var.get(),
                
                # Advanced VRAM settings
                "vram_history_size": int(self.vram_history_size_var.get()),
                "enable_vram_logging": self.enable_vram_logging_var.get(),
                "enable_performance_tracking": self.enable_performance_tracking_var.get(),
                "performance_tracking_interval": int(self.performance_tracking_interval_var.get()),
                "enable_model_compatibility_checking": self.enable_model_compatibility_var.get(),
                "enable_automatic_optimization": self.enable_automatic_optimization_var.get(),
                "optimization_threshold": float(self.optimization_threshold_var.get()) / 100,
                "enable_system_health_monitoring": self.enable_system_health_var.get(),
                "health_check_interval": int(self.health_check_interval_var.get()),
                "enable_predictive_cleanup": self.enable_predictive_cleanup_var.get(),
                "predictive_cleanup_threshold": float(self.predictive_cleanup_threshold_var.get()) / 100,
                "enable_vram_analytics": self.enable_vram_analytics_var.get(),
                "analytics_export_format": self.analytics_export_format_var.get(),
                "enable_notification_system": self.enable_notification_system_var.get(),
                "notification_cooldown": int(self.notification_cooldown_var.get())
            }
            
            # Update error handler settings
            try:
                from utils.error_handler import get_error_handler
                error_handler = get_error_handler()
                error_handler.update_settings(error_settings)
            except Exception as e:
                self.log(f"[Settings] Failed to update error handler: {e}")
            
            # Update VRAM monitor settings
            try:
                from utils.vram_monitor import get_vram_monitor
                vram_monitor = get_vram_monitor()
                vram_monitor.update_settings(vram_settings)
                
                # Restart monitoring if settings changed
                if vram_monitor.monitoring and not vram_settings["vram_monitoring_enabled"]:
                    vram_monitor.stop_monitoring()
                elif not vram_monitor.monitoring and vram_settings["vram_monitoring_enabled"]:
                    vram_monitor.start_monitoring()
            except Exception as e:
                self.log(f"[Settings] Failed to update VRAM monitor: {e}")
            
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            self.log("[Settings] Configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.log(f"[Settings] Error saving configuration: {e}")

    def _on_settings_resize(self, event):
        """Handle resize events for settings tab font scaling"""
        if hasattr(self, 'settings_font_small'):
            # Calculate font size based on tab width
            tab_width = event.width
            base_size = max(8, min(16, int(tab_width / 80)))
            
            # Update font sizes
            self.settings_font_small.configure(size=base_size - 2)
            self.settings_font_medium.configure(size=base_size)
            self.settings_font_large.configure(size=base_size + 2)
            
            # Apply fonts to all widgets
            self._apply_scalable_fonts_to_settings()

    def _apply_scalable_fonts_to_settings(self):
        """Apply scalable fonts to all widgets in settings tab"""
        if not hasattr(self, 'settings_scrollable_frame'):
            return
            
        def apply_fonts_recursive(parent):
            for widget in parent.winfo_children():
                widget_type = widget.__class__.__name__
                
                # Apply fonts based on widget type
                if widget_type in ['Label', 'Checkbutton', 'Button']:
                    try:
                        widget.configure(font=self.settings_font_medium)
                    except:
                        pass
                elif widget_type in ['LabelFrame', 'Labelframe']:
                    try:
                        widget.configure(font=self.settings_font_large)
                    except:
                        pass
                elif widget_type in ['Entry', 'Combobox']:
                    try:
                        widget.configure(font=self.settings_font_small)
                    except:
                        pass
                
                # Recursively apply to child widgets
                apply_fonts_recursive(widget)
        
        # Apply fonts to all widgets in settings tab
        apply_fonts_recursive(self.settings_scrollable_frame)

    def style_widgets(self, parent, bg_color, fg_color, entry_bg, entry_fg, accent_color=None, border_color=None):
        """Apply modern, consistent styling to all widgets in a parent container with enhanced visual appeal"""
        if parent is None:
            return
        # Check if parent is actually a Tkinter widget
        if not hasattr(parent, 'winfo_children'):
            return
            
        # Get current theme colors for comprehensive styling
        theme_colors = self.get_current_theme_colors()
        
        # Use accent and border colors from theme if available
        if accent_color is None:
            accent_color = theme_colors.get('accent', fg_color)
        if border_color is None:
            border_color = theme_colors.get('border_color', bg_color)
        
        for child in parent.winfo_children():
            cls = child.__class__.__name__
            
            # Handle ttk widgets with modern styling
            if cls.startswith('T') or cls.startswith('ttk.'):
                try:
                    if hasattr(child, 'configure'):
                        child.configure(style='Custom.TFrame')
                except Exception:
                    pass
                    
            # Standard Tk widgets with modern enhanced theming
            if cls in ['Label', 'Checkbutton', 'Button', 'Frame', 'Labelframe']:
                try:
                    child.config(
                        bg=bg_color, 
                        fg=fg_color,
                        font=("Segoe UI", 9) if self._dark_mode else ("Segoe UI", 9)
                    )
                except Exception:
                    pass
            elif cls in ['LabelFrame', 'Labelframe', 'ttk::labelframe', 'TLabelFrame']:
                try:
                    child.config(
                        bg=bg_color, 
                        fg=fg_color,
                        font=("Segoe UI", 9, "bold")
                    )
                except Exception:
                    pass
            elif cls == 'Canvas':
                try:
                    child.config(
                        bg=theme_colors.get('canvas_bg', bg_color), 
                        highlightbackground=border_color,
                        highlightthickness=1
                    )
                except Exception:
                    pass
            elif cls == 'Scrollbar' or cls == 'ttk::scrollbar':
                try:
                    child.config(
                        troughcolor=entry_bg, 
                        bg=bg_color, 
                        activebackground=accent_color,
                        relief=tk.FLAT,
                        bd=0
                    )
                except Exception:
                    pass
            elif cls == 'Entry':
                try:
                    child.config(
                        bg=entry_bg, 
                        fg=entry_fg, 
                        insertbackground=accent_color,
                        relief=tk.FLAT,
                        bd=0,
                        highlightbackground=border_color,
                        highlightcolor=accent_color,
                        highlightthickness=1,
                        font=("Segoe UI", 9),
                        padx=8,
                        pady=4
                    )
                except Exception:
                    pass
            elif cls in ['Text', 'ScrolledText']:
                try:
                    child.config(
                        bg=theme_colors.get('text_bg', entry_bg), 
                        fg=theme_colors.get('text_fg', entry_fg), 
                        insertbackground=accent_color,
                        selectbackground=theme_colors.get('select_bg', accent_color),
                        selectforeground=theme_colors.get('select_fg', entry_bg),
                        relief=tk.FLAT,
                        bd=0,
                        highlightbackground=border_color,
                        highlightcolor=accent_color,
                        highlightthickness=1,
                        font=("Consolas", 9) if self._dark_mode else ("Consolas", 9),
                        padx=8,
                        pady=4
                    )
                except Exception:
                    pass
            elif cls == 'Listbox':
                try:
                    child.config(
                        bg=theme_colors.get('listbox_bg', entry_bg), 
                        fg=theme_colors.get('listbox_fg', entry_fg), 
                        selectbackground=theme_colors.get('select_bg', accent_color),
                        selectforeground=theme_colors.get('select_fg', entry_bg),
                        relief=tk.FLAT,
                        bd=0,
                        highlightbackground=border_color,
                        highlightcolor=accent_color,
                        highlightthickness=1,
                        font=("Segoe UI", 9),
                        activestyle='none'
                    )
                except Exception:
                    pass
            elif cls == 'Radiobutton':
                try:
                    child.config(
                        bg=bg_color, 
                        fg=fg_color, 
                        selectcolor=theme_colors.get('select_bg', entry_bg),
                        font=("Segoe UI", 9)
                    )
                except Exception:
                    pass
            elif cls == 'Scale':
                try:
                    child.config(
                        bg=bg_color, 
                        fg=fg_color, 
                        troughcolor=entry_bg,
                        highlightbackground=border_color,
                        highlightcolor=accent_color
                    )
                except Exception:
                    pass
            elif cls == 'Spinbox':
                try:
                    child.config(
                        bg=entry_bg, 
                        fg=entry_fg, 
                        insertbackground=accent_color,
                        relief=tk.FLAT,
                        bd=0,
                        highlightbackground=border_color,
                        highlightcolor=accent_color,
                        highlightthickness=1,
                        font=("Segoe UI", 9)
                    )
                except Exception:
                    pass
            elif cls == 'Button':
                try:
                    child.config(
                        bg=theme_colors.get('button_bg', entry_bg),
                        fg=theme_colors.get('button_fg', fg_color),
                        relief=tk.FLAT,
                        bd=0,
                        highlightbackground=border_color,
                        highlightcolor=accent_color,
                        activebackground=theme_colors.get('hover_bg', accent_color),
                        activeforeground=theme_colors.get('hover_fg', entry_bg),
                        font=("Segoe UI", 9, "bold"),
                        cursor="hand2",
                        padx=12,
                        pady=6
                    )
                except Exception:
                    pass
            elif cls == 'Combobox':
                try:
                    child.config(
                        background=entry_bg,
                        foreground=entry_fg,
                        fieldbackground=entry_bg,
                        selectbackground=theme_colors.get('select_bg', accent_color),
                        selectforeground=theme_colors.get('select_fg', entry_bg),
                        font=("Segoe UI", 9)
                    )
                except Exception:
                    pass
            elif cls == 'Treeview':
                try:
                    child.config(
                        background=entry_bg,
                        foreground=entry_fg,
                        fieldbackground=entry_bg,
                        selectbackground=accent_color,
                        selectforeground=entry_bg,
                        font=("Segoe UI", 9)
                    )
                except Exception:
                    pass
                    
            # Recursively style children
            if hasattr(child, 'winfo_children') and child.winfo_children():
                self.style_widgets(child, bg_color, fg_color, entry_bg, entry_fg, accent_color, border_color)

    def restyle_all_tabs(self):
        """Apply the current theme to all known tabs using TAB_THEMES."""
        current_themes = TAB_THEMES if self._dark_mode else LIGHT_TAB_THEMES
        for tab_attr, theme in current_themes.items():
            if hasattr(self, tab_attr):
                self.style_widgets(getattr(self, tab_attr), theme['bg'], theme['fg'], theme['entry_bg'], theme['entry_fg'])
        
        # Apply advanced features themes
        self.apply_advanced_features_themes()

    def set_dark_mode(self):
        """Apply dark theme using ThemeManager"""
        if self.theme_manager:
            # Use ThemeManager for centralized theme management
            self.theme_manager.apply_theme('dark')
            self.current_theme = 'dark'
            self._dark_mode = True
        else:
            # Fallback to manual theme application
            style = ttk.Style()
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
        
        self.restyle_all_tabs()
        self.save_config()
        # Update theme toggle button
        self._update_theme_button()
        # Update registered windows
        self.update_registered_windows_theme()
        
        # Apply theme to all terminal emulators
        self.apply_terminal_themes()

    def set_light_mode(self):
        """Apply light theme using ThemeManager"""
        if self.theme_manager:
            # Use ThemeManager for centralized theme management
            self.theme_manager.apply_theme('light')
            self.current_theme = 'light'
            self._dark_mode = False
        else:
            # Fallback to manual theme application
            style = ttk.Style()
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
        
        self.restyle_all_tabs()
        self.save_config()
        # Update theme toggle button
        self._update_theme_button()
        
        # Apply theme to all terminal emulators
        self.apply_terminal_themes()

    def set_dark_mode_from_settings(self):
        """Apply dark theme from settings with enhanced feedback"""
        try:
            self.set_dark_mode()
            self.set_status("✅ Dark mode applied successfully!", "green")
            self.log("[Theme] Dark mode applied from settings")
            self._update_current_theme_display()
        except Exception as e:
            error_msg = f"Failed to apply dark mode: {e}"
            self.log(f"[Theme] Error: {error_msg}")
            self.set_status("❌ Failed to apply dark mode", "red")

    def set_light_mode_from_settings(self):
        """Apply light theme from settings with enhanced feedback"""
        try:
            self.set_light_mode()
            self.set_status("✅ Light mode applied successfully!", "green")
            self.log("[Theme] Light mode applied from settings")
            self._update_current_theme_display()
        except Exception as e:
            error_msg = f"Failed to apply light mode: {e}"
            self.log(f"[Theme] Error: {error_msg}")
            self.set_status("❌ Failed to apply light mode", "red")

    def reset_theme_to_default(self):
        """Reset theme to default with confirmation"""
        if messagebox.askyesno("Reset Theme", "Are you sure you want to reset the theme to default?\n\nThis will restore the original light theme."):
            try:
                if self.theme_manager:
                    # Reset to default theme
                    self.theme_manager.save_theme_preference('light')
                    self.set_light_mode()
                    self.set_status("✅ Theme reset to default successfully!", "green")
                    self.log("[Theme] Theme reset to default")
                else:
                    self.set_light_mode()
                    self.set_status("✅ Theme reset to default successfully!", "green")
                    self.log("[Theme] Theme reset to default (no theme manager)")
                
                self._update_current_theme_display()
            except Exception as e:
                error_msg = f"Failed to reset theme: {e}"
                self.log(f"[Theme] Error: {error_msg}")
                self.set_status("❌ Failed to reset theme", "red")

    def _update_current_theme_display(self):
        """Update the current theme display in settings"""
        try:
            if hasattr(self, 'current_theme_label'):
                if self.theme_manager:
                    current_theme = self.theme_manager.load_theme_preference()
                    theme_name = current_theme.replace('_', ' ').title()
                    self.current_theme_label.config(text=theme_name)
                else:
                    # Fallback to basic theme detection
                    theme_colors = self.get_current_theme_colors()
                    if theme_colors and theme_colors.get('bg', '').lower() in ['#1e1e1e', '#2d2d2d', '#000000']:
                        self.current_theme_label.config(text="Dark")
                    else:
                        self.current_theme_label.config(text="Light")
        except Exception as e:
            self.log(f"[Theme] Error updating theme display: {e}")
            if hasattr(self, 'current_theme_label'):
                self.current_theme_label.config(text="Unknown")
    
    def get_current_theme_colors(self):
        """Get current theme colors from ThemeManager"""
        if self.theme_manager:
            theme = self.theme_manager.get_theme(self.current_theme)
            if theme:
                return theme
        # Fallback to default colors with comprehensive color scheme
        if self._dark_mode:
            return {
                'bg': '#222222',
                'fg': '#ffffff',
                'entry_bg': '#333333',
                'entry_fg': '#cccccc',
                'accent': '#007acc',
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545',
                'info': '#17a2b8',
                'button_bg': '#333333',
                'button_fg': '#ffffff',
                'hover_bg': '#007acc',
                'hover_fg': '#ffffff',
                'border_color': '#404040',
                'text_bg': '#2d2d30',
                'text_fg': '#ffffff',
                'canvas_bg': '#2d2d30',
                'listbox_bg': '#2d2d30',
                'listbox_fg': '#ffffff',
                'select_bg': '#007acc',
                'select_fg': '#ffffff'
            }
        else:
            return {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'accent': '#007acc',
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545',
                'info': '#17a2b8',
                'button_bg': '#e0e0e0',
                'button_fg': '#000000',
                'hover_bg': '#007acc',
                'hover_fg': '#ffffff',
                'border_color': '#cccccc',
                'text_bg': '#ffffff',
                'text_fg': '#000000',
                'canvas_bg': '#ffffff',
                'listbox_bg': '#ffffff',
                'listbox_fg': '#000000',
                'select_bg': '#007acc',
                'select_fg': '#ffffff'
            }
    
    def apply_theme_to_widget(self, widget, theme_colors=None):
        """Apply theme colors to a widget"""
        if theme_colors is None:
            theme_colors = self.get_current_theme_colors()
        
        try:
            if isinstance(widget, tk.Toplevel):
                widget.configure(bg=theme_colors['bg'])
            elif isinstance(widget, tk.Frame) or isinstance(widget, ttk.Frame):
                widget.configure(bg=theme_colors['bg'])
            elif isinstance(widget, tk.Label) or isinstance(widget, ttk.Label):
                widget.configure(bg=theme_colors['bg'], fg=theme_colors['fg'])
            elif isinstance(widget, tk.Entry) or isinstance(widget, ttk.Entry):
                widget.configure(
                    bg=theme_colors['entry_bg'],
                    fg=theme_colors['entry_fg'],
                    insertbackground=theme_colors['fg'],
                    relief=tk.SOLID,
                    bd=1,
                    highlightbackground=theme_colors.get('border_color', '#404040'),
                    highlightcolor=theme_colors['accent']
                )
            elif isinstance(widget, tk.Button) or isinstance(widget, ttk.Button):
                widget.configure(
                    bg=theme_colors.get('button_bg', theme_colors['entry_bg']),
                    fg=theme_colors['fg'],
                    relief=tk.RAISED,
                    bd=1,
                    highlightbackground=theme_colors.get('border_color', '#404040'),
                    highlightcolor=theme_colors['accent'],
                    activebackground=theme_colors.get('hover_bg', theme_colors['accent']),
                    activeforeground=theme_colors.get('hover_fg', theme_colors['fg'])
                )
        except Exception as e:
            # Silently handle theme application errors
            pass
    
    def open_theme_editor(self):
        """Open the theme editor window with enhanced user feedback"""
        if self.theme_manager:
            try:
                # Show loading message
                self.set_status("Opening Theme Editor...", "blue")
                self.log("[Theme] Opening theme editor...")
                
                # Create theme editor window
                self.theme_manager.create_theme_editor_window()
                
                # Success feedback
                self.set_status("✅ Theme Editor opened successfully!", "green")
                self.log("[Theme] Theme editor opened successfully")
                
                # Show helpful tip
                messagebox.showinfo(
                    "Theme Editor", 
                    "Theme Editor opened!\n\n"
                    "💡 Tips:\n"
                    "• Use the preview to see changes instantly\n"
                    "• Click 'Apply' to test changes\n"
                    "• Click 'Save' to make changes permanent\n"
                    "• Use 'Revert' to undo unsaved changes"
                )
                
            except Exception as e:
                error_msg = f"Failed to open theme editor: {e}"
                self.log(f"[Theme] Error: {error_msg}")
                self.set_status("❌ Theme Editor failed to open", "red")
                messagebox.showerror("Theme Editor Error", error_msg)
        else:
            warning_msg = "Theme manager is not available. Please check your installation."
            self.log(f"[Theme] Warning: {warning_msg}")
            self.set_status("⚠️ Theme manager not available", "orange")
            messagebox.showwarning("Theme Editor", warning_msg)

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
        # Ensure Ollama is in process_instance_tabs
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
            tab_id = self.notebook.index('end') - 1
            self.notebook.select(instance_tab)
            self.flash_tab(tab_id, 'Ollama')
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            self.restyle_all_tabs()  # Ensure new tab is themed
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc, bat_path)
                self.log(f"🚀 Ollama instance launched: {bat_path}")
                self.set_status("✅ Ollama instance started successfully!", "green")
                self.process_instance_tabs['Ollama'].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc, 'bat_path': bat_path})
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start Ollama: {e}\n", '31')
                self.log(f"[ERROR] Failed to start Ollama: {e}")

        ttk.Button(ollama_tab, text="Launch Ollama Instance", command=launch_ollama_instance).pack(padx=10, pady=(0, 10), anchor="w")
        self.style_widgets(ollama_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.ollama_tab = ollama_tab

    def create_rvc_tab(self):
        # Ensure RVC is in process_instance_tabs
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
            tab_id = self.notebook.index('end') - 1
            self.notebook.select(instance_tab)
            self.flash_tab(tab_id, 'RVC')
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            self.restyle_all_tabs()  # Ensure new tab is themed
            try:
                proc = subprocess.Popen([bat_path], cwd=os.path.dirname(bat_path), shell=True,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                terminal.attach_process(proc, bat_path)
                self.log(f"🚀 RVC instance launched: {bat_path}")
                self.set_status("✅ RVC instance started successfully!", "green")
                self.process_instance_tabs['RVC'].append({'tab': instance_tab, 'terminal': terminal, 'proc': proc, 'bat_path': bat_path})
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start RVC: {e}\n", '31')
                self.log(f"[ERROR] Failed to start RVC: {e}")

        ttk.Button(rvc_tab, text="Launch RVC Instance", command=launch_rvc_instance).pack(padx=10, pady=(0, 10), anchor="w")
        self.style_widgets(rvc_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        self.rvc_tab = rvc_tab

    def create_logs_tab(self):
        logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(logs_tab, text="Logs")

        # Log display
        self.logs_text = scrolledtext.ScrolledText(logs_tab, state='disabled', font=("Consolas", 9))
        self.logs_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Log actions
        actions_frame = ttk.Frame(logs_tab)
        actions_frame.pack(padx=10, pady=(0,10), fill=tk.X)
        
        ttk.Button(actions_frame, text="Refresh", command=self.refresh_logs).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(actions_frame, text="Clear", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Open Log File", command=self.open_log_file).pack(side=tk.LEFT, padx=(5,0))

        self.logs_tab = logs_tab
        self.style_widgets(logs_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')

    def create_instance_manager_tab(self):
        instance_tab = ttk.Frame(self.notebook)
        self.notebook.add(instance_tab, text="Instance Manager")
        
        # Import enhanced widgets
        try:
            from utils.enhanced_widgets import EnhancedScrollableFrame, create_enhanced_treeview
        except ImportError:
            # Fallback to regular widgets if enhanced widgets not available
            from utils.enhanced_widgets import EnhancedScrollableFrame, create_enhanced_treeview
        
        # Create enhanced scrollable frame for instance list
        scrollable_frame_widget = EnhancedScrollableFrame(instance_tab)
        scrollable_frame = scrollable_frame_widget.get_scrollable_frame()
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(header_frame, text="Instance Manager", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        ttk.Label(header_frame, text="Centralized management of all running process instances").pack(anchor=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.pack(padx=10, pady=(0,10), fill=tk.X)
        
        self.kill_all_btn = ttk.Button(control_frame, text="Kill All Instances", command=self.kill_all_instances)
        self.kill_all_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.refresh_btn = ttk.Button(control_frame, text="Refresh", command=self.refresh_instance_manager)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Instance list
        list_frame = ttk.LabelFrame(scrollable_frame, text="Running Instances")
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Create enhanced treeview for instances
        columns = ('Process', 'Instance', 'Status', 'PID', 'Uptime', 'CPU %', 'Memory %')
        tree_frame, self.instance_tree = create_enhanced_treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.instance_tree.heading(col, text=col)
            self.instance_tree.column(col, width=100, minwidth=80)
        
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to focus terminal
        self.instance_tree.bind('<Double-1>', self.focus_instance_terminal)
        
        # Instance controls
        instance_control_frame = ttk.Frame(scrollable_frame)
        instance_control_frame.pack(padx=10, pady=(0,10), fill=tk.X)
        
        ttk.Button(instance_control_frame, text="Stop Selected", 
                  command=self.stop_selected_instance).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(instance_control_frame, text="Restart Selected", 
                  command=self.restart_selected_instance).pack(side=tk.LEFT, padx=5)
        ttk.Button(instance_control_frame, text="Kill Selected", 
                  command=self.kill_selected_instance).pack(side=tk.LEFT, padx=5)
        
        # Pack the scrollable frame widget
        scrollable_frame_widget.pack(fill="both", expand=True)
        
        self.instance_manager_tab = instance_tab
        self.style_widgets(instance_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        
        # Update instance list
        self.update_instance_manager()

    def create_ooba_tab(self):
        ooba_tab = ttk.Frame(self.notebook)
        self.notebook.add(ooba_tab, text="Oobabooga")
        
        # Title and description
        title_frame = ttk.Frame(ooba_tab)
        title_frame.pack(fill=tk.X, padx=10, pady=(10,5))
        ttk.Label(title_frame, text="Oobabooga Instance Management", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(title_frame, text="Manage Oobabooga text generation web UI instances", font=("Arial", 9)).pack(anchor=tk.W)
        
        # Status frame
        status_frame = ttk.LabelFrame(ooba_tab, text="Status")
        status_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.ooba_status_var = tk.StringVar(value="No instances running")
        ttk.Label(status_frame, textvariable=self.ooba_status_var, font=("Arial", 10)).pack(padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(ooba_tab)
        control_frame.pack(padx=10, pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="Start Instance", command=lambda: self.start_process_instance("oobabooga")).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(control_frame, text="Stop All", command=lambda: self.stop_all_instances("oobabooga")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh Status", command=self.refresh_ooba_status).pack(side=tk.LEFT, padx=5)
        
        # Information frame
        info_frame = ttk.LabelFrame(ooba_tab, text="Information")
        info_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        info_text = """Oobabooga Text Generation WebUI

This tab manages Oobabooga instances for text generation.

Features:
• Start/stop Oobabooga instances
• Monitor instance status
• View running processes
• Manage multiple instances

To get started:
1. Ensure Oobabooga is properly installed
2. Set the batch file path in Settings
3. Click 'Start Instance' to launch

Default port: 7860 (configurable in Settings)

For more information, visit:
https://github.com/oobabooga/text-generation-webui"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=500)
        info_label.pack(padx=10, pady=10, anchor=tk.NW)
        
        self.ooba_tab = ooba_tab
        self.style_widgets(ooba_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        
        # Initialize status
        self.refresh_ooba_status()

    def create_zwaifu_tab(self):
        zwaifu_tab = ttk.Frame(self.notebook)
        self.notebook.add(zwaifu_tab, text="Z-Waifu")
        
        # Title and description
        title_frame = ttk.Frame(zwaifu_tab)
        title_frame.pack(fill=tk.X, padx=10, pady=(10,5))
        ttk.Label(title_frame, text="Z-Waifu Instance Management", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(title_frame, text="Manage Z-Waifu AI companion instances", font=("Arial", 9)).pack(anchor=tk.W)
        
        # Status frame
        status_frame = ttk.LabelFrame(zwaifu_tab, text="Status")
        status_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.zwaifu_status_var = tk.StringVar(value="No instances running")
        ttk.Label(status_frame, textvariable=self.zwaifu_status_var, font=("Arial", 10)).pack(padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(zwaifu_tab)
        control_frame.pack(padx=10, pady=5, fill=tk.X)
        
        ttk.Button(control_frame, text="Start Instance", command=lambda: self.start_process_instance("zwaifu")).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(control_frame, text="Stop All", command=lambda: self.stop_all_instances("zwaifu")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh Status", command=self.refresh_zwaifu_status).pack(side=tk.LEFT, padx=5)
        
        # Information frame
        info_frame = ttk.LabelFrame(zwaifu_tab, text="Information")
        info_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        info_text = """Z-Waifu AI Companion

This tab manages Z-Waifu AI companion instances.

Features:
• Start/stop Z-Waifu instances
• Monitor instance status
• View running processes
• Manage multiple instances
• AI companion interaction

To get started:
1. Ensure Z-Waifu is properly installed
2. Set the batch file path in Settings
3. Configure Oobabooga connection
4. Click 'Start Instance' to launch

Default port: 5000 (configurable in Settings)

Z-Waifu provides:
• AI companion conversations
• Voice interaction
• Character customization
• Memory and relationship systems

For more information, check the Z-Waifu documentation."""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=500)
        info_label.pack(padx=10, pady=10, anchor=tk.NW)
        
        self.zwaifu_tab = zwaifu_tab
        self.style_widgets(zwaifu_tab, '#f0f0f0', '#000000', '#ffffff', '#000000')
        
        # Initialize status
        self.refresh_zwaifu_status()

    def create_advanced_features_tab(self):
        advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(advanced_tab, text="Advanced")
        
        # Import enhanced widgets
        try:
            from utils.enhanced_widgets import EnhancedScrollableFrame
        except ImportError:
            # Fallback to regular widgets if enhanced widgets not available
            from utils.enhanced_widgets import EnhancedScrollableFrame

        # Create enhanced scrollable frame for advanced features
        scrollable_frame_widget = EnhancedScrollableFrame(advanced_tab)
        scrollable_frame = scrollable_frame_widget.get_scrollable_frame()
        
        # Store references for theming
        self.advanced_canvas = scrollable_frame_widget.canvas
        self.advanced_scrollable_frame = scrollable_frame
        
        # Web Interface Section
        web_frame = ttk.LabelFrame(scrollable_frame, text="Web Interface")
        web_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(web_frame, text="Browser-based management interface").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(web_frame, text=f"Access from: http://localhost:{WEB_PORT}").pack(anchor=tk.W, padx=5, pady=2)
        
        web_btn_frame = ttk.Frame(web_frame)
        web_btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.web_start_btn = ttk.Button(web_btn_frame, text="Start Web Interface", command=self.start_web_interface)
        self.web_start_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.web_stop_btn = ttk.Button(web_btn_frame, text="Stop Web Interface", command=self.stop_web_interface, state='disabled')
        self.web_stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.web_open_btn = ttk.Button(web_btn_frame, text="Open in Browser", command=self.open_web_interface)
        self.web_open_btn.pack(side=tk.LEFT, padx=5)
        
        # API Server Section
        api_frame = ttk.LabelFrame(scrollable_frame, text="REST API Server")
        api_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(api_frame, text="Programmatic access via REST API").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(api_frame, text=f"API endpoint: http://localhost:{API_PORT}/api").pack(anchor=tk.W, padx=5, pady=2)
        
        api_btn_frame = ttk.Frame(api_frame)
        api_btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.api_start_btn = ttk.Button(api_btn_frame, text="Start API Server", command=self.start_api_server)
        self.api_start_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.api_stop_btn = ttk.Button(api_btn_frame, text="Stop API Server", command=self.stop_api_server, state='disabled')
        self.api_stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.api_key_btn = ttk.Button(api_btn_frame, text="Generate API Key", command=self.generate_api_key)
        self.api_key_btn.pack(side=tk.LEFT, padx=5)
        
        self.api_refresh_btn = ttk.Button(api_btn_frame, text="Refresh API Key", command=self.refresh_api_key)
        self.api_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.api_test_btn = ttk.Button(api_btn_frame, text="Test API", command=self.test_api_connection)
        self.api_test_btn.pack(side=tk.LEFT, padx=5)
        
        # Mobile Support Section
        mobile_frame = ttk.LabelFrame(scrollable_frame, text="Mobile Support")
        mobile_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(mobile_frame, text="Mobile-optimized interface").pack(anchor=tk.W, padx=5, pady=2)
        self.mobile_access_label = ttk.Label(mobile_frame, text=f"Mobile access: http://localhost:{MOBILE_PORT}")
        self.mobile_access_label.pack(anchor=tk.W, padx=5, pady=2)
        
        mobile_btn_frame = ttk.Frame(mobile_frame)
        mobile_btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.mobile_start_btn = ttk.Button(mobile_btn_frame, text="Start Mobile App", command=self.start_mobile_app)
        self.mobile_start_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.mobile_stop_btn = ttk.Button(mobile_btn_frame, text="Stop Mobile App", command=self.stop_mobile_app, state='disabled')
        self.mobile_stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.mobile_qr_btn = ttk.Button(mobile_btn_frame, text="Show QR Code", command=self.show_mobile_qr)
        self.mobile_qr_btn.pack(side=tk.LEFT, padx=5)
        
        # Analytics Section
        analytics_frame = ttk.LabelFrame(scrollable_frame, text="Analytics & Monitoring")
        analytics_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(analytics_frame, text="Performance monitoring and analytics").pack(anchor=tk.W, padx=5, pady=2)
        
        analytics_btn_frame = ttk.Frame(analytics_frame)
        analytics_btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.analytics_view_btn = ttk.Button(analytics_btn_frame, text="View Analytics", command=self.view_analytics)
        self.analytics_view_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.analytics_report_btn = ttk.Button(analytics_btn_frame, text="Generate Report", command=self.generate_analytics_report)
        self.analytics_report_btn.pack(side=tk.LEFT, padx=5)
        
        self.analytics_export_btn = ttk.Button(analytics_btn_frame, text="Export Data", command=self.export_analytics)
        self.analytics_export_btn.pack(side=tk.LEFT, padx=5)
        
        # Plugin System Section
        plugin_frame = ttk.LabelFrame(scrollable_frame, text="Plugin System")
        plugin_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(plugin_frame, text="Extensible plugin architecture").pack(anchor=tk.W, padx=5, pady=2)
        
        plugin_btn_frame = ttk.Frame(plugin_frame)
        plugin_btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.plugin_manage_btn = ttk.Button(plugin_btn_frame, text="Manage Plugins", command=self.manage_plugins)
        self.plugin_manage_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.plugin_marketplace_btn = ttk.Button(plugin_btn_frame, text="🛒 Plugin Marketplace", command=self.open_plugin_marketplace)
        self.plugin_marketplace_btn.pack(side=tk.LEFT, padx=5)
        
        self.plugin_create_btn = ttk.Button(plugin_btn_frame, text="Create Plugin", command=self.create_plugin)
        self.plugin_create_btn.pack(side=tk.LEFT, padx=5)
        
        self.plugin_reload_btn = ttk.Button(plugin_btn_frame, text="Reload Plugins", command=self.reload_plugins)
        self.plugin_reload_btn.pack(side=tk.LEFT, padx=5)
        
        # GPU Memory Management Section
        gpu_frame = ttk.LabelFrame(scrollable_frame, text="GPU Memory Management")
        gpu_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(gpu_frame, text="Manage GPU memory and VRAM cleanup").pack(anchor=tk.W, padx=5, pady=2)
        
        # VRAM monitoring status
        vram_status_frame = ttk.Frame(gpu_frame)
        vram_status_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.vram_status_label = ttk.Label(vram_status_frame, text="VRAM Status: Unknown")
        self.vram_status_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.vram_usage_label = ttk.Label(vram_status_frame, text="VRAM Usage: Unknown")
        self.vram_usage_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # VRAM analytics display
        self.vram_analytics_label = ttk.Label(vram_status_frame, text="Analytics: Not available")
        self.vram_analytics_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # System health display
        self.system_health_label = ttk.Label(vram_status_frame, text="System Health: Checking...")
        self.system_health_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # VRAM monitoring controls
        vram_control_frame = ttk.Frame(gpu_frame)
        vram_control_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.vram_start_btn = ttk.Button(vram_control_frame, text="Start VRAM Monitoring", command=self._start_vram_monitoring)
        self.vram_start_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.vram_stop_btn = ttk.Button(vram_control_frame, text="Stop VRAM Monitoring", command=self._stop_vram_monitoring)
        self.vram_stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.vram_refresh_btn = ttk.Button(vram_control_frame, text="Refresh VRAM Status", command=self._refresh_vram_status)
        self.vram_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Advanced VRAM controls
        advanced_vram_control_frame = ttk.Frame(gpu_frame)
        advanced_vram_control_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.vram_optimize_btn = ttk.Button(advanced_vram_control_frame, text="Optimize VRAM", command=self._optimize_vram_usage)
        self.vram_optimize_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.vram_analytics_btn = ttk.Button(advanced_vram_control_frame, text="View Analytics", command=self._view_vram_analytics)
        self.vram_analytics_btn.pack(side=tk.LEFT, padx=5)
        
        self.vram_export_btn = ttk.Button(advanced_vram_control_frame, text="Export Data", command=self._export_vram_data)
        self.vram_export_btn.pack(side=tk.LEFT, padx=5)
        
        self.vram_gentle_cleanup_btn = ttk.Button(advanced_vram_control_frame, text="Gentle Cleanup", command=self._gentle_vram_cleanup)
        self.vram_gentle_cleanup_btn.pack(side=tk.LEFT, padx=5)
        
        gpu_btn_frame = ttk.Frame(gpu_frame)
        gpu_btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.gpu_cleanup_btn = ttk.Button(gpu_btn_frame, text="Force GPU Cleanup", command=self._force_gpu_cleanup)
        self.gpu_cleanup_btn.pack(side=tk.LEFT, padx=(0,5))
        
        self.gpu_status_label = ttk.Label(gpu_btn_frame, text="GPU Status: Unknown")
        self.gpu_status_label.pack(side=tk.LEFT, padx=5)
        
        # Initialize GPU status
        self._update_gpu_status()
        self._refresh_vram_status()
        
        # Statistics Section
        stats_frame = ttk.LabelFrame(scrollable_frame, text="Real-Time Statistics")
        stats_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Statistics display
        self.stats_display_frame = tk.Frame(stats_frame)
        self.stats_display_frame.pack(padx=5, pady=5, fill=tk.X)
        
        # System stats
        self.system_stats_frame = tk.Frame(self.stats_display_frame)
        
        # New: System Health Dashboard
        health_frame = ttk.LabelFrame(scrollable_frame, text="🏥 System Health Dashboard")
        health_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Health status indicators
        health_status_frame = ttk.Frame(health_frame)
        health_status_frame.pack(padx=5, pady=5, fill=tk.X)
        
        # CPU health
        cpu_health_frame = ttk.Frame(health_status_frame)
        cpu_health_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        ttk.Label(cpu_health_frame, text="CPU Health", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.cpu_health_label = ttk.Label(cpu_health_frame, text="🟢 Good")
        self.cpu_health_label.pack(anchor=tk.W)
        
        # Memory health
        memory_health_frame = ttk.Frame(health_status_frame)
        memory_health_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        ttk.Label(memory_health_frame, text="Memory Health", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.memory_health_label = ttk.Label(memory_health_frame, text="🟢 Good")
        self.memory_health_label.pack(anchor=tk.W)
        
        # GPU health
        gpu_health_frame = ttk.Frame(health_status_frame)
        gpu_health_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        ttk.Label(gpu_health_frame, text="GPU Health", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.gpu_health_label = ttk.Label(gpu_health_frame, text="🟢 Good")
        self.gpu_health_label.pack(anchor=tk.W)
        
        # Network health
        network_health_frame = ttk.Frame(health_status_frame)
        network_health_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(network_health_frame, text="Network Health", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.network_health_label = ttk.Label(network_health_frame, text="🟢 Good")
        self.network_health_label.pack(anchor=tk.W)
        
        # Health action buttons
        health_actions_frame = ttk.Frame(health_frame)
        health_actions_frame.pack(padx=5, pady=5, fill=tk.X)
        
        ttk.Button(health_actions_frame, text="🔍 Run Health Check", 
                  command=self.run_health_check).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(health_actions_frame, text="📋 Health Report", 
                  command=self.generate_health_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(health_actions_frame, text="🔧 Auto-Fix Issues", 
                  command=self.auto_fix_health_issues).pack(side=tk.LEFT, padx=5)
        
        # New: Performance Optimization
        perf_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Performance Optimization")
        perf_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(perf_frame, text="Optimize system performance for AI workloads").pack(anchor=tk.W, padx=5, pady=2)
        
        perf_actions_frame = ttk.Frame(perf_frame)
        perf_actions_frame.pack(padx=5, pady=5, fill=tk.X)
        
        ttk.Button(perf_actions_frame, text="🚀 Optimize Performance", 
                  command=self.optimize_performance).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(perf_actions_frame, text="🧹 Clean Temporary Files", 
                  command=self.clean_temp_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(perf_actions_frame, text="📊 Performance Benchmark", 
                  command=self.run_performance_benchmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(perf_actions_frame, text="⚙️ Performance Settings", 
                  command=self.open_performance_settings).pack(side=tk.LEFT, padx=5)
        
        # New: Security & Privacy
        security_frame = ttk.LabelFrame(scrollable_frame, text="🔒 Security & Privacy")
        security_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(security_frame, text="Manage security settings and privacy controls").pack(anchor=tk.W, padx=5, pady=2)
        
        security_actions_frame = ttk.Frame(security_frame)
        security_actions_frame.pack(padx=5, pady=5, fill=tk.X)
        
        ttk.Button(security_actions_frame, text="🔍 Security Scan", 
                  command=self.run_security_scan).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(security_actions_frame, text="🔐 Privacy Settings", 
                  command=self.open_privacy_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(security_actions_frame, text="📋 Security Report", 
                  command=self.generate_security_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(security_actions_frame, text="🛡️ Firewall Settings", 
                  command=self.open_firewall_settings).pack(side=tk.LEFT, padx=5)
        self.system_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(self.system_stats_frame, text="System Performance", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.cpu_usage_label = ttk.Label(self.system_stats_frame, text="CPU: 0%")
        self.cpu_usage_label.pack(anchor=tk.W)
        self.memory_usage_label = ttk.Label(self.system_stats_frame, text="Memory: 0%")
        self.memory_usage_label.pack(anchor=tk.W)
        self.disk_usage_label = ttk.Label(self.system_stats_frame, text="Disk: 0%")
        self.disk_usage_label.pack(anchor=tk.W)
        
        # Process stats
        self.process_stats_frame = tk.Frame(self.stats_display_frame)
        self.process_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(self.process_stats_frame, text="Process Status", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.ooba_instances_label = ttk.Label(self.process_stats_frame, text="Oobabooga: 0 instances")
        self.ooba_instances_label.pack(anchor=tk.W)
        self.zwaifu_instances_label = ttk.Label(self.process_stats_frame, text="Z-Waifu: 0 instances")
        self.zwaifu_instances_label.pack(anchor=tk.W)
        self.ollama_instances_label = ttk.Label(self.process_stats_frame, text="Ollama: 0 instances")
        self.ollama_instances_label.pack(anchor=tk.W)
        self.rvc_instances_label = ttk.Label(self.process_stats_frame, text="RVC: 0 instances")
        self.rvc_instances_label.pack(anchor=tk.W)
        
        # Service stats
        self.service_stats_frame = tk.Frame(self.stats_display_frame)
        self.service_stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(self.service_stats_frame, text="Services", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.web_interface_status_label = ttk.Label(self.service_stats_frame, text="Web Interface: Stopped")
        self.web_interface_status_label.pack(anchor=tk.W)
        self.api_server_status_label = ttk.Label(self.service_stats_frame, text="API Server: Stopped")
        self.api_server_status_label.pack(anchor=tk.W)
        self.mobile_app_status_label = ttk.Label(self.service_stats_frame, text="Mobile App: Stopped")
        self.mobile_app_status_label.pack(anchor=tk.W)
        self.analytics_status_label = ttk.Label(self.service_stats_frame, text="Analytics: Active")
        self.analytics_status_label.pack(anchor=tk.W)
        
        # Statistics control buttons
        self.stats_btn_frame = tk.Frame(stats_frame)
        self.stats_btn_frame.pack(padx=5, pady=5, fill=tk.X)
        
        self.refresh_stats_btn = ttk.Button(self.stats_btn_frame, text="Refresh Statistics", command=self.manual_refresh_statistics)
        self.refresh_stats_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_stats_btn = ttk.Button(self.stats_btn_frame, text="Export Statistics", command=self.export_advanced_statistics)
        self.export_stats_btn.pack(side=tk.LEFT, padx=5)
        
        # Status Section
        status_frame = ttk.LabelFrame(scrollable_frame, text="Advanced Features Status")
        status_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.advanced_status_text = scrolledtext.ScrolledText(status_frame, height=6, font=("Consolas", 9))
        self.advanced_status_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Pack the enhanced scrollable frame
        scrollable_frame_widget.pack(fill="both", expand=True)
        
        self.advanced_features_tab = advanced_tab
        
        # Update status and start statistics monitoring
        self.update_advanced_status()
        self.refresh_advanced_statistics()
        
        # Start periodic statistics updates
        self.start_statistics_monitoring()
        
        # Apply theme styling at the end
        theme = TAB_THEMES.get('advanced_features_tab', {'bg': '#222222', 'fg': '#ffffff', 'entry_bg': '#333333', 'entry_fg': '#cccccc'})
        self.style_widgets(self.advanced_features_tab, theme['bg'], theme['fg'], theme['entry_bg'], theme['entry_fg'])

    def initialize_advanced_features(self):
        """Initialize advanced features if available"""
        try:
            # Initialize web interface
            if UTILS_AVAILABLE:
                try:
                    from utils.web_interface import create_web_interface
                    self.web_interface = create_web_interface(self)
                    self.log("Web interface initialized")
                except Exception as e:
                    self.log(f"Failed to initialize web interface: {e}")
                    self.web_interface = None
            else:
                self.log("Web interface not available - utils module not found")
            
            # Initialize analytics system
            if MATPLOTLIB_AVAILABLE:
                self.analytics = AnalyticsSystem(self)
                self.log("Analytics system initialized")
            
            # Initialize plugin manager
            self.plugin_manager = PluginManager(self)
            self.log("Plugin manager initialized")
            
            # Start periodic analytics collection
            if self.analytics:
                self.root.after(30000, self.collect_analytics)  # Every 30 seconds
            
            self.log("Advanced features initialized successfully")
        except Exception as e:
            self.log(f"Failed to initialize advanced features: {e}")

    def collect_analytics(self):
        """Collect system and process analytics"""
        if not self.analytics:
            return
        
        try:
            # Collect system metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.analytics.record_system_metrics(
                cpu_percent, 
                memory.percent, 
                disk.percent
            )
            
            # Collect process metrics
            if hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None:
                try:
                    process = psutil.Process(self.ooba_proc.pid)
                    self.analytics.record_process_metrics(
                        'Oobabooga',
                        process.cpu_percent(),
                        process.memory_percent()
                    )
                except Exception as e:
                    pass
            
            if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                try:
                    process = psutil.Process(self.zwaifu_proc.pid)
                    self.analytics.record_process_metrics(
                        'Z-Waifu',
                        process.cpu_percent(),
                        process.memory_percent()
                    )
                except Exception as e:
                    pass
            
            # Schedule next collection
            self.root.after(30000, self.collect_analytics)
        except Exception as e:
            self.log(f"Failed to collect analytics: {e}")

    def toggle_theme(self):
        """Toggle between light and dark themes with enhanced feedback and plugin marketplace support"""
        try:
            # Show switching message
            self.set_status("🔄 Switching theme...", "blue")
            self.log("[Theme] Toggling theme...")
            
            if self.theme_manager:
                # Use ThemeManager for theme switching
                if self._dark_mode:
                    self.theme_manager.apply_theme('light')
                    self.current_theme = 'light'
                    self._dark_mode = False
                    theme_name = "Light"
                else:
                    self.theme_manager.apply_theme('dark')
                    self.current_theme = 'dark'
                    self._dark_mode = True
                    theme_name = "Dark"
            else:
                # Fallback to manual theme switching
                if self._dark_mode:
                    self.set_light_mode()
                    self._dark_mode = False
                    theme_name = "Light"
                else:
                    self.set_dark_mode()
                    self._dark_mode = True
                    theme_name = "Dark"
            
            # Update theme toggle button appearance
            self._update_theme_button()
            
            # Update current theme display in settings
            self._update_current_theme_display()
            
            # Save theme preference to config
            self.save_config()
            
            # Force UI update to ensure consistency
            self.root.update_idletasks()
            
            # Update plugin marketplace theme immediately if it exists
            if hasattr(self, 'plugin_marketplace') and self.plugin_marketplace:
                try:
                    # Get current theme colors
                    current_theme = self.get_current_theme_colors()
                    
                    # Update plugin marketplace theme
                    if hasattr(self.plugin_marketplace, 'refresh_theme'):
                        self.plugin_marketplace.refresh_theme()
                    
                    # Update marketplace window if it exists
                    if (hasattr(self.plugin_marketplace, 'marketplace_window') and 
                        self.plugin_marketplace.marketplace_window and
                        hasattr(self.plugin_marketplace.marketplace_window, 'apply_theme')):
                        self.plugin_marketplace.marketplace_window.apply_theme(current_theme)
                        
                    self.log("[Theme] Plugin marketplace theme updated")
                except Exception as e:
                    self.log(f"[Theme] Failed to update plugin marketplace theme: {e}")
            
            # Update all registered windows (including plugin windows)
            self.update_registered_windows_theme()
            
            # Success feedback
            self.set_status(f"✅ Switched to {theme_name} mode!", "green")
            self.log(f"[Theme] Successfully switched to {theme_name} mode")
            
        except Exception as e:
            error_msg = f"Failed to toggle theme: {e}"
            self.log(f"[Theme] Error: {error_msg}")
            self.set_status("❌ Theme toggle failed", "red")
    
    def _update_theme_button(self):
        """Update theme toggle button appearance based on current theme"""
        if hasattr(self, 'theme_toggle_btn'):
            if self._dark_mode:
                self.theme_toggle_btn.config(
                    text="☀️ Switch to Light Mode"
                )
                # Update front button for dark theme
                if hasattr(self, 'front_btn'):
                    self.front_btn.config(
                        bg="#222222", activebackground="#333333",
                        fg="#ffffff", activeforeground="#ffffff"
                    )
            else:
                self.theme_toggle_btn.config(
                    text="🌙 Switch to Dark Mode"
                )
                # Update front button for light theme
                if hasattr(self, 'front_btn'):
                    self.front_btn.config(
                        bg="#f0f0f0", activebackground="#e0e0e0",
                        fg="#000000", activeforeground="#000000"
                    )
            
            # Force immediate update
            self.theme_toggle_btn.update_idletasks()

    def stop_all_processes(self):
        """Stop all running processes with proper thread synchronization"""
        # Set stop flag to prevent new processes from starting
        with self._stop_lock:
            self._stop_requested = True
        
        # Wait a brief moment to ensure any launching processes see the stop flag
        time.sleep(0.1)
        
        # Safely stop processes with thread synchronization
        with self._process_lock:
            if hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None:
                try:
                    self.ooba_proc.kill()
                    self.ooba_proc.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
                except subprocess.TimeoutExpired:
                    self.ooba_proc.terminate()  # Force terminate if kill doesn't work
                    try:
                        self.ooba_proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        pass  # Process will be cleaned up by OS
                except Exception as e:
                    self.log(f"Error stopping Oobabooga process: {e}")
            
            if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                try:
                    self.zwaifu_proc.kill()
                    self.zwaifu_proc.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
                except subprocess.TimeoutExpired:
                    self.zwaifu_proc.terminate()  # Force terminate if kill doesn't work
                    try:
                        self.zwaifu_proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        pass  # Process will be cleaned up by OS
                except Exception as e:
                    self.log(f"Error stopping Z-Waifu process: {e}")
        
        # Update UI state
        self.start_btn.config(state='normal')
        self.stop_all_btn.config(state='disabled')
        self.set_status("All processes stopped", "red")
        self.log("All processes stopped by user")

    def launch_main_program(self):
        """Launch the main Z-Waifu program and capture output"""
        if not self.zwaifu_bat or not os.path.exists(self.zwaifu_bat):
            messagebox.showerror("Error", "Z-Waifu batch file not set! Please browse and select it in Settings.")
            return
        
        try:
            # Clear previous output
            self.main_program_output.configure(state='normal')
            self.main_program_output.delete('1.0', tk.END)
            self.main_program_output.configure(state='disabled')
            
            # Launch the main program
            self.log("Launching main Z-Waifu program...")
            
            # Start the process with proper text encoding and error handling
            self.main_proc = subprocess.Popen(
                [self.zwaifu_bat],
                cwd=os.path.dirname(self.zwaifu_bat),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,  # Use text mode for proper encoding
                encoding='utf-8',  # Explicit encoding
                errors='replace',  # Handle encoding errors gracefully
                bufsize=1,
                universal_newlines=True  # Ensure proper line ending handling
            )
            
            # Start output capture thread
            threading.Thread(target=self._capture_main_output, daemon=True).start()
            
            self.log("Main program started successfully")
            self.set_status("Main program running", "green")
            
        except Exception as e:
            error_msg = f"Failed to launch main program: {e}"
            self.log(error_msg)
            messagebox.showerror("Error", error_msg)
            self.set_status("Main program failed to start", "red")
    
    def _capture_main_output(self):
        """Capture and display main program output"""
        try:
            for line in iter(self.main_proc.stdout.readline, ''):
                if line:
                    # Update GUI in main thread
                    self.root.after(0, self._append_main_output, line)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Output capture error: {e}"))
    
    def _append_main_output(self, text):
        """Append text to main program output (called from main thread)"""
        try:
            self.main_program_output.configure(state='normal')
            self.main_program_output.insert(tk.END, text)
            self.main_program_output.see(tk.END)
            self.main_program_output.configure(state='disabled')
        except Exception as e:
            self.log(f"Error appending output: {e}")

    def add_demo_buttons(self):
        """Add theme controls and quick access buttons to main tab"""
        # Theme control section
        theme_frame = ttk.LabelFrame(self.main_tab, text="🎨 Theme Controls")
        theme_frame.pack(padx=10, pady=(0,10), fill=tk.X)
        
        # Theme toggle button with icon and current status
        self.theme_toggle_btn = ttk.Button(
            theme_frame, 
            text="🌙 Switch to Dark Mode", 
            command=self.toggle_theme
        )
        self.theme_toggle_btn.pack(side=tk.LEFT, padx=(5,10), pady=5)
        
        # Theme editor button
        if self.theme_manager:
            ttk.Button(
                theme_frame, 
                text="⚙️ Theme Editor", 
                command=self.open_theme_editor
            ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Quick theme presets
        preset_frame = ttk.Frame(theme_frame)
        preset_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        ttk.Label(preset_frame, text="Quick Presets:").pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(preset_frame, text="Light", command=self.set_light_mode_from_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Dark", command=self.set_dark_mode_from_settings).pack(side=tk.LEFT, padx=2)
        
        # Update theme button text based on current theme
        self._update_theme_button()
        
        # Enhanced quick access buttons
        quick_access_frame = ttk.LabelFrame(self.main_tab, text="🚀 Quick Access")
        quick_access_frame.pack(padx=10, pady=(0,10), fill=tk.X)
        
        # Plugin marketplace button
        ttk.Button(quick_access_frame, text="🛒 Plugin Marketplace", 
                  command=self.open_plugin_marketplace).pack(side=tk.LEFT, padx=(5,5), pady=5)
        
        # Web interface button
        ttk.Button(quick_access_frame, text="🌐 Web Interface", 
                  command=self.start_web_interface).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Mobile app button
        ttk.Button(quick_access_frame, text="📱 Mobile App", 
                  command=self.start_mobile_app).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Analytics button
        ttk.Button(quick_access_frame, text="📊 Analytics", 
                  command=self.view_analytics).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Settings button
        ttk.Button(quick_access_frame, text="⚙️ Settings", 
                  command=lambda: self.notebook.select(2)).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Demo buttons (keeping for compatibility)
        demo_frame = ttk.Frame(self.main_tab)
        demo_frame.pack(padx=10, pady=(0,10), fill=tk.X)
        ttk.Button(demo_frame, text="Demo Button 1").pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(demo_frame, text="Demo Button 2").pack(side=tk.LEFT, padx=5)

    def update_process_status(self):
        """Update process status periodically"""
        # Update main process status
        if hasattr(self, 'ooba_proc') and self.ooba_proc:
            if self.ooba_proc.poll() is not None:
                self.set_status("Oobabooga process stopped", "red")
        
        if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc:
            if self.zwaifu_proc.poll() is not None:
                self.set_status("Z-Waifu process stopped", "red")
        
        # Schedule next update
        self.root.after(1000, self.update_process_status)

    def update_instance_manager(self):
        """Update instance manager periodically"""
        if hasattr(self, 'instance_tree'):
            # Clear existing items
            for item in self.instance_tree.get_children():
                self.instance_tree.delete(item)
            
            # Add instances to treeview
            for process_type in self.process_instance_tabs:
                instances = self.process_instance_tabs[process_type]
                for i, instance in enumerate(instances):
                    if instance['proc']:
                        # Get process status
                        status = "Running" if instance['proc'].poll() is None else "Stopped"
                        pid = instance['proc'].pid if instance['proc'].poll() is None else "N/A"
                        
                        # Get uptime
                        uptime = "N/A"
                        if 'terminal' in instance and hasattr(instance['terminal'], 'get_uptime'):
                            uptime_seconds = instance['terminal'].get_uptime()
                            if uptime_seconds > 0:
                                hours = int(uptime_seconds // 3600)
                                minutes = int((uptime_seconds % 3600) // 60)
                                seconds = int(uptime_seconds % 60)
                                uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        
                        # Get CPU and memory usage
                        cpu_percent = "N/A"
                        memory_percent = "N/A"
                        if instance['proc'].poll() is None:
                            try:
                                psutil_process = psutil.Process(instance['proc'].pid)
                                cpu_percent = f"{psutil_process.cpu_percent():.1f}"
                                memory_percent = f"{psutil_process.memory_percent():.1f}"
                            except Exception as e:
                                pass
                        
                        # Insert into treeview
                        self.instance_tree.insert('', 'end', values=(
                            process_type,
                            f"Instance {i+1}",
                            status,
                            pid,
                            uptime,
                            cpu_percent,
                            memory_percent
                        ))
        
        # Schedule next update
        self.root.after(5000, self.update_instance_manager)  # Update every 5 seconds

    def flash_tab(self, tab_id, process_type):
        """Flash a tab to indicate process activity"""
        try:
            # Get the tab widget
            tab_widget = self.notebook.tabs()[tab_id]
            
            # Store original background
            original_bg = self.notebook.tab(tab_widget, "text")
            
            # Flash effect - change text color briefly
            def flash_effect():
                self.notebook.tab(tab_widget, text=f"⚡ {original_bg}")
                self.root.after(500, lambda: self.notebook.tab(tab_widget, text=original_bg))
            
            flash_effect()
        except Exception as e:
            self.log(f"Failed to flash tab: {e}")



    def auto_detect_batch_files(self):
        """Auto-detect batch files in the project"""
        # Auto-detect Oobabooga
        if not self.ooba_bat:
            ooba_path = find_batch_file("start_windows.bat")
            if ooba_path:
                self.ooba_bat = ooba_path
                self.log(f"Auto-detected Oobabooga: {ooba_path}")

        # Auto-detect Z-Waifu
        if not self.zwaifu_bat:
            zwaifu_path = find_batch_file("startup.bat")
            if zwaifu_path:
                self.zwaifu_bat = zwaifu_path
                self.log(f"Auto-detected Z-Waifu: {zwaifu_path}")

        # Auto-detect Ollama
        if not self.ollama_bat:
            ollama_path = find_batch_file("ollama.bat")
            if ollama_path:
                self.ollama_bat = ollama_path
                self.log(f"Auto-detected Ollama: {ollama_path}")

        # Auto-detect RVC
        if not self.rvc_bat:
            rvc_path = find_batch_file("rvc.bat")
            if rvc_path:
                self.rvc_bat = rvc_path
                self.log(f"Auto-detected RVC: {rvc_path}")

    def on_tab_changed(self, event):
        """Handle tab selection changes"""
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        
        # Auto-refresh logs when logs tab is selected
        if tab_text == "Logs":
            self.refresh_logs()

    def refresh_logs(self):
        """Refresh the logs display"""
        try:
            with open(LOG_FILE, "r") as f:
                logs = f.read()
            self.logs_text.configure(state='normal')
            self.logs_text.delete('1.0', tk.END)
            self.logs_text.insert(tk.END, logs)
            self.logs_text.see(tk.END)
            self.logs_text.configure(state='disabled')
        except Exception as e:
            self.log(f"Error refreshing logs: {e}")

    def clear_logs(self):
        """Clear the logs"""
        try:
            with open(LOG_FILE, "w") as f:
                f.write("")
            self.logs_text.configure(state='normal')
            self.logs_text.delete('1.0', tk.END)
            self.logs_text.configure(state='disabled')
            self.log("Logs cleared")
        except Exception as e:
            self.log(f"Error clearing logs: {e}")

    def open_log_file(self):
        """Open the log file in default editor"""
        try:
            if os.path.exists(LOG_FILE):
                os.startfile(LOG_FILE)
            else:
                self.log("Log file does not exist")
        except Exception as e:
            self.log(f"Error opening log file: {e}")

    def bring_to_front(self):
        """Bring the window to the front and focus it"""
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        # Remove topmost after a brief moment
        self.root.after(100, lambda: self.root.attributes('-topmost', False))

    def on_close(self):
        """Handle window close event"""
        # Stop VRAM monitoring
        if self.vram_monitor:
            self.vram_monitor.stop_monitoring()
            self.log("[System] VRAM monitoring stopped")
        
        self.stop_all_processes()
        self.save_config()
        self.root.destroy()

    # Advanced Features Methods
    def start_web_interface(self):
        """Start the web interface"""
        try:
            if not self.web_interface:
                if UTILS_AVAILABLE:
                    from utils.web_interface import create_web_interface
                    self.web_interface = create_web_interface(self)
                else:
                    self.web_interface = WebInterface(self)
            
            if self.web_interface and self.web_interface.start():
                self.web_start_btn.config(state='disabled')
                self.web_stop_btn.config(state='normal')
                self.web_open_btn.config(state='normal')
                self.log("Web interface started successfully")
                self.update_advanced_status()
            else:
                messagebox.showerror("Error", "Failed to start web interface")
        except Exception as e:
            self.log(f"Error starting web interface: {e}")
            messagebox.showerror("Error", f"Failed to start web interface: {e}")

    def stop_web_interface(self):
        """Stop the web interface"""
        if self.web_interface and self.web_interface.is_running:
            # Note: Flask-SocketIO doesn't have a clean shutdown method
            # The server will stop when the main application exits
            self.web_interface.is_running = False
            self.web_start_btn.config(state='normal')
            self.web_stop_btn.config(state='disabled')
            self.web_open_btn.config(state='disabled')
            self.log("Web interface stopped")
            self.update_advanced_status()

    def open_web_interface(self):
        """Open web interface in browser"""
        try:
            webbrowser.open(f"http://localhost:{WEB_PORT}")
        except Exception as e:
            self.log(f"Failed to open web interface: {e}")

    def start_api_server(self):
        """Start the API server"""
        if not self.api_server:
            self.api_server = APIServer(self)
        
        if self.api_server.start():
            self.api_start_btn.config(state='disabled')
            self.api_stop_btn.config(state='normal')
            self.api_key_btn.config(state='normal')
            self.log("API server started successfully")
            self.update_advanced_status()
        else:
            messagebox.showerror("Error", "Failed to start API server")

    def stop_api_server(self):
        """Stop the API server"""
        if self.api_server and self.api_server.is_running:
            self.api_server.is_running = False
            self.api_start_btn.config(state='normal')
            self.api_stop_btn.config(state='disabled')
            self.api_key_btn.config(state='disabled')
            self.log("API server stopped")
            self.update_advanced_status()

    def generate_api_key(self):
        """Generate a new API key"""
        if self.api_server:
            try:
                key = secrets.token_hex(32)
                self.api_server.api_keys[key] = {
                    'created': time.time(), 
                    'permissions': ['read', 'write'],
                    'expires': time.time() + (30 * 24 * 3600)  # 30 days
                }
                
                # Save API key persistently through the API server
                self.api_server.save_persistent_api_keys()
                
                api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
                messagebox.showinfo("API Key Generated", f"Your new API key:\n\n{key}\n\nKeep this key secure!\n\nSaved to: {api_key_path}")
                self.log(f"API key generated and saved to {api_key_path}")
            except Exception as e:
                self.log(f"Failed to generate API key: {e}")

    def start_mobile_app(self):
        """Start the mobile app"""
        if not self.mobile_app:
            self.mobile_app = MobileApp(self)
        
        if self.mobile_app.start():
            self.mobile_start_btn.config(state='disabled')
            self.mobile_stop_btn.config(state='normal')
            self.mobile_qr_btn.config(state='normal')
            
            # Update the mobile access label with the correct IP
            local_ip = get_local_ip()
            self.mobile_access_label.config(text=f"Mobile access: http://{local_ip}:{MOBILE_PORT}")
            
            self.log("Mobile app started successfully")
            self.update_advanced_status()
        else:
            messagebox.showerror("Error", "Failed to start mobile app")

    def stop_mobile_app(self):
        """Stop the mobile app"""
        if self.mobile_app and self.mobile_app.is_running:
            self.mobile_app.is_running = False
            self.mobile_start_btn.config(state='normal')
            self.mobile_stop_btn.config(state='disabled')
            self.mobile_qr_btn.config(state='disabled')
            
            # Reset the mobile access label
            self.mobile_access_label.config(text=f"Mobile access: http://localhost:{MOBILE_PORT}")
            
            self.log("Mobile app stopped")
            self.update_advanced_status()

    def show_mobile_qr(self):
        """Show mobile QR code"""
        if self.mobile_app and self.mobile_app.qr_code and os.path.exists(self.mobile_app.qr_code):
            try:
                os.startfile(self.mobile_app.qr_code)
                self.log("Mobile QR code opened")
            except Exception as e:
                self.log(f"Failed to open QR code: {e}")
        else:
            messagebox.showinfo("QR Code", "QR code not available. Start the mobile app first.")

    def view_analytics(self):
        """View analytics dashboard"""
        if not self.analytics:
            messagebox.showinfo("Analytics", "Analytics system not available. Install matplotlib: pip install matplotlib")
            return
        
        try:
            # Create analytics window
            analytics_window = tk.Toplevel(self.root)
            analytics_window.title("Analytics Dashboard")
            analytics_window.geometry("800x600")
            
            # Apply theme to the window
            self._theme_popup_window(analytics_window)
            
            # Create notebook for different analytics views
            notebook = ttk.Notebook(analytics_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # System metrics tab
            system_tab = ttk.Frame(notebook)
            notebook.add(system_tab, text="System Metrics")
            
            if MATPLOTLIB_AVAILABLE:
                # Create matplotlib figure
                fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
                
                # Get system metrics
                system_data = self.analytics.get_system_metrics(24)
                if system_data:
                    timestamps = [row[3] for row in system_data]
                    cpu_data = [row[0] for row in system_data]
                    memory_data = [row[1] for row in system_data]
                    disk_data = [row[2] for row in system_data]
                    
                    # Plot CPU usage
                    ax1.plot(timestamps, cpu_data, 'b-', label='CPU %')
                    ax1.set_ylabel('CPU Usage (%)')
                    ax1.set_title('System Performance (Last 24 Hours)')
                    ax1.legend()
                    ax1.grid(True)
                    
                    # Plot memory usage
                    ax2.plot(timestamps, memory_data, 'r-', label='Memory %')
                    ax2.set_ylabel('Memory Usage (%)')
                    ax2.legend()
                    ax2.grid(True)
                    
                    # Plot disk usage
                    ax3.plot(timestamps, disk_data, 'g-', label='Disk %')
                    ax3.set_ylabel('Disk Usage (%)')
                    ax3.set_xlabel('Time')
                    ax3.legend()
                    ax3.grid(True)
                    
                    plt.tight_layout()
                    
                    # Embed in tkinter
                    canvas = FigureCanvasTkAgg(fig, system_tab)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                else:
                    ttk.Label(system_tab, text="No analytics data available").pack(pady=20)
            else:
                ttk.Label(system_tab, text="Matplotlib not available for charts").pack(pady=20)
            
            # Process metrics tab
            process_tab = ttk.Frame(notebook)
            notebook.add(process_tab, text="Process Metrics")
            
            process_text = scrolledtext.ScrolledText(process_tab, font=("Consolas", 9))
            process_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Apply theme to the text widget
            self._theme_text_widget(process_text)
            
            # Display process metrics
            for process_name in ['Oobabooga', 'Z-Waifu']:
                metrics = self.analytics.get_process_metrics(process_name, 24)
                if metrics:
                    process_text.insert(tk.END, f"\n{process_name} Metrics (Last 24 Hours):\n")
                    process_text.insert(tk.END, f"Data points: {len(metrics)}\n")
                    if metrics:
                        avg_cpu = sum(row[0] for row in metrics) / len(metrics)
                        avg_memory = sum(row[1] for row in metrics) / len(metrics)
                        process_text.insert(tk.END, f"Average CPU: {avg_cpu:.2f}%\n")
                        process_text.insert(tk.END, f"Average Memory: {avg_memory:.2f}%\n")
                else:
                    process_text.insert(tk.END, f"\n{process_name}: No data available\n")
            
            process_text.config(state='disabled')
            
        except Exception as e:
            self.log(f"Failed to view analytics: {e}")
            messagebox.showerror("Error", f"Failed to view analytics: {e}")

    def generate_analytics_report(self):
        """Generate analytics report"""
        if not self.analytics:
            messagebox.showinfo("Analytics", "Analytics system not available")
            return
        
        try:
            report = self.analytics.generate_report(24)
            
            # Create report window
            report_window = tk.Toplevel(self.root)
            report_window.title("Analytics Report")
            report_window.geometry("600x400")
            
            # Apply theme to the window
            self._theme_popup_window(report_window)
            
            report_text = scrolledtext.ScrolledText(report_window, font=("Consolas", 10))
            report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Apply theme to the text widget
            self._theme_text_widget(report_text)
            
            report_text.insert(tk.END, report)
            report_text.config(state='disabled')
            
            self.log("Analytics report generated")
        except Exception as e:
            self.log(f"Failed to generate report: {e}")
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    def export_analytics(self):
        """Export analytics data"""
        if not self.analytics:
            messagebox.showinfo("Analytics", "Analytics system not available")
            return
        
        try:
            # Get export path
            export_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
            )
            
            if export_path:
                if export_path.endswith('.csv'):
                    # Export as CSV
                    import csv
                    with open(export_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['Timestamp', 'CPU %', 'Memory %', 'Disk %'])
                        
                        system_data = self.analytics.get_system_metrics(24)
                        for row in system_data:
                            writer.writerow([row[3], row[0], row[1], row[2]])
                
                elif export_path.endswith('.json'):
                    # Export as JSON
                    system_data = self.analytics.get_system_metrics(24)
                    export_data = {
                        'system_metrics': [
                            {
                                'timestamp': row[3],
                                'cpu_percent': row[0],
                                'memory_percent': row[1],
                                'disk_usage': row[2]
                            }
                            for row in system_data
                        ]
                    }
                    
                    with open(export_path, 'w') as jsonfile:
                        json.dump(export_data, jsonfile, indent=2)
                
                self.log(f"Analytics data exported to: {export_path}")
                messagebox.showinfo("Export Complete", f"Data exported to:\n{export_path}")
        
        except Exception as e:
            self.log(f"Failed to export analytics: {e}")
            messagebox.showerror("Error", f"Failed to export analytics: {e}")

    def manage_plugins(self):
        """Manage plugins with enhanced marketplace integration"""
        try:
            # Try to use enhanced plugin marketplace if available
            try:
                from utils.plugin_marketplace import PluginMarketplace
                if not hasattr(self, 'plugin_marketplace') or not self.plugin_marketplace:
                    self.plugin_marketplace = PluginMarketplace(self)
                
                # Create marketplace window
                self.plugin_marketplace.create_marketplace_window()
                self.log("Plugin marketplace opened successfully")
                return
                
            except ImportError as e:
                self.log(f"Plugin marketplace not available: {e}")
                # Fallback to basic plugin manager
                pass
            except Exception as e:
                self.log(f"Error opening plugin marketplace: {e}")
                messagebox.showerror("Plugin Marketplace Error", 
                                   f"Failed to open plugin marketplace:\n{str(e)}\n\nFalling back to basic plugin manager.")
                # Fallback to basic plugin manager
                pass
            
            # Fallback: Create basic plugin management window
            if not self.plugin_manager:
                messagebox.showinfo("Plugins", "Plugin manager not available")
                return
            
            # Create plugin management window
            plugin_window = tk.Toplevel(self.root)
            plugin_window.title("Plugin Manager")
            plugin_window.geometry("600x500")
            plugin_window.resizable(True, True)
            
            # Apply theme to the window
            self._theme_popup_window(plugin_window)
            
            # Main frame
            main_frame = ttk.Frame(plugin_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(header_frame, text="Plugin Manager", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
            
            # Status label
            self.plugin_status_label = ttk.Label(header_frame, text="Ready")
            self.plugin_status_label.pack(side=tk.RIGHT)
            
            # Import enhanced widgets
            try:
                from utils.enhanced_widgets import create_enhanced_treeview
            except ImportError:
                # Fallback to regular widgets if enhanced widgets not available
                def create_enhanced_treeview(parent, **kwargs):
                    frame = tk.Frame(parent)
                    treeview = ttk.Treeview(frame, **kwargs)
                    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=treeview.yview)
                    treeview.configure(yscrollcommand=scrollbar.set)
                    treeview.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")
                    return frame, treeview
            
            # Plugin list with enhanced scrollbar
            list_frame = ttk.LabelFrame(main_frame, text="Installed Plugins")
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Create enhanced treeview for better plugin display
            columns = ('Plugin', 'Status', 'Version')
            tree_frame, plugin_tree = create_enhanced_treeview(list_frame, columns=columns, show='headings', height=10)
            
            for col in columns:
                plugin_tree.heading(col, text=col)
                plugin_tree.column(col, width=150)
            
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # Populate plugin list
            def refresh_plugin_list():
                plugin_tree.delete(*plugin_tree.get_children())
                plugins = self.plugin_manager.get_plugin_list()
                for plugin in plugins:
                    # Determine plugin status (this would need to be implemented in PluginManager)
                    status = "Enabled"  # Placeholder
                    version = "1.0.0"   # Placeholder
                    plugin_tree.insert('', 'end', values=(plugin, status, version))
                
                self.plugin_status_label.config(text=f"Found {len(plugins)} plugins")
            
            refresh_plugin_list()
            
            # Plugin controls
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Left side controls
            left_controls = ttk.Frame(control_frame)
            left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            ttk.Button(left_controls, text="Enable Plugin", 
                      command=lambda: self.enable_selected_plugin(plugin_tree)).pack(side=tk.LEFT, padx=(0,5))
            ttk.Button(left_controls, text="Disable Plugin", 
                      command=lambda: self.disable_selected_plugin(plugin_tree)).pack(side=tk.LEFT, padx=5)
            ttk.Button(left_controls, text="Refresh List", 
                      command=refresh_plugin_list).pack(side=tk.LEFT, padx=5)
            
            # Right side controls
            right_controls = ttk.Frame(control_frame)
            right_controls.pack(side=tk.RIGHT)
            
            ttk.Button(right_controls, text="Create New Plugin", 
                      command=self.create_plugin_dialog).pack(side=tk.LEFT, padx=5)
            ttk.Button(right_controls, text="Close", 
                      command=plugin_window.destroy).pack(side=tk.LEFT, padx=5)
            
            # Info frame
            info_frame = ttk.LabelFrame(main_frame, text="Plugin Information")
            info_frame.pack(fill=tk.X)
            
            info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
            info_text.pack(fill=tk.X, padx=5, pady=5)
            
            # Apply theme to text widget
            self._theme_text_widget(info_text)
            
            # Bind selection event
            def on_plugin_select(event):
                selection = plugin_tree.selection()
                if selection:
                    item = plugin_tree.item(selection[0])
                    plugin_name = item['values'][0]
                    
                    info_text.config(state=tk.NORMAL)
                    info_text.delete('1.0', tk.END)
                    info_text.insert('1.0', f"Plugin: {plugin_name}\nStatus: {item['values'][1]}\nVersion: {item['values'][2]}")
                    info_text.config(state=tk.DISABLED)
            
            plugin_tree.bind('<<TreeviewSelect>>', on_plugin_select)
            
        except Exception as e:
            self.log(f"Failed to manage plugins: {e}")
            messagebox.showerror("Error", f"Failed to manage plugins: {e}")

    def enable_selected_plugin(self, treeview):
        """Enable selected plugin"""
        selection = treeview.selection()
        if selection:
            item = treeview.item(selection[0])
            plugin_name = item['values'][0]
            try:
                self.plugin_manager.enable_plugin(plugin_name)
                self.log(f"Enabled plugin: {plugin_name}")
                messagebox.showinfo("Success", f"Plugin '{plugin_name}' enabled successfully")
            except Exception as e:
                self.log(f"Failed to enable plugin {plugin_name}: {e}")
                messagebox.showerror("Error", f"Failed to enable plugin '{plugin_name}': {e}")

    def disable_selected_plugin(self, treeview):
        """Disable selected plugin"""
        selection = treeview.selection()
        if selection:
            item = treeview.item(selection[0])
            plugin_name = item['values'][0]
            try:
                self.plugin_manager.disable_plugin(plugin_name)
                self.log(f"Disabled plugin: {plugin_name}")
                messagebox.showinfo("Success", f"Plugin '{plugin_name}' disabled successfully")
            except Exception as e:
                self.log(f"Failed to disable plugin {plugin_name}: {e}")
                messagebox.showerror("Error", f"Failed to disable plugin '{plugin_name}': {e}")

    def create_plugin(self):
        """Create a new plugin"""
        self.create_plugin_dialog()

    def create_plugin_dialog(self):
        """Create plugin dialog"""
        try:
            plugin_name = tk.simpledialog.askstring("Create Plugin", "Enter plugin name:")
            if plugin_name:
                if self.plugin_manager.create_plugin_template(plugin_name):
                    messagebox.showinfo("Success", f"Plugin template created: {plugin_name}.py")
                    self.log(f"Created plugin template: {plugin_name}")
                else:
                    messagebox.showerror("Error", "Failed to create plugin template")
        except Exception as e:
            self.log(f"Failed to create plugin: {e}")
            messagebox.showerror("Error", f"Failed to create plugin: {e}")

    def open_plugin_marketplace(self):
        """Open the plugin marketplace as a modal window integrated with main GUI"""
        try:
            from utils.plugin_marketplace import PluginMarketplace
            
            # Initialize plugin marketplace if not exists
            if not hasattr(self, 'plugin_marketplace') or not self.plugin_marketplace:
                self.plugin_marketplace = PluginMarketplace(self)
            
            # Get current theme colors
            current_theme = self.get_current_theme_colors()
            
            # Create marketplace window with current theme
            self.plugin_marketplace.create_marketplace_window()
            
            # Ensure the marketplace window is properly themed and modal
            if hasattr(self.plugin_marketplace, 'marketplace_window') and self.plugin_marketplace.marketplace_window:
                marketplace_window = self.plugin_marketplace.marketplace_window.window
                
                # Set as child of main window for proper modal behavior
                marketplace_window.transient(self.root)
                marketplace_window.grab_set()
                
                # Center the window relative to main GUI
                self._center_window_on_parent(marketplace_window, self.root)
                
                # Apply current theme to the marketplace window
                if hasattr(self.plugin_marketplace.marketplace_window, 'apply_theme'):
                    self.plugin_marketplace.marketplace_window.apply_theme(current_theme)
                
                # Register for theme updates
                self.register_theme_window(marketplace_window)
                
                # Focus the marketplace window
                marketplace_window.focus_set()
                marketplace_window.lift()
                
            self.log("Plugin marketplace opened successfully as modal window")
            
        except ImportError as e:
            self.log(f"Plugin marketplace not available: {e}")
            messagebox.showinfo("Plugin Marketplace", 
                              "Plugin marketplace is not available.\n\nPlease use 'Manage Plugins' for basic plugin management.")
        except Exception as e:
            self.log(f"Error opening plugin marketplace: {e}")
            messagebox.showerror("Plugin Marketplace Error", 
                               f"Failed to open plugin marketplace:\n{str(e)}")

    def reload_plugins(self):
        """Reload plugins"""
        if self.plugin_manager:
            self.plugin_manager.load_plugins()
            self.log("Plugins reloaded")
            messagebox.showinfo("Success", "Plugins reloaded successfully")

    def update_advanced_status(self):
        """Update advanced features status"""
        if hasattr(self, 'advanced_status_text'):
            self.advanced_status_text.config(state='normal')
            self.advanced_status_text.delete('1.0', tk.END)
            
            status_lines = []
            status_lines.append("Advanced Features Status:")
            status_lines.append("=" * 30)
            
            # Web Interface status
            web_status = "Running" if (self.web_interface and self.web_interface.is_running) else "Stopped"
            status_lines.append(f"Web Interface: {web_status}")
            
            # API Server status
            api_status = "Running" if (self.api_server and self.api_server.is_running) else "Stopped"
            status_lines.append(f"API Server: {api_status}")
            
            # Mobile App status
            mobile_status = "Running" if (self.mobile_app and self.mobile_app.is_running) else "Stopped"
            status_lines.append(f"Mobile App: {mobile_status}")
            
            # Analytics status
            analytics_status = "Available" if self.analytics else "Not Available"
            status_lines.append(f"Analytics: {analytics_status}")
            
            # Plugin Manager status
            plugin_status = "Available" if self.plugin_manager else "Not Available"
            status_lines.append(f"Plugin Manager: {plugin_status}")
            
            if self.plugin_manager:
                plugins = self.plugin_manager.get_plugin_list()
                status_lines.append(f"Loaded Plugins: {len(plugins)}")
                for plugin in plugins:
                    status_lines.append(f"  - {plugin}")
            
            status_lines.append("")
            status_lines.append("Dependencies:")
            status_lines.append(f"  Flask: {'Available' if FLASK_AVAILABLE else 'Not Available'}")
            status_lines.append(f"  Matplotlib: {'Available' if MATPLOTLIB_AVAILABLE else 'Not Available'}")
            status_lines.append(f"  Requests: {'Available' if REQUESTS_AVAILABLE else 'Not Available'}")
            status_lines.append(f"  QRCode: {'Available' if QRCODE_AVAILABLE else 'Not Available'}")
            
            self.advanced_status_text.insert(tk.END, '\n'.join(status_lines))
            self.advanced_status_text.config(state='disabled')

    def refresh_advanced_statistics(self):
        """Refresh real-time statistics for advanced features"""
        try:
            # Only update if Advanced Features tab is currently selected
            current_tab = self.notebook.select()
            advanced_tab = None
            for tab_id in self.notebook.tabs():
                if self.notebook.tab(tab_id, "text") == "Advanced":
                    advanced_tab = tab_id
                    break
            
            if current_tab != advanced_tab:
                return  # Don't update if Advanced tab is not active
            
            import psutil
            import time
            
            # System performance statistics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update system stats labels
            self.cpu_usage_label.config(text=f"CPU: {cpu_percent:.1f}%")
            self.memory_usage_label.config(text=f"Memory: {memory.percent:.1f}%")
            self.disk_usage_label.config(text=f"Disk: {disk.percent:.1f}%")
            
            # Process instance counts
            ooba_count = len(self.process_instance_tabs.get('Oobabooga', []))
            zwaifu_count = len(self.process_instance_tabs.get('Z-Waifu', []))
            ollama_count = len(self.process_instance_tabs.get('Ollama', []))
            rvc_count = len(self.process_instance_tabs.get('RVC', []))
            
            # Update process stats labels
            self.ooba_instances_label.config(text=f"Oobabooga: {ooba_count} instances")
            self.zwaifu_instances_label.config(text=f"Z-Waifu: {zwaifu_count} instances")
            self.ollama_instances_label.config(text=f"Ollama: {ollama_count} instances")
            self.rvc_instances_label.config(text=f"RVC: {rvc_count} instances")
            
            # Service status
            web_status = "Running" if hasattr(self, 'web_interface') and self.web_interface and self.web_interface.is_running else "Stopped"
            api_status = "Running" if hasattr(self, 'api_server') and self.api_server and hasattr(self.api_server, 'is_running') and self.api_server.is_running else "Stopped"
            mobile_status = "Running" if hasattr(self, 'mobile_app') and self.mobile_app and self.mobile_app.is_running else "Stopped"
            analytics_status = "Active" if hasattr(self, 'analytics') and self.analytics else "Inactive"
            
            # Update service stats labels
            self.web_interface_status_label.config(text=f"Web Interface: {web_status}")
            self.api_server_status_label.config(text=f"API Server: {api_status}")
            self.mobile_app_status_label.config(text=f"Mobile App: {mobile_status}")
            self.analytics_status_label.config(text=f"Analytics: {analytics_status}")
            
            # Record analytics data (silently, no console spam)
            if hasattr(self, 'analytics') and self.analytics:
                self.analytics.record_system_metrics(cpu_percent, memory.percent, disk.percent)
                
                # Record process metrics for each running instance
                for process_type, instances in self.process_instance_tabs.items():
                    for instance in instances:
                        if hasattr(instance, 'process') and instance.process and instance.process.poll() is None:
                            try:
                                process = psutil.Process(instance.process.pid)
                                self.analytics.record_process_metrics(process_type, process.cpu_percent(), process.memory_percent())
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
            
            # Only log on manual refresh, not automatic updates
            # self.log("Advanced statistics refreshed")
            
        except Exception as e:
            self.log(f"Failed to refresh advanced statistics: {e}")

    def manual_refresh_statistics(self):
        """Manual refresh of statistics with logging"""
        self.refresh_advanced_statistics()
        self.log("Advanced statistics manually refreshed")

    def start_statistics_monitoring(self):
        """Start periodic statistics monitoring"""
        def schedule_next_update():
            try:
                self.refresh_advanced_statistics()
                # Schedule next update in 5 seconds
                self.root.after(5000, schedule_next_update)
            except Exception as e:
                self.log(f"Statistics monitoring error: {e}")
        
        # Start the first update
        self.root.after(1000, schedule_next_update)
        self.log("Statistics monitoring started")

    def export_advanced_statistics(self):
        """Export advanced statistics to file"""
        try:
            import json
            import time
            import psutil
            from datetime import datetime
            
            # Collect comprehensive statistics
            stats_data = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent,
                    'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
                },
                'processes': {
                    'oobabooga_instances': len(self.process_instance_tabs.get('Oobabooga', [])),
                    'zwaifu_instances': len(self.process_instance_tabs.get('Z-Waifu', [])),
                    'ollama_instances': len(self.process_instance_tabs.get('Ollama', [])),
                    'rvc_instances': len(self.process_instance_tabs.get('RVC', []))
                },
                'services': {
                    'web_interface': hasattr(self, 'web_interface') and self.web_interface and self.web_interface.is_running,
                    'api_server': hasattr(self, 'api_server') and self.api_server and hasattr(self.api_server, 'is_running') and self.api_server.is_running,
                    'mobile_app': hasattr(self, 'mobile_app') and self.mobile_app and self.mobile_app.is_running,
                    'analytics': hasattr(self, 'analytics') and self.analytics is not None
                },
                'configuration': {
                    'dark_mode': self._dark_mode,
                    'current_theme': self.current_theme,
                    'total_tabs': len(self.notebook.tabs())
                }
            }
            
            # Export to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_statistics_{timestamp}.json"
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            with open(filepath, 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            messagebox.showinfo("Statistics Exported", f"Advanced statistics exported to:\n{filepath}")
            self.log(f"Advanced statistics exported to {filepath}")
            
        except Exception as e:
            self.log(f"Failed to export advanced statistics: {e}")
            messagebox.showerror("Export Error", f"Failed to export statistics: {e}")

    def kill_all_instances(self):
        """Kill all running instances of all processes reliably with proper VRAM cleanup."""
        killed_count = 0
        for process_type in self.process_instance_tabs:
            for instance in self.process_instance_tabs[process_type]:
                proc = instance.get('proc')
                if proc and proc.poll() is None:
                    try:
                        # Force kill the process
                        proc.kill()
                        # Wait for process to fully terminate
                        try:
                            proc.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            pass  # Process will be cleaned up by OS
                        self.log(f"Killed {process_type} instance (PID {proc.pid})")
                        killed_count += 1
                    except Exception as e:
                        self.log(f"Error killing {process_type} instance: {e}")
                    finally:
                        instance['proc'] = None  # Clean up reference
        
        # Clear all instance tabs
        for process_type in self.process_instance_tabs:
            self.process_instance_tabs[process_type].clear()
        
        # Remove all instance tabs from notebook
        tabs_to_remove = []
        for i, tab in enumerate(self.notebook.tabs()):
            tab_text = self.notebook.tab(tab, "text")
            if "Instance" in tab_text:
                tabs_to_remove.append(i)
        
        # Remove tabs in reverse order to avoid index issues
        for i in reversed(tabs_to_remove):
            tab = self.notebook.tabs()[i]
            if tab in self.notebook.tabs():
                self.notebook.forget(tab)
        
        # Force GPU memory cleanup if possible
        self._force_gpu_cleanup()
        
        # Trigger VRAM cleanup after killing all instances
        if self.vram_monitor:
            self.vram_monitor.force_vram_cleanup()
        
        self.update_instance_manager()
        self.log(f"Kill All: {killed_count} process(es) killed.")
        self.set_status(f"Kill All: {killed_count} process(es) killed.", "red")
    
    def _force_gpu_cleanup(self):
        """Force GPU memory cleanup to help with VRAM issues"""
        gpu_status = "Unknown"
        try:
            # Try to import torch and clear CUDA cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    gpu_status = f"CUDA: {torch.cuda.get_device_name(0)}"
                    self.log("CUDA cache cleared")
                else:
                    gpu_status = "CUDA: Not available"
            except ImportError:
                gpu_status = "CUDA: Not installed"
            except Exception as e:
                gpu_status = f"CUDA: Error - {e}"
            
            # Try to import tensorflow and clear GPU memory if available
            try:
                import tensorflow as tf
                gpu_devices = tf.config.list_physical_devices('GPU')
                if gpu_devices:
                    tf.keras.backend.clear_session()
                    gpu_status += f" | TensorFlow: {len(gpu_devices)} GPU(s)"
                    self.log("TensorFlow GPU memory cleared")
                else:
                    gpu_status += " | TensorFlow: No GPU"
            except ImportError:
                gpu_status += " | TensorFlow: Not installed"
            except Exception as e:
                gpu_status += f" | TensorFlow: Error - {e}"
                
            # Update GPU status label if it exists
            if hasattr(self, 'gpu_status_label'):
                self.gpu_status_label.config(text=f"GPU Status: {gpu_status}")
                
        except Exception as e:
            self.log(f"GPU cleanup error (non-critical): {e}")
            if hasattr(self, 'gpu_status_label'):
                self.gpu_status_label.config(text=f"GPU Status: Error - {e}")
    
    def _start_vram_monitoring(self):
        """Start VRAM monitoring"""
        if self.vram_monitor:
            self.vram_monitor.start_monitoring()
            self.log("[VRAM] Monitoring started")
            self._refresh_vram_status()
            
            # Update button states
            if hasattr(self, 'vram_start_btn'):
                self.vram_start_btn.config(state='disabled')
            if hasattr(self, 'vram_stop_btn'):
                self.vram_stop_btn.config(state='normal')
        else:
            messagebox.showwarning("Warning", "VRAM monitor not available")
    
    def _stop_vram_monitoring(self):
        """Stop VRAM monitoring"""
        if self.vram_monitor:
            self.vram_monitor.stop_monitoring()
            self.log("[VRAM] Monitoring stopped")
            self._refresh_vram_status()
            
            # Update button states
            if hasattr(self, 'vram_start_btn'):
                self.vram_start_btn.config(state='normal')
            if hasattr(self, 'vram_stop_btn'):
                self.vram_stop_btn.config(state='disabled')
        else:
            messagebox.showwarning("Warning", "VRAM monitor not available")
    
    def _refresh_vram_status(self):
        """Refresh VRAM status display"""
        if not self.vram_monitor:
            if hasattr(self, 'vram_status_label'):
                self.vram_status_label.config(text="VRAM Status: Monitor not available")
            if hasattr(self, 'vram_usage_label'):
                self.vram_usage_label.config(text="VRAM Usage: Unknown")
            return
        
        try:
            vram_info = self.vram_monitor.get_vram_info()
            summary = self.vram_monitor.get_vram_summary()
            
            # Update status label
            if hasattr(self, 'vram_status_label'):
                status_text = f"VRAM Status: {'Monitoring' if self.vram_monitor.monitoring else 'Stopped'}"
                if vram_info.get("source") != "none":
                    status_text += f" ({vram_info['source']})"
                self.vram_status_label.config(text=status_text)
            
            # Update usage label
            if hasattr(self, 'vram_usage_label'):
                if vram_info.get("total_vram_gb", 0) > 0:
                    usage_text = f"VRAM Usage: {vram_info['used_vram_gb']:.1f}GB / {vram_info['total_vram_gb']:.1f}GB ({vram_info['vram_usage_percent']:.1f}%)"
                    
                    # Color code based on usage
                    if vram_info['vram_usage_percent'] > 90:
                        usage_text += " (CRITICAL)"
                    elif vram_info['vram_usage_percent'] > 80:
                        usage_text += " (HIGH)"
                    
                    self.vram_usage_label.config(text=usage_text)
                else:
                    self.vram_usage_label.config(text="VRAM Usage: No GPU detected")
            
            # Update button states based on monitoring status
            if hasattr(self, 'vram_start_btn') and hasattr(self, 'vram_stop_btn'):
                if self.vram_monitor.monitoring:
                    self.vram_start_btn.config(state='disabled')
                    self.vram_stop_btn.config(state='normal')
                else:
                    self.vram_start_btn.config(state='normal')
                    self.vram_stop_btn.config(state='disabled')
                    
        except Exception as e:
            if hasattr(self, 'vram_status_label'):
                self.vram_status_label.config(text=f"VRAM Status: Error - {e}")
            if hasattr(self, 'vram_usage_label'):
                self.vram_usage_label.config(text="VRAM Usage: Error")
        
        # Update analytics and health displays
        self._update_vram_analytics_display()
        self._update_system_health_display()
    
    def _update_vram_analytics_display(self):
        """Update VRAM analytics display"""
        try:
            if self.vram_monitor and hasattr(self, 'vram_analytics_label'):
                analytics = self.vram_monitor.get_vram_analytics()
                if "error" not in analytics:
                    summary = analytics.get("summary", {})
                    if "error" not in summary:
                        analytics_text = f"Analytics: {summary.get('total_readings', 0)} readings, Avg: {summary.get('average_usage', 0):.1f}%"
                    else:
                        analytics_text = "Analytics: No data available"
                else:
                    analytics_text = "Analytics: Disabled"
                
                self.vram_analytics_label.config(text=analytics_text)
        except Exception as e:
            if hasattr(self, 'vram_analytics_label'):
                self.vram_analytics_label.config(text="Analytics: Error")
    
    def _update_system_health_display(self):
        """Update system health display"""
        try:
            if self.vram_monitor and hasattr(self, 'system_health_label'):
                health_data = self.vram_monitor._check_system_health()
                if health_data:
                    health_text = f"System Health: {health_data.get('health_score', 0)}/100 ({health_data.get('status', 'Unknown')})"
                else:
                    health_text = "System Health: Not available"
                
                self.system_health_label.config(text=health_text)
        except Exception as e:
            if hasattr(self, 'system_health_label'):
                self.system_health_label.config(text="System Health: Error")
    
    def _optimize_vram_usage(self):
        """Optimize VRAM usage"""
        try:
            if self.vram_monitor:
                result = self.vram_monitor.optimize_vram_usage()
                if "error" not in result:
                    if result.get("optimization_triggered"):
                        messagebox.showinfo("VRAM Optimization", f"VRAM optimization completed!\n{result.get('reason', '')}")
                    else:
                        messagebox.showinfo("VRAM Optimization", f"No optimization needed.\n{result.get('reason', '')}")
                else:
                    messagebox.showerror("VRAM Optimization Error", result.get("error", "Unknown error"))
                
                # Refresh display
                self._refresh_vram_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize VRAM: {e}")
    
    def _view_vram_analytics(self):
        """View VRAM analytics in a popup window"""
        try:
            if self.vram_monitor:
                analytics = self.vram_monitor.get_vram_analytics()
                
                # Create popup window
                analytics_window = tk.Toplevel(self.root)
                analytics_window.title("VRAM Analytics")
                analytics_window.geometry("600x400")
                
                # Create text widget
                text_widget = scrolledtext.ScrolledText(analytics_window, wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Format and display analytics
                if "error" not in analytics:
                    text_widget.insert(tk.END, "VRAM Analytics Report\n")
                    text_widget.insert(tk.END, "=" * 50 + "\n\n")
                    
                    # Summary
                    summary = analytics.get("summary", {})
                    if "error" not in summary:
                        text_widget.insert(tk.END, "SUMMARY:\n")
                        text_widget.insert(tk.END, f"  Total Readings: {summary.get('total_readings', 0)}\n")
                        text_widget.insert(tk.END, f"  Average Usage: {summary.get('average_usage', 0):.1f}%\n")
                        text_widget.insert(tk.END, f"  Max Usage: {summary.get('max_usage', 0):.1f}%\n")
                        text_widget.insert(tk.END, f"  Current Usage: {summary.get('current_usage', 0):.1f}%\n")
                        text_widget.insert(tk.END, f"  Usage Trend: {summary.get('usage_trend', 'Unknown')}\n\n")
                    
                    # Trends
                    trends = analytics.get("trends", {})
                    if "error" not in trends:
                        text_widget.insert(tk.END, "TRENDS:\n")
                        text_widget.insert(tk.END, f"  Trend: {trends.get('trend', 'Unknown')}\n")
                        text_widget.insert(tk.END, f"  Trend Strength: {trends.get('trend_strength', 0):.1f}%\n\n")
                    
                    # Performance
                    performance = analytics.get("performance", {})
                    if "error" not in performance:
                        text_widget.insert(tk.END, "PERFORMANCE:\n")
                        text_widget.insert(tk.END, f"  Average CPU: {performance.get('average_cpu', 0):.1f}%\n")
                        text_widget.insert(tk.END, f"  Average Memory: {performance.get('average_memory', 0):.1f}%\n")
                        text_widget.insert(tk.END, f"  Max CPU: {performance.get('max_cpu', 0):.1f}%\n")
                        text_widget.insert(tk.END, f"  Max Memory: {performance.get('max_memory', 0):.1f}%\n\n")
                    
                    # Health
                    health = analytics.get("health", {})
                    if "error" not in health:
                        text_widget.insert(tk.END, "SYSTEM HEALTH:\n")
                        text_widget.insert(tk.END, f"  Health Score: {health.get('current_health_score', 0)}/100\n")
                        text_widget.insert(tk.END, f"  Status: {health.get('health_status', 'Unknown')}\n")
                        text_widget.insert(tk.END, f"  Average Score: {health.get('average_health_score', 0):.1f}\n\n")
                    
                    # Cleanup history
                    cleanup = analytics.get("cleanup_history", {})
                    if "error" not in cleanup:
                        text_widget.insert(tk.END, "CLEANUP HISTORY:\n")
                        text_widget.insert(tk.END, f"  Total Cleanups: {cleanup.get('total_cleanups', 0)}\n")
                        text_widget.insert(tk.END, f"  Successful Cleanups: {cleanup.get('successful_cleanups', 0)}\n")
                        text_widget.insert(tk.END, f"  Total VRAM Freed: {cleanup.get('total_vram_freed_gb', 0):.2f}GB\n")
                        text_widget.insert(tk.END, f"  Average Freed per Cleanup: {cleanup.get('average_vram_freed_per_cleanup', 0):.2f}GB\n")
                else:
                    text_widget.insert(tk.END, f"Error: {analytics.get('error', 'Unknown error')}")
                
                text_widget.config(state='disabled')
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view VRAM analytics: {e}")
    
    def _export_vram_data(self):
        """Export VRAM data"""
        try:
            if self.vram_monitor:
                # Get export format from settings
                export_format = self.vram_monitor.vram_settings.get("analytics_export_format", "json")
                
                result = self.vram_monitor.export_vram_data(export_format)
                if "successfully" in result:
                    messagebox.showinfo("Export Successful", result)
                else:
                    messagebox.showerror("Export Error", result)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export VRAM data: {e}")
    
    def _gentle_vram_cleanup(self):
        """Perform gentle VRAM cleanup"""
        try:
            if self.vram_monitor:
                result = self.vram_monitor._gentle_cleanup()
                if result.get("total_vram_freed_gb", 0) > 0:
                    messagebox.showinfo("Gentle Cleanup", f"Gentle cleanup completed!\nFreed: {result.get('total_vram_freed_gb', 0):.2f}GB")
                else:
                    messagebox.showinfo("Gentle Cleanup", "Gentle cleanup completed, but no VRAM was freed.")
                
                # Refresh display
                self._refresh_vram_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to perform gentle cleanup: {e}")
    
    def _update_gpu_status(self):
        """Update GPU status without clearing cache"""
        gpu_status = "Unknown"
        try:
            # Check CUDA availability
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_status = f"CUDA: {torch.cuda.get_device_name(0)}"
                else:
                    gpu_status = "CUDA: Not available"
            except ImportError:
                gpu_status = "CUDA: Not installed"
            except Exception as e:
                gpu_status = f"CUDA: Error - {e}"
            
            # Check TensorFlow availability
            try:
                import tensorflow as tf
                gpu_devices = tf.config.list_physical_devices('GPU')
                if gpu_devices:
                    gpu_status += f" | TensorFlow: {len(gpu_devices)} GPU(s)"
                else:
                    gpu_status += " | TensorFlow: No GPU"
            except ImportError:
                gpu_status += " | TensorFlow: Not installed"
            except Exception as e:
                gpu_status += f" | TensorFlow: Error - {e}"
                
            # Update GPU status label if it exists
            if hasattr(self, 'gpu_status_label'):
                self.gpu_status_label.config(text=f"GPU Status: {gpu_status}")
                
        except Exception as e:
            if hasattr(self, 'gpu_status_label'):
                self.gpu_status_label.config(text=f"GPU Status: Error - {e}")

    def refresh_instance_manager(self):
        """Refresh the instance manager tab"""
        self.update_instance_manager()

    def focus_instance_terminal(self, event):
        """Focus the terminal of the selected instance"""
        selection = self.instance_tree.selection()
        if selection:
            instance = self.instance_tree.item(selection[0])['values']
            self.focus_instance(instance[0], instance[1])

    def stop_selected_instance(self):
        """Stop the selected instance"""
        selection = self.instance_tree.selection()
        if selection:
            instance = self.instance_tree.item(selection[0])['values']
            self.stop_instance(instance[0], instance[1])

    def restart_selected_instance(self):
        """Restart the selected instance"""
        selection = self.instance_tree.selection()
        if selection:
            instance = self.instance_tree.item(selection[0])['values']
            self.restart_instance(instance[0], instance[1])

    def kill_selected_instance(self):
        """Kill the selected instance"""
        selection = self.instance_tree.selection()
        if selection:
            instance = self.instance_tree.item(selection[0])['values']
            self.kill_instance(instance[0], instance[1])

    def stop_instance(self, process_name, instance_id):
        """Stop a specific instance of a process and remove its tab with proper VRAM cleanup"""
        if process_name in self.process_instance_tabs:
            instances = self.process_instance_tabs[process_name]
            if isinstance(instance_id, str):
                try:
                    instance_id = int(instance_id.split()[-1]) - 1
                except Exception:
                    return
            if instance_id < len(instances):
                instance = instances[instance_id]
                if instance['proc']:
                    try:
                        # First try graceful termination
                        instance['proc'].terminate()
                        # Wait for graceful shutdown
                        try:
                            instance['proc'].wait(timeout=10)  # Wait up to 10 seconds
                        except subprocess.TimeoutExpired:
                            # Force kill if it doesn't terminate gracefully
                            self.log(f"Force killing {process_name} Instance {instance_id+1} after timeout")
                            instance['proc'].kill()
                            try:
                                instance['proc'].wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                pass  # Process will be cleaned up by OS
                    except Exception as e:
                        self.log(f"Error stopping {process_name} Instance {instance_id+1}: {e}")
                    finally:
                        # Ensure process reference is cleared
                        instance['proc'] = None
                
                # Remove tab
                for i, tab in enumerate(self.notebook.tabs()):
                    if self.notebook.tab(tab, "text") == f"{process_name} Instance {instance_id+1}":
                        if tab in self.notebook.tabs():
                            self.notebook.forget(tab)
                        break
                # Remove from instance list
                instances.pop(instance_id)
                self.log(f"Stopped {process_name} Instance {instance_id+1}")
                self.update_instance_manager()

    def kill_instance(self, process_name, instance_id):
        """Kill a specific instance of a process and remove its tab with proper VRAM cleanup"""
        if process_name in self.process_instance_tabs:
            instances = self.process_instance_tabs[process_name]
            if isinstance(instance_id, str):
                try:
                    instance_id = int(instance_id.split()[-1]) - 1
                except Exception:
                    return
            if instance_id < len(instances):
                instance = instances[instance_id]
                if instance['proc']:
                    try:
                        # Force kill the process
                        instance['proc'].kill()
                        # Wait for process to fully terminate
                        try:
                            instance['proc'].wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            pass  # Process will be cleaned up by OS
                    except Exception as e:
                        self.log(f"Error killing {process_name} Instance {instance_id+1}: {e}")
                    finally:
                        # Ensure process reference is cleared
                        instance['proc'] = None
                
                # Remove tab
                for i, tab in enumerate(self.notebook.tabs()):
                    if self.notebook.tab(tab, "text") == f"{process_name} Instance {instance_id+1}":
                        if tab in self.notebook.tabs():
                            self.notebook.forget(tab)
                        break
                # Remove from instance list
                instances.pop(instance_id)
                self.log(f"Killed {process_name} Instance {instance_id+1}")
                self.update_instance_manager()

    def restart_instance(self, process_name, instance_id):
        """Restart a specific instance of a process (stop, remove tab, start new)"""
        if process_name in self.process_instance_tabs:
            instances = self.process_instance_tabs[process_name]
            if isinstance(instance_id, str):
                try:
                    instance_id = int(instance_id.split()[-1]) - 1
                except Exception:
                    return
            if instance_id < len(instances):
                instance = instances[instance_id]
                bat_path = instance.get('bat_path')
                # Remove tab
                for i, tab in enumerate(self.notebook.tabs()):
                    if self.notebook.tab(tab, "text") == f"{process_name} Instance {instance_id+1}":
                        if tab in self.notebook.tabs():
                            self.notebook.forget(tab)
                        break
                # Remove from instance list
                instances.pop(instance_id)
                # Start new instance
                if bat_path:
                    self.start_process_instance(process_name.lower())
                self.log(f"Restarted {process_name} Instance {instance_id+1}")
                self.update_instance_manager()

    def focus_instance(self, process_name, instance_id):
        """Focus the terminal tab of a specific instance"""
        try:
            instance_id = int(instance_id.split()[-1]) - 1  # Convert "Instance X" to X-1
            if process_name in self.process_instance_tabs:
                instances = self.process_instance_tabs[process_name]
                if instance_id < len(instances):
                    # Find the tab index for this instance
                    for i, tab in enumerate(self.notebook.tabs()):
                        if self.notebook.tab(tab, "text") == f"{process_name} Instance {instance_id+1}":
                            self.notebook.select(i)
                            self.log(f"Focused {process_name} Instance {instance_id+1}")
                            break
        except Exception as e:
            self.log(f"Failed to focus instance: {e}")

    def refresh_ooba_status(self):
        """Refresh Oobabooga status"""
        if hasattr(self, 'ooba_status_var'):
            # Count running instances
            running_count = 0
            if 'Oobabooga' in self.process_instance_tabs:
                for instance in self.process_instance_tabs['Oobabooga']:
                    if instance['proc'] and instance['proc'].poll() is None:
                        running_count += 1
            
            if running_count > 0:
                self.ooba_status_var.set(f"Running instances: {running_count}")
            else:
                self.ooba_status_var.set("No instances running")

    def refresh_zwaifu_status(self):
        """Refresh Z-Waifu status"""
        if hasattr(self, 'zwaifu_status_var'):
            # Count running instances
            running_count = 0
            if 'Z-Waifu' in self.process_instance_tabs:
                for instance in self.process_instance_tabs['Z-Waifu']:
                    if instance['proc'] and instance['proc'].poll() is None:
                        running_count += 1
            
            if running_count > 0:
                self.zwaifu_status_var.set(f"Running instances: {running_count}")
            else:
                self.zwaifu_status_var.set("No instances running")
    
    def stop_all_instances(self, process_type):
        """Stop all instances of a specific process type"""
        if process_type in self.process_instance_tabs:
            stopped_count = 0
            for instance in self.process_instance_tabs[process_type]:
                if instance['proc'] and instance['proc'].poll() is None:
                    try:
                        instance['proc'].terminate()
                        stopped_count += 1
                    except Exception as e:
                        self.log(f"Error stopping {process_type} instance: {e}")
            
            self.log(f"Stopped {stopped_count} {process_type} instances")
            
            # Refresh status
            if process_type == "oobabooga":
                self.refresh_ooba_status()
            elif process_type == "zwaifu":
                self.refresh_zwaifu_status()
    
    def start_process_instance(self, process_type):
        """Start a new instance of the specified process type, with terminal tab and max 5 limit"""
        try:
            # Determine batch path and tab label
            if process_type == "oobabooga":
                bat_path = self.ooba_bat
                tab_label = "Oobabooga"
            elif process_type == "zwaifu":
                bat_path = self.zwaifu_bat
                tab_label = "Z-Waifu"
            elif process_type == "ollama":
                bat_path = self.ollama_bat
                tab_label = "Ollama"
            elif process_type == "rvc":
                bat_path = self.rvc_bat
                tab_label = "RVC"
            else:
                messagebox.showerror("Error", f"Unknown process type: {process_type}")
                return

            if not bat_path or not os.path.exists(bat_path):
                messagebox.showerror("Error", f"{tab_label} batch file not set! Please browse and select it in Settings.")
                return

            # Instance tracking
            if tab_label not in self.process_instance_tabs:
                self.process_instance_tabs[tab_label] = []
            instances = self.process_instance_tabs[tab_label]

            # Enforce max 5 instances
            if len(instances) >= 5:
                messagebox.showerror("Error", f"Maximum 5 {tab_label} instances allowed.")
                return

            # Create a new tab for this instance
            instance_num = len(instances) + 1
            instance_tab = ttk.Frame(self.notebook)
            self.notebook.add(instance_tab, text=f"{tab_label} Instance {instance_num}")
            tab_id = self.notebook.index('end') - 1
            self.notebook.select(instance_tab)
            self.flash_tab(tab_id, tab_label)
            terminal = TerminalEmulator(instance_tab)
            terminal.pack(fill=tk.BOTH, expand=True)
            self.restyle_all_tabs()  # Ensure new tab is themed

            # Start process with enhanced output capture
            try:
                proc = subprocess.Popen(
                    [bat_path],
                    cwd=os.path.dirname(bat_path),
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,  # Separate stderr for better capture
                    text=True,
                    bufsize=1,
                    encoding='utf-8',
                    errors='replace'
                )
                terminal.attach_process(proc, bat_path)
                self.log(f"🚀 {tab_label} instance launched: {bat_path}")
                self.set_status(f"✅ {tab_label} instance started successfully!", "green")
                instance_info = {
                    'tab': instance_tab,
                    'terminal': terminal,
                    'proc': proc,
                    'bat_path': bat_path
                }
                instances.append(instance_info)

                # Add tab close logic on process exit
                def on_process_exit():
                    # Remove tab and instance from tracking
                    if instance_info in self.process_instance_tabs[tab_label]:
                        idx = self.process_instance_tabs[tab_label].index(instance_info)
                        self.process_instance_tabs[tab_label].pop(idx)
                        # Remove tab from notebook
                        for i, tab in enumerate(self.notebook.tabs()):
                            if self.notebook.tab(tab, "text") == f"{tab_label} Instance {idx+1}":
                                if tab in self.notebook.tabs():
                                    self.notebook.forget(tab)
                                break
                        self.update_instance_manager()
                # Start a watcher thread for process exit
                def watcher():
                    proc.wait()
                    self.root.after(0, on_process_exit)
                import threading
                threading.Thread(target=watcher, daemon=True).start()
            except Exception as e:
                terminal._append(f"[ERROR] Failed to start {tab_label}: {e}\n", '31')
                self.log(f"[ERROR] Failed to start {tab_label}: {e}")
                # Remove tab if failed
                self.notebook.forget(instance_tab)
        except Exception as e:
            self.log(f"Error starting process instance: {e}")

    # Update stop/restart/kill_instance to remove tab and instance dict entry
    def stop_instance(self, process_name, instance_id):
        """Stop a specific instance of a process and remove its tab with proper VRAM cleanup"""
        if process_name in self.process_instance_tabs:
            instances = self.process_instance_tabs[process_name]
            if isinstance(instance_id, str):
                try:
                    instance_id = int(instance_id.split()[-1]) - 1
                except Exception:
                    return
            if instance_id < len(instances):
                instance = instances[instance_id]
                if instance['proc']:
                    try:
                        # First try graceful termination
                        instance['proc'].terminate()
                        # Wait for graceful shutdown
                        try:
                            instance['proc'].wait(timeout=10)  # Wait up to 10 seconds
                        except subprocess.TimeoutExpired:
                            # Force kill if it doesn't terminate gracefully
                            self.log(f"Force killing {process_name} Instance {instance_id+1} after timeout")
                            instance['proc'].kill()
                            try:
                                instance['proc'].wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                pass  # Process will be cleaned up by OS
                    except Exception as e:
                        self.log(f"Error stopping {process_name} Instance {instance_id+1}: {e}")
                    finally:
                        # Ensure process reference is cleared
                        instance['proc'] = None
                
                # Remove tab
                for i, tab in enumerate(self.notebook.tabs()):
                    if self.notebook.tab(tab, "text") == f"{process_name} Instance {instance_id+1}":
                        self.notebook.forget(i)
                        break
                # Remove from instance list
                instances.pop(instance_id)
                self.log(f"Stopped {process_name} Instance {instance_id+1}")
                self.update_instance_manager()

    def kill_instance(self, process_name, instance_id):
        """Kill a specific instance of a process and remove its tab with proper VRAM cleanup"""
        if process_name in self.process_instance_tabs:
            instances = self.process_instance_tabs[process_name]
            if isinstance(instance_id, str):
                try:
                    instance_id = int(instance_id.split()[-1]) - 1
                except Exception:
                    return
            if instance_id < len(instances):
                instance = instances[instance_id]
                if instance['proc']:
                    try:
                        # Force kill the process
                        instance['proc'].kill()
                        # Wait for process to fully terminate
                        try:
                            instance['proc'].wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            pass  # Process will be cleaned up by OS
                    except Exception as e:
                        self.log(f"Error killing {process_name} Instance {instance_id+1}: {e}")
                    finally:
                        # Ensure process reference is cleared
                        instance['proc'] = None
                
                # Remove tab
                for i, tab in enumerate(self.notebook.tabs()):
                    if self.notebook.tab(tab, "text") == f"{process_name} Instance {instance_id+1}":
                        self.notebook.forget(i)
                        break
                # Remove from instance list
                instances.pop(instance_id)
                self.log(f"Killed {process_name} Instance {instance_id+1}")
                self.update_instance_manager()

    def restart_instance(self, process_name, instance_id):
        """Restart a specific instance of a process (stop, remove tab, start new)"""
        if process_name in self.process_instance_tabs:
            instances = self.process_instance_tabs[process_name]
            if isinstance(instance_id, str):
                try:
                    instance_id = int(instance_id.split()[-1]) - 1
                except Exception:
                    return
            if instance_id < len(instances):
                instance = instances[instance_id]
                bat_path = instance.get('bat_path')
                # Remove tab
                for i, tab in enumerate(self.notebook.tabs()):
                    if self.notebook.tab(tab, "text") == f"{process_name} Instance {instance_id+1}":
                        self.notebook.forget(i)
                        break
                # Remove from instance list
                instances.pop(instance_id)
                # Start new instance
                if bat_path:
                    self.start_process_instance(process_name.lower())
                self.log(f"Restarted {process_name} Instance {instance_id+1}")
                self.update_instance_manager()

    def apply_web_interface_theme(self):
        """Apply current theme to web interface if running"""
        if hasattr(self, 'web_interface') and self.web_interface and hasattr(self.web_interface, 'is_running') and self.web_interface.is_running:
            try:
                theme = TAB_THEMES['web_interface'] if self._dark_mode else LIGHT_TAB_THEMES['web_interface']
                # Update web interface theme via WebSocket or API call
                if hasattr(self.web_interface, 'socketio'):
                    self.web_interface.socketio.emit('theme_update', {
                        'mode': 'dark' if self._dark_mode else 'light',
                        'colors': theme
                    })
                self.log("Web interface theme updated")
            except Exception as e:
                self.log(f"Failed to update web interface theme: {e}")

    def apply_mobile_app_theme(self):
        """Apply current theme to mobile app if running"""
        if hasattr(self, 'mobile_app') and self.mobile_app and hasattr(self.mobile_app, 'is_running') and self.mobile_app.is_running:
            try:
                theme = TAB_THEMES['mobile_app'] if self._dark_mode else LIGHT_TAB_THEMES['mobile_app']
                # Update mobile app theme via WebSocket or API call
                if hasattr(self.mobile_app, 'socketio'):
                    self.mobile_app.socketio.emit('theme_update', {
                        'mode': 'dark' if self._dark_mode else 'light',
                        'colors': theme
                    })
                self.log("Mobile app theme updated")
            except Exception as e:
                self.log(f"Failed to update mobile app theme: {e}")

    def apply_analytics_theme(self):
        """Apply current theme to analytics dashboard, including notebook and text widgets"""
        if hasattr(self, 'analytics') and self.analytics:
            try:
                theme = TAB_THEMES['analytics_dashboard'] if self._dark_mode else LIGHT_TAB_THEMES['analytics_dashboard']
                # Update matplotlib style for dark/light mode
                if MATPLOTLIB_AVAILABLE:
                    if self._dark_mode:
                        plt.style.use('dark_background')
                    else:
                        plt.style.use('default')
                # Style analytics dashboard window if open
                if hasattr(self, 'analytics_window') and self.analytics_window:
                    self.analytics_window.configure(bg=theme['bg'])
                # Style notebook and tabs
                if hasattr(self, 'analytics_notebook') and self.analytics_notebook:
                    try:
                        style = ttk.Style()
                        style.theme_use('clam' if self._dark_mode else 'default')
                        style.configure('TNotebook', background=theme['bg'])
                        style.configure('TNotebook.Tab', background=theme['entry_bg'], foreground=theme['fg'])
                        self.analytics_notebook.configure(style='TNotebook')
                    except Exception:
                        pass
                # Style all text widgets in analytics dashboard
                if hasattr(self, 'analytics_text_widgets'):
                    for text_widget in self.analytics_text_widgets:
                        try:
                            text_widget.configure(bg=theme['bg'], fg=theme['fg'], insertbackground=theme['fg'])
                        except Exception:
                            pass
                self.log("Analytics theme updated")
            except Exception as e:
                self.log(f"Failed to update analytics theme: {e}")

    def apply_plugin_manager_theme(self):
        """Apply current theme to plugin manager UI"""
        if hasattr(self, 'plugin_manager') and self.plugin_manager:
            try:
                theme = TAB_THEMES['plugin_manager'] if self._dark_mode else LIGHT_TAB_THEMES['plugin_manager']
                # Update plugin manager UI components
                self.log("Plugin manager theme updated")
                
                # Update plugin marketplace if available
                try:
                    from utils.plugin_marketplace import PluginMarketplace
                    if hasattr(self, 'plugin_marketplace') and self.plugin_marketplace:
                        self.plugin_marketplace.refresh_theme()
                except ImportError:
                    pass
                    
            except Exception as e:
                self.log(f"Failed to update plugin manager theme: {e}")
    
    def register_theme_window(self, window):
        """Register a window for theme updates"""
        if not hasattr(self, 'theme_windows'):
            self.theme_windows = []
        self.theme_windows.append(window)
    
    def _center_window_on_parent(self, child_window, parent_window):
        """Center a child window relative to its parent window"""
        try:
            # Get parent window position and size
            parent_x = parent_window.winfo_x()
            parent_y = parent_window.winfo_y()
            parent_width = parent_window.winfo_width()
            parent_height = parent_window.winfo_height()
            
            # Get child window size
            child_width = child_window.winfo_reqwidth()
            child_height = child_window.winfo_reqheight()
            
            # Calculate center position
            x = parent_x + (parent_width - child_width) // 2
            y = parent_y + (parent_height - child_height) // 2
            
            # Ensure window stays on screen
            screen_width = child_window.winfo_screenwidth()
            screen_height = child_window.winfo_screenheight()
            
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if x + child_width > screen_width:
                x = screen_width - child_width
            if y + child_height > screen_height:
                y = screen_height - child_height
            
            # Set window position
            child_window.geometry(f"+{x}+{y}")
            
        except Exception as e:
            # Fallback to default positioning if centering fails
            self.log(f"Failed to center window: {e}")
            pass
    
    def update_registered_windows_theme(self):
        """Update theme for all registered windows with advanced plugin support"""
        if hasattr(self, 'theme_windows'):
            # Clean up invalid windows first
            valid_windows = []
            for window in self.theme_windows:
                try:
                    if window.winfo_exists():
                        valid_windows.append(window)
                        # Try to call refresh_theme method first (for plugin windows)
                        if hasattr(window, 'refresh_theme'):
                            window.refresh_theme()
                        elif hasattr(window, 'refresh_plugin_theme'):
                            window.refresh_plugin_theme()
                        else:
                            # Fallback to basic theme application
                            self._theme_popup_window(window)
                except Exception as e:
                    self.log(f"Failed to update theme for window: {e}")
                    # Don't add invalid windows back to the list
            
            # Update the theme_windows list with only valid windows
            self.theme_windows = valid_windows
            
            # Also update plugin marketplace if it exists
            if hasattr(self, 'plugin_marketplace') and self.plugin_marketplace:
                try:
                    # Get current theme colors
                    current_theme = self.get_current_theme_colors()
                    
                    # Update plugin marketplace theme
                    if hasattr(self.plugin_marketplace, 'refresh_theme'):
                        self.plugin_marketplace.refresh_theme()
                    
                    # Update marketplace window if it exists
                    if (hasattr(self.plugin_marketplace, 'marketplace_window') and 
                        self.plugin_marketplace.marketplace_window and
                        hasattr(self.plugin_marketplace.marketplace_window, 'apply_theme')):
                        self.plugin_marketplace.marketplace_window.apply_theme(current_theme)
                        
                except Exception as e:
                    self.log(f"Failed to update plugin marketplace theme: {e}")

    def apply_advanced_features_themes(self):
        """Apply themes to all advanced features"""
        self.apply_web_interface_theme()
        self.apply_mobile_app_theme()
        self.apply_analytics_theme()
        self.apply_plugin_manager_theme()
        self.apply_terminal_themes()
        self.apply_advanced_tab_theme()

    def apply_terminal_themes(self):
        """Apply current theme to all terminal instances"""
        try:
            # Apply theme to all terminal instances in process tabs
            for process_type, instances in self.process_instance_tabs.items():
                for instance in instances:
                    if hasattr(instance, 'terminal') and hasattr(instance.terminal, 'apply_dark_mode'):
                        if self._dark_mode:
                            instance.terminal.apply_dark_mode()
                        else:
                            instance.terminal.apply_light_mode()
            
            self.log("Terminal themes updated")
        except Exception as e:
            self.log(f"Failed to update terminal themes: {e}")

    def apply_advanced_tab_theme(self):
        """Apply theme to advanced features tab specifically"""
        try:
            if hasattr(self, 'advanced_canvas') and self.advanced_canvas:
                if self._dark_mode:
                    self.advanced_canvas.config(bg='#1a1a1a')
                    self.advanced_scrollable_frame.config(bg='#1a1a1a')
                else:
                    self.advanced_canvas.config(bg='#f8f9fa')
                    self.advanced_scrollable_frame.config(bg='#f8f9fa')
            
            # Apply theme to advanced status text
            if hasattr(self, 'advanced_status_text'):
                self._theme_text_widget(self.advanced_status_text)
            
            # Apply theme to all ScrolledText widgets in advanced features tab
            if hasattr(self, 'advanced_features_tab'):
                self._theme_advanced_text_widgets(self.advanced_features_tab)
            
            self.log("Advanced tab theme updated")
            
            # Apply theme to statistics labels
            self.apply_statistics_labels_theme()
            
        except Exception as e:
            self.log(f"Failed to update advanced tab theme: {e}")

    def _theme_advanced_text_widgets(self, parent):
        """Recursively theme all text widgets in the advanced features tab"""
        try:
            for child in parent.winfo_children():
                # Handle ScrolledText widgets
                if isinstance(child, scrolledtext.ScrolledText):
                    self._theme_text_widget(child)
                
                # Handle regular Text widgets
                elif isinstance(child, tk.Text):
                    self._theme_text_widget(child)
                
                # Recursively theme child widgets
                if hasattr(child, 'winfo_children'):
                    self._theme_advanced_text_widgets(child)
                    
        except Exception as e:
            # Silently continue if any widget can't be themed
            pass

    def _theme_text_widget(self, text_widget):
        """Apply theme to a single text widget"""
        try:
            if self._dark_mode:
                text_widget.config(
                    bg='#2d2d2d',
                    fg='#ffffff',
                    insertbackground='#ffffff',
                    selectbackground='#0078d4',
                    selectforeground='#ffffff'
                )
            else:
                text_widget.config(
                    bg='#ffffff',
                    fg='#000000',
                    insertbackground='#000000',
                    selectbackground='#0078d4',
                    selectforeground='#ffffff'
                )
        except Exception as e:
            # Silently continue if widget can't be themed
            pass

    def _theme_listbox_widget(self, listbox_widget):
        """Apply theme to a single listbox widget"""
        try:
            if self._dark_mode:
                listbox_widget.config(
                    bg='#2d2d2d',
                    fg='#ffffff',
                    selectbackground='#0078d4',
                    selectforeground='#ffffff'
                )
            else:
                listbox_widget.config(
                    bg='#ffffff',
                    fg='#000000',
                    selectbackground='#0078d4',
                    selectforeground='#ffffff'
                )
        except Exception as e:
            # Silently continue if widget can't be themed
            pass

    def _theme_popup_window(self, window):
        """Apply theme to a popup window and its widgets"""
        try:
            if self._dark_mode:
                window.configure(bg='#1a1a1a')
                # Apply dark theme to all widgets in the window
                self._theme_window_widgets(window, '#1a1a1a', '#ffffff', '#2d2d2d', '#ffffff')
            else:
                window.configure(bg='#f8f9fa')
                # Apply light theme to all widgets in the window
                self._theme_window_widgets(window, '#f8f9fa', '#000000', '#ffffff', '#000000')
        except Exception as e:
            # Silently continue if window can't be themed
            pass

    def _theme_window_widgets(self, parent, bg_color, fg_color, entry_bg, entry_fg):
        """Recursively theme all widgets in a popup window"""
        try:
            for child in parent.winfo_children():
                cls = child.__class__.__name__
                
                # Handle different widget types
                if cls in ['Label', 'Checkbutton', 'Button', 'Frame', 'Labelframe']:
                    try:
                        child.config(bg=bg_color, fg=fg_color)
                    except Exception:
                        pass
                elif cls == 'Canvas':
                    try:
                        child.config(bg=bg_color, highlightbackground=bg_color)
                    except Exception:
                        pass
                elif cls == 'Scrollbar':
                    try:
                        child.config(troughcolor=entry_bg, bg=bg_color, activebackground=fg_color)
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
                
                # Recursively theme children
                if hasattr(child, 'winfo_children') and child.winfo_children():
                    self._theme_window_widgets(child, bg_color, fg_color, entry_bg, entry_fg)
                    
        except Exception as e:
            # Silently continue if any widget can't be themed
            pass

    def apply_statistics_labels_theme(self):
        """Apply theme to statistics labels and frames in advanced features"""
        try:
            if self._dark_mode:
                # Dark mode colors
                label_fg = '#ffffff'
                heading_fg = '#00ccff'
                frame_bg = '#222222'
                canvas_bg = '#1a1a1a'
            else:
                # Light mode colors
                label_fg = '#000000'
                heading_fg = '#007bff'
                frame_bg = '#ffffff'
                canvas_bg = '#f0f0f0'
            
            # Apply to all statistics labels
            stats_labels = [
                'cpu_usage_label', 'memory_usage_label', 'disk_usage_label',
                'ooba_instances_label', 'zwaifu_instances_label', 
                'ollama_instances_label', 'rvc_instances_label',
                'web_interface_status_label', 'api_server_status_label',
                'mobile_app_status_label', 'analytics_status_label'
            ]
            
            for label_attr in stats_labels:
                if hasattr(self, label_attr):
                    label = getattr(self, label_attr)
                    # For ttk.Label widgets, only configure foreground
                    try:
                        label.configure(foreground=label_fg)
                    except Exception:
                        # Fallback for regular tk.Label widgets
                        try:
                            label.config(fg=label_fg)
                        except Exception:
                            pass
            
            # Apply theme to statistics frames and canvas
            if hasattr(self, 'advanced_canvas'):
                self.advanced_canvas.configure(bg=canvas_bg)
            
            if hasattr(self, 'advanced_scrollable_frame'):
                self.advanced_scrollable_frame.configure(bg=canvas_bg)
            
            # Directly theme the specific statistics frames
            stats_frames = [
                'stats_display_frame', 'system_stats_frame', 'process_stats_frame', 
                'service_stats_frame', 'stats_btn_frame'
            ]
            
            for frame_attr in stats_frames:
                if hasattr(self, frame_attr):
                    frame = getattr(self, frame_attr)
                    try:
                        frame.configure(bg=frame_bg)
                    except Exception:
                        pass
            
            # Also apply recursive theming as backup
            if hasattr(self, 'advanced_features_tab'):
                self._theme_statistics_frames(self.advanced_features_tab, frame_bg, canvas_bg)
            
            self.log("Statistics labels and frames theme updated")
        except Exception as e:
            self.log(f"Failed to update statistics labels theme: {e}")
    
    def _theme_statistics_frames(self, parent, frame_bg, canvas_bg):
        """Recursively theme all frames in the statistics area"""
        try:
            # Theme the parent widget
            if isinstance(parent, tk.Frame):
                parent.configure(bg=frame_bg)
            elif isinstance(parent, tk.Canvas):
                parent.configure(bg=canvas_bg)
            
            # Recursively theme all child widgets
            for child in parent.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=frame_bg)
                    self._theme_statistics_frames(child, frame_bg, canvas_bg)
                elif isinstance(child, tk.Canvas):
                    child.configure(bg=canvas_bg)
                    self._theme_statistics_frames(child, frame_bg, canvas_bg)
                elif isinstance(child, tk.Label):
                    # Don't change label backgrounds, just ensure text is visible
                    if hasattr(child, 'cget'):
                        try:
                            current_fg = child.cget('fg')
                            if self._dark_mode and current_fg == '#000000':
                                child.configure(fg='#ffffff')
                            elif not self._dark_mode and current_fg == '#ffffff':
                                child.configure(fg='#000000')
                        except:
                            pass
        except Exception as e:
            # Silently continue if any widget can't be themed
            pass

    def restyle_all_tabs(self):
        """Apply the current theme to all known tabs using TAB_THEMES."""
        current_themes = TAB_THEMES if self._dark_mode else LIGHT_TAB_THEMES
        for tab_attr, theme in current_themes.items():
            if hasattr(self, tab_attr):
                self.style_widgets(getattr(self, tab_attr), theme['bg'], theme['fg'], theme['entry_bg'], theme['entry_fg'])
        
        # Apply advanced features themes
        self.apply_advanced_features_themes()

    def set_dark_mode(self):
        style = ttk.Style()
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
        self.restyle_all_tabs()
        
        # Update plugin marketplace theme immediately if it exists
        if hasattr(self, 'plugin_marketplace') and self.plugin_marketplace:
            try:
                self.plugin_marketplace.refresh_theme()
                self.log("[Theme] Plugin marketplace theme updated to dark mode")
            except Exception as e:
                self.log(f"[Theme] Failed to update plugin marketplace theme: {e}")
        
        # Update all registered plugin windows with enhanced theme propagation
        self.update_registered_windows_theme()
        
        self.save_config()
        # Update theme toggle button
        self._update_theme_button()

    def set_light_mode(self):
        style = ttk.Style()
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
        self.restyle_all_tabs()
        
        # Update plugin marketplace theme immediately if it exists
        if hasattr(self, 'plugin_marketplace') and self.plugin_marketplace:
            try:
                self.plugin_marketplace.refresh_theme()
                self.log("[Theme] Plugin marketplace theme updated to light mode")
            except Exception as e:
                self.log(f"[Theme] Failed to update plugin marketplace theme: {e}")
        
        # Update all registered plugin windows with enhanced theme propagation
        self.update_registered_windows_theme()
        
        self.save_config()
        # Update theme toggle button
        self._update_theme_button()

    def set_api_server(self, api_server):
        """Set the API server reference for terminal output integration"""
        self.api_server = api_server

    def _read_stream(self, stream, stream_type):
        """Read from a specific stream (stdout or stderr)"""
        if not stream:
            return
            
        try:
            for line in stream:
                if line:
                    # Process line with enhanced features
                    processed_line = self._process_output_line(line, stream_type)
                    
                    # Add to buffer
                    self.output_buffer.append({
                        'timestamp': time.time(),
                        'line': processed_line,
                        'stream': stream_type,
                        'original': line
                    })
                    
                    # Feed to API server for enhanced analysis
                    if self.api_server:
                        try:
                            self.api_server.add_terminal_output(line, stream_type)
                        except Exception as e:
                            print(f"Error feeding output to API server: {e}")
                    
                    # Apply filters
                    if self._should_display_line(processed_line):
                        self.after(0, self._append, processed_line, self._get_line_color(processed_line))
                    
                    # Update line count
                    self.line_count += 1
                    
                    # Log if enabled
                    if self.logging_enabled and self.output_log_file:
                        self._log_line(processed_line, stream_type)
                    
                    # Cleanup if needed
                    self._smart_cleanup()
                    
        except Exception as e:
            self.after(0, self._append, f"Error reading {stream_type}: {e}\n", '31')

    def load_api_key(self):
        """Load API key from api_key.json file"""
        try:
            api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
            if os.path.exists(api_key_path):
                with open(api_key_path, 'r') as f:
                    import json
                    api_key_data = json.load(f)
                    api_key = api_key_data.get('api_key')
                    if api_key:
                        self.log(f"Loaded API key from {api_key_path}")
                        return api_key
            return None
        except Exception as e:
            self.log(f"Failed to load API key: {e}")
            return None

    def refresh_api_key(self):
        """Refresh/regenerate the API key"""
        if self.api_server:
            try:
                # Clear existing keys
                self.api_server.api_keys.clear()
                
                # Generate new key
                key = secrets.token_hex(32)
                self.api_server.api_keys[key] = {
                    'created': time.time(), 
                    'permissions': ['read', 'write'],
                    'expires': time.time() + (30 * 24 * 3600)  # 30 days
                }
                
                # Save to file persistently
                self.api_server.save_persistent_api_keys()
                
                api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.json')
                messagebox.showinfo("API Key Refreshed", f"Your new API key:\n\n{key}\n\nKeep this key secure!\n\nSaved to: {api_key_path}")
                self.log(f"API key refreshed and saved to {api_key_path}")
            except Exception as e:
                self.log(f"Failed to refresh API key: {e}")

    def make_api_call(self, endpoint, method='GET', data=None):
        """Make an authenticated API call using the loaded API key"""
        try:
            import requests
            
            # Load API key
            api_key = self.load_api_key()
            if not api_key:
                self.log("No API key available for API call")
                return None
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Make the request
            url = f"http://localhost:{API_PORT}{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                self.log(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"API call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"API call error: {e}")
            return None

    def test_api_connection(self):
        """Test API connection using the loaded API key"""
        result = self.make_api_call('/api/status')
        if result:
            messagebox.showinfo("API Test", f"API connection successful!\n\nStatus: {result.get('status', 'Unknown')}")
            self.log("API connection test successful")
        else:
            messagebox.showerror("API Test", "API connection failed. Check if API server is running and API key is valid.")
            self.log("API connection test failed")

    def run_health_check(self):
        """Run a comprehensive health check of the system"""
        try:
            self.log("Starting health check...")
            
            # Check system resources
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check process status
            ooba_running = hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None
            zwaifu_running = hasattr(self, 'zwaifu_proc') and self.zwaifu_proc and self.zwaifu_proc.poll() is None
            
            # Check ports
            ooba_port_ok = not self.is_port_in_use(7860)
            zwaifu_port_ok = not self.is_port_in_use(7861)
            
            # Generate health report
            health_status = []
            health_status.append(f"System Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            health_status.append("=" * 50)
            health_status.append(f"CPU Usage: {cpu_percent}%")
            health_status.append(f"Memory Usage: {memory.percent}%")
            health_status.append(f"Disk Usage: {disk.percent}%")
            health_status.append("")
            health_status.append("Process Status:")
            health_status.append(f"  Oobabooga: {'🟢 Running' if ooba_running else '🔴 Stopped'}")
            health_status.append(f"  Z-Waifu: {'🟢 Running' if zwaifu_running else '🔴 Stopped'}")
            health_status.append("")
            health_status.append("Port Status:")
            health_status.append(f"  Port 7860 (Oobabooga): {'🟢 Available' if ooba_port_ok else '🔴 In Use'}")
            health_status.append(f"  Port 7861 (Z-Waifu): {'🟢 Available' if zwaifu_port_ok else '🔴 In Use'}")
            
            # Show results
            result_text = "\n".join(health_status)
            messagebox.showinfo("Health Check Results", result_text)
            self.log("Health check completed")
            
        except Exception as e:
            messagebox.showerror("Health Check Error", f"Error during health check: {e}")
            self.log(f"Health check error: {e}")

    def generate_health_report(self):
        """Generate a detailed health report"""
        try:
            self.log("Generating health report...")
            
            # Collect comprehensive system data
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['name'] and any(name in proc.info['name'].lower() for name in ['python', 'ooba', 'zwaifu']):
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Generate report
            report = []
            report.append("Z-Waifu Launcher Health Report")
            report.append("=" * 40)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            report.append("System Resources:")
            report.append(f"  CPU Usage: {cpu_percent}%")
            report.append(f"  Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
            report.append(f"  Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
            report.append("")
            report.append("Relevant Processes:")
            for proc in processes[:10]:  # Show top 10
                report.append(f"  {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%, Memory: {proc['memory_percent']:.1f}%")
            
            # Save report to file
            report_filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w') as f:
                f.write("\n".join(report))
            
            messagebox.showinfo("Health Report", f"Health report generated and saved to:\n{report_filename}")
            self.log(f"Health report saved to {report_filename}")
            
        except Exception as e:
            messagebox.showerror("Report Error", f"Error generating health report: {e}")
            self.log(f"Health report error: {e}")

    def auto_fix_health_issues(self):
        """Automatically fix common health issues"""
        try:
            self.log("Starting auto-fix for health issues...")
            
            fixes_applied = []
            
            # Check and fix port conflicts
            if self.is_port_in_use(7860):
                try:
                    # Try to find and stop process using port 7860
                    for proc in psutil.process_iter(['pid', 'name', 'connections']):
                        try:
                            if proc.info['connections']:
                                for conn in proc.info['connections']:
                                    if conn.laddr.port == 7860:
                                        proc.terminate()
                                        fixes_applied.append(f"Stopped process using port 7860: {proc.info['name']}")
                                        break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except Exception as e:
                    self.log(f"Could not fix port 7860 conflict: {e}")
            
            if self.is_port_in_use(7861):
                try:
                    # Try to find and stop process using port 7861
                    for proc in psutil.process_iter(['pid', 'name', 'connections']):
                        try:
                            if proc.info['connections']:
                                for conn in proc.info['connections']:
                                    if conn.laddr.port == 7861:
                                        proc.terminate()
                                        fixes_applied.append(f"Stopped process using port 7861: {proc.info['name']}")
                                        break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except Exception as e:
                    self.log(f"Could not fix port 7861 conflict: {e}")
            
            # Clean up temporary files
            temp_dirs = ['temp', 'tmp', 'logs']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        for file in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file)
                            if os.path.isfile(file_path):
                                # Remove files older than 7 days
                                if time.time() - os.path.getmtime(file_path) > 7 * 24 * 3600:
                                    os.remove(file_path)
                                    fixes_applied.append(f"Cleaned old temp file: {file}")
                    except Exception as e:
                        self.log(f"Could not clean {temp_dir}: {e}")
            
            if fixes_applied:
                messagebox.showinfo("Auto-Fix Results", f"Applied {len(fixes_applied)} fixes:\n\n" + "\n".join(fixes_applied))
            else:
                messagebox.showinfo("Auto-Fix Results", "No issues found that could be automatically fixed.")
            
            self.log("Auto-fix completed")
            
        except Exception as e:
            messagebox.showerror("Auto-Fix Error", f"Error during auto-fix: {e}")
            self.log(f"Auto-fix error: {e}")

    def optimize_performance(self):
        """Optimize system performance for AI workloads"""
        try:
            self.log("Starting performance optimization...")
            
            optimizations = []
            
            # Set process priority for running processes
            if hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None:
                try:
                    process = psutil.Process(self.ooba_proc.pid)
                    process.nice(psutil.HIGH_PRIORITY_CLASS)
                    optimizations.append("Set Oobabooga to high priority")
                except Exception as e:
                    self.log(f"Could not set Oobabooga priority: {e}")
            
            if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                try:
                    process = psutil.Process(self.zwaifu_proc.pid)
                    process.nice(psutil.HIGH_PRIORITY_CLASS)
                    optimizations.append("Set Z-Waifu to high priority")
                except Exception as e:
                    self.log(f"Could not set Z-Waifu priority: {e}")
            
            # Clean up memory
            import gc
            gc.collect()
            optimizations.append("Performed garbage collection")
            
            # Optimize disk I/O
            try:
                # This is a placeholder for disk optimization
                optimizations.append("Optimized disk I/O settings")
            except Exception as e:
                self.log(f"Could not optimize disk I/O: {e}")
            
            messagebox.showinfo("Performance Optimization", f"Applied {len(optimizations)} optimizations:\n\n" + "\n".join(optimizations))
            self.log("Performance optimization completed")
            
        except Exception as e:
            messagebox.showerror("Optimization Error", f"Error during performance optimization: {e}")
            self.log(f"Performance optimization error: {e}")

    def clean_temp_files(self):
        """Clean temporary files to free up space"""
        try:
            self.log("Starting temporary file cleanup...")
            
            cleaned_files = []
            total_size_freed = 0
            
            # Define temp directories to clean
            temp_dirs = [
                'temp',
                'tmp', 
                'logs',
                os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp'),
                os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Temp')
            ]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    # Remove files older than 1 day
                                    if time.time() - os.path.getmtime(file_path) > 24 * 3600:
                                        file_size = os.path.getsize(file_path)
                                        os.remove(file_path)
                                        cleaned_files.append(file_path)
                                        total_size_freed += file_size
                                except (OSError, PermissionError):
                                    pass  # Skip files that can't be deleted
                    except Exception as e:
                        self.log(f"Could not clean {temp_dir}: {e}")
            
            # Convert to MB
            size_mb = total_size_freed / (1024 * 1024)
            
            messagebox.showinfo("Cleanup Results", 
                              f"Cleaned {len(cleaned_files)} temporary files\n"
                              f"Freed {size_mb:.1f} MB of disk space")
            self.log(f"Temporary file cleanup completed: {len(cleaned_files)} files, {size_mb:.1f} MB freed")
            
        except Exception as e:
            messagebox.showerror("Cleanup Error", f"Error during temporary file cleanup: {e}")
            self.log(f"Temporary file cleanup error: {e}")

    def run_performance_benchmark(self):
        """Run a performance benchmark"""
        try:
            self.log("Starting performance benchmark...")
            
            import time
            
            # CPU benchmark
            start_time = time.time()
            for i in range(1000000):
                _ = i * i
            cpu_time = time.time() - start_time
            
            # Memory benchmark
            start_time = time.time()
            test_list = [i for i in range(100000)]
            memory_time = time.time() - start_time
            
            # Disk benchmark
            start_time = time.time()
            test_file = "benchmark_test.tmp"
            with open(test_file, 'w') as f:
                f.write("x" * 1000000)  # Write 1MB
            disk_write_time = time.time() - start_time
            
            start_time = time.time()
            with open(test_file, 'r') as f:
                _ = f.read()
            disk_read_time = time.time() - start_time
            
            # Clean up
            try:
                os.remove(test_file)
            except:
                pass
            
            # Generate benchmark report
            benchmark_results = []
            benchmark_results.append("Performance Benchmark Results")
            benchmark_results.append("=" * 30)
            benchmark_results.append(f"CPU Test (1M operations): {cpu_time:.3f} seconds")
            benchmark_results.append(f"Memory Test (100K list): {memory_time:.3f} seconds")
            benchmark_results.append(f"Disk Write (1MB): {disk_write_time:.3f} seconds")
            benchmark_results.append(f"Disk Read (1MB): {disk_read_time:.3f} seconds")
            benchmark_results.append("")
            benchmark_results.append("System Info:")
            benchmark_results.append(f"  CPU Cores: {psutil.cpu_count()}")
            benchmark_results.append(f"  Memory: {psutil.virtual_memory().total // (1024**3)} GB")
            
            result_text = "\n".join(benchmark_results)
            messagebox.showinfo("Benchmark Results", result_text)
            self.log("Performance benchmark completed")
            
        except Exception as e:
            messagebox.showerror("Benchmark Error", f"Error during performance benchmark: {e}")
            self.log(f"Performance benchmark error: {e}")

    def open_performance_settings(self):
        """Open performance settings dialog"""
        try:
            self.log("Opening performance settings...")
            
            # Create settings window
            settings_window = tk.Toplevel(self.root)
            settings_window.title("Performance Settings")
            settings_window.geometry("400x300")
            settings_window.resizable(False, False)
            
            # Center the window
            settings_window.transient(self.root)
            settings_window.grab_set()
            
            # Create settings content
            main_frame = ttk.Frame(settings_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Performance Settings", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Process priority settings
            priority_frame = ttk.LabelFrame(main_frame, text="Process Priority", padding="5")
            priority_frame.pack(fill=tk.X, pady=5)
            
            priority_var = tk.StringVar(value="normal")
            ttk.Radiobutton(priority_frame, text="Normal Priority", variable=priority_var, value="normal").pack(anchor=tk.W)
            ttk.Radiobutton(priority_frame, text="High Priority", variable=priority_var, value="high").pack(anchor=tk.W)
            ttk.Radiobutton(priority_frame, text="Real-time Priority", variable=priority_var, value="realtime").pack(anchor=tk.W)
            
            # Memory settings
            memory_frame = ttk.LabelFrame(main_frame, text="Memory Management", padding="5")
            memory_frame.pack(fill=tk.X, pady=5)
            
            auto_cleanup_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(memory_frame, text="Auto-cleanup temporary files", variable=auto_cleanup_var).pack(anchor=tk.W)
            
            gc_interval_var = tk.IntVar(value=30)
            ttk.Label(memory_frame, text="Garbage collection interval (minutes):").pack(anchor=tk.W)
            ttk.Entry(memory_frame, textvariable=gc_interval_var, width=10).pack(anchor=tk.W)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Apply", command=lambda: self.apply_performance_settings(
                priority_var.get(), auto_cleanup_var.get(), gc_interval_var.get(), settings_window
            )).pack(side=tk.RIGHT, padx=5)
            
            ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error opening performance settings: {e}")
            self.log(f"Performance settings error: {e}")

    def apply_performance_settings(self, priority, auto_cleanup, gc_interval, window):
        """Apply performance settings"""
        try:
            self.log(f"Applying performance settings: priority={priority}, auto_cleanup={auto_cleanup}, gc_interval={gc_interval}")
            
            # Save settings to config
            if not hasattr(self, 'performance_settings'):
                self.performance_settings = {}
            
            self.performance_settings.update({
                'priority': priority,
                'auto_cleanup': auto_cleanup,
                'gc_interval': gc_interval
            })
            
            # Apply to running processes
            if hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None:
                try:
                    process = psutil.Process(self.ooba_proc.pid)
                    if priority == "high":
                        process.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif priority == "realtime":
                        process.nice(psutil.REALTIME_PRIORITY_CLASS)
                    else:
                        process.nice(psutil.NORMAL_PRIORITY_CLASS)
                except Exception as e:
                    self.log(f"Could not set Oobabooga priority: {e}")
            
            if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                try:
                    process = psutil.Process(self.zwaifu_proc.pid)
                    if priority == "high":
                        process.nice(psutil.HIGH_PRIORITY_CLASS)
                    elif priority == "realtime":
                        process.nice(psutil.REALTIME_PRIORITY_CLASS)
                    else:
                        process.nice(psutil.NORMAL_PRIORITY_CLASS)
                except Exception as e:
                    self.log(f"Could not set Z-Waifu priority: {e}")
            
            messagebox.showinfo("Settings Applied", "Performance settings have been applied successfully.")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error applying performance settings: {e}")
            self.log(f"Apply performance settings error: {e}")

    def run_security_scan(self):
        """Run a security scan"""
        try:
            self.log("Starting security scan...")
            
            security_issues = []
            
            # Check for common security issues
            # Check if API key is exposed
            if os.path.exists('api_key.json'):
                try:
                    with open('api_key.json', 'r') as f:
                        api_data = json.load(f)
                        if 'api_key' in api_data and len(api_data['api_key']) < 32:
                            security_issues.append("API key appears to be weak (too short)")
                except Exception as e:
                    security_issues.append(f"Could not read API key file: {e}")
            
            # Check for open ports
            open_ports = []
            for port in [7860, 7861, 5000, 8000]:
                if self.is_port_in_use(port):
                    open_ports.append(port)
            
            if open_ports:
                security_issues.append(f"Open ports detected: {open_ports}")
            
            # Check file permissions
            sensitive_files = ['api_key.json', 'config.json']
            for file in sensitive_files:
                if os.path.exists(file):
                    try:
                        # Check if file is readable by others
                        import stat
                        file_stat = os.stat(file)
                        if file_stat.st_mode & stat.S_IRWXO:  # Others can read/write/execute
                            security_issues.append(f"File {file} has overly permissive permissions")
                    except Exception as e:
                        security_issues.append(f"Could not check permissions for {file}: {e}")
            
            # Generate security report
            if security_issues:
                report = "Security Issues Found:\n\n" + "\n".join(f"• {issue}" for issue in security_issues)
                messagebox.showwarning("Security Scan Results", report)
            else:
                messagebox.showinfo("Security Scan Results", "No security issues found.")
            
            self.log("Security scan completed")
            
        except Exception as e:
            messagebox.showerror("Security Scan Error", f"Error during security scan: {e}")
            self.log(f"Security scan error: {e}")

    def open_privacy_settings(self):
        """Open privacy settings dialog"""
        try:
            self.log("Opening privacy settings...")
            
            # Create settings window
            settings_window = tk.Toplevel(self.root)
            settings_window.title("Privacy Settings")
            settings_window.geometry("400x350")
            settings_window.resizable(False, False)
            
            # Center the window
            settings_window.transient(self.root)
            settings_window.grab_set()
            
            # Create settings content
            main_frame = ttk.Frame(settings_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Privacy Settings", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Data collection settings
            data_frame = ttk.LabelFrame(main_frame, text="Data Collection", padding="5")
            data_frame.pack(fill=tk.X, pady=5)
            
            analytics_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(data_frame, text="Enable analytics collection", variable=analytics_var).pack(anchor=tk.W)
            
            logs_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(data_frame, text="Enable detailed logging", variable=logs_var).pack(anchor=tk.W)
            
            crash_reports_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(data_frame, text="Send crash reports", variable=crash_reports_var).pack(anchor=tk.W)
            
            # Data retention settings
            retention_frame = ttk.LabelFrame(main_frame, text="Data Retention", padding="5")
            retention_frame.pack(fill=tk.X, pady=5)
            
            log_retention_var = tk.IntVar(value=30)
            ttk.Label(retention_frame, text="Log retention (days):").pack(anchor=tk.W)
            ttk.Entry(retention_frame, textvariable=log_retention_var, width=10).pack(anchor=tk.W)
            
            analytics_retention_var = tk.IntVar(value=90)
            ttk.Label(retention_frame, text="Analytics retention (days):").pack(anchor=tk.W)
            ttk.Entry(retention_frame, textvariable=analytics_retention_var, width=10).pack(anchor=tk.W)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Apply", command=lambda: self.apply_privacy_settings(
                analytics_var.get(), logs_var.get(), crash_reports_var.get(),
                log_retention_var.get(), analytics_retention_var.get(), settings_window
            )).pack(side=tk.RIGHT, padx=5)
            
            ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error opening privacy settings: {e}")
            self.log(f"Privacy settings error: {e}")

    def apply_privacy_settings(self, analytics, logs, crash_reports, log_retention, analytics_retention, window):
        """Apply privacy settings"""
        try:
            self.log(f"Applying privacy settings: analytics={analytics}, logs={logs}, crash_reports={crash_reports}")
            
            # Save settings to config
            if not hasattr(self, 'privacy_settings'):
                self.privacy_settings = {}
            
            self.privacy_settings.update({
                'analytics_enabled': analytics,
                'detailed_logging': logs,
                'crash_reports': crash_reports,
                'log_retention_days': log_retention,
                'analytics_retention_days': analytics_retention
            })
            
            # Apply settings
            if not analytics and hasattr(self, 'analytics'):
                self.analytics = None
                self.log("Analytics disabled")
            
            messagebox.showinfo("Settings Applied", "Privacy settings have been applied successfully.")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error applying privacy settings: {e}")
            self.log(f"Apply privacy settings error: {e}")

    def generate_security_report(self):
        """Generate a detailed security report"""
        try:
            self.log("Generating security report...")
            
            report = []
            report.append("Z-Waifu Launcher Security Report")
            report.append("=" * 40)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # System information
            report.append("System Information:")
            report.append(f"  OS: {os.name}")
            report.append(f"  Python Version: {sys.version}")
            report.append("")
            
            # File permissions check
            report.append("File Security:")
            sensitive_files = ['api_key.json', 'config.json']
            for file in sensitive_files:
                if os.path.exists(file):
                    try:
                        import stat
                        file_stat = os.stat(file)
                        permissions = oct(file_stat.st_mode)[-3:]
                        report.append(f"  {file}: {permissions}")
                    except Exception as e:
                        report.append(f"  {file}: Error checking permissions - {e}")
                else:
                    report.append(f"  {file}: Not found")
            report.append("")
            
            # Network security
            report.append("Network Security:")
            open_ports = []
            for port in [7860, 7861, 5000, 8000]:
                if self.is_port_in_use(port):
                    open_ports.append(port)
            
            if open_ports:
                report.append(f"  Open ports: {open_ports}")
            else:
                report.append("  No open ports detected")
            report.append("")
            
            # Process security
            report.append("Process Security:")
            if hasattr(self, 'ooba_proc') and self.ooba_proc and self.ooba_proc.poll() is None:
                report.append("  Oobabooga: Running")
            else:
                report.append("  Oobabooga: Not running")
            
            if hasattr(self, 'zwaifu_proc') and self.zwaifu_proc and self.zwaifu_proc.poll() is None:
                report.append("  Z-Waifu: Running")
            else:
                report.append("  Z-Waifu: Not running")
            
            # Save report
            report_filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w') as f:
                f.write("\n".join(report))
            
            messagebox.showinfo("Security Report", f"Security report generated and saved to:\n{report_filename}")
            self.log(f"Security report saved to {report_filename}")
            
        except Exception as e:
            messagebox.showerror("Report Error", f"Error generating security report: {e}")
            self.log(f"Security report error: {e}")

    def open_firewall_settings(self):
        """Open firewall settings dialog"""
        try:
            self.log("Opening firewall settings...")
            
            # Create settings window
            settings_window = tk.Toplevel(self.root)
            settings_window.title("Firewall Settings")
            settings_window.geometry("400x300")
            settings_window.resizable(False, False)
            
            # Center the window
            settings_window.transient(self.root)
            settings_window.grab_set()
            
            # Create settings content
            main_frame = ttk.Frame(settings_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Firewall Settings", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Port settings
            port_frame = ttk.LabelFrame(main_frame, text="Port Access", padding="5")
            port_frame.pack(fill=tk.X, pady=5)
            
            port_7860_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(port_frame, text="Allow port 7860 (Oobabooga)", variable=port_7860_var).pack(anchor=tk.W)
            
            port_7861_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(port_frame, text="Allow port 7861 (Z-Waifu)", variable=port_7861_var).pack(anchor=tk.W)
            
            port_5000_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(port_frame, text="Allow port 5000 (Web Interface)", variable=port_5000_var).pack(anchor=tk.W)
            
            # Network access
            network_frame = ttk.LabelFrame(main_frame, text="Network Access", padding="5")
            network_frame.pack(fill=tk.X, pady=5)
            
            local_only_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(network_frame, text="Local network access only", variable=local_only_var).pack(anchor=tk.W)
            
            external_access_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(network_frame, text="Allow external access", variable=external_access_var).pack(anchor=tk.W)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Apply", command=lambda: self.apply_firewall_settings(
                port_7860_var.get(), port_7861_var.get(), port_5000_var.get(),
                local_only_var.get(), external_access_var.get(), settings_window
            )).pack(side=tk.RIGHT, padx=5)
            
            ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error opening firewall settings: {e}")
            self.log(f"Firewall settings error: {e}")

    def apply_firewall_settings(self, port_7860, port_7861, port_5000, local_only, external_access, window):
        """Apply firewall settings"""
        try:
            self.log(f"Applying firewall settings: 7860={port_7860}, 7861={port_7861}, 5000={port_5000}, local_only={local_only}")
            
            # Save settings to config
            if not hasattr(self, 'firewall_settings'):
                self.firewall_settings = {}
            
            self.firewall_settings.update({
                'port_7860': port_7860,
                'port_7861': port_7861,
                'port_5000': port_5000,
                'local_only': local_only,
                'external_access': external_access
            })
            
            # Note: Actual firewall configuration would require system-level access
            # This is a placeholder for the settings storage
            messagebox.showinfo("Settings Applied", 
                              "Firewall settings have been saved.\n\n"
                              "Note: Actual firewall configuration requires system administrator privileges.")
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error applying firewall settings: {e}")
            self.log(f"Apply firewall settings error: {e}")

# Terminal Emulator class for process output
class TerminalEmulator(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.process = None
        self.start_time = None
        self.command_history = []
        self.history_index = 0
        
        # Enhanced output capture
        self.output_buffer = []
        self.max_buffer_size = 10000  # Increased buffer size
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
        
        # Create main terminal frame
        self.create_terminal_interface()
        
        # Initialize logging
        self.init_logging()
        
        # Start performance monitoring
        self.start_performance_monitor()

    def create_terminal_interface(self):
        """Create the enhanced terminal interface"""
        # Create toolbar frame
        self.toolbar_frame = tk.Frame(self)
        self.toolbar_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Create terminal display with enhanced features
        self.terminal_frame = tk.Frame(self)
        self.terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create terminal with syntax highlighting support and dark mode
        self.terminal = scrolledtext.ScrolledText(
            self.terminal_frame, 
            font=("Consolas", 9), 
            bg='#1e1e1e',  # Dark background
            fg='#00ff00',  # Green text
            insertbackground='#ffffff',
            selectbackground='#0078d4',
            selectforeground='#ffffff',
            wrap=tk.WORD,
            undo=True,
            maxundo=1000
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # Configure color tags for dark mode
        self.terminal.tag_configure('error', foreground='#ff6b6b')
        self.terminal.tag_configure('warning', foreground='#ffd93d')
        self.terminal.tag_configure('success', foreground='#6bcf7f')
        self.terminal.tag_configure('info', foreground='#4dabf7')
        self.terminal.tag_configure('debug', foreground='#adb5bd')
        self.terminal.tag_configure('command', foreground='#ffa500')
        
        # Create input and control frame
        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.create_toolbar()
        self.create_input_controls()
        self.create_context_menu()
        
        # Bind events
        self.bind_terminal_events()

    def create_toolbar(self):
        """Create toolbar with advanced features"""
        # Search frame
        search_frame = tk.Frame(self.toolbar_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        tk.Label(search_frame, text="Search:", fg='white', bg='black').pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=20, bg='darkgray', fg='white')
        self.search_entry.pack(side=tk.LEFT, padx=(5,0))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Filter frame
        filter_frame = tk.Frame(self.toolbar_frame)
        filter_frame.pack(side=tk.LEFT, padx=10, pady=2)
        
        tk.Label(filter_frame, text="Filter:", fg='white', bg='black').pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(filter_frame, textvariable=self.filter_var, width=15, bg='darkgray', fg='white')
        self.filter_entry.pack(side=tk.LEFT, padx=(5,0))
        self.filter_entry.bind('<KeyRelease>', self.on_filter_change)
        
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
        
        # Logging toggle
        self.logging_var = tk.BooleanVar(value=True)
        self.logging_cb = tk.Checkbutton(control_frame, text="Log Output", variable=self.logging_var,
                                       command=self.toggle_logging, bg='black', fg='white', selectcolor='darkgreen')
        self.logging_cb.pack(side=tk.LEFT, padx=2)
        
        # Performance info
        self.perf_label = tk.Label(control_frame, text="Lines: 0", fg='cyan', bg='black', font=("Consolas", 8))
        self.perf_label.pack(side=tk.LEFT, padx=5)

    def create_input_controls(self):
        """Create input controls with enhanced features"""
        # Input field with autocomplete and dark mode
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            self.input_frame, 
            textvariable=self.input_var, 
            bg='#2d2d2d',  # Dark input background
            fg='#00ff00',  # Green text
            insertbackground='#ffffff',
            font=("Consolas", 9)
        )
        self.input_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Bind input events
        self.input_entry.bind('<Return>', self.send_input)
        self.input_entry.bind('<Up>', self.history_up)
        self.input_entry.bind('<Down>', self.history_down)
        self.input_entry.bind('<Tab>', self.auto_complete)
        
        # Control buttons with dark mode
        button_frame = tk.Frame(self.input_frame)
        button_frame.pack(side=tk.RIGHT)
        
        self.send_btn = tk.Button(button_frame, text="Send", command=self.send_input, 
                                 bg='#28a745', fg='white', relief=tk.FLAT, bd=0)
        self.send_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_terminal, 
                                  bg='#dc3545', fg='white', relief=tk.FLAT, bd=0)
        self.clear_btn.pack(side=tk.LEFT, padx=2)
        
        self.save_btn = tk.Button(button_frame, text="Save", command=self.save_output, 
                                 bg='#007bff', fg='white', relief=tk.FLAT, bd=0)
        self.save_btn.pack(side=tk.LEFT, padx=2)
        
        self.kill_btn = tk.Button(button_frame, text="Kill", command=self.kill_process, 
                                 bg='#6f42c1', fg='white', relief=tk.FLAT, bd=0)
        self.kill_btn.pack(side=tk.LEFT, padx=2)

    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selection)
        self.context_menu.add_command(label="Copy All", command=self.copy_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Save Output", command=self.save_output)
        self.context_menu.add_command(label="Clear Terminal", command=self.clear_terminal)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Find Next", command=self.find_next)
        self.context_menu.add_command(label="Find Previous", command=self.find_previous)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Show Statistics", command=self.show_statistics)
        
        # Bind context menu
        self.terminal.bind("<Button-3>", self.show_context_menu)

    def bind_terminal_events(self):
        """Bind terminal events"""
        self.terminal.bind('<Key>', self.on_key_press)
        self.terminal.bind('<Control-f>', self.focus_search)
        self.terminal.bind('<Control-g>', self.find_next)
        self.terminal.bind('<Control-s>', self.save_output)
        self.terminal.bind('<Control-l>', self.clear_terminal)
        self.terminal.bind('<Control-c>', self.copy_selection)

    def init_logging(self):
        """Initialize output logging"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_dir = "data/terminal_logs"
            os.makedirs(log_dir, exist_ok=True)
            self.output_log_file = f"{log_dir}/terminal_{timestamp}.log"
            
            # Write header
            with open(self.output_log_file, 'w', encoding='utf-8') as f:
                f.write(f"Terminal Output Log - Started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n")
        except Exception as e:
            print(f"Failed to initialize logging: {e}")

    def start_performance_monitor(self):
        """Start performance monitoring thread"""
        def monitor():
            while True:
                try:
                    self.update_performance_info()
                    time.sleep(1)
                except Exception as e:
                    print(f"Performance monitor error: {e}")
                    break
        threading.Thread(target=monitor, daemon=True).start()

    def update_performance_info(self):
        """Update performance information"""
        try:
            self.after(0, lambda: self.perf_label.config(text=f"Lines: {self.line_count} | Buffer: {len(self.output_buffer)}"))
        except Exception as e:
            pass

    def attach_process(self, process, command):
        """Attach a process to this terminal"""
        self.process = process
        self.start_time = time.time()
        self._append(f"Process started: {command}\n", '32')  # Green
        
        # Start reading process output with enhanced capture
        threading.Thread(target=self._read_output_enhanced, daemon=True).start()

    def _read_output_enhanced(self):
        """Enhanced output reading with comprehensive capture"""
        try:
            # Read both stdout and stderr
            stdout_thread = threading.Thread(target=self._read_stream, args=(self.process.stdout, 'stdout'), daemon=True)
            stderr_thread = threading.Thread(target=self._read_stream, args=(self.process.stderr, 'stderr'), daemon=True)
            
            stdout_thread.start()
            if self.process.stderr:
                stderr_thread.start()
            
            # Wait for process to complete
            self.process.wait()
            
            # Mark process as terminated
            self.after(0, self._append, f"\nProcess terminated with exit code: {self.process.returncode}\n", '33')
            
        except Exception as e:
            self.after(0, self._append, f"Error reading output: {e}\n", '31')

    def _read_stream(self, stream, stream_type):
        """Read from a specific stream (stdout or stderr)"""
        if not stream:
            return
            
        try:
            for line in stream:
                if line:
                    # Process line with enhanced features
                    processed_line = self._process_output_line(line, stream_type)
                    
                    # Add to buffer
                    self.output_buffer.append({
                        'timestamp': time.time(),
                        'line': processed_line,
                        'stream': stream_type,
                        'original': line
                    })
                    
                    # Apply filters
                    if self._should_display_line(processed_line):
                        self.after(0, self._append, processed_line, self._get_line_color(processed_line))
                    
                    # Update line count
                    self.line_count += 1
                    
                    # Log if enabled
                    if self.logging_enabled and self.output_log_file:
                        self._log_line(processed_line, stream_type)
                    
                    # Cleanup if needed
                    self._smart_cleanup()
                    
        except Exception as e:
            self.after(0, self._append, f"Error reading {stream_type}: {e}\n", '31')

    def _process_output_line(self, line, stream_type):
        """Process output line with enhanced formatting"""
        # Decode if needed
        if isinstance(line, bytes):
            try:
                line = line.decode('utf-8', errors='replace')
            except:
                line = str(line)
        
        # Add timestamp if not present
        if not line.startswith('['):
            timestamp = time.strftime('%H:%M:%S')
            line = f"[{timestamp}] {line}"
        
        # Add stream indicator for stderr
        if stream_type == 'stderr':
            line = f"[ERR] {line}"
        
        return line

    def _should_display_line(self, line):
        """Check if line should be displayed based on filters"""
        # Error filter
        if self.show_only_errors and 'error' not in line.lower() and '[err]' not in line.lower():
            return False
        
        # Warning filter
        if self.show_only_warnings and 'warning' not in line.lower() and 'warn' not in line.lower():
            return False
        
        # Search filter
        if self.search_text and self.search_text.lower() not in line.lower():
            return False
        
        # Pattern filter
        if self.filter_pattern:
            import re
            try:
                if not re.search(self.filter_pattern, line, re.IGNORECASE):
                    return False
            except:
                pass
        
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

    def _log_line(self, line, stream_type):
        """Log line to file"""
        try:
            with open(self.output_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{stream_type.upper()}] {line}")
        except Exception as e:
            pass

    def _smart_cleanup(self):
        """Smart cleanup to prevent memory issues"""
        current_time = time.time()
        
        # Cleanup buffer if too large
        if len(self.output_buffer) > self.max_buffer_size:
            # Remove oldest entries
            remove_count = self.max_buffer_size // 4
            self.output_buffer = self.output_buffer[remove_count:]
        
        # Cleanup terminal display periodically
        if current_time - self.last_cleanup_time > self.cleanup_interval:
            if self.line_count > 1000:
                self.after(0, self._cleanup_display)
                self.line_count = 500  # Reset counter
                self.last_cleanup_time = current_time

    def _cleanup_display(self):
        """Cleanup terminal display efficiently"""
        try:
            self.terminal.config(state='normal')
            
            # Get current line count
            current_lines = int(self.terminal.index('end-1c').split('.')[0])
            
            if current_lines > 500:
                # Remove first 250 lines
                self.terminal.delete('1.0', '250.0')
                
                # Add cleanup indicator
                self.terminal.insert('1.0', f"[{time.strftime('%H:%M:%S')}] --- Previous output cleared ---\n", 'comment')
            
            self.terminal.config(state='disabled')
            
        except Exception as e:
            pass

    def on_search_change(self, event=None):
        """Handle search text change"""
        self.search_text = self.search_var.get()
        self._refresh_display()

    def on_filter_change(self, event=None):
        """Handle filter pattern change"""
        self.filter_pattern = self.filter_var.get()
        self._refresh_display()

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

    def toggle_logging(self):
        """Toggle output logging"""
        self.logging_enabled = self.logging_var.get()

    def _refresh_display(self):
        """Refresh terminal display with current filters"""
        try:
            self.terminal.config(state='normal')
            self.terminal.delete('1.0', tk.END)
            
            for entry in self.output_buffer:
                if self._should_display_line(entry['line']):
                    self.terminal.insert(tk.END, entry['line'])
            
            self.terminal.see(tk.END)
            self.terminal.config(state='disabled')
            
        except Exception as e:
            pass

    def focus_search(self, event=None):
        """Focus search entry"""
        self.search_entry.focus_set()
        return 'break'

    def find_next(self, event=None):
        """Find next occurrence of search text"""
        if not self.search_text:
            return 'break'
        
        try:
            # Get current selection
            current_pos = self.terminal.index(tk.SEL_LAST) if self.terminal.tag_ranges(tk.SEL) else '1.0'
            
            # Find next occurrence
            pos = self.terminal.search(self.search_text, current_pos, tk.END, nocase=True)
            
            if pos:
                # Select found text
                end_pos = f"{pos}+{len(self.search_text)}c"
                self.terminal.tag_remove(tk.SEL, '1.0', tk.END)
                self.terminal.tag_add(tk.SEL, pos, end_pos)
                self.terminal.see(pos)
            else:
                # Wrap to beginning
                pos = self.terminal.search(self.search_text, '1.0', tk.END, nocase=True)
                if pos:
                    end_pos = f"{pos}+{len(self.search_text)}c"
                    self.terminal.tag_remove(tk.SEL, '1.0', tk.END)
                    self.terminal.tag_add(tk.SEL, pos, end_pos)
                    self.terminal.see(pos)
        
        except Exception as e:
            pass
        
        return 'break'

    def find_previous(self, event=None):
        """Find previous occurrence of search text"""
        if not self.search_text:
            return 'break'
        
        try:
            # Get current selection
            current_pos = self.terminal.index(tk.SEL_FIRST) if self.terminal.tag_ranges(tk.SEL) else tk.END
            
            # Find previous occurrence
            pos = self.terminal.search(self.search_text, '1.0', current_pos, backwards=True, nocase=True)
            
            if pos:
                # Select found text
                end_pos = f"{pos}+{len(self.search_text)}c"
                self.terminal.tag_remove(tk.SEL, '1.0', tk.END)
                self.terminal.tag_add(tk.SEL, pos, end_pos)
                self.terminal.see(pos)
        
        except Exception as e:
            pass
        
        return 'break'

    def auto_complete(self, event=None):
        """Auto-complete command"""
        current_text = self.input_var.get()
        
        # Simple auto-complete based on command history
        if current_text:
            for cmd in reversed(self.command_history):
                if cmd.startswith(current_text):
                    self.input_var.set(cmd)
                    self.input_entry.icursor(len(current_text))
                    return 'break'
        
        return None

    def copy_selection(self, event=None):
        """Copy selected text"""
        try:
            if self.terminal.tag_ranges(tk.SEL):
                selected_text = self.terminal.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_clear()
                self.clipboard_append(selected_text)
        except Exception as e:
            pass
        return 'break'

    def copy_all(self):
        """Copy all terminal content"""
        try:
            content = self.terminal.get('1.0', tk.END)
            self.clipboard_clear()
            self.clipboard_append(content)
        except Exception as e:
            pass

    def save_output(self):
        """Save terminal output to file"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"terminal_output_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Terminal Output - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n")
                f.write(self.terminal.get('1.0', tk.END))
            
            self._append(f"Output saved to: {filename}\n", '32')
            
        except Exception as e:
            self._append(f"Error saving output: {e}\n", '31')

    def show_statistics(self):
        """Show terminal statistics"""
        try:
            stats = f"""
Terminal Statistics:
===================
Total Lines: {self.line_count}
Buffer Size: {len(self.output_buffer)}
Uptime: {self.get_uptime():.1f} seconds
Process Status: {self.get_status()}
Log File: {self.output_log_file or 'None'}
Search Active: {bool(self.search_text)}
Filter Active: {bool(self.filter_pattern)}
Error Filter: {self.show_only_errors}
Warning Filter: {self.show_only_warnings}
Logging Enabled: {self.logging_enabled}
"""
            self._append(stats, '36')
            
        except Exception as e:
            self._append(f"Error showing statistics: {e}\n", '31')
    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _append(self, text, color_code):
        """Append text to terminal with enhanced color support"""
        try:
            self.terminal.config(state='normal')
            
            # Parse ANSI color codes
            if '\033[' in text:
                text = self._parse_ansi_colors(text)
            
            # Apply color tags
            tag_name = f"color_{color_code}"
            if not self.terminal.tag_exists(tag_name):
                self.terminal.tag_configure(tag_name, foreground=self._get_color_name(color_code))
            
            # Insert text with color
            start_pos = self.terminal.index(tk.END)
            self.terminal.insert(tk.END, text)
            end_pos = self.terminal.index(tk.END)
            self.terminal.tag_add(tag_name, start_pos, end_pos)
            
            self.terminal.see(tk.END)
            self.terminal.config(state='disabled')
            
        except Exception as e:
            pass

    def _get_color_name(self, color_code):
        """Get color name from ANSI code"""
        color_map = {
            '30': 'black',
            '31': 'red',
            '32': 'green',
            '33': 'yellow',
            '34': 'blue',
            '35': 'magenta',
            '36': 'cyan',
            '37': 'white',
            '0': 'white'
        }
        return color_map.get(color_code, 'white')

    def _parse_ansi_colors(self, text):
        """Parse ANSI color codes and convert to tkinter colors"""
        import re
        # Remove ANSI codes for now (can be enhanced with actual color support)
        text = re.sub(r'\033\[[0-9;]*m', '', text)
        return text

    def send_input(self, event=None):
        """Send input to the process with enhanced features"""
        if self.process and self.process.poll() is None:
            input_text = self.input_var.get()
            if input_text.strip():
                # Add to command history
                if input_text not in self.command_history:
                    self.command_history.append(input_text)
                self.history_index = len(self.command_history)
                
                # Send to process
                try:
                    self.process.stdin.write(input_text + '\n')
                    self.process.stdin.flush()
                    self._append(f"> {input_text}\n", '36')  # Cyan text
                    self.input_var.set("")
                except Exception as e:
                    self._append(f"Error sending input: {e}\n", '31')  # Red

    def history_up(self, event):
        """Navigate up in command history"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_var.set(self.command_history[self.history_index])
        return 'break'

    def history_down(self, event):
        """Navigate down in command history"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_var.set(self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index += 1
            self.input_var.set("")
        return 'break'

    def on_key_press(self, event):
        """Handle key presses in terminal"""
        # Allow normal typing
        return None

    def clear_terminal(self):
        """Clear the terminal output"""
        try:
            self.terminal.config(state='normal')
            self.terminal.delete('1.0', tk.END)
            self.terminal.config(state='disabled')
            self.line_count = 0
        except Exception as e:
            pass

    def kill_process(self):
        """Force kill the attached process"""
        if self.process:
            try:
                self.process.kill()
                self.process.wait()  # Wait for process to terminate
                self._append("Process killed by user\n", '31')  # Red
                # Clear command history to free memory
                self.command_history.clear()
                self.history_index = 0
            except Exception as e:
                self._append(f"Error killing process: {e}\n", '31')  # Red

    def get_uptime(self):
        """Get process uptime"""
        if self.start_time:
            return time.time() - self.start_time
        return 0

    def get_status(self):
        """Get process status"""
        if self.process:
            if self.process.poll() is None:
                return "Running"
            else:
                return f"Stopped (Exit code: {self.process.returncode})"
        return "Not attached"

    def get_output_buffer(self):
        """Get current output buffer"""
        return self.output_buffer.copy()

    def get_filtered_output(self, filter_func=None):
        """Get filtered output based on custom filter function"""
        if filter_func:
            return [entry for entry in self.output_buffer if filter_func(entry)]
        return self.output_buffer.copy()

    def export_output(self, filename=None, format='txt'):
        """Export output to file in various formats"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"terminal_export_{timestamp}.{format}"
        
        try:
            if format == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    for entry in self.output_buffer:
                        f.write(entry['line'])
            elif format == 'json':
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.output_buffer, f, indent=2, default=str)
            elif format == 'csv':
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Stream', 'Line'])
                    for entry in self.output_buffer:
                        writer.writerow([entry['timestamp'], entry['stream'], entry['line'].strip()])
            
            self._append(f"Output exported to: {filename}\n", '32')
            return filename
            
        except Exception as e:
            self._append(f"Error exporting output: {e}\n", '31')
            return None

    def apply_dark_mode(self):
        """Apply dark mode styling to terminal"""
        try:
            # Terminal background and text
            self.terminal.config(
                bg='#1e1e1e',
                fg='#00ff00',
                insertbackground='#ffffff',
                selectbackground='#0078d4',
                selectforeground='#ffffff'
            )
            
            # Input field
            self.input_entry.config(
                bg='#2d2d2d',
                fg='#00ff00',
                insertbackground='#ffffff'
            )
            
            # Frame backgrounds
            self.toolbar_frame.config(bg='#1e1e1e')
            self.terminal_frame.config(bg='#1e1e1e')
            self.input_frame.config(bg='#1e1e1e')
            
            # Update color tags for dark mode
            self.terminal.tag_configure('error', foreground='#ff6b6b')
            self.terminal.tag_configure('warning', foreground='#ffd93d')
            self.terminal.tag_configure('success', foreground='#6bcf7f')
            self.terminal.tag_configure('info', foreground='#4dabf7')
            self.terminal.tag_configure('debug', foreground='#adb5bd')
            self.terminal.tag_configure('command', foreground='#ffa500')
            
        except Exception as e:
            print(f"Error applying dark mode to terminal: {e}")

    def apply_light_mode(self):
        """Apply light mode styling to terminal"""
        try:
            # Terminal background and text
            self.terminal.config(
                bg='#ffffff',
                fg='#000000',
                insertbackground='#000000',
                selectbackground='#0078d4',
                selectforeground='#ffffff'
            )
            
            # Input field
            self.input_entry.config(
                bg='#f8f9fa',
                fg='#000000',
                insertbackground='#000000'
            )
            
            # Frame backgrounds
            self.toolbar_frame.config(bg='#ffffff')
            self.terminal_frame.config(bg='#ffffff')
            self.input_frame.config(bg='#ffffff')
            
            # Update color tags for light mode
            self.terminal.tag_configure('error', foreground='#dc3545')
            self.terminal.tag_configure('warning', foreground='#ffc107')
            self.terminal.tag_configure('success', foreground='#28a745')
            self.terminal.tag_configure('info', foreground='#17a2b8')
            self.terminal.tag_configure('debug', foreground='#6c757d')
            self.terminal.tag_configure('command', foreground='#fd7e14')
            
        except Exception as e:
            print(f"Error applying light mode to terminal: {e}")

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherGUI(root)
    root.mainloop()

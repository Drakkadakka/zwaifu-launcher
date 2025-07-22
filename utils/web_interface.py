"""
Web Interface Module
Provides web-based dashboard for launcher management
"""

import threading
import time
import os
from typing import Dict, Any, Optional
import webbrowser

# Advanced Features Imports
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class WebInterface:
    """Web-based dashboard for launcher management"""
    
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.app = None
        self.socketio = None
        self.server_thread = None
        self.is_running = False
        self.port = 8080
        self.api_key = None
        self.load_api_key()

    def load_api_key(self):
        """Load API key from api_key.json file"""
        try:
            api_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api_key.json')
            if os.path.exists(api_key_path):
                import json
                with open(api_key_path, 'r') as f:
                    api_key_data = json.load(f)
                    self.api_key = api_key_data.get('api_key')
                    if self.api_key:
                        self.launcher_gui.log(f"Web interface loaded API key from {api_key_path}")
            return self.api_key
        except Exception as e:
            self.launcher_gui.log(f"Failed to load API key for web interface: {e}")
            return None

    def make_authenticated_api_call(self, url, method='GET', data=None):
        """Make an authenticated API call using the loaded API key"""
        try:
            import requests
            
            if not self.api_key:
                self.api_key = self.load_api_key()
                if not self.api_key:
                    self.launcher_gui.log("No API key available for authenticated API call")
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
                self.launcher_gui.log(f"Authenticated API call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.launcher_gui.log(f"Authenticated API call error: {e}")
            return None

    def start(self):
        """Start the web interface server"""
        if not FLASK_AVAILABLE:
            self.launcher_gui.log("Flask not available. Install with: pip install flask flask-socketio flask-cors")
            return False

        try:
            self.app = Flask(__name__)
            self.app.config['SECRET_KEY'] = 'zwaifu_launcher_secret_key'
            
            # Enable CORS
            CORS(self.app)
            
            # Initialize SocketIO
            self.socketio = SocketIO(self.app, cors_allowed_origins="*")
            
            # Setup routes
            self._setup_routes()
            
            # Start server in background thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            self.launcher_gui.log(f"Web interface started on http://localhost:{self.port}")
            return True
            
        except Exception as e:
            self.launcher_gui.log(f"Error starting web interface: {e}")
            return False

    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return self.render_dashboard()
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify(self.get_status())

        @self.app.route('/api/start/<process_type>', methods=['POST'])
        def api_start_process(process_type):
            success = self.start_process_instance(process_type)
            return jsonify({'success': success})

        @self.app.route('/api/stop_all/<process_type>', methods=['POST'])
        def api_stop_all_instances(process_type):
            success = self.stop_all_instances(process_type)
            return jsonify({'success': success})

        @self.app.route('/api/stop/<process_type>/<instance_id>', methods=['POST'])
        def api_stop_instance(process_type, instance_id):
            success = self.stop_instance(process_type, instance_id)
            return jsonify({'success': success})

        @self.app.route('/api/restart/<process_type>/<instance_id>', methods=['POST'])
        def api_restart_instance(process_type, instance_id):
            success = self.restart_instance(process_type, instance_id)
            return jsonify({'success': success})

        @self.app.route('/api/kill/<process_type>/<instance_id>', methods=['POST'])
        def api_kill_instance(process_type, instance_id):
            success = self.kill_instance(process_type, instance_id)
            return jsonify({'success': success})

        @self.app.route('/api/focus/<process_type>/<instance_id>', methods=['POST'])
        def api_focus_instance(process_type, instance_id):
            success = self.focus_instance(process_type, instance_id)
            return jsonify({'success': success})

        @self.socketio.on('connect')
        def handle_connect():
            emit('status_update', self.get_status())

        @self.socketio.on('start_process')
        def handle_start_process(data):
            process_type = data.get('process_type')
            if process_type:
                success = self.start_process_instance(process_type)
                emit('process_started', {'process_type': process_type, 'success': success})
                emit('status_update', self.get_status())

    def _run_server(self):
        """Run the Flask server"""
        try:
            self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=False)
        except Exception as e:
            self.launcher_gui.log(f"Web server error: {e}")

    def render_dashboard(self):
        """Render the main dashboard HTML"""
        status = self.get_status()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Z-Waifu Launcher Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .status-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .status-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }}
        
        .status-card h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-running {{
            background-color: #28a745;
            box-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
        }}
        
        .status-stopped {{
            background-color: #dc3545;
        }}
        
        .status-starting {{
            background-color: #ffc107;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        
        .button-group {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-success {{
            background: #28a745;
            color: white;
        }}
        
        .btn-success:hover {{
            background: #218838;
            transform: translateY(-2px);
        }}
        
        .btn-danger {{
            background: #dc3545;
            color: white;
        }}
        
        .btn-danger:hover {{
            background: #c82333;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #5a6268;
            transform: translateY(-2px);
        }}
        
        .instances-list {{
            margin-top: 15px;
        }}
        
        .instance-item {{
            background: #f8f9fa;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 8px;
            border-left: 3px solid #667eea;
        }}
        
        .instance-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }}
        
        .instance-id {{
            font-weight: bold;
            color: #333;
        }}
        
        .instance-status {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .instance-actions {{
            display: flex;
            gap: 5px;
        }}
        
        .btn-sm {{
            padding: 5px 10px;
            font-size: 0.8em;
        }}
        
        .no-instances {{
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 20px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #dee2e6;
        }}
        
        .refresh-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }}
        
        .refresh-btn:hover {{
            transform: rotate(180deg);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }}
        
        @media (max-width: 768px) {{
            .status-grid {{
                grid-template-columns: 1fr;
            }}
            
            .button-group {{
                flex-direction: column;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <button class="refresh-btn" onclick="location.reload()" title="Refresh">🔄</button>
    
    <div class="container">
        <div class="header">
            <h1>🎮 Z-Waifu Launcher</h1>
            <p>Advanced AI Tools Management Dashboard</p>
        </div>
        
        <div class="content">
            <div class="status-grid">
                <!-- Oobabooga Status -->
                <div class="status-card">
                    <h3>🤖 Oobabooga</h3>
                    <div class="status-info">
                        <span class="status-indicator {'status-running' if status['oobabooga']['running'] else 'status-stopped'}"></span>
                        <span>{'Running' if status['oobabooga']['running'] else 'Stopped'}</span>
                    </div>
                    <div class="instances-list">
                        {self._render_instances('oobabooga', status['oobabooga']['instances'])}
                    </div>
                    <div class="button-group">
                        <button class="btn btn-success" onclick="startProcess('oobabooga')">Start Instance</button>
                        <button class="btn btn-danger" onclick="stopAllInstances('oobabooga')">Stop All</button>
                    </div>
                </div>
                
                <!-- Z-Waifu Status -->
                <div class="status-card">
                    <h3>💬 Z-Waifu</h3>
                    <div class="status-info">
                        <span class="status-indicator {'status-running' if status['zwaifu']['running'] else 'status-stopped'}"></span>
                        <span>{'Running' if status['zwaifu']['running'] else 'Stopped'}</span>
                    </div>
                    <div class="instances-list">
                        {self._render_instances('zwaifu', status['zwaifu']['instances'])}
                    </div>
                    <div class="button-group">
                        <button class="btn btn-success" onclick="startProcess('zwaifu')">Start Instance</button>
                        <button class="btn btn-danger" onclick="stopAllInstances('zwaifu')">Stop All</button>
                    </div>
                </div>
                
                <!-- Ollama Status -->
                <div class="status-card">
                    <h3>🦙 Ollama</h3>
                    <div class="status-info">
                        <span class="status-indicator {'status-running' if status['ollama']['running'] else 'status-stopped'}"></span>
                        <span>{'Running' if status['ollama']['running'] else 'Stopped'}</span>
                    </div>
                    <div class="instances-list">
                        {self._render_instances('ollama', status['ollama']['instances'])}
                    </div>
                    <div class="button-group">
                        <button class="btn btn-success" onclick="startProcess('ollama')">Start Instance</button>
                        <button class="btn btn-danger" onclick="stopAllInstances('ollama')">Stop All</button>
                    </div>
                </div>
                
                <!-- RVC Status -->
                <div class="status-card">
                    <h3>🎵 RVC</h3>
                    <div class="status-info">
                        <span class="status-indicator {'status-running' if status['rvc']['running'] else 'status-stopped'}"></span>
                        <span>{'Running' if status['rvc']['running'] else 'Stopped'}</span>
                    </div>
                    <div class="instances-list">
                        {self._render_instances('rvc', status['rvc']['instances'])}
                    </div>
                    <div class="button-group">
                        <button class="btn btn-success" onclick="startProcess('rvc')">Start Instance</button>
                        <button class="btn btn-danger" onclick="stopAllInstances('rvc')">Stop All</button>
                    </div>
                </div>
            </div>
            
            <div class="button-group" style="justify-content: center; margin-top: 30px;">
                <a href="/api/status" class="btn btn-secondary" target="_blank">API Status</a>
                <button class="btn btn-primary" onclick="refreshStatus()">Refresh Status</button>
            </div>
        </div>
        
        <div class="footer">
            <p>Z-Waifu Launcher Web Dashboard | Real-time monitoring and control</p>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();
        
        socket.on('connect', function() {{
            console.log('Connected to server');
        }});
        
        socket.on('status_update', function(data) {{
            console.log('Status update received:', data);
            // Could implement real-time updates here
        }});
        
        socket.on('process_started', function(data) {{
            console.log('Process started:', data);
            if (data.success) {{
                setTimeout(() => location.reload(), 1000);
            }}
        }});
        
        function startProcess(processType) {{
            socket.emit('start_process', {{process_type: processType}});
        }}
        
        function stopAllInstances(processType) {{
            // Disable button to prevent multiple clicks
            const button = event.target;
            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = 'Stopping...';
            
            fetch(`/api/stop_all/${{processType}}`, {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        button.textContent = 'Stopped!';
                        setTimeout(() => location.reload(), 1000);
                    }} else {{
                        button.textContent = 'Failed!';
                        setTimeout(() => {{
                            button.disabled = false;
                            button.textContent = originalText;
                        }}, 2000);
                    }}
                }})
                .catch(error => {{
                    console.error('Error stopping instances:', error);
                    button.textContent = 'Error!';
                    setTimeout(() => {{
                        button.disabled = false;
                        button.textContent = originalText;
                    }}, 2000);
                }});
        }}
        
        function stopInstance(processType, instanceId) {{
            fetch(`/api/stop/${{processType}}/${{instanceId}}`, {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        setTimeout(() => location.reload(), 1000);
                    }}
                }});
        }}
        
        function restartInstance(processType, instanceId) {{
            fetch(`/api/restart/${{processType}}/${{instanceId}}`, {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        setTimeout(() => location.reload(), 1000);
                    }}
                }});
        }}
        
        function killInstance(processType, instanceId) {{
            fetch(`/api/kill/${{processType}}/${{instanceId}}`, {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        setTimeout(() => location.reload(), 1000);
                    }}
                }});
        }}
        
        function focusInstance(processType, instanceId) {{
            fetch(`/api/focus/${{processType}}/${{instanceId}}`, {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        console.log('Instance focused');
                    }}
                }});
        }}
        
        function refreshStatus() {{
            location.reload();
        }}
        
        // Auto-refresh every 30 seconds
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
        """
        
        return html

    def _render_instances(self, process_type: str, instances: list) -> str:
        """Render instances list HTML"""
        if not instances:
            return '<div class="no-instances">No instances running</div>'
        
        html = ""
        for instance in instances:
            status_class = "status-running" if instance.get('running', False) else "status-stopped"
            status_text = "Running" if instance.get('running', False) else "Stopped"
            
            html += f"""
            <div class="instance-item">
                <div class="instance-header">
                    <span class="instance-id">Instance {instance.get('id', 'Unknown')}</span>
                    <span class="instance-status">
                        <span class="status-indicator {status_class}"></span>
                        {status_text}
                    </span>
                </div>
                <div class="instance-actions">
                    <button class="btn btn-sm btn-success" onclick="startProcess('{process_type}')">Start</button>
                    <button class="btn btn-sm btn-danger" onclick="stopInstance('{process_type}', '{instance.get('id', '')}')">Stop</button>
                    <button class="btn btn-sm btn-secondary" onclick="restartInstance('{process_type}', '{instance.get('id', '')}')">Restart</button>
                    <button class="btn btn-sm btn-secondary" onclick="killInstance('{process_type}', '{instance.get('id', '')}')">Kill</button>
                    <button class="btn btn-sm btn-primary" onclick="focusInstance('{process_type}', '{instance.get('id', '')}')">Focus</button>
                </div>
            </div>
            """
        
        return html

    def get_status(self) -> Dict[str, Any]:
        """Get current status of all processes"""
        try:
            # Get process status from launcher GUI
            if not hasattr(self.launcher_gui, 'process_instance_tabs'):
                self.launcher_gui.log("process_instance_tabs missing in launcher_gui! Initializing with all process types.")
                self.launcher_gui.process_instance_tabs = {
                    'Oobabooga': [],
                    'Z-Waifu': [],
                    'Ollama': [],
                    'RVC': []
                }
            process_tabs = self.launcher_gui.process_instance_tabs
            
            status = {
                'oobabooga': {
                    'running': False,
                    'instances': []
                },
                'zwaifu': {
                    'running': False,
                    'instances': []
                },
                'ollama': {
                    'running': False,
                    'instances': []
                },
                'rvc': {
                    'running': False,
                    'instances': []
                }
            }
            
            # Check each process type
            for process_type in ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']:
                if process_type in process_tabs:
                    instances = process_tabs[process_type]
                    status_key = process_type.lower()
                    status[status_key]['instances'] = []
                    
                    for i, instance_data in enumerate(instances):
                        # Check if process is running
                        running = False
                        if 'proc' in instance_data and instance_data['proc']:
                            try:
                                running = instance_data['proc'].poll() is None
                            except:
                                running = False
                        
                        instance_info = {
                            'id': i + 1,
                            'running': running,
                            'pid': instance_data.get('proc', {}).pid if hasattr(instance_data.get('proc', {}), 'pid') else None,
                            'start_time': instance_data.get('start_time'),
                            'uptime': instance_data.get('uptime', 0)
                        }
                        status[status_key]['instances'].append(instance_info)
                        
                        if instance_info['running']:
                            status[status_key]['running'] = True
            
            return status
            
        except Exception as e:
            self.launcher_gui.log(f"Error getting web interface status: {e}")
            return {
                'oobabooga': {'running': False, 'instances': []},
                'zwaifu': {'running': False, 'instances': []},
                'ollama': {'running': False, 'instances': []},
                'rvc': {'running': False, 'instances': []}
            }

    def start_process_instance(self, process_type: str) -> bool:
        """Start a new process instance"""
        try:
            if hasattr(self.launcher_gui, 'start_process_instance'):
                return self.launcher_gui.start_process_instance(process_type)
            else:
                self.launcher_gui.log(f"Launcher GUI does not support starting {process_type} instances")
                return False
        except Exception as e:
            self.launcher_gui.log(f"Error starting {process_type} instance: {e}")
            return False

    def stop_all_instances(self, process_type: str) -> bool:
        """Stop all instances of a process type"""
        try:
            if hasattr(self.launcher_gui, 'stop_all_instances'):
                stopped_count = self.launcher_gui.stop_all_instances(process_type)
                if stopped_count > 0:
                    self.launcher_gui.log(f"Successfully stopped {stopped_count} {process_type} instances")
                    return True
                else:
                    self.launcher_gui.log(f"No {process_type} instances were running to stop")
                    return True  # Still return True as this is not an error
            else:
                self.launcher_gui.log(f"Launcher GUI does not support stopping all {process_type} instances")
                return False
        except Exception as e:
            self.launcher_gui.log(f"Error stopping all {process_type} instances: {e}")
            return False

    def stop_instance(self, process_type: str, instance_id: str) -> bool:
        """Stop a specific instance"""
        try:
            if hasattr(self.launcher_gui, 'stop_instance'):
                # Convert process type to proper format
                process_name = process_type.title()
                if process_name == "Zwaifu":
                    process_name = "Z-Waifu"
                
                # Convert instance_id to integer
                try:
                    instance_id_int = int(instance_id) - 1  # Convert to 0-based index
                except ValueError:
                    self.launcher_gui.log(f"Invalid instance ID: {instance_id}")
                    return False
                
                self.launcher_gui.stop_instance(process_name, instance_id_int)
                return True
            else:
                self.launcher_gui.log(f"Launcher GUI does not support stopping {process_type} instances")
                return False
        except Exception as e:
            self.launcher_gui.log(f"Error stopping {process_type} instance {instance_id}: {e}")
            return False

    def restart_instance(self, process_type: str, instance_id: str) -> bool:
        """Restart a specific instance"""
        try:
            if hasattr(self.launcher_gui, 'restart_instance'):
                # Convert process type to proper format
                process_name = process_type.title()
                if process_name == "Zwaifu":
                    process_name = "Z-Waifu"
                
                # Convert instance_id to integer
                try:
                    instance_id_int = int(instance_id) - 1  # Convert to 0-based index
                except ValueError:
                    self.launcher_gui.log(f"Invalid instance ID: {instance_id}")
                    return False
                
                self.launcher_gui.restart_instance(process_name, instance_id_int)
                return True
            else:
                self.launcher_gui.log(f"Launcher GUI does not support restarting {process_type} instances")
                return False
        except Exception as e:
            self.launcher_gui.log(f"Error restarting {process_type} instance {instance_id}: {e}")
            return False

    def kill_instance(self, process_type: str, instance_id: str) -> bool:
        """Kill a specific instance"""
        try:
            if hasattr(self.launcher_gui, 'kill_instance'):
                # Convert process type to proper format
                process_name = process_type.title()
                if process_name == "Zwaifu":
                    process_name = "Z-Waifu"
                
                # Convert instance_id to integer
                try:
                    instance_id_int = int(instance_id) - 1  # Convert to 0-based index
                except ValueError:
                    self.launcher_gui.log(f"Invalid instance ID: {instance_id}")
                    return False
                
                self.launcher_gui.kill_instance(process_name, instance_id_int)
                return True
            else:
                self.launcher_gui.log(f"Launcher GUI does not support killing {process_type} instances")
                return False
        except Exception as e:
            self.launcher_gui.log(f"Error killing {process_type} instance {instance_id}: {e}")
            return False

    def focus_instance(self, process_type: str, instance_id: str) -> bool:
        """Focus a specific instance"""
        try:
            if hasattr(self.launcher_gui, 'focus_instance'):
                # Convert process type to proper format
                process_name = process_type.title()
                if process_name == "Zwaifu":
                    process_name = "Z-Waifu"
                
                # Convert instance_id to proper format
                instance_id_str = f"Instance {instance_id}"
                
                self.launcher_gui.focus_instance(process_name, instance_id_str)
                return True
            else:
                self.launcher_gui.log(f"Launcher GUI does not support focusing {process_type} instances")
                return False
        except Exception as e:
            self.launcher_gui.log(f"Error focusing {process_type} instance {instance_id}: {e}")
            return False

    def stop(self):
        """Stop the web interface server"""
        try:
            if self.socketio:
                self.socketio.stop()
            self.is_running = False
            self.launcher_gui.log("Web interface stopped")
        except Exception as e:
            self.launcher_gui.log(f"Error stopping web interface: {e}")

    def is_server_running(self) -> bool:
        """Check if the web server is running"""
        return self.is_running 

# Factory function for compatibility with imports

def create_web_interface(launcher_gui):
    """Factory function to create a WebInterface instance (for compatibility)"""
    return WebInterface(launcher_gui) 
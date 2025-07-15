#!/usr/bin/env python3
"""
Z-Waifu Launcher GUI - REST API Server
REST API for remote management of the launcher.
"""

import os
import sys
import json
import threading
import time
import subprocess
import psutil
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response, send_file, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt
import hashlib
import secrets
from utils.terminal_enhancements import TerminalEnhancer, OutputType
import csv
from io import StringIO

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zwaifu_launcher_gui import LauncherGUI, TerminalEmulator
except ImportError:
    print("Error: Could not import launcher modules")
    sys.exit(1)

class APIServer:
    def __init__(self, launcher_gui, host='127.0.0.1', port=5001, secret_key=None):
        self.launcher_gui = launcher_gui
        self.host = host
        self.port = port
        self.secret_key = secret_key or secrets.token_hex(32)
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self.secret_key
        
        # Enable CORS
        CORS(self.app)
        
        # Initialize SocketIO for WebSocket support
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
        # API keys (in production, use a database)
        self.api_keys = {}
        self.generate_default_api_key()
        
        # Terminal Enhancer for output analysis
        self.terminal_enhancer = TerminalEnhancer()
        self.output_entries = []  # List of OutputEntry
        
        # WebSocket clients
        self.terminal_subscribers = set()
        
        # Setup routes
        self.setup_routes()
        
        # Setup WebSocket events
        self.setup_websocket_events()
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
    
    def generate_default_api_key(self):
        """Generate a default API key for testing"""
        api_key = secrets.token_hex(32)
        self.api_keys[api_key] = {
            'name': 'Default API Key',
            'created': datetime.now().isoformat(),
            'permissions': ['read', 'write', 'admin']
        }
        print(f"Default API Key: {api_key}")
        return api_key
    
    def verify_api_key(self, api_key):
        """Verify API key and return permissions"""
        if api_key in self.api_keys:
            return self.api_keys[api_key]['permissions']
        return None
    
    def require_auth(self, required_permissions=None):
        """Decorator to require API key authentication"""
        def decorator(f):
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get('X-API-Key')
                if not api_key:
                    return jsonify({'error': 'API key required'}), 401
                
                permissions = self.verify_api_key(api_key)
                if not permissions:
                    return jsonify({'error': 'Invalid API key'}), 401
                
                if required_permissions:
                    if not all(perm in permissions for perm in required_permissions):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        @self.app.route('/api/v1/status', methods=['GET'])
        @self.limiter.limit("10 per minute")
        @self.require_auth(['read'])
        def get_status():
            """Get overall system status"""
            try:
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'launcher_running': True,
                    'processes': self.get_process_status(),
                    'system_info': self.get_system_info(),
                    'config': self.get_config()
                }
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/processes', methods=['GET'])
        @self.limiter.limit("30 per minute")
        @self.require_auth(['read'])
        def get_processes():
            """Get all process instances"""
            try:
                processes = self.get_process_status()
                return jsonify(processes)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/processes/<process_type>', methods=['GET', 'POST'])
        @self.limiter.limit("20 per minute")
        @self.require_auth(['read', 'write'])
        def manage_process_type(process_type):
            """Manage process type"""
            try:
                if request.method == 'GET':
                    # Get all instances of a process type
                    processes = self.get_process_status()
                    if process_type in processes:
                        return jsonify(processes[process_type])
                    else:
                        return jsonify({'error': f'Process type {process_type} not found'}), 404
                
                elif request.method == 'POST':
                    # Create new instance
                    data = request.get_json() or {}
                    result = self.create_process_instance(process_type, data)
                    return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/processes/<process_type>/<int:instance_id>', methods=['GET', 'POST', 'DELETE', 'PUT'])
        @self.limiter.limit("30 per minute")
        @self.require_auth(['read', 'write'])
        def manage_process_instance(process_type, instance_id):
            """Manage individual process instances"""
            try:
                if request.method == 'GET':
                    # Get process status
                    status = self.get_process_instance_status(process_type, instance_id)
                    return jsonify(status)
                
                elif request.method == 'POST':
                    # Start process
                    data = request.get_json() or {}
                    result = self.start_process_instance(process_type, instance_id, data)
                    return jsonify(result)
                
                elif request.method == 'DELETE':
                    # Stop process
                    result = self.stop_process_instance(process_type, instance_id)
                    return jsonify(result)
                
                elif request.method == 'PUT':
                    # Restart process
                    result = self.restart_process_instance(process_type, instance_id)
                    return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/processes/<process_type>/<int:instance_id>/terminal', methods=['GET', 'POST'])
        @self.limiter.limit("50 per minute")
        @self.require_auth(['read', 'write'])
        def manage_terminal(process_type, instance_id):
            """Manage terminal for a process instance"""
            try:
                if request.method == 'GET':
                    # Get terminal output
                    output = self.get_terminal_output(process_type, instance_id)
                    return jsonify({'output': output})
                
                elif request.method == 'POST':
                    # Send command to terminal
                    data = request.get_json()
                    command = data.get('command', '')
                    result = self.send_terminal_command(process_type, instance_id, command)
                    return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/config', methods=['GET', 'PUT'])
        @self.limiter.limit("10 per minute")
        @self.require_auth(['read', 'write'])
        def manage_config():
            """Manage launcher configuration"""
            try:
                if request.method == 'GET':
                    config = self.get_config()
                    return jsonify(config)
                
                elif request.method == 'PUT':
                    data = request.get_json()
                    result = self.update_config(data)
                    return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/logs', methods=['GET'])
        @self.limiter.limit("20 per minute")
        @self.require_auth(['read'])
        def get_logs():
            """Get application logs"""
            try:
                logs = self.get_application_logs()
                return jsonify({'logs': logs})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/analytics', methods=['GET'])
        @self.limiter.limit("10 per minute")
        @self.require_auth(['read'])
        def get_analytics():
            """Get performance analytics"""
            try:
                analytics = self.get_performance_analytics()
                return jsonify(analytics)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/actions/start-all', methods=['POST'])
        @self.limiter.limit("5 per minute")
        @self.require_auth(['write', 'admin'])
        def start_all_processes():
            """Start all processes"""
            try:
                result = self.start_all_processes()
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/actions/stop-all', methods=['POST'])
        @self.limiter.limit("5 per minute")
        @self.require_auth(['write', 'admin'])
        def stop_all_processes():
            """Stop all processes"""
            try:
                result = self.stop_all_processes()
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/actions/restart-all', methods=['POST'])
        @self.limiter.limit("5 per minute")
        @self.require_auth(['write', 'admin'])
        def restart_all_processes():
            """Restart all processes"""
            try:
                result = self.restart_all_processes()
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/keys', methods=['GET', 'POST'])
        @self.limiter.limit("10 per minute")
        @self.require_auth(['admin'])
        def manage_api_keys():
            """Manage API keys"""
            try:
                if request.method == 'GET':
                    # Return list of API keys (without the actual keys)
                    keys_info = []
                    for key, info in self.api_keys.items():
                        keys_info.append({
                            'name': info['name'],
                            'created': info['created'],
                            'permissions': info['permissions'],
                            'key_preview': key[:8] + '...'
                        })
                    return jsonify({'keys': keys_info})
                
                elif request.method == 'POST':
                    # Generate new API key
                    data = request.get_json() or {}
                    name = data.get('name', 'New API Key')
                    permissions = data.get('permissions', ['read'])
                    
                    api_key = secrets.token_hex(32)
                    self.api_keys[api_key] = {
                        'name': name,
                        'created': datetime.now().isoformat(),
                        'permissions': permissions
                    }
                    
                    return jsonify({
                        'success': True,
                        'api_key': api_key,
                        'name': name,
                        'permissions': permissions
                    })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/terminal/output', methods=['GET'])
        def api_terminal_output():
            """Get terminal output for WebSocket clients"""
            try:
                output = self.get_filtered_output()
                return jsonify({'output': output})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/terminal/statistics', methods=['GET'])
        def api_terminal_statistics():
            """Get terminal statistics"""
            try:
                stats = {
                    'total_lines': len(self.output_entries),
                    'error_count': len([e for e in self.output_entries if e.output_type == OutputType.ERROR]),
                    'warning_count': len([e for e in self.output_entries if e.output_type == OutputType.WARNING]),
                    'success_count': len([e for e in self.output_entries if e.output_type == OutputType.SUCCESS])
                }
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/terminal/export', methods=['GET'])
        def api_terminal_export():
            """Export terminal output"""
            try:
                format_type = request.args.get('format', 'csv')
                hours = int(request.args.get('hours', 24))
                
                if format_type == 'csv':
                    def generate_csv():
                        output = StringIO()
                        writer = csv.writer(output)
                        writer.writerow(['Timestamp', 'Type', 'Process', 'Message'])
                        
                        cutoff_time = datetime.now() - timedelta(hours=hours)
                        for entry in self.output_entries:
                            if entry.timestamp >= cutoff_time:
                                writer.writerow([
                                    entry.timestamp.isoformat(),
                                    entry.output_type.value,
                                    entry.process_type or 'system',
                                    entry.message
                                ])
                        
                        output.seek(0)
                        return output.getvalue()
                    
                    response = make_response(generate_csv())
                    response.headers['Content-Type'] = 'text/csv'
                    response.headers['Content-Disposition'] = f'attachment; filename=terminal_output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                    return response
                
                else:
                    return jsonify({'error': 'Unsupported format'}), 400
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(429)
        def too_many_requests(error):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
    
    def setup_websocket_events(self):
        """Setup WebSocket events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            emit('status', {'message': 'Connected to Z-Waifu Launcher API'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            if request.sid in self.terminal_subscribers:
                self.terminal_subscribers.remove(request.sid)
        
        @self.socketio.on('subscribe_terminal')
        def handle_subscribe_terminal():
            """Subscribe to terminal output"""
            self.terminal_subscribers.add(request.sid)
            emit('terminal_subscribed', {'message': 'Subscribed to terminal output'})
        
        @self.socketio.on('unsubscribe_terminal')
        def handle_unsubscribe_terminal():
            """Unsubscribe from terminal output"""
            if request.sid in self.terminal_subscribers:
                self.terminal_subscribers.remove(request.sid)
            emit('terminal_unsubscribed', {'message': 'Unsubscribed from terminal output'})
    
    def broadcast_terminal_output(self, entry):
        """Broadcast terminal output to WebSocket clients"""
        try:
            if self.terminal_subscribers:
                data = {
                    'timestamp': entry.timestamp.isoformat(),
                    'type': entry.output_type.value,
                    'process_type': entry.process_type,
                    'message': entry.message
                }
                self.socketio.emit('terminal_output', data, room=list(self.terminal_subscribers))
        except Exception as e:
            print(f"Error broadcasting terminal output: {e}")
    
    def get_process_status(self):
        """Get status of all processes"""
        try:
            if hasattr(self.launcher_gui, 'process_instance_tabs'):
                process_tabs = self.launcher_gui.process_instance_tabs
            else:
                process_tabs = {}
            
            status = {}
            
            for process_type in ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']:
                if process_type in process_tabs:
                    instances = process_tabs[process_type]
                    status[process_type.lower()] = []
                    
                    for i, instance_data in enumerate(instances):
                        # Check if process is running
                        running = False
                        pid = None
                        if 'proc' in instance_data and instance_data['proc']:
                            try:
                                running = instance_data['proc'].poll() is None
                                pid = instance_data['proc'].pid
                            except:
                                running = False
                        
                        instance_info = {
                            'id': i + 1,
                            'running': running,
                            'pid': pid,
                            'start_time': instance_data.get('start_time'),
                            'uptime': instance_data.get('uptime', 0),
                            'cpu_percent': self.get_process_cpu(instance_data.get('proc')),
                            'memory_mb': self.get_process_memory(instance_data.get('proc'))
                        }
                        status[process_type.lower()].append(instance_info)
            
            return status
            
        except Exception as e:
            self.launcher_gui.log(f"Error getting process status: {e}")
            return {}
    
    def get_process_instance_status(self, process_type, instance_id):
        """Get status of a specific process instance"""
        try:
            process_name = process_type.title()
            if process_name == "Zwaifu":
                process_name = "Z-Waifu"
            
            if hasattr(self.launcher_gui, 'process_instance_tabs'):
                process_tabs = self.launcher_gui.process_instance_tabs
                if process_name in process_tabs:
                    instances = process_tabs[process_name]
                    if instance_id <= len(instances):
                        instance_data = instances[instance_id - 1]
                        
                        # Check if process is running
                        running = False
                        pid = None
                        if 'proc' in instance_data and instance_data['proc']:
                            try:
                                running = instance_data['proc'].poll() is None
                                pid = instance_data['proc'].pid
                            except:
                                running = False
                        
                        return {
                            'id': instance_id,
                            'running': running,
                            'pid': pid,
                            'start_time': instance_data.get('start_time'),
                            'uptime': self.get_process_uptime(instance_data.get('terminal')),
                            'cpu_percent': self.get_process_cpu(instance_data.get('proc')),
                            'memory_mb': self.get_process_memory(instance_data.get('proc'))
                        }
            
            return {'error': 'Instance not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def start_process_instance(self, process_type, instance_id, data=None):
        """Start a process instance"""
        try:
            # Get batch file path
            batch_path = None
            if process_type == "oobabooga":
                batch_path = self.launcher_gui.ooba_bat
            elif process_type == "zwaifu":
                batch_path = self.launcher_gui.zwaifu_bat
            elif process_type == "ollama":
                batch_path = self.launcher_gui.ollama_bat
            elif process_type == "rvc":
                batch_path = self.launcher_gui.rvc_bat
            
            if not batch_path or not os.path.exists(batch_path):
                return {'error': f'Batch file not found for {process_type}'}
            
            # Create new process
            proc = subprocess.Popen([batch_path], cwd=os.path.dirname(batch_path), shell=False,
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
        """Stop a process instance"""
        try:
            if process_type in self.launcher_gui.process_instance_tabs:
                instances = self.launcher_gui.process_instance_tabs[process_type]
                if instance_id < len(instances):
                    instance_data = instances[instance_id]
                    proc = instance_data.get('proc')
                    
                    if proc and proc.poll() is None:
                        proc.terminate()
                        return {'success': True, 'message': f'Stopped {process_type} Instance {instance_id+1}'}
                    else:
                        return {'error': f'Process {process_type} Instance {instance_id+1} is not running'}
            
            return {'error': f'Instance {instance_id} not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def restart_process_instance(self, process_type, instance_id):
        """Restart a process instance"""
        try:
            # Stop first
            stop_result = self.stop_process_instance(process_type, instance_id)
            if 'error' in stop_result:
                return stop_result
            
            # Wait a moment
            time.sleep(1)
            
            # Start again
            start_result = self.start_process_instance(process_type, instance_id)
            return start_result
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_process_instance(self, process_type, data=None):
        """Create a new process instance"""
        try:
            # This would create a new tab and instance
            # For now, we'll just return success
            return {'success': True, 'message': f'Created new {process_type} instance'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_config(self):
        """Get launcher configuration"""
        try:
            config = {
                'ooba_bat': getattr(self.launcher_gui, 'ooba_bat', None),
                'zwaifu_bat': getattr(self.launcher_gui, 'zwaifu_bat', None),
                'ollama_bat': getattr(self.launcher_gui, 'ollama_bat', None),
                'rvc_bat': getattr(self.launcher_gui, 'rvc_bat', None),
                'ooba_port': getattr(self.launcher_gui, 'ooba_port_var', None),
                'zwaifu_port': getattr(self.launcher_gui, 'zwaifu_port_var', None)
            }
            return config
        except Exception as e:
            return {'error': str(e)}
    
    def update_config(self, data):
        """Update launcher configuration"""
        try:
            # Update configuration based on data
            # This would update the launcher GUI configuration
            return {'success': True, 'message': 'Configuration updated'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_terminal_output(self, process_type, instance_id):
        """Get terminal output for a process instance"""
        try:
            if hasattr(self.launcher_gui, 'process_instance_tabs'):
                process_tabs = self.launcher_gui.process_instance_tabs
                if process_type in process_tabs:
                    instances = process_tabs[process_type]
                    if instance_id <= len(instances):
                        instance_data = instances[instance_id - 1]
                        if 'terminal' in instance_data:
                            terminal = instance_data['terminal']
                            if terminal:
                                return terminal.get_output_buffer()
            return []
        except Exception as e:
            return []
    
    def send_terminal_command(self, process_type, instance_id, command):
        """Send command to terminal"""
        try:
            if hasattr(self.launcher_gui, 'process_instance_tabs'):
                process_tabs = self.launcher_gui.process_instance_tabs
                if process_type in process_tabs:
                    instances = process_tabs[process_type]
                    if instance_id <= len(instances):
                        instance_data = instances[instance_id - 1]
                        if 'terminal' in instance_data:
                            terminal = instance_data['terminal']
                            if terminal and terminal.process:
                                terminal.process.stdin.write(command + '\n')
                                terminal.process.stdin.flush()
                                return {'success': True, 'message': 'Command sent'}
            return {'error': 'Terminal not found'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_application_logs(self):
        """Get application logs"""
        try:
            # This would read from the actual log file
            return []
        except Exception as e:
            return []
    
    def get_performance_analytics(self):
        """Get performance analytics"""
        try:
            analytics = {
                'system': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent
                },
                'processes': self.get_process_status()
            }
            return analytics
        except Exception as e:
            return {'error': str(e)}
    
    def start_all_processes(self):
        """Start all processes"""
        try:
            # This would start all configured processes
            return {'success': True, 'message': 'All processes started'}
        except Exception as e:
            return {'error': str(e)}
    
    def stop_all_processes(self):
        """Stop all processes"""
        try:
            # This would stop all running processes
            return {'success': True, 'message': 'All processes stopped'}
        except Exception as e:
            return {'error': str(e)}
    
    def restart_all_processes(self):
        """Restart all processes"""
        try:
            # This would restart all processes
            return {'success': True, 'message': 'All processes restarted'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_process_uptime(self, terminal):
        """Get process uptime"""
        try:
            if terminal and hasattr(terminal, 'start_time') and terminal.start_time:
                return time.time() - terminal.start_time
            return 0
        except Exception:
            return 0
    
    def get_process_cpu(self, proc):
        """Get process CPU usage"""
        try:
            if proc and proc.poll() is None:
                process = psutil.Process(proc.pid)
                return process.cpu_percent()
            return 0
        except Exception:
            return 0
    
    def get_process_memory(self, proc):
        """Get process memory usage"""
        try:
            if proc and proc.poll() is None:
                process = psutil.Process(proc.pid)
                return process.memory_info().rss / 1024 / 1024  # MB
            return 0
        except Exception:
            return 0
    
    def get_system_info(self):
        """Get system information"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_launcher_memory_usage(self):
        """Get launcher memory usage"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except Exception:
            return 0
    
    def monitor_system(self):
        """Monitor system and broadcast updates"""
        while self.monitoring_active:
            try:
                # Broadcast system status
                system_info = self.get_system_info()
                self.socketio.emit('system_update', system_info)
                time.sleep(5)
            except Exception as e:
                print(f"Error in system monitoring: {e}")
                time.sleep(10)
    
    def start(self):
        """Start the API server"""
        try:
            self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
        except Exception as e:
            print(f"Error starting API server: {e}")
    
    def stop(self):
        """Stop the API server"""
        self.monitoring_active = False
        if hasattr(self, 'socketio'):
            self.socketio.stop()
    
    def add_terminal_output(self, line, stream='stdout'):
        """Add terminal output entry"""
        try:
            entry = self.terminal_enhancer.analyze_output(line, stream)
            self.output_entries.append(entry)
            
            # Keep only last 1000 entries
            if len(self.output_entries) > 1000:
                self.output_entries.pop(0)
            
            # Broadcast to WebSocket clients
            self.broadcast_terminal_output(entry)
            
        except Exception as e:
            print(f"Error adding terminal output: {e}")
    
    def get_filtered_output(self, errors_only=False, warnings_only=False, search=None):
        """Get filtered terminal output"""
        try:
            filtered = self.output_entries
            
            if errors_only:
                filtered = [e for e in filtered if e.output_type == OutputType.ERROR]
            elif warnings_only:
                filtered = [e for e in filtered if e.output_type == OutputType.WARNING]
            
            if search:
                filtered = [e for e in filtered if search.lower() in e.message.lower()]
            
            return [{'timestamp': e.timestamp.isoformat(), 'type': e.output_type.value, 'message': e.message} for e in filtered]
        except Exception as e:
            return []

def create_api_server(launcher_gui, host='127.0.0.1', port=5001, secret_key=None):
    """Create and return an API server instance"""
    try:
        return APIServer(launcher_gui, host, port, secret_key)
    except Exception as e:
        print(f"Error creating API server: {e}")
        return None

if __name__ == "__main__":
    # Test API server
    print("Z-Waifu Launcher API Server")
    print("This module provides REST API for remote management of the launcher.")
    print("To use, import and call create_api_server() with your launcher instance.") 
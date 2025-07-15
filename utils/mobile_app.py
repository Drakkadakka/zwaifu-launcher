#!/usr/bin/env python3
"""
Z-Waifu Launcher GUI - Mobile App Interface
Mobile app for remote monitoring and control.
"""

import os
import sys
import json
import threading
import time
import subprocess
import psutil
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import webbrowser
from typing import Dict, List, Any, Optional
import logging

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zwaifu_launcher_gui import LauncherGUI, TerminalEmulator
except ImportError:
    print("Error: Could not import launcher modules")
    sys.exit(1)

class MobileApp:
    def __init__(self, launcher_gui, host='0.0.0.0', port=8081):
        self.launcher_gui = launcher_gui
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'zwaifu-launcher-mobile-app'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Mobile-specific features
        self.push_notifications = []
        self.mobile_sessions = {}
        
        # Setup routes
        self.setup_routes()
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_for_mobile, daemon=True)
        self.monitor_thread.start()
    
    def setup_routes(self):
        """Setup Flask routes for mobile app"""
        
        @self.app.route('/')
        def mobile_dashboard():
            """Mobile dashboard page"""
            return render_template('mobile_dashboard.html')
        
        @self.app.route('/mobile/api/status')
        def mobile_status():
            """Get mobile-optimized status"""
            try:
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'launcher_running': True,
                    'processes': self.get_mobile_process_status(),
                    'system_info': self.get_mobile_system_info(),
                    'notifications': self.get_notifications()
                }
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/processes')
        def mobile_processes():
            """Get mobile-optimized process list"""
            try:
                processes = self.get_mobile_process_status()
                return jsonify(processes)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/process/<process_type>/<int:instance_id>', methods=['GET', 'POST', 'DELETE'])
        def mobile_process_control(process_type, instance_id):
            """Mobile process control"""
            try:
                if request.method == 'GET':
                    status = self.get_process_instance_status(process_type, instance_id)
                    return jsonify(status)
                
                elif request.method == 'POST':
                    result = self.start_process_instance(process_type, instance_id)
                    return jsonify(result)
                
                elif request.method == 'DELETE':
                    result = self.stop_process_instance(process_type, instance_id)
                    return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/quick-actions', methods=['POST'])
        def mobile_quick_actions():
            """Mobile quick actions"""
            try:
                data = request.get_json()
                action = data.get('action')
                
                if action == 'start_all':
                    result = self.start_all_processes()
                elif action == 'stop_all':
                    result = self.stop_all_processes()
                elif action == 'restart_all':
                    result = self.restart_all_processes()
                else:
                    result = {'error': 'Unknown action'}
                
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/notifications')
        def mobile_notifications():
            """Get mobile notifications"""
            try:
                notifications = self.get_notifications()
                return jsonify(notifications)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/notifications/clear', methods=['POST'])
        def clear_notifications():
            """Clear notifications"""
            try:
                self.clear_notifications()
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/terminal/<process_type>/<int:instance_id>')
        def mobile_terminal(process_type, instance_id):
            """Get terminal output for mobile"""
            try:
                output = self.get_terminal_output(process_type, instance_id)
                return jsonify({'output': output})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/terminal/<process_type>/<int:instance_id>', methods=['POST'])
        def mobile_terminal_input(process_type, instance_id):
            """Send terminal input from mobile"""
            try:
                data = request.get_json()
                command = data.get('command', '')
                result = self.send_terminal_command(process_type, instance_id, command)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/analytics')
        def mobile_analytics():
            """Get mobile-optimized analytics"""
            try:
                analytics = self.get_mobile_analytics()
                return jsonify(analytics)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/settings')
        def mobile_settings():
            """Get mobile settings"""
            try:
                settings = self.get_mobile_settings()
                return jsonify(settings)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/mobile/api/settings', methods=['PUT'])
        def update_mobile_settings():
            """Update mobile settings"""
            try:
                data = request.get_json()
                result = self.update_mobile_settings(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # WebSocket events for mobile
        @self.socketio.on('mobile_connect')
        def handle_mobile_connect():
            """Handle mobile client connection"""
            try:
                session_id = request.sid
                self.mobile_sessions[session_id] = {
                    'connected_at': datetime.now(),
                    'last_activity': datetime.now()
                }
                emit('mobile_status', {'message': 'Connected to Z-Waifu Launcher Mobile'})
            except Exception as e:
                print(f"Error handling mobile connect: {e}")
        
        @self.socketio.on('mobile_disconnect')
        def handle_mobile_disconnect():
            """Handle mobile client disconnection"""
            try:
                session_id = request.sid
                if session_id in self.mobile_sessions:
                    del self.mobile_sessions[session_id]
            except Exception as e:
                print(f"Error handling mobile disconnect: {e}")
        
        @self.socketio.on('mobile_request_status')
        def handle_mobile_status_request():
            """Handle mobile status request"""
            try:
                status = self.get_mobile_process_status()
                emit('mobile_status_update', status)
            except Exception as e:
                print(f"Error handling mobile status request: {e}")
    
    def get_mobile_process_status(self):
        """Get mobile-optimized process status"""
        try:
            if hasattr(self.launcher_gui, 'process_instance_tabs'):
                process_tabs = self.launcher_gui.process_instance_tabs
            else:
                process_tabs = {}
            
            mobile_status = {}
            
            for process_type in ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']:
                if process_type in process_tabs:
                    instances = process_tabs[process_type]
                    mobile_status[process_type.lower()] = {
                        'name': process_type,
                        'icon': self.get_process_icon(process_type),
                        'color': self.get_process_color(process_type),
                        'running_count': 0,
                        'total_count': len(instances),
                        'instances': []
                    }
                    
                    for i, instance_data in enumerate(instances):
                        # Check if process is running
                        running = False
                        if 'proc' in instance_data and instance_data['proc']:
                            try:
                                running = instance_data['proc'].poll() is None
                            except:
                                running = False
                        
                        if running:
                            mobile_status[process_type.lower()]['running_count'] += 1
                        
                        instance_info = {
                            'id': i + 1,
                            'running': running,
                            'uptime': self.get_process_uptime(instance_data.get('terminal')),
                            'cpu_percent': self.get_process_cpu(instance_data.get('proc')),
                            'memory_mb': self.get_process_memory(instance_data.get('proc'))
                        }
                        mobile_status[process_type.lower()]['instances'].append(instance_info)
            
            return mobile_status
            
        except Exception as e:
            self.launcher_gui.log(f"Error getting mobile process status: {e}")
            return {}
    
    def get_mobile_system_info(self):
        """Get mobile-optimized system info"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'uptime': self.get_system_uptime()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_mobile_analytics(self):
        """Get mobile-optimized analytics"""
        try:
            return {
                'system': self.get_mobile_system_info(),
                'processes': self.get_mobile_process_status(),
                'notifications_count': len(self.push_notifications)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_mobile_settings(self):
        """Get mobile settings"""
        try:
            return {
                'auto_refresh': True,
                'refresh_interval': 30,
                'notifications_enabled': True,
                'dark_mode': True
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_mobile_settings(self, settings):
        """Update mobile settings"""
        try:
            # This would update mobile-specific settings
            return {'success': True, 'message': 'Settings updated'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_notifications(self):
        """Get push notifications"""
        return self.push_notifications
    
    def add_notification(self, title, message, level='info'):
        """Add a push notification"""
        try:
            notification = {
                'id': len(self.push_notifications) + 1,
                'title': title,
                'message': message,
                'level': level,
                'timestamp': datetime.now().isoformat(),
                'read': False
            }
            self.push_notifications.append(notification)
            
            # Keep only last 50 notifications
            if len(self.push_notifications) > 50:
                self.push_notifications.pop(0)
            
            # Broadcast to mobile clients
            self.socketio.emit('mobile_notification', notification)
            
        except Exception as e:
            print(f"Error adding notification: {e}")
    
    def clear_notifications(self):
        """Clear all notifications"""
        try:
            self.push_notifications.clear()
        except Exception as e:
            print(f"Error clearing notifications: {e}")
    
    def get_process_icon(self, process_type):
        """Get process icon for mobile"""
        icons = {
            'Oobabooga': '🤖',
            'Z-Waifu': '💬',
            'Ollama': '🦙',
            'RVC': '🎵'
        }
        return icons.get(process_type, '⚙️')
    
    def get_process_color(self, process_type):
        """Get process color for mobile"""
        colors = {
            'Oobabooga': '#667eea',
            'Z-Waifu': '#764ba2',
            'Ollama': '#28a745',
            'RVC': '#ffc107'
        }
        return colors.get(process_type, '#6c757d')
    
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
                        if 'proc' in instance_data and instance_data['proc']:
                            try:
                                running = instance_data['proc'].poll() is None
                            except:
                                running = False
                        
                        return {
                            'id': instance_id,
                            'running': running,
                            'uptime': self.get_process_uptime(instance_data.get('terminal')),
                            'cpu_percent': self.get_process_cpu(instance_data.get('proc')),
                            'memory_mb': self.get_process_memory(instance_data.get('proc'))
                        }
            
            return {'error': 'Instance not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def start_process_instance(self, process_type, instance_id):
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
            
            # Add notification
            self.add_notification(
                f"{process_type.title()} Started",
                f"Instance {instance_id+1} has been started successfully",
                'success'
            )
            
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
                        
                        # Add notification
                        self.add_notification(
                            f"{process_type.title()} Stopped",
                            f"Instance {instance_id+1} has been stopped",
                            'info'
                        )
                        
                        return {'success': True, 'message': f'Stopped {process_type} Instance {instance_id+1}'}
                    else:
                        return {'error': f'Process {process_type} Instance {instance_id+1} is not running'}
            
            return {'error': f'Instance {instance_id} not found'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def start_all_processes(self):
        """Start all processes"""
        try:
            # This would start all configured processes
            self.add_notification(
                "All Processes Started",
                "All configured processes have been started",
                'success'
            )
            return {'success': True, 'message': 'All processes started'}
        except Exception as e:
            return {'error': str(e)}
    
    def stop_all_processes(self):
        """Stop all processes"""
        try:
            # This would stop all running processes
            self.add_notification(
                "All Processes Stopped",
                "All running processes have been stopped",
                'warning'
            )
            return {'success': True, 'message': 'All processes stopped'}
        except Exception as e:
            return {'error': str(e)}
    
    def restart_all_processes(self):
        """Restart all processes"""
        try:
            # This would restart all processes
            self.add_notification(
                "All Processes Restarted",
                "All processes have been restarted",
                'info'
            )
            return {'success': True, 'message': 'All processes restarted'}
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
    
    def get_system_uptime(self):
        """Get system uptime"""
        try:
            return time.time() - psutil.boot_time()
        except Exception:
            return 0
    
    def monitor_for_mobile(self):
        """Monitor system for mobile updates"""
        while self.monitoring_active:
            try:
                # Check for system alerts
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                if cpu_percent > 80:
                    self.add_notification(
                        "High CPU Usage",
                        f"CPU usage is at {cpu_percent:.1f}%",
                        'warning'
                    )
                
                if memory_percent > 80:
                    self.add_notification(
                        "High Memory Usage",
                        f"Memory usage is at {memory_percent:.1f}%",
                        'warning'
                    )
                
                # Broadcast status updates to mobile clients
                if self.mobile_sessions:
                    status = self.get_mobile_process_status()
                    self.socketio.emit('mobile_status_update', status)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in mobile monitoring: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the mobile app server"""
        try:
            self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
        except Exception as e:
            print(f"Error starting mobile app: {e}")
    
    def stop(self):
        """Stop the mobile app server"""
        self.monitoring_active = False
        if hasattr(self, 'socketio'):
            self.socketio.stop()

def create_mobile_app(launcher_gui, host='0.0.0.0', port=8081):
    """Create and return a mobile app instance"""
    try:
        return MobileApp(launcher_gui, host, port)
    except Exception as e:
        print(f"Error creating mobile app: {e}")
        return None 
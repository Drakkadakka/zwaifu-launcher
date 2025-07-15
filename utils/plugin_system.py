#!/usr/bin/env python3
"""
Z-Waifu Launcher GUI - Plugin System
Extensible architecture for custom features and plugins.
"""

import os
import sys
import json
import importlib
import importlib.util
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import logging

try:
    import psutil
except ImportError:
    psutil = None

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zwaifu_launcher_gui import LauncherGUI, TerminalEmulator
except ImportError:
    print("Error: Could not import launcher modules")
    sys.exit(1)

class PluginBase:
    """Base class for all plugins"""
    
    def __init__(self, launcher_gui: LauncherGUI):
        self.launcher_gui = launcher_gui
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.description = "Base plugin class"
        self.author = "Unknown"
        self.enabled = False
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"plugin.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            self.logger.info(f"Initializing plugin: {self.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing plugin {self.name}: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable the plugin"""
        try:
            self.enabled = True
            self.logger.info(f"Enabled plugin: {self.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error enabling plugin {self.name}: {e}")
            return False
    
    def disable(self) -> bool:
        """Disable the plugin"""
        try:
            self.enabled = False
            self.logger.info(f"Disabled plugin: {self.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error disabling plugin {self.name}: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        try:
            self.logger.info(f"Cleaning up plugin: {self.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error cleaning up plugin {self.name}: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self.config
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """Set plugin configuration"""
        try:
            self.config = config
            return True
        except Exception as e:
            self.logger.error(f"Error setting config for plugin {self.name}: {e}")
            return False
    
    def on_process_start(self, process_type: str, instance_id: int) -> None:
        """Called when a process starts"""
        pass
    
    def on_process_stop(self, process_type: str, instance_id: int) -> None:
        """Called when a process stops"""
        pass
    
    def on_process_error(self, process_type: str, instance_id: int, error: str) -> None:
        """Called when a process encounters an error"""
        pass
    
    def on_config_change(self, config: Dict[str, Any]) -> None:
        """Called when launcher configuration changes"""
        pass
    
    def on_launcher_start(self) -> None:
        """Called when launcher starts"""
        pass
    
    def on_launcher_stop(self) -> None:
        """Called when launcher stops"""
        pass

class PluginManager:
    """Manages plugin loading, enabling, and lifecycle"""
    
    def __init__(self, launcher_gui: LauncherGUI):
        self.launcher_gui = launcher_gui
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        self.config_file = os.path.join(os.path.dirname(__file__), 'plugin_config.json')
        
        # Create plugin directory if it doesn't exist
        os.makedirs(self.plugin_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('plugin_manager')
        
        # Load plugin configurations
        self.load_plugin_configs()
        
        # Auto-discovery and loading
        self.discover_plugins()
    
    def load_plugin_configs(self) -> None:
        """Load plugin configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.plugin_configs = json.load(f)
            else:
                self.plugin_configs = {}
        except Exception as e:
            self.logger.error(f"Error loading plugin configs: {e}")
            self.plugin_configs = {}
    
    def save_plugin_configs(self) -> None:
        """Save plugin configurations to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.plugin_configs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin configs: {e}")
    
    def discover_plugins(self) -> None:
        """Discover and load available plugins"""
        try:
            self.logger.info("Discovering plugins...")
            
            # Look for plugin files in the plugin directory
            for filename in os.listdir(self.plugin_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    plugin_name = filename[:-3]  # Remove .py extension
                    plugin_path = os.path.join(self.plugin_dir, filename)
                    
                    try:
                        self.load_plugin(plugin_name, plugin_path)
                    except Exception as e:
                        self.logger.error(f"Error loading plugin {plugin_name}: {e}")
        except Exception as e:
            self.logger.error(f"Error discovering plugins: {e}")
    
    def load_plugin(self, plugin_name: str, plugin_path: str) -> bool:
        """Load a plugin from file"""
        try:
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"Failed to create spec for plugin {plugin_name}")
                return False
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class (should inherit from PluginBase)
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginBase) and 
                    attr != PluginBase):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                self.logger.warning(f"No plugin class found in {plugin_name}")
                return False
            
            # Create plugin instance
            plugin = plugin_class(self.launcher_gui)
            
            # Load plugin configuration
            if plugin_name in self.plugin_configs:
                plugin.set_config(self.plugin_configs[plugin_name])
            
            # Initialize plugin
            if plugin.initialize():
                self.plugins[plugin_name] = plugin
                self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                
                # Auto-enable if configured
                if plugin_name in self.plugin_configs:
                    if self.plugin_configs[plugin_name].get('auto_enable', False):
                        self.enable_plugin(plugin_name)
                
                return True
            else:
                self.logger.error(f"Failed to initialize plugin {plugin_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                if plugin.enable():
                    # Update configuration
                    if plugin_name not in self.plugin_configs:
                        self.plugin_configs[plugin_name] = {}
                    self.plugin_configs[plugin_name]['enabled'] = True
                    self.save_plugin_configs()
                    return True
                else:
                    return False
            else:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error enabling plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                if plugin.disable():
                    # Update configuration
                    if plugin_name not in self.plugin_configs:
                        self.plugin_configs[plugin_name] = {}
                    self.plugin_configs[plugin_name]['enabled'] = False
                    self.save_plugin_configs()
                    return True
                else:
                    return False
            else:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error disabling plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                plugin.cleanup()
                del self.plugins[plugin_name]
                self.logger.info(f"Unloaded plugin: {plugin_name}")
                return True
            else:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a plugin by name"""
        return self.plugins.get(plugin_name)
    
    def get_plugins(self) -> Dict[str, PluginBase]:
        """Get all plugins"""
        return self.plugins.copy()
    
    def get_enabled_plugins(self) -> Dict[str, PluginBase]:
        """Get all enabled plugins"""
        return {name: plugin for name, plugin in self.plugins.items() if plugin.enabled}
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Set configuration for a plugin"""
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                if plugin.set_config(config):
                    self.plugin_configs[plugin_name] = config
                    self.save_plugin_configs()
                    return True
                else:
                    return False
            else:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error setting config for plugin {plugin_name}: {e}")
            return False
    
    def notify_process_start(self, process_type: str, instance_id: int) -> None:
        """Notify all enabled plugins of process start"""
        try:
            for plugin in self.get_enabled_plugins().values():
                try:
                    plugin.on_process_start(process_type, instance_id)
                except Exception as e:
                    self.logger.error(f"Error in plugin {plugin.name} on_process_start: {e}")
        except Exception as e:
            self.logger.error(f"Error notifying plugins of process start: {e}")
    
    def notify_process_stop(self, process_type: str, instance_id: int) -> None:
        """Notify all enabled plugins of process stop"""
        try:
            for plugin in self.get_enabled_plugins().values():
                try:
                    plugin.on_process_stop(process_type, instance_id)
                except Exception as e:
                    self.logger.error(f"Error in plugin {plugin.name} on_process_stop: {e}")
        except Exception as e:
            self.logger.error(f"Error notifying plugins of process stop: {e}")
    
    def notify_process_error(self, process_type: str, instance_id: int, error: str) -> None:
        """Notify all enabled plugins of process error"""
        try:
            for plugin in self.get_enabled_plugins().values():
                try:
                    plugin.on_process_error(process_type, instance_id, error)
                except Exception as e:
                    self.logger.error(f"Error in plugin {plugin.name} on_process_error: {e}")
        except Exception as e:
            self.logger.error(f"Error notifying plugins of process error: {e}")
    
    def notify_config_change(self, config: Dict[str, Any]) -> None:
        """Notify all enabled plugins of configuration change"""
        try:
            for plugin in self.get_enabled_plugins().values():
                try:
                    plugin.on_config_change(config)
                except Exception as e:
                    self.logger.error(f"Error in plugin {plugin.name} on_config_change: {e}")
        except Exception as e:
            self.logger.error(f"Error notifying plugins of config change: {e}")
    
    def notify_launcher_start(self) -> None:
        """Notify all enabled plugins of launcher start"""
        try:
            for plugin in self.get_enabled_plugins().values():
                try:
                    plugin.on_launcher_start()
                except Exception as e:
                    self.logger.error(f"Error in plugin {plugin.name} on_launcher_start: {e}")
        except Exception as e:
            self.logger.error(f"Error notifying plugins of launcher start: {e}")
    
    def notify_launcher_stop(self) -> None:
        """Notify all enabled plugins of launcher stop"""
        try:
            for plugin in self.get_enabled_plugins().values():
                try:
                    plugin.on_launcher_stop()
                except Exception as e:
                    self.logger.error(f"Error in plugin {plugin.name} on_launcher_stop: {e}")
        except Exception as e:
            self.logger.error(f"Error notifying plugins of launcher stop: {e}")
    
    def cleanup(self) -> None:
        """Cleanup all plugins"""
        try:
            for plugin_name, plugin in self.plugins.items():
                try:
                    plugin.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up plugin {plugin_name}: {e}")
            
            self.plugins.clear()
            self.logger.info("Plugin manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error in plugin manager cleanup: {e}")

class ProcessMonitorPlugin(PluginBase):
    """Plugin for monitoring process health and performance"""
    
    def __init__(self, launcher_gui: LauncherGUI):
        super().__init__(launcher_gui)
        self.name = "Process Monitor"
        self.version = "1.0.0"
        self.description = "Monitors process health and performance"
        self.author = "Z-Waifu Team"
        self.monitoring_thread = None
        self.monitoring_active = False
    
    def initialize(self) -> bool:
        """Initialize the process monitor plugin"""
        try:
            self.config.setdefault('monitor_interval', 30)  # seconds
            self.config.setdefault('alert_thresholds', {
                'cpu_percent': 80,
                'memory_percent': 80,
                'restart_count': 5
            })
            return True
        except Exception as e:
            self.logger.error(f"Error initializing ProcessMonitorPlugin: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable the process monitor"""
        try:
            if super().enable():
                self.monitoring_active = True
                self.monitoring_thread = threading.Thread(target=self._monitor_processes, daemon=True)
                self.monitoring_thread.start()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error enabling ProcessMonitorPlugin: {e}")
            return False
    
    def disable(self) -> bool:
        """Disable the process monitor"""
        try:
            self.monitoring_active = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            return super().disable()
        except Exception as e:
            self.logger.error(f"Error disabling ProcessMonitorPlugin: {e}")
            return False
    
    def _monitor_processes(self) -> None:
        """Monitor processes for health issues"""
        try:
            while self.monitoring_active:
                if hasattr(self.launcher_gui, 'process_instance_tabs'):
                    process_tabs = self.launcher_gui.process_instance_tabs
                    
                    for process_type in ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']:
                        if process_type in process_tabs:
                            instances = process_tabs[process_type]
                            
                            for i, instance_data in enumerate(instances):
                                proc = instance_data.get('proc')
                                if proc and proc.poll() is None:
                                    try:
                                        process = psutil.Process(proc.pid)
                                        cpu_percent = process.cpu_percent()
                                        memory_percent = process.memory_percent()
                                        
                                        # Check thresholds
                                        if cpu_percent > self.config['alert_thresholds']['cpu_percent']:
                                            self.logger.warning(f"High CPU usage in {process_type} Instance {i+1}: {cpu_percent:.1f}%")
                                        
                                        if memory_percent > self.config['alert_thresholds']['memory_percent']:
                                            self.logger.warning(f"High memory usage in {process_type} Instance {i+1}: {memory_percent:.1f}%")
                                            
                                    except (psutil.NoProcess, psutil.AccessDenied):
                                        pass
                
                time.sleep(self.config['monitor_interval'])
        except Exception as e:
            self.logger.error(f"Error in process monitoring: {e}")

class AutoRestartPlugin(PluginBase):
    """Plugin for automatically restarting failed processes"""
    
    def __init__(self, launcher_gui: LauncherGUI):
        super().__init__(launcher_gui)
        self.name = "Auto Restart"
        self.version = "1.0.0"
        self.description = "Automatically restarts failed processes"
        self.author = "Z-Waifu Team"
        self.restart_counts = {}
    
    def initialize(self) -> bool:
        """Initialize the auto restart plugin"""
        try:
            self.config.setdefault('max_restarts', 3)
            self.config.setdefault('restart_delay', 30)  # seconds
            self.config.setdefault('reset_interval', 3600)  # 1 hour
            return True
        except Exception as e:
            self.logger.error(f"Error initializing AutoRestartPlugin: {e}")
            return False
    
    def on_process_error(self, process_type: str, instance_id: int, error: str) -> None:
        """Handle process errors and attempt restart"""
        try:
            process_key = f"{process_type}_{instance_id}"
            
            # Increment restart count
            if process_key not in self.restart_counts:
                self.restart_counts[process_key] = 0
            self.restart_counts[process_key] += 1
            
            # Check if we should restart
            if self.restart_counts[process_key] <= self.config['max_restarts']:
                self.logger.info(f"Auto-restarting {process_type} Instance {instance_id} (attempt {self.restart_counts[process_key]})")
                
                # Schedule restart
                threading.Timer(self.config['restart_delay'], 
                              self._restart_process, 
                              args=[process_type, instance_id]).start()
            else:
                self.logger.error(f"Max restart attempts reached for {process_type} Instance {instance_id}")
        except Exception as e:
            self.logger.error(f"Error in auto restart plugin: {e}")
    
    def _restart_process(self, process_type: str, instance_id: int) -> None:
        """Restart a specific process"""
        try:
            if hasattr(self.launcher_gui, 'start_process_instance'):
                self.launcher_gui.start_process_instance(process_type.lower())
                self.logger.info(f"Successfully restarted {process_type} Instance {instance_id}")
            else:
                self.logger.error("Launcher GUI does not support process restart")
        except Exception as e:
            self.logger.error(f"Error restarting process: {e}")

class NotificationPlugin(PluginBase):
    """Plugin for sending notifications on events"""
    
    def __init__(self, launcher_gui: LauncherGUI):
        super().__init__(launcher_gui)
        self.name = "Notifications"
        self.version = "1.0.0"
        self.description = "Sends notifications for important events"
        self.author = "Z-Waifu Team"
    
    def initialize(self) -> bool:
        """Initialize the notification plugin"""
        try:
            self.config.setdefault('notify_on_start', True)
            self.config.setdefault('notify_on_stop', True)
            self.config.setdefault('notify_on_error', True)
            return True
        except Exception as e:
            self.logger.error(f"Error initializing NotificationPlugin: {e}")
            return False
    
    def on_process_start(self, process_type: str, instance_id: int) -> None:
        """Send notification when process starts"""
        if self.config.get('notify_on_start', True):
            self._send_notification(f"{process_type} Started", f"Instance {instance_id} has started", 'info')
    
    def on_process_stop(self, process_type: str, instance_id: int) -> None:
        """Send notification when process stops"""
        if self.config.get('notify_on_stop', True):
            self._send_notification(f"{process_type} Stopped", f"Instance {instance_id} has stopped", 'warning')
    
    def on_process_error(self, process_type: str, instance_id: int, error: str) -> None:
        """Send notification when process encounters error"""
        if self.config.get('notify_on_error', True):
            self._send_notification(f"{process_type} Error", f"Instance {instance_id}: {error}", 'error')
    
    def _send_notification(self, title: str, message: str, level: str) -> None:
        """Send a notification"""
        try:
            # This would integrate with the system's notification system
            # For now, just log the notification
            self.logger.info(f"NOTIFICATION [{level.upper()}]: {title} - {message}")
            
            # Could also integrate with web interface or mobile app notifications
            if hasattr(self.launcher_gui, 'web_interface') and self.launcher_gui.web_interface:
                # Send to web interface
                pass
            
            if hasattr(self.launcher_gui, 'mobile_app') and self.launcher_gui.mobile_app:
                # Send to mobile app
                pass
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")

def create_plugin_manager(launcher_gui: LauncherGUI) -> Optional[PluginManager]:
    """Create and return a plugin manager instance"""
    try:
        plugin_manager = PluginManager(launcher_gui)
        
        # Create example plugins if they don't exist
        create_example_plugins(plugin_manager.plugin_dir)
        
        return plugin_manager
    except Exception as e:
        print(f"Error creating plugin manager: {e}")
        return None

def create_example_plugins(plugins_dir: str) -> None:
    """Create example plugin files"""
    try:
        # Process Monitor Plugin
        process_monitor_content = '''#!/usr/bin/env python3
"""
Example Process Monitor Plugin
Monitors process health and performance
"""

from utils.plugin_system import PluginBase
import psutil
import threading
import time

class ProcessMonitorPlugin(PluginBase):
    def __init__(self, launcher_gui):
        super().__init__(launcher_gui)
        self.name = "Process Monitor"
        self.version = "1.0.0"
        self.description = "Monitors process health and performance"
        self.author = "Z-Waifu Team"
        self.monitoring_thread = None
        self.monitoring_active = False
    
    def initialize(self):
        self.config.setdefault('monitor_interval', 30)
        self.config.setdefault('alert_thresholds', {
            'cpu_percent': 80,
            'memory_percent': 80
        })
        return True
    
    def enable(self):
        if super().enable():
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitor_processes, daemon=True)
            self.monitoring_thread.start()
            return True
        return False
    
    def disable(self):
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        return super().disable()
    
    def _monitor_processes(self):
        while self.monitoring_active:
            # Monitor processes here
            time.sleep(self.config['monitor_interval'])
'''
        
        # Auto Restart Plugin
        auto_restart_content = '''#!/usr/bin/env python3
"""
Example Auto Restart Plugin
Automatically restarts failed processes
"""

from utils.plugin_system import PluginBase
import threading

class AutoRestartPlugin(PluginBase):
    def __init__(self, launcher_gui):
        super().__init__(launcher_gui)
        self.name = "Auto Restart"
        self.version = "1.0.0"
        self.description = "Automatically restarts failed processes"
        self.author = "Z-Waifu Team"
        self.restart_counts = {}
    
    def initialize(self):
        self.config.setdefault('max_restarts', 3)
        self.config.setdefault('restart_delay', 30)
        return True
    
    def on_process_error(self, process_type, instance_id, error):
        # Handle process errors and restart if needed
        pass
'''
        
        # Write example plugins
        process_monitor_file = os.path.join(plugins_dir, 'process_monitor_example.py')
        auto_restart_file = os.path.join(plugins_dir, 'auto_restart_example.py')
        
        if not os.path.exists(process_monitor_file):
            with open(process_monitor_file, 'w', encoding='utf-8') as f:
                f.write(process_monitor_content)
        
        if not os.path.exists(auto_restart_file):
            with open(auto_restart_file, 'w', encoding='utf-8') as f:
                f.write(auto_restart_content)
                
    except Exception as e:
        print(f"Error creating example plugins: {e}") 
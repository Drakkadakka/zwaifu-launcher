#!/usr/bin/env python3
"""
Auto Restart Plugin
Automatically restarts processes that fail
"""

import threading
import time
import sys
import os

try:
    from utils.plugin_system import PluginBase
except ImportError:
    # Fallback if plugin system not available
    class PluginBase:
        def __init__(self, launcher_gui):
            self.launcher_gui = launcher_gui
            self.logger = launcher_gui.log if hasattr(launcher_gui, 'log') else print

class AutoRestartPlugin(PluginBase):
    def __init__(self, launcher_gui):
        super().__init__(launcher_gui)
        self.name = "Auto Restart"
        self.version = "1.0.0"
        self.description = "Automatically restarts processes that fail"
        self.author = "Z-Waifu Team"
        self.restart_counts = {}
    
    def initialize(self):
        self.config = {
            'max_restarts': 3,
            'restart_delay': 5,
            'restart_window': 300,
            'enabled_processes': ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']
        }
        return True
    
    def on_process_error(self, process_type, instance_id, error):
        if process_type not in self.config['enabled_processes']:
            return
        
        key = f"{process_type}_{instance_id}"
        current_time = time.time()
        
        if key not in self.restart_counts:
            self.restart_counts[key] = {'count': 0, 'last_restart': 0}
        
        restart_info = self.restart_counts[key]
        
        if current_time - restart_info['last_restart'] > self.config['restart_window']:
            restart_info['count'] = 0
        
        if restart_info['count'] < self.config['max_restarts']:
            restart_info['count'] += 1
            restart_info['last_restart'] = current_time
            
            self.logger.info(f"Auto-restarting {process_type} Instance {instance_id+1} (attempt {restart_info['count']})")
            
            threading.Timer(self.config['restart_delay'], 
                          lambda: self._restart_process(process_type, instance_id)).start()
        else:
            self.logger.error(f"Max restarts reached for {process_type} Instance {instance_id+1}")
    
    def _restart_process(self, process_type, instance_id):
        # Implementation for restarting process
        pass

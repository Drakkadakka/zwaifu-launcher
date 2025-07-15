#!/usr/bin/env python3
"""
Process Monitor Plugin
Monitors process performance and logs metrics
"""

import psutil
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

class ProcessMonitorPlugin(PluginBase):
    def __init__(self, launcher_gui):
        super().__init__(launcher_gui)
        self.name = "Process Monitor"
        self.version = "1.0.0"
        self.description = "Monitors process performance and logs metrics"
        self.author = "Z-Waifu Team"
        self.monitoring_thread = None
        self.monitoring_active = False
    
    def initialize(self):
        self.config = {
            'monitor_interval': 5,
            'log_metrics': True,
            'alert_threshold_cpu': 80,
            'alert_threshold_memory': 1024
        }
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
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        return super().disable()
    
    def _monitor_processes(self):
        while self.monitoring_active:
            try:
                if hasattr(self.launcher_gui, 'process_instance_tabs'):
                    for process_type, instances in self.launcher_gui.process_instance_tabs.items():
                        for i, instance_data in enumerate(instances):
                            proc = instance_data.get('proc')
                            if proc and proc.poll() is None:
                                try:
                                    p = psutil.Process(proc.pid)
                                    cpu_percent = p.cpu_percent(interval=0.1)
                                    memory_mb = p.memory_info().rss / (1024 * 1024)
                                    
                                    if cpu_percent > self.config['alert_threshold_cpu']:
                                        self.logger.warning(f"High CPU usage for {process_type} Instance {i+1}: {cpu_percent:.1f}%")
                                    
                                    if memory_mb > self.config['alert_threshold_memory']:
                                        self.logger.warning(f"High memory usage for {process_type} Instance {i+1}: {memory_mb:.1f} MB")
                                    
                                    if self.config['log_metrics']:
                                        self.logger.info(f"{process_type} Instance {i+1}: CPU {cpu_percent:.1f}%, Memory {memory_mb:.1f} MB")
                                        
                                except Exception as e:
                                    self.logger.error(f"Error monitoring {process_type} Instance {i+1}: {e}")
                
                time.sleep(self.config['monitor_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring: {e}")
                time.sleep(10)

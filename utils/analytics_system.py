#!/usr/bin/env python3
"""
Z-Waifu Launcher GUI - Advanced Analytics System
Detailed performance metrics and reporting system.
"""

import os
import sys
import json
import threading
import time
import subprocess
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64

# Add the parent directory to the path so we can import the launcher
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from zwaifu_launcher_gui import LauncherGUI, TerminalEmulator
except ImportError:
    print("Error: Could not import launcher modules")
    sys.exit(1)

class AnalyticsSystem:
    """Advanced analytics system for performance monitoring and reporting"""
    
    def __init__(self, launcher_gui: LauncherGUI):
        self.launcher_gui = launcher_gui
        self.db_path = os.path.join(os.path.dirname(__file__), 'analytics.db')
        self.logger = logging.getLogger('analytics')
        
        # Initialize database
        self.init_database()
        
        # Analytics configuration
        self.config = {
            'collect_interval': 5,  # seconds
            'retention_days': 30,
            'enable_charts': True,
            'enable_alerts': True,
            'alert_thresholds': {
                'cpu_percent': 80,
                'memory_percent': 80,
                'disk_percent': 90,
                'process_restarts': 5
            }
        }
        
        # Start data collection
        self.collection_active = True
        self.collection_thread = threading.Thread(target=self.collect_metrics, daemon=True)
        self.collection_thread.start()
        
        # Performance history
        self.performance_history = {
            'system': [],
            'processes': {},
            'events': []
        }
    
    def init_database(self):
        """Initialize SQLite database for analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_sent REAL,
                    network_recv REAL,
                    temperature REAL
                )
            ''')
            
            # Process metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS process_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    process_type TEXT,
                    instance_id INTEGER,
                    pid INTEGER,
                    cpu_percent REAL,
                    memory_mb REAL,
                    status TEXT,
                    uptime_seconds INTEGER
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    process_type TEXT,
                    instance_id INTEGER,
                    message TEXT,
                    severity TEXT
                )
            ''')
            
            # Performance reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    report_type TEXT,
                    data TEXT,
                    summary TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    def collect_metrics(self):
        """Collect system and process metrics"""
        while self.collection_active:
            try:
                timestamp = datetime.now()
                
                # Collect system metrics
                system_metrics = self.collect_system_metrics()
                self.store_system_metrics(system_metrics)
                
                # Collect process metrics
                process_metrics = self.collect_process_metrics()
                self.store_process_metrics(process_metrics)
                
                # Check for alerts
                if self.config['enable_alerts']:
                    self.check_alerts(system_metrics, process_metrics)
                
                # Update performance history
                self.update_performance_history(system_metrics, process_metrics)
                
                time.sleep(self.config['collect_interval'])
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                time.sleep(10)
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network usage
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent / (1024 * 1024)  # MB
            network_recv = network.bytes_recv / (1024 * 1024)  # MB
            
            # Temperature (if available)
            temperature = None
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            for entry in entries:
                                if entry.current > 0:
                                    temperature = entry.current
                                    break
                            if temperature:
                                break
            except Exception:
                pass
            
            return {
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_sent': network_sent,
                'network_recv': network_recv,
                'temperature': temperature
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {
                'timestamp': datetime.now(),
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'network_sent': 0,
                'network_recv': 0,
                'temperature': None
            }
    
    def collect_process_metrics(self) -> List[Dict[str, Any]]:
        """Collect process-level metrics"""
        try:
            metrics = []
            
            if hasattr(self.launcher_gui, 'process_instance_tabs'):
                process_tabs = self.launcher_gui.process_instance_tabs
                
                for process_type in ['Oobabooga', 'Z-Waifu', 'Ollama', 'RVC']:
                    if process_type in process_tabs:
                        instances = process_tabs[process_type]
                        
                        for i, instance_data in enumerate(instances):
                            proc = instance_data.get('proc')
                            terminal = instance_data.get('terminal')
                            
                            # Check if process is running
                            running = False
                            pid = None
                            cpu_percent = 0
                            memory_mb = 0
                            
                            if proc:
                                try:
                                    running = proc.poll() is None
                                    if running:
                                        pid = proc.pid
                                        process = psutil.Process(pid)
                                        cpu_percent = process.cpu_percent()
                                        memory_mb = process.memory_info().rss / (1024 * 1024)
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    pass
                            
                            # Get uptime
                            uptime_seconds = 0
                            if terminal and hasattr(terminal, 'start_time') and terminal.start_time:
                                uptime_seconds = time.time() - terminal.start_time
                            
                            metric = {
                                'timestamp': datetime.now(),
                                'process_type': process_type,
                                'instance_id': i + 1,
                                'pid': pid,
                                'cpu_percent': cpu_percent,
                                'memory_mb': memory_mb,
                                'status': 'running' if running else 'stopped',
                                'uptime_seconds': uptime_seconds
                            }
                            metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting process metrics: {e}")
            return []
    
    def store_system_metrics(self, metrics: Dict[str, Any]):
        """Store system metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv, temperature)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics['timestamp'],
                metrics['cpu_percent'],
                metrics['memory_percent'],
                metrics['disk_percent'],
                metrics['network_sent'],
                metrics['network_recv'],
                metrics['temperature']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing system metrics: {e}")
    
    def store_process_metrics(self, metrics: List[Dict[str, Any]]):
        """Store process metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for metric in metrics:
                cursor.execute('''
                    INSERT INTO process_metrics 
                    (timestamp, process_type, instance_id, pid, cpu_percent, memory_mb, status, uptime_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metric['timestamp'],
                    metric['process_type'],
                    metric['instance_id'],
                    metric['pid'],
                    metric['cpu_percent'],
                    metric['memory_mb'],
                    metric['status'],
                    metric['uptime_seconds']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing process metrics: {e}")
    
    def log_event(self, event_type: str, process_type: str = None, instance_id: int = None, 
                  message: str = "", severity: str = "info"):
        """Log an event to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (timestamp, event_type, process_type, instance_id, message, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), event_type, process_type, instance_id, message, severity))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
    
    def check_alerts(self, system_metrics: Dict[str, Any], process_metrics: List[Dict[str, Any]]):
        """Check for alert conditions"""
        try:
            thresholds = self.config['alert_thresholds']
            
            # System alerts
            if system_metrics['cpu_percent'] > thresholds['cpu_percent']:
                self.log_event('high_cpu', message=f"CPU usage: {system_metrics['cpu_percent']:.1f}%", severity='warning')
            
            if system_metrics['memory_percent'] > thresholds['memory_percent']:
                self.log_event('high_memory', message=f"Memory usage: {system_metrics['memory_percent']:.1f}%", severity='warning')
            
            if system_metrics['disk_percent'] > thresholds['disk_percent']:
                self.log_event('high_disk', message=f"Disk usage: {system_metrics['disk_percent']:.1f}%", severity='warning')
            
            # Process alerts
            for metric in process_metrics:
                if metric['status'] == 'stopped':
                    self.log_event('process_stopped', metric['process_type'], metric['instance_id'], 
                                 f"Process stopped unexpectedly", 'error')
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    def update_performance_history(self, system_metrics: Dict[str, Any], process_metrics: List[Dict[str, Any]]):
        """Update in-memory performance history"""
        try:
            # Update system history
            self.performance_history['system'].append(system_metrics)
            
            # Keep only last 1000 entries
            if len(self.performance_history['system']) > 1000:
                self.performance_history['system'] = self.performance_history['system'][-1000:]
            
            # Update process history
            for metric in process_metrics:
                process_key = f"{metric['process_type']}_{metric['instance_id']}"
                if process_key not in self.performance_history['processes']:
                    self.performance_history['processes'][process_key] = []
                
                self.performance_history['processes'][process_key].append(metric)
                
                # Keep only last 1000 entries per process
                if len(self.performance_history['processes'][process_key]) > 1000:
                    self.performance_history['processes'][process_key] = self.performance_history['processes'][process_key][-1000:]
            
        except Exception as e:
            self.logger.error(f"Error updating performance history: {e}")
    
    def get_system_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get system metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT timestamp, cpu_percent, memory_percent, disk_percent, network_sent, network_recv, temperature
                FROM system_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            conn.close()
            
            metrics = []
            for row in rows:
                metrics.append({
                    'timestamp': row[0],
                    'cpu_percent': row[1],
                    'memory_percent': row[2],
                    'disk_percent': row[3],
                    'network_sent': row[4],
                    'network_recv': row[5],
                    'temperature': row[6]
                })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return []
    
    def get_process_metrics(self, process_type: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get process metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            if process_type:
                cursor.execute('''
                    SELECT timestamp, process_type, instance_id, pid, cpu_percent, memory_mb, status, uptime_seconds
                    FROM process_metrics
                    WHERE timestamp >= ? AND process_type = ?
                    ORDER BY timestamp ASC
                ''', (cutoff_time, process_type))
            else:
                cursor.execute('''
                    SELECT timestamp, process_type, instance_id, pid, cpu_percent, memory_mb, status, uptime_seconds
                    FROM process_metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            conn.close()
            
            metrics = []
            for row in rows:
                metrics.append({
                    'timestamp': row[0],
                    'process_type': row[1],
                    'instance_id': row[2],
                    'pid': row[3],
                    'cpu_percent': row[4],
                    'memory_mb': row[5],
                    'status': row[6],
                    'uptime_seconds': row[7]
                })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting process metrics: {e}")
            return []
    
    def get_events(self, hours: int = 24, severity: str = None) -> List[Dict[str, Any]]:
        """Get events from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            if severity:
                cursor.execute('''
                    SELECT timestamp, event_type, process_type, instance_id, message, severity
                    FROM events
                    WHERE timestamp >= ? AND severity = ?
                    ORDER BY timestamp DESC
                ''', (cutoff_time, severity))
            else:
                cursor.execute('''
                    SELECT timestamp, event_type, process_type, instance_id, message, severity
                    FROM events
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                events.append({
                    'timestamp': row[0],
                    'event_type': row[1],
                    'process_type': row[2],
                    'instance_id': row[3],
                    'message': row[4],
                    'severity': row[5]
                })
            
            return events
            
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
            return []
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        try:
            system_metrics = self.get_system_metrics(hours)
            process_metrics = self.get_process_metrics(hours=hours)
            events = self.get_events(hours)
            
            # Calculate averages
            if system_metrics:
                avg_cpu = sum(m['cpu_percent'] for m in system_metrics) / len(system_metrics)
                avg_memory = sum(m['memory_percent'] for m in system_metrics) / len(system_metrics)
                avg_disk = sum(m['disk_percent'] for m in system_metrics) / len(system_metrics)
            else:
                avg_cpu = avg_memory = avg_disk = 0
            
            # Process statistics
            process_stats = {}
            for metric in process_metrics:
                process_key = f"{metric['process_type']}_{metric['instance_id']}"
                if process_key not in process_stats:
                    process_stats[process_key] = {
                        'process_type': metric['process_type'],
                        'instance_id': metric['instance_id'],
                        'avg_cpu': 0,
                        'avg_memory': 0,
                        'total_uptime': 0,
                        'restart_count': 0
                    }
                
                process_stats[process_key]['avg_cpu'] += metric['cpu_percent']
                process_stats[process_key]['avg_memory'] += metric['memory_mb']
                process_stats[process_key]['total_uptime'] += metric['uptime_seconds']
            
            # Calculate averages for processes
            for process_key in process_stats:
                count = len([m for m in process_metrics if f"{m['process_type']}_{m['instance_id']}" == process_key])
                if count > 0:
                    process_stats[process_key]['avg_cpu'] /= count
                    process_stats[process_key]['avg_memory'] /= count
            
            # Event statistics
            error_count = len([e for e in events if e['severity'] == 'error'])
            warning_count = len([e for e in events if e['severity'] == 'warning'])
            info_count = len([e for e in events if e['severity'] == 'info'])
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'period_hours': hours,
                'system_summary': {
                    'avg_cpu_percent': round(avg_cpu, 2),
                    'avg_memory_percent': round(avg_memory, 2),
                    'avg_disk_percent': round(avg_disk, 2),
                    'total_metrics_collected': len(system_metrics)
                },
                'process_summary': {
                    'total_processes': len(process_stats),
                    'process_details': list(process_stats.values())
                },
                'events_summary': {
                    'total_events': len(events),
                    'error_count': error_count,
                    'warning_count': warning_count,
                    'info_count': info_count
                },
                'recommendations': self.generate_recommendations(system_metrics, process_metrics, events)
            }
            
            # Store report
            self.store_performance_report(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    def generate_recommendations(self, system_metrics: List[Dict], process_metrics: List[Dict], 
                                events: List[Dict]) -> List[str]:
        """Generate recommendations based on metrics"""
        try:
            recommendations = []
            
            if system_metrics:
                # Check for high resource usage
                avg_cpu = sum(m['cpu_percent'] for m in system_metrics) / len(system_metrics)
                avg_memory = sum(m['memory_percent'] for m in system_metrics) / len(system_metrics)
                
                if avg_cpu > 70:
                    recommendations.append("Consider reducing CPU load or upgrading hardware")
                
                if avg_memory > 80:
                    recommendations.append("Consider increasing RAM or optimizing memory usage")
            
            # Check for frequent process restarts
            restart_events = [e for e in events if e['event_type'] == 'process_stopped']
            if len(restart_events) > 5:
                recommendations.append("High number of process restarts detected - check for stability issues")
            
            # Check for error events
            error_events = [e for e in events if e['severity'] == 'error']
            if error_events:
                recommendations.append(f"Found {len(error_events)} error events - review logs for issues")
            
            if not recommendations:
                recommendations.append("System performance appears to be within normal parameters")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations due to error"]
    
    def store_performance_report(self, report: Dict[str, Any]):
        """Store performance report in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_reports (timestamp, report_type, data, summary)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now(),
                'performance_report',
                json.dumps(report),
                f"Performance report for {report.get('period_hours', 24)} hours"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing performance report: {e}")
    
    def generate_chart(self, chart_type: str, hours: int = 24) -> str:
        """Generate a chart and return as base64 encoded image"""
        try:
            if not self.config['enable_charts']:
                return None
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'system':
                system_metrics = self.get_system_metrics(hours)
                if system_metrics:
                    timestamps = [datetime.fromisoformat(m['timestamp']) for m in system_metrics]
                    cpu_values = [m['cpu_percent'] for m in system_metrics]
                    memory_values = [m['memory_percent'] for m in system_metrics]
                    
                    plt.plot(timestamps, cpu_values, label='CPU %', linewidth=2)
                    plt.plot(timestamps, memory_values, label='Memory %', linewidth=2)
                    plt.title('System Performance Over Time')
                    plt.xlabel('Time')
                    plt.ylabel('Percentage')
                    plt.legend()
                    plt.grid(True, alpha=0.3)
                    
                    # Format x-axis
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=max(1, hours//6)))
                    plt.xticks(rotation=45)
            
            elif chart_type == 'process':
                process_metrics = self.get_process_metrics(hours=hours)
                if process_metrics:
                    # Group by process type
                    process_groups = {}
                    for metric in process_metrics:
                        key = metric['process_type']
                        if key not in process_groups:
                            process_groups[key] = []
                        process_groups[key].append(metric)
                    
                    for process_type, metrics in process_groups.items():
                        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
                        cpu_values = [m['cpu_percent'] for m in metrics]
                        plt.plot(timestamps, cpu_values, label=process_type, linewidth=2)
                    
                    plt.title('Process CPU Usage Over Time')
                    plt.xlabel('Time')
                    plt.ylabel('CPU %')
                    plt.legend()
                    plt.grid(True, alpha=0.3)
                    
                    # Format x-axis
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=max(1, hours//6)))
                    plt.xticks(rotation=45)
            
            # Save to bytes
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Convert to base64
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            self.logger.error(f"Error generating chart: {e}")
            return None
    
    def export_data(self, format_type: str = 'csv', hours: int = 24) -> str:
        """Export analytics data"""
        try:
            if format_type == 'csv':
                return self.export_to_csv(hours)
            elif format_type == 'json':
                return self.export_to_json(hours)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return None
    
    def export_to_csv(self, hours: int) -> str:
        """Export data to CSV format"""
        try:
            export_dir = os.path.join(os.path.dirname(__file__), 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(export_dir, f"analytics_export_{timestamp}.csv")
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write system metrics
                writer.writerow(['=== SYSTEM METRICS ==='])
                writer.writerow(['Timestamp', 'CPU %', 'Memory %', 'Disk %', 'Network Sent (MB)', 'Network Recv (MB)', 'Temperature'])
                
                system_metrics = self.get_system_metrics(hours)
                for metric in system_metrics:
                    writer.writerow([
                        metric['timestamp'],
                        metric['cpu_percent'],
                        metric['memory_percent'],
                        metric['disk_percent'],
                        metric['network_sent'],
                        metric['network_recv'],
                        metric['temperature'] or 'N/A'
                    ])
                
                writer.writerow([])
                
                # Write process metrics
                writer.writerow(['=== PROCESS METRICS ==='])
                writer.writerow(['Timestamp', 'Process Type', 'Instance ID', 'PID', 'CPU %', 'Memory (MB)', 'Status', 'Uptime (s)'])
                
                process_metrics = self.get_process_metrics(hours=hours)
                for metric in process_metrics:
                    writer.writerow([
                        metric['timestamp'],
                        metric['process_type'],
                        metric['instance_id'],
                        metric['pid'] or 'N/A',
                        metric['cpu_percent'],
                        metric['memory_mb'],
                        metric['status'],
                        metric['uptime_seconds']
                    ])
                
                writer.writerow([])
                
                # Write events
                writer.writerow(['=== EVENTS ==='])
                writer.writerow(['Timestamp', 'Event Type', 'Process Type', 'Instance ID', 'Message', 'Severity'])
                
                events = self.get_events(hours)
                for event in events:
                    writer.writerow([
                        event['timestamp'],
                        event['event_type'],
                        event['process_type'] or 'N/A',
                        event['instance_id'] or 'N/A',
                        event['message'],
                        event['severity']
                    ])
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return None
    
    def export_to_json(self, hours: int) -> str:
        """Export data to JSON format"""
        try:
            export_dir = os.path.join(os.path.dirname(__file__), 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(export_dir, f"analytics_export_{timestamp}.json")
            
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'period_hours': hours,
                'system_metrics': self.get_system_metrics(hours),
                'process_metrics': self.get_process_metrics(hours=hours),
                'events': self.get_events(hours),
                'performance_report': self.generate_performance_report(hours)
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, default=str)
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            return None
    
    def cleanup_old_data(self):
        """Clean up old data based on retention policy"""
        try:
            retention_days = self.config['retention_days']
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old system metrics
            cursor.execute('DELETE FROM system_metrics WHERE timestamp < ?', (cutoff_time,))
            
            # Delete old process metrics
            cursor.execute('DELETE FROM process_metrics WHERE timestamp < ?', (cutoff_time,))
            
            # Delete old events
            cursor.execute('DELETE FROM events WHERE timestamp < ?', (cutoff_time,))
            
            # Delete old performance reports
            cursor.execute('DELETE FROM performance_reports WHERE timestamp < ?', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleaned up data older than {retention_days} days")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a summary of analytics data"""
        try:
            # Get recent metrics
            system_metrics = self.get_system_metrics(1)  # Last hour
            process_metrics = self.get_process_metrics(hours=1)
            events = self.get_events(1)
            
            # Calculate current values
            current_cpu = system_metrics[-1]['cpu_percent'] if system_metrics else 0
            current_memory = system_metrics[-1]['memory_percent'] if system_metrics else 0
            current_disk = system_metrics[-1]['disk_percent'] if system_metrics else 0
            
            # Count running processes
            running_processes = len([m for m in process_metrics if m['status'] == 'running'])
            total_processes = len(process_metrics)
            
            # Count recent events
            error_events = len([e for e in events if e['severity'] == 'error'])
            warning_events = len([e for e in events if e['severity'] == 'warning'])
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': current_cpu,
                    'memory_percent': current_memory,
                    'disk_percent': current_disk
                },
                'processes': {
                    'running': running_processes,
                    'total': total_processes
                },
                'events': {
                    'errors_last_hour': error_events,
                    'warnings_last_hour': warning_events
                },
                'database': {
                    'system_metrics_count': len(self.get_system_metrics(24)),
                    'process_metrics_count': len(self.get_process_metrics(24)),
                    'events_count': len(self.get_events(24))
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting analytics summary: {e}")
            return {'error': str(e)}
    
    def stop(self):
        """Stop the analytics system"""
        try:
            self.collection_active = False
            if hasattr(self, 'collection_thread') and self.collection_thread.is_alive():
                self.collection_thread.join(timeout=5)
            
            # Clean up old data
            self.cleanup_old_data()
            
            self.logger.info("Analytics system stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping analytics system: {e}")

def create_analytics_system(launcher_gui: LauncherGUI) -> AnalyticsSystem:
    """Create and return an analytics system instance"""
    try:
        return AnalyticsSystem(launcher_gui)
    except Exception as e:
        print(f"Error creating analytics system: {e}")
        return None

if __name__ == "__main__":
    # Test analytics system
    print("Z-Waifu Launcher Analytics System")
    print("This module provides advanced performance metrics and reporting.")
    print("To use, import and call create_analytics_system() with your launcher instance.") 
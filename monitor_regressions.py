#!/usr/bin/env python3
"""
Regression Monitoring System for Z-Waifu Launcher GUI
"""

import os
import sys
import json
import time
import psutil
import threading
import subprocess
import datetime
import sqlite3
from pathlib import Path
from collections import defaultdict

class RegressionMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.monitor_db = self.project_root / "data" / "monitoring.db"
        self.monitor_log = self.project_root / "logs" / "monitoring.log"
        self.alert_log = self.project_root / "logs" / "alerts.log"
        
        # Ensure directories exist
        self.monitor_db.parent.mkdir(exist_ok=True)
        self.monitor_log.parent.mkdir(exist_ok=True)
        self.alert_log.parent.mkdir(exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Monitoring configuration
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Thresholds for alerts
        self.thresholds = {
            "memory_usage_mb": 500,  # Alert if memory usage > 500MB
            "cpu_usage_percent": 80,  # Alert if CPU usage > 80%
            "error_rate_percent": 5,  # Alert if error rate > 5%
            "response_time_ms": 2000,  # Alert if response time > 2s
            "process_count": 10,  # Alert if too many processes
        }
    
    def log(self, message, level="INFO"):
        """Log monitoring messages"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        with open(self.monitor_log, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def alert(self, message, severity="WARNING"):
        """Log alert messages"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"[{timestamp}] [{severity}] ALERT: {message}"
        print(f"🚨 {alert_message}")
        
        with open(self.alert_log, "a", encoding="utf-8") as f:
            f.write(alert_message + "\n")
    
    def init_database(self):
        """Initialize monitoring database"""
        try:
            conn = sqlite3.connect(self.monitor_db)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_usage_mb REAL,
                    disk_usage_percent REAL,
                    process_count INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS application_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    process_name TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    status TEXT,
                    uptime_seconds INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    error_type TEXT,
                    error_message TEXT,
                    stack_trace TEXT,
                    severity TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    duration_ms INTEGER,
                    success BOOLEAN,
                    details TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            self.log("Monitoring database initialized")
            
        except Exception as e:
            self.log(f"ERROR: Failed to initialize database: {e}", "ERROR")
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_usage_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Process count
            process_count = len(psutil.pids())
            
            # Store in database
            conn = sqlite3.connect(self.monitor_db)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, memory_usage_mb, disk_usage_percent, process_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (cpu_percent, memory_percent, memory_usage_mb, disk_usage_percent, process_count))
            conn.commit()
            conn.close()
            
            # Check thresholds
            if memory_usage_mb > self.thresholds["memory_usage_mb"]:
                self.alert(f"High memory usage: {memory_usage_mb:.1f}MB", "WARNING")
            
            if cpu_percent > self.thresholds["cpu_usage_percent"]:
                self.alert(f"High CPU usage: {cpu_percent:.1f}%", "WARNING")
            
            if process_count > self.thresholds["process_count"]:
                self.alert(f"High process count: {process_count}", "WARNING")
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_usage_mb": memory_usage_mb,
                "disk_usage_percent": disk_usage_percent,
                "process_count": process_count
            }
            
        except Exception as e:
            self.log(f"ERROR: Failed to collect system metrics: {e}", "ERROR")
            return None
    
    def collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # Look for Z-Waifu Launcher processes
            target_processes = ["python", "zwaifu_launcher_gui.py"]
            app_metrics = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any(target in ' '.join(proc.info['cmdline'] or []) for target in target_processes):
                        # Get process metrics
                        process = psutil.Process(proc.info['pid'])
                        cpu_percent = process.cpu_percent()
                        memory_percent = process.memory_percent()
                        
                        # Calculate uptime
                        create_time = process.create_time()
                        uptime_seconds = int(time.time() - create_time)
                        
                        # Determine status
                        status = "running" if process.is_running() else "stopped"
                        
                        app_metrics.append({
                            "process_name": proc.info['name'],
                            "cpu_percent": cpu_percent,
                            "memory_percent": memory_percent,
                            "status": status,
                            "uptime_seconds": uptime_seconds
                        })
                        
                        # Store in database
                        conn = sqlite3.connect(self.monitor_db)
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO application_metrics 
                            (process_name, cpu_percent, memory_percent, status, uptime_seconds)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (proc.info['name'], cpu_percent, memory_percent, status, uptime_seconds))
                        conn.commit()
                        conn.close()
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return app_metrics
            
        except Exception as e:
            self.log(f"ERROR: Failed to collect application metrics: {e}", "ERROR")
            return []
    
    def check_log_files(self):
        """Check log files for errors and warnings"""
        try:
            log_files = [
                self.project_root / "data" / "launcher_log.txt",
                self.project_root / "logs" / "deployment.log"
            ]
            
            error_patterns = [
                "ERROR", "Exception", "Traceback", "Failed", "Critical"
            ]
            
            for log_file in log_files:
                if log_file.exists():
                    with open(log_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        
                        # Check last 100 lines for errors
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        
                        for line in recent_lines:
                            if any(pattern in line for pattern in error_patterns):
                                # Store error in database
                                conn = sqlite3.connect(self.monitor_db)
                                cursor = conn.cursor()
                                cursor.execute('''
                                    INSERT INTO errors 
                                    (error_type, error_message, severity)
                                    VALUES (?, ?, ?)
                                ''', ("log_error", line.strip(), "WARNING"))
                                conn.commit()
                                conn.close()
                                
                                self.alert(f"Error detected in {log_file.name}: {line.strip()}", "WARNING")
            
        except Exception as e:
            self.log(f"ERROR: Failed to check log files: {e}", "ERROR")
    
    def monitor_performance(self):
        """Monitor application performance"""
        try:
            # Test application startup time
            start_time = time.time()
            
            # Simulate application operations
            test_operations = [
                ("config_loading", self.test_config_loading),
                ("theme_switching", self.test_theme_switching),
                ("process_management", self.test_process_management)
            ]
            
            for operation_name, test_func in test_operations:
                try:
                    op_start = time.time()
                    success = test_func()
                    duration_ms = int((time.time() - op_start) * 1000)
                    
                    # Store performance event
                    conn = sqlite3.connect(self.monitor_db)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO performance_events 
                        (event_type, duration_ms, success, details)
                        VALUES (?, ?, ?, ?)
                    ''', (operation_name, duration_ms, success, ""))
                    conn.commit()
                    conn.close()
                    
                    # Check response time threshold
                    if duration_ms > self.thresholds["response_time_ms"]:
                        self.alert(f"Slow {operation_name}: {duration_ms}ms", "WARNING")
                    
                except Exception as e:
                    self.log(f"ERROR: Performance test {operation_name} failed: {e}", "ERROR")
            
        except Exception as e:
            self.log(f"ERROR: Failed to monitor performance: {e}", "ERROR")
    
    def test_config_loading(self):
        """Test configuration loading performance"""
        try:
            config_file = self.project_root / "config" / "launcher_config.json"
            if config_file.exists():
                with open(config_file, "r") as f:
                    json.load(f)
            return True
        except Exception:
            return False
    
    def test_theme_switching(self):
        """Test theme switching performance"""
        try:
            # Simulate theme switching logic
            time.sleep(0.01)  # Simulate processing time
            return True
        except Exception:
            return False
    
    def test_process_management(self):
        """Test process management performance"""
        try:
            # Simulate process management operations
            time.sleep(0.01)  # Simulate processing time
            return True
        except Exception:
            return False
    
    def generate_report(self):
        """Generate monitoring report"""
        try:
            conn = sqlite3.connect(self.monitor_db)
            cursor = conn.cursor()
            
            # Get recent metrics
            cursor.execute('''
                SELECT * FROM system_metrics 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            system_metrics = cursor.fetchall()
            
            cursor.execute('''
                SELECT * FROM application_metrics 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            app_metrics = cursor.fetchall()
            
            cursor.execute('''
                SELECT * FROM errors 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            errors = cursor.fetchall()
            
            cursor.execute('''
                SELECT * FROM performance_events 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            performance_events = cursor.fetchall()
            
            conn.close()
            
            # Generate report
            report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "system_metrics": {
                    "recent_cpu_avg": sum(row[2] for row in system_metrics) / len(system_metrics) if system_metrics else 0,
                    "recent_memory_avg": sum(row[3] for row in system_metrics) / len(system_metrics) if system_metrics else 0,
                    "recent_memory_mb_avg": sum(row[4] for row in system_metrics) / len(system_metrics) if system_metrics else 0
                },
                "application_metrics": {
                    "active_processes": len([row for row in app_metrics if row[4] == "running"]),
                    "total_processes": len(app_metrics)
                },
                "errors": {
                    "recent_count": len(errors),
                    "recent_errors": [{"type": row[2], "message": row[3], "severity": row[5]} for row in errors]
                },
                "performance": {
                    "recent_events": len(performance_events),
                    "avg_response_time": sum(row[3] for row in performance_events) / len(performance_events) if performance_events else 0
                }
            }
            
            # Save report
            report_file = self.project_root / "reports" / f"monitoring_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            self.log(f"Monitoring report generated: {report_file}")
            return report
            
        except Exception as e:
            self.log(f"ERROR: Failed to generate report: {e}", "ERROR")
            return None
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        self.log("Starting monitoring loop...")
        
        while self.monitoring_active:
            try:
                # Collect metrics
                system_metrics = self.collect_system_metrics()
                app_metrics = self.collect_application_metrics()
                
                # Check logs
                self.check_log_files()
                
                # Monitor performance
                self.monitor_performance()
                
                # Log status
                if system_metrics:
                    self.log(f"System: CPU {system_metrics['cpu_percent']:.1f}%, "
                           f"Memory {system_metrics['memory_usage_mb']:.1f}MB, "
                           f"Processes {system_metrics['process_count']}")
                
                # Wait before next collection
                time.sleep(30)  # Collect metrics every 30 seconds
                
            except Exception as e:
                self.log(f"ERROR: Monitoring loop error: {e}", "ERROR")
                time.sleep(60)  # Wait longer on error
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            self.log("Monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        self.log("Monitoring stopped")

def main():
    """Main monitoring function"""
    monitor = RegressionMonitor()
    
    print("Z-Waifu Launcher GUI - Regression Monitoring")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            monitor.start_monitoring()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                monitor.stop_monitoring()
        elif sys.argv[1] == "report":
            report = monitor.generate_report()
            if report:
                print("Monitoring Report:")
                print(json.dumps(report, indent=2))
        elif sys.argv[1] == "test":
            print("Running monitoring tests...")
            monitor.collect_system_metrics()
            monitor.collect_application_metrics()
            monitor.check_log_files()
            monitor.monitor_performance()
            print("✅ Monitoring tests completed")
    else:
        print("Usage:")
        print("  python monitor_regressions.py start    - Start monitoring")
        print("  python monitor_regressions.py report   - Generate report")
        print("  python monitor_regressions.py test     - Run tests")

if __name__ == "__main__":
    main() 
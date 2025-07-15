"""
VRAM Monitoring System
Provides automatic VRAM usage monitoring, warnings, and cleanup functionality.
"""

import os
import sys
import time
import threading
import subprocess
import platform
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import json


class VRAMMonitor:
    """VRAM monitoring system with automatic cleanup and warnings"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.monitoring = False
        self.monitor_thread = None
        self.vram_callbacks = []
        self.last_vram_info = {}
        self.cleanup_history = []
        self.vram_history = []
        self.performance_data = []
        self.system_health_data = []
        self.last_notification_time = 0
        self.notification_cooldown = 300  # 5 minutes
        
        # Load VRAM settings
        self.vram_settings = self._load_vram_settings()
        
        # Initialize VRAM detection
        self.vram_sources = self._detect_vram_sources()
        
        # Initialize logging if enabled
        if self.vram_settings.get("enable_vram_logging", True):
            self._setup_logging()
        
        # Initialize performance tracking if enabled
        if self.vram_settings.get("enable_performance_tracking", True):
            self._setup_performance_tracking()
        
    def _load_vram_settings(self) -> Dict[str, Any]:
        """Load VRAM monitoring configuration"""
        default_settings = {
            "vram_monitoring_enabled": True,
            "vram_check_interval": 30,  # seconds
            "vram_warning_threshold": 0.8,  # 80%
            "vram_critical_threshold": 0.95,  # 95%
            "auto_cleanup_enabled": True,
            "auto_cleanup_threshold": 0.9,  # 90%
            "cleanup_after_process_stop": True,
            "show_vram_warnings": True,
            "vram_warning_sound": True,
            "cleanup_methods": ["cuda", "tensorflow", "gputil", "nvidia_smi"],
            "vram_history_size": 100,  # Number of VRAM readings to keep
            "enable_vram_logging": True,
            "vram_log_file": "vram_monitor.log",
            "enable_performance_tracking": True,
            "performance_tracking_interval": 60,  # seconds
            "enable_model_compatibility_checking": True,
            "model_vram_requirements": {},  # Cache for model VRAM requirements
            "enable_automatic_optimization": True,
            "optimization_threshold": 0.85,  # 85%
            "enable_system_health_monitoring": True,
            "health_check_interval": 300,  # 5 minutes
            "enable_resource_usage_tracking": True,
            "resource_tracking_interval": 120,  # 2 minutes
            "enable_predictive_cleanup": True,
            "predictive_cleanup_threshold": 0.75,  # 75%
            "enable_vram_analytics": True,
            "analytics_export_format": "json",  # json, csv, txt
            "enable_notification_system": True,
            "notification_cooldown": 300  # 5 minutes between notifications
        }
        
        if self.config_manager:
            try:
                config = self.config_manager.load_config()
                vram_config = config.get("vram_monitoring", {})
                # Merge with defaults, keeping user settings
                merged_settings = default_settings.copy()
                merged_settings.update(vram_config)
                return merged_settings
            except Exception as e:
                print(f"Failed to load VRAM settings: {e}")
        
        return default_settings
    
    def _detect_vram_sources(self) -> List[str]:
        """Detect available VRAM monitoring sources"""
        sources = []
        
        # Check CUDA (PyTorch)
        try:
            import torch
            if torch.cuda.is_available():
                sources.append("cuda")
        except ImportError:
            pass
        
        # Check TensorFlow
        try:
            import tensorflow as tf
            gpu_devices = tf.config.list_physical_devices('GPU')
            if gpu_devices:
                sources.append("tensorflow")
        except (ImportError, AttributeError):
            pass
        
        # Check GPUtil
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                sources.append("gputil")
        except (ImportError, AttributeError):
            pass
        
        # Check nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                sources.append("nvidia_smi")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return sources
    
    def _setup_logging(self):
        """Setup VRAM logging"""
        try:
            log_file = self.vram_settings.get("vram_log_file", "vram_monitor.log")
            log_path = os.path.join("logs", log_file)
            os.makedirs("logs", exist_ok=True)
            
            # Create a simple log handler
            import logging
            self.logger = logging.getLogger("vram_monitor")
            self.logger.setLevel(logging.INFO)
            
            # File handler
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.info("VRAM monitoring logging initialized")
            
        except Exception as e:
            print(f"Failed to setup VRAM logging: {e}")
    
    def _setup_performance_tracking(self):
        """Setup performance tracking"""
        try:
            self.performance_tracking_enabled = True
            self.last_performance_check = time.time()
        except Exception as e:
            print(f"Failed to setup performance tracking: {e}")
            self.performance_tracking_enabled = False
    
    def _log_vram_event(self, event_type: str, message: str, data: Dict[str, Any] = None):
        """Log VRAM events if logging is enabled"""
        if not self.vram_settings.get("enable_vram_logging", True):
            return
        
        try:
            if hasattr(self, 'logger'):
                log_message = f"[{event_type.upper()}] {message}"
                if data:
                    log_message += f" - Data: {data}"
                self.logger.info(log_message)
        except Exception as e:
            print(f"Failed to log VRAM event: {e}")
    
    def _add_to_vram_history(self, vram_info: Dict[str, Any]):
        """Add VRAM info to history"""
        self.vram_history.append(vram_info)
        
        # Keep history size within limits
        max_history = self.vram_settings.get("vram_history_size", 100)
        if len(self.vram_history) > max_history:
            self.vram_history.pop(0)
    
    def _check_performance_tracking(self):
        """Check if it's time for performance tracking"""
        if not self.performance_tracking_enabled:
            return
        
        current_time = time.time()
        interval = self.vram_settings.get("performance_tracking_interval", 60)
        
        if current_time - self.last_performance_check >= interval:
            self._track_performance()
            self.last_performance_check = current_time
    
    def _track_performance(self):
        """Track system performance metrics"""
        try:
            import psutil
            
            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "vram_info": self.last_vram_info.copy() if self.last_vram_info else {}
            }
            
            self.performance_data.append(performance_data)
            
            # Keep performance data within reasonable limits
            if len(self.performance_data) > 1000:
                self.performance_data = self.performance_data[-500:]
            
            self._log_vram_event("performance", "Performance tracking completed", performance_data)
            
        except Exception as e:
            print(f"Failed to track performance: {e}")
    
    def _check_system_health(self):
        """Check system health if enabled"""
        if not self.vram_settings.get("enable_system_health_monitoring", True):
            return
        
        try:
            import psutil
            
            # Calculate health score based on various factors
            health_score = 100
            
            # VRAM usage impact
            vram_usage = self.last_vram_info.get("vram_usage_percent", 0)
            if vram_usage > 90:
                health_score -= 30
            elif vram_usage > 80:
                health_score -= 15
            elif vram_usage > 70:
                health_score -= 5
            
            # CPU usage impact
            cpu_usage = psutil.cpu_percent(interval=0.1)
            if cpu_usage > 90:
                health_score -= 20
            elif cpu_usage > 80:
                health_score -= 10
            elif cpu_usage > 70:
                health_score -= 5
            
            # Memory usage impact
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > 90:
                health_score -= 20
            elif memory_usage > 80:
                health_score -= 10
            elif memory_usage > 70:
                health_score -= 5
            
            # Ensure score doesn't go below 0
            health_score = max(0, health_score)
            
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "health_score": health_score,
                "vram_usage": vram_usage,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "status": self._get_health_status(health_score)
            }
            
            self.system_health_data.append(health_data)
            
            # Keep health data within reasonable limits
            if len(self.system_health_data) > 500:
                self.system_health_data = self.system_health_data[-250:]
            
            self._log_vram_event("health", f"System health check: {health_score}/100", health_data)
            
            return health_data
            
        except Exception as e:
            print(f"Failed to check system health: {e}")
            return None
    
    def _get_health_status(self, score: int) -> str:
        """Get health status based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _check_predictive_cleanup(self, vram_info: Dict[str, Any]):
        """Check if predictive cleanup should be triggered"""
        if not self.vram_settings.get("enable_predictive_cleanup", True):
            return
        
        usage_percent = vram_info.get("vram_usage_percent", 0)
        threshold = self.vram_settings.get("predictive_cleanup_threshold", 0.75) * 100
        
        if usage_percent > threshold:
            # Check if VRAM usage is trending upward
            if len(self.vram_history) >= 3:
                recent_usage = [h.get("vram_usage_percent", 0) for h in self.vram_history[-3:]]
                if all(recent_usage[i] <= recent_usage[i+1] for i in range(len(recent_usage)-1)):
                    self._log_vram_event("predictive", f"Predictive cleanup triggered at {usage_percent:.1f}% usage")
                    self._handle_predictive_cleanup(usage_percent)
    
    def _handle_predictive_cleanup(self, usage_percent: float):
        """Handle predictive cleanup"""
        message = f"Predictive VRAM cleanup triggered at {usage_percent:.1f}% usage"
        print(f"[VRAM] {message}")
        
        # Perform gentle cleanup
        self._gentle_cleanup()
        
        # Trigger callbacks
        self._trigger_vram_callbacks({
            "type": "predictive_cleanup",
            "usage_percent": usage_percent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _gentle_cleanup(self) -> Dict[str, Any]:
        """Perform gentle cleanup without forcing GPU reset"""
        cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "type": "gentle_cleanup",
            "methods_successful": [],
            "methods_failed": [],
            "total_vram_freed_gb": 0
        }
        
        # Get VRAM before cleanup
        vram_before = self.get_vram_info()
        used_before = vram_before.get("used_vram_gb", 0)
        
        # Try gentle cleanup methods first
        gentle_methods = ["cuda", "tensorflow"]
        
        for method in gentle_methods:
            try:
                if method == "cuda":
                    success = self._cleanup_cuda()
                elif method == "tensorflow":
                    success = self._cleanup_tensorflow()
                else:
                    success = False
                
                if success:
                    cleanup_results["methods_successful"].append(method)
                else:
                    cleanup_results["methods_failed"].append(method)
                    
            except Exception as e:
                cleanup_results["methods_failed"].append(f"{method}: {e}")
        
        # Get VRAM after cleanup
        time.sleep(1)  # Give cleanup time to take effect
        vram_after = self.get_vram_info()
        used_after = vram_after.get("used_vram_gb", 0)
        
        cleanup_results["total_vram_freed_gb"] = max(0, used_before - used_after)
        cleanup_results["vram_before_gb"] = used_before
        cleanup_results["vram_after_gb"] = used_after
        
        self._log_vram_event("gentle_cleanup", f"Gentle cleanup completed: {cleanup_results['total_vram_freed_gb']:.2f}GB freed", cleanup_results)
        
        return cleanup_results
    
    def get_vram_info(self) -> Dict[str, Any]:
        """Get current VRAM information from the best available source"""
        vram_info = {
            "timestamp": datetime.now().isoformat(),
            "source": "none",
            "total_vram_gb": 0,
            "used_vram_gb": 0,
            "free_vram_gb": 0,
            "vram_usage_percent": 0,
            "available_sources": self.vram_sources
        }
        
        # Try sources in order of preference
        for source in self.vram_sources:
            try:
                if source == "cuda":
                    info = self._get_cuda_vram()
                elif source == "tensorflow":
                    info = self._get_tensorflow_vram()
                elif source == "gputil":
                    info = self._get_gputil_vram()
                elif source == "nvidia_smi":
                    info = self._get_nvidia_smi_vram()
                else:
                    continue
                
                if info and info.get("total_vram_gb", 0) > 0:
                    vram_info.update(info)
                    vram_info["source"] = source
                    break
                    
            except Exception as e:
                print(f"Error getting VRAM info from {source}: {e}")
                continue
        
        return vram_info
    
    def _get_cuda_vram(self) -> Optional[Dict[str, Any]]:
        """Get VRAM info using PyTorch CUDA"""
        try:
            import torch
            if not torch.cuda.is_available():
                return None
            
            device = torch.cuda.current_device()
            total_memory = torch.cuda.get_device_properties(device).total_memory
            allocated_memory = torch.cuda.memory_allocated(device)
            reserved_memory = torch.cuda.memory_reserved(device)
            
            total_gb = total_memory / (1024**3)
            used_gb = reserved_memory / (1024**3)
            free_gb = (total_memory - reserved_memory) / (1024**3)
            usage_percent = (reserved_memory / total_memory) * 100
            
            return {
                "total_vram_gb": total_gb,
                "used_vram_gb": used_gb,
                "free_vram_gb": free_gb,
                "vram_usage_percent": usage_percent,
                "allocated_memory_gb": allocated_memory / (1024**3),
                "reserved_memory_gb": reserved_memory / (1024**3)
            }
        except Exception as e:
            print(f"CUDA VRAM error: {e}")
            return None
    
    def _get_tensorflow_vram(self) -> Optional[Dict[str, Any]]:
        """Get VRAM info using TensorFlow"""
        try:
            import tensorflow as tf
            gpu_devices = tf.config.list_physical_devices('GPU')
            if not gpu_devices:
                return None
            
            # TensorFlow doesn't provide direct VRAM info, so we'll use nvidia-smi
            return self._get_nvidia_smi_vram()
        except (ImportError, AttributeError) as e:
            print(f"TensorFlow not available: {e}")
            return None
        except Exception as e:
            print(f"TensorFlow VRAM error: {e}")
            return None
    
    def _get_gputil_vram(self) -> Optional[Dict[str, Any]]:
        """Get VRAM info using GPUtil"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if not gpus:
                return None
            
            gpu = gpus[0]  # Use first GPU
            total_gb = gpu.memoryTotal / 1024
            used_gb = gpu.memoryUsed / 1024
            free_gb = gpu.memoryFree / 1024
            usage_percent = (gpu.memoryUsed / gpu.memoryTotal) * 100
            
            return {
                "total_vram_gb": total_gb,
                "used_vram_gb": used_gb,
                "free_vram_gb": free_gb,
                "vram_usage_percent": usage_percent,
                "gpu_name": gpu.name,
                "gpu_load": gpu.load * 100 if gpu.load else 0
            }
        except (ImportError, AttributeError) as e:
            print(f"GPUtil not available: {e}")
            return None
        except Exception as e:
            print(f"GPUtil VRAM error: {e}")
            return None
    
    def _get_nvidia_smi_vram(self) -> Optional[Dict[str, Any]]:
        """Get VRAM info using nvidia-smi"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free,name', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            lines = result.stdout.strip().split('\n')
            if not lines:
                return None
            
            # Parse first GPU info
            parts = lines[0].split(', ')
            if len(parts) >= 4:
                total_mb = int(parts[0])
                used_mb = int(parts[1])
                free_mb = int(parts[2])
                gpu_name = parts[3].strip()
                
                total_gb = total_mb / 1024
                used_gb = used_mb / 1024
                free_gb = free_mb / 1024
                usage_percent = (used_mb / total_mb) * 100
                
                return {
                    "total_vram_gb": total_gb,
                    "used_vram_gb": used_gb,
                    "free_vram_gb": free_gb,
                    "vram_usage_percent": usage_percent,
                    "gpu_name": gpu_name
                }
            
            return None
        except Exception as e:
            print(f"nvidia-smi VRAM error: {e}")
            return None
    
    def start_monitoring(self):
        """Start VRAM monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("VRAM monitoring started")
    
    def stop_monitoring(self):
        """Stop VRAM monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("VRAM monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                vram_info = self.get_vram_info()
                self.last_vram_info = vram_info
                
                # Add to history
                self._add_to_vram_history(vram_info)
                
                # Check thresholds and trigger warnings/cleanup
                self._check_thresholds(vram_info)
                
                # Check predictive cleanup
                self._check_predictive_cleanup(vram_info)
                
                # Check performance tracking
                self._check_performance_tracking()
                
                # Check system health
                self._check_system_health()
                
                # Trigger callbacks
                self._trigger_vram_callbacks(vram_info)
                
                # Log VRAM status if logging is enabled
                if self.vram_settings.get("enable_vram_logging", True):
                    self._log_vram_event("monitoring", f"VRAM usage: {vram_info.get('vram_usage_percent', 0):.1f}%", vram_info)
                
                # Wait for next check
                time.sleep(self.vram_settings.get("vram_check_interval", 30))
                
            except Exception as e:
                print(f"Error in VRAM monitoring loop: {e}")
                self._log_vram_event("error", f"Monitoring loop error: {e}")
                time.sleep(10)  # Wait a bit before retrying
    
    def _check_thresholds(self, vram_info: Dict[str, Any]):
        """Check VRAM usage against thresholds"""
        usage_percent = vram_info.get("vram_usage_percent", 0)
        
        # Check critical threshold
        critical_threshold = self.vram_settings.get("vram_critical_threshold", 0.95) * 100
        if usage_percent > critical_threshold:
            self._handle_critical_vram(usage_percent)
        
        # Check warning threshold
        warning_threshold = self.vram_settings.get("vram_warning_threshold", 0.8) * 100
        if usage_percent > warning_threshold:
            self._handle_vram_warning(usage_percent)
        
        # Check auto-cleanup threshold
        if self.vram_settings.get("auto_cleanup_enabled", True):
            cleanup_threshold = self.vram_settings.get("auto_cleanup_threshold", 0.9) * 100
            if usage_percent > cleanup_threshold:
                self._handle_auto_cleanup(usage_percent)
    
    def _handle_critical_vram(self, usage_percent: float):
        """Handle critical VRAM usage"""
        message = f"CRITICAL VRAM USAGE: {usage_percent:.1f}%"
        print(f"[VRAM] {message}")
        
        # Force cleanup
        self.force_cleanup()
        
        # Trigger callbacks
        self._trigger_vram_callbacks({
            "type": "critical",
            "usage_percent": usage_percent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _handle_vram_warning(self, usage_percent: float):
        """Handle VRAM warning"""
        if not self.vram_settings.get("show_vram_warnings", True):
            return
        
        message = f"High VRAM usage: {usage_percent:.1f}%"
        print(f"[VRAM] {message}")
        
        # Play warning sound if enabled
        if self.vram_settings.get("vram_warning_sound", True):
            self._play_warning_sound()
        
        # Trigger callbacks
        self._trigger_vram_callbacks({
            "type": "warning",
            "usage_percent": usage_percent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _handle_auto_cleanup(self, usage_percent: float):
        """Handle automatic VRAM cleanup"""
        message = f"Auto-cleanup triggered at {usage_percent:.1f}% VRAM usage"
        print(f"[VRAM] {message}")
        
        # Perform cleanup
        self.force_cleanup()
        
        # Trigger callbacks
        self._trigger_vram_callbacks({
            "type": "auto_cleanup",
            "usage_percent": usage_percent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _play_warning_sound(self):
        """Play warning sound"""
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(800, 200)
                time.sleep(0.1)
                winsound.Beep(1200, 200)
            else:
                # Use system beep on other platforms
                print('\a')
        except Exception:
            pass
    
    def force_cleanup(self) -> Dict[str, Any]:
        """Force VRAM cleanup using all available methods"""
        cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "methods_attempted": [],
            "methods_successful": [],
            "methods_failed": [],
            "total_vram_freed_gb": 0
        }
        
        # Get VRAM before cleanup
        vram_before = self.get_vram_info()
        used_before = vram_before.get("used_vram_gb", 0)
        
        # Try each cleanup method
        cleanup_methods = self.vram_settings.get("cleanup_methods", ["cuda", "tensorflow", "gputil", "nvidia_smi"])
        
        for method in cleanup_methods:
            cleanup_results["methods_attempted"].append(method)
            
            try:
                if method == "cuda":
                    success = self._cleanup_cuda()
                elif method == "tensorflow":
                    success = self._cleanup_tensorflow()
                elif method == "gputil":
                    success = self._cleanup_gputil()
                elif method == "nvidia_smi":
                    success = self._cleanup_nvidia_smi()
                else:
                    success = False
                
                if success:
                    cleanup_results["methods_successful"].append(method)
                else:
                    cleanup_results["methods_failed"].append(method)
                    
            except Exception as e:
                cleanup_results["methods_failed"].append(f"{method}: {e}")
        
        # Get VRAM after cleanup
        time.sleep(1)  # Give cleanup time to take effect
        vram_after = self.get_vram_info()
        used_after = vram_after.get("used_vram_gb", 0)
        
        cleanup_results["total_vram_freed_gb"] = max(0, used_before - used_after)
        cleanup_results["vram_before_gb"] = used_before
        cleanup_results["vram_after_gb"] = used_after
        
        # Store cleanup history
        self.cleanup_history.append(cleanup_results)
        if len(self.cleanup_history) > 10:  # Keep last 10 cleanups
            self.cleanup_history.pop(0)
        
        # Trigger callbacks
        self._trigger_vram_callbacks({
            "type": "cleanup",
            "results": cleanup_results,
            "timestamp": datetime.now().isoformat()
        })
        
        return cleanup_results
    
    def _cleanup_cuda(self) -> bool:
        """Cleanup CUDA memory"""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                return True
        except Exception as e:
            print(f"CUDA cleanup error: {e}")
        return False
    
    def _cleanup_tensorflow(self) -> bool:
        """Cleanup TensorFlow memory"""
        try:
            import tensorflow as tf
            tf.keras.backend.clear_session()
            return True
        except (ImportError, AttributeError) as e:
            print(f"TensorFlow not available for cleanup: {e}")
        except Exception as e:
            print(f"TensorFlow cleanup error: {e}")
        return False
    
    def _cleanup_gputil(self) -> bool:
        """Cleanup using GPUtil (limited functionality)"""
        try:
            import GPUtil
            # GPUtil doesn't provide direct cleanup, but we can reset the cache
            GPUtil.getGPUs()  # Refresh cache
            return True
        except (ImportError, AttributeError) as e:
            print(f"GPUtil not available for cleanup: {e}")
        except Exception as e:
            print(f"GPUtil cleanup error: {e}")
        return False
    
    def _cleanup_nvidia_smi(self) -> bool:
        """Cleanup using nvidia-smi"""
        try:
            # nvidia-smi doesn't provide direct cleanup, but we can reset the driver
            result = subprocess.run(['nvidia-smi', '--gpu-reset'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            print(f"nvidia-smi cleanup error: {e}")
        return False
    
    def cleanup_after_process_stop(self, process_name: str):
        """Cleanup VRAM after a process stops"""
        if not self.vram_settings.get("cleanup_after_process_stop", True):
            return
        
        print(f"[VRAM] Cleaning up after {process_name} process stop")
        self.force_cleanup()
    
    def _trigger_vram_callbacks(self, vram_info: Dict[str, Any]):
        """Trigger registered VRAM callbacks"""
        for callback in self.vram_callbacks:
            try:
                callback(vram_info)
            except Exception as e:
                print(f"Error in VRAM callback: {e}")
    
    def register_vram_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback function to be called when VRAM events occur"""
        self.vram_callbacks.append(callback)
    
    def get_vram_summary(self) -> Dict[str, Any]:
        """Get a summary of VRAM status"""
        vram_info = self.get_vram_info()
        
        return {
            "monitoring": self.monitoring,
            "available_sources": self.vram_sources,
            "current_source": vram_info.get("source", "none"),
            "total_vram_gb": vram_info.get("total_vram_gb", 0),
            "used_vram_gb": vram_info.get("used_vram_gb", 0),
            "free_vram_gb": vram_info.get("free_vram_gb", 0),
            "usage_percent": vram_info.get("vram_usage_percent", 0),
            "last_cleanup": self.cleanup_history[-1] if self.cleanup_history else None,
            "cleanup_count": len(self.cleanup_history)
        }
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update VRAM monitoring settings"""
        self.vram_settings.update(new_settings)
        
        # Save to config if config manager is available
        if self.config_manager:
            try:
                config = self.config_manager.load_config()
                config["vram_monitoring"] = self.vram_settings
                self.config_manager.save_config(config)
            except Exception as e:
                print(f"Failed to save VRAM settings: {e}")
    
    def get_vram_analytics(self) -> Dict[str, Any]:
        """Get comprehensive VRAM analytics"""
        if not self.vram_settings.get("enable_vram_analytics", True):
            return {"error": "VRAM analytics disabled"}
        
        try:
            analytics = {
                "timestamp": datetime.now().isoformat(),
                "summary": self._get_vram_summary_analytics(),
                "trends": self._get_vram_trends(),
                "performance": self._get_performance_analytics(),
                "health": self._get_health_analytics(),
                "cleanup_history": self._get_cleanup_analytics()
            }
            
            return analytics
            
        except Exception as e:
            return {"error": f"Failed to generate analytics: {e}"}
    
    def _get_vram_summary_analytics(self) -> Dict[str, Any]:
        """Get VRAM usage summary analytics"""
        if not self.vram_history:
            return {"error": "No VRAM history available"}
        
        usage_values = [h.get("vram_usage_percent", 0) for h in self.vram_history]
        
        return {
            "total_readings": len(self.vram_history),
            "average_usage": sum(usage_values) / len(usage_values),
            "max_usage": max(usage_values),
            "min_usage": min(usage_values),
            "current_usage": self.last_vram_info.get("vram_usage_percent", 0),
            "usage_trend": "increasing" if len(usage_values) >= 2 and usage_values[-1] > usage_values[-2] else "decreasing"
        }
    
    def _get_vram_trends(self) -> Dict[str, Any]:
        """Get VRAM usage trends"""
        if len(self.vram_history) < 10:
            return {"error": "Insufficient data for trend analysis"}
        
        recent_usage = [h.get("vram_usage_percent", 0) for h in self.vram_history[-10:]]
        
        # Calculate trend
        if len(recent_usage) >= 2:
            trend = "stable"
            if recent_usage[-1] > recent_usage[0] + 5:
                trend = "increasing"
            elif recent_usage[-1] < recent_usage[0] - 5:
                trend = "decreasing"
        else:
            trend = "unknown"
        
        return {
            "trend": trend,
            "recent_values": recent_usage,
            "trend_strength": abs(recent_usage[-1] - recent_usage[0]) if len(recent_usage) >= 2 else 0
        }
    
    def _get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics"""
        if not self.performance_data:
            return {"error": "No performance data available"}
        
        cpu_values = [p.get("cpu_percent", 0) for p in self.performance_data]
        memory_values = [p.get("memory_percent", 0) for p in self.performance_data]
        
        return {
            "total_performance_readings": len(self.performance_data),
            "average_cpu": sum(cpu_values) / len(cpu_values),
            "average_memory": sum(memory_values) / len(memory_values),
            "max_cpu": max(cpu_values),
            "max_memory": max(memory_values),
            "performance_trend": "stable"  # Could be enhanced with more analysis
        }
    
    def _get_health_analytics(self) -> Dict[str, Any]:
        """Get system health analytics"""
        if not self.system_health_data:
            return {"error": "No health data available"}
        
        health_scores = [h.get("health_score", 0) for h in self.system_health_data]
        
        return {
            "total_health_readings": len(self.system_health_data),
            "average_health_score": sum(health_scores) / len(health_scores),
            "current_health_score": health_scores[-1] if health_scores else 0,
            "health_trend": "stable",  # Could be enhanced with more analysis
            "health_status": self._get_health_status(health_scores[-1] if health_scores else 0)
        }
    
    def _get_cleanup_analytics(self) -> Dict[str, Any]:
        """Get cleanup history analytics"""
        if not self.cleanup_history:
            return {"error": "No cleanup history available"}
        
        total_freed = sum(c.get("total_vram_freed_gb", 0) for c in self.cleanup_history)
        successful_cleanups = len([c for c in self.cleanup_history if c.get("methods_successful")])
        
        return {
            "total_cleanups": len(self.cleanup_history),
            "successful_cleanups": successful_cleanups,
            "total_vram_freed_gb": total_freed,
            "average_vram_freed_per_cleanup": total_freed / len(self.cleanup_history) if self.cleanup_history else 0,
            "last_cleanup": self.cleanup_history[-1] if self.cleanup_history else None
        }
    
    def export_vram_data(self, format_type: str = "json", file_path: str = None) -> str:
        """Export VRAM data in specified format"""
        if not self.vram_settings.get("enable_vram_analytics", True):
            return "VRAM analytics disabled"
        
        try:
            if not file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"vram_export_{timestamp}.{format_type}"
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "vram_history": self.vram_history,
                "performance_data": self.performance_data,
                "system_health_data": self.system_health_data,
                "cleanup_history": self.cleanup_history,
                "analytics": self.get_vram_analytics()
            }
            
            if format_type.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
            elif format_type.lower() == "csv":
                self._export_to_csv(export_data, file_path)
            elif format_type.lower() == "txt":
                self._export_to_txt(export_data, file_path)
            else:
                return f"Unsupported format: {format_type}"
            
            self._log_vram_event("export", f"VRAM data exported to {file_path}")
            return f"Data exported successfully to {file_path}"
            
        except Exception as e:
            error_msg = f"Failed to export VRAM data: {e}"
            self._log_vram_event("error", error_msg)
            return error_msg
    
    def _export_to_csv(self, data: Dict[str, Any], file_path: str):
        """Export data to CSV format"""
        import csv
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write VRAM history
            if data.get("vram_history"):
                writer.writerow(["VRAM History"])
                writer.writerow(["Timestamp", "Source", "Total VRAM (GB)", "Used VRAM (GB)", "Free VRAM (GB)", "Usage %"])
                for entry in data["vram_history"]:
                    writer.writerow([
                        entry.get("timestamp", ""),
                        entry.get("source", ""),
                        entry.get("total_vram_gb", 0),
                        entry.get("used_vram_gb", 0),
                        entry.get("free_vram_gb", 0),
                        entry.get("vram_usage_percent", 0)
                    ])
                writer.writerow([])
            
            # Write performance data
            if data.get("performance_data"):
                writer.writerow(["Performance Data"])
                writer.writerow(["Timestamp", "CPU %", "Memory %", "Disk %"])
                for entry in data["performance_data"]:
                    writer.writerow([
                        entry.get("timestamp", ""),
                        entry.get("cpu_percent", 0),
                        entry.get("memory_percent", 0),
                        entry.get("disk_percent", 0)
                    ])
    
    def _export_to_txt(self, data: Dict[str, Any], file_path: str):
        """Export data to text format"""
        with open(file_path, 'w') as f:
            f.write("VRAM Monitoring Data Export\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Export Time: {data.get('export_timestamp', 'Unknown')}\n\n")
            
            # Summary
            analytics = data.get("analytics", {})
            if "summary" in analytics:
                summary = analytics["summary"]
                f.write("VRAM Summary:\n")
                f.write(f"  Total Readings: {summary.get('total_readings', 0)}\n")
                f.write(f"  Average Usage: {summary.get('average_usage', 0):.1f}%\n")
                f.write(f"  Max Usage: {summary.get('max_usage', 0):.1f}%\n")
                f.write(f"  Current Usage: {summary.get('current_usage', 0):.1f}%\n\n")
            
            # Cleanup history
            if data.get("cleanup_history"):
                f.write("Cleanup History:\n")
                for i, cleanup in enumerate(data["cleanup_history"], 1):
                    f.write(f"  {i}. {cleanup.get('timestamp', 'Unknown')} - {cleanup.get('total_vram_freed_gb', 0):.2f}GB freed\n")
                f.write("\n")
    
    def get_model_compatibility(self, model_name: str, model_size_gb: float = None) -> Dict[str, Any]:
        """Check if a model is compatible with current VRAM"""
        if not self.vram_settings.get("enable_model_compatibility_checking", True):
            return {"error": "Model compatibility checking disabled"}
        
        try:
            current_vram = self.last_vram_info.get("free_vram_gb", 0)
            
            # Estimate VRAM requirement if not provided
            if model_size_gb is None:
                # Rough estimation based on model name patterns
                if "7b" in model_name.lower() or "7b" in model_name:
                    model_size_gb = 7
                elif "13b" in model_name.lower() or "13b" in model_name:
                    model_size_gb = 13
                elif "30b" in model_name.lower() or "30b" in model_name:
                    model_size_gb = 30
                elif "70b" in model_name.lower() or "70b" in model_name:
                    model_size_gb = 70
                else:
                    model_size_gb = 7  # Default assumption
            
            # Add buffer for model loading
            required_vram = model_size_gb * 1.2  # 20% buffer
            
            compatible = current_vram >= required_vram
            safety_margin = current_vram - required_vram
            
            result = {
                "model_name": model_name,
                "estimated_size_gb": model_size_gb,
                "required_vram_gb": required_vram,
                "available_vram_gb": current_vram,
                "compatible": compatible,
                "safety_margin_gb": safety_margin,
                "recommendation": "Compatible" if compatible else "Insufficient VRAM"
            }
            
            # Cache the result
            self.vram_settings["model_vram_requirements"][model_name] = result
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to check model compatibility: {e}"}
    
    def optimize_vram_usage(self) -> Dict[str, Any]:
        """Optimize VRAM usage based on current conditions"""
        if not self.vram_settings.get("enable_automatic_optimization", True):
            return {"error": "Automatic optimization disabled"}
        
        try:
            current_usage = self.last_vram_info.get("vram_usage_percent", 0)
            threshold = self.vram_settings.get("optimization_threshold", 0.85) * 100
            
            if current_usage > threshold:
                # Perform optimization
                optimization_result = self._gentle_cleanup()
                optimization_result["optimization_triggered"] = True
                optimization_result["reason"] = f"Usage {current_usage:.1f}% exceeded threshold {threshold:.1f}%"
                return optimization_result
            else:
                return {
                    "optimization_triggered": False,
                    "reason": f"Usage {current_usage:.1f}% below threshold {threshold:.1f}%",
                    "current_usage": current_usage,
                    "threshold": threshold
                }
                
        except Exception as e:
            return {"error": f"Failed to optimize VRAM usage: {e}"}


# Global VRAM monitor instance
_vram_monitor = None

def get_vram_monitor() -> VRAMMonitor:
    """Get the global VRAM monitor instance"""
    global _vram_monitor
    if _vram_monitor is None:
        _vram_monitor = VRAMMonitor()
    return _vram_monitor

def setup_vram_monitor(config_manager=None) -> VRAMMonitor:
    """Setup and return the global VRAM monitor"""
    global _vram_monitor
    _vram_monitor = VRAMMonitor(config_manager)
    return _vram_monitor 
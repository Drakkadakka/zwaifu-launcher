"""
Configuration Manager Module
Handles configuration loading, saving, and validation
"""

import os
import json
import shutil
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime


class ConfigManager:
    """Manages launcher configuration with validation and backup"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_dir = os.path.dirname(config_file)
        self.backup_dir = os.path.join(self.config_dir, "backups")
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Default configuration
        self.default_config = {
            "ooba_bat": "",
            "zwaifu_bat": "",
            "ollama_bat": "",
            "rvc_bat": "",
            "ooba_port": 7860,
            "zwaifu_port": 5000,
            "ollama_port": 11434,
            "rvc_port": 6842,
            "theme": "dark",
            "auto_start": False,
            "web_interface": {
                "enabled": True,
                "port": 8080,
                "auto_start": False
            },
            "api_server": {
                "enabled": False,
                "port": 8081,
                "auto_start": False
            },
            "mobile_app": {
                "enabled": False,
                "port": 8082,
                "auto_start": False
            },
            "analytics": {
                "enabled": True,
                "auto_start": False
            },
            "plugins": {
                "enabled": True,
                "auto_load": True
            },
            "error_handling": {
                "error_reporting_verbosity": "detailed",
                "show_error_dialogs": True,
                "auto_copy_to_clipboard": False,
                "include_stack_traces": True,
                "error_dialog_timeout": 30,
                "enable_error_logging": True,
                "error_log_file": "error_handler.log",
                "max_error_history": 100,
                "enable_error_analytics": True,
                "error_notification_cooldown": 300
            },
            "vram_monitoring": {
                "vram_monitoring_enabled": True,
                "vram_check_interval": 30,
                "vram_warning_threshold": 0.8,
                "vram_critical_threshold": 0.95,
                "auto_cleanup_enabled": True,
                "auto_cleanup_threshold": 0.9,
                "cleanup_after_process_stop": True,
                "show_vram_warnings": True,
                "vram_warning_sound": True,
                "cleanup_methods": ["cuda", "tensorflow", "gputil", "nvidia_smi"],
                "vram_history_size": 100,
                "enable_vram_logging": True,
                "vram_log_file": "vram_monitor.log",
                "enable_performance_tracking": True,
                "performance_tracking_interval": 60,
                "enable_model_compatibility_checking": True,
                "model_vram_requirements": {},
                "enable_automatic_optimization": True,
                "optimization_threshold": 0.85,
                "enable_system_health_monitoring": True,
                "health_check_interval": 300,
                "enable_resource_usage_tracking": True,
                "resource_tracking_interval": 120,
                "enable_predictive_cleanup": True,
                "predictive_cleanup_threshold": 0.75,
                "enable_vram_analytics": True,
                "analytics_export_format": "json",
                "enable_notification_system": True,
                "notification_cooldown": 300
            }
        }

    def load_config(self) -> Dict[str, Any]:
        """Load configuration with validation and fallback"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Validate and merge with defaults
                validated_config = self._validate_config_data(config_data)
                return validated_config
            else:
                # Create default config if file doesn't exist
                return self._set_default_config()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._set_default_config()

    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration with backup"""
        try:
            # Create backup before saving
            self._create_backup()
            
            # Validate before saving
            validated_config = self._validate_config_data(config_data)
            
            # Save to file
            with open(self.config_file, "w", encoding='utf-8') as f:
                json.dump(validated_config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _validate_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize configuration data"""
        try:
            if not isinstance(config_data, dict):
                return self._set_default_config()
            
            # Start with default config
            validated = self.default_config.copy()
            
            # Merge with provided data, validating each field
            for key, value in config_data.items():
                if key in validated:
                    if key.endswith('_bat'):
                        # Validate batch file paths
                        if isinstance(value, str) and self._is_safe_path_enhanced(value):
                            validated[key] = value
                    elif key.endswith('_port'):
                        # Validate port numbers
                        if isinstance(value, (int, str)) and self._is_valid_port(str(value)):
                            validated[key] = int(value)
                    elif key == 'theme':
                        # Validate theme
                        if isinstance(value, str) and value in ['dark', 'light']:
                            validated[key] = value
                    elif key == 'auto_start':
                        # Validate boolean
                        if isinstance(value, bool):
                            validated[key] = value
                    elif key in ['error_handling', 'vram_monitoring']:
                        # Validate specialized configurations
                        if isinstance(value, dict) and key in validated:
                            validated[key] = self._validate_nested_config(validated[key], value)
                    elif isinstance(value, dict) and key in validated:
                        # Validate nested configurations
                        validated[key] = self._validate_nested_config(validated[key], value)
            
            return validated
        except Exception as e:
            print(f"Error validating config data: {e}")
            return self._set_default_config()

    def _validate_nested_config(self, default: Dict[str, Any], provided: Dict[str, Any]) -> Dict[str, Any]:
        """Validate nested configuration objects"""
        try:
            validated = default.copy()
            
            for key, value in provided.items():
                if key in validated:
                    if isinstance(value, bool):
                        validated[key] = value
                    elif isinstance(value, int):
                        # Validate integer values
                        if key.endswith('_port') or key.endswith('_interval') or key.endswith('_timeout') or key.endswith('_cooldown'):
                            if self._is_valid_port(str(value)) or value > 0:
                                validated[key] = value
                        elif key.endswith('_size') or key.endswith('_count'):
                            if value >= 0:
                                validated[key] = value
                    elif isinstance(value, (int, float)) and key.endswith('_threshold'):
                        # Validate threshold values (0.0 to 1.0)
                        if 0.0 <= value <= 1.0:
                            validated[key] = value
                    elif isinstance(value, str):
                        # Validate string values
                        if key == 'error_reporting_verbosity' and value in ['minimal', 'basic', 'detailed', 'verbose']:
                            validated[key] = value
                        elif key == 'analytics_export_format' and value in ['json', 'csv', 'txt']:
                            validated[key] = value
                        elif key.endswith('_file') or key.endswith('_log'):
                            # Validate file paths
                            if self._is_safe_path_enhanced(value):
                                validated[key] = value
                        else:
                            validated[key] = value
                    elif isinstance(value, list) and key == 'cleanup_methods':
                        # Validate cleanup methods list
                        valid_methods = ['cuda', 'tensorflow', 'gputil', 'nvidia_smi']
                        if all(method in valid_methods for method in value):
                            validated[key] = value
                    elif isinstance(value, dict):
                        validated[key] = self._validate_nested_config(validated[key], value)
            
            return validated
        except Exception as e:
            print(f"Error validating nested config: {e}")
            return default.copy()

    def _is_safe_path_enhanced(self, path: str) -> bool:
        """Enhanced path safety validation"""
        try:
            if not path or not isinstance(path, str):
                return False
            
            # Normalize path
            try:
                normalized_path = os.path.normpath(path)
            except Exception:
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = [
                '..', '//', '\\', ':', '*', '?', '"', '<', '>', '|',
                'cmd.exe', 'powershell.exe', 'bash.exe', 'sh.exe'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in normalized_path.lower():
                    return False
            
            # Check if path is within project directory
            project_root = os.path.dirname(os.path.dirname(self.config_file))
            try:
                abs_path = os.path.abspath(normalized_path)
                if not abs_path.startswith(project_root):
                    return False
            except Exception:
                return False
            
            return True
        except Exception as e:
            print(f"Error checking path safety: {e}")
            return False

    def _is_valid_port(self, port_str: str) -> bool:
        """Validate port number"""
        try:
            port = int(port_str)
            return 1 <= port <= 65535
        except (ValueError, TypeError):
            return False

    def _set_default_config(self) -> Dict[str, Any]:
        """Set and save default configuration"""
        try:
            config = self.default_config.copy()
            self.save_config(config)
            return config
        except Exception as e:
            print(f"Error setting default config: {e}")
            return self.default_config.copy()

    def _create_backup(self) -> None:
        """Create a backup of the current configuration"""
        try:
            if os.path.exists(self.config_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.backup_dir, f"config_backup_{timestamp}.json")
                
                try:
                    shutil.copy2(self.config_file, backup_file)
                    
                    # Clean up old backups
                    self._cleanup_old_backups()
                    
                except Exception as e:
                    print(f"Error creating backup: {e}")
        except Exception as e:
            print(f"Error in backup creation: {e}")

    def _cleanup_old_backups(self, keep_count: int = 5) -> None:
        """Clean up old backup files, keeping only the most recent ones"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("config_backup_") and filename.endswith(".json"):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for filepath, _ in backup_files[keep_count:]:
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error removing old backup {filepath}: {e}")
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")

    def get_batch_paths(self) -> Tuple[str, str, str, str]:
        """Get batch file paths from configuration"""
        try:
            config = self.load_config()
            return (
                config.get("ooba_bat", ""),
                config.get("zwaifu_bat", ""),
                config.get("ollama_bat", ""),
                config.get("rvc_bat", "")
            )
        except Exception as e:
            print(f"Error getting batch paths: {e}")
            return ("", "", "", "")

    def get_ports(self) -> Tuple[int, int, int, int]:
        """Get port numbers from configuration"""
        try:
            config = self.load_config()
            return (
                config.get("ooba_port", 7860),
                config.get("zwaifu_port", 5000),
                config.get("ollama_port", 11434),
                config.get("rvc_port", 6842)
            )
        except Exception as e:
            print(f"Error getting ports: {e}")
            return (7860, 5000, 11434, 6842)

    def update_batch_path(self, key: str, path: str) -> bool:
        """Update a batch file path in configuration"""
        try:
            config = self.load_config()
            if key in config and self._is_safe_path_enhanced(path):
                config[key] = path
                return self.save_config(config)
            return False
        except Exception as e:
            print(f"Error updating batch path: {e}")
            return False

    def update_port(self, key: str, port: int) -> bool:
        """Update a port number in configuration"""
        try:
            config = self.load_config()
            if key in config and self._is_valid_port(str(port)):
                config[key] = port
                return self.save_config(config)
            return False
        except Exception as e:
            print(f"Error updating port: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            return self.save_config(self.default_config.copy())
        except Exception as e:
            print(f"Error resetting to defaults: {e}")
            return False

    def get_web_interface_config(self) -> Dict[str, Any]:
        """Get web interface configuration"""
        try:
            config = self.load_config()
            return config.get("web_interface", self.default_config["web_interface"])
        except Exception as e:
            print(f"Error getting web interface config: {e}")
            return self.default_config["web_interface"].copy()

    def get_api_server_config(self) -> Dict[str, Any]:
        """Get API server configuration"""
        try:
            config = self.load_config()
            return config.get("api_server", self.default_config["api_server"])
        except Exception as e:
            print(f"Error getting API server config: {e}")
            return self.default_config["api_server"].copy()

    def get_mobile_app_config(self) -> Dict[str, Any]:
        """Get mobile app configuration"""
        try:
            config = self.load_config()
            return config.get("mobile_app", self.default_config["mobile_app"])
        except Exception as e:
            print(f"Error getting mobile app config: {e}")
            return self.default_config["mobile_app"].copy()

    def get_analytics_config(self) -> Dict[str, Any]:
        """Get analytics configuration"""
        try:
            config = self.load_config()
            return config.get("analytics", self.default_config["analytics"])
        except Exception as e:
            print(f"Error getting analytics config: {e}")
            return self.default_config["analytics"].copy()

    def get_plugins_config(self) -> Dict[str, Any]:
        """Get plugins configuration"""
        try:
            config = self.load_config()
            return config.get("plugins", self.default_config["plugins"])
        except Exception as e:
            print(f"Error getting plugins config: {e}")
            return self.default_config["plugins"].copy()

    def update_web_interface_config(self, web_config: Dict[str, Any]) -> bool:
        """Update web interface configuration"""
        try:
            config = self.load_config()
            config["web_interface"] = self._validate_nested_config(
                self.default_config["web_interface"], web_config
            )
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating web interface config: {e}")
            return False

    def update_api_server_config(self, api_config: Dict[str, Any]) -> bool:
        """Update API server configuration"""
        try:
            config = self.load_config()
            config["api_server"] = self._validate_nested_config(
                self.default_config["api_server"], api_config
            )
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating API server config: {e}")
            return False

    def update_mobile_app_config(self, mobile_config: Dict[str, Any]) -> bool:
        """Update mobile app configuration"""
        try:
            config = self.load_config()
            config["mobile_app"] = self._validate_nested_config(
                self.default_config["mobile_app"], mobile_config
            )
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating mobile app config: {e}")
            return False

    def update_analytics_config(self, analytics_config: Dict[str, Any]) -> bool:
        """Update analytics configuration"""
        try:
            config = self.load_config()
            config["analytics"] = self._validate_nested_config(
                self.default_config["analytics"], analytics_config
            )
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating analytics config: {e}")
            return False

    def update_plugins_config(self, plugins_config: Dict[str, Any]) -> bool:
        """Update plugins configuration"""
        try:
            config = self.load_config()
            config["plugins"] = self._validate_nested_config(
                self.default_config["plugins"], plugins_config
            )
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating plugins config: {e}")
            return False

    def get_error_handling_config(self) -> Dict[str, Any]:
        """Get error handling configuration"""
        try:
            config = self.load_config()
            return config.get("error_handling", self.default_config["error_handling"])
        except Exception as e:
            print(f"Error getting error handling config: {e}")
            return self.default_config["error_handling"].copy()

    def get_vram_monitoring_config(self) -> Dict[str, Any]:
        """Get VRAM monitoring configuration"""
        try:
            config = self.load_config()
            return config.get("vram_monitoring", self.default_config["vram_monitoring"])
        except Exception as e:
            print(f"Error getting VRAM monitoring config: {e}")
            return self.default_config["vram_monitoring"].copy()

    def update_error_handling_config(self, error_config: Dict[str, Any]) -> bool:
        """Update error handling configuration"""
        try:
            config = self.load_config()
            config["error_handling"] = self._validate_nested_config(
                self.default_config["error_handling"], error_config
            )
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating error handling config: {e}")
            return False

    def update_vram_monitoring_config(self, vram_config: Dict[str, Any]) -> bool:
        """Update VRAM monitoring configuration"""
        try:
            config = self.load_config()
            config["vram_monitoring"] = self._validate_nested_config(
                self.default_config["vram_monitoring"], vram_config
            )
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating VRAM monitoring config: {e}")
            return False

    def get_all_config_sections(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration sections"""
        try:
            config = self.load_config()
            return {
                "basic": {
                    "ooba_bat": config.get("ooba_bat", ""),
                    "zwaifu_bat": config.get("zwaifu_bat", ""),
                    "ollama_bat": config.get("ollama_bat", ""),
                    "rvc_bat": config.get("rvc_bat", ""),
                    "ooba_port": config.get("ooba_port", 7860),
                    "zwaifu_port": config.get("zwaifu_port", 5000),
                    "ollama_port": config.get("ollama_port", 11434),
                    "rvc_port": config.get("rvc_port", 6842),
                    "theme": config.get("theme", "dark"),
                    "auto_start": config.get("auto_start", False)
                },
                "web_interface": config.get("web_interface", self.default_config["web_interface"]),
                "api_server": config.get("api_server", self.default_config["api_server"]),
                "mobile_app": config.get("mobile_app", self.default_config["mobile_app"]),
                "analytics": config.get("analytics", self.default_config["analytics"]),
                "plugins": config.get("plugins", self.default_config["plugins"]),
                "error_handling": config.get("error_handling", self.default_config["error_handling"]),
                "vram_monitoring": config.get("vram_monitoring", self.default_config["vram_monitoring"])
            }
        except Exception as e:
            print(f"Error getting all config sections: {e}")
            return {
                "basic": self.default_config.copy(),
                "web_interface": self.default_config["web_interface"],
                "api_server": self.default_config["api_server"],
                "mobile_app": self.default_config["mobile_app"],
                "analytics": self.default_config["analytics"],
                "plugins": self.default_config["plugins"],
                "error_handling": self.default_config["error_handling"],
                "vram_monitoring": self.default_config["vram_monitoring"]
            }

    def get_backup_list(self) -> List[Tuple[str, datetime]]:
        """Get list of available backups"""
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("config_backup_") and filename.endswith(".json"):
                    filepath = os.path.join(self.backup_dir, filename)
                    try:
                        mtime = os.path.getmtime(filepath)
                        backup_time = datetime.fromtimestamp(mtime)
                        backups.append((filepath, backup_time))
                    except Exception:
                        pass
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            return backups
        except Exception as e:
            print(f"Error getting backup list: {e}")
            return []

    def restore_backup(self, backup_file: str) -> bool:
        """Restore configuration from backup"""
        try:
            if os.path.exists(backup_file):
                # Create backup of current config before restoring
                self._create_backup()
                
                # Copy backup to config file
                shutil.copy2(backup_file, self.config_file)
                return True
            return False
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def export_config(self, export_file: str) -> bool:
        """Export configuration to file"""
        try:
            config = self.load_config()
            with open(export_file, "w", encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, import_file: str) -> bool:
        """Import configuration from file"""
        try:
            if os.path.exists(import_file):
                with open(import_file, "r", encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Validate imported config
                validated_config = self._validate_config_data(config_data)
                return self.save_config(validated_config)
            return False
        except Exception as e:
            print(f"Error importing config: {e}")
            return False


def save_config(ooba_path: str, zwaifu_path: str, config_file: str) -> None:
    """Legacy function for saving basic configuration"""
    try:
        config_manager = ConfigManager(config_file)
        config = config_manager.load_config()
        config["ooba_bat"] = ooba_path
        config["zwaifu_bat"] = zwaifu_path
        config_manager.save_config(config)
    except Exception as e:
        print(f"Error in legacy save_config: {e}")


def load_config(config_file: str) -> Tuple[Optional[str], Optional[str]]:
    """Legacy function for loading basic configuration"""
    try:
        config_manager = ConfigManager(config_file)
        ooba_path, zwaifu_path, _, _ = config_manager.get_batch_paths()
        return ooba_path, zwaifu_path
    except Exception as e:
        print(f"Error in legacy load_config: {e}")
        return None, None 
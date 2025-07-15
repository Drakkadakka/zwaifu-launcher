#!/usr/bin/env python3
"""
Plugin Marketplace for Z-Waifu Launcher GUI
Browse and install plugins from repository with automatic dependency management.
"""

import os
import sys
import json
import requests
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import zipfile
import tempfile
import shutil
from tkinter import simpledialog

class PluginMarketplace:
    """Plugin marketplace for browsing and installing plugins"""
    
    def __init__(self, launcher_gui):
        self.launcher_gui = launcher_gui
        self.plugins_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')
        self.marketplace_dir = os.path.join(self.plugins_dir, 'marketplace')
        self.installed_plugins_file = os.path.join(self.plugins_dir, 'installed_plugins.json')
        
        # Create directories
        os.makedirs(self.plugins_dir, exist_ok=True)
        os.makedirs(self.marketplace_dir, exist_ok=True)
        
        # Marketplace configuration
        self.marketplace_url = "https://api.github.com/repos/zwaifu-launcher/plugins/contents"
        self.plugin_repo_base = "https://raw.githubusercontent.com/zwaifu-launcher/plugins/main"
        
        # Cache
        self.plugin_cache = {}
        self.installed_plugins = self.load_installed_plugins()
        
        # Load plugin registry
        self.plugin_registry = self.load_plugin_registry()
        
        # Theme support
        self.current_theme = self._get_current_theme()
        
    def _get_current_theme(self) -> Dict[str, str]:
        """Get current theme from launcher GUI using TAB_THEMES/LIGHT_TAB_THEMES['plugin_manager']"""
        # Use the main GUI's theme dictionaries for plugin_manager
        if hasattr(self.launcher_gui, '_dark_mode') and hasattr(self.launcher_gui, 'current_theme'):
            if self.launcher_gui._dark_mode:
                theme_dict = getattr(self.launcher_gui, 'TAB_THEMES', None)
            else:
                theme_dict = getattr(self.launcher_gui, 'LIGHT_TAB_THEMES', None)
            if theme_dict and 'plugin_manager' in theme_dict:
                # Map the theme keys to the expected keys in the marketplace
                gui_theme = theme_dict['plugin_manager']
                # Provide defaults for any missing keys
                return {
                    'bg': gui_theme.get('bg', '#1a1a1a'),
                    'fg': gui_theme.get('fg', '#ff99cc'),
                    'entry_bg': gui_theme.get('entry_bg', '#222222'),
                    'entry_fg': gui_theme.get('entry_fg', '#ff99cc'),
                    'accent': gui_theme.get('accent', '#cc6699'),
                    'button_bg': gui_theme.get('accent', '#cc6699'),
                    'button_fg': gui_theme.get('fg', '#ff99cc'),
                    'tree_bg': gui_theme.get('entry_bg', '#222222'),
                    'tree_fg': gui_theme.get('fg', '#ff99cc'),
                    'tree_select_bg': gui_theme.get('accent', '#cc6699'),
                    'tree_select_fg': gui_theme.get('fg', '#ff99cc'),
                    'card_bg': gui_theme.get('entry_bg', '#222222'),
                    'card_fg': gui_theme.get('fg', '#ff99cc'),
                    'border_color': gui_theme.get('accent', '#cc6699'),
                    'hover_bg': gui_theme.get('bg', '#1a1a1a'),
                    'hover_fg': gui_theme.get('fg', '#ff99cc'),
                    'success_color': '#28a745',
                    'warning_color': '#ffc107',
                    'error_color': '#dc3545',
                    'info_color': '#17a2b8',
                    'tooltip_bg': gui_theme.get('entry_bg', '#222222'),
                    'tooltip_fg': gui_theme.get('fg', '#ff99cc'),
                    'tooltip_border': gui_theme.get('accent', '#cc6699'),
                }
        # Fallback to previous logic
        if hasattr(self.launcher_gui, '_dark_mode'):
            if self.launcher_gui._dark_mode:
                return {
                    'bg': '#1a1a1a',
                    'fg': '#ff99cc',
                    'entry_bg': '#222222',
                    'entry_fg': '#ff99cc',
                    'accent': '#cc6699',
                    'button_bg': '#333333',
                    'button_fg': '#ffffff',
                    'tree_bg': '#2d2d2d',
                    'tree_fg': '#ffffff',
                    'tree_select_bg': '#0078d4',
                    'tree_select_fg': '#ffffff',
                    'card_bg': '#2a2a2a',
                    'card_fg': '#ff99cc',
                    'border_color': '#404040',
                    'hover_bg': '#3a3a3a',
                    'hover_fg': '#ffffff',
                    'success_color': '#00ff99',
                    'warning_color': '#ffcc00',
                    'error_color': '#ff6666',
                    'info_color': '#99ccff',
                    'tooltip_bg': '#2d2d2d',
                    'tooltip_fg': '#ffffff',
                    'tooltip_border': '#404040'
                }
            else:
                return {
                    'bg': '#f8f9fa',
                    'fg': '#721c24',
                    'entry_bg': '#ffffff',
                    'entry_fg': '#721c24',
                    'accent': '#dc3545',
                    'button_bg': '#e0e0e0',
                    'button_fg': '#000000',
                    'tree_bg': '#ffffff',
                    'tree_fg': '#000000',
                    'tree_select_bg': '#0078d4',
                    'tree_select_fg': '#ffffff',
                    'card_bg': '#ffffff',
                    'card_fg': '#721c24',
                    'border_color': '#dee2e6',
                    'hover_bg': '#f8f9fa',
                    'hover_fg': '#000000',
                    'success_color': '#28a745',
                    'warning_color': '#ffc107',
                    'error_color': '#dc3545',
                    'info_color': '#17a2b8',
                    'tooltip_bg': '#ffffff',
                    'tooltip_fg': '#000000',
                    'tooltip_border': '#dee2e6'
                }
        else:
            # Default light theme
            return {
                'bg': '#f8f9fa',
                'fg': '#721c24',
                'entry_bg': '#ffffff',
                'entry_fg': '#721c24',
                'accent': '#dc3545',
                'button_bg': '#e0e0e0',
                'button_fg': '#000000',
                'tree_bg': '#ffffff',
                'tree_fg': '#000000',
                'tree_select_bg': '#0078d4',
                'tree_select_fg': '#ffffff',
                'card_bg': '#ffffff',
                'card_fg': '#721c24',
                'border_color': '#dee2e6',
                'hover_bg': '#f8f9fa',
                'hover_fg': '#000000',
                'success_color': '#28a745',
                'warning_color': '#ffc107',
                'error_color': '#dc3545',
                'info_color': '#17a2b8',
                'tooltip_bg': '#ffffff',
                'tooltip_fg': '#000000',
                'tooltip_border': '#dee2e6'
            }
    
    def update_theme(self):
        """Update theme when GUI theme changes"""
        self.current_theme = self._get_current_theme()
        if hasattr(self, 'marketplace_window') and self.marketplace_window:
            self._apply_theme_to_window(self.marketplace_window)
    
    def _apply_theme_to_window(self, window):
        """Apply current theme to a window and all its widgets"""
        try:
            # Apply theme to main window
            window.configure(bg=self.current_theme['bg'])
            
            # Apply theme to all widgets recursively
            self._theme_widget_tree(window)
        except Exception as e:
            print(f"Error applying theme to window: {e}")
    
    def _theme_widget_tree(self, parent):
        """Recursively apply theme to all widgets in a widget tree"""
        try:
            # Apply theme to current widget
            if isinstance(parent, tk.Toplevel):
                parent.configure(bg=self.current_theme['bg'])
            elif isinstance(parent, tk.Frame) or isinstance(parent, ttk.Frame):
                parent.configure(bg=self.current_theme['bg'])
            elif isinstance(parent, tk.Label) or isinstance(parent, ttk.Label):
                parent.configure(bg=self.current_theme['bg'], fg=self.current_theme['fg'])
            elif isinstance(parent, tk.Entry) or isinstance(parent, ttk.Entry):
                parent.configure(
                    bg=self.current_theme['entry_bg'],
                    fg=self.current_theme['entry_fg'],
                    insertbackground=self.current_theme['fg'],
                    relief=tk.SOLID,
                    bd=1,
                    highlightbackground=self.current_theme['border_color'],
                    highlightcolor=self.current_theme['accent']
                )
            elif isinstance(parent, tk.Button) or isinstance(parent, ttk.Button):
                parent.configure(
                    bg=self.current_theme['button_bg'],
                    fg=self.current_theme['button_fg'],
                    relief=tk.RAISED,
                    bd=1,
                    highlightbackground=self.current_theme['border_color'],
                    highlightcolor=self.current_theme['accent'],
                    activebackground=self.current_theme['hover_bg'],
                    activeforeground=self.current_theme['hover_fg']
                )
            elif isinstance(parent, tk.Text):
                parent.configure(
                    bg=self.current_theme['entry_bg'],
                    fg=self.current_theme['entry_fg'],
                    insertbackground=self.current_theme['fg'],
                    selectbackground=self.current_theme['accent'],
                    selectforeground=self.current_theme['tree_select_fg'],
                    relief=tk.SOLID,
                    bd=1,
                    highlightbackground=self.current_theme['border_color'],
                    highlightcolor=self.current_theme['accent']
                )
            elif isinstance(parent, ttk.Treeview):
                parent.configure(
                    background=self.current_theme['tree_bg'],
                    foreground=self.current_theme['tree_fg'],
                    selectbackground=self.current_theme['tree_select_bg'],
                    selectforeground=self.current_theme['tree_select_fg'],
                    fieldbackground=self.current_theme['tree_bg']
                )
            elif isinstance(parent, tk.Listbox):
                parent.configure(
                    bg=self.current_theme['tree_bg'],
                    fg=self.current_theme['tree_fg'],
                    selectbackground=self.current_theme['tree_select_bg'],
                    selectforeground=self.current_theme['tree_select_fg'],
                    relief=tk.SOLID,
                    bd=1,
                    highlightbackground=self.current_theme['border_color'],
                    highlightcolor=self.current_theme['accent']
                )
            elif isinstance(parent, ttk.Combobox):
                parent.configure(
                    background=self.current_theme['entry_bg'],
                    foreground=self.current_theme['entry_fg']
                )
            elif isinstance(parent, ttk.LabelFrame):
                parent.configure(
                    background=self.current_theme['card_bg'],
                    foreground=self.current_theme['card_fg']
                )
            
            # Recursively theme all children
            for child in parent.winfo_children():
                self._theme_widget_tree(child)
                
        except Exception as e:
            # Silently continue if widget can't be themed
            pass
    
    def load_installed_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Load installed plugins information"""
        try:
            if os.path.exists(self.installed_plugins_file):
                with open(self.installed_plugins_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading installed plugins: {e}")
            return {}
    
    def save_installed_plugins(self) -> bool:
        """Save installed plugins information"""
        try:
            with open(self.installed_plugins_file, 'w', encoding='utf-8') as f:
                json.dump(self.installed_plugins, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving installed plugins: {e}")
            return False
    
    def load_plugin_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load plugin registry from local cache or remote"""
        registry_file = os.path.join(self.marketplace_dir, 'plugin_registry.json')
        
        try:
            # Try to load from cache first
            if os.path.exists(registry_file):
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                
                # Check if cache is recent (less than 1 hour old)
                if 'last_updated' in registry:
                    last_updated = datetime.fromisoformat(registry['last_updated'])
                    if (datetime.now() - last_updated).total_seconds() < 3600:
                        return registry
            
            # Load from remote
            return self.fetch_plugin_registry()
            
        except Exception as e:
            print(f"Error loading plugin registry: {e}")
            return {}
    
    def fetch_plugin_registry(self) -> Dict[str, Dict[str, Any]]:
        """Fetch plugin registry from remote repository (GitHub), fallback to sample if fails"""
        registry_file = os.path.join(self.marketplace_dir, 'plugin_registry.json')
        github_url = "https://raw.githubusercontent.com/zwaifu-launcher/plugins/main/registry.json"
        try:
            response = requests.get(github_url, timeout=10)
            if response.status_code == 200:
                registry = response.json()
                registry['last_updated'] = datetime.now().isoformat()
                with open(registry_file, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
                return registry
            else:
                print(f"Warning: Could not fetch remote registry, status {response.status_code}")
        except Exception as e:
            print(f"Network error fetching remote registry: {e}")
        # Fallback to sample registry
        print("Falling back to sample registry.")
        return self._sample_registry(registry_file)

    def _sample_registry(self, registry_file):
        registry = {
            'last_updated': datetime.now().isoformat(),
            'plugins': {
                'process_monitor': {
                    'name': 'Process Monitor',
                    'version': '1.0.0',
                    'description': 'Advanced process monitoring with alerts',
                    'author': 'Z-Waifu Team',
                    'category': 'monitoring',
                    'tags': ['monitoring', 'alerts', 'process'],
                    'dependencies': ['psutil>=5.8.0'],
                    'download_url': 'https://github.com/zwaifu-launcher/plugins/raw/main/process_monitor.zip',
                    'documentation_url': 'https://github.com/zwaifu-launcher/plugins/blob/main/process_monitor/README.md',
                    'rating': 4.5,
                    'downloads': 1250,
                    'last_updated': '2024-01-15T10:30:00Z'
                },
                'auto_restart': {
                    'name': 'Auto Restart',
                    'version': '1.1.0',
                    'description': 'Automatically restart processes on failure',
                    'author': 'Z-Waifu Team',
                    'category': 'automation',
                    'tags': ['automation', 'restart', 'reliability'],
                    'dependencies': [],
                    'download_url': 'https://github.com/zwaifu-launcher/plugins/raw/main/auto_restart.zip',
                    'documentation_url': 'https://github.com/zwaifu-launcher/plugins/blob/main/auto_restart/README.md',
                    'rating': 4.2,
                    'downloads': 890,
                    'last_updated': '2024-01-10T14:20:00Z'
                },
                'performance_analyzer': {
                    'name': 'Performance Analyzer',
                    'version': '1.0.0',
                    'description': 'Advanced performance analysis and optimization',
                    'author': 'Z-Waifu Team',
                    'category': 'analytics',
                    'tags': ['analytics', 'performance', 'optimization'],
                    'dependencies': ['matplotlib>=3.5.0', 'numpy>=1.21.0'],
                    'download_url': 'https://github.com/zwaifu-launcher/plugins/raw/main/performance_analyzer.zip',
                    'documentation_url': 'https://github.com/zwaifu-launcher/plugins/blob/main/performance_analyzer/README.md',
                    'rating': 4.7,
                    'downloads': 2100,
                    'last_updated': '2024-01-20T09:15:00Z'
                },
                'backup_manager': {
                    'name': 'Backup Manager',
                    'version': '1.0.0',
                    'description': 'Automated backup and restore functionality',
                    'author': 'Z-Waifu Team',
                    'category': 'backup',
                    'tags': ['backup', 'restore', 'automation'],
                    'dependencies': ['cryptography>=3.4.0'],
                    'download_url': 'https://github.com/zwaifu-launcher/plugins/raw/main/backup_manager.zip',
                    'documentation_url': 'https://github.com/zwaifu-launcher/plugins/blob/main/backup_manager/README.md',
                    'rating': 4.3,
                    'downloads': 750,
                    'last_updated': '2024-01-12T16:45:00Z'
                },
                'notification_center': {
                    'name': 'Notification Center',
                    'version': '1.0.0',
                    'description': 'Centralized notification management',
                    'author': 'Z-Waifu Team',
                    'category': 'notifications',
                    'tags': ['notifications', 'alerts', 'ui'],
                    'dependencies': ['plyer>=2.0.0'],
                    'download_url': 'https://github.com/zwaifu-launcher/plugins/raw/main/notification_center.zip',
                    'documentation_url': 'https://github.com/zwaifu-launcher/plugins/blob/main/notification_center/README.md',
                    'rating': 4.1,
                    'downloads': 680,
                    'last_updated': '2024-01-08T11:30:00Z'
                }
            }
        }
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        return registry
    
    def get_available_plugins(self, category: Optional[str] = None, 
                            search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available plugins with optional filtering"""
        plugins = []
        
        for plugin_id, plugin_data in self.plugin_registry.get('plugins', {}).items():
            # Check if already installed
            is_installed = plugin_id in self.installed_plugins
            
            # Apply filters
            if category and plugin_data.get('category') != category:
                continue
            
            if search_term:
                search_lower = search_term.lower()
                if not (search_lower in plugin_data.get('name', '').lower() or
                       search_lower in plugin_data.get('description', '').lower() or
                       search_lower in ' '.join(plugin_data.get('tags', [])).lower()):
                    continue
            
            plugins.append({
                'id': plugin_id,
                'is_installed': is_installed,
                'installed_version': self.installed_plugins.get(plugin_id, {}).get('version'),
                **plugin_data
            })
        
        # Sort by rating, then by downloads
        plugins.sort(key=lambda x: (x.get('rating', 0), x.get('downloads', 0)), reverse=True)
        
        return plugins
    
    def get_plugin_categories(self) -> List[str]:
        """Get available plugin categories"""
        categories = set()
        for plugin_data in self.plugin_registry.get('plugins', {}).values():
            category = plugin_data.get('category', 'other')
            categories.add(category)
        return sorted(list(categories))
    
    def install_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Install a plugin with error handling and rollback"""
        try:
            plugin_data = self.plugin_registry.get('plugins', {}).get(plugin_id)
            if not plugin_data:
                return False, f"Plugin {plugin_id} not found in registry"
            if plugin_id in self.installed_plugins:
                return False, f"Plugin {plugin_id} is already installed"
            download_url = plugin_data.get('download_url')
            if not download_url:
                return False, "Download URL not available"
            # Security check: warn if unsigned or untrusted
            if not plugin_data.get('signed', False):
                return False, f"Security warning: Plugin '{plugin_id}' is unsigned or from an untrusted source. Installation aborted."
            # Dependency conflict check
            conflicts = self._check_dependency_conflicts(plugin_data.get('dependencies', []))
            if conflicts:
                return False, f"Dependency conflict: {conflicts}"
            with tempfile.TemporaryDirectory() as temp_dir:
                plugin_file = os.path.join(temp_dir, f"{plugin_id}.zip")
                # Download plugin file
                try:
                    resp = requests.get(download_url, timeout=20)
                    if resp.status_code == 200:
                        with open(plugin_file, 'wb') as f:
                            f.write(resp.content)
                    else:
                        return False, f"Failed to download plugin: HTTP {resp.status_code}"
                except Exception as e:
                    return False, f"Network error downloading plugin: {e}"
                plugin_dir = os.path.join(self.plugins_dir, plugin_id)
                if os.path.exists(plugin_dir):
                    shutil.rmtree(plugin_dir)
                try:
                    with zipfile.ZipFile(plugin_file, 'r') as zip_ref:
                        zip_ref.extractall(plugin_dir)
                except Exception as e:
                    if os.path.exists(plugin_dir):
                        shutil.rmtree(plugin_dir)
                    return False, f"Failed to extract plugin: {e}"
                dependencies = plugin_data.get('dependencies', [])
                if dependencies:
                    if not self.install_plugin_dependencies(dependencies):
                        if os.path.exists(plugin_dir):
                            shutil.rmtree(plugin_dir)
                        return False, "Failed to install dependencies. Plugin install rolled back."
                self.installed_plugins[plugin_id] = {
                    'version': plugin_data.get('version'),
                    'installed_at': datetime.now().isoformat(),
                    'dependencies': dependencies
                }
                self.save_installed_plugins()
                return True, f"Plugin {plugin_id} installed successfully"
        except Exception as e:
            # Rollback on any error
            plugin_dir = os.path.join(self.plugins_dir, plugin_id)
            if os.path.exists(plugin_dir):
                shutil.rmtree(plugin_dir)
            return False, f"Error installing plugin: {e}"
    
    def create_sample_plugin(self, plugin_id: str, plugin_data: Dict[str, Any], output_file: str):
        """Create a sample plugin file for demonstration"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                plugin_dir = os.path.join(temp_dir, plugin_id)
                os.makedirs(plugin_dir)
                
                # Create plugin main file
                main_file = os.path.join(plugin_dir, f"{plugin_id}.py")
                with open(main_file, 'w', encoding='utf-8') as f:
                    f.write(f'''#!/usr/bin/env python3
"""
{plugin_data.get('name', plugin_id)} Plugin
{plugin_data.get('description', '')}
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Add the utils directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

try:
    from plugin_system import PluginBase
except ImportError:
    print(f"Error: Could not import PluginBase for {plugin_id}")
    sys.exit(1)

class {plugin_id.replace('_', '').title()}Plugin(PluginBase):
    """{plugin_data.get('name', plugin_id)} plugin implementation"""
    
    def __init__(self, launcher_gui):
        super().__init__(launcher_gui)
        self.name = "{plugin_data.get('name', plugin_id)}"
        self.version = "{plugin_data.get('version', '1.0.0')}"
        self.description = "{plugin_data.get('description', '')}"
        self.author = "{plugin_data.get('author', 'Unknown')}"
        self.enabled = False
        self.config = {{}}
        
        # Plugin-specific variables
        self.monitoring_thread = None
        self.stop_monitoring = False
        
    def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            self.launcher_gui.log(f"Initializing {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error initializing {{self.name}} plugin: {{e}}")
            return False
    
    def enable(self) -> bool:
        """Enable the plugin"""
        try:
            self.enabled = True
            self.launcher_gui.log(f"Enabled {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error enabling {{self.name}} plugin: {{e}}")
            return False
    
    def disable(self) -> bool:
        """Disable the plugin"""
        try:
            self.enabled = False
            self.stop_monitoring = True
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=2)
            self.launcher_gui.log(f"Disabled {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error disabling {{self.name}} plugin: {{e}}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        try:
            self.disable()
            self.launcher_gui.log(f"Cleaned up {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error cleaning up {{self.name}} plugin: {{e}}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self.config
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """Set plugin configuration"""
        try:
            self.config = config
            self.launcher_gui.log(f"Updated config for {{self.name}} plugin")
            return True
        except Exception as e:
            self.launcher_gui.log(f"Error setting config for {{self.name}} plugin: {{e}}")
            return False
    
    def on_process_start(self, process_type: str, instance_id: int) -> None:
        """Called when a process starts"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Process {{process_type}} (instance {{instance_id}}) started")
    
    def on_process_stop(self, process_type: str, instance_id: int) -> None:
        """Called when a process stops"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Process {{process_type}} (instance {{instance_id}}) stopped")
    
    def on_process_error(self, process_type: str, instance_id: int, error: str) -> None:
        """Called when a process encounters an error"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Process {{process_type}} (instance {{instance_id}}) error: {{error}}")
    
    def on_launcher_start(self) -> None:
        """Called when the launcher starts"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Launcher started")
    
    def on_launcher_stop(self) -> None:
        """Called when the launcher stops"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Launcher stopped")
    
    def on_config_change(self, config: Dict[str, Any]) -> None:
        """Called when launcher configuration changes"""
        if self.enabled:
            self.launcher_gui.log(f"[{{self.name}}] Launcher config changed")

# Plugin factory function (required for plugin loading)
def create_plugin(launcher_gui):
    """Create plugin instance"""
    return {plugin_id.replace('_', '').title()}Plugin(launcher_gui)
''')
                
                # Create README
                readme_file = os.path.join(plugin_dir, 'README.md')
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(f'''# {plugin_data.get('name', plugin_id)}

{plugin_data.get('description', '')}

## Installation

This plugin is installed through the Z-Waifu Launcher Plugin Marketplace.

## Configuration

No additional configuration required.

## Usage

This plugin will be automatically loaded by the launcher.

## Dependencies

{', '.join(plugin_data.get('dependencies', ['None']))}

## Version

{plugin_data.get('version', '1.0.0')}

## Author

{plugin_data.get('author', 'Unknown')}

## Features

- Process monitoring and event handling
- Configuration management
- Automatic lifecycle management
- Integration with launcher logging system
''')
                
                # Create plugin manifest
                manifest_file = os.path.join(plugin_dir, 'manifest.json')
                with open(manifest_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'name': plugin_data.get('name', plugin_id),
                        'version': plugin_data.get('version', '1.0.0'),
                        'description': plugin_data.get('description', ''),
                        'author': plugin_data.get('author', 'Unknown'),
                        'main_file': f'{plugin_id}.py',
                        'dependencies': plugin_data.get('dependencies', []),
                        'category': plugin_data.get('category', 'other'),
                        'tags': plugin_data.get('tags', []),
                        'rating': plugin_data.get('rating', 0),
                        'downloads': plugin_data.get('downloads', 0)
                    }, f, indent=2, ensure_ascii=False)
                
                # Create zip file
                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(plugin_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, plugin_dir)
                            zipf.write(file_path, arc_name)
                            
        except Exception as e:
            print(f"Error creating sample plugin: {e}")
    
    def _check_dependency_conflicts(self, dependencies: List[str]) -> str:
        """Check for dependency conflicts"""
        # This is a placeholder - in a real implementation, you'd check
        # for conflicts with existing packages
        return ""
    
    def create_test_plugin(self, plugin_name: str = "test_plugin") -> bool:
        """Create a test plugin for debugging purposes"""
        try:
            plugin_data = {
                'name': f'Test {plugin_name.replace("_", " ").title()}',
                'version': '1.0.0',
                'description': f'A test plugin for {plugin_name} functionality',
                'author': 'Z-Waifu Team',
                'category': 'testing',
                'tags': ['test', 'debug', 'development'],
                'dependencies': [],
                'rating': 4.0,
                'downloads': 100,
                'last_updated': datetime.now().isoformat()
            }
            
            # Create the plugin file directly in the plugins directory
            plugin_file = os.path.join(self.plugins_dir, f"{plugin_name}.py")
            
            # Use the create_sample_plugin method to generate the content
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_zip = os.path.join(temp_dir, f"{plugin_name}.zip")
                self.create_sample_plugin(plugin_name, plugin_data, temp_zip)
                
                # Extract the main plugin file
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Copy the main plugin file to the plugins directory
                extracted_plugin_file = os.path.join(temp_dir, f"{plugin_name}.py")
                if os.path.exists(extracted_plugin_file):
                    shutil.copy2(extracted_plugin_file, plugin_file)
                    print(f"Created test plugin: {plugin_file}")
                    return True
                else:
                    print(f"Failed to create test plugin: {plugin_name}")
                    return False
                    
        except Exception as e:
            print(f"Error creating test plugin: {e}")
            return False
    
    def install_plugin_dependencies(self, dependencies: List[str]) -> bool:
        """Install plugin dependencies"""
        try:
            for dependency in dependencies:
                # Parse dependency (e.g., "package>=1.0.0")
                if '>=' in dependency:
                    package, version = dependency.split('>=')
                elif '==' in dependency:
                    package, version = dependency.split('==')
                else:
                    package = dependency
                    version = None
                
                # Install package
                cmd = [sys.executable, '-m', 'pip', 'install', dependency]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Warning: Failed to install dependency {dependency}: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def uninstall_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Uninstall a plugin"""
        try:
            if plugin_id not in self.installed_plugins:
                return False, f"Plugin {plugin_id} is not installed"
            
            # Remove plugin directory
            plugin_dir = os.path.join(self.plugins_dir, plugin_id)
            if os.path.exists(plugin_dir):
                shutil.rmtree(plugin_dir)
            
            # Remove from installed plugins
            del self.installed_plugins[plugin_id]
            self.save_installed_plugins()
            
            return True, f"Plugin {plugin_id} uninstalled successfully"
            
        except Exception as e:
            return False, f"Error uninstalling plugin: {e}"
    
    def update_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """Update a plugin"""
        try:
            if plugin_id not in self.installed_plugins:
                return False, f"Plugin {plugin_id} is not installed"
            
            plugin_data = self.plugin_registry.get('plugins', {}).get(plugin_id)
            if not plugin_data:
                return False, f"Plugin {plugin_id} not found in registry"
            
            current_version = self.installed_plugins[plugin_id].get('version')
            new_version = plugin_data.get('version')
            
            if current_version == new_version:
                return False, f"Plugin {plugin_id} is already up to date"
            
            # Uninstall current version
            success, message = self.uninstall_plugin(plugin_id)
            if not success:
                return False, f"Failed to uninstall current version: {message}"
            
            # Install new version
            return self.install_plugin(plugin_id)
            
        except Exception as e:
            return False, f"Error updating plugin: {e}"
    
    def refresh_registry(self) -> bool:
        """Refresh the plugin registry"""
        try:
            self.plugin_registry = self.fetch_plugin_registry()
            return True
        except Exception as e:
            print(f"Error refreshing registry: {e}")
            return False
    
    def create_marketplace_window(self):
        """Create the plugin marketplace window integrated with main GUI"""
        marketplace = PluginMarketplaceWindow(self, self.current_theme)
        marketplace.show()
        
        # Store reference for theme propagation
        self.marketplace_window = marketplace
    
    def refresh_theme(self):
        """Refresh theme when GUI theme changes with enhanced responsiveness"""
        try:
            # Update current theme from main GUI
            self.current_theme = self._get_current_theme()
            
            # Update marketplace window if it exists
            if hasattr(self, 'marketplace_window') and self.marketplace_window:
                # Apply theme to the window itself
                self._apply_theme_to_window(self.marketplace_window)
                
                # Re-setup styles for marketplace window
                if hasattr(self.marketplace_window, 'setup_styles'):
                    self.marketplace_window.setup_styles()
                    
                # Reload plugins to update alternating colors
                if hasattr(self.marketplace_window, 'load_plugins'):
                    self.marketplace_window.load_plugins()
                    
                # Force window update to ensure immediate visual changes
                self.marketplace_window.update_idletasks()
                
                # Log theme update for debugging
                if hasattr(self.launcher_gui, 'log'):
                    self.launcher_gui.log(f"[Plugin Marketplace] Theme refreshed to: {self.launcher_gui.current_theme}")
                    
        except Exception as e:
            # Log error but don't crash
            if hasattr(self.launcher_gui, 'log'):
                self.launcher_gui.log(f"[Plugin Marketplace] Error refreshing theme: {e}")
            else:
                print(f"[Plugin Marketplace] Error refreshing theme: {e}")
    
    def refresh_styles(self):
        """Refresh styles for all open windows with enhanced responsiveness"""
        try:
            if hasattr(self, 'marketplace_window') and self.marketplace_window:
                # Update current theme first
                self.current_theme = self._get_current_theme()
                
                # Re-setup styles
                self.marketplace_window.setup_styles()
                
                # Apply theme to window
                self._apply_theme_to_window(self.marketplace_window)
                
                # Reload plugins to update alternating colors
                if hasattr(self.marketplace_window, 'load_plugins'):
                    self.marketplace_window.load_plugins()
                    
                # Force immediate update
                self.marketplace_window.update_idletasks()
                
        except Exception as e:
            if hasattr(self.launcher_gui, 'log'):
                self.launcher_gui.log(f"[Plugin Marketplace] Error refreshing styles: {e}")
            else:
                print(f"[Plugin Marketplace] Error refreshing styles: {e}")

class PluginMarketplaceWindow:
    """Plugin marketplace window"""
    
    def __init__(self, marketplace: PluginMarketplace, theme_dict: Optional[Dict[str, str]] = None):
        self.marketplace = marketplace
        self.window = None
        self.plugin_list = None
        self.search_var = None
        self.category_var = None
        self.status_var = None
        self.style = None
        
        # Store theme dictionary
        self.theme_dict = theme_dict or marketplace.current_theme
        
    def apply_theme(self, theme_dict: Dict[str, str]):
        """Apply theme dictionary to all widgets in the window"""
        self.theme_dict = theme_dict
        
        if not self.window or not self.window.winfo_exists():
            return
            
        try:
            # Apply theme to main window
            self.window.configure(bg=theme_dict.get('bg', '#1a1a1a'))
            
            # Re-setup styles with new theme
            self.setup_styles()
            
            # Apply theme to all widgets recursively
            self._apply_theme_to_widgets(self.window, theme_dict)
            
            # Reload plugins to update alternating colors
            if hasattr(self, 'load_plugins'):
                self.load_plugins()
            
            # Force window update
            self.window.update_idletasks()
            
        except Exception as e:
            if hasattr(self.marketplace.launcher_gui, 'log'):
                self.marketplace.launcher_gui.log(f"[PluginMarketplaceWindow] Error applying theme: {e}")
    
    def _apply_theme_to_widgets(self, parent, theme_dict):
        """Recursively apply theme to all widgets in a widget tree"""
        try:
            for child in parent.winfo_children():
                # Apply theme to current widget
                self._apply_theme_to_single_widget(child, theme_dict)
                
                # Recursively theme all children
                self._apply_theme_to_widgets(child, theme_dict)
                
        except Exception as e:
            # Silently continue if widget can't be themed
            pass
    
    def _apply_theme_to_single_widget(self, widget, theme_dict):
        """Apply theme to a single widget"""
        try:
            widget_class = widget.__class__.__name__
            
            if widget_class in ['Toplevel', 'Frame', 'ttk.Frame']:
                widget.configure(bg=theme_dict.get('bg', '#1a1a1a'))
            elif widget_class in ['Label', 'ttk.Label']:
                widget.configure(
                    bg=theme_dict.get('bg', '#1a1a1a'),
                    fg=theme_dict.get('fg', '#ff99cc')
                )
            elif widget_class in ['Entry', 'ttk.Entry']:
                widget.configure(
                    bg=theme_dict.get('entry_bg', '#222222'),
                    fg=theme_dict.get('entry_fg', '#ff99cc'),
                    insertbackground=theme_dict.get('fg', '#ff99cc'),
                    relief=tk.SOLID,
                    bd=1,
                    highlightbackground=theme_dict.get('border_color', '#404040'),
                    highlightcolor=theme_dict.get('accent', '#cc6699')
                )
            elif widget_class in ['Button', 'ttk.Button']:
                widget.configure(
                    bg=theme_dict.get('button_bg', '#333333'),
                    fg=theme_dict.get('button_fg', '#ffffff'),
                    relief=tk.RAISED,
                    bd=1,
                    highlightbackground=theme_dict.get('border_color', '#404040'),
                    highlightcolor=theme_dict.get('accent', '#cc6699'),
                    activebackground=theme_dict.get('hover_bg', '#3a3a3a'),
                    activeforeground=theme_dict.get('hover_fg', '#ffffff')
                )
            elif widget_class == 'Text':
                widget.configure(
                    bg=theme_dict.get('entry_bg', '#222222'),
                    fg=theme_dict.get('entry_fg', '#ff99cc'),
                    insertbackground=theme_dict.get('fg', '#ff99cc'),
                    selectbackground=theme_dict.get('accent', '#cc6699'),
                    selectforeground=theme_dict.get('tree_select_fg', '#ffffff'),
                    relief=tk.SOLID,
                    bd=1,
                    highlightbackground=theme_dict.get('border_color', '#404040'),
                    highlightcolor=theme_dict.get('accent', '#cc6699')
                )
            elif widget_class == 'Treeview':
                widget.configure(
                    background=theme_dict.get('tree_bg', '#2d2d2d'),
                    foreground=theme_dict.get('tree_fg', '#ffffff'),
                    selectbackground=theme_dict.get('tree_select_bg', '#0078d4'),
                    selectforeground=theme_dict.get('tree_select_fg', '#ffffff'),
                    fieldbackground=theme_dict.get('tree_bg', '#2d2d2d')
                )
            elif widget_class == 'Listbox':
                widget.configure(
                    bg=theme_dict.get('tree_bg', '#2d2d2d'),
                    fg=theme_dict.get('tree_fg', '#ffffff'),
                    selectbackground=theme_dict.get('tree_select_bg', '#0078d4'),
                    selectforeground=theme_dict.get('tree_select_fg', '#ffffff'),
                    relief=tk.SOLID,
                    bd=1,
                    highlightbackground=theme_dict.get('border_color', '#404040'),
                    highlightcolor=theme_dict.get('accent', '#cc6699')
                )
            elif widget_class == 'Combobox':
                widget.configure(
                    background=theme_dict.get('entry_bg', '#222222'),
                    foreground=theme_dict.get('entry_fg', '#ff99cc')
                )
            elif widget_class == 'LabelFrame':
                widget.configure(
                    background=theme_dict.get('card_bg', '#2a2a2a'),
                    foreground=theme_dict.get('card_fg', '#ff99cc')
                )
            elif widget_class == 'Canvas':
                widget.configure(
                    bg=theme_dict.get('canvas_bg', '#2d2d30'),
                    highlightbackground=theme_dict.get('border_color', '#404040')
                )
            elif widget_class == 'Scrollbar':
                widget.configure(
                    troughcolor=theme_dict.get('entry_bg', '#222222'),
                    bg=theme_dict.get('bg', '#1a1a1a'),
                    activebackground=theme_dict.get('accent', '#cc6699')
                )
                
        except Exception as e:
            # Silently continue if widget can't be themed
            pass
    
    def setup_styles(self):
        """Set up custom ttk styles for dark/light themes"""
        theme = self.theme_dict
        self.style = ttk.Style()
        # Use a unique style prefix to avoid conflicts
        prefix = 'ZWaifuMarketplace.'
        # General
        self.style.configure(prefix + 'TFrame', background=theme['bg'])
        self.style.configure(prefix + 'TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure(prefix + 'TButton', background=theme['button_bg'], foreground=theme['button_fg'], borderwidth=1, focusthickness=2, focuscolor=theme['accent'])
        self.style.map(prefix + 'TButton',
            background=[('active', theme['accent']), ('pressed', theme['accent'])],
            foreground=[('active', theme['button_fg']), ('pressed', theme['button_fg'])]
        )
        self.style.configure(prefix + 'TEntry', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])
        # Treeview
        self.style.configure(prefix + 'Treeview',
            background=theme['tree_bg'],
            foreground=theme['tree_fg'],
            fieldbackground=theme['tree_bg'],
            bordercolor=theme['accent'],
            rowheight=26
        )
        self.style.map(prefix + 'Treeview',
            background=[('selected', theme['tree_select_bg'])],
            foreground=[('selected', theme['tree_select_fg'])]
        )
        # Progressbar
        self.style.configure(prefix + 'Horizontal.TProgressbar',
            background=theme['accent'],
            troughcolor=theme['entry_bg'],
            bordercolor=theme['bg']
        )
        # Combobox
        self.style.configure(prefix + 'TCombobox',
            fieldbackground=theme['entry_bg'],
            background=theme['entry_bg'],
            foreground=theme['entry_fg']
        )
        # Scrollbar
        self.style.configure(prefix + 'Vertical.TScrollbar',
            background=theme['tree_bg']
        )
        self.style.configure(prefix + 'Horizontal.TScrollbar',
            background=theme['tree_bg']
        )
    
    def refresh_theme(self):
        """Refresh theme when GUI theme changes with advanced styling and immediate responsiveness"""
        try:
            # Update current theme from marketplace
            self.marketplace.current_theme = self.marketplace._get_current_theme()
            
            # Update our theme dictionary
            self.theme_dict = self.marketplace.current_theme
            
            # Apply the new theme to all widgets
            self.apply_theme(self.theme_dict)
            
            # Apply advanced styling features
            self._setup_advanced_styling()
            
            # Update theme toggle button if it exists
            self._update_theme_button()
            
            # Log successful theme refresh
            if hasattr(self.marketplace.launcher_gui, 'log'):
                self.marketplace.launcher_gui.log(f"[Marketplace Window] Theme refreshed to: {self.marketplace.launcher_gui.current_theme}")
                
        except Exception as e:
            # Log error but don't crash
            if hasattr(self.marketplace.launcher_gui, 'log'):
                self.marketplace.launcher_gui.log(f"[Marketplace Window] Error refreshing theme: {e}")
            else:
                print(f"[Marketplace Window] Error refreshing theme: {e}")
    
    def _update_theme_button(self):
        """Update theme toggle button appearance based on current theme"""
        try:
            # Find theme button in the interface
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Button) and hasattr(grandchild, '_theme_button'):
                                    # Update button text based on current theme
                                    if self.marketplace.launcher_gui._dark_mode:
                                        grandchild.configure(text="☀️")
                                    else:
                                        grandchild.configure(text="🌙")
                                    break
        except Exception as e:
            # Silently continue if button update fails
            pass
    
    def _setup_advanced_styling(self):
        """Set up advanced styling features for the window"""
        theme = self.theme_dict
        
        # Add hover effects to buttons
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.bind('<Enter>', lambda e, w=widget: self._on_button_hover(w, True))
                widget.bind('<Leave>', lambda e, w=widget: self._on_button_hover(w, False))
        
        # Add smooth transitions (if supported)
        try:
            self.window.after(100, self._apply_smooth_transitions)
        except:
            pass
    
    def _on_button_hover(self, button, entering):
        """Handle button hover effects"""
        theme = self.theme_dict
        if entering:
            button.configure(style='ZWaifuMarketplace.TButton.Hover')
        else:
            button.configure(style='ZWaifuMarketplace.TButton')
    
    def _apply_smooth_transitions(self):
        """Apply smooth transition effects"""
        theme = self.theme_dict
        
        # Configure hover styles for buttons
        prefix = 'ZWaifuMarketplace.'
        self.style.configure(prefix + 'TButton.Hover', 
                           background=theme['accent'], 
                           foreground=theme['button_fg'])
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        # Toggle the main GUI theme
        self.marketplace.launcher_gui.toggle_theme()
        # Refresh the marketplace theme
        self.refresh_theme()
        # Update the theme button text
        theme_btn = self.window.winfo_children()[0].winfo_children()[0].winfo_children()[1]  # Get theme button
        theme_btn.configure(text="🌙" if self.marketplace.launcher_gui._dark_mode else "☀️")
    
    def show(self):
        """Show the marketplace window integrated with main GUI"""
        self.window = tk.Toplevel()
        self.window.title("🛒 Z-Waifu Plugin Marketplace")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'launcher_icon.png')
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.window.iconphoto(True, icon)
        except Exception:
            pass  # Icon not critical
        
        # Note: Modal behavior is set by main GUI for proper integration
        # self.window.transient() and self.window.grab_set() are called by main GUI
        
        # Apply theme to window using stored theme dictionary
        self.window.configure(bg=self.theme_dict.get('bg', '#1a1a1a'))
        
        # Store reference in marketplace for theme updates
        self.marketplace.marketplace_window = self.window
        
        # Set up custom styles
        self.setup_styles()
        
        self.create_interface()
        
        # Apply theme to all widgets after interface is created
        self._apply_theme_to_widgets(self.window, self.theme_dict)
        
        # Register with main GUI for theme updates
        if hasattr(self.marketplace.launcher_gui, 'register_theme_window'):
            self.marketplace.launcher_gui.register_theme_window(self.window)
        
    def create_interface(self):
        """Create the marketplace interface"""
        prefix = 'ZWaifuMarketplace.'
        theme = self.theme_dict
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10", style=prefix+'TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame, style=prefix+'TFrame')
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        header_label = ttk.Label(header_frame, text="Plugin Marketplace", font=("Arial", 16, "bold"), style=prefix+'TLabel')
        header_label.grid(row=0, column=0, sticky="w")
        
        # Quick access buttons frame
        quick_access_frame = ttk.Frame(header_frame, style=prefix+'TFrame')
        quick_access_frame.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Plugin marketplace button
        marketplace_btn = ttk.Button(quick_access_frame, text="🛒 Marketplace", 
                                   command=self.refresh_plugins, style=prefix+'TButton')
        marketplace_btn.grid(row=0, column=0, padx=(0, 5))
        self.create_tooltip(marketplace_btn, "Refresh plugin marketplace")
        
        # Theme toggle button
        theme_btn = ttk.Button(quick_access_frame, text="🌙" if self.marketplace.launcher_gui._dark_mode else "☀️", 
                              command=self.toggle_theme, style=prefix+'TButton')
        theme_btn.grid(row=0, column=1, padx=(5, 5))
        theme_btn._theme_button = True  # Mark as theme button for updates
        self.create_tooltip(theme_btn, "Toggle dark/light theme")
        
        refresh_btn = ttk.Button(quick_access_frame, text="⟳ Refresh", command=self.refresh_plugins, style=prefix+'TButton')
        refresh_btn.grid(row=0, column=2, padx=(5, 5))
        self.create_tooltip(refresh_btn, "Refresh plugin list from repository")
        
        installed_btn = ttk.Button(quick_access_frame, text="📦 Installed", command=self.show_installed, style=prefix+'TButton')
        installed_btn.grid(row=0, column=3, padx=(5, 5))
        self.create_tooltip(installed_btn, "View installed plugins")
        
        # New: Quick actions buttons
        quick_actions_frame = ttk.Frame(header_frame, style=prefix+'TFrame')
        quick_actions_frame.grid(row=0, column=2, padx=(10, 0), sticky="e")
        
        # Backup/Restore buttons
        backup_btn = ttk.Button(quick_actions_frame, text="💾 Backup", command=self.backup_plugins, style=prefix+'TButton')
        backup_btn.grid(row=0, column=0, padx=(0, 5))
        self.create_tooltip(backup_btn, "Backup all installed plugins")
        
        restore_btn = ttk.Button(quick_actions_frame, text="📥 Restore", command=self.restore_plugins, style=prefix+'TButton')
        restore_btn.grid(row=0, column=1, padx=(5, 5))
        self.create_tooltip(restore_btn, "Restore plugins from backup")
        
        # Settings button
        settings_btn = ttk.Button(quick_actions_frame, text="⚙️ Settings", command=self.open_settings, style=prefix+'TButton')
        settings_btn.grid(row=0, column=2, padx=(5, 5))
        self.create_tooltip(settings_btn, "Plugin marketplace settings")
        
        # Help button
        help_btn = ttk.Button(quick_actions_frame, text="❓ Help", command=self.show_help, style=prefix+'TButton')
        help_btn.grid(row=0, column=3, padx=(5, 0))
        self.create_tooltip(help_btn, "Show help and documentation")
        
        # Search and filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Search & Filter", padding="10", style=prefix+'TFrame')
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.columnconfigure(2, weight=1)
        
        search_label = ttk.Label(filter_frame, text="Search:", style=prefix+'TLabel')
        search_label.grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30, style=prefix+'TEntry')
        search_entry.grid(row=0, column=1, padx=(5, 10), sticky="ew")
        self.create_tooltip(search_entry, "Search plugins by name, description, or tags")
        
        category_label = ttk.Label(filter_frame, text="Category:", style=prefix+'TLabel')
        category_label.grid(row=0, column=2, sticky="w")
        self.category_var = tk.StringVar(value="all")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, width=15, style=prefix+'TCombobox')
        category_combo.grid(row=0, column=3, padx=(5, 0), sticky="ew")
        self.create_tooltip(category_combo, "Filter plugins by category")
        
        # New: Advanced filter controls
        advanced_filter_frame = ttk.Frame(filter_frame, style=prefix+'TFrame')
        advanced_filter_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        
        # Sort options
        sort_label = ttk.Label(advanced_filter_frame, text="Sort by:", style=prefix+'TLabel')
        sort_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_var = tk.StringVar(value="rating")
        sort_combo = ttk.Combobox(advanced_filter_frame, textvariable=self.sort_var, width=12, style=prefix+'TCombobox')
        sort_combo['values'] = ['rating', 'downloads', 'name', 'date', 'version']
        sort_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(sort_combo, "Sort plugins by different criteria")
        
        # Status filter
        status_label = ttk.Label(advanced_filter_frame, text="Status:", style=prefix+'TLabel')
        status_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(advanced_filter_frame, textvariable=self.status_var, width=12, style=prefix+'TCombobox')
        status_combo['values'] = ['all', 'installed', 'available', 'updates']
        status_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(status_combo, "Filter by plugin status")
        
        # Clear filters button
        clear_filters_btn = ttk.Button(advanced_filter_frame, text="Clear Filters", command=self.clear_filters, style=prefix+'TButton')
        clear_filters_btn.pack(side=tk.RIGHT)
        self.create_tooltip(clear_filters_btn, "Clear all search and filter criteria")
        
        # Load categories
        categories = ["all"] + self.marketplace.get_plugin_categories()
        category_combo['values'] = categories
        
        # Bind search and filters
        self.search_var.trace('w', lambda *args: self.filter_plugins())
        self.category_var.trace('w', lambda *args: self.filter_plugins())
        self.sort_var.trace('w', lambda *args: self.filter_plugins())
        self.status_var.trace('w', lambda *args: self.filter_plugins())
        
        # Plugin list with themed tabs
        list_frame = ttk.LabelFrame(main_frame, text="Available Plugins", padding="10", style=prefix+'TFrame')
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Create notebook for themed tabs
        self.plugin_notebook = ttk.Notebook(list_frame)
        self.plugin_notebook.grid(row=0, column=0, sticky="nsew")
        
        # All plugins tab
        all_plugins_frame = ttk.Frame(self.plugin_notebook, style=prefix+'TFrame')
        self.plugin_notebook.add(all_plugins_frame, text="All Plugins")
        
        columns = ('Name', 'Version', 'Category', 'Rating', 'Downloads', 'Status')
        self.plugin_list = ttk.Treeview(all_plugins_frame, columns=columns, show='headings', height=15, style=prefix+'Treeview')
        for col in columns:
            self.plugin_list.heading(col, text=col)
        self.plugin_list.column('Name', width=200)
        self.plugin_list.column('Version', width=80)
        self.plugin_list.column('Category', width=100)
        self.plugin_list.column('Rating', width=80)
        self.plugin_list.column('Downloads', width=100)
        self.plugin_list.column('Status', width=100)
        
        scrollbar = ttk.Scrollbar(all_plugins_frame, orient=tk.VERTICAL, command=self.plugin_list.yview, style=prefix+'Vertical.TScrollbar')
        self.plugin_list.configure(yscrollcommand=scrollbar.set)
        self.plugin_list.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Popular plugins tab
        popular_frame = ttk.Frame(self.plugin_notebook, style=prefix+'TFrame')
        self.plugin_notebook.add(popular_frame, text="Popular")
        
        self.popular_list = ttk.Treeview(popular_frame, columns=columns, show='headings', height=15, style=prefix+'Treeview')
        for col in columns:
            self.popular_list.heading(col, text=col)
        self.plugin_list.column('Name', width=200)
        self.plugin_list.column('Version', width=80)
        self.plugin_list.column('Category', width=100)
        self.plugin_list.column('Rating', width=80)
        self.plugin_list.column('Downloads', width=100)
        self.plugin_list.column('Status', width=100)
        
        popular_scrollbar = ttk.Scrollbar(popular_frame, orient=tk.VERTICAL, command=self.popular_list.yview, style=prefix+'Vertical.TScrollbar')
        self.popular_list.configure(yscrollcommand=popular_scrollbar.set)
        self.popular_list.grid(row=0, column=0, sticky="nsew")
        popular_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Recent plugins tab
        recent_frame = ttk.Frame(self.plugin_notebook, style=prefix+'TFrame')
        self.plugin_notebook.add(recent_frame, text="Recent")
        
        self.recent_list = ttk.Treeview(recent_frame, columns=columns, show='headings', height=15, style=prefix+'Treeview')
        for col in columns:
            self.recent_list.heading(col, text=col)
        self.plugin_list.column('Name', width=200)
        self.plugin_list.column('Version', width=80)
        self.plugin_list.column('Category', width=100)
        self.plugin_list.column('Rating', width=80)
        self.plugin_list.column('Downloads', width=100)
        self.plugin_list.column('Status', width=100)
        
        recent_scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_list.yview, style=prefix+'Vertical.TScrollbar')
        self.recent_list.configure(yscrollcommand=recent_scrollbar.set)
        self.recent_list.grid(row=0, column=0, sticky="nsew")
        recent_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Plugin details
        details_frame = ttk.LabelFrame(main_frame, text="Plugin Details", padding="10", style=prefix+'TFrame')
        details_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        # Plugin card preview
        self.plugin_card_frame = ttk.Frame(details_frame, style=prefix+'TFrame')
        self.plugin_card_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add border and padding to card
        card_container = tk.Frame(self.plugin_card_frame, 
                                bg=theme['card_bg'], 
                                relief=tk.RAISED, 
                                bd=2,
                                highlightbackground=theme['border_color'],
                                highlightthickness=1)
        card_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Plugin icon and basic info
        self.plugin_icon_label = ttk.Label(card_container, text="🔌", font=("Arial", 24), style=prefix+'TLabel')
        self.plugin_icon_label.pack(side=tk.LEFT, padx=(10, 10))
        
        self.plugin_info_frame = ttk.Frame(card_container, style=prefix+'TFrame')
        self.plugin_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.plugin_name_label = ttk.Label(self.plugin_info_frame, text="Select a plugin", font=("Arial", 14, "bold"), style=prefix+'TLabel')
        self.plugin_name_label.pack(anchor=tk.W)
        
        self.plugin_meta_label = ttk.Label(self.plugin_info_frame, text="", style=prefix+'TLabel')
        self.plugin_meta_label.pack(anchor=tk.W)
        
        # Plugin rating and downloads
        self.plugin_stats_frame = ttk.Frame(card_container, style=prefix+'TFrame')
        self.plugin_stats_frame.pack(side=tk.RIGHT, padx=(0, 10))
        
        self.plugin_rating_label = ttk.Label(self.plugin_stats_frame, text="", style=prefix+'TLabel')
        self.plugin_rating_label.pack(anchor=tk.E)
        
        self.plugin_downloads_label = ttk.Label(self.plugin_stats_frame, text="", style=prefix+'TLabel')
        self.plugin_downloads_label.pack(anchor=tk.E)
        
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD, state=tk.DISABLED, bg=theme['entry_bg'], fg=theme['entry_fg'], insertbackground=theme['fg'])
        self.details_text.pack(fill=tk.X)
        
        config_reviews_frame = ttk.Frame(details_frame, style=prefix+'TFrame')
        config_reviews_frame.pack(fill=tk.X, pady=(5, 0))
        self.config_btn = ttk.Button(config_reviews_frame, text="⚙ Configure Plugin", command=self.configure_selected, state=tk.DISABLED, style=prefix+'TButton')
        self.config_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(self.config_btn, "Configure plugin settings")
        
        self.reviews_btn = ttk.Button(config_reviews_frame, text="★ Show Reviews", command=self.show_reviews, state=tk.DISABLED, style=prefix+'TButton')
        self.reviews_btn.pack(side=tk.LEFT)
        self.create_tooltip(self.reviews_btn, "View user reviews and ratings")
        
        # New: Additional action buttons
        self.documentation_btn = ttk.Button(config_reviews_frame, text="📖 Documentation", command=self.show_documentation, state=tk.DISABLED, style=prefix+'TButton')
        self.documentation_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.create_tooltip(self.documentation_btn, "View plugin documentation")
        
        self.changelog_btn = ttk.Button(config_reviews_frame, text="📝 Changelog", command=self.show_changelog, state=tk.DISABLED, style=prefix+'TButton')
        self.changelog_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.create_tooltip(self.changelog_btn, "View plugin changelog")
        
        # Debug button for creating test plugin
        self.debug_btn = ttk.Button(config_reviews_frame, text="🐛 Create Test Plugin", command=self.create_test_plugin, style=prefix+'TButton')
        self.debug_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.create_tooltip(self.debug_btn, "Create a test plugin for debugging")
        
        # Action buttons
        button_frame = ttk.Frame(main_frame, style=prefix+'TFrame')
        button_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        self.install_btn = ttk.Button(button_frame, text="⬇ Install", command=self.install_selected, state=tk.DISABLED, style=prefix+'TButton')
        self.install_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(self.install_btn, "Install the selected plugin")
        
        self.uninstall_btn = ttk.Button(button_frame, text="🗑 Uninstall", command=self.uninstall_selected, state=tk.DISABLED, style=prefix+'TButton')
        self.uninstall_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.uninstall_btn, "Uninstall the selected plugin")
        
        self.update_btn = ttk.Button(button_frame, text="⟳ Update", command=self.update_selected, state=tk.DISABLED, style=prefix+'TButton')
        self.update_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.update_btn, "Update the selected plugin to latest version")
        
        # New: Batch operations
        batch_frame = ttk.Frame(button_frame, style=prefix+'TFrame')
        batch_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        self.batch_install_btn = ttk.Button(batch_frame, text="⬇ Batch Install", command=self.batch_install, style=prefix+'TButton')
        self.batch_install_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.create_tooltip(self.batch_install_btn, "Install multiple selected plugins")
        
        self.batch_update_btn = ttk.Button(batch_frame, text="⟳ Batch Update", command=self.batch_update, style=prefix+'TButton')
        self.batch_update_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.batch_update_btn, "Update all installed plugins")
        
        close_btn = ttk.Button(button_frame, text="✖ Close", command=self.window.destroy, style=prefix+'TButton')
        close_btn.pack(side=tk.RIGHT)
        self.create_tooltip(close_btn, "Close the plugin marketplace")
        
        # Status bar with additional info
        status_frame = ttk.Frame(self.window, style=prefix+'TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, anchor="w", style=prefix+'TLabel')
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Plugin count
        self.plugin_count_var = tk.StringVar(value="0 plugins available")
        plugin_count_label = ttk.Label(status_frame, textvariable=self.plugin_count_var, anchor="e", style=prefix+'TLabel')
        plugin_count_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Progress bar (hidden by default)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.window, variable=self.progress_var, style=prefix+'Horizontal.TProgressbar')
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, before=status_bar)
        self.progress_bar.pack_forget()  # Hide initially
        
        # Bind events
        self.plugin_list.bind('<<TreeviewSelect>>', self.on_plugin_select)
        self.popular_list.bind('<<TreeviewSelect>>', self.on_plugin_select)
        self.recent_list.bind('<<TreeviewSelect>>', self.on_plugin_select)
        
        # Keyboard navigation
        self.window.bind('<Return>', lambda e: self.install_selected())
        self.window.bind('<Delete>', lambda e: self.uninstall_selected())
        self.window.bind('<F5>', lambda e: self.refresh_plugins())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        
        # Focus management
        self.plugin_list.focus_set()
        
        # Load plugins
        self.load_plugins()
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Use theme colors for tooltip
            theme = self.theme_dict
            label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                           background=theme['tooltip_bg'], 
                           foreground=theme['tooltip_fg'],
                           relief=tk.SOLID, 
                           borderwidth=1,
                           font=("Arial", "9", "normal"),
                           padx=8, pady=4)
            label.pack()
            
            # Add border color
            tooltip.configure(bg=theme['tooltip_border'])
            
            def hide_tooltip(event):
                tooltip.destroy()
            
            widget.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Button-1>', hide_tooltip)
            
            # Auto-hide after 3 seconds
            tooltip.after(3000, hide_tooltip)
        
        widget.bind('<Enter>', show_tooltip)
    
    def load_plugins(self):
        """Load plugins into the list with enhanced categorization"""
        self.plugin_list.delete(*self.plugin_list.get_children())
        self.popular_list.delete(*self.popular_list.get_children())
        self.recent_list.delete(*self.recent_list.get_children())
        
        plugins = self.marketplace.get_available_plugins()
        
        # Sort plugins by rating for popular list
        popular_plugins = sorted(plugins, key=lambda x: x.get('rating', 0), reverse=True)[:10]
        
        # Sort plugins by last updated for recent list
        recent_plugins = sorted(plugins, key=lambda x: x.get('last_updated', ''), reverse=True)[:10]
        
        for i, plugin in enumerate(plugins):
            status = "Installed" if plugin['is_installed'] else "Available"
            if plugin['is_installed'] and plugin.get('installed_version') != plugin.get('version'):
                status = "Update Available"
            
            item = self.plugin_list.insert('', 'end', values=(
                plugin.get('name', ''),
                plugin.get('version', ''),
                plugin.get('category', ''),
                f"{plugin.get('rating', 0):.1f}",
                plugin.get('downloads', 0),
                status
            ), tags=(plugin['id'],))
            
            # Add alternating row colors
            if i % 2 == 0:
                self.plugin_list.tag_configure('even_row', background=self.theme_dict['tree_bg'])
                self.plugin_list.item(item, tags=(plugin['id'], 'even_row'))
            else:
                alt_bg = self.theme_dict['hover_bg']
                self.plugin_list.tag_configure('odd_row', background=alt_bg)
                self.plugin_list.item(item, tags=(plugin['id'], 'odd_row'))
        
        # Load popular plugins
        for plugin in popular_plugins:
            status = "Installed" if plugin['is_installed'] else "Available"
            if plugin['is_installed'] and plugin.get('installed_version') != plugin.get('version'):
                status = "Update Available"
            
            self.popular_list.insert('', 'end', values=(
                plugin.get('name', ''),
                plugin.get('version', ''),
                plugin.get('category', ''),
                f"{plugin.get('rating', 0):.1f}",
                plugin.get('downloads', 0),
                status
            ), tags=(plugin['id'],))
        
        # Load recent plugins
        for plugin in recent_plugins:
            status = "Installed" if plugin['is_installed'] else "Available"
            if plugin['is_installed'] and plugin.get('installed_version') != plugin.get('version'):
                status = "Update Available"
            
            self.recent_list.insert('', 'end', values=(
                plugin.get('name', ''),
                plugin.get('version', ''),
                plugin.get('category', ''),
                f"{plugin.get('rating', 0):.1f}",
                plugin.get('downloads', 0),
                status
            ), tags=(plugin['id'],))
        
        # Update plugin count
        if hasattr(self, 'plugin_count_var'):
            installed_count = sum(1 for plugin in plugins if plugin['is_installed'])
            self.plugin_count_var.set(f"{len(plugins)} plugins available ({installed_count} installed)")
    
    def filter_plugins(self):
        """Filter plugins based on search and category with enhanced sorting"""
        search_term = self.search_var.get().strip()
        category = self.category_var.get()
        sort_by = self.sort_var.get()
        status_filter = self.status_var.get()
        
        if category == "all":
            category = None
        
        plugins = self.marketplace.get_available_plugins(category, search_term)
        
        # Apply status filter
        if status_filter != "all":
            if status_filter == "installed":
                plugins = [p for p in plugins if p['is_installed']]
            elif status_filter == "available":
                plugins = [p for p in plugins if not p['is_installed']]
            elif status_filter == "updates":
                plugins = [p for p in plugins if p['is_installed'] and p.get('installed_version') != p.get('version')]
        
        # Apply sorting
        if sort_by == "rating":
            plugins.sort(key=lambda x: x.get('rating', 0), reverse=True)
        elif sort_by == "downloads":
            plugins.sort(key=lambda x: x.get('downloads', 0), reverse=True)
        elif sort_by == "name":
            plugins.sort(key=lambda x: x.get('name', '').lower())
        elif sort_by == "date":
            plugins.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
        elif sort_by == "version":
            plugins.sort(key=lambda x: x.get('version', ''), reverse=True)
        
        # Update all treeviews
        for treeview in [self.plugin_list, self.popular_list, self.recent_list]:
            treeview.delete(*treeview.get_children())
        
        for i, plugin in enumerate(plugins):
            status = "Installed" if plugin['is_installed'] else "Available"
            if plugin['is_installed'] and plugin.get('installed_version') != plugin.get('version'):
                status = "Update Available"
            
            item = self.plugin_list.insert('', 'end', values=(
                plugin.get('name', ''),
                plugin.get('version', ''),
                plugin.get('category', ''),
                f"{plugin.get('rating', 0):.1f}",
                plugin.get('downloads', 0),
                status
            ), tags=(plugin['id'],))
            
            # Add alternating row colors
            if i % 2 == 0:
                self.plugin_list.tag_configure('even_row', background=self.theme_dict['tree_bg'])
                self.plugin_list.item(item, tags=(plugin['id'], 'even_row'))
            else:
                alt_bg = self.theme_dict['hover_bg']
                self.plugin_list.tag_configure('odd_row', background=alt_bg)
                self.plugin_list.item(item, tags=(plugin['id'], 'odd_row'))
            
            # Add to popular list (top 10 by rating)
            if i < 10 and plugin.get('rating', 0) >= 4.0:
                self.popular_list.insert('', 'end', values=(
                    plugin.get('name', ''),
                    plugin.get('version', ''),
                    plugin.get('category', ''),
                    f"{plugin.get('rating', 0):.1f}",
                    plugin.get('downloads', 0),
                    status
                ), tags=(plugin['id'],))
            
            # Add to recent list (last 10 updated)
            if i < 10:
                self.recent_list.insert('', 'end', values=(
                    plugin.get('name', ''),
                    plugin.get('version', ''),
                    plugin.get('category', ''),
                    f"{plugin.get('rating', 0):.1f}",
                    plugin.get('downloads', 0),
                    status
                ), tags=(plugin['id'],))
        
        # Update plugin count for filtered results
        if hasattr(self, 'plugin_count_var'):
            installed_count = sum(1 for plugin in plugins if plugin['is_installed'])
            self.plugin_count_var.set(f"{len(plugins)} plugins found ({installed_count} installed)")
    
    def on_plugin_select(self, event):
        """Handle plugin selection from any treeview"""
        # Determine which treeview was clicked
        treeview = event.widget
        
        selection = treeview.selection()
        if not selection:
            return
        
        item = treeview.item(selection[0])
        plugin_id = item['tags'][0]
        
        # Get plugin details
        plugin_data = self.marketplace.plugin_registry.get('plugins', {}).get(plugin_id)
        if not plugin_data:
            return
        
        # Update plugin card preview
        self.plugin_icon_label.config(text=plugin_data.get('icon', '🔌'))
        self.plugin_name_label.config(text=plugin_data.get('name', plugin_id))
        self.plugin_meta_label.config(text=f"Version: {plugin_data.get('version', '')} | Author: {plugin_data.get('author', '')}")
        self.plugin_rating_label.config(text=f"Rating: {plugin_data.get('rating', 0):.1f}/5.0")
        self.plugin_downloads_label.config(text=f"Downloads: {plugin_data.get('downloads', 0)}")
        
        # Update details text
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        
        details = f"""Name: {plugin_data.get('name', '')}
Version: {plugin_data.get('version', '')}
Author: {plugin_data.get('author', '')}
Category: {plugin_data.get('category', '')}
Rating: {plugin_data.get('rating', 0):.1f}/5.0
Downloads: {plugin_data.get('downloads', 0)}
Last Updated: {plugin_data.get('last_updated', 'Unknown')}

Description:
{plugin_data.get('description', '')}

Tags: {', '.join(plugin_data.get('tags', []))}

Dependencies: {', '.join(plugin_data.get('dependencies', ['None']))}

Documentation: {plugin_data.get('documentation_url', 'Not available')}
"""
        
        self.details_text.insert('1.0', details)
        self.details_text.config(state=tk.DISABLED)
        
        # Update button states
        is_installed = plugin_id in self.marketplace.installed_plugins
        has_update = is_installed and self.marketplace.installed_plugins[plugin_id].get('version') != plugin_data.get('version')
        
        if is_installed:
            self.install_btn.config(state=tk.DISABLED)
            self.uninstall_btn.config(state=tk.NORMAL)
            if has_update:
                self.update_btn.config(state=tk.NORMAL)
            else:
                self.update_btn.config(state=tk.DISABLED)
            self.config_btn.config(state=tk.NORMAL)
        else:
            self.install_btn.config(state=tk.NORMAL)
            self.uninstall_btn.config(state=tk.DISABLED)
            self.update_btn.config(state=tk.DISABLED)
            self.config_btn.config(state=tk.DISABLED)
        
        # Reviews button enabled if reviews exist
        if plugin_data.get('reviews'):
            self.reviews_btn.config(state=tk.NORMAL)
        else:
            self.reviews_btn.config(state=tk.DISABLED)
        
        # Documentation and changelog buttons
        doc_url = plugin_data.get('documentation_url')
        if doc_url and doc_url != 'Not available':
            self.documentation_btn.config(state=tk.NORMAL)
        else:
            self.documentation_btn.config(state=tk.DISABLED)
        
        self.changelog_btn.config(state=tk.NORMAL)  # Always available for now
    
    def install_selected(self):
        """Install selected plugin"""
        selection = self.plugin_list.selection()
        if not selection:
            return
        
        item = self.plugin_list.item(selection[0])
        plugin_id = item['tags'][0]
        
        # Show confirmation dialog
        plugin_data = self.marketplace.plugin_registry.get('plugins', {}).get(plugin_id)
        if not plugin_data:
            return
        
        result = messagebox.askyesno(
            "Install Plugin",
            f"Are you sure you want to install '{plugin_data.get('name', plugin_id)}'?\n\n"
            f"Version: {plugin_data.get('version', '')}\n"
            f"Author: {plugin_data.get('author', '')}\n\n"
            f"Dependencies: {', '.join(plugin_data.get('dependencies', ['None']))}"
        )
        
        if result:
            # Show progress bar
            self.show_progress(f"Installing {plugin_data.get('name', plugin_id)}...")
            
            def install_thread():
                try:
                    # Simulate progress updates
                    self.update_progress(20, "Downloading plugin...")
                    time.sleep(0.5)
                    self.update_progress(40, "Extracting files...")
                    time.sleep(0.5)
                    self.update_progress(60, "Installing dependencies...")
                    time.sleep(0.5)
                    self.update_progress(80, "Finalizing installation...")
                    time.sleep(0.5)
                    
                    success, message = self.marketplace.install_plugin(plugin_id)
                    
                    self.window.after(0, lambda: self.install_complete(success, message))
                except Exception as e:
                    self.window.after(0, lambda: self.install_complete(False, f"Installation failed: {e}"))
            
            threading.Thread(target=install_thread, daemon=True).start()
    
    def install_complete(self, success: bool, message: str):
        """Handle installation completion"""
        self.hide_progress()
        
        if success:
            self.show_status(f"✅ {message}", 5000, "success")
            self.load_plugins()
        else:
            self.show_status(f"❌ {message}", 5000, "error")
            messagebox.showerror("Installation Error", message)
    
    def uninstall_selected(self):
        """Uninstall selected plugin"""
        selection = self.plugin_list.selection()
        if not selection:
            return
        
        item = self.plugin_list.item(selection[0])
        plugin_id = item['tags'][0]
        
        result = messagebox.askyesno(
            "Uninstall Plugin",
            f"Are you sure you want to uninstall '{plugin_id}'?\n\n"
            "This will remove the plugin and all its data."
        )
        
        if result:
            success, message = self.marketplace.uninstall_plugin(plugin_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_plugins()
            else:
                messagebox.showerror("Error", message)
    
    def update_selected(self):
        """Update selected plugin"""
        selection = self.plugin_list.selection()
        if not selection:
            return
        
        item = self.plugin_list.item(selection[0])
        plugin_id = item['tags'][0]
        
        result = messagebox.askyesno(
            "Update Plugin",
            f"Are you sure you want to update '{plugin_id}'?"
        )
        
        if result:
            success, message = self.marketplace.update_plugin(plugin_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_plugins()
            else:
                messagebox.showerror("Error", message)
    
    def refresh_plugins(self):
        """Refresh the plugin list"""
        self.show_status("Refreshing plugin registry...", "info")
        if self.marketplace.refresh_registry():
            self.load_plugins()
            self.show_status("✅ Plugin registry refreshed successfully", 3000, "success")
        else:
            self.show_status("❌ Failed to refresh plugin registry", 3000, "error")
            messagebox.showerror("Error", "Failed to refresh plugin registry")
    
    def show_installed(self):
        """Show installed plugins window integrated with main GUI"""
        try:
            installed = InstalledPluginsWindow(self.marketplace)
            installed.show()
            
            # Ensure the installed plugins window is properly themed and modal
            if hasattr(installed, 'window') and installed.window:
                # Set as child of main window for proper modal behavior
                installed.window.transient(self.marketplace.launcher_gui.root)
                installed.window.grab_set()
                
                # Center the window relative to main GUI
                self.marketplace.launcher_gui._center_window_on_parent(installed.window, self.marketplace.launcher_gui.root)
                
                # Apply current theme immediately
                self.marketplace.launcher_gui._theme_popup_window(installed.window)
                
                # Register for theme updates
                self.marketplace.launcher_gui.register_theme_window(installed.window)
                
                # Focus the installed plugins window
                installed.window.focus_set()
                installed.window.lift()
                
        except Exception as e:
            self.show_status(f"❌ Error opening installed plugins: {e}", 5000, "error")
            messagebox.showerror("Error", f"Failed to open installed plugins: {e}")

    def configure_selected(self):
        selection = self.plugin_list.selection()
        if not selection:
            self.show_status("Please select a plugin to configure", 2000, "warning")
            return
        item = self.plugin_list.item(selection[0])
        plugin_id = item['tags'][0]
        # Try to get plugin instance from PluginManager
        plugin_instance = None
        if hasattr(self.marketplace.launcher_gui, 'plugin_manager'):
            plugin_manager = self.marketplace.launcher_gui.plugin_manager
            if hasattr(plugin_manager, 'plugins') and plugin_id in plugin_manager.plugins:
                plugin_instance = plugin_manager.plugins[plugin_id]
        if plugin_instance and hasattr(plugin_instance, 'get_config') and hasattr(plugin_instance, 'set_config'):
            config = plugin_instance.get_config()
            config_str = json.dumps(config, indent=2)
            new_config_str = simpledialog.askstring("Configure Plugin", f"Edit config for {plugin_id} (JSON):", initialvalue=config_str)
            if new_config_str:
                try:
                    new_config = json.loads(new_config_str)
                    plugin_instance.set_config(new_config)
                    self.show_status("✅ Plugin configuration updated successfully", 3000, "success")
                except Exception as e:
                    self.show_status(f"❌ Invalid configuration: {e}", 5000, "error")
                    messagebox.showerror("Error", f"Invalid config: {e}")
        else:
            self.show_status("This plugin does not support configuration", 3000, "warning")
            messagebox.showinfo("Not Supported", "This plugin does not support configuration.")

    def show_reviews(self):
        selection = self.plugin_list.selection()
        if not selection:
            self.show_status("Please select a plugin to view reviews", 2000, "warning")
            return
        item = self.plugin_list.item(selection[0])
        plugin_id = item['tags'][0]
        plugin_data = self.marketplace.plugin_registry.get('plugins', {}).get(plugin_id)
        if not plugin_data or not plugin_data.get('reviews'):
            self.show_status("No reviews available for this plugin", 3000, "info")
            messagebox.showinfo("No Reviews", "No reviews available for this plugin.")
            return
        reviews = plugin_data['reviews']
        reviews_text = "\n\n".join([f"Rating: {r.get('rating', '?')}/5\nBy: {r.get('author', 'Anonymous')}\n{r.get('text', '')}" for r in reviews])
        messagebox.showinfo(f"Reviews for {plugin_data.get('name', plugin_id)}", reviews_text)
    
    def create_test_plugin(self):
        """Create a test plugin for debugging"""
        try:
            plugin_name = simpledialog.askstring("Create Test Plugin", "Enter test plugin name:", initialvalue="test_plugin")
            if plugin_name:
                if self.marketplace.create_test_plugin(plugin_name):
                    self.show_status(f"✅ Created test plugin: {plugin_name}", 3000, "success")
                    messagebox.showinfo("Success", f"Test plugin '{plugin_name}' created successfully!\n\nYou can now reload plugins to see it in the list.")
                else:
                    self.show_status(f"❌ Failed to create test plugin: {plugin_name}", 3000, "error")
                    messagebox.showerror("Error", f"Failed to create test plugin: {plugin_name}")
        except Exception as e:
            self.show_status(f"❌ Error creating test plugin: {e}", 3000, "error")
            messagebox.showerror("Error", f"Error creating test plugin: {e}")

    def backup_plugins(self):
        """Backup all installed plugins"""
        try:
            backup_dir = os.path.join(self.marketplace.plugins_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"plugins_backup_{timestamp}.zip")
            
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup installed plugins data
                if os.path.exists(self.marketplace.installed_plugins_file):
                    zipf.write(self.marketplace.installed_plugins_file, 'installed_plugins.json')
                
                # Backup plugin directories
                for plugin_id in self.marketplace.installed_plugins:
                    plugin_dir = os.path.join(self.marketplace.plugins_dir, plugin_id)
                    if os.path.exists(plugin_dir):
                        for root, dirs, files in os.walk(plugin_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, self.marketplace.plugins_dir)
                                zipf.write(file_path, arc_name)
            
            self.show_status(f"✅ Plugins backed up to: {backup_file}", 5000, "success")
            messagebox.showinfo("Backup Complete", f"All installed plugins have been backed up to:\n{backup_file}")
            
        except Exception as e:
            self.show_status(f"❌ Backup failed: {e}", 5000, "error")
            messagebox.showerror("Backup Error", f"Failed to backup plugins: {e}")

    def restore_plugins(self):
        """Restore plugins from backup"""
        try:
            backup_dir = os.path.join(self.marketplace.plugins_dir, 'backups')
            if not os.path.exists(backup_dir):
                messagebox.showwarning("No Backups", "No backup directory found.")
                return
            
            # Get list of backup files
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip') and f.startswith('plugins_backup_')]
            if not backup_files:
                messagebox.showwarning("No Backups", "No backup files found.")
                return
            
            # Let user select backup file
            backup_file = filedialog.askopenfilename(
                title="Select Backup File",
                initialdir=backup_dir,
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
            )
            
            if not backup_file:
                return
            
            # Confirm restoration
            result = messagebox.askyesno(
                "Confirm Restore",
                "This will overwrite existing plugins. Are you sure you want to continue?"
            )
            
            if result:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(self.marketplace.plugins_dir)
                
                # Reload installed plugins
                self.marketplace.installed_plugins = self.marketplace.load_installed_plugins()
                
                self.show_status("✅ Plugins restored successfully", 5000, "success")
                messagebox.showinfo("Restore Complete", "Plugins have been restored from backup.")
                
                # Refresh the plugin list
                self.load_plugins()
                
        except Exception as e:
            self.show_status(f"❌ Restore failed: {e}", 5000, "error")
            messagebox.showerror("Restore Error", f"Failed to restore plugins: {e}")

    def open_settings(self):
        """Open plugin marketplace settings"""
        try:
            settings_window = tk.Toplevel(self.window)
            settings_window.title("Plugin Marketplace Settings")
            settings_window.geometry("500x400")
            settings_window.resizable(True, True)
            
            # Apply theme
            self.marketplace._apply_theme_to_window(settings_window)
            
            # Settings content
            main_frame = ttk.Frame(settings_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Auto-update settings
            update_frame = ttk.LabelFrame(main_frame, text="Auto-Update Settings")
            update_frame.pack(fill=tk.X, pady=(0, 10))
            
            self.auto_update_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(update_frame, text="Check for updates automatically", 
                           variable=self.auto_update_var).pack(anchor=tk.W, padx=5, pady=2)
            
            self.auto_install_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(update_frame, text="Auto-install security updates", 
                           variable=self.auto_install_var).pack(anchor=tk.W, padx=5, pady=2)
            
            # Repository settings
            repo_frame = ttk.LabelFrame(main_frame, text="Repository Settings")
            repo_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(repo_frame, text="Repository URL:").pack(anchor=tk.W, padx=5, pady=2)
            self.repo_url_var = tk.StringVar(value=self.marketplace.marketplace_url)
            repo_entry = ttk.Entry(repo_frame, textvariable=self.repo_url_var, width=50)
            repo_entry.pack(fill=tk.X, padx=5, pady=2)
            
            # Cache settings
            cache_frame = ttk.LabelFrame(main_frame, text="Cache Settings")
            cache_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(cache_frame, text="Cache duration (hours):").pack(anchor=tk.W, padx=5, pady=2)
            self.cache_duration_var = tk.StringVar(value="1")
            cache_entry = ttk.Entry(cache_frame, textvariable=self.cache_duration_var, width=10)
            cache_entry.pack(anchor=tk.W, padx=5, pady=2)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(button_frame, text="Save", command=lambda: self.save_settings(settings_window)).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {e}")

    def save_settings(self, settings_window):
        """Save marketplace settings"""
        try:
            # Save settings to config file
            settings = {
                'auto_update': self.auto_update_var.get(),
                'auto_install': self.auto_install_var.get(),
                'repository_url': self.repo_url_var.get(),
                'cache_duration': int(self.cache_duration_var.get())
            }
            
            settings_file = os.path.join(self.marketplace.marketplace_dir, 'settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            settings_window.destroy()
            self.show_status("✅ Settings saved successfully", 3000, "success")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def show_help(self):
        """Show help and documentation"""
        try:
            help_text = """
Plugin Marketplace Help

📖 Getting Started:
• Browse plugins in the "All Plugins" tab
• Use search and filters to find specific plugins
• Click on a plugin to view details and install

🔍 Filtering & Sorting:
• Search: Type keywords to search plugin names, descriptions, and tags
• Category: Filter by plugin category (monitoring, automation, etc.)
• Sort by: Choose sorting criteria (rating, downloads, name, date, version)
• Status: Filter by installation status (all, installed, available, updates)

📦 Installation:
• Select a plugin and click "Install"
• Dependencies will be automatically installed
• Installation progress is shown in the status bar

⚙️ Management:
• Configure: Modify plugin settings (if supported)
• Update: Install the latest version of a plugin
• Uninstall: Remove a plugin and its data

🛠️ Advanced Features:
• Batch Install: Install multiple selected plugins
• Batch Update: Update all installed plugins at once
• Backup/Restore: Create and restore plugin backups
• Settings: Configure marketplace behavior

🔧 Troubleshooting:
• If installation fails, check the status bar for error messages
• Use "Reload Plugins" to refresh the plugin list
• Check "Installed Plugins" to see what's currently installed

For more information, visit the plugin documentation.
"""
            
            help_window = tk.Toplevel(self.window)
            help_window.title("Plugin Marketplace Help")
            help_window.geometry("600x500")
            help_window.resizable(True, True)
            
            # Apply theme
            self.marketplace._apply_theme_to_window(help_window)
            
            # Help content
            text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Apply theme to text widget
            theme = self.theme_dict
            text_widget.configure(
                bg=theme['entry_bg'],
                fg=theme['entry_fg'],
                insertbackground=theme['fg'],
                selectbackground=theme['accent'],
                selectforeground=theme['tree_select_fg']
            )
            
            text_widget.insert('1.0', help_text)
            text_widget.config(state=tk.DISABLED)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show help: {e}")

    def show_documentation(self):
        """Show plugin documentation"""
        selection = self.plugin_list.selection()
        if not selection:
            self.show_status("Please select a plugin to view documentation", 2000, "warning")
            return
        
        item = self.plugin_list.item(selection[0])
        plugin_id = item['tags'][0]
        plugin_data = self.marketplace.plugin_registry.get('plugins', {}).get(plugin_id)
        
        if not plugin_data:
            self.show_status("Plugin data not found", 2000, "error")
            return
        
        doc_url = plugin_data.get('documentation_url')
        if not doc_url or doc_url == 'Not available':
            self.show_status("No documentation available for this plugin", 3000, "info")
            messagebox.showinfo("No Documentation", "This plugin doesn't have documentation available.")
            return
        
        try:
            import webbrowser
            webbrowser.open(doc_url)
            self.show_status("Documentation opened in browser", 2000, "success")
        except Exception as e:
            self.show_status(f"Failed to open documentation: {e}", 3000, "error")
            messagebox.showerror("Error", f"Failed to open documentation: {e}")

    def show_changelog(self):
        """Show plugin changelog"""
        selection = self.plugin_list.selection()
        if not selection:
            self.show_status("Please select a plugin to view changelog", 2000, "warning")
            return
        
        item = self.plugin_list.item(selection[0])
        plugin_id = item['tags'][0]
        plugin_data = self.marketplace.plugin_registry.get('plugins', {}).get(plugin_id)
        
        if not plugin_data:
            self.show_status("Plugin data not found", 2000, "error")
            return
        
        # For now, show a sample changelog since we don't have real changelog data
        changelog_text = f"""
Changelog for {plugin_data.get('name', plugin_id)}

Version {plugin_data.get('version', '1.0.0')} - {plugin_data.get('last_updated', 'Unknown')}
• Initial release
• Basic functionality implemented
• Documentation added

Version 0.9.0 - Development
• Beta testing phase
• Bug fixes and improvements
• Performance optimizations

For detailed changelog information, please visit the plugin's documentation page.
"""
        
        changelog_window = tk.Toplevel(self.window)
        changelog_window.title(f"Changelog - {plugin_data.get('name', plugin_id)}")
        changelog_window.geometry("500x400")
        changelog_window.resizable(True, True)
        
        # Apply theme
        self.marketplace._apply_theme_to_window(changelog_window)
        
        # Changelog content
        text_widget = tk.Text(changelog_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Apply theme to text widget
        theme = self.theme_dict
        text_widget.configure(
            bg=theme['entry_bg'],
            fg=theme['entry_fg'],
            insertbackground=theme['fg'],
            selectbackground=theme['accent'],
            selectforeground=theme['tree_select_fg']
        )
        
        text_widget.insert('1.0', changelog_text)
        text_widget.config(state=tk.DISABLED)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(changelog_window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

    def batch_install(self):
        """Install multiple selected plugins"""
        try:
            # Get all selected items from all treeviews
            selected_items = []
            for treeview in [self.plugin_list, self.popular_list, self.recent_list]:
                selected_items.extend(treeview.selection())
            
            if not selected_items:
                self.show_status("Please select plugins to install", 2000, "warning")
                return
            
            # Get unique plugin IDs
            plugin_ids = set()
            for item in selected_items:
                plugin_id = treeview.item(item)['tags'][0]
                if plugin_id not in self.marketplace.installed_plugins:
                    plugin_ids.add(plugin_id)
            
            if not plugin_ids:
                self.show_status("All selected plugins are already installed", 2000, "info")
                return
            
            # Confirm batch installation
            result = messagebox.askyesno(
                "Batch Install",
                f"Install {len(plugin_ids)} plugins?\n\n" + "\n".join(plugin_ids)
            )
            
            if result:
                self.show_progress(f"Installing {len(plugin_ids)} plugins...")
                
                def install_thread():
                    try:
                        success_count = 0
                        for i, plugin_id in enumerate(plugin_ids):
                            self.update_progress((i / len(plugin_ids)) * 100, f"Installing {plugin_id}...")
                            success, message = self.marketplace.install_plugin(plugin_id)
                            if success:
                                success_count += 1
                            time.sleep(0.5)  # Small delay between installations
                        
                        self.window.after(0, lambda: self.batch_install_complete(success_count, len(plugin_ids)))
                    except Exception as e:
                        self.window.after(0, lambda: self.batch_install_complete(0, len(plugin_ids), str(e)))
                
                threading.Thread(target=install_thread, daemon=True).start()
                
        except Exception as e:
            self.show_status(f"❌ Batch install failed: {e}", 5000, "error")
            messagebox.showerror("Error", f"Batch install failed: {e}")

    def batch_install_complete(self, success_count, total_count, error=None):
        """Handle batch installation completion"""
        self.hide_progress()
        
        if error:
            self.show_status(f"❌ Batch install failed: {error}", 5000, "error")
            messagebox.showerror("Batch Install Error", f"Failed to install plugins: {error}")
        else:
            self.show_status(f"✅ Successfully installed {success_count}/{total_count} plugins", 5000, "success")
            messagebox.showinfo("Batch Install Complete", f"Successfully installed {success_count} out of {total_count} plugins.")
            self.load_plugins()

    def batch_update(self):
        """Update all installed plugins"""
        try:
            installed_plugins = list(self.marketplace.installed_plugins.keys())
            if not installed_plugins:
                self.show_status("No plugins installed to update", 2000, "info")
                return
            
            # Check for updates
            plugins_with_updates = []
            for plugin_id in installed_plugins:
                plugin_data = self.marketplace.plugin_registry.get('plugins', {}).get(plugin_id)
                if plugin_data:
                    current_version = self.marketplace.installed_plugins[plugin_id].get('version')
                    new_version = plugin_data.get('version')
                    if current_version != new_version:
                        plugins_with_updates.append(plugin_id)
            
            if not plugins_with_updates:
                self.show_status("All plugins are up to date", 2000, "info")
                return
            
            # Confirm batch update
            result = messagebox.askyesno(
                "Batch Update",
                f"Update {len(plugins_with_updates)} plugins?\n\n" + "\n".join(plugins_with_updates)
            )
            
            if result:
                self.show_progress(f"Updating {len(plugins_with_updates)} plugins...")
                
                def update_thread():
                    try:
                        success_count = 0
                        for i, plugin_id in enumerate(plugins_with_updates):
                            self.update_progress((i / len(plugins_with_updates)) * 100, f"Updating {plugin_id}...")
                            success, message = self.marketplace.update_plugin(plugin_id)
                            if success:
                                success_count += 1
                            time.sleep(0.5)  # Small delay between updates
                        
                        self.window.after(0, lambda: self.batch_update_complete(success_count, len(plugins_with_updates)))
                    except Exception as e:
                        self.window.after(0, lambda: self.batch_update_complete(0, len(plugins_with_updates), str(e)))
                
                threading.Thread(target=update_thread, daemon=True).start()
                
        except Exception as e:
            self.show_status(f"❌ Batch update failed: {e}", 5000, "error")
            messagebox.showerror("Error", f"Batch update failed: {e}")

    def batch_update_complete(self, success_count, total_count, error=None):
        """Handle batch update completion"""
        self.hide_progress()
        
        if error:
            self.show_status(f"❌ Batch update failed: {error}", 5000, "error")
            messagebox.showerror("Batch Update Error", f"Failed to update plugins: {error}")
        else:
            self.show_status(f"✅ Successfully updated {success_count}/{total_count} plugins", 5000, "success")
            messagebox.showinfo("Batch Update Complete", f"Successfully updated {success_count} out of {total_count} plugins.")
            self.load_plugins()

    def clear_filters(self):
        """Clear all search and filter criteria"""
        self.search_var.set("")
        self.category_var.set("all")
        self.sort_var.set("rating")
        self.status_var.set("all")
        self.filter_plugins()

    def show_progress(self, message="Processing..."):
        """Show progress bar with message"""
        self.status_var.set(message)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, before=self.window.winfo_children()[-1])
        self.progress_var.set(0)
        self.window.update_idletasks()
    
    def update_progress(self, value, message=None):
        """Update progress bar value and optionally message"""
        self.progress_var.set(value)
        if message:
            self.status_var.set(message)
        self.window.update_idletasks()
    
    def hide_progress(self, message="Ready."):
        """Hide progress bar and set final message"""
        self.progress_bar.pack_forget()
        self.status_var.set(message)
        self.window.update_idletasks()
    
    def show_status(self, message, duration=3000, message_type="info"):
        """Show status message for specified duration with color coding"""
        theme = self.theme_dict
        
        # Color code based on message type
        if message_type == "success":
            color = theme['success_color']
        elif message_type == "error":
            color = theme['error_color']
        elif message_type == "warning":
            color = theme['warning_color']
        elif message_type == "info":
            color = theme['info_color']
        else:
            color = theme['fg']
        
        # Update status with color
        self.status_var.set(message)
        
        # Apply color to status bar (if possible)
        try:
            status_bar = self.window.winfo_children()[-1]  # Status bar is last child
            if hasattr(status_bar, 'configure'):
                status_bar.configure(foreground=color)
        except:
            pass
        
        # Reset color after duration
        def reset_color():
            try:
                status_bar = self.window.winfo_children()[-1]
                if hasattr(status_bar, 'configure'):
                    status_bar.configure(foreground=theme['fg'])
                if self.status_var.get() == message:
                    self.status_var.set("Ready.")
            except:
                pass
        
        self.window.after(duration, reset_color)

class InstalledPluginsWindow:
    """Installed plugins window"""
    
    def __init__(self, marketplace: PluginMarketplace):
        self.marketplace = marketplace
        self.window = None
        self.style = None
        self.status_var = None
        
    def setup_styles(self):
        """Set up custom ttk styles for dark/light themes"""
        theme = self.marketplace.current_theme
        self.style = ttk.Style()
        prefix = 'ZWaifuInstalled.'
        # General
        self.style.configure(prefix + 'TFrame', background=theme['bg'])
        self.style.configure(prefix + 'TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure(prefix + 'TButton', background=theme['button_bg'], foreground=theme['button_fg'], borderwidth=1, focusthickness=2, focuscolor=theme['accent'])
        self.style.map(prefix + 'TButton',
            background=[('active', theme['accent']), ('pressed', theme['accent'])],
            foreground=[('active', theme['button_fg']), ('pressed', theme['button_fg'])]
        )
        # Treeview
        self.style.configure(prefix + 'Treeview',
            background=theme['tree_bg'],
            foreground=theme['tree_fg'],
            fieldbackground=theme['tree_bg'],
            bordercolor=theme['accent'],
            rowheight=26
        )
        self.style.map(prefix + 'Treeview',
            background=[('selected', theme['tree_select_bg'])],
            foreground=[('selected', theme['tree_select_fg'])]
        )
        # Scrollbar
        self.style.configure(prefix + 'Vertical.TScrollbar', background=theme['tree_bg'])
        self.style.configure(prefix + 'Horizontal.TScrollbar', background=theme['tree_bg'])
    
    def refresh_theme(self):
        """Refresh theme when GUI theme changes with enhanced responsiveness"""
        try:
            # Update current theme from marketplace
            self.marketplace.current_theme = self.marketplace._get_current_theme()
            
            # Re-setup all styles with new theme
            self.setup_styles()
            
            # Apply theme to the window and all its widgets
            self.marketplace._apply_theme_to_window(self.window)
            
            # Set up advanced styling features
            self._setup_advanced_styling()
            
            # Force immediate visual update
            self.window.update_idletasks()
            
            # Log successful theme refresh
            if hasattr(self.marketplace.launcher_gui, 'log'):
                self.marketplace.launcher_gui.log(f"[Installed Plugins Window] Theme refreshed to: {self.marketplace.launcher_gui.current_theme}")
                
        except Exception as e:
            # Log error but don't crash
            if hasattr(self.marketplace.launcher_gui, 'log'):
                self.marketplace.launcher_gui.log(f"[Installed Plugins Window] Error refreshing theme: {e}")
            else:
                print(f"[Installed Plugins Window] Error refreshing theme: {e}")
    
    def _setup_advanced_styling(self):
        """Set up advanced styling features for the installed plugins window"""
        try:
            theme = self.marketplace.current_theme
            
            # Add hover effects to buttons
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.bind('<Enter>', lambda e, w=child: self._on_button_hover(w, True))
                            child.bind('<Leave>', lambda e, w=child: self._on_button_hover(w, False))
                            
        except Exception as e:
            # Silently continue if styling fails
            pass
    
    def _on_button_hover(self, button, entering):
        """Handle button hover effects for installed plugins window"""
        try:
            theme = self.marketplace.current_theme
            if entering:
                button.configure(style='ZWaifuInstalled.TButton.Hover')
            else:
                button.configure(style='ZWaifuInstalled.TButton')
        except Exception as e:
            # Silently continue if hover effect fails
            pass
    
    def show(self):
        """Show the installed plugins window integrated with main GUI"""
        self.window = tk.Toplevel()
        self.window.title("Installed Plugins")
        self.window.geometry("600x400")
        self.window.resizable(True, True)
        
        # Note: Modal behavior is set by main GUI for proper integration
        # self.window.transient() and self.window.grab_set() are called by main GUI
        
        # Apply theme to window using main GUI's theme system
        self.marketplace._apply_theme_to_window(self.window)
        
        # Set up custom styles
        self.setup_styles()
        
        self.create_interface()
        
        # Apply theme after interface is created
        self.marketplace._apply_theme_to_window(self.window)
        
        # Register with main GUI for theme updates
        if hasattr(self.marketplace.launcher_gui, 'register_theme_window'):
            self.marketplace.launcher_gui.register_theme_window(self.window)
        
        # Set up advanced styling features
        self._setup_advanced_styling()
        
    def create_interface(self):
        """Create the installed plugins interface"""
        prefix = 'ZWaifuInstalled.'
        theme = self.marketplace.current_theme
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10", style=prefix+'TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header with theme-aware styling
        header_label = ttk.Label(main_frame, text="Installed Plugins", font=("Arial", 16, "bold"), style=prefix+'TLabel')
        header_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Plugin list
        list_frame = ttk.Frame(main_frame, style=prefix+'TFrame')
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Create treeview with theme-aware styling
        columns = ('Plugin', 'Version', 'Installed', 'Dependencies')
        plugin_list = ttk.Treeview(list_frame, columns=columns, show='headings', height=15, style=prefix+'Treeview')
        
        # Configure columns
        for col in columns:
            plugin_list.heading(col, text=col)
        plugin_list.column('Plugin', width=200)
        plugin_list.column('Version', width=100)
        plugin_list.column('Installed', width=150)
        plugin_list.column('Dependencies', width=200)
        
        # Theme-aware scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=plugin_list.yview, style=prefix+'TScrollbar')
        plugin_list.configure(yscrollcommand=scrollbar.set)
        
        plugin_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load installed plugins
        for plugin_id, plugin_info in self.marketplace.installed_plugins.items():
            plugin_data = self.marketplace.plugin_registry.get('plugins', {}).get(plugin_id, {})
            
            installed_date = plugin_info.get('installed_at', 'Unknown')
            if installed_date != 'Unknown':
                try:
                    dt = datetime.fromisoformat(installed_date)
                    installed_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            dependencies = ', '.join(plugin_info.get('dependencies', []))
            if not dependencies:
                dependencies = 'None'
            
            plugin_list.insert('', 'end', values=(
                plugin_data.get('name', plugin_id),
                plugin_info.get('version', 'Unknown'),
                installed_date,
                dependencies
            ))
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style=prefix+'TFrame')
        button_frame.grid(row=2, column=0, sticky="ew")
        
        # Theme-aware close button
        close_btn = ttk.Button(button_frame, text="✖ Close", command=self.window.destroy, style=prefix+'TButton')
        close_btn.pack(side=tk.RIGHT)
        self.create_tooltip(close_btn, "Close the installed plugins window")
        
        # Status bar
        self.status_var = tk.StringVar(value=f"Found {len(self.marketplace.installed_plugins)} installed plugins.")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, anchor="w", style=prefix+'TLabel')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                           background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                           font=("Arial", "8", "normal"))
            label.pack(ipadx=2, ipady=2)
            
            def hide_tooltip(event):
                tooltip.destroy()
            
            widget.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Button-1>', hide_tooltip)
        
        widget.bind('<Enter>', show_tooltip) 
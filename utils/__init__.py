#!/usr/bin/env python3
"""
Z-Waifu Launcher Utils Package
Contains utility modules for the launcher system.
"""

from .analytics_system import AnalyticsSystem, create_analytics_system
from .mobile_app import MobileApp, create_mobile_app
from .plugin_system import PluginManager, PluginBase, create_plugin_manager
from .api_server import APIServer, create_api_server
from .web_interface import WebInterface, create_web_interface
from .theme_manager import EnhancedThemeManager as ThemeManager

__all__ = [
    'AnalyticsSystem',
    'create_analytics_system',
    'MobileApp', 
    'create_mobile_app',
    'PluginManager',
    'PluginBase',
    'create_plugin_manager',
    'APIServer',
    'create_api_server',
    'WebInterface',
    'create_web_interface',
    'ThemeManager'
]

__version__ = "1.0.0"
__author__ = "Z-Waifu Team" 
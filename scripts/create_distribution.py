#!/usr/bin/env python3
"""
Z-Waifu Launcher GUI - Distribution Creator
This script creates a distributable zip file with all necessary launcher files.
Updated for the new project structure with advanced features.
"""

import os
import zipfile
import shutil
import sys
from datetime import datetime

# Add parent directory to path so we can find the project files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

def create_distribution():
    """Create a distributable zip file with ALL launcher files"""
    
    # Distribution name and version
    DIST_NAME = "Z-Waifu-Launcher-GUI"
    VERSION = "1.0.0"  # Updated version for new structure
    DIST_FOLDER = f"{DIST_NAME}-v{VERSION}"
    
    # Create missing files if they don't exist
    create_missing_files()
    
    # Core files to include in distribution (root level)
    CORE_FILES = [
        os.path.join(PROJECT_ROOT, "zwaifu_launcher_gui.py"),
        os.path.join(PROJECT_ROOT, "launch_launcher.py"), 
        os.path.join(PROJECT_ROOT, "launch_launcher.bat"),
        os.path.join(PROJECT_ROOT, "launch_launcher.sh"),
        os.path.join(PROJECT_ROOT, "run.sh"),
        os.path.join(PROJECT_ROOT, "install_linux.sh"),
        os.path.join(PROJECT_ROOT, "zwaifu-launcher.desktop"),
        os.path.join(PROJECT_ROOT, "test_linux_compatibility.py"),
        os.path.join(PROJECT_ROOT, "README_LINUX.md"),
        os.path.join(PROJECT_ROOT, "LINUX_SETUP.md"),
        os.path.join(PROJECT_ROOT, "README.md"),
        os.path.join(PROJECT_ROOT, "LICENSE"),
        os.path.join(PROJECT_ROOT, "LAUNCHER_README.md"),
        os.path.join(PROJECT_ROOT, "SECURITY.md"),
        os.path.join(PROJECT_ROOT, "security_config.json"),
        os.path.join(PROJECT_ROOT, "example_api_usage.py"),
        os.path.join(PROJECT_ROOT, "get_admin_key.py"),
        os.path.join(PROJECT_ROOT, "security_fixes.py"),
        os.path.join(PROJECT_ROOT, "security_audit.py"),
        os.path.join(PROJECT_ROOT, "setup_static_analysis.py"),
        os.path.join(PROJECT_ROOT, "monitor_regressions.py"),
        os.path.join(PROJECT_ROOT, "debug_output.txt"),
        os.path.join(PROJECT_ROOT, "mobile_qr.png"),
        os.path.join(PROJECT_ROOT, ".gitignore")
    ]
    
    # Configuration files
    CONFIG_FILES = [
        os.path.join(PROJECT_ROOT, "config", "requirements.txt"),
        os.path.join(PROJECT_ROOT, "config", "VERSION.txt"),
        os.path.join(PROJECT_ROOT, "config", "launcher_config.json"),
        os.path.join(PROJECT_ROOT, "config", "project_config.json")
    ]
    
    # Documentation files
    DOC_FILES = [
        os.path.join(PROJECT_ROOT, "docs", "README.md"),
        os.path.join(PROJECT_ROOT, "docs", "INSTALLATION_GUIDE.md"),
        os.path.join(PROJECT_ROOT, "docs", "DISTRIBUTION_GUIDE.md"),
        os.path.join(PROJECT_ROOT, "docs", "PROJECT_STRUCTURE.md"),
        os.path.join(PROJECT_ROOT, "docs", "CHANGELOG.md"),
        os.path.join(PROJECT_ROOT, "docs", "API_DOCUMENTATION.md"),
        os.path.join(PROJECT_ROOT, "docs", "PLUGIN_GUIDE.md"),
        os.path.join(PROJECT_ROOT, "docs", "INSTALL.txt"),
        os.path.join(PROJECT_ROOT, "docs", "API_KEY_MANAGEMENT.md"),
        os.path.join(PROJECT_ROOT, "docs", "API_TESTING_README.md"),
        os.path.join(PROJECT_ROOT, "docs", "SECURITY_GUIDE.md"),
        os.path.join(PROJECT_ROOT, "docs", "TROUBLESHOOTING.md"),
        os.path.join(PROJECT_ROOT, "docs", "DEVELOPMENT_GUIDE.md"),
        os.path.join(PROJECT_ROOT, "docs", "ENHANCED_WIDGETS.md"),
        os.path.join(PROJECT_ROOT, "docs", "ADVANCED_THEME_SYSTEM.md")
    ]
    
    # Utility files (from utils directory)
    UTILS_FILES = [
        os.path.join(PROJECT_ROOT, "utils", "__init__.py"),
        os.path.join(PROJECT_ROOT, "utils", "analytics_system.py"),
        os.path.join(PROJECT_ROOT, "utils", "api_server.py"),
        os.path.join(PROJECT_ROOT, "utils", "api_utils.py"),
        os.path.join(PROJECT_ROOT, "utils", "config_manager.py"),
        os.path.join(PROJECT_ROOT, "utils", "error_handler.py"),
        os.path.join(PROJECT_ROOT, "utils", "enhanced_widgets.py"),
        os.path.join(PROJECT_ROOT, "utils", "mobile_app.py"),
        os.path.join(PROJECT_ROOT, "utils", "plugin_system.py"),
        os.path.join(PROJECT_ROOT, "utils", "process_manager.py"),
        os.path.join(PROJECT_ROOT, "utils", "terminal_emulator.py"),
        os.path.join(PROJECT_ROOT, "utils", "terminal_enhancements.py"),
        os.path.join(PROJECT_ROOT, "utils", "theme_manager.py"),
        os.path.join(PROJECT_ROOT, "utils", "vram_monitor.py"),
        os.path.join(PROJECT_ROOT, "utils", "web_interface.py")
    ]
    
    # Script files (from scripts directory)
    SCRIPT_FILES = [
        os.path.join(PROJECT_ROOT, "scripts", "__init__.py"),
        os.path.join(PROJECT_ROOT, "scripts", "create_distribution.py"),
        os.path.join(PROJECT_ROOT, "scripts", "create_distribution.bat"),
        os.path.join(PROJECT_ROOT, "scripts", "create_distribution_linux.sh"),
        os.path.join(PROJECT_ROOT, "scripts", "create_launcher_icon.py"),
        os.path.join(PROJECT_ROOT, "scripts", "organize_project.py"),
        os.path.join(PROJECT_ROOT, "scripts", "install_dependencies.py"),
        os.path.join(PROJECT_ROOT, "scripts", "install_dependencies.bat"),
        os.path.join(PROJECT_ROOT, "scripts", "setup_venv_and_run_launcher.bat"),
        os.path.join(PROJECT_ROOT, "scripts", "launcher.spec"),
        os.path.join(PROJECT_ROOT, "scripts", "launch_ooba_zwaifu.bat"),
        os.path.join(PROJECT_ROOT, "scripts", "test_launcher.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_advanced_features.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_flash_effect.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_tab_switching.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_theme_toggle.py"),
        os.path.join(PROJECT_ROOT, "scripts", "update_flash_calls.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_enhanced_features.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_persistent_api_key.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_api_authentication.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_api_powershell.ps1"),
        os.path.join(PROJECT_ROOT, "scripts", "test_api_curl.bat"),
        os.path.join(PROJECT_ROOT, "scripts", "test_api_curl.sh"),
        os.path.join(PROJECT_ROOT, "scripts", "test_gui.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_web_interface.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_enhanced_dashboard.py"),
        os.path.join(PROJECT_ROOT, "scripts", "simple_terminal_test.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_terminal_enhancements.py"),
        os.path.join(PROJECT_ROOT, "scripts", "verify_dark_mode_fix.py"),
        os.path.join(PROJECT_ROOT, "scripts", "test_dark_mode_fix.py"),
        os.path.join(PROJECT_ROOT, "scripts", "diagnostic_tool.py"),
        os.path.join(PROJECT_ROOT, "scripts", "setup_and_launch.py"),
        os.path.join(PROJECT_ROOT, "scripts", "quick_launch.bat"),
        os.path.join(PROJECT_ROOT, "scripts", "launch_launcher.py"),
        os.path.join(PROJECT_ROOT, "scripts", "launch_launcher.bat")
    ]
    
    # Test files (root level)
    TEST_FILES = [
        os.path.join(PROJECT_ROOT, "test_fixes.py"),
        os.path.join(PROJECT_ROOT, "test_enhanced_widgets.py"),
        os.path.join(PROJECT_ROOT, "debug_output.txt")
    ]
    
    # Plugin files
    PLUGIN_FILES = [
        os.path.join(PROJECT_ROOT, "plugins", "__init__.py"),
        os.path.join(PROJECT_ROOT, "plugins", "auto_restart.py"),
        os.path.join(PROJECT_ROOT, "plugins", "process_monitor.py"),
        os.path.join(PROJECT_ROOT, "plugins", "README.md"),
        os.path.join(PROJECT_ROOT, "plugins", "marketplace", "plugins.json")
    ]
    
    # Static files (web assets)
    STATIC_FILES = [
        os.path.join(PROJECT_ROOT, "static", "css", "style.css"),
        os.path.join(PROJECT_ROOT, "static", "js", "app.js"),
        os.path.join(PROJECT_ROOT, "static", "images", "launcher_icon.png"),
        os.path.join(PROJECT_ROOT, "static", "images", ".gitkeep"),
        os.path.join(PROJECT_ROOT, "static", "mobile", "app.js"),
        os.path.join(PROJECT_ROOT, "static", "mobile", "manifest.json"),
        os.path.join(PROJECT_ROOT, "static", "mobile", "icon-192.png"),
        os.path.join(PROJECT_ROOT, "static", "mobile", "icon-512.png"),
        os.path.join(PROJECT_ROOT, "static", "mobile", "icon-72.png"),
        os.path.join(PROJECT_ROOT, "static", "mobile", "icon-96.png")
    ]
    
    # Template files
    TEMPLATE_FILES = [
        os.path.join(PROJECT_ROOT, "templates", "dashboard.html"),
        os.path.join(PROJECT_ROOT, "templates", "mobile_dashboard.html")
    ]
    
    # AI Tools configuration files
    AI_TOOLS_FILES = [
        os.path.join(PROJECT_ROOT, "ai_tools", "ollama", "README.md"),
        os.path.join(PROJECT_ROOT, "ai_tools", "oobabooga", "README.md"),
        os.path.join(PROJECT_ROOT, "ai_tools", "oobabooga", "CMD_FLAGS.txt"),
        os.path.join(PROJECT_ROOT, "ai_tools", "oobabooga", "start_windows - Ooba.lnk"),
        os.path.join(PROJECT_ROOT, "ai_tools", "rvc", "README.md"),
        os.path.join(PROJECT_ROOT, "ai_tools", "zwaifu", "README.md")
    ]
    
    # Data files (initial/example data)
    DATA_FILES = [
        os.path.join(PROJECT_ROOT, "data", "launcher_log.txt"),
        os.path.join(PROJECT_ROOT, "data", "ooba_log.txt"),
        os.path.join(PROJECT_ROOT, "data", "analytics.db"),
        os.path.join(PROJECT_ROOT, "data", "terminal_logs", ".gitkeep")
    ]
    
    # Optional files (include if they exist)
    OPTIONAL_FILES = [
        os.path.join(PROJECT_ROOT, "launcher_icon.png"),
        os.path.join(PROJECT_ROOT, "launcher.spec"),
        os.path.join(PROJECT_ROOT, "INSTALL.txt"),
        os.path.join(PROJECT_ROOT, "mobile_qr.png"),
        os.path.join(PROJECT_ROOT, ".gitignore"),
        os.path.join(PROJECT_ROOT, "themes", "default_theme.json"),
        os.path.join(PROJECT_ROOT, "themes", "dark_theme.json"),
        os.path.join(PROJECT_ROOT, "themes", "light_theme.json")
    ]
    
    # Directories to include completely
    DIRECTORIES = [
        "utils/",
        "scripts/",
        "config/",
        "docs/",
        "data/",
        "logs/",
        "plugins/",
        "templates/",
        "static/",
        "ai_tools/"
    ]
    
    # Additional directories to create (empty but needed)
    EMPTY_DIRECTORIES = [
        "static/images/",
        "static/css/",
        "static/js/",
        "data/",
        "logs/",
        "config/",
        "plugins/",
        "templates/"
    ]
    
    print(f"Creating distribution: {DIST_NAME} v{VERSION}")
    print("=" * 50)
    
    # Create distribution directory
    if os.path.exists(DIST_FOLDER):
        print(f"Removing existing distribution folder: {DIST_FOLDER}")
        shutil.rmtree(DIST_FOLDER)
    
    os.makedirs(DIST_FOLDER)
    print(f"Created distribution folder: {DIST_FOLDER}")
    
    # Copy core files
    print("\nCopying core files:")
    for file in CORE_FILES:
        if os.path.exists(file):
            # Extract just the filename for copying to root of distribution
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(DIST_FOLDER, filename))
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {os.path.basename(file)} (not found)")
    
    # Copy configuration files
    print("\nCopying configuration files:")
    for file in CONFIG_FILES:
        if os.path.exists(file):
            # Create config directory if needed
            config_dir = os.path.join(DIST_FOLDER, "config")
            os.makedirs(config_dir, exist_ok=True)
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(config_dir, filename))
            print(f"  ✓ config/{filename}")
        else:
            print(f"  ✗ config/{os.path.basename(file)} (not found)")
    
    # Copy documentation files
    print("\nCopying documentation files:")
    for file in DOC_FILES:
        if os.path.exists(file):
            # Create docs directory if needed
            docs_dir = os.path.join(DIST_FOLDER, "docs")
            os.makedirs(docs_dir, exist_ok=True)
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(docs_dir, filename))
            print(f"  ✓ docs/{filename}")
        else:
            print(f"  ✗ docs/{os.path.basename(file)} (not found)")
    
    # Copy utility files
    print("\nCopying utility files:")
    for file in UTILS_FILES:
        if os.path.exists(file):
            # Create utils directory if needed
            utils_dir = os.path.join(DIST_FOLDER, "utils")
            os.makedirs(utils_dir, exist_ok=True)
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(utils_dir, filename))
            print(f"  ✓ utils/{filename}")
        else:
            print(f"  ✗ utils/{os.path.basename(file)} (not found)")
    
    # Copy script files
    print("\nCopying script files:")
    for file in SCRIPT_FILES:
        if os.path.exists(file):
            # Create scripts directory if needed
            scripts_dir = os.path.join(DIST_FOLDER, "scripts")
            os.makedirs(scripts_dir, exist_ok=True)
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(scripts_dir, filename))
            print(f"  ✓ scripts/{filename}")
        else:
            print(f"  ✗ scripts/{os.path.basename(file)} (not found)")
    
    # Copy test files
    print("\nCopying test files:")
    for file in TEST_FILES:
        if os.path.exists(file):
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(DIST_FOLDER, filename))
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {os.path.basename(file)} (not found)")
    
    # Copy plugin files
    print("\nCopying plugin files:")
    for file in PLUGIN_FILES:
        if os.path.exists(file):
            # Create plugins directory if needed
            plugins_dir = os.path.join(DIST_FOLDER, "plugins")
            os.makedirs(plugins_dir, exist_ok=True)
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(plugins_dir, filename))
            print(f"  ✓ plugins/{filename}")
        else:
            print(f"  ✗ plugins/{os.path.basename(file)} (not found)")
    
    # Copy static files
    print("\nCopying static files:")
    for file in STATIC_FILES:
        if os.path.exists(file):
            # Create static directory structure if needed
            static_dir = os.path.join(DIST_FOLDER, "static")
            if "css" in file:
                css_dir = os.path.join(static_dir, "css")
                os.makedirs(css_dir, exist_ok=True)
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(css_dir, filename))
                print(f"  ✓ static/css/{filename}")
            elif "js" in file:
                js_dir = os.path.join(static_dir, "js")
                os.makedirs(js_dir, exist_ok=True)
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(js_dir, filename))
                print(f"  ✓ static/js/{filename}")
        else:
            print(f"  ✗ {os.path.basename(file)} (not found)")
    
    # Copy template files
    print("\nCopying template files:")
    for file in TEMPLATE_FILES:
        if os.path.exists(file):
            # Create templates directory if needed
            templates_dir = os.path.join(DIST_FOLDER, "templates")
            os.makedirs(templates_dir, exist_ok=True)
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(templates_dir, filename))
            print(f"  ✓ templates/{filename}")
        else:
            print(f"  ✗ templates/{os.path.basename(file)} (not found)")
    
    # Copy AI tools files
    print("\nCopying AI tools files:")
    for file in AI_TOOLS_FILES:
        if os.path.exists(file):
            # Create ai_tools directory structure if needed
            ai_tools_dir = os.path.join(DIST_FOLDER, "ai_tools")
            if "ollama" in file:
                ollama_dir = os.path.join(ai_tools_dir, "ollama")
                os.makedirs(ollama_dir, exist_ok=True)
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(ollama_dir, filename))
                print(f"  ✓ ai_tools/ollama/{filename}")
            elif "oobabooga" in file:
                oobabooga_dir = os.path.join(ai_tools_dir, "oobabooga")
                os.makedirs(oobabooga_dir, exist_ok=True)
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(oobabooga_dir, filename))
                print(f"  ✓ ai_tools/oobabooga/{filename}")
            elif "rvc" in file:
                rvc_dir = os.path.join(ai_tools_dir, "rvc")
                os.makedirs(rvc_dir, exist_ok=True)
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(rvc_dir, filename))
                print(f"  ✓ ai_tools/rvc/{filename}")
            elif "zwaifu" in file:
                zwaifu_dir = os.path.join(ai_tools_dir, "zwaifu")
                os.makedirs(zwaifu_dir, exist_ok=True)
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(zwaifu_dir, filename))
                print(f"  ✓ ai_tools/zwaifu/{filename}")
        else:
            print(f"  ✗ {os.path.basename(file)} (not found)")
    
    # Copy data files
    print("\nCopying data files:")
    for file in DATA_FILES:
        if os.path.exists(file):
            # Create data directory if needed
            data_dir = os.path.join(DIST_FOLDER, "data")
            os.makedirs(data_dir, exist_ok=True)
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(data_dir, filename))
            print(f"  ✓ data/{filename}")
        else:
            print(f"  ✗ data/{os.path.basename(file)} (not found)")
    
    # Copy optional files
    print("\nCopying optional files:")
    for file in OPTIONAL_FILES:
        if os.path.exists(file):
            filename = os.path.basename(file)
            shutil.copy2(file, os.path.join(DIST_FOLDER, filename))
            print(f"  ✓ {filename}")
        else:
            print(f"  - {os.path.basename(file)} (not found, skipping)")
    
    # Create additional distribution files
    print("\nCreating distribution files:")
    
    # Create version info file
    version_info = f"""Z-Waifu Launcher GUI
Version: {VERSION}
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python Version: {sys.version.split()[0]}

This distribution contains the COMPLETE GUI codebase:

CORE APPLICATION:
- Main launcher application (zwaifu_launcher_gui.py)
- Smart launcher with dependency checking (launch_launcher.py)
- Windows batch launcher (launch_launcher.bat)
- Linux launcher scripts (launch_launcher.sh, run.sh, install_linux.sh)

UTILITY MODULES (utils/):
- Enhanced widgets system (enhanced_widgets.py)
- VRAM monitoring system (vram_monitor.py)
- Configuration management (config_manager.py)
- Error handling (error_handler.py)
- API utilities (api_utils.py)
- Process management (process_manager.py)
- Terminal emulation (terminal_emulator.py)
- Terminal enhancements (terminal_enhancements.py)
- Theme management (theme_manager.py)
- Analytics system (analytics_system.py)
- API server (api_server.py)
- Mobile app (mobile_app.py)
- Plugin system (plugin_system.py)
- Web interface (web_interface.py)

ENHANCED FEATURES:
- Scalable fonts in settings tab
- Single-click widget selection
- Enhanced scrolling with mouse wheel
- Keyboard navigation support
- Visual feedback and highlighting
- Cross-platform compatibility

PLUGIN SYSTEM (plugins/):
- Auto restart plugin (auto_restart.py)
- Process monitor plugin (process_monitor.py)
- Plugin marketplace (marketplace/plugins.json)

WEB INTERFACE:
- Static assets (static/css/, static/js/, static/images/)
- Mobile app assets (static/mobile/)
- HTML templates (templates/)

THEME SYSTEM:
- Default theme (themes/default_theme.json)
- Dark theme (themes/dark_theme.json)
- Light theme (themes/light_theme.json)
- Advanced theme editor
- Real-time theme switching

CONFIGURATION (config/):
- Requirements (requirements.txt)
- Version info (VERSION.txt)
- Launcher config (launcher_config.json)
- Project config (project_config.json)

DOCUMENTATION (docs/):
- Installation guide
- API documentation
- Security guide
- Troubleshooting guide
- Development guide
- Plugin guide
- Enhanced widgets guide
- Advanced theme system guide

TEST SUITE (scripts/):
- Comprehensive test scripts
- API testing tools
- GUI testing tools
- Diagnostic tools
- Installation scripts
- Enhanced widgets testing

SECURITY TOOLS:
- Security fixes (security_fixes.py)
- Security audit (security_audit.py)
- Admin key generation (get_admin_key.py)
- Static analysis (setup_static_analysis.py)
- Regression monitoring (monitor_regressions.py)

AI TOOLS CONFIGURATION (ai_tools/):
- Oobabooga configuration
- Ollama configuration
- RVC configuration
- Z-Waifu configuration

DATA FILES (data/):
- Launcher logs
- Analytics database
- Terminal logs

Installation:
1. Extract this zip file
2. Double-click launch_launcher.bat to start
3. Or run: python launch_launcher.py
4. Linux: chmod +x launch_launcher.sh && ./launch_launcher.sh

For detailed installation instructions, see docs/INSTALLATION_GUIDE.md
"""
    
    with open(os.path.join(DIST_FOLDER, "VERSION.txt"), "w", encoding="utf-8") as f:
        f.write(version_info)
    print("  ✓ VERSION.txt")
    
    # Create quick start guide
    quick_start = """QUICK START GUIDE
================

1. INSTALLATION
   - Extract this zip file to any folder
   - No installation required - just extract and run
   - Linux: chmod +x launch_launcher.sh && ./launch_launcher.sh

2. FIRST LAUNCH
   - Double-click: launch_launcher.bat
   - Or run: python launch_launcher.py
   - The launcher will automatically install dependencies

3. CONFIGURATION
   - Go to Settings tab
   - Browse and select your batch files:
     * Oobabooga: text-generation-webui-main/start_windows.bat
     * Z-Waifu: z-waif-1.14-R4/startup.bat
   - Set your preferred ports
   - Click "Save Settings"

4. USAGE
   - Main tab: Start/stop all processes
   - Individual tabs: Launch multiple instances
   - Instance Manager: Monitor all running instances
   - CMD Flags: Edit Oobabooga command line flags
   - Advanced tab: Web interface, API server, mobile app

5. ENHANCED FEATURES
   - Scalable fonts in settings tab (resize window to see)
   - Single-click selection for all widgets
   - Enhanced scrolling with mouse wheel
   - Keyboard navigation (arrow keys, Home/End)
   - Visual feedback and highlighting
   - Advanced theme system with real-time switching
   - Plugin marketplace for extensions

6. FEATURES
   - Multiple process instances
   - Embedded terminal with ANSI colors
   - Command history and input
   - Real-time process monitoring
   - Light/dark themes with advanced customization
   - Web-based management interface
   - REST API for automation
   - Mobile-optimized interface
   - Analytics and performance monitoring
   - Plugin system for extensibility
   - Security validation and path protection
   - Comprehensive test suite for verification

7. TESTING
   - Run test_fixes.py to verify all features work
   - Run test_enhanced_widgets.py to test new widgets
   - Test files included for validation
   - Security audit tools included

8. ADVANCED FEATURES
   - Web Interface: http://localhost:8080
   - API Server: http://localhost:8081/api
   - Mobile App: http://localhost:8082
   - Analytics Dashboard: View performance metrics
   - Plugin Management: Extend functionality
   - Theme Editor: Customize appearance

For detailed instructions, see docs/INSTALLATION_GUIDE.md
"""
    
    with open(os.path.join(DIST_FOLDER, "QUICK_START.txt"), "w", encoding="utf-8") as f:
        f.write(quick_start)
    print("  ✓ QUICK_START.txt")
    
    # Create system requirements file
    requirements_info = """SYSTEM REQUIREMENTS
===================

Minimum Requirements:
- Windows 10/11
- Python 3.7 or higher
- 4GB RAM
- 100MB disk space

Recommended Requirements:
- Windows 10/11
- Python 3.8 or higher
- 8GB RAM
- 500MB disk space
- Internet connection for dependency installation

Supported AI Tools:
- Oobabooga (text-generation-webui)
- Z-Waifu (character AI)
- Ollama (local LLMs)
- RVC (voice cloning)

For detailed requirements, see docs/INSTALLATION_GUIDE.md
"""
    
    with open(os.path.join(DIST_FOLDER, "REQUIREMENTS.txt"), "w", encoding="utf-8") as f:
        f.write(requirements_info)
    print("  ✓ REQUIREMENTS.txt")
    
    # Create advanced features guide
    advanced_guide = """ADVANCED FEATURES GUIDE
========================

WEB INTERFACE
-------------
- Access: http://localhost:8080
- Features: Browser-based management
- Real-time WebSocket updates
- Process control and monitoring
- Terminal access via web
- Responsive mobile design

REST API
--------
- Access: http://localhost:8081/api
- Features: Complete REST API
- API key authentication
- Rate limiting
- JSON responses
- Automation support

MOBILE APP
----------
- Access: http://localhost:8082
- Features: Mobile-optimized interface
- QR code for easy access
- Touch-friendly controls
- Responsive design

ANALYTICS SYSTEM
----------------
- Performance monitoring
- CPU and memory usage tracking
- Process uptime statistics
- Historical data analysis
- Export capabilities

PLUGIN SYSTEM
-------------
- Extensible architecture
- Custom plugin development
- Hot-reload capability
- Event-driven design
- Documentation included

USAGE EXAMPLES
--------------

1. Start Advanced Features:
   - Go to Advanced tab
   - Click "Start Web Interface"
   - Click "Start API Server"
   - Click "Start Mobile App"

2. Access Web Interface:
   - Open browser to http://localhost:8080
   - Monitor and control processes
   - View real-time status

3. Use REST API:
   - GET /api/status - Get system status
   - POST /api/start/Oobabooga - Start process
   - POST /api/stop/Z-Waifu - Stop process

4. Mobile Access:
   - Scan QR code from Advanced tab
   - Or visit http://localhost:8082
   - Use touch controls

5. View Analytics:
   - Click "View Analytics" in Advanced tab
   - Monitor performance metrics
   - Generate reports

For more information, see the documentation in the docs/ directory.
"""
    
    with open(os.path.join(DIST_FOLDER, "ADVANCED_FEATURES.txt"), "w", encoding="utf-8") as f:
        f.write(advanced_guide)
    print("  ✓ ADVANCED_FEATURES.txt")
    
    # Create zip file in project root
    zip_filename = os.path.join(PROJECT_ROOT, f"{DIST_FOLDER}.zip")
    print(f"\nCreating zip file: {zip_filename}")
    
    # Create empty directories that are needed
    print("\nCreating empty directories:")
    for dir_path in EMPTY_DIRECTORIES:
        full_path = os.path.join(DIST_FOLDER, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"  ✓ Created: {dir_path}")
    
    # Create .gitkeep files in empty directories to preserve them in Git
    gitkeep_dirs = [
        "static/images/",
        "data/terminal_logs/",
        "logs/",
        "backups/",
        "security_backups/"
    ]
    
    for dir_path in gitkeep_dirs:
        full_path = os.path.join(DIST_FOLDER, dir_path)
        if os.path.exists(full_path) and not os.listdir(full_path):
            gitkeep_file = os.path.join(full_path, ".gitkeep")
            with open(gitkeep_file, 'w') as f:
                pass  # Create empty file
            print(f"  ✓ Added .gitkeep to: {dir_path}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DIST_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, DIST_FOLDER)
                zipf.write(file_path, arc_name)
                print(f"  ✓ Added: {arc_name}")
    
    # Clean up distribution folder
    print(f"\nCleaning up distribution folder: {DIST_FOLDER}")
    shutil.rmtree(DIST_FOLDER)
    
    # Final summary
    print(f"\nDistribution created successfully!")
    print(f"Zip file: {zip_filename}")
    print(f"Size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    
    # List contents
    print(f"\nDistribution contents:")
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        for info in zipf.infolist():
            print(f"  - {info.filename}")
    
    print(f"\nReady for distribution! 🚀")
    return zip_filename

def create_missing_files():
    """Create missing files that are needed for the distribution"""
    
    # Create missing directories
    missing_dirs = [
        os.path.join(PROJECT_ROOT, "themes"),
        os.path.join(PROJECT_ROOT, "plugins", "marketplace"),
        os.path.join(PROJECT_ROOT, "static", "mobile"),
        os.path.join(PROJECT_ROOT, "data", "terminal_logs"),
        os.path.join(PROJECT_ROOT, "logs"),
        os.path.join(PROJECT_ROOT, "backups"),
        os.path.join(PROJECT_ROOT, "security_backups")
    ]
    
    for dir_path in missing_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create missing theme files
    theme_files = {
        "themes/default_theme.json": """{
    "name": "Default Theme",
    "description": "Default theme for Z-Waifu Launcher",
    "colors": {
        "bg_color": "#f0f0f0",
        "fg_color": "#000000",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "accent_color": "#0078d4",
        "border_color": "#cccccc"
    }
}""",
        "themes/dark_theme.json": """{
    "name": "Dark Theme",
    "description": "Dark theme for Z-Waifu Launcher",
    "colors": {
        "bg_color": "#2d2d30",
        "fg_color": "#ffffff",
        "entry_bg": "#3c3c3c",
        "entry_fg": "#ffffff",
        "accent_color": "#0078d4",
        "border_color": "#555555"
    }
}""",
        "themes/light_theme.json": """{
    "name": "Light Theme",
    "description": "Light theme for Z-Waifu Launcher",
    "colors": {
        "bg_color": "#ffffff",
        "fg_color": "#000000",
        "entry_bg": "#f8f9fa",
        "entry_fg": "#000000",
        "accent_color": "#0078d4",
        "border_color": "#dee2e6"
    }
}"""
    }
    
    for file_path, content in theme_files.items():
        full_path = os.path.join(PROJECT_ROOT, file_path)
        if not os.path.exists(full_path):
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created theme file: {file_path}")
    
    # Create missing plugin marketplace file
    marketplace_file = os.path.join(PROJECT_ROOT, "plugins", "marketplace", "plugins.json")
    if not os.path.exists(marketplace_file):
        marketplace_content = """{
    "plugins": [
        {
            "name": "auto_restart",
            "title": "Auto Restart",
            "description": "Automatically restarts processes when they crash",
            "version": "1.0.0",
            "author": "Z-Waifu Team",
            "category": "automation",
            "enabled": true
        },
        {
            "name": "process_monitor",
            "title": "Process Monitor",
            "description": "Advanced process monitoring and analytics",
            "version": "1.0.0",
            "author": "Z-Waifu Team",
            "category": "monitoring",
            "enabled": true
        }
    ]
}"""
        with open(marketplace_file, 'w', encoding='utf-8') as f:
            f.write(marketplace_content)
        print("Created plugin marketplace file: plugins/marketplace/plugins.json")
    
    # Create missing mobile app files
    mobile_files = {
        "static/mobile/manifest.json": """{
    "name": "Z-Waifu Launcher",
    "short_name": "Z-Waifu",
    "description": "Mobile interface for Z-Waifu Launcher",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#0078d4",
    "icons": [
        {
            "src": "/mobile/icon-72.png",
            "sizes": "72x72",
            "type": "image/png"
        },
        {
            "src": "/mobile/icon-96.png",
            "sizes": "96x96",
            "type": "image/png"
        },
        {
            "src": "/mobile/icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/mobile/icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}""",
        "static/mobile/app.js": """// Mobile app JavaScript
console.log('Z-Waifu Mobile App loaded');

// Mobile-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mobile app initialized');
});
"""
    }
    
    for file_path, content in mobile_files.items():
        full_path = os.path.join(PROJECT_ROOT, file_path)
        if not os.path.exists(full_path):
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created mobile file: {file_path}")
    
    # Create placeholder mobile icons (empty files for now)
    mobile_icons = [
        "static/mobile/icon-72.png",
        "static/mobile/icon-96.png", 
        "static/mobile/icon-192.png",
        "static/mobile/icon-512.png"
    ]
    
    for icon_path in mobile_icons:
        full_path = os.path.join(PROJECT_ROOT, icon_path)
        if not os.path.exists(full_path):
            # Create empty file as placeholder
            with open(full_path, 'wb') as f:
                f.write(b'')
            print(f"Created placeholder icon: {icon_path}")

def create_minimal_distribution():
    """Create a minimal distribution with only essential files"""
    
    # Distribution name and version
    DIST_NAME = "Z-Waifu-Launcher-GUI-Minimal"
    VERSION = "1.0.0"  # Updated version
    DIST_FOLDER = f"{DIST_NAME}-v{VERSION}"
    
    # Essential files only
    ESSENTIAL_FILES = [
        os.path.join(PROJECT_ROOT, "zwaifu_launcher_gui.py"),
        os.path.join(PROJECT_ROOT, "launch_launcher.py"),
        os.path.join(PROJECT_ROOT, "launch_launcher.bat"),
        os.path.join(PROJECT_ROOT, "config", "requirements.txt"),
        os.path.join(PROJECT_ROOT, "README.md")
    ]
    
    print(f"Creating minimal distribution: {DIST_NAME} v{VERSION}")
    print("=" * 50)
    
    # Create distribution directory
    if os.path.exists(DIST_FOLDER):
        print(f"Removing existing distribution folder: {DIST_FOLDER}")
        shutil.rmtree(DIST_FOLDER)
    
    os.makedirs(DIST_FOLDER)
    print(f"Created distribution folder: {DIST_FOLDER}")
    
    # Copy essential files
    print("\nCopying essential files:")
    for file in ESSENTIAL_FILES:
        if os.path.exists(file):
            # Handle config directory
            if "config" in file:
                config_dir = os.path.join(DIST_FOLDER, "config")
                os.makedirs(config_dir, exist_ok=True)
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(config_dir, filename))
                print(f"  ✓ config/{filename}")
            else:
                filename = os.path.basename(file)
                shutil.copy2(file, os.path.join(DIST_FOLDER, filename))
                print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {os.path.basename(file)} (not found)")
    
    # Create minimal readme
    minimal_readme = """Z-Waifu Launcher GUI - Minimal Distribution
===============================================

This is a minimal distribution containing only the essential files.

QUICK START:
1. Double-click: launch_launcher.bat
2. Or run: python launch_launcher.py
3. Configure your batch files in Settings tab

FEATURES INCLUDED:
- Main launcher application
- Smart dependency installation
- Basic process management
- Settings configuration
- Light/dark themes

ADVANCED FEATURES NOT INCLUDED:
- Web interface
- REST API server
- Mobile app
- Analytics system
- Plugin system

For full features and documentation, 
download the complete distribution.
"""
    
    with open(os.path.join(DIST_FOLDER, "README.txt"), "w", encoding="utf-8") as f:
        f.write(minimal_readme)
    print("  ✓ README.txt")
    
    # Create zip file
    zip_filename = f"{DIST_FOLDER}.zip"
    print(f"\nCreating zip file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DIST_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, DIST_FOLDER)
                zipf.write(file_path, arc_name)
                print(f"  ✓ Added: {arc_name}")
    
    # Clean up
    shutil.rmtree(DIST_FOLDER)
    
    print(f"\nMinimal distribution created: {zip_filename}")
    print(f"Size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    return zip_filename

def main():
    """Main function"""
    print("Z-Waifu Launcher GUI - Distribution Creator")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--minimal":
        create_minimal_distribution()
    else:
        create_distribution()

if __name__ == "__main__":
    main() 
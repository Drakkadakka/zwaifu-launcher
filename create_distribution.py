#!/usr/bin/env python3
"""
Z-Waifu Launcher GUI - Distribution Creator
This script creates a distributable zip file with all necessary launcher files.
"""

import os
import zipfile
import shutil
import sys
from datetime import datetime

def create_distribution():
    """Create a distributable zip file with all launcher files"""
    
    # Distribution name and version
    DIST_NAME = "Z-Waifu-Launcher-GUI"
    VERSION = "1.0.0"
    DIST_FOLDER = f"{DIST_NAME}-v{VERSION}"
    
    # Files to include in distribution
    CORE_FILES = [
        "zwaifu_launcher_gui.py",
        "launch_launcher.py", 
        "launch_launcher.bat",
        "test_launcher.py",
        "requirements.txt",
        "README.md",
        "INSTALLATION_GUIDE.md"
    ]
    
    # Optional files (include if they exist)
    OPTIONAL_FILES = [
        "create_launcher_icon.py",
        "launcher_config.json",
        "launcher_log.txt"
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
            shutil.copy2(file, DIST_FOLDER)
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (not found)")
    
    # Copy optional files
    print("\nCopying optional files:")
    for file in OPTIONAL_FILES:
        if os.path.exists(file):
            shutil.copy2(file, DIST_FOLDER)
            print(f"  ✓ {file}")
        else:
            print(f"  - {file} (not found, skipping)")
    
    # Create additional distribution files
    print("\nCreating distribution files:")
    
    # Create version info file
    version_info = f"""Z-Waifu Launcher GUI
Version: {VERSION}
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python Version: {sys.version.split()[0]}

This distribution contains:
- Main launcher application (zwaifu_launcher_gui.py)
- Smart launcher with dependency checking (launch_launcher.py)
- Windows batch launcher (launch_launcher.bat)
- Test suite (test_launcher.py)
- Dependencies list (requirements.txt)
- Documentation (README.md, INSTALLATION_GUIDE.md)

Installation:
1. Extract this zip file
2. Double-click launch_launcher.bat to start
3. Or run: python launch_launcher.py

For detailed installation instructions, see INSTALLATION_GUIDE.md
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

5. FEATURES
   - Multiple process instances
   - Embedded terminal with ANSI colors
   - Command history and input
   - Real-time process monitoring
   - Light/dark themes

For detailed instructions, see INSTALLATION_GUIDE.md
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

Recommended:
- Windows 10/11
- Python 3.8 or higher
- 8GB RAM
- 500MB disk space

Dependencies (auto-installed):
- psutil >= 5.8.0
- Pillow >= 8.0.0
- pystray >= 0.19.0

The launcher will automatically install these dependencies
when you first run it.
"""
    
    with open(os.path.join(DIST_FOLDER, "REQUIREMENTS.txt"), "w", encoding="utf-8") as f:
        f.write(requirements_info)
    print("  ✓ REQUIREMENTS.txt")
    
    # Create changelog
    changelog = f"""CHANGELOG - v{VERSION}
====================

Version {VERSION} - {datetime.now().strftime('%Y-%m-%d')}
====================================================

NEW FEATURES:
- Instance Manager tab for centralized process management
- Enhanced Terminal Emulator with ANSI color support
- Multi-instance support for all process types
- CMD Flags editor for Oobabooga customization
- Per-instance controls (stop/restart/kill/clear)
- Command history navigation (up/down arrows)
- Real-time process monitoring (CPU, memory, uptime)
- Light/dark theme support
- Auto-detection of batch files
- Smart dependency installation

IMPROVEMENTS:
- Robust error handling and logging
- Thread-safe terminal operations
- Graceful process termination
- Comprehensive configuration saving
- Enhanced user interface
- Better documentation

BUG FIXES:
- Fixed process cleanup issues
- Improved batch file detection
- Enhanced stability and reliability
- Better cross-platform compatibility

TECHNICAL DETAILS:
- Complete rewrite of process management
- New TerminalEmulator class
- Enhanced LauncherGUI with instance tracking
- Improved configuration system
- Better resource management
"""
    
    with open(os.path.join(DIST_FOLDER, "CHANGELOG.txt"), "w", encoding="utf-8") as f:
        f.write(changelog)
    print("  ✓ CHANGELOG.txt")
    
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

def create_minimal_distribution():
    """Create a minimal distribution with only essential files"""
    
    # Distribution name and version
    DIST_NAME = "Z-Waifu-Launcher-GUI-Minimal"
    VERSION = "1.0.0"
    DIST_FOLDER = f"{DIST_NAME}-v{VERSION}"
    
    # Essential files only
    ESSENTIAL_FILES = [
        "zwaifu_launcher_gui.py",
        "launch_launcher.py",
        "launch_launcher.bat",
        "requirements.txt",
        "README.md"
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
            shutil.copy2(file, DIST_FOLDER)
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (not found)")
    
    # Create minimal readme
    minimal_readme = """Z-Waifu Launcher GUI - Minimal Distribution
===============================================

This is a minimal distribution containing only the essential files.

QUICK START:
1. Double-click: launch_launcher.bat
2. Or run: python launch_launcher.py
3. Configure your batch files in Settings tab

For full documentation and installation guide, 
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
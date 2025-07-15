# Z-Waifu Launcher Linux Setup Guide

This guide provides everything you need to run the Z-Waifu Launcher on Linux systems.

## 📁 Linux-Specific Files

The following files have been created specifically for Linux compatibility:

### Core Launchers
- **`launch_launcher.sh`** - Main Linux shell launcher
- **`run.sh`** - Simple direct launcher
- **`install_linux.sh`** - Complete Linux installer

### Distribution & Testing
- **`scripts/create_distribution_linux.sh`** - Linux distribution creator
- **`test_linux_compatibility.py`** - Compatibility test script

### Desktop Integration
- **`zwaifu-launcher.desktop`** - Desktop menu entry
- **`README_LINUX.md`** - Comprehensive Linux documentation

## 🚀 Quick Start Options

### Option 1: One-Click Installation (Recommended)
```bash
chmod +x install_linux.sh
./install_linux.sh
```

### Option 2: Direct Launch
```bash
chmod +x launch_launcher.sh
./launch_launcher.sh
```

### Option 3: Simple Launch
```bash
chmod +x run.sh
./run.sh
```

### Option 4: Test Compatibility First
```bash
python3 test_linux_compatibility.py
```

## 🔧 Installation Methods

### Automatic Installation
The `install_linux.sh` script provides:
- ✅ System dependency detection and installation
- ✅ Python virtual environment setup
- ✅ Desktop menu integration
- ✅ Systemd service (optional)
- ✅ Command-line shortcuts
- ✅ Uninstall script creation

### Manual Installation
For advanced users who prefer manual control:
```bash
# 1. Install system dependencies
sudo apt update && sudo apt install python3 python3-pip python3-venv python3-tk xdg-utils

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r config/requirements.txt

# 4. Run launcher
python3 launch_launcher.py
```

## 🎯 Usage After Installation

### Launch Methods
- **Desktop Menu**: Search for "Z-Waifu Launcher"
- **Terminal Command**: `zwaifu-launcher`
- **Direct Path**: `/opt/zwaifu-launcher/launch_launcher.sh`

### Features Available
- 🖥️ **GUI Interface**: Full graphical user interface
- 🌐 **Web Interface**: Browser access at http://localhost:8080
- 📱 **Mobile App**: Mobile interface at http://localhost:8082
- 🔌 **API Server**: RESTful API at http://localhost:8081
- 🔧 **Plugin System**: Extensible plugin architecture
- 📊 **Analytics**: Usage monitoring and statistics

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### Permission Denied
```bash
chmod +x launch_launcher.sh install_linux.sh run.sh
```

#### Python/tkinter Missing
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Arch Linux
sudo pacman -S tk
```

#### Port Already in Use
```bash
sudo netstat -tulpn | grep :8080
sudo kill -9 <PID>
```

#### Virtual Environment Issues
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

### Testing Your Setup
Run the compatibility test to diagnose issues:
```bash
python3 test_linux_compatibility.py
```

## 📦 Creating Linux Distributions

### For Developers
To create a Linux distribution package:
```bash
chmod +x scripts/create_distribution_linux.sh
./scripts/create_distribution_linux.sh
```

This creates:
- `Z-Waifu-Launcher-GUI-v1.0.0-Linux.tar.gz`
- `Z-Waifu-Launcher-GUI-v1.0.0-Linux.tar.bz2`
- `Z-Waifu-Launcher-GUI-v1.0.0-Linux.zip`
- Checksum files for verification

## 🔄 Updates & Maintenance

### Updating the Launcher
```bash
# Stop service if running
sudo systemctl stop zwaifu-launcher

# Backup current installation
sudo cp -r /opt/zwaifu-launcher /opt/zwaifu-launcher.backup

# Extract new version
sudo tar -xzf Z-Waifu-Launcher-GUI-v*.tar.gz -C /opt/

# Restart service
sudo systemctl start zwaifu-launcher
```

### Uninstalling
```bash
/opt/zwaifu-launcher/uninstall.sh
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 18.04+, Debian 10+, CentOS 7+, Arch Linux)
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

### Required Packages
- `python3` - Python 3.7+
- `python3-pip` - Python package manager
- `python3-venv` - Virtual environment support
- `python3-tk` - Tkinter GUI framework
- `xdg-utils` - Desktop integration utilities

## 🎨 Desktop Integration

### Desktop Entry
The installer creates a desktop entry at:
`~/.local/share/applications/zwaifu-launcher.desktop`

### Systemd Service (Optional)
If you choose to create a systemd service:
```bash
# Start service
sudo systemctl start zwaifu-launcher

# Enable auto-start
sudo systemctl enable zwaifu-launcher

# Check status
sudo systemctl status zwaifu-launcher

# View logs
sudo journalctl -u zwaifu-launcher -f
```

## 🔍 Advanced Configuration

### API Usage
```bash
# Generate API key
curl -X POST http://localhost:8081/api/keys/generate

# Check status
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8081/api/status

# Start Oobabooga
curl -X POST -H "X-API-Key: YOUR_API_KEY" http://localhost:8081/api/start/oobabooga
```

### Plugin Development
```bash
# Create a new plugin
python3 -c "
from utils import create_plugin_manager
pm = create_plugin_manager()
pm.create_plugin_template('my_plugin')
"
```

## 📚 Documentation

### Main Documentation
- **`README_LINUX.md`** - Comprehensive Linux guide
- **`docs/`** - General project documentation
- **`config/`** - Configuration examples

### Logs and Debugging
- **Launcher Logs**: `data/launcher_log.txt`
- **Oobabooga Logs**: `data/ooba_log.txt`
- **Terminal Logs**: `data/terminal_logs/`

## 🤝 Support

### Getting Help
1. Check `README_LINUX.md` for detailed instructions
2. Run `test_linux_compatibility.py` to diagnose issues
3. Review logs in the `data/` directory
4. Check the main project documentation

### Reporting Issues
When reporting Linux-specific issues, include:
- Linux distribution and version (`lsb_release -a`)
- Python version (`python3 --version`)
- Output from `test_linux_compatibility.py`
- Error messages from logs
- Steps to reproduce the issue

## 🎉 Success!

Once installed, you'll have a fully functional Z-Waifu Launcher that:
- ✅ Works natively on Linux
- ✅ Integrates with your desktop environment
- ✅ Provides web and mobile interfaces
- ✅ Includes comprehensive monitoring and analytics
- ✅ Supports plugin development
- ✅ Offers API access for automation

**Happy AI Waifu launching on Linux! 🐧✨** 
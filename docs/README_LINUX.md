# Z-Waifu Launcher for Linux

A comprehensive AI Waifu launcher with Oobabooga and Z-Waifu integration, designed to work seamlessly on Linux systems.

## 🚀 Quick Start

### Option 1: Automatic Installation (Recommended)
```bash
chmod +x install_linux.sh
./install_linux.sh
```

### Option 2: Manual Launch
```bash
chmod +x launch_launcher.sh
./launch_launcher.sh
```

### Option 3: Simple Direct Launch
```bash
chmod +x run.sh
./run.sh
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 18.04+, Debian 10+, CentOS 7+, Arch Linux, etc.)
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

### Required Packages
- `python3` - Python 3.7+
- `python3-pip` - Python package manager
- `python3-venv` - Virtual environment support
- `python3-tk` - Tkinter GUI framework
- `xdg-utils` - Desktop integration utilities

## 🔧 Installation

### Automatic Installation
The `install_linux.sh` script will handle everything automatically:

1. **System Dependencies**: Installs required packages for your distribution
2. **Virtual Environment**: Creates a Python virtual environment
3. **Python Dependencies**: Installs all required Python packages
4. **Desktop Integration**: Creates desktop menu entry
5. **Systemd Service**: Optional auto-start service
6. **Symlinks**: Creates convenient command shortcuts

```bash
# Make executable and run
chmod +x install_linux.sh
./install_linux.sh
```

### Manual Installation
If you prefer manual installation:

```bash
# 1. Install system dependencies
sudo apt update  # Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv python3-tk xdg-utils

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install --upgrade pip
pip install -r config/requirements.txt

# 4. Run the launcher
python3 launch_launcher.py
```

## 🎯 Usage

### After Installation
Once installed, you can launch the application using:

- **Desktop Menu**: Look for "Z-Waifu Launcher" in your applications menu
- **Command Line**: `zwaifu-launcher`
- **Direct Path**: `/opt/zwaifu-launcher/launch_launcher.sh`

### First Run
1. The launcher will automatically detect your system
2. Configure paths to Oobabooga and Z-Waifu installations
3. Set up command-line flags and settings
4. Launch your AI applications

### Features
- **GUI Interface**: User-friendly graphical interface
- **Process Management**: Start/stop AI applications
- **Web Interface**: Access via browser (port 8080)
- **Mobile App**: Mobile-friendly interface (port 8082)
- **API Server**: RESTful API for automation (port 8081)
- **Plugin System**: Extensible plugin architecture
- **Analytics**: Usage statistics and monitoring

## 🗂️ Directory Structure

```
/opt/zwaifu-launcher/
├── zwaifu_launcher_gui.py    # Main launcher application
├── launch_launcher.py        # Python launcher script
├── launch_launcher.sh        # Linux shell launcher
├── install_linux.sh          # Linux installer
├── run.sh                    # Simple launcher
├── uninstall.sh              # Uninstall script
├── config/                   # Configuration files
├── utils/                    # Utility modules
├── plugins/                  # Plugin system
├── static/                   # Web interface assets
├── templates/                # Web templates
├── docs/                     # Documentation
├── scripts/                  # Scripts and tools
├── ai_tools/                 # AI tools configuration
└── data/                     # Data files and logs
```

## 🔧 Configuration

### Main Configuration
- **File**: `config/launcher_config.json`
- **Settings**: Oobabooga and Z-Waifu paths, ports, themes

### Command Line Flags
- **File**: `ai_tools/oobabooga/CMD_FLAGS.txt`
- **Purpose**: Customize Oobabooga startup parameters

### Web Interface
- **Port**: 8080 (configurable)
- **Access**: http://localhost:8080
- **Features**: Dashboard, process control, settings

### API Server
- **Port**: 8081 (configurable)
- **Purpose**: RESTful API for automation
- **Authentication**: API key required

### Mobile Interface
- **Port**: 8082 (configurable)
- **Access**: http://localhost:8082
- **Features**: Mobile-optimized interface

## 🛠️ Troubleshooting

### Common Issues

#### Python/tkinter not found
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Arch Linux
sudo pacman -S tk
```

#### Permission denied
```bash
chmod +x launch_launcher.sh
chmod +x install_linux.sh
chmod +x run.sh
```

#### Port already in use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8080

# Kill the process if needed
sudo kill -9 <PID>
```

#### Virtual environment issues
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

#### Desktop entry not working
```bash
# Update desktop database
update-desktop-database ~/.local/share/applications

# Check desktop entry
cat ~/.local/share/applications/zwaifu-launcher.desktop
```

### Logs and Debugging
- **Launcher Logs**: `data/launcher_log.txt`
- **Oobabooga Logs**: `data/ooba_log.txt`
- **Terminal Logs**: `data/terminal_logs/`

### Performance Issues
- **Memory**: Close other applications to free RAM
- **GPU**: Ensure proper GPU drivers are installed
- **Storage**: Check available disk space

## 🔄 Updates

### Updating the Launcher
```bash
# Stop the launcher
sudo systemctl stop zwaifu-launcher  # if using systemd

# Backup current installation
sudo cp -r /opt/zwaifu-launcher /opt/zwaifu-launcher.backup

# Extract new version
sudo tar -xzf Z-Waifu-Launcher-GUI-v*.tar.gz -C /opt/

# Restart the launcher
sudo systemctl start zwaifu-launcher  # if using systemd
```

## 🗑️ Uninstallation

### Complete Uninstallation
```bash
/opt/zwaifu-launcher/uninstall.sh
```

### Manual Uninstallation
```bash
# Remove desktop entry
rm ~/.local/share/applications/zwaifu-launcher.desktop

# Remove symlink
sudo rm /usr/local/bin/zwaifu-launcher

# Remove systemd service (if created)
sudo systemctl stop zwaifu-launcher
sudo systemctl disable zwaifu-launcher
sudo rm /etc/systemd/system/zwaifu-launcher.service
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /opt/zwaifu-launcher
```

## 📚 Advanced Usage

### Systemd Service
If you created a systemd service during installation:

```bash
# Start the service
sudo systemctl start zwaifu-launcher

# Stop the service
sudo systemctl stop zwaifu-launcher

# Enable auto-start
sudo systemctl enable zwaifu-launcher

# Check status
sudo systemctl status zwaifu-launcher

# View logs
sudo journalctl -u zwaifu-launcher -f
```

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

## 🤝 Support

### Getting Help
1. Check this README for common solutions
2. Review the logs in `data/` directory
3. Check the main project documentation
4. Create an issue on the project repository

### Reporting Issues
When reporting issues, please include:
- Linux distribution and version
- Python version (`python3 --version`)
- Error messages from logs
- Steps to reproduce the issue

### Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on Linux
5. Submit a pull request

## 📄 License

This project is licensed under the same terms as the main Z-Waifu project.

## 🙏 Acknowledgments

- Oobabooga team for the text generation web UI
- Z-Waifu developers for the AI character system
- Linux community for excellent tools and documentation

---

**Happy AI Waifu launching on Linux! 🐧✨** 
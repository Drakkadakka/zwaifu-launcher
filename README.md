# Z-Waifu Launcher GUI

A powerful, feature-rich GUI launcher for managing AI/ML processes including Oobabooga, Z-Waifu, Ollama, and RVC with advanced terminal emulation, instance management, web interface, API integration, plugin system, mobile support, and comprehensive analytics.

## 🚀 Quick Start

### Option 1: Simple Launch (Recommended)
1. **Double-click** `scripts/launch_launcher.bat` to start the launcher
2. The script will automatically check and install dependencies
3. The GUI will open and you can start configuring

### Option 2: Manual Launch
1. **Install dependencies**:
   ```bash
   pip install -r config/requirements.txt
   ```
2. **Run the launcher**:
   ```bash
   python zwaifu_launcher_gui.py
   ```

### Option 3: Smart Launcher
1. **Run the smart launcher**:
   ```bash
   python scripts/launch_launcher.py
   ```
2. This will automatically install missing dependencies

## 📁 Project Structure

```
ZWAIFU-PROJECT/
├── zwaifu_launcher_gui.py    # Main launcher application
├── README.md                 # This file
├── LICENSE                   # License file
├── .gitignore               # Git ignore file
├── utils/                    # Utility modules
│   ├── __init__.py          # Package initialization
│   ├── analytics_system.py  # Analytics and monitoring
│   ├── mobile_app.py        # Mobile interface
│   ├── plugin_system.py     # Plugin management
│   ├── api_server.py        # REST API server
│   └── web_interface.py     # Web interface
├── scripts/                  # Utility scripts
│   ├── launch_launcher.py   # Smart launcher
│   ├── launch_launcher.bat  # Windows launcher
│   ├── install_dependencies.py # Dependency installer
│   ├── test_*.py            # Test suite
│   ├── create_distribution.py # Distribution creator
│   └── update_flash_calls.py # Utility scripts
├── config/                   # Configuration files
│   ├── launcher_config.json # Launcher settings
│   ├── requirements.txt     # Python dependencies
│   └── VERSION.txt          # Version information
├── docs/                     # Documentation
│   ├── INSTALLATION_GUIDE.md # Installation instructions
│   ├── CHANGELOG.md         # Version history
│   ├── API_DOCUMENTATION.md # API reference
│   ├── PLUGIN_GUIDE.md      # Plugin development guide
│   ├── PROJECT_STRUCTURE.md # Project structure guide
│   └── DISTRIBUTION_GUIDE.md # Distribution guide
├── data/                     # Data and logs
│   ├── analytics.db         # Analytics database
│   ├── launcher_log.txt     # Application logs
│   └── ooba_log.txt         # Oobabooga logs
├── logs/                     # Additional logs
├── plugins/                  # Plugin system
│   └── README.md            # Plugin documentation
├── templates/                # Web templates
│   ├── dashboard.html       # Web dashboard template
│   └── mobile_dashboard.html # Mobile dashboard template
├── static/                   # Web assets
│   ├── css/style.css        # Main stylesheet
│   ├── js/app.js            # Main JavaScript
│   └── images/              # Images and icons
└── ai_tools/                 # AI tool configurations
    ├── oobabooga/           # Oobabooga setup
    ├── zwaifu/              # Z-Waifu setup
    ├── ollama/              # Ollama setup
    └── rvc/                 # RVC setup
```

## 🎯 Features

### Core Functionality
- **Multi-Process Management**: Launch and manage Oobabooga, Z-Waifu, Ollama, and RVC processes
- **Embedded Terminal Emulator**: Full-featured terminal with ANSI color support, command history, and real-time output
- **Instance Manager**: Centralized management of all running process instances
- **Auto-Detection**: Automatically finds batch files in your project structure
- **Theme Support**: Light and dark mode with customizable themes
- **Process Monitoring**: Real-time CPU, memory, and uptime tracking

### 🌐 Web Interface
- **Browser-Based Management**: Full web interface accessible from any device on your network
- **Real-Time Updates**: Live status updates via WebSocket connections
- **Process Control**: Start, stop, restart, and monitor processes from any browser
- **Terminal Access**: Web-based terminal with command input and output display
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Push Notifications**: Real-time alerts for process events and system status
- **Dashboard**: Comprehensive overview of all processes and system resources
- **Remote Access**: Access your launcher from anywhere on your network

### 🔌 REST API
- **Remote Management**: Complete REST API for programmatic control
- **API Key Authentication**: Secure access with configurable API keys
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Comprehensive Endpoints**: Full CRUD operations for all launcher features
- **Real-Time Data**: Live metrics and status information
- **Documentation**: Auto-generated API documentation and examples
- **Key Management**: Generate, revoke, and manage API keys
- **Permission System**: Granular permissions for different API operations

### 🔧 Plugin System
- **Extensible Architecture**: Plugin-based system for custom features
- **Hot Reloading**: Load and unload plugins without restarting
- **Event System**: Plugin hooks for process events and system changes
- **Configuration Management**: Per-plugin configuration storage
- **Example Plugins**: Process monitoring, auto-restart, and notification plugins included
- **Plugin Development**: Easy-to-use plugin development framework
- **Plugin Manager**: GUI for managing installed plugins
- **Template Generator**: Create new plugins from templates

### 📱 Mobile Support
- **Mobile-Optimized Interface**: Touch-friendly mobile dashboard
- **Cross-Platform Access**: Works on iOS, Android, and any mobile browser
- **Offline Capability**: Basic functionality works without internet
- **Push Notifications**: Mobile notifications for important events
- **Swipe Gestures**: Intuitive touch controls and gestures
- **Real-Time Monitoring**: Live process status and system metrics
- **QR Code Access**: Quick access via QR code scanning
- **Responsive Design**: Optimized for all screen sizes

### 📊 Advanced Analytics
- **Performance Metrics**: Detailed CPU, memory, and disk usage tracking
- **Process Analytics**: Individual process performance analysis
- **Historical Data**: Long-term performance trends and patterns
- **Custom Reports**: Generate comprehensive performance reports
- **Data Export**: Export analytics data in CSV and JSON formats
- **Visual Charts**: Interactive charts and graphs for data visualization
- **Alert System**: Configurable alerts for performance thresholds
- **Recommendations**: AI-powered recommendations for system optimization
- **Resource Monitoring**: Real-time system resource tracking
- **Performance Dashboard**: Comprehensive performance overview

### Advanced Terminal Features
- **ANSI Color Support**: Full color parsing and display from process output
- **Command History**: Navigate with up/down arrow keys
- **Real-time Input**: Send commands directly to processes
- **Thread-safe Operations**: Safe concurrent access to stdin/stdout
- **Process Attachment**: Easy attachment to subprocess.Popen objects
- **Multi-instance Support**: Each process instance gets its own terminal
- **Per-instance Controls**: Individual stop, restart, kill, and clear controls

### Multi-Instance Support
- **Multiple Tabs**: Each process instance gets its own tab
- **Independent Terminals**: Each instance has its own terminal emulator
- **Process Tracking**: Comprehensive tracking of all running instances
- **Instance Management**: Centralized control through Instance Manager
- **Load Balancing**: Distribute load across multiple instances
- **Cluster Support**: Manage multiple nodes in a cluster

### Instance Manager
- **Central Dashboard**: Real-time list of all running process instances
- **Status Monitoring**: Shows Running/Stopped status, PID, and uptime for each instance
- **Individual Controls**: Stop, restart, and kill buttons for each instance
- **Bulk Operations**: "Kill All" button to terminate all running instances
- **Focus Navigation**: Double-click any instance to focus its terminal tab
- **Auto-refresh**: Updates every 5 seconds to show current status
- **Resource Usage**: Real-time CPU and memory usage per instance

### CMD Flags Editor
- **Visual Editor**: Edit Oobabooga command line flags
- **Load/Save**: Load existing flags and save changes
- **Reset Function**: Reset to default content
- **Auto-creation**: Creates default file if not found

### Enhanced Process Management
- **Graceful Termination**: Proper process cleanup with child process handling
- **Force Kill**: Emergency termination when needed
- **Auto-restart**: Optional automatic restart on crash
- **Status Monitoring**: Real-time CPU, memory, and uptime tracking
- **Process Logging**: Comprehensive logging of all process activities

## 📋 System Requirements

- **Operating System**: Windows 10/11 (tested)
- **Python**: 3.7 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 100MB for launcher + space for your AI models

### Optional Dependencies
The following packages are automatically installed if available:
- **Flask**: Web interface and API server
- **Flask-SocketIO**: Real-time WebSocket support
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-Limiter**: API rate limiting
- **PyJWT**: JWT token authentication
- **matplotlib**: Analytics charts and graphs
- **numpy**: Numerical computing for analytics
- **requests**: HTTP client for API calls
- **qrcode**: QR code generation for mobile access

## 🔧 Installation

### Prerequisites

#### Install Python
1. Download Python 3.7+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```bash
   python --version
   ```

### Installation Steps

#### Option 1: Automatic Installation (Recommended)
1. Download the distribution zip file
2. Extract to your desired location
3. Double-click `scripts/launch_launcher.bat`
4. The launcher will automatically install all dependencies

#### Option 2: Manual Installation
1. **Install core dependencies**:
   ```bash
   pip install psutil pillow pystray
   ```
2. **Install optional dependencies for advanced features**:
   ```bash
   pip install flask flask-socketio flask-cors flask-limiter pyjwt matplotlib numpy requests qrcode
   ```
3. **Run the launcher**:
   ```bash
   python zwaifu_launcher_gui.py
   ```

#### Option 3: Smart Installation
1. **Run the smart launcher**:
   ```bash
   python scripts/launch_launcher.py
   ```
2. This will automatically install missing dependencies

## 🎯 First Launch

### 1. Start the Launcher
- Double-click `scripts/launch_launcher.bat` or run `python zwaifu_launcher_gui.py`

### 2. Configure Settings
1. Go to the **Settings** tab
2. Browse and select your batch files:
   - Oobabooga batch file
   - Z-Waifu batch file
   - Ollama batch file (if using)
   - RVC batch file (if using)
3. Set your preferred ports
4. Choose your theme (Light/Dark)
5. Click "Save Settings"

### 3. Test Your Setup
1. Go to the **Main** tab
2. Click "Start All" to test Oobabooga and Z-Waifu
3. Check that processes start successfully
4. Use "Stop All" to stop the processes

### 4. Explore Advanced Features
1. Go to the **Advanced Features** tab
2. Start the Web Interface for browser-based management
3. Enable the API Server for remote access
4. Explore the Plugin System for extensibility
5. Check out the Mobile Support for remote monitoring
6. View Analytics for performance insights

## 🔧 Advanced Configuration

### Web Interface Configuration
1. Go to the **Advanced Features** tab
2. Click "Configure Remote Access"
3. Set authentication method (API Key or JWT)
4. Configure SSL settings for secure access
5. Set host and port for web interface
6. Start the Web Interface

### API Server Setup
1. Go to the **Advanced Features** tab
2. Click "Start API Server"
3. Generate API keys for secure access
4. Configure rate limiting settings
5. View API documentation for available endpoints

### Plugin Management
1. Go to the **Advanced Features** tab
2. Click "Manage Plugins"
3. Enable/disable installed plugins
4. Create new plugins using templates
5. Configure plugin settings

### Mobile Access
1. Start the Mobile App from Advanced Features
2. Scan the QR code with your mobile device
3. Access the mobile dashboard
4. Monitor processes and system resources
5. Receive push notifications for events

### Analytics Configuration
1. Go to the **Advanced Features** tab
2. Click "View Analytics"
3. Configure data collection settings
4. Set up performance alerts
5. Generate custom reports
6. Export data for external analysis

### CMD Flags Editor
1. Go to the **CMD Flags** tab
2. Edit Oobabooga command line flags
3. Add flags like `--listen`, `--api`, `--extensions api`
4. Save your changes

### Instance Management
1. Use individual process tabs to launch multiple instances
2. Use the **Instance Manager** to monitor all running instances
3. Each instance gets its own terminal with controls
4. Configure load balancing for multiple instances

### Terminal Features
- **ANSI Color Support**: Colored output from processes
- **Command History**: Navigate with up/down arrows
- **Real-time Input**: Send commands to processes
- **Per-instance Controls**: Stop, restart, kill, clear

## 📦 Distribution

### Creating Distributions
The launcher includes a distribution system for easy packaging and distribution:

#### Full Distribution
```bash
python scripts/create_distribution.py
```
Creates a complete distribution package (~37 KB) with all files and documentation.

#### Minimal Distribution
```bash
python scripts/create_distribution.py --minimal
```
Creates a minimal distribution package (~30 KB) with essential files only.

### Distribution Contents

#### Full Distribution (`Z-Waifu-Launcher-GUI-v1.0.0.zip`)
- ✅ Main launcher application (`zwaifu_launcher_gui.py`)
- ✅ Smart launcher with dependency checking (`scripts/launch_launcher.py`)
- ✅ Windows batch launcher (`scripts/launch_launcher.bat`)
- ✅ Test suite (`scripts/test_launcher.py`, `scripts/test_advanced_features.py`)
- ✅ Dependencies list (`config/requirements.txt`)
- ✅ Complete documentation (`README.md`, `docs/INSTALLATION_GUIDE.md`)
- ✅ Version information (`config/VERSION.txt`)
- ✅ Quick start guide (`scripts/QUICK_START.txt`)
- ✅ System requirements (`scripts/REQUIREMENTS.txt`)
- ✅ Changelog (`docs/CHANGELOG.md`)
- ✅ Distribution guide (`docs/DISTRIBUTION_GUIDE.md`)

#### Minimal Distribution (`Z-Waifu-Launcher-GUI-Minimal-v1.0.0.zip`)
- ✅ Main launcher application (`zwaifu_launcher_gui.py`)
- ✅ Smart launcher (`scripts/launch_launcher.py`)
- ✅ Windows batch launcher (`scripts/launch_launcher.bat`)
- ✅ Dependencies list (`config/requirements.txt`)
- ✅ Basic documentation (`README.md`)

For detailed distribution information, see [docs/DISTRIBUTION_GUIDE.md](docs/DISTRIBUTION_GUIDE.md).

## 🧪 Testing

### Core Functionality Tests
Run the basic test suite to verify core functionality:
```bash
python scripts/test_launcher.py
```

This will test:
- ✅ GUI creation
- ✅ Terminal emulator
- ✅ Instance manager
- ✅ All imports and initialization

### Advanced Features Tests
Run the advanced features test suite to verify all advanced functionality:
```bash
python scripts/test_advanced_features.py
```

This will test:
- ✅ All advanced feature imports
- ✅ Web interface functionality
- ✅ API server capabilities
- ✅ Plugin system
- ✅ Mobile support
- ✅ Analytics system
- ✅ Configuration file creation
- ✅ Plugin template generation

## 🔧 Troubleshooting

### Common Issues

#### Dependencies Not Found
If you get import errors:
1. Run `python scripts/launch_launcher.py` to automatically install dependencies
2. Or manually install: `pip install -r config/requirements.txt`

#### Advanced Features Not Working
If advanced features fail to start:
1. Check that optional dependencies are installed
2. Run `python scripts/test_advanced_features.py` to diagnose issues
3. Check the launcher logs for error messages

#### Web Interface Not Accessible
If the web interface doesn't work:
1. Check that Flask is installed: `pip install flask flask-socketio`
2. Verify the port isn't in use by another application
3. Check firewall settings

#### API Server Issues
If the API server fails:
1. Check that all API dependencies are installed
2. Verify API key generation is working
3. Check rate limiting settings

### Getting Help

1. **Check the logs**: The launcher creates detailed logs in the Logs directory
2. **Run tests**: Use the test scripts to verify functionality
3. **Check documentation**: See INSTALLATION_GUIDE.md for detailed setup instructions
4. **Review requirements**: Ensure all dependencies are properly installed

## 📝 Changelog

### Version 1.0.0 (Latest)
- ✨ Added comprehensive Web Interface with real-time updates
- ✨ Added REST API server with authentication and rate limiting
- ✨ Added Plugin System for extensible architecture
- ✨ Added Mobile Support with touch-friendly interface
- ✨ Added Advanced Analytics with performance monitoring
- ✨ Enhanced Terminal Emulator with ANSI color support
- ✨ Added Multi-Instance Support with individual terminals
- ✨ Added Instance Manager for centralized process control
- ✨ Added comprehensive testing suite
- ✨ Added distribution system for easy packaging
- ✨ Added smart launcher with automatic dependency installation
- ✨ Added theme support (light/dark modes)
- ✨ Added process monitoring with real-time metrics
- ✨ Added auto-restart functionality
- ✨ Added graceful process termination
- ✨ Added CMD flags editor
- ✨ Added comprehensive documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Advanced features powered by Flask, SocketIO, and modern web technologies
- Process management enhanced with psutil
- Terminal emulation with ANSI color support
- Analytics powered by matplotlib and numpy
- Mobile support with responsive web design
- Plugin system for extensible architecture

---

**Z-Waifu Launcher GUI** - Your comprehensive AI/ML process management solution with advanced features for professional use. 

## Recent Improvements in Version 1.0.0

- **Theme Toggle:** Button now uses sun/moon emoji, with clear logic and consistent styling.
- **Kill All Button:** Now reliably kills all running processes and updates the UI/log.
- **File Dialogs:** Remember the last used directory for batch file and CMD_FLAGS selection.
- **CMD_FLAGS Editor:** Prompts user to locate CMD_FLAGS.txt if missing, or creates default content.
- **Logging:** All log output is now written to the log file (`data/launcher_log.txt`).
- **Port Settings:** Port values in the settings panel are now saved and loaded correctly. 
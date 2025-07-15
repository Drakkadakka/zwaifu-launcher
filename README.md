# Z-Waifu Launcher GUI

A powerful, feature-rich GUI launcher for managing AI/ML processes including Oobabooga, Z-Waifu, Ollama, and RVC with advanced terminal emulation, instance management, web interface, API integration, plugin system, mobile support, and comprehensive analytics.

## 🚀 Quick Start

### One-Click Launch (Recommended)
Simply run the smart launcher which handles everything automatically:

**Windows:**
```bash
launch_launcher.bat
```

**Cross-platform:**
   ```bash
python launch_launcher.py
```

The launcher will automatically:
- ✅ Check Python version compatibility
- ✅ Validate project structure
- ✅ Create virtual environment if needed
- ✅ Install dependencies automatically
- ✅ Launch the GUI on top of other windows
- ✅ Handle all setup and configuration

### Alternative Launch Methods

**Option 1: Install Dependencies First**
   ```bash
python scripts/install_dependencies.py
python zwaifu_launcher_gui.py
   ```

**Option 2: Manual Setup**
   ```bash
   pip install -r config/requirements.txt
   python zwaifu_launcher_gui.py
   ```

## 🆕 What's New in v1.1.0

### ✅ **Bug Fixes & Improvements**
- **Fixed Unicode decode errors** in configuration loading
- **Enhanced path validation** with comprehensive security checks
- **Improved thread safety** for process management
- **Fixed race conditions** in process start/stop operations
- **Enhanced memory management** with efficient cleanup
- **Fixed theme state consistency** issues
- **Improved error handling** with graceful fallbacks
- **Fixed corrupted config backup** creation
- **Fixed Instance Manager tab** - Resolved canvas/scrollbar reference errors

### ✅ **New Features**
- **One-click setup** - Automatic dependency installation and configuration
- **Window management** - GUI appears on top of other windows
- **Bring to front** - Button and keyboard shortcuts (Ctrl+F, F12)
- **Enhanced security** - Path traversal protection and command injection prevention
- **Robust icon handling** - Automatic icon generation and fallback
- **Improved logging** - Better error reporting and debugging
- **VRAM Monitoring** - Real-time GPU memory monitoring and auto-cleanup
- **Enhanced Terminal Emulator** - ANSI color support, command history, real-time input

### ✅ **Enhanced User Experience**
- **Smart launcher** - Handles all setup automatically
- **Better error messages** - Clear feedback and recovery options
- **Cross-platform compatibility** - Works on Windows, Linux, macOS
- **Consistent environment** - Always uses the same setup process
- **Graceful fallbacks** - Uses system Python if venv fails
- **Advanced Analytics** - Performance metrics, process monitoring, custom reports

## 🎯 Core Features

### **Multi-Process Management**
- **Launch and manage** Oobabooga, Z-Waifu, Ollama, and RVC processes
- **Auto-detection** of batch files in your project structure
- **Port validation** and conflict detection
- **Graceful termination** with proper cleanup
- **Process monitoring** with real-time status updates

### **GUI Tabs and Interface**
- **Main Tab** - Central control panel with launch buttons and status
- **Settings Tab** - Configuration, themes, VRAM monitoring, auto-start options
- **Instance Manager** - Centralized dashboard for all running instances
- **Oobabooga Tab** - Dedicated Oobabooga instance management
- **Z-Waifu Tab** - Dedicated Z-Waifu instance management
- **Ollama Tab** - Dedicated Ollama instance management
- **RVC Tab** - Dedicated RVC instance management
- **Advanced Tab** - Analytics, performance monitoring, system health
- **Logs Tab** - Real-time log viewing and management
- **About Tab** - Version information and project details

### **Advanced Terminal Emulator**
- **ANSI color support** for rich output display
- **Command history** with up/down arrow navigation
- **Real-time input** - Send commands directly to processes
- **Thread-safe operations** for concurrent access
- **Memory-efficient** with automatic cleanup
- **Multi-instance support** - Each process gets its own terminal
- **Search and filter** - Find specific output lines
- **Export functionality** - Save terminal output to files
- **Performance monitoring** - Real-time CPU/memory tracking

### **Instance Manager**
- **Centralized dashboard** for all running instances
- **Real-time monitoring** - Status, PID, uptime, CPU, memory
- **Individual controls** - Stop, restart, kill per instance
- **Bulk operations** - Kill all instances at once
- **Focus navigation** - Double-click to focus terminal tabs
- **Auto-refresh** every 5 seconds

### **Theme System**
- **Light and dark modes** with customizable themes
- **Theme toggle button** with emoji indicators
- **Persistent settings** - Remembers your preference
- **Consistent styling** across all components

### **Window Management**
- **Appears on top** when launched
- **Bring to front button** (📋) for easy access
- **Keyboard shortcuts** - Ctrl+F or F12 to bring to front
- **Smart behavior** - Stays on top briefly, then normal operation

## 🌐 Advanced Features

### **Web Interface** (Optional)
- **Browser-based management** accessible from any device
- **Real-time updates** via WebSocket connections
- **Process control** from any web browser
- **Mobile-responsive** design
- **Access at**: http://localhost:8080

### **REST API** (Optional)
- **Programmatic control** via REST API
- **API key authentication** with rate limiting
- **Comprehensive endpoints** for all features
- **Documentation** and examples included
- **Access at**: http://localhost:8081/api

### **Mobile Support** (Optional)
- **Mobile-optimized interface** for touch devices
- **QR code access** for quick connection
- **Cross-platform** - iOS, Android, any mobile browser
- **Access at**: http://localhost:8082

### **Analytics System** (Optional)
- **Performance metrics** - CPU, memory, disk usage
- **Process analytics** with historical data
- **Custom reports** and data export
- **Visual charts** and graphs
- **Alert system** for performance thresholds
- **VRAM monitoring** - GPU memory tracking and optimization
- **System health monitoring** - Real-time diagnostics
- **Performance benchmarking** - Automated performance testing

### **Plugin System** (Optional)
- **Extensible architecture** with plugin support
- **Hot reloading** - Load/unload without restart
- **Event system** for process hooks
- **Example plugins** included
- **Plugin manager** GUI

## 📁 Project Structure

```
ZWAIFU-PROJECT/
├── zwaifu_launcher_gui.py    # Main launcher application
├── launch_launcher.py        # Smart launcher (handles setup)
├── launch_launcher.bat       # Windows launcher
├── README.md                 # This file
├── LICENSE                   # License file
├── SECURITY.md              # Security documentation
├── test_fixes.py            # Test suite for verification
├── utils/                    # Utility modules
│   ├── __init__.py          # Package initialization
│   ├── analytics_system.py  # Analytics and monitoring
│   ├── mobile_app.py        # Mobile interface
│   ├── plugin_system.py     # Plugin management
│   ├── api_server.py        # REST API server
│   ├── web_interface.py     # Web interface
│   ├── enhanced_widgets.py  # Enhanced GUI widgets
│   ├── vram_monitor.py      # GPU memory monitoring
│   └── error_handler.py     # Error handling system
├── scripts/                  # Utility scripts
│   ├── install_dependencies.py # Dependency installer
│   ├── install_dependencies.bat # Windows dependency installer
│   ├── create_distribution.py # Distribution creator
│   ├── create_launcher_icon.py # Icon generator
│   └── test_*.py            # Test suite
├── config/                   # Configuration files
│   ├── launcher_config.json # Launcher settings
│   ├── requirements.txt     # Python dependencies
│   └── VERSION.txt          # Version information
├── docs/                     # Documentation
├── data/                     # Data and logs
├── logs/                     # Additional logs
├── plugins/                  # Plugin system
├── templates/                # Web templates
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

## 📋 System Requirements

- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.7 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 100MB for launcher + space for your AI models

### **Required Dependencies**
The launcher automatically installs:
- **tkinter** - GUI framework (usually included with Python)
- **psutil** - Process and system monitoring
- **PIL/Pillow** - Image processing
- **pystray** - System tray support
- **GPUtil** - GPU monitoring and VRAM management

### **Optional Dependencies**
For advanced features (installed automatically if available):
- **Flask** - Web interface and API server
- **Flask-SocketIO** - Real-time WebSocket support
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-Limiter** - API rate limiting
- **PyJWT** - JWT token authentication
- **matplotlib** - Analytics charts and graphs
- **numpy** - Numerical computing for analytics
- **requests** - HTTP client for API calls

## 🔧 Configuration

### **Automatic Configuration**
The launcher automatically:
- **Detects batch files** in your project structure
- **Sets default ports** (Oobabooga: 7860, Z-Waifu: 5000)
- **Creates config files** with sensible defaults
- **Validates paths** for security
- **Backs up config** before changes

### **Manual Configuration**
Edit `config/launcher_config.json` to customize:
- **Batch file paths** for each AI tool
- **Port settings** for services
- **Theme preferences** (light/dark)
- **Auto-start options** for processes
- **VRAM monitoring settings** - Thresholds, cleanup options
- **Analytics preferences** - Data collection, retention settings

## 🛠️ Troubleshooting

### **Common Issues**

**"Python not found"**
- Install Python 3.7+ from https://python.org
- Ensure Python is in your system PATH

**"Dependencies not installed"**
- Run `python scripts/install_dependencies.py`
- Or use the smart launcher: `python launch_launcher.py`

**"Batch files not found"**
- Use the Settings tab to browse and select batch files
- Or place batch files in the project directory for auto-detection

**"Port already in use"**
- Change ports in Settings tab
- Or stop the process using the port

**"VRAM issues"**
- Check VRAM monitoring settings in Settings tab
- Enable auto-cleanup for automatic memory management
- Monitor GPU usage in Advanced tab

### **Getting Help**

1. **Check the logs** in `data/launcher_log.txt`
2. **Run the test suite**: `python test_fixes.py`
3. **Use diagnostic tool**: `python scripts/diagnostic_tool.py`
4. **Check documentation** in the `docs/` folder

## 🔒 Security Features

- **Path validation** - Prevents directory traversal attacks
- **Command injection protection** - Validates all inputs
- **API key authentication** - Secure API access
- **Rate limiting** - Prevents abuse
- **Input sanitization** - Cleans user inputs
- **Config backup** - Automatic backup before changes
- **Enhanced error handling** - Secure error reporting without data leakage
- **Process isolation** - Safe process management and termination

## 📊 Performance

- **Memory efficient** - Automatic cleanup of old terminal lines
- **Thread-safe** - Safe concurrent operations
- **Fast startup** - Optimized initialization
- **Responsive UI** - Non-blocking operations
- **Resource monitoring** - Real-time performance tracking
- **VRAM optimization** - Automatic GPU memory management
- **Process monitoring** - Real-time CPU and memory tracking
- **Performance analytics** - Historical performance data and trends

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Run tests**: `python test_fixes.py`
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Oobabooga** team for the text generation web UI
- **Z-Waifu** developers for the AI companion system
- **Ollama** team for the local LLM framework
- **RVC** community for voice cloning technology

---

**Ready to launch?** Run `python launch_launcher.py` and enjoy your AI tools! 🚀 
# Z-Waifu Launcher GUI

A powerful, feature-rich GUI launcher for managing AI/ML processes including Oobabooga, Z-Waifu, Ollama, and RVC with advanced terminal emulation and instance management.

## 🚀 Quick Start

### Option 1: Simple Launch (Recommended)
1. **Double-click** `launch_launcher.bat` to start the launcher
2. The script will automatically check and install dependencies
3. The GUI will open and you can start configuring

### Option 2: Manual Launch
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the launcher**:
   ```bash
   python zwaifu_launcher_gui.py
   ```

### Option 3: Smart Launcher
1. **Run the smart launcher**:
   ```bash
   python launch_launcher.py
   ```
2. This will automatically install missing dependencies

## 🎯 Features

### Core Functionality
- **Multi-Process Management**: Launch and manage Oobabooga, Z-Waifu, Ollama, and RVC processes
- **Embedded Terminal Emulator**: Full-featured terminal with ANSI color support, command history, and real-time output
- **Instance Manager**: Centralized management of all running process instances
- **Auto-Detection**: Automatically finds batch files in your project structure
- **Theme Support**: Light and dark mode with customizable themes
- **Process Monitoring**: Real-time CPU, memory, and uptime tracking

### Advanced Terminal Features
- **ANSI Color Support**: Full color parsing and display from process output
- **Command History**: Navigate with up/down arrow keys
- **Real-time Input**: Send commands directly to processes
- **Thread-safe Operations**: Safe concurrent access to stdin/stdout
- **Process Attachment**: Easy attachment to subprocess.Popen objects

### Multi-Instance Support
- **Multiple Tabs**: Each process instance gets its own tab
- **Independent Terminals**: Each instance has its own terminal emulator
- **Process Tracking**: Comprehensive tracking of all running instances
- **Instance Management**: Centralized control through Instance Manager

### Instance Manager
- **Central Dashboard**: Real-time list of all running process instances
- **Status Monitoring**: Shows Running/Stopped status, PID, and uptime for each instance
- **Individual Controls**: Stop, restart, and kill buttons for each instance
- **Bulk Operations**: "Kill All" button to terminate all running instances
- **Focus Navigation**: Double-click any instance to focus its terminal tab
- **Auto-refresh**: Updates every 5 seconds to show current status

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

## 📋 System Requirements

- **Operating System**: Windows 10/11 (tested)
- **Python**: 3.7 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 100MB for launcher + space for your AI models

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

#### Option 1: Automatic Installation
1. Download the distribution zip file
2. Extract to your desired location
3. Double-click `launch_launcher.bat`
4. The launcher will automatically install dependencies

#### Option 2: Manual Installation
1. **Install dependencies**:
   ```bash
   pip install psutil pillow pystray
   ```
2. **Run the launcher**:
   ```bash
   python zwaifu_launcher_gui.py
   ```

#### Option 3: Smart Installation
1. **Run the smart launcher**:
   ```bash
   python launch_launcher.py
   ```
2. This will automatically install missing dependencies

## 🎯 First Launch

### 1. Start the Launcher
- Double-click `launch_launcher.bat` or run `python zwaifu_launcher_gui.py`

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

## 🔧 Advanced Configuration

### CMD Flags Editor
1. Go to the **CMD Flags** tab
2. Edit Oobabooga command line flags
3. Add flags like `--listen`, `--api`, `--extensions api`
4. Save your changes

### Instance Management
1. Use individual process tabs to launch multiple instances
2. Use the **Instance Manager** to monitor all running instances
3. Each instance gets its own terminal with controls

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
python create_distribution.py
```
Creates a complete distribution package (~37 KB) with all files and documentation.

#### Minimal Distribution
```bash
python create_distribution.py --minimal
```
Creates a minimal distribution package (~30 KB) with essential files only.

### Distribution Contents

#### Full Distribution (`Z-Waifu-Launcher-GUI-v1.0.0.zip`)
- ✅ Main launcher application (`zwaifu_launcher_gui.py`)
- ✅ Smart launcher with dependency checking (`launch_launcher.py`)
- ✅ Windows batch launcher (`launch_launcher.bat`)
- ✅ Test suite (`test_launcher.py`)
- ✅ Dependencies list (`requirements.txt`)
- ✅ Complete documentation (`README.md`, `INSTALLATION_GUIDE.md`)
- ✅ Version information (`VERSION.txt`)
- ✅ Quick start guide (`QUICK_START.txt`)
- ✅ System requirements (`REQUIREMENTS.txt`)
- ✅ Changelog (`CHANGELOG.txt`)

#### Minimal Distribution (`Z-Waifu-Launcher-GUI-Minimal-v1.0.0.zip`)
- ✅ Main launcher application (`zwaifu_launcher_gui.py`)
- ✅ Smart launcher (`launch_launcher.py`)
- ✅ Windows batch launcher (`launch_launcher.bat`)
- ✅ Dependencies list (`requirements.txt`)
- ✅ Basic documentation (`README.md`)

For detailed distribution information, see [DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md).

## 🧪 Testing

Run the test suite to verify everything works:
```bash
python test_launcher.py
```

This will test:
- ✅ GUI creation
- ✅ Terminal emulator
- ✅ Instance manager
- ✅ All imports and initialization

## 🔍 Troubleshooting

### Common Issues

#### "Python not found"
- Install Python and check "Add to PATH"
- Restart your command prompt after installation

#### "Module not found"
- Run: `pip install -r requirements.txt`
- Or use the smart launcher: `python launch_launcher.py`

#### "Batch file not found"
- Use Settings tab to browse and select batch files
- Ensure batch files exist and are executable

#### "Port already in use"
- Change port settings in Settings tab
- Stop any existing processes using those ports

#### "Process failed to start"
- Check batch file path is correct
- Verify batch file works when run manually
- Check for missing dependencies in batch files

### Debug Information

#### Logs
- Check the **Logs** tab for detailed application logs
- View `launcher_log.txt` for file-based logs

#### Console Output
- Run from command line to see console output
- Check for error messages during startup

#### Process Status
- Use **Instance Manager** to monitor process state
- Check individual terminal tabs for process output

### Getting Help

1. **Check the logs** in the Logs tab
2. **Run the test suite**: `python test_launcher.py`
3. **Verify dependencies**: `pip list`
4. **Check file paths** in Settings tab
5. **Review console output** for error messages

## 📁 File Structure

```
ZWAIFU-PROJECT/
├── zwaifu_launcher_gui.py    # Main launcher application
├── launch_launcher.py        # Smart launcher with dependency check
├── launch_launcher.bat       # Windows batch launcher
├── test_launcher.py          # Test suite
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── INSTALLATION_GUIDE.md     # Detailed installation guide
├── DISTRIBUTION_GUIDE.md     # Distribution creation guide
├── create_distribution.py    # Distribution creator script
├── create_distribution.bat   # Distribution creator batch file
├── launcher_config.json      # Configuration file (auto-created)
├── launcher_log.txt          # Application logs (auto-created)
├── text-generation-webui-main/  # Oobabooga installation
├── z-waif-1.14-R4/          # Z-Waifu installation
└── [other project files]
```

## 🔄 Updates

### Updating the Launcher
1. Download the latest version
2. Replace the launcher files
3. Your configuration will be preserved

### Updating Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 📊 Features Overview

### GUI Tabs
- **Main**: Start/stop all processes, main log, program output
- **Settings**: Configuration, batch files, ports, themes
- **CMD Flags**: Oobabooga command line flags editor
- **About**: Information and links
- **Ollama**: Ollama process management
- **RVC**: RVC process management
- **Logs**: Application logs and debugging
- **Instance Manager**: Centralized process management

### Process Management
- **Multiple Instances**: Launch multiple instances of each process type
- **Individual Controls**: Stop, restart, kill, clear for each instance
- **Terminal Emulation**: Full-featured terminal with ANSI colors
- **Process Monitoring**: Real-time CPU, memory, and uptime tracking
- **Graceful Termination**: Proper cleanup of processes and child processes

### User Experience
- **Auto-detection**: Automatically finds batch files
- **Smart Dependencies**: Automatic installation of missing packages
- **Theme Support**: Light and dark mode
- **Configuration Persistence**: Settings saved between sessions
- **Error Handling**: Comprehensive error checking and user feedback

## 🎯 Use Cases

### Development
- **Multiple Model Testing**: Run different models simultaneously
- **Process Debugging**: Real-time output and control
- **Configuration Management**: Easy CMD flags editing

### Production
- **Server Management**: Monitor and control AI services
- **Multi-user Environment**: Multiple instances for different users
- **Automation**: Scriptable process management

### Learning
- **AI/ML Workflow**: Integrated management of AI tools
- **Process Understanding**: Real-time monitoring and control
- **Configuration Learning**: Visual CMD flags editing

## 🆘 Support

For issues and questions:
1. Check this README and installation guide
2. Review the troubleshooting section
3. Check the logs in the Logs tab
4. Run the test suite to verify installation
5. Ensure all dependencies are installed

## 📈 Performance

### System Impact
- **Memory Usage**: ~50-100 MB (depending on number of instances)
- **CPU Usage**: Minimal when idle, scales with process monitoring
- **Disk Usage**: ~100 MB for launcher + logs

### Scalability
- **Multiple Instances**: Support for unlimited instances (limited by system resources)
- **Process Monitoring**: Efficient monitoring with minimal overhead
- **Terminal Performance**: Smooth scrolling and input handling

## 🔮 Future Features

### Planned Enhancements
- **Web Interface**: Browser-based management
- **API Integration**: REST API for remote management
- **Plugin System**: Extensible architecture for custom features
- **Mobile Support**: Mobile app for remote monitoring
- **Advanced Analytics**: Detailed performance metrics and reporting

### Community Contributions
- **Custom Themes**: User-created theme packs
- **Process Templates**: Pre-configured process setups
- **Integration Scripts**: Custom automation scripts
- **Documentation**: User guides and tutorials

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_launcher.py`
5. Submit a pull request

### Testing
- Run the test suite: `python test_launcher.py`
- Test on different Python versions
- Verify all features work correctly

---

**Happy launching! 🚀**

For detailed installation instructions, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md).
For distribution information, see [DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md). 
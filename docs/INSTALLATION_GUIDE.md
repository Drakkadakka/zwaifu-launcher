# Z-Waifu Launcher GUI - Installation Guide

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 (tested), Linux/macOS (experimental)
- **Python**: 3.7 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 100MB for launcher + space for your AI models

### Required Software
1. **Python 3.7+**: Download from [python.org](https://www.python.org/downloads/)
   - **Important**: Check "Add Python to PATH" during installation
   - Verify installation: `python --version`

2. **Git** (optional): For cloning the repository
   - Download from [git-scm.com](https://git-scm.com/)

## 🚀 Installation Methods

### Method 1: Distribution Package (Recommended)

#### Step 1: Download
1. Download the latest distribution package:
   - **Full Version**: `Z-Waifu-Launcher-GUI-v1.1.0.zip`
   - **Minimal Version**: `Z-Waifu-Launcher-GUI-Minimal-v1.1.0.zip`

#### Step 2: Extract
1. Extract the zip file to your desired location
2. Navigate to the extracted folder

#### Step 3: Launch
1. **Windows**: Double-click `scripts/launch_launcher.bat`
2. **All Platforms**: Run `python scripts/launch_launcher.py`
3. The launcher will automatically install dependencies

### Method 2: Source Code Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/Drakkadakka/zwaifu-launcher.git
cd zwaifu-launcher
```

#### Step 2: Install Dependencies
```bash
# Install core dependencies
pip install -r config/requirements.txt

# Or use the automatic installer
python scripts/install_dependencies.py
```

#### Step 3: Launch
```bash
# Direct launch
python zwaifu_launcher_gui.py

# Or use the smart launcher
python scripts/launch_launcher.py
```

### Method 3: Virtual Environment (Recommended for Development)

#### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r config/requirements.txt
```

#### Step 3: Launch
```bash
python zwaifu_launcher_gui.py
```

## 🔧 Configuration

### First Launch Setup

#### Step 1: Start the Launcher
- Run `python zwaifu_launcher_gui.py` or double-click `scripts/launch_launcher.bat`

#### Step 2: Configure Batch Files
1. Go to the **Settings** tab
2. Browse and select your batch files:
   - **Oobabooga**: `text-generation-webui-main/start_windows.bat`
   - **Z-Waifu**: `z-waif-1.14-R4/startup.bat`
   - **Ollama**: `ollama/ollama.bat` (if using)
   - **RVC**: `rvc/rvc.bat` (if using)

#### Step 3: Configure Ports
1. Set your preferred ports:
   - **Oobabooga**: Default 7860
   - **Z-Waifu**: Default 5000
   - **Web Interface**: Default 8080
   - **API Server**: Default 8081
   - **Mobile App**: Default 8082

#### Step 4: Save Settings
1. Click "Save Settings" to store your configuration
2. Settings are automatically saved to `config/launcher_config.json`

### Advanced Configuration

#### CMD Flags Editor
1. Go to the **CMD Flags** tab
2. Edit Oobabooga command line flags
3. Click "Save File" to apply changes
4. Flags are saved to `ai_tools/oobabooga/CMD_FLAGS.txt`

#### Theme Configuration
1. Go to the **Settings** tab
2. Choose between Light and Dark themes
3. Theme preference is automatically saved

#### Auto-Start Configuration
1. Go to the **Settings** tab
2. Enable auto-start for desired processes
3. Processes will start automatically when launcher launches

## 📦 Dependencies

### Core Dependencies (Required)
- `psutil >= 5.8.0` - System and process monitoring
- `Pillow >= 8.0.0` - Image processing
- `pystray >= 0.17.0` - System tray support

### Advanced Features Dependencies (Optional)
- `Flask >= 2.0.0` - Web interface
- `Flask-SocketIO >= 5.0.0` - Real-time updates
- `Flask-CORS >= 3.0.0` - Cross-origin support
- `Flask-Limiter >= 3.0.0` - API rate limiting
- `PyJWT >= 2.0.0` - API authentication
- `matplotlib >= 3.5.0` - Analytics charts
- `numpy >= 1.21.0` - Data processing
- `requests >= 2.25.0` - HTTP client
- `qrcode >= 7.0.0` - QR code generation

### Installation Commands
```bash
# Core dependencies only
pip install psutil pillow pystray

# All dependencies (including advanced features)
pip install -r config/requirements.txt

# Individual advanced features
pip install flask flask-socketio flask-cors  # Web interface
pip install matplotlib numpy                 # Analytics
pip install requests qrcode                  # Mobile support
```

## 🧪 Testing Installation

### Basic Test
```bash
python scripts/test_launcher.py
```

### Advanced Features Test
```bash
python scripts/test_advanced_features.py
```

### Manual Verification
1. Launch the application
2. Check that all tabs load correctly
3. Verify that settings can be saved
4. Test that batch file browsing works
5. Confirm that theme switching works

## 🔍 Troubleshooting

### Common Issues

#### Python Not Found
```bash
# Check Python installation
python --version

# If not found, add Python to PATH or reinstall
```

#### Import Errors
```bash
# Install missing dependencies
python scripts/launch_launcher.py

# Or manually install
pip install -r config/requirements.txt
```

#### Batch Files Not Found
1. Verify batch file paths in Settings
2. Check that files exist at specified locations
3. Ensure batch files have correct permissions

#### Port Already in Use
1. Change ports in Settings tab
2. Or stop the process using the port
3. Check for other instances of the launcher

#### Advanced Features Not Working
1. Install optional dependencies:
   ```bash
   pip install flask flask-socketio matplotlib numpy requests qrcode
   ```
2. Check launcher logs for error messages
3. Run test suite: `python scripts/test_advanced_features.py`

### Log Files
- **Main Log**: `data/launcher_log.txt`
- **Oobabooga Log**: `data/ooba_log.txt`
- **Analytics Database**: `data/analytics.db`

### Getting Help
1. Check the logs for error messages
2. Run the test suite to identify issues
3. Review the documentation in `docs/`
4. Check the project structure in `docs/PROJECT_STRUCTURE.md`

## 🚀 Quick Start After Installation

### 1. Launch the Application
```bash
python zwaifu_launcher_gui.py
```

### 2. Configure Your AI Tools
1. Go to Settings tab
2. Browse and select your batch files
3. Set your preferred ports
4. Save settings

### 3. Start Your Processes
1. Go to Main tab
2. Click "Start All" to launch all configured processes
3. Or use individual tabs for specific processes

### 4. Access Advanced Features
1. **Web Interface**: http://localhost:8080
2. **API Server**: http://localhost:8081/api
3. **Mobile App**: http://localhost:8082
4. **Analytics**: View in Advanced tab

### 5. Monitor and Manage
1. Use Instance Manager to monitor all processes
2. Check individual terminal tabs for process output
3. Use web interface for remote management
4. View analytics for performance monitoring

## 📚 Next Steps

### Documentation
- **README.md** - Main project overview
- **docs/API_DOCUMENTATION.md** - REST API reference
- **docs/PLUGIN_GUIDE.md** - Plugin development guide
- **docs/PROJECT_STRUCTURE.md** - Project organization

### Development
- **Plugin Development**: See `docs/PLUGIN_GUIDE.md`
- **API Integration**: See `docs/API_DOCUMENTATION.md`
- **Testing**: Run `python scripts/test_advanced_features.py`
- **Distribution**: See `docs/DISTRIBUTION_GUIDE.md`

### Support
- **Issues**: Check launcher logs in `data/launcher_log.txt`
- **Testing**: Run test suite for diagnostics
- **Documentation**: Review all files in `docs/` directory
- **Community**: Check project repository for updates
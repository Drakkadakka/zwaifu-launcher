# Z-Waifu Launcher GUI - Installation Guide

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

## 📋 System Requirements

- **Operating System**: Windows 10/11 (tested)
- **Python**: 3.7 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 100MB for launcher + space for your AI models

## 🔧 Installation Steps

### 1. Prerequisites

#### Install Python
1. Download Python 3.7+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```bash
   python --version
   ```

#### Install Git (Optional)
- Download from [git-scm.com](https://git-scm.com/)
- Required only if you want to clone the repository

### 2. Get the Launcher

#### Option A: Download ZIP
1. Download the project ZIP file
2. Extract to your desired location
3. Open the extracted folder

#### Option B: Clone Repository
```bash
git clone https://github.com/Drakkadakka/zwaifu-launcher.git
cd zwaifu-launcher
```

### 3. Install Dependencies

#### Automatic Installation
The launcher will automatically install dependencies when you run it.

#### Manual Installation
```bash
pip install psutil pillow pystray
```

### 4. Configure Your Environment

#### Set Up AI Tools
1. **Oobabooga**: Install in `text-generation-webui-main/` folder
2. **Z-Waifu**: Install in `z-waif-1.14-R4/` folder
3. **Ollama**: Install Ollama and create batch files
4. **RVC**: Install RVC and create batch files

#### Batch File Setup
The launcher will auto-detect common batch file locations:
- `text-generation-webui-main/start_windows.bat` (Oobabooga)
- `z-waif-1.14-R4/startup.bat` (Z-Waifu)
- Various Ollama and RVC batch files

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

## 🧪 Testing Your Installation

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
├── README.md                 # Main documentation
├── INSTALLATION_GUIDE.md     # This file
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

## 🆘 Support

For issues and questions:
1. Check this installation guide
2. Review the troubleshooting section
3. Check the logs in the Logs tab
4. Run the test suite to verify installation
5. Ensure all dependencies are installed

---

**Happy launching! 🚀** 
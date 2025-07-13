# Z-Waifu Launcher - Quick Start Guide

## Prerequisites
- Python 3.7 or higher installed on your system
- Windows operating system (for batch files)

## Quick Start

### Option 1: Simple Batch File (Recommended)
1. Double-click `launch_launcher.bat` in the project root directory
2. The script will automatically:
   - Check if Python is installed
   - Create a virtual environment if needed
   - Install all required dependencies
   - Start the launcher GUI

### Option 2: Python Script
1. Open a command prompt in the project root directory
2. Run: `python launch_launcher.py`
3. The script will handle all setup automatically

### Option 3: Manual Setup
1. Open a command prompt in the project root directory
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate.bat`
4. Install dependencies: `pip install -r config\requirements.txt`
5. Run launcher: `python zwaifu_launcher_gui.py`

## Troubleshooting

### "Python is not installed" Error
- Download and install Python 3.7+ from https://python.org
- Make sure to check "Add Python to PATH" during installation

### "requirements.txt not found" Error
- Make sure you're running the script from the project root directory
- The requirements.txt file should be in the `config` folder

### "zwaifu_launcher_gui.py not found" Error
- Make sure you're running the script from the project root directory
- The main launcher file should be in the root directory

### Virtual Environment Issues
- Delete the `venv` folder and run the launcher again
- The script will recreate the virtual environment

## File Structure
```
ZWAIFU-PROJECT/
├── zwaifu_launcher_gui.py    # Main launcher file
├── launch_launcher.bat       # Windows batch launcher
├── launch_launcher.py        # Python launcher script
├── config/
│   └── requirements.txt      # Python dependencies
├── venv/                     # Virtual environment (created automatically)
└── ...
```

## Support
If you encounter any issues, please check:
1. Python version (should be 3.7+)
2. You're running from the correct directory
3. All files are present in the project structure

For additional help, please refer to the main README.md file or create an issue on the project repository. 
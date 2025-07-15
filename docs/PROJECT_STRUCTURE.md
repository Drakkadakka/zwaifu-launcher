# Z-Waifu Launcher GUI - Project Structure

## 📁 Directory Overview

```
ZWAIFU-PROJECT/
├── zwaifu_launcher_gui.py    # Main launcher application
├── README.md                 # Main project documentation
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore patterns
├── utils/                    # Utility modules package
├── scripts/                  # Utility scripts and tools
├── config/                   # Configuration files
├── docs/                     # Documentation files
├── data/                     # Data storage and logs
├── logs/                     # Additional logs
├── plugins/                  # Plugin system
├── templates/                # Web interface templates
├── static/                   # Web assets
├── ai_tools/                 # AI tool configurations
├── venv/                     # Virtual environment (not in git)
├── __pycache__/              # Python cache (not in git)
└── [distribution zips]       # Distribution packages
```

## 📂 Detailed Structure

### Root Directory
- **`zwaifu_launcher_gui.py`** - Main launcher application (2885 lines)
  - Core GUI implementation
  - Process management
  - Terminal emulator
  - Theme system
  - Advanced features integration

- **`README.md`** - Main project documentation
  - Quick start guide
  - Feature overview
  - Installation instructions
  - Usage examples

- **`LICENSE`** - MIT License file
- **`.gitignore`** - Git ignore patterns for Python projects

### `utils/` - Utility Modules Package
```
utils/
├── __init__.py              # Package initialization and exports
├── analytics_system.py      # Analytics and performance monitoring
├── mobile_app.py            # Mobile web interface
├── plugin_system.py         # Plugin management system
├── api_server.py            # REST API server
└── web_interface.py         # Web interface and dashboard
```

**Purpose**: Contains all utility modules that provide advanced features to the main launcher.

**Key Files**:
- **`__init__.py`** - Exports all utility classes for easy importing
- **`analytics_system.py`** - Performance monitoring, metrics collection, reporting
- **`mobile_app.py`** - Mobile-optimized web interface with QR code access
- **`plugin_system.py`** - Plugin architecture with hot reloading and event system
- **`api_server.py`** - REST API with authentication, rate limiting, and comprehensive endpoints
- **`web_interface.py`** - Web dashboard with real-time updates and process control

### `scripts/` - Utility Scripts and Tools
```
scripts/
├── launch_launcher.py       # Smart launcher with dependency checking
├── launch_launcher.bat      # Windows batch launcher
├── launch_ooba_zwaifu.bat   # Combined Oobabooga + Z-Waifu launcher
├── install_dependencies.py  # Dependency installer
├── install_dependencies.bat # Windows dependency installer
├── create_distribution.py   # Distribution package creator
├── create_distribution.bat  # Windows distribution creator
├── update_flash_calls.py    # Utility for updating flash calls
├── setup_venv_and_run_launcher.bat # Virtual environment setup
├── launcher.spec            # PyInstaller specification
├── test_launcher.py         # Basic launcher tests
├── test_advanced_features.py # Advanced features test suite
├── test_flash_effect.py     # Flash effect tests
├── test_tab_switching.py    # Tab switching tests
├── test_theme_toggle.py     # Theme toggle tests
├── create_launcher_icon.py  # Icon generator
└── organize_project.py      # Project organization utility
```

**Purpose**: Contains all utility scripts for launching, testing, installing, and distributing the launcher.

**Key Scripts**:
- **`launch_launcher.py`** - Smart launcher that checks dependencies and handles errors
- **`install_dependencies.py`** - Automatic dependency installation and verification
- **`create_distribution.py`** - Creates distribution packages with proper file organization
- **`test_*.py`** - Comprehensive test suite for all features

### `config/` - Configuration Files
```
config/
├── launcher_config.json     # Launcher settings and preferences
├── requirements.txt         # Python dependencies list
├── VERSION.txt             # Version information
└── project_config.json     # Project configuration metadata
```

**Purpose**: Centralized configuration management for the launcher.

**Key Files**:
- **`launcher_config.json`** - User settings, batch file paths, theme preferences
- **`requirements.txt`** - Python package dependencies with versions
- **`VERSION.txt`** - Current version and build information

### `docs/` - Documentation Files
```
docs/
├── README.md               # Main documentation (duplicate of root)
├── INSTALLATION_GUIDE.md   # Comprehensive installation guide
├── CHANGELOG.md           # Version history and changes
├── API_DOCUMENTATION.md   # REST API reference
├── PLUGIN_GUIDE.md        # Plugin development guide
├── PROJECT_STRUCTURE.md   # This file
├── DISTRIBUTION_GUIDE.md  # Distribution creation guide
└── INSTALL.txt           # Quick installation instructions
```

**Purpose**: Complete documentation for users and developers.

**Key Files**:
- **`INSTALLATION_GUIDE.md`** - Step-by-step installation instructions
- **`API_DOCUMENTATION.md`** - Complete REST API reference
- **`PLUGIN_GUIDE.md`** - Plugin development and usage guide
- **`CHANGELOG.md`** - Detailed version history and feature changes

### `data/` - Data Storage and Logs
```
data/
├── analytics.db            # SQLite database for analytics
├── launcher_log.txt        # Main application log
└── ooba_log.txt           # Oobabooga process log
```

**Purpose**: Persistent data storage and logging.

**Key Files**:
- **`analytics.db`** - Performance metrics and historical data
- **`launcher_log.txt`** - Application events and error logging

### `logs/` - Additional Logs
```
logs/
└── .gitkeep               # Keep directory in git
```

**Purpose**: Additional log storage for future expansion.

### `plugins/` - Plugin System
```
plugins/
├── __init__.py            # Plugin package initialization
├── README.md              # Plugin documentation
├── process_monitor.py     # Example process monitoring plugin
├── auto_restart.py        # Example auto-restart plugin
└── .gitkeep               # Keep directory in git
```

**Purpose**: Extensible plugin system for custom features.

**Key Features**:
- **Hot reloading** - Load/unload plugins without restart
- **Event system** - Plugin hooks for process events
- **Configuration** - Per-plugin configuration storage
- **Example plugins** - Process monitoring and auto-restart

### `templates/` - Web Interface Templates
```
templates/
├── dashboard.html         # Main web dashboard template
├── mobile_dashboard.html  # Mobile-optimized dashboard
└── .gitkeep              # Keep directory in git
```

**Purpose**: HTML templates for web interface.

**Key Files**:
- **`dashboard.html`** - Full-featured web dashboard
- **`mobile_dashboard.html`** - Touch-friendly mobile interface

### `static/` - Web Assets
```
static/
├── css/
│   ├── style.css         # Main stylesheet
│   └── .gitkeep          # Keep directory in git
├── js/
│   ├── app.js            # Main JavaScript application
│   └── .gitkeep          # Keep directory in git
└── images/
    ├── launcher_icon.png # Launcher icon
    └── .gitkeep          # Keep directory in git
```

**Purpose**: Static assets for web interface.

**Key Files**:
- **`css/style.css`** - Modern, responsive styling
- **`js/app.js`** - Interactive web application logic
- **`images/launcher_icon.png`** - Application icon

### `ai_tools/` - AI Tool Configurations
```
ai_tools/
├── oobabooga/
│   ├── README.md         # Oobabooga setup guide
│   ├── CMD_FLAGS.txt     # Command line flags
│   └── start_windows - Ooba.lnk # Windows shortcut
├── zwaifu/
│   └── README.md         # Z-Waifu setup guide
├── ollama/
│   └── README.md         # Ollama setup guide
└── rvc/
    └── README.md         # RVC setup guide
```

**Purpose**: Configuration and setup guides for supported AI tools.

**Key Files**:
- **`oobabooga/CMD_FLAGS.txt`** - Editable command line flags
- **Setup guides** - Installation and configuration instructions

## 🔄 File Organization Principles

### 1. Separation of Concerns
- **Core application** in root directory
- **Utility modules** in `utils/` package
- **Scripts and tools** in `scripts/` directory
- **Configuration** in `config/` directory
- **Documentation** in `docs/` directory

### 2. Modular Design
- **Independent modules** that can be imported separately
- **Clear interfaces** between components
- **Plugin architecture** for extensibility
- **Configuration-driven** behavior

### 3. User-Friendly Structure
- **Intuitive organization** - easy to find files
- **Clear naming** - descriptive file and directory names
- **Logical grouping** - related files together
- **Documentation** - comprehensive guides and examples

### 4. Development-Friendly
- **Test suite** - comprehensive testing
- **Build scripts** - automated distribution creation
- **Development tools** - utilities for development
- **Version control** - proper .gitignore and structure

## 📦 Distribution Structure

### Full Distribution
```
Z-Waifu-Launcher-GUI-v1.1.0/
├── zwaifu_launcher_gui.py
├── README.md
├── LICENSE
├── utils/
├── scripts/
├── config/
├── docs/
├── data/
├── logs/
├── plugins/
├── templates/
├── static/
├── ai_tools/
├── VERSION.txt
├── QUICK_START.txt
└── REQUIREMENTS.txt
```

### Minimal Distribution
```
Z-Waifu-Launcher-GUI-Minimal-v1.1.0/
├── zwaifu_launcher_gui.py
├── README.md
├── scripts/launch_launcher.py
├── scripts/launch_launcher.bat
└── config/requirements.txt
```

## 🔧 Development Workflow

### 1. Development Setup
```bash
# Clone repository
git clone https://github.com/Drakkadakka/zwaifu-launcher.git
cd zwaifu-launcher

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r config/requirements.txt
```

### 2. Running Development Version
```bash
# Direct launch
python zwaifu_launcher_gui.py

# Or use smart launcher
python scripts/launch_launcher.py
```

### 3. Testing
```bash
# Basic tests
python scripts/test_launcher.py

# Advanced features tests
python scripts/test_advanced_features.py
```

### 4. Building Distribution
```bash
# Full distribution
python scripts/create_distribution.py

# Minimal distribution
python scripts/create_distribution.py --minimal
```

## 📚 Key Design Decisions

### 1. Package Structure
- **`utils/` package** - Centralized utility modules
- **`scripts/` directory** - All executable scripts
- **`config/` directory** - Centralized configuration
- **`docs/` directory** - Complete documentation

### 2. Import Strategy
- **Relative imports** within packages
- **Absolute imports** for main application
- **Fallback imports** for missing dependencies
- **Clear import hierarchy** - no circular dependencies

### 3. Configuration Management
- **JSON configuration** for user settings
- **Environment-based** configuration
- **Default values** for all settings
- **Validation** of configuration data

### 4. Logging Strategy
- **Centralized logging** in `data/` directory
- **Structured logging** with timestamps
- **Error tracking** and debugging information
- **Performance metrics** storage

### 5. Testing Approach
- **Comprehensive test suite** in `scripts/`
- **Unit tests** for individual components
- **Integration tests** for full system
- **Automated testing** for distribution builds

This structure provides a clean, maintainable, and extensible foundation for the Z-Waifu Launcher GUI project. 
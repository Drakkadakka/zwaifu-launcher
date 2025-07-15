#!/bin/bash

# Z-Waifu Launcher Linux Distribution Creator
# ==========================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
VERSION="1.0.0"
DIST_NAME="Z-Waifu-Launcher-GUI-v${VERSION}-Linux"
OUTPUT_FILE="${DIST_NAME}.tar.gz"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create exclude list
create_exclude_list() {
    local exclude_file="zwaifu_exclude_linux.txt"
    
    print_status "Creating exclude list..."
    
    cat > "$exclude_file" << 'EOF'
venv/
logs/
__pycache__/
.git/
.idea/
.vscode/
*.pyc
*.log
*.tmp
*.rar
*.zip
*.7z
Z-Waifu-Launcher-GUI-*.zip
Z-Waifu-Launcher-GUI-*.rar
text-generation-webui-main/
z-waif-1.14-R4/
MMVCServerSIO/
MMVCServerSIO.rar
backups/
security_backups/
.mypy_cache/
advanced_statistics_*.json
api_key.json
debug_output.txt
zwaifu_launcher_gui.py.backup
ZWAIFU-PROJECT.zip
zwaifu_exclude*.txt
*.egg-info/
build/
dist/
.Python
.installed.cfg
*.egg
.DS_Store
Thumbs.db
*.swp
*.swo
config_backup_*.json
EOF
    
    echo "$exclude_file"
}

# Function to create Linux-specific files
create_linux_files() {
    print_status "Creating Linux-specific files..."
    
    # Ensure all Linux files exist and are executable
    linux_files=(
        "launch_launcher.sh"
        "run.sh" 
        "install_linux.sh"
        "zwaifu-launcher.desktop"
        "test_linux_compatibility.py"
        "README_LINUX.md"
        "LINUX_SETUP.md"
    )
    
    for file in "${linux_files[@]}"; do
        if [ -f "$file" ]; then
            # Make shell scripts executable
            if [[ "$file" == *.sh ]]; then
                chmod +x "$file"
            fi
            print_status "  $file - OK" "SUCCESS"
        else
            print_warning "  $file - MISSING"
        fi
    done
    
    # Create a Linux-specific README if it doesn't exist
    if [ ! -f "README_LINUX.md" ]; then
        cat > "README_LINUX.md" << 'EOF'
# Z-Waifu Launcher for Linux

## Quick Start

### Option 1: Automatic Installation
```bash
chmod +x install_linux.sh
./install_linux.sh
```

### Option 2: Manual Launch
```bash
chmod +x launch_launcher.sh
./launch_launcher.sh
```

## System Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- xdg-utils (for desktop integration)

## Installation

The installation script will:
1. Install system dependencies
2. Create a virtual environment
3. Install Python dependencies
4. Create desktop integration
5. Set up systemd service (optional)

## Usage

After installation, you can launch the application using:
- Desktop application menu
- Command: `zwaifu-launcher`
- Command: `/opt/zwaifu-launcher/launch_launcher.sh`

## Uninstallation

To uninstall, run:
```bash
/opt/zwaifu-launcher/uninstall.sh
```

## Troubleshooting

### tkinter not found
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Arch Linux
sudo pacman -S tk
```

### Permission denied
```bash
chmod +x launch_launcher.sh
chmod +x install_linux.sh
```

## Support

For issues and support, please check the main documentation or create an issue on the project repository.
EOF
    
    # Create a simple launcher script for direct execution
    cat > "run.sh" << 'EOF'
#!/bin/bash

# Simple launcher for Z-Waifu
# This script can be run directly from the extracted directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check for tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "ERROR: tkinter is not installed"
    echo "Please install python3-tk package for your distribution"
    exit 1
fi

# Run the launcher
python3 launch_launcher.py
EOF
    
    chmod +x "run.sh"
    chmod +x "launch_launcher.sh"
    chmod +x "install_linux.sh"
    
    print_success "Linux-specific files created"
}

# Function to create distribution
create_distribution() {
    local exclude_file="$1"
    
    print_status "Creating Linux distribution..."
    
    # Remove old archive if exists
    if [ -f "$OUTPUT_FILE" ]; then
        rm "$OUTPUT_FILE"
    fi
    
    # Create the archive
    print_status "Creating archive: $OUTPUT_FILE"
    
    # Use tar with gzip compression
    tar --exclude-from="$exclude_file" \
        --exclude="*.tar.gz" \
        --exclude="*.tar.bz2" \
        --exclude="*.zip" \
        --exclude="*.rar" \
        --exclude="*.7z" \
        -czf "$OUTPUT_FILE" .
    
    if [ $? -eq 0 ]; then
        print_success "Distribution created successfully!"
        
        # Show archive info
        local size=$(du -h "$OUTPUT_FILE" | cut -f1)
        print_status "Archive size: $size"
        print_status "Archive location: $(pwd)/$OUTPUT_FILE"
    else
        print_error "Failed to create distribution"
        exit 1
    fi
}

# Function to create additional formats
create_additional_formats() {
    print_status "Creating additional distribution formats..."
    
    # Create .tar.bz2 version (smaller)
    local bz2_file="${DIST_NAME}.tar.bz2"
    if command_exists bzip2; then
        print_status "Creating .tar.bz2 version..."
        tar --exclude-from="zwaifu_exclude_linux.txt" \
            --exclude="*.tar.gz" \
            --exclude="*.tar.bz2" \
            --exclude="*.zip" \
            --exclude="*.rar" \
            --exclude="*.7z" \
            -cjf "$bz2_file" .
        
        if [ $? -eq 0 ]; then
            local bz2_size=$(du -h "$bz2_file" | cut -f1)
            print_success "Created $bz2_file ($bz2_size)"
        fi
    fi
    
    # Create .zip version
    local zip_file="${DIST_NAME}.zip"
    if command_exists zip; then
        print_status "Creating .zip version..."
        zip -r "$zip_file" . -x@"zwaifu_exclude_linux.txt" \
            -x "*.tar.gz" -x "*.tar.bz2" -x "*.zip" -x "*.rar" -x "*.7z"
        
        if [ $? -eq 0 ]; then
            local zip_size=$(du -h "$zip_file" | cut -f1)
            print_success "Created $zip_file ($zip_size)"
        fi
    fi
}

# Function to create checksums
create_checksums() {
    print_status "Creating checksums..."
    
    for file in "${DIST_NAME}".*; do
        if [ -f "$file" ]; then
            if command_exists sha256sum; then
                sha256sum "$file" > "${file}.sha256"
                print_status "Created ${file}.sha256"
            fi
            if command_exists md5sum; then
                md5sum "$file" > "${file}.md5"
                print_status "Created ${file}.md5"
            fi
        fi
    done
}

# Function to show distribution contents
show_distribution_info() {
    print_status "Distribution contents:"
    echo
    echo "Core files:"
    echo "  - zwaifu_launcher_gui.py (Main launcher)"
    echo "  - launch_launcher.py (Python launcher)"
    echo "  - launch_launcher.sh (Linux shell launcher)"
    echo "  - install_linux.sh (Linux installer)"
    echo "  - run.sh (Simple launcher)"
    echo
    echo "Directories:"
    echo "  - utils/ (Utility modules)"
    echo "  - config/ (Configuration files)"
    echo "  - docs/ (Documentation)"
    echo "  - scripts/ (Scripts and tools)"
    echo "  - plugins/ (Plugin system)"
    echo "  - static/ (Web interface assets)"
    echo "  - templates/ (Web templates)"
    echo "  - ai_tools/ (AI tools configuration)"
    echo "  - data/ (Data files)"
    echo
    echo "Linux-specific:"
    echo "  - launch_launcher.sh (Main Linux launcher)"
    echo "  - run.sh (Simple launcher)"
    echo "  - install_linux.sh (Linux installer)"
    echo "  - zwaifu-launcher.desktop (Desktop entry)"
    echo "  - test_linux_compatibility.py (Compatibility test)"
    echo "  - README_LINUX.md (Linux documentation)"
    echo "  - LINUX_SETUP.md (Setup guide)"
    echo
}

# Main function
main() {
    echo "Z-Waifu Launcher Linux Distribution Creator"
    echo "==========================================="
    echo
    
    # Check if we're in the project directory
    if [ ! -f "zwaifu_launcher_gui.py" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Change to project root
    cd "$PROJECT_ROOT"
    print_status "Working directory: $(pwd)"
    
    # Create exclude list
    local exclude_file=$(create_exclude_list)
    
    # Create Linux-specific files
    create_linux_files
    
    # Create distribution
    create_distribution "$exclude_file"
    
    # Create additional formats
    create_additional_formats
    
    # Create checksums
    create_checksums
    
    # Clean up exclude file
    rm -f "$exclude_file"
    
    # Show distribution info
    show_distribution_info
    
    print_success "Linux distribution creation completed!"
    echo
    echo "Created files:"
    ls -la "${DIST_NAME}".*
    echo
    echo "To install on a Linux system:"
    echo "1. Extract the archive: tar -xzf $OUTPUT_FILE"
    echo "2. Run the installer: ./install_linux.sh"
    echo "3. Or run directly: ./run.sh"
    echo
}

# Run main function
main "$@" 
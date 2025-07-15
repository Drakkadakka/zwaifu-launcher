#!/bin/bash

# Z-Waifu Launcher Linux Installation Script
# =========================================

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif command_exists lsb_release; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

# Function to install system dependencies
install_system_deps() {
    local distro=$(detect_distro)
    print_status "Detected distribution: $distro"
    
    case $distro in
        ubuntu|debian|linuxmint)
            print_status "Installing dependencies for Ubuntu/Debian..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv python3-tk xdg-utils curl wget
            ;;
        centos|rhel|fedora)
            print_status "Installing dependencies for CentOS/RHEL/Fedora..."
            if command_exists dnf; then
                sudo dnf install -y python3 python3-pip python3-tkinter xdg-utils curl wget
            else
                sudo yum install -y python3 python3-pip tkinter xdg-utils curl wget
            fi
            ;;
        arch|manjaro)
            print_status "Installing dependencies for Arch Linux..."
            sudo pacman -S --noconfirm python python-pip tk xdg-utils curl wget
            ;;
        *)
            print_warning "Unknown distribution. Please install dependencies manually:"
            echo "  - Python 3.7+"
            echo "  - python3-pip"
            echo "  - python3-tkinter"
            echo "  - xdg-utils"
            echo "  - curl"
            echo "  - wget"
            ;;
    esac
}

# Function to create installation directory
create_install_dir() {
    local install_dir="/opt/zwaifu-launcher"
    print_status "Creating installation directory: $install_dir"
    
    sudo mkdir -p "$install_dir"
    sudo chown $USER:$USER "$install_dir"
    
    # Copy files to installation directory
    print_status "Copying files to installation directory..."
    cp -r * "$install_dir/"
    
    # Make scripts executable
    chmod +x "$install_dir/launch_launcher.sh"
    chmod +x "$install_dir/launch_launcher.py"
    
    print_success "Files copied to $install_dir"
}

# Function to install desktop entry
install_desktop_entry() {
    local desktop_file="$HOME/.local/share/applications/zwaifu-launcher.desktop"
    local install_dir="/opt/zwaifu-launcher"
    
    print_status "Installing desktop entry..."
    
    # Create applications directory if it doesn't exist
    mkdir -p "$HOME/.local/share/applications"
    
    # Create desktop entry
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Z-Waifu Launcher
Comment=AI Waifu Launcher with Oobabooga and Z-Waifu Integration
Exec=$install_dir/launch_launcher.sh
Icon=$install_dir/static/images/launcher_icon.png
Terminal=true
Categories=Utility;Development;AI;
Keywords=AI;Waifu;Launcher;Oobabooga;Z-Waifu;
StartupWMClass=Z-Waifu-Launcher
EOF
    
    # Make desktop entry executable
    chmod +x "$desktop_file"
    
    # Update desktop database
    if command_exists update-desktop-database; then
        update-desktop-database "$HOME/.local/share/applications"
    fi
    
    print_success "Desktop entry installed at $desktop_file"
}

# Function to create systemd service (optional)
create_systemd_service() {
    local service_file="/etc/systemd/system/zwaifu-launcher.service"
    local install_dir="/opt/zwaifu-launcher"
    
    print_status "Creating systemd service (optional)..."
    
    sudo tee "$service_file" > /dev/null << EOF
[Unit]
Description=Z-Waifu Launcher
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$install_dir
ExecStart=$install_dir/launch_launcher.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable zwaifu-launcher.service
    
    print_success "Systemd service created and enabled"
    print_status "To start the service: sudo systemctl start zwaifu-launcher"
    print_status "To stop the service: sudo systemctl stop zwaifu-launcher"
}

# Function to create symlinks
create_symlinks() {
    local install_dir="/opt/zwaifu-launcher"
    
    print_status "Creating symlinks..."
    
    # Create symlink in /usr/local/bin
    sudo ln -sf "$install_dir/launch_launcher.sh" /usr/local/bin/zwaifu-launcher
    
    print_success "Symlink created: /usr/local/bin/zwaifu-launcher"
}

# Function to set up virtual environment
setup_virtual_env() {
    local install_dir="/opt/zwaifu-launcher"
    
    print_status "Setting up virtual environment..."
    
    cd "$install_dir"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    
    if [ -f "config/requirements.txt" ]; then
        pip install -r config/requirements.txt
    fi
    
    print_success "Virtual environment set up successfully"
}

# Function to create uninstall script
create_uninstall_script() {
    local install_dir="/opt/zwaifu-launcher"
    
    print_status "Creating uninstall script..."
    
    cat > "$install_dir/uninstall.sh" << 'EOF'
#!/bin/bash

# Z-Waifu Launcher Uninstall Script
# =================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Remove desktop entry
if [ -f "$HOME/.local/share/applications/zwaifu-launcher.desktop" ]; then
    print_status "Removing desktop entry..."
    rm "$HOME/.local/share/applications/zwaifu-launcher.desktop"
    print_success "Desktop entry removed"
fi

# Remove symlink
if [ -L "/usr/local/bin/zwaifu-launcher" ]; then
    print_status "Removing symlink..."
    sudo rm /usr/local/bin/zwaifu-launcher
    print_success "Symlink removed"
fi

# Remove systemd service
if [ -f "/etc/systemd/system/zwaifu-launcher.service" ]; then
    print_status "Removing systemd service..."
    sudo systemctl stop zwaifu-launcher.service 2>/dev/null || true
    sudo systemctl disable zwaifu-launcher.service 2>/dev/null || true
    sudo rm /etc/systemd/system/zwaifu-launcher.service
    sudo systemctl daemon-reload
    print_success "Systemd service removed"
fi

# Remove installation directory
if [ -d "/opt/zwaifu-launcher" ]; then
    print_status "Removing installation directory..."
    sudo rm -rf /opt/zwaifu-launcher
    print_success "Installation directory removed"
fi

print_success "Z-Waifu Launcher has been completely uninstalled"
EOF
    
    chmod +x "$install_dir/uninstall.sh"
    print_success "Uninstall script created at $install_dir/uninstall.sh"
}

# Main installation function
main() {
    echo "Z-Waifu Launcher Linux Installation"
    echo "==================================="
    echo
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Check if we're in the project directory
    if [ ! -f "zwaifu_launcher_gui.py" ]; then
        print_error "Please run this script from the Z-Waifu project directory"
        exit 1
    fi
    
    # Check for sudo access
    if ! sudo -n true 2>/dev/null; then
        print_status "This script requires sudo access. Please enter your password when prompted."
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Create installation directory and copy files
    create_install_dir
    
    # Set up virtual environment
    setup_virtual_env
    
    # Create symlinks
    create_symlinks
    
    # Install desktop entry
    install_desktop_entry
    
    # Create systemd service (optional)
    read -p "Do you want to create a systemd service for auto-start? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_systemd_service
    fi
    
    # Create uninstall script
    create_uninstall_script
    
    echo
    print_success "Installation completed successfully!"
    echo
    echo "You can now launch Z-Waifu Launcher using:"
    echo "  - Desktop application menu"
    echo "  - Command: zwaifu-launcher"
    echo "  - Command: /opt/zwaifu-launcher/launch_launcher.sh"
    echo
    echo "To uninstall, run: /opt/zwaifu-launcher/uninstall.sh"
    echo
}

# Run main function
main "$@" 
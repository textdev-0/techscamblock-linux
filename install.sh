#!/bin/bash

# TechScamBlock Installer

# --- Configuration ---
INSTALL_DIR="/opt/techscamblock"
CONFIG_DIR="/etc/techscamblock"
BIN_DIR="/usr/bin"
SERVICE_DIR="/lib/systemd/system"
DESKTOP_DIR="/usr/share/applications"
ICON_NAME="tray.png"
APP_NAME="techscamblock"
SERVICE_NAME="killdaemon.service"
DESKTOP_FILE="techscamblock.desktop"

# --- Functions ---
function check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "This script must be run as root. Please use sudo."
        exit 1
    fi
}

function install_dependencies() {
    echo "Checking for dependencies..."
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        apt-get update
        apt-get install -y python3 python3-pip
    elif command -v dnf &> /dev/null; then
        # Fedora/CentOS
        dnf install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        pacman -Syu --noconfirm python python-pip
    else
        echo "Unsupported package manager. Please install Python 3 and pip manually."
        exit 1
    fi
    pip3 install -r requirements.txt
}

function create_directories() {
    echo "Creating directories..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
}

function copy_files() {
    echo "Copying application files..."
    cp techscamblock.py "$INSTALL_DIR/"
    cp killdaemon.py "$INSTALL_DIR/"
    cp tray.py "$INSTALL_DIR/"
    cp aboutremoteblock.py "$INSTALL_DIR/"
    cp "$ICON_NAME" "$INSTALL_DIR/"
}

function setup_service() {
    echo "Setting up systemd service..."
    # Update paths in the service file
    sed -i "s|/opt/techscamblock/killdaemon.py|$INSTALL_DIR/killdaemon.py|g" "$SERVICE_NAME"
    cp "$SERVICE_NAME" "$SERVICE_DIR/"
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
}

function create_launcher() {
    echo "Creating application launcher..."
    cat <<EOF > "${BIN_DIR}/${APP_NAME}"
#!/bin/bash
/usr/bin/python3 ${INSTALL_DIR}/techscamblock.py
EOF
    chmod +x "${BIN_DIR}/${APP_NAME}"
}

function create_desktop_entry() {
    echo "Creating desktop entry..."
    # Update paths in the desktop file
    sed -i "s|/opt/techscamblock/tray.png|$INSTALL_DIR/$ICON_NAME|g" "$DESKTOP_FILE"
    sed -i "s|/usr/bin/techscamblock|$BIN_DIR/$APP_NAME|g" "$DESKTOP_FILE"
    cp "$DESKTOP_FILE" "$DESKTOP_DIR/"
}

# --- Main ---
check_root
install_dependencies
create_directories
copy_files
setup_service
create_launcher
create_desktop_entry

echo "TechScamBlock has been successfully installed."
echo "The service is running, and the application will start on login."

#!/bin/bash

# TechScamBlock Uninstaller

# --- Configuration ---
INSTALL_DIR="/opt/techscamblock"
CONFIG_DIR="/etc/techscamblock"
BIN_DIR="/usr/bin"
SERVICE_DIR="/lib/systemd/system"
DESKTOP_DIR="/usr/share/applications"
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

function stop_service() {
    echo "Stopping and disabling systemd service..."
    systemctl stop "$SERVICE_NAME"
    systemctl disable "$SERVICE_NAME"
}

function remove_files() {
    echo "Removing application files..."
    rm -rf "$INSTALL_DIR"
    rm -f "${BIN_DIR}/${APP_NAME}"
    rm -f "${SERVICE_DIR}/${SERVICE_NAME}"
    rm -f "${DESKTOP_DIR}/${DESKTOP_FILE}"
}

function remove_config() {
    echo "Removing configuration directory..."
    rm -rf "$CONFIG_DIR"
}

# --- Main ---
check_root
stop_service
remove_files
remove_config

systemctl daemon-reload

echo "TechScamBlock has been successfully uninstalled."

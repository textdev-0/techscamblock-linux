#!/bin/bash

# 1. Setup
set -e
PACKAGE_NAME="techscamblock"
VERSION="1.0.0"
ARCH="amd64"
BUILD_DIR="${PACKAGE_NAME}-build"

# Clean up previous builds
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# 2. Create Package Structure
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/opt/${PACKAGE_NAME}"
mkdir -p "${BUILD_DIR}/lib/systemd/system"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/etc/${PACKAGE_NAME}"

# 3. Create Control File
cat <<EOF > "${BUILD_DIR}/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Architecture: ${ARCH}
Maintainer: Your Name <you@example.com>
Description: Blocks remote access tools used by scammers.
Depends: python3, python3-pyqt5, python3-psutil, python3-plyer
EOF

# 4. Create Executable Wrapper
cat <<EOF > "${BUILD_DIR}/usr/bin/${PACKAGE_NAME}"
#!/bin/bash
/usr/bin/python3 /opt/${PACKAGE_NAME}/techscamblock.py
EOF
chmod +x "${BUILD_DIR}/usr/bin/${PACKAGE_NAME}"

# 5. Copy Application Files
cp techscamblock.py "${BUILD_DIR}/opt/${PACKAGE_NAME}/"
cp killdaemon.py "${BUILD_DIR}/opt/${PACKAGE_NAME}/"
cp tray.py "${BUILD_DIR}/opt/${PACKAGE_NAME}/"
cp aboutremoteblock.py "${BUILD_DIR}/opt/${PACKAGE_NAME}/"
cp tray.png "${BUILD_DIR}/opt/${PACKAGE_NAME}/"

# 6. Copy System Files
cp killdaemon.service "${BUILD_DIR}/lib/systemd/system/"
cp techscamblock.desktop "${BUILD_DIR}/usr/share/applications/"

# 7. Build the Package
dpkg-deb --build "${BUILD_DIR}"
echo "Successfully created ${BUILD_DIR}.deb"

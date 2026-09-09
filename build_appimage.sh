#!/bin/bash
# Build AppImage for IV League Desktop using PyInstaller
set -e

APP_NAME="IVLeague"
APP_DIR="AppDir"
VERSION="1.0.0"

echo "Building IV League Desktop v${VERSION} AppImage..."

# Clean previous build
rm -rf ${APP_DIR} *.AppImage dist build *.spec

# Build single binary with PyInstaller
echo "Running PyInstaller..."
pyinstaller \
    --onefile \
    --windowed \
    --name IVLeague \
    --add-data "iv_league/assets:iv_league/assets" \
    --add-data "iv_league/database:iv_league/database" \
    --clean \
    main.py

# Create AppDir structure
mkdir -p ${APP_DIR}/usr/bin
mkdir -p ${APP_DIR}/usr/share/applications
mkdir -p ${APP_DIR}/usr/share/icons/hicolor/256x256/apps

# Copy PyInstaller binary
cp dist/IVLeague ${APP_DIR}/usr/bin/iv-league
chmod +x ${APP_DIR}/usr/bin/iv-league

# Create desktop file
cat > ${APP_DIR}/iv-league.desktop << EOF
[Desktop Entry]
Name=IV League
Comment=IV Therapy Tracking and Invoicing
Exec=iv-league
Icon=iv-league
Terminal=false
Type=Application
Categories=Utility;
EOF

# Copy icon
cp iv_league/assets/icon.svg ${APP_DIR}/usr/share/icons/hicolor/256x256/apps/iv-league.svg
cp iv_league/assets/icon.svg ${APP_DIR}/iv-league.svg

# Create AppRun entry point
ln -sf usr/bin/iv-league ${APP_DIR}/AppRun

# Download appimagetools if not present
if [ ! -f appimagetool-x86_64.AppImage ]; then
    echo "Downloading appimagetools..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "Creating AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage ${APP_DIR} ${APP_NAME}-v${VERSION}-x86_64.AppImage

echo "Done! Created ${APP_NAME}-v${VERSION}-x86_64.AppImage"

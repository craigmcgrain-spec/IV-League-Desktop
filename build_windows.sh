#!/bin/bash
# Build Windows .exe installer for IV League Desktop
# Run this on Windows with Python and PyInstaller installed
set -e

APP_NAME="IVLeague"
VERSION="1.0.0"

echo "Building IV League Desktop v${VERSION} Windows installer..."

# Install dependencies
pip install pyinstaller PyQt6 reportlab

# Build executable
pyinstaller \
    --onefile \
    --windowed \
    --name ${APP_NAME} \
    --icon iv_league/assets/icon.ico \
    --add-data "iv_league/assets;iv_league/assets" \
    --add-data "iv_league/database;iv_league/database" \
    main.py

echo "Done! Created dist/${APP_NAME}.exe"
echo ""
echo "To create an installer, use Inno Setup or NSIS with the generated .exe"

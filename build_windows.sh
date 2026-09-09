#!/bin/bash
# Build Windows .exe for IV League Desktop
# Run this on Windows with Python 3.10+ installed
set -e

APP_NAME="IVLeague"
VERSION="1.0.0"

echo "Building IV League Desktop v${VERSION} Windows installer..."
echo ""

# Check Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found."
    echo "Install Python 3.10+ from https://python.org"
    echo "Make sure to check 'Add Python to PATH' during installation."
    exit 1
fi

PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "[1/3] Installing dependencies..."
${PYTHON_CMD} -m pip install pyinstaller PyQt6 reportlab

echo ""
echo "[2/3] Building executable..."
${PYTHON_CMD} -m PyInstaller \
    --onefile \
    --windowed \
    --name ${APP_NAME} \
    --icon iv_league/assets/icon.ico \
    --add-data "iv_league/assets;iv_league/assets" \
    --add-data "iv_league/database;iv_league/database" \
    --clean \
    main.py

echo ""
echo "[3/3] Build complete!"
echo ""
echo "============================================"
echo "  Output: dist/${APP_NAME}.exe"
echo "============================================"
echo ""
echo "To create an installer:"
echo "  1. Download Inno Setup from https://jrsoftware.org/isinfo.php"
echo "  2. Open installer/iv-league-setup.iss"
echo "  3. Click Build > Compile"
echo ""
echo "Or distribute dist/${APP_NAME}.exe directly (no installer needed)."

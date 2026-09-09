#!/bin/bash
# Build AppImage for IV League Desktop
set -e

APP_NAME="IVLeague"
APP_DIR="AppDir"
VERSION="1.0.0"

echo "Building IV League Desktop v${VERSION} AppImage..."

# Clean previous build
rm -rf ${APP_DIR} *.AppImage

# Create AppDir structure
mkdir -p ${APP_DIR}/usr/bin
mkdir -p ${APP_DIR}/usr/share/applications
mkdir -p ${APP_DIR}/usr/share/icons/hicolor/256x256/apps

# Install Python dependencies
pip install --target=${APP_DIR}/usr/lib/python3/site-packages PyQt6 reportlab

# Copy application files
cp -r iv_league ${APP_DIR}/usr/lib/python3/site-packages/
cp main.py ${APP_DIR}/usr/bin/iv-league

# Create wrapper script
cat > ${APP_DIR}/usr/bin/iv-league << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${DIR}/../lib/python3/site-packages:${PYTHONPATH}"
python3 "${DIR}/../lib/python3/site-packages/main.py" "$@"
EOF
chmod +x ${APP_DIR}/usr/bin/iv-league

# Create desktop file
cat > ${APP_DIR}/usr/share/applications/iv-league.desktop << EOF
[Desktop Entry]
Name=IV League
Comment=IV Therapy Tracking and Invoicing
Exec=iv-league
Icon=iv-league
Terminal=false
Type=Application
Categories=Medical;Utility;
Version=${VERSION}
EOF

# Copy icon
cp iv_league/assets/icon.svg ${APP_DIR}/usr/share/icons/hicolor/256x256/apps/iv-league.svg
cp iv_league/assets/icon.svg ${APP_DIR}/iv-league.svg

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

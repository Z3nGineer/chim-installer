#!/usr/bin/env bash
# Build CHIM Installer (Linux, --onedir)
# Usage: ./build.sh
# Output: dist/CHIM_Installer/  (directory with exe + patches/)

set -euo pipefail
cd "$(dirname "$0")"

echo "=== CHIM Installer — PyInstaller Build ==="

# Sanity checks
if ! command -v pyinstaller &>/dev/null; then
    echo "ERROR: pyinstaller not found. Install with: pip install pyinstaller"
    exit 1
fi

if [ ! -d patches ]; then
    echo "ERROR: patches/ directory not found in project root."
    exit 1
fi

if [ ! -f 7zzs ]; then
    echo "WARNING: 7zzs not found — bundled 7z extraction will be unavailable."
fi

# Clean previous build
rm -rf build/CHIM_Installer dist/CHIM_Installer

echo "Building with --onedir (patches/ is ~370MB, --onefile would be impractical)..."

pyinstaller \
    --noconfirm \
    --onedir \
    --name CHIM_Installer \
    --add-data "patches:patches" \
    --add-data "deck_engine.ini:." \
    --add-data "deck_gameusersettings.ini:." \
    --add-data "7zzs:." \
    --windowed \
    chim_installer.py

echo ""
echo "=== Build complete ==="
echo "Output: dist/CHIM_Installer/"
echo ""
echo "To create a distributable tarball:"
echo "  cd dist && tar czf CHIM_Installer_Linux.tar.gz CHIM_Installer/"

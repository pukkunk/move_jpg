#!/bin/bash

# Create virtual environment if it does not exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Remove dist directory if it exists
if [ -d "dist" ]; then
    rm -rf dist
fi

# Remove build directory if it exists
if [ -d "build" ]; then
    rm -rf build
fi

# Remove .spec files if they exist
if ls *.spec 1> /dev/null 2>&1; then
    rm -f *.spec
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip to the latest version
python3 -m pip install --upgrade pip

# Install required packages
pip install ini_cfg_parser
pip install pyinstaller
pip install Pillow
pip install piexif
pip install pillow_heif
pip install numpy
pip install ffmpeg-python

# Build with PyInstaller
pyinstaller move_jpg.py --onefile \
    --hidden-import=PIL._imaging \
    --hidden-import=PIL.Image \
    --hidden-import=PIL.ExifTags \
    --hidden-import=piexif \
    --hidden-import=ffmpeg \
    --hidden-import=ffmpeg._run \
    --hidden-import=ffmpeg._probe

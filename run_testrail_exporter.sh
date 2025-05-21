#!/bin/bash

# Get the source and target directories
SOURCE_DIR="/opt/homebrew/opt/tcl-tk@8/lib"
TARGET_DIR="/opt/homebrew/opt/tcl-tk/lib"

# Check if the target directory exists; if not, create it
if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# Check if the symbolic links exist; if not, create them
if [ ! -e "$TARGET_DIR/libtcl8.6.dylib" ]; then
    echo "Creating symbolic link for libtcl8.6.dylib"
    ln -sf "$SOURCE_DIR/libtcl8.6.dylib" "$TARGET_DIR/libtcl8.6.dylib"
fi

if [ ! -e "$TARGET_DIR/libtk8.6.dylib" ]; then
    echo "Creating symbolic link for libtk8.6.dylib"
    ln -sf "$SOURCE_DIR/libtk8.6.dylib" "$TARGET_DIR/libtk8.6.dylib"
fi

# Set environment variables to use tcl-tk@8
export TCLLIBPATH="$SOURCE_DIR"
export DYLD_LIBRARY_PATH="$SOURCE_DIR:$DYLD_LIBRARY_PATH"
export DYLD_FRAMEWORK_PATH="$SOURCE_DIR:$DYLD_FRAMEWORK_PATH"

# Run the application
cd "$(dirname "$0")"
python testrail_exporter/main.py
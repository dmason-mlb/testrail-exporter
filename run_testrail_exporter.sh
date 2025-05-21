#!/bin/bash

# Set environment variables to use tcl-tk@8
export TCLLIBPATH="/opt/homebrew/opt/tcl-tk@8/lib"
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/tcl-tk@8/lib:$DYLD_LIBRARY_PATH"
export DYLD_FRAMEWORK_PATH="/opt/homebrew/opt/tcl-tk@8/lib:$DYLD_FRAMEWORK_PATH"

# Run the application
cd "$(dirname "$0")"
python testrail_exporter/main.py
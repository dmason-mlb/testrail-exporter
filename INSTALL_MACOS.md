# macOS Installation Guide for TestRail Exporter

This guide will help you properly install TestRail Exporter on macOS, especially when using pyenv or Homebrew Python installations.

## Prerequisites

TestRail Exporter requires:
- Python 3.6 or higher
- Tkinter (Python's GUI toolkit)
- Tcl/Tk 8.6.x (required by Tkinter)

## Tcl/Tk Compatibility

Python 3.12 is designed to work with Tcl/Tk 8.6.x, but macOS Homebrew now installs Tcl/Tk 9.0 by default. This causes compatibility issues with Tkinter applications.

### Option 1: Install Tcl/Tk 8.6 alongside Tcl/Tk 9.0

```bash
# Install Tcl/Tk 8.6
brew install tcl-tk@8
```

After installing, you can use the provided run script which sets the necessary environment variables:

```bash
# Run the application using the provided script
./run_testrail_exporter.sh
```

The run script sets the required environment variables to use Tcl/Tk 8.6 instead of 9.0.

If you want to set these variables manually:

```bash
# Set environment variables to use Tcl/Tk 8.6
export TCLLIBPATH="/opt/homebrew/opt/tcl-tk@8/lib"
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/tcl-tk@8/lib:$DYLD_LIBRARY_PATH"
export DYLD_FRAMEWORK_PATH="/opt/homebrew/opt/tcl-tk@8/lib:$DYLD_FRAMEWORK_PATH"

# Run the application
python testrail_exporter/main.py
```

### Option 2: Reinstall Python with Tcl/Tk 8.6

If you're using pyenv, you need to set environment variables before installing Python:

```bash
# Install tcl-tk 8
brew install tcl-tk@8

# Get the installation path
TCL_TK_PATH=$(brew --prefix tcl-tk@8)

# Set environment variables for pyenv to use tcl-tk 8.6
export PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$TCL_TK_PATH/include' --with-tcltk-libs='-L$TCL_TK_PATH/lib -ltcl8.6 -ltk8.6'"

# Install Python 3.12 with tcl-tk 8.6 support
pyenv install 3.12.x
```

### Option 3: Create a virtualenv with system's Tcl/Tk

```bash
# Create a virtualenv with system site packages
python -m venv --system-site-packages venv

# Activate the virtualenv
source venv/bin/activate

# Install TestRail Exporter in development mode
pip install -e .
```

## Running the Application

After proper installation, you can run the application using any of these methods:

```bash
# Method 1: Use the provided run script (recommended on macOS)
./run_testrail_exporter.sh

# Method 2: Direct execution (after setting environment variables)
python testrail_exporter/main.py

# Method 3: Using the entry point (if installed with pip)
testrail-exporter
```

## Troubleshooting

### Tkinter Import Error

If you see an error like:

```
ImportError: dlopen(.../_tkinter.cpython-312-darwin.so, 0x0002): Library not loaded: /opt/homebrew/opt/tcl-tk/lib/libtk8.6.dylib
```

This indicates that Python is looking for Tcl/Tk 8.6 libraries but can't find them. Follow Option 1 or Option 2 above to resolve this issue.

### Checking Your Tcl/Tk Version

You can check which Tcl/Tk version Python is using with:

```bash
python -m tkinter
```

This will open a small window showing the Tcl/Tk version. For Python 3.12, it should be using version 8.6.x.

## Note on Python 3.12 and Tcl/Tk 9.0

Python 3.12 was developed to work with Tcl/Tk 8.6.x. Full support for Tcl/Tk 9.0 is expected in Python 3.14, but is not officially available in Python 3.12 or 3.13. While Tcl/Tk 9.0 offers many improvements, Python applications should continue using Tcl/Tk 8.6.x for stability and compatibility with Python 3.12.
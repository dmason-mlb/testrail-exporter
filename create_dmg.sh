#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# create_dmg.sh
#
# Build script for TestRail Exporter macOS distribution
# -----------------------------------------------------------------------------
# This script will:
#   1. Generate a macOS .icns icon from a source PNG
#   2. Bundle the Python application into a standalone .app using PyInstaller
#   3. Package the .app bundle into a compressed DMG using create-dmg tool
#
# Prerequisites (install once):
#   brew install python  # if Python 3 is not installed
#   pip install pyinstaller
#   brew install create-dmg
#   brew install imagemagick  # for image conversion if needed
#   # "sips" and "iconutil" are shipped with macOS
#
# Usage:
#   ./create_dmg.sh [/full/path/to/source_icon.png]
#
# If no argument is supplied, the script falls back to the default location
# used during development.
# -----------------------------------------------------------------------------

set -euo pipefail

# ----------------------------- CONFIGURATION ---------------------------------
# Optionally load local environment variables (e.g., Developer ID) from an
# untracked file. Add the file name (e.g., .env) to .gitignore so it is not
# committed to version control.
ENV_FILE=".dmg_env"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

APP_NAME="TestRail Exporter"

# Extract version from setup.py
CURRENT_VERSION=$(python3 -c "
import re
with open('setup.py', 'r') as f:
    content = f.read()
    match = re.search(r'version=[\"\'](.*?)[\"\']', content)
    if match:
        print(match.group(1))
    else:
        print('1.0.0')  # fallback version
")

echo "Current version: $CURRENT_VERSION"

# Auto-increment the last digit of the version
NEW_VERSION=$(python3 -c "
version = '$CURRENT_VERSION'
parts = version.split('.')
if len(parts) >= 3:
    # Increment the patch version (last digit)
    parts[-1] = str(int(parts[-1]) + 1)
else:
    # If version format is unexpected, append .1
    parts.append('1')
print('.'.join(parts))
")

echo "New version: $NEW_VERSION"

# Update setup.py with the new version
python3 -c "
import re
with open('setup.py', 'r') as f:
    content = f.read()

# Replace the version string
new_content = re.sub(r'version=[\"\'](.*?)[\"\']', f'version=\"$NEW_VERSION\"', content)

with open('setup.py', 'w') as f:
    f.write(new_content)
"

echo "Updated setup.py with version $NEW_VERSION"

# Use the new version for the DMG
VERSION=$NEW_VERSION

# Final DMG name includes the version
DMG_NAME="testrail_exporter-${VERSION}.dmg"

# Allow the user to override the icon source via CLI argument
ICON_SRC_DEFAULT="testrail_exporter/icon.png"
ICON_SRC="${1:-$ICON_SRC_DEFAULT}"

BUILD_DIR="build"
ICONSET_DIR="$BUILD_DIR/icon.iconset"
ICNS_FILE="$BUILD_DIR/icon.icns"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/${APP_NAME}.app"
PYTHON_ENTRY="testrail_exporter/main.py"

# DMG Customization Settings
DMG_BACKGROUND_IMG="docs/images/dmg_background.png"

# ------------------------------- FUNCTIONS -----------------------------------
function check_deps() {
  command -v pyinstaller >/dev/null 2>&1 || {
    echo >&2 "PyInstaller is required but not installed. Install with: pip install pyinstaller";
    exit 1;
  }
  command -v create-dmg >/dev/null 2>&1 || {
    echo >&2 "create-dmg is required but not installed. Install with: brew install create-dmg";
    exit 1;
  }
  for cmd in sips iconutil; do
    command -v "$cmd" >/dev/null 2>&1 || {
      echo >&2 "macOS utility '$cmd' is required but was not found.";
      exit 1;
    }
  done

  # -----------------------------------------------------------------
  # Workaround: The legacy "typing" back-port package conflicts with
  # PyInstaller on Python ≥3.8 because the typing module is built-in.
  # If it exists in the current environment, uninstall it silently.
  # -----------------------------------------------------------------
  if python3 -m pip show typing >/dev/null 2>&1; then
    echo "Detected obsolete \"typing\" package — removing to avoid PyInstaller crash …"
    python3 -m pip uninstall -y typing >/dev/null 2>&1 || true
  fi
}

function generate_icns() {
  echo "[1/4] Generating .icns icon from $ICON_SRC ..."
  if [[ ! -f "$ICON_SRC" ]]; then
    echo "Source icon not found at $ICON_SRC"
    exit 1
  fi

  # Clean previous build artifacts
  rm -rf "$BUILD_DIR"
  mkdir -p "$BUILD_DIR"

  # Check if we should use the new Apple-style icon generator
  if [[ -x "./generate_macos_icon.sh" ]]; then
    echo "  Using Apple-style icon generator with rounded corners and 3D effect..."
    ./generate_macos_icon.sh "$ICON_SRC"
    mv icon.icns "$ICNS_FILE"
    rm -f icon_preview.png
  else
    # Fall back to original simple icon generation
    echo "  Using simple icon generation (run ./generate_macos_icon.sh for Apple-style icons)..."
    mkdir -p "$ICONSET_DIR"
    
    declare -a sizes=(16 32 128 256 512)
    for size in "${sizes[@]}"; do
      sips -z "$size" "$size" "$ICON_SRC" --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
      double=$((size*2))
      sips -z "$double" "$double" "$ICON_SRC" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
    done

    # Build the .icns file
    iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"
  fi
  
  echo "Created $ICNS_FILE"

  # Also copy (or update) the PNG used at runtime by the Tkinter UI
  PNG_RUNTIME_PATH="docs/images/icon.png"
  mkdir -p "$(dirname "$PNG_RUNTIME_PATH")"
  cp "$ICON_SRC" "$PNG_RUNTIME_PATH"
  echo "Updated runtime icon at $PNG_RUNTIME_PATH"
}

function build_app() {
  echo "[2/4] Building .app bundle with PyInstaller ..."
  # Remove previous PyInstaller outputs
  rm -rf build/pyinstaller "$DIST_DIR" "${APP_NAME}.spec" # Corrected: remove build/pyinstaller, not all of build

  echo "  DEBUG: Checking icon file to be used by PyInstaller: $ICNS_FILE"
  if [[ ! -f "$ICNS_FILE" ]]; then
    echo "  FATAL ERROR: Icon file '$ICNS_FILE' not found for PyInstaller."
    exit 1
  fi
  echo "  DEBUG: Icon file '$ICNS_FILE' exists."
  echo "  DEBUG: Size of '$ICNS_FILE' is $(stat -f%z "$ICNS_FILE") bytes."
  echo "  DEBUG: For manual inspection, open '$ICNS_FILE' with Preview now if you pause the script."
  # You can even add a command to open it with Preview if you want to force a check:
  # read -p "  DEBUG: Press [Enter] to continue after inspecting $ICNS_FILE (or Ctrl+C to abort)..."

  pyinstaller \
    --clean \
    --windowed \
    --name "$APP_NAME" \
    --icon "$ICNS_FILE" \
    "$PYTHON_ENTRY"

  if [[ ! -d "$APP_BUNDLE" ]]; then
    echo "PyInstaller failed to create the .app bundle"
    exit 1
  fi
  echo "Created $APP_BUNDLE"

  # Post-build check of the icon inside the .app
  echo "  DEBUG: Checking icon embedded in the .app bundle..."
  APP_ICON_PATH_EXPECTED="$APP_BUNDLE/Contents/Resources/icon-windowed.icns" # Common PyInstaller name
  # PyInstaller might also use the original name, or ' standaard.icns', 'application.icns', check common ones.
  # The Info.plist CFBundleIconFile entry will specify the exact name.
  
  PLIST_ICON_FILE=$(/usr/libexec/PlistBuddy -c "Print CFBundleIconFile" "$APP_BUNDLE/Contents/Info.plist" 2>/dev/null)
  if [[ -n "$PLIST_ICON_FILE" ]]; then
      # If not an absolute path, prepend Resources
      if [[ "$PLIST_ICON_FILE" != /* ]]; then
          PLIST_ICON_FILE="Contents/Resources/$PLIST_ICON_FILE"
      fi
      ACTUAL_APP_ICON_PATH="$APP_BUNDLE/$PLIST_ICON_FILE"
      # Normalize potential .. in path (though unlikely here)
      ACTUAL_APP_ICON_PATH=$(cd "$(dirname "$ACTUAL_APP_ICON_PATH")" && pwd)/$(basename "$ACTUAL_APP_ICON_PATH")


      echo "  DEBUG: Info.plist points to CFBundleIconFile: $PLIST_ICON_FILE"
      if [[ -f "$ACTUAL_APP_ICON_PATH" ]]; then
          echo "  DEBUG: Embedded icon at '$ACTUAL_APP_ICON_PATH' exists."
          echo "  DEBUG: Size of embedded icon is $(stat -f%z "$ACTUAL_APP_ICON_PATH") bytes."
          echo "  DEBUG: Compare this size to the original. If smaller, PyInstaller likely reprocessed it."
      else
          echo "  DEBUG: WARNING - Embedded icon '$ACTUAL_APP_ICON_PATH' (from Info.plist) not found!"
      fi
  else
      echo "  DEBUG: WARNING - CFBundleIconFile not found in Info.plist or PlistBuddy failed."
  fi
}

function sign_app() {
  echo "[3/4] Code-signing the app (if DEVELOPER_ID_APP is provided) ..."

  # Expecting the Developer ID to be provided via environment variable or
  # env-file (see top of script). Example line in .dmg_env:
  #   export DEVELOPER_ID_APP="Developer ID Application: Douglas Mason (3PAP25XR7L)"

  DEVELOPER_ID="${DEVELOPER_ID_APP:-}"

  # Check if a developer ID is set
  if [ -z "$DEVELOPER_ID" ]; then
    echo "  Skipping code signing: No DEVELOPER_ID configured in script."
    return
  fi

  echo "  Signing application with identity: $DEVELOPER_ID"
  # --force: Replaces any existing signature.
  # --deep: Ensures all nested code (frameworks, helpers) is signed.
  # -s: Specifies the certificate common name or fingerprint.
  # --options runtime: Enables hardened runtime, recommended for notarization.
  if codesign --force --deep -s "$DEVELOPER_ID" --options runtime "$APP_BUNDLE"; then
    echo "  App signing successful."
    echo "  Verifying signature..."
    if codesign --verify --deep --strict --verbose=2 "$APP_BUNDLE"; then
      echo "  Signature verification successful."
    else
      echo "  Error: Signature verification failed."
      # Optionally, exit here if verification failure is critical
      # exit 1
    fi
  else
    echo "  Error: App signing failed. Check if DEVELOPER_ID is correct and installed in Keychain."
    # Optionally, exit here if signing failure is critical
    # exit 1
  fi
}

function create_dmg() {
  echo "[4/4] Packaging DMG using create-dmg tool ..."

  # Clean up old DMGs
  rm -f "$BUILD_DIR/$DMG_NAME"

  # Check if background image exists
  if [[ ! -f "$DMG_BACKGROUND_IMG" ]]; then
    echo "Warning: Background image '$DMG_BACKGROUND_IMG' not found. Creating DMG without background."
    DMG_BACKGROUND_ARG=""
  else
    DMG_BACKGROUND_ARG="--background \"$DMG_BACKGROUND_IMG\""
  fi

  # Create DMG using create-dmg tool
  # The tool automatically handles the window size, icon positions, and other settings
  echo "  Creating DMG with create-dmg..."
  
  # Build the create-dmg command
  CREATE_DMG_CMD="create-dmg \
    --volname \"$APP_NAME\" \
    --window-pos 200 120 \
    --window-size 800 533 \
    --icon-size 128 \
    --icon \"${APP_NAME}.app\" 200 267 \
    --hide-extension \"${APP_NAME}.app\" \
    --app-drop-link 600 267"
  
  # Add codesign if developer ID is available
  if [ -n "$DEVELOPER_ID" ]; then
    CREATE_DMG_CMD="$CREATE_DMG_CMD --codesign \"$DEVELOPER_ID\""
  fi
  
  # Add background if available
  if [ -n "$DMG_BACKGROUND_ARG" ]; then
    CREATE_DMG_CMD="$CREATE_DMG_CMD $DMG_BACKGROUND_ARG"
  fi
  
  # Add output file and source
  CREATE_DMG_CMD="$CREATE_DMG_CMD \
    \"$BUILD_DIR/$DMG_NAME\" \
    \"$APP_BUNDLE\""
  
  # Execute the command
  if eval $CREATE_DMG_CMD; then
    echo "Successfully created $BUILD_DIR/$DMG_NAME"
  else
    echo "Error: Failed to create DMG. The create-dmg tool may have encountered an issue."
    echo "Trying alternative method without background..."
    
    # Fallback: Try without background
    FALLBACK_CMD="create-dmg \
      --volname \"$APP_NAME\" \
      --window-pos 200 120 \
      --window-size 800 533 \
      --icon-size 128 \
      --icon \"${APP_NAME}.app\" 200 267 \
      --hide-extension \"${APP_NAME}.app\" \
      --app-drop-link 600 267"
    
    # Add codesign if developer ID is available
    if [ -n "$DEVELOPER_ID" ]; then
      FALLBACK_CMD="$FALLBACK_CMD --codesign \"$DEVELOPER_ID\""
    fi
    
    # Add output and source
    FALLBACK_CMD="$FALLBACK_CMD \"$BUILD_DIR/$DMG_NAME\" \"$APP_BUNDLE\""
    
    # Execute fallback command
    if eval $FALLBACK_CMD; then
      echo "Successfully created $BUILD_DIR/$DMG_NAME (without background)"
    else
      echo "Error: Failed to create DMG even without background. Please check the create-dmg installation."
      exit 1
    fi
  fi
}

# ------------------------------- MAIN ----------------------------------------
check_deps

# Ensure we're running from repo root (directory of this script)
cd "$(dirname "$0")"

generate_icns
build_app
sign_app
create_dmg

echo -e "\nDone! You can now distribute $BUILD_DIR/$DMG_NAME to other macOS users."
#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# create_dmg.sh
#
# Build script for TestRail Exporter macOS distribution (version 1.0)
# -----------------------------------------------------------------------------
# This script will:
#   1. Generate a macOS .icns icon from a source PNG
#   2. Bundle the Python application into a standalone .app using PyInstaller
#   3. Package the .app bundle into a compressed DMG named "testrail_exporter.dmg"
#
# Prerequisites (install once):
#   brew install python  # if Python 3 is not installed
#   pip install pyinstaller
#   # "sips", "iconutil" and "hdiutil" are shipped with macOS
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
VERSION="1.0"
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
DMG_BACKGROUND_IMG_SRC="docs/images/dmg_background.png" # User should create this image (e.g., 600x400 with an arrow)
DMG_WINDOW_WIDTH=600
DMG_WINDOW_HEIGHT=400
DMG_ICON_SIZE=96      # Icon size for items within the DMG
DMG_APP_X_POS=150     # X position for the .app icon
DMG_APP_Y_POS=190     # Y position for the .app icon (adjust for vertical centering)
DMG_APPLICATIONS_LINK_X_POS=450 # X position for Applications link
DMG_APPLICATIONS_LINK_Y_POS=190 # Y position for Applications link

# ------------------------------- FUNCTIONS -----------------------------------
function check_deps() {
  command -v pyinstaller >/dev/null 2>&1 || {
    echo >&2 "PyInstaller is required but not installed. Install with: pip install pyinstaller";
    exit 1;
  }
  for cmd in sips iconutil hdiutil; do
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
  mkdir -p "$ICONSET_DIR"

  declare -a sizes=(16 32 128 256 512)
  for size in "${sizes[@]}"; do
    sips -z "$size" "$size" "$ICON_SRC" --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
    double=$((size*2))
    sips -z "$double" "$double" "$ICON_SRC" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
  done

  # Build the .icns file
  iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"
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
  rm -rf build/pyinstaller "$DIST_DIR" "${APP_NAME}.spec"

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
}

function sign_app() {
  echo "[3/4] Code-signing the app (if DEVELOPER_ID_APP is provided) ..."

  # Expecting the Developer ID to be provided via environment variable or
  # env-file (see top of script). Example line in .dmg_env:
  #   export DEVELOPER_ID_APP="Developer ID Application: Douglas Mason (3PAP25XR7L)"

  DEVELOPER_ID="${DEVELOPER_ID_APP:-}"

  echo "  Signing application with identity: $DEVELOPER_ID"

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
  echo "[4/4] Packaging DMG ..."

  # Temporary DMG name
  TEMP_DMG_RW="$BUILD_DIR/${APP_NAME}_rw.dmg"

  # DMG settings
  DMG_WINDOW_TITLE="$APP_NAME" # Volume name and window title
  DMG_APP_NAME_IN_DMG="${APP_NAME}.app" # Actual name of the .app bundle inside DMG

  # Clean up old DMGs
  rm -f "$DMG_NAME" "$TEMP_DMG_RW"

  # Create a new read/write DMG
  # Increased size just in case, can be tuned. fsargs are common for DMGs.
  echo "  Creating temporary Read/Write DMG..."
  hdiutil create -o "$TEMP_DMG_RW" -size 350m -volname "$DMG_WINDOW_TITLE" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -layout SPUD
  if [ $? -ne 0 ]; then echo "Error: Failed to create temporary DMG. Aborting."; exit 1; fi

  # Mount the DMG
  echo "  Mounting DMG..."
  # Capture all output, then parse. Grep everything starting with /Volumes/ to
  # the end of the line – this supports spaces in volume names.
  MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "$TEMP_DMG_RW")
  # device id is first field (e.g. /dev/disk4)
  DEV_ID=$(echo "$MOUNT_OUTPUT" | head -n 1 | awk '{print $1}')
  MOUNT_PATH=$(echo "$MOUNT_OUTPUT" | grep -oE '/Volumes/.*' | head -n 1)

  if [ -z "$MOUNT_PATH" ] || [ ! -d "$MOUNT_PATH" ]; then
    echo "Error: Failed to mount DMG at '$MOUNT_PATH'. Aborting."
    echo "Attach output: $MOUNT_OUTPUT"
    rm -f "$TEMP_DMG_RW"
    exit 1
  fi
  echo "  Mounted at: $MOUNT_PATH"

  # Ensure APP_BUNDLE (e.g., dist/TestRail Exporter.app) exists
  if [ ! -d "$APP_BUNDLE" ]; then
    echo "Error: App bundle '$APP_BUNDLE' not found. Build the app first."
    hdiutil detach "$DEV_ID" -force >/dev/null 2>&1 || true
    rm -f "$TEMP_DMG_RW"
    exit 1
  fi
  
  echo "  Copying .app bundle to DMG..."
  cp -R "$APP_BUNDLE" "$MOUNT_PATH/"

  echo "  Creating Applications symlink in DMG..."
  ln -s /Applications "$MOUNT_PATH/Applications"

  DMG_BACKGROUND_FILE_NAME_IN_DMG=""
  if [ -f "$DMG_BACKGROUND_IMG_SRC" ]; then
    echo "  Adding background image to DMG..."
    mkdir "$MOUNT_PATH/.background"
    # Get just the filename for AppleScript
    DMG_BACKGROUND_FILE_NAME_IN_DMG=$(basename "$DMG_BACKGROUND_IMG_SRC")
    cp "$DMG_BACKGROUND_IMG_SRC" "$MOUNT_PATH/.background/$DMG_BACKGROUND_FILE_NAME_IN_DMG"
  else
    echo "  Warning: Background image '$DMG_BACKGROUND_IMG_SRC' not found. Skipping background."
  fi

  echo "  Customizing DMG appearance via AppleScript..."
  # Use cat EOF for multiline AppleScript clarity
  APPLESCRIPT_CODE=$(cat <<EOF
    tell application "Finder"
      tell disk "$DMG_WINDOW_TITLE"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 100 + $DMG_WINDOW_WIDTH, 100 + $DMG_WINDOW_HEIGHT}
        set opts to the icon view options of container window
        set arrangement of opts to not arranged
        set icon size of opts to $DMG_ICON_SIZE
EOF
)

  if [ -n "$DMG_BACKGROUND_FILE_NAME_IN_DMG" ]; then
    APPLESCRIPT_CODE="${APPLESCRIPT_CODE}"$'\n'"    set background picture of opts to file \".background:$DMG_BACKGROUND_FILE_NAME_IN_DMG\""
  fi

  APPLESCRIPT_CODE="${APPLESCRIPT_CODE}"$'\n'$(cat <<EOF
        set position of item "$DMG_APP_NAME_IN_DMG" of container window to {$DMG_APP_X_POS, $DMG_APP_Y_POS}
        set position of item "Applications" of container window to {$DMG_APPLICATIONS_LINK_X_POS, $DMG_APPLICATIONS_LINK_Y_POS}
        update without registering applications
        delay 1
        close
      end tell
      -- Window closed; Finder has saved .DS_Store at this point
EOF
)
  
  # echo "AppleScript to be executed:"
  # echo "$APPLESCRIPT_CODE"
  
  if ! osascript -e "$APPLESCRIPT_CODE"; then
     echo "Warning: AppleScript customization failed. The DMG will be functional but basic."
  fi
  
  # Ensure .DS_Store is written by making Finder aware
  # touch "$MOUNT_PATH/.DS_Store" # May not be needed if AppleScript works
  # Set volume icon (optional, if you have one for the mounted volume itself)
  # cp YourVolumeIcon.icns "$MOUNT_PATH/.VolumeIcon.icns"
  # SetFile -a C "$MOUNT_PATH"

  #-------------------------------------------------------------
  # Bless (auto-open) is not supported on Apple Silicon. Because
  # `set -e` is enabled, a failing bless would abort the script
  # before the read-write DMG is converted.  Skip it on arm64 or
  # ignore failures so the build always completes.
  #-------------------------------------------------------------
  if [[ $(uname -m) != "arm64" ]]; then
    echo "  Blessing DMG folder (auto-open on mount)…"
    bless --folder "$MOUNT_PATH" --openfolder "$MOUNT_PATH" || echo "  Warning: bless failed, continuing."
  else
    echo "  Skipping bless step on Apple Silicon (not supported)."
  fi

  # Unmount the DMG
  echo "  Unmounting DMG..."
  COUNT=0
  MAX_RETRIES=5
  DETACH_SUCCESS=false
  while [ $COUNT -lt $MAX_RETRIES ]; do
    if hdiutil detach "$DEV_ID" -force; then
      DETACH_SUCCESS=true
      break
    fi
    echo "  Detach attempt $(($COUNT + 1)) failed. Retrying..."
    sleep 2
    COUNT=$(($COUNT + 1))
  done

  if [ "$DETACH_SUCCESS" = false ]; then
    echo "Error: Failed to detach DMG '$DEV_ID' after $MAX_RETRIES retries. Please detach manually. Continuing to conversion."
    # Proceeding to conversion might fail if still mounted, but worth a try.
  fi
  
  # Convert to compressed read-only DMG
  echo "  Converting to final compressed DMG: $DMG_NAME..."
  hdiutil convert "$TEMP_DMG_RW" -format UDZO -imagekey zlib-level=9 -o "$DMG_NAME"
  if [ $? -ne 0 ]; then echo "Error: Failed to convert DMG to final format. Aborting."; rm -f "$TEMP_DMG_RW"; exit 1; fi

  # Clean up temporary read/write DMG
  rm -f "$TEMP_DMG_RW"

  echo "Successfully created $DMG_NAME with custom appearance."
}

# ------------------------------- MAIN ----------------------------------------
check_deps

# Ensure we're running from repo root (directory of this script)
cd "$(dirname "$0")"

generate_icns
build_app
sign_app
create_dmg

echo "\nDone! You can now distribute $DMG_NAME to other macOS users." 
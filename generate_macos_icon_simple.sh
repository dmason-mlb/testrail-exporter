#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# generate_macos_icon_simple.sh
#
# Generate a macOS app icon with Apple-style rounded corners (simpler version)
# -----------------------------------------------------------------------------

set -euo pipefail

# Input and output paths
INPUT_ICON="${1:-testrail_exporter/icon.png}"
OUTPUT_DIR="icon.iconset"
OUTPUT_ICNS="icon.icns"

# Check if input file exists
if [[ ! -f "$INPUT_ICON" ]]; then
    echo "Error: Input icon not found at $INPUT_ICON"
    echo "Usage: $0 [input_icon.png]"
    exit 1
fi

echo "Generating macOS icon with Apple-style rounded corners..."

# Create iconset directory
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Function to create icon with rounded corners
create_rounded_icon() {
    local size=$1
    local filename=$2
    
    echo "  Creating ${size}x${size} icon..."
    
    # Calculate corner radius (22.4% of icon size per Apple HIG)
    local radius=$(echo "$size * 0.224" | bc -l | cut -d'.' -f1)
    
    # Create the rounded corner icon with subtle shadow
    magick "$INPUT_ICON" -resize ${size}x${size} \
        \( +clone -alpha extract \
           -draw "fill black rectangle 0,0 $((size-1)),$((size-1))" \
           -draw "fill white roundrectangle 0,0 $((size-1)),$((size-1)) $radius,$radius" \
        \) -alpha off -compose copy_opacity -composite \
        \( +clone -background black -shadow 50x3+0+0 \) \
        +swap -background none -layers merge +repage \
        "$OUTPUT_DIR/$filename"
}

# Generate all required icon sizes
create_rounded_icon 16 "icon_16x16.png"
create_rounded_icon 32 "icon_16x16@2x.png"
create_rounded_icon 32 "icon_32x32.png"
create_rounded_icon 64 "icon_32x32@2x.png"
create_rounded_icon 128 "icon_128x128.png"
create_rounded_icon 256 "icon_128x128@2x.png"
create_rounded_icon 256 "icon_256x256.png"
create_rounded_icon 512 "icon_256x256@2x.png"
create_rounded_icon 512 "icon_512x512.png"
create_rounded_icon 1024 "icon_512x512@2x.png"

# Create the .icns file
echo "Creating .icns file..."
iconutil -c icns "$OUTPUT_DIR" -o "$OUTPUT_ICNS"

# Also create a preview of the 512x512 version
echo "Creating preview image..."
cp "$OUTPUT_DIR/icon_512x512.png" "icon_preview_simple.png"

# Clean up
rm -rf "$OUTPUT_DIR"

echo "✅ Icon generation complete!"
echo "   - macOS icon: $OUTPUT_ICNS"
echo "   - Preview: icon_preview_simple.png"
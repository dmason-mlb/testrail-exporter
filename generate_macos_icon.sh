#!/bin/bash

# Stop on any error and on unset variables or pipe failures
set -euo pipefail
# set -x # DEBUG: Print executed commands (Uncomment to debug, will be verbose)

# --- Configuration ---
INPUT_PNG_DEFAULT="testrail_exporter/icon.png"
INPUT_PNG="${1:-$INPUT_PNG_DEFAULT}"
OUTPUT_ICONSET_DIR="icon.iconset"
FINAL_ICNS_FILE="icon.icns"
CORNER_RADIUS_PERCENT=0.224
DEBUG_STEP=false

# --- Check Dependencies ---
command -v magick >/dev/null 2>&1 || { echo >&2 "Error: ImageMagick (magick command) not found. Please install it (e.g., 'brew install imagemagick')."; exit 1; }
command -v iconutil >/dev/null 2>&1 || { echo >&2 "Error: iconutil (macOS specific) not found. This script requires macOS to create .icns files."; exit 1; }
command -v bc >/dev/null 2>&1 || { echo >&2 "Error: bc (basic calculator) not found. Please install it."; exit 1; }
command -v sips >/dev/null 2>&1 || { echo >&2 "Error: sips (macOS specific) not found. This script needs sips for verification."; exit 1; }

# --- Validate Input ---
if [ ! -f "$INPUT_PNG" ]; then
    echo >&2 "Error: Input PNG file not found at '$INPUT_PNG'"
    exit 1
fi
echo "Using input image: $INPUT_PNG"

# --- Setup Output Directory ---
if [ -d "$OUTPUT_ICONSET_DIR" ]; then
    echo "Clearing existing output directory: $OUTPUT_ICONSET_DIR"
    rm -rf "$OUTPUT_ICONSET_DIR"
fi
mkdir -p "$OUTPUT_ICONSET_DIR"
echo "Created output directory: $OUTPUT_ICONSET_DIR"

# --- Icon Sizes and Names ---
declare -a SIZES=(16 32  32 64  128 256  256 512  512 1024)
declare -a NAMES=(
    "icon_16x16.png" "icon_16x16@2x.png" "icon_32x32.png" "icon_32x32@2x.png"
    "icon_128x128.png" "icon_128x128@2x.png" "icon_256x256.png" "icon_256x256@2x.png"
    "icon_512x512.png" "icon_512x512@2x.png"
)

# --- Temporary File Management ---
TEMP_FILES_TO_CLEAN=()
function cleanup_temp_files {
    if [ ${#TEMP_FILES_TO_CLEAN[@]} -gt 0 ]; then
        echo "Cleaning up temporary files..."
        for tmp_file in "${TEMP_FILES_TO_CLEAN[@]}"; do
            rm -f "$tmp_file"
        done
    fi
}
trap cleanup_temp_files EXIT SIGINT SIGTERM

# --- Main Processing Loop ---
echo "Generating PNGs for .iconset..."
for i in "${!SIZES[@]}"; do
    SIZE=${SIZES[$i]}
    FILENAME=${NAMES[$i]}
    OUTPUT_PNG_PATH="$OUTPUT_ICONSET_DIR/$FILENAME"

    RADIUS_PX=$(printf "%.0f" "$(echo "$SIZE * $CORNER_RADIUS_PERCENT" | bc -l)")
    if [ "$RADIUS_PX" -lt 1 ]; then RADIUS_PX=1; fi
    HALF_SIZE=$((SIZE / 2))
    if [ "$RADIUS_PX" -gt "$HALF_SIZE" ]; then RADIUS_PX=$HALF_SIZE; fi

    # Define all temporary files for this iteration
    TEMP_RESIZED="temp_resized_${SIZE}_${RANDOM}.png"; TEMP_FILES_TO_CLEAN+=("$TEMP_RESIZED")
    TEMP_ROUNDED_MASK="mask_${SIZE}_${RANDOM}.png"; TEMP_FILES_TO_CLEAN+=("$TEMP_ROUNDED_MASK")
    TEMP_GRADIENT_LAYER="temp_gradient_layer_${SIZE}_${RANDOM}.png"; TEMP_FILES_TO_CLEAN+=("$TEMP_GRADIENT_LAYER") # DEFINITION ADDED/CORRECTED
    TEMP_SQUARE_WITH_GLOSS="temp_square_gloss_${SIZE}_${RANDOM}.png"; TEMP_FILES_TO_CLEAN+=("$TEMP_SQUARE_WITH_GLOSS")
    TEMP_SQUARE_WITH_INNER_SHADOW="temp_square_inner_shadow_${SIZE}_${RANDOM}.png"; TEMP_FILES_TO_CLEAN+=("$TEMP_SQUARE_WITH_INNER_SHADOW")
    
    TEMP_EDGE_MASK="temp_edge_mask_${SIZE}_${RANDOM}.miff"; TEMP_FILES_TO_CLEAN+=("$TEMP_EDGE_MASK")
    TEMP_INNER_SHADOW_PART1="temp_inner_shadow_part1_${SIZE}_${RANDOM}.miff"; TEMP_FILES_TO_CLEAN+=("$TEMP_INNER_SHADOW_PART1")
    TEMP_INNER_SHADOW_LAYER="temp_inner_shadow_layer_${SIZE}_${RANDOM}.miff"; TEMP_FILES_TO_CLEAN+=("$TEMP_INNER_SHADOW_LAYER")
    
    TEMP_ROUNDED_FINAL_ICON="temp_rounded_final_icon_${SIZE}_${RANDOM}.png"; TEMP_FILES_TO_CLEAN+=("$TEMP_ROUNDED_FINAL_ICON")
    TEMP_ALPHA_MASK_FOR_SHADOW="temp_alpha_mask_shadow_${SIZE}_${RANDOM}.miff"; TEMP_FILES_TO_CLEAN+=("$TEMP_ALPHA_MASK_FOR_SHADOW")
    TEMP_SHADOW_ONLY="temp_shadow_only_${SIZE}_${RANDOM}.miff"; TEMP_FILES_TO_CLEAN+=("$TEMP_SHADOW_ONLY")

    # Step 1: Resize input to a square image
    magick "$INPUT_PNG" -filter LanczosSharp -resize "${SIZE}x${SIZE}!" "PNG32:$TEMP_RESIZED"
    
    # Step 2: Create the Rounded Corner Mask
    SIZE_MINUS_1=$((SIZE - 1))
    magick -size "${SIZE}x${SIZE}" xc:none -fill white \
        -draw "roundrectangle 0,0,${SIZE_MINUS_1},${SIZE_MINUS_1},${RADIUS_PX},${RADIUS_PX}" \
        "PNG32:$TEMP_ROUNDED_MASK"
    
    # Step 3: Gradient Overlay (Top Gloss) - applied to the square image
    GLOSS_HEIGHT=$(printf "%.0f" "$(echo "$SIZE * 0.40" | bc -l)")
    GLOSS_OPACITY_START="0.15"
    # Part 3a: Generate the gradient layer
    magick -size "${SIZE}x${GLOSS_HEIGHT}" \
           gradient:"rgba(255,255,255,${GLOSS_OPACITY_START})"-"rgba(255,255,255,0.0)" \
           -gravity North -background None -extent "${SIZE}x${SIZE}" \
           "PNG32:$TEMP_GRADIENT_LAYER" # Removed redundant array append
    # Part 3b: Composite the gradient layer onto the resized (still square) image
    magick "$TEMP_RESIZED" "$TEMP_GRADIENT_LAYER" \
           -compose Over -composite "PNG32:$TEMP_SQUARE_WITH_GLOSS"
        
    # Step 4: Inner Shadow - applied to the square image with gloss
    INNER_SHADOW_COLOR="rgba(0,0,0,0.20)"
    INNER_SHADOW_BLUR="0x0.75"
    # Create inner shadow based on the rounded mask, then composite onto the square glossed image
    magick "$TEMP_ROUNDED_MASK" \
           -morphology EdgeIn Diamond:1 \
           -fill "$INNER_SHADOW_COLOR" -opaque white \
           -fill transparent -opaque black \
           -blur "$INNER_SHADOW_BLUR" \
           "$TEMP_INNER_SHADOW_LAYER" # Output is the shaped, colored, blurred inner shadow layer
    
    magick "$TEMP_SQUARE_WITH_GLOSS" "$TEMP_INNER_SHADOW_LAYER" \
           -compose Atop -composite "PNG32:$TEMP_SQUARE_WITH_INNER_SHADOW"

    # Step 5: Final Rounding and Drop Shadow
    # First, apply the rounded corners to the fully styled square image
    magick "$TEMP_SQUARE_WITH_INNER_SHADOW" "$TEMP_ROUNDED_MASK" \
        -alpha off -compose CopyOpacity -composite "PNG32:$TEMP_ROUNDED_FINAL_ICON"

    if [ "$SIZE" -ge 128 ]; then
        SHADOW_OPACITY=35
        current_shadow_params=""
        if [ "$SIZE" -ge 512 ]; then current_shadow_params="${SHADOW_OPACITY}x5+3+4";
        elif [ "$SIZE" -ge 256 ]; then current_shadow_params="${SHADOW_OPACITY}x4+2+3";
        else current_shadow_params="${SHADOW_OPACITY}x3+2+2"; fi
        
        # Part 5a: Extract alpha from the *now rounded* final icon for shadow casting
        magick "$TEMP_ROUNDED_FINAL_ICON" \
            -alpha extract \
            "$TEMP_ALPHA_MASK_FOR_SHADOW"

        # Part 5b: Generate shadow from the rounded alpha mask
        magick "$TEMP_ALPHA_MASK_FOR_SHADOW" \
            -virtual-pixel transparent \
            -background black \
            -shadow "$current_shadow_params" \
            +repage \
            "$TEMP_SHADOW_ONLY"

        # Part 5c: Composite Shadow and the rounded icon
        magick -size "${SIZE}x${SIZE}" xc:none \
               "$TEMP_ROUNDED_FINAL_ICON" -gravity center -compose Over -composite \
               "$TEMP_SHADOW_ONLY" -gravity center -compose DstOver -composite \
               "PNG32:$OUTPUT_PNG_PATH"

        # Part 5d: Re-apply the rounded mask so that any shadow pixels that were
        # laid down outside of the rounded rectangle (especially in the corner
        # areas) are clipped out, preventing the appearance of sharp, semi-
        # transparent corners while preserving the shadow elsewhere.
        magick "$OUTPUT_PNG_PATH" "$TEMP_ROUNDED_MASK" \
               -alpha off -compose CopyOpacity -composite \
               "PNG32:$OUTPUT_PNG_PATH"
    else
        # For smaller sizes, no drop shadow, just output the rounded final icon
        # $TEMP_ROUNDED_FINAL_ICON is already created, so just copy or magick it
        cp "$TEMP_ROUNDED_FINAL_ICON" "$OUTPUT_PNG_PATH" # cp is fine, or magick if paranoid
        # magick "$TEMP_ROUNDED_FINAL_ICON" "PNG32:$OUTPUT_PNG_PATH" # Alternative
    fi

    # Verification
    if [[ -f "$OUTPUT_PNG_PATH" ]]; then
        actual_width=$(sips -g pixelWidth "$OUTPUT_PNG_PATH" 2>/dev/null | awk '/pixelWidth/ {print $2}')
        actual_height=$(sips -g pixelHeight "$OUTPUT_PNG_PATH" 2>/dev/null | awk '/pixelHeight/ {print $2}')
        if [[ "$actual_width" -ne "$SIZE" ]] || [[ "$actual_height" -ne "$SIZE" ]]; then
            echo "ERROR [$FILENAME]: Dimension mismatch for $OUTPUT_PNG_PATH! Expected ${SIZE}x${SIZE}, got ${actual_width}x${actual_height}"
        else
            echo "Verified $OUTPUT_PNG_PATH (${actual_width}x${actual_height})"
        fi
    else
        echo "ERROR [$FILENAME]: Failed to generate $OUTPUT_PNG_PATH during loop."
    fi
done # End of main processing loop

echo "All PNGs for .iconset processing loop completed."

# --- Create .icns File ---
echo "Creating $FINAL_ICNS_FILE from $OUTPUT_ICONSET_DIR ($PWD/$OUTPUT_ICONSET_DIR)..."
iconutil --convert icns --output "$FINAL_ICNS_FILE" "$OUTPUT_ICONSET_DIR"

if [ "$DEBUG_STEP" = true ]; then
    DEBUG_ICNS_COPY="./DEBUG_FINAL_ICON.icns"
    if [[ -f "$FINAL_ICNS_FILE" ]]; then
        cp "$FINAL_ICNS_FILE" "$DEBUG_ICNS_COPY"
        echo "DEBUG: Copied final generated icon to '$DEBUG_ICNS_COPY' for inspection."
    else
        echo "ERROR: $FINAL_ICNS_FILE was not created by iconutil (DEBUG_STEP)."
    fi
fi

echo "Successfully created $FINAL_ICNS_FILE (if iconutil succeeded)."
echo "Script finished. ✨"

exit 0
#!/bin/bash

# Script to simplify all robot mesh files using Fast-Quadric-Mesh-Simplification
# Only processes .obj files as the tool doesn't support .stl format

SIMPLIFY_TOOL="/home/user/hello-robot-simulation/Fast-Quadric-Mesh-Simplification/bin.Linux/simplify"
ASSETS_DIR="$HOME/Downloads/assets"
REDUCTION_RATIO=0.4  # Reduce to 40% of original triangles (60% reduction)
AGGRESSIVENESS=7.0   # Default aggressiveness

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to get file size in human readable format
get_file_size() {
    if [[ -f "$1" ]]; then
        du -h "$1" | cut -f1
    else
        echo "N/A"
    fi
}

# Function to get triangle count from OBJ file
get_triangle_count() {
    if [[ -f "$1" ]]; then
        grep -c "^f " "$1" 2>/dev/null || echo "N/A"
    else
        echo "N/A"
    fi
}

echo "=================================================="
echo "Robot Mesh Simplification Script"
echo "=================================================="
echo "Reduction ratio: ${REDUCTION_RATIO} (keeping $(echo "scale=1; $REDUCTION_RATIO * 100" | bc)% of triangles)"
echo "Aggressiveness: ${AGGRESSIVENESS}"
echo "Assets directory: ${ASSETS_DIR}"
echo ""

# Check if simplify tool exists
if [[ ! -f "$SIMPLIFY_TOOL" ]]; then
    echo -e "${RED}Error: Simplify tool not found at $SIMPLIFY_TOOL${NC}"
    exit 1
fi

# Make sure it's executable
chmod +x "$SIMPLIFY_TOOL"

# Check if assets directory exists
if [[ ! -d "$ASSETS_DIR" ]]; then
    echo -e "${RED}Error: Assets directory not found at $ASSETS_DIR${NC}"
    exit 1
fi

# Find all .obj files
obj_files=($(find "$ASSETS_DIR" -name "*.obj"))
stl_files=($(find "$ASSETS_DIR" -name "*.stl"))

total_obj=${#obj_files[@]}
total_stl=${#stl_files[@]}

echo "Found $total_obj .obj files and $total_stl .stl files"
echo "Note: Only .obj files will be processed (tool doesn't support .stl)"
echo ""

if [[ $total_obj -eq 0 ]]; then
    echo -e "${YELLOW}No .obj files found to process${NC}"
    exit 0
fi

processed=0
failed=0
total_original_size=0
total_simplified_size=0

echo "Processing .obj files..."
echo "----------------------------------------"

for obj_file in "${obj_files[@]}"; do
    filename=$(basename "$obj_file")
    echo -n "Processing: $filename ... "
    
    # Get original file stats
    original_size=$(stat -c%s "$obj_file" 2>/dev/null || echo 0)
    original_triangles=$(get_triangle_count "$obj_file")
    
    # Create temporary output file
    temp_output="/tmp/simplified_$(basename "$obj_file")"
    
    # Run simplification
    if "$SIMPLIFY_TOOL" "$obj_file" "$temp_output" "$REDUCTION_RATIO" "$AGGRESSIVENESS" >/dev/null 2>&1; then
        # Check if output file was created and is valid
        if [[ -f "$temp_output" && -s "$temp_output" ]]; then
            # Get simplified file stats
            simplified_size=$(stat -c%s "$temp_output" 2>/dev/null || echo 0)
            simplified_triangles=$(get_triangle_count "$temp_output")
            
            # Replace original with simplified version
            mv "$temp_output" "$obj_file"
            
            # Calculate reduction
            if [[ $original_size -gt 0 ]]; then
                reduction_percent=$(echo "scale=1; (($original_size - $simplified_size) * 100) / $original_size" | bc 2>/dev/null || echo "N/A")
            else
                reduction_percent="N/A"
            fi
            
            echo -e "${GREEN}✓${NC} ${reduction_percent}% size reduction ($original_triangles → $simplified_triangles triangles)"
            
            total_original_size=$((total_original_size + original_size))
            total_simplified_size=$((total_simplified_size + simplified_size))
            processed=$((processed + 1))
        else
            echo -e "${RED}✗ Failed (no output generated)${NC}"
            rm -f "$temp_output"
            failed=$((failed + 1))
        fi
    else
        echo -e "${RED}✗ Failed (simplification error)${NC}"
        rm -f "$temp_output"
        failed=$((failed + 1))
    fi
done

echo ""
echo "=================================================="
echo "Summary:"
echo "=================================================="
echo "Total .obj files found: $total_obj"
echo "Successfully processed: $processed"
echo "Failed: $failed"

if [[ $total_stl -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}Note: $total_stl .stl files were skipped (not supported by tool)${NC}"
    echo "Consider converting .stl files to .obj format for processing"
fi

if [[ $processed -gt 0 && $total_original_size -gt 0 ]]; then
    total_reduction=$(echo "scale=1; (($total_original_size - $total_simplified_size) * 100) / $total_original_size" | bc 2>/dev/null || echo "N/A")
    original_mb=$(echo "scale=2; $total_original_size / 1048576" | bc 2>/dev/null || echo "N/A")
    simplified_mb=$(echo "scale=2; $total_simplified_size / 1048576" | bc 2>/dev/null || echo "N/A")
    
    echo ""
    echo "Overall file size reduction: ${total_reduction}%"
    echo "Total original size: ${original_mb} MB"
    echo "Total simplified size: ${simplified_mb} MB"
fi

echo ""
echo "Backup of original files available at: ~/Downloads/assets_backup/"
echo "=================================================="

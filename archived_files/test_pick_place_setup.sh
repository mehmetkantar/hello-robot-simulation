#!/bin/bash

echo "🧪 Testing Pick & Place Setup"
echo "============================"

# Check if required files exist
echo "📁 Checking required files..."

files=(
    "launch_pick_place_world.sh"
    "robot_pick_place_control.py"
    "launch/multi_world.launch.py"
    "worlds/multi_world.world"
)

all_found=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - Found"
    else
        echo "❌ $file - Missing"
        all_found=false
    fi
done

if [ "$all_found" = true ]; then
    echo ""
    echo "🎉 All required files found!"
    echo ""
    echo "🚀 Ready to launch pick and place simulation!"
    echo ""
    echo "📋 To run the simulation:"
    echo "   1. Terminal 1: ./launch_pick_place_world.sh"
    echo "   2. Terminal 2: python3 robot_pick_place_control.py"
    echo ""
    echo "🎯 World contains:"
    echo "   • 5 obstacles for navigation challenges"
    echo "   • Table with glass for pick and place"
    echo "   • Side table with additional objects"
    echo ""
    echo "🤖 Robot features:"
    echo "   • Full automated pick and place sequence"
    echo "   • Manual navigation controls"
    echo "   • Individual joint control"
    echo "   • Emergency stop functions"
else
    echo ""
    echo "❌ Some files are missing. Please check the setup."
fi
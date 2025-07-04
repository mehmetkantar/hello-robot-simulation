#!/bin/bash

echo "🔍 Hello Robot Stretch 3 - System Check"
echo "========================================"

# Check ROS2
echo "🔧 Checking ROS2 Humble..."
if command -v ros2 >/dev/null 2>&1; then
    ROS_VERSION=$(ros2 --version 2>/dev/null)
    echo "✅ ROS2 found: $ROS_VERSION"
else
    echo "❌ ROS2 not found"
    exit 1
fi

# Check Python
echo "🐍 Checking Python..."
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# Check workspace structure
echo "📁 Checking workspace structure..."
if [ -d "stretch_ws/src" ]; then
    echo "✅ Workspace structure exists"
else
    echo "❌ Workspace structure missing"
    exit 1
fi

# Check packages
echo "📦 Checking packages..."
if [ -d "stretch_ws/src/stretch_ros2" ]; then
    echo "✅ stretch_ros2 package found"
else
    echo "❌ stretch_ros2 package missing"
fi

if [ -d "stretch_ws/src/stretch_moveit_config" ]; then
    echo "✅ stretch_moveit_config package found"
else
    echo "❌ stretch_moveit_config package missing"
fi

# Check URDF files
echo "🤖 Checking robot description..."
if [ -f "stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf" ]; then
    echo "✅ Stretch 3 URDF found"
else
    echo "❌ Stretch 3 URDF missing"
fi

# Memory check
echo "💾 Checking system memory..."
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
if (( $(echo "$TOTAL_MEM >= 8.0" | bc -l) )); then
    echo "✅ Memory: ${TOTAL_MEM}GB (sufficient)"
else
    echo "⚠️  Memory: ${TOTAL_MEM}GB (recommended: 16GB+)"
fi

echo ""
echo "📋 System Check Summary:"
echo "======================="
echo "Ready to run: ./start_stretch_simulation.sh"
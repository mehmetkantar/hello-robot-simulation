#!/bin/bash

echo "🔧 Hello Robot Stretch 3 - Debug Simulation"
echo "============================================"

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 gzserver gzclient gazebo rviz2 2>/dev/null || true
sleep 2

# Check display
echo "🖥️  Display check:"
echo "DISPLAY: $DISPLAY"
echo "XDG_SESSION_TYPE: $XDG_SESSION_TYPE"
echo "WAYLAND_DISPLAY: $WAYLAND_DISPLAY"

# Test basic GUI capability
echo "🧪 Testing GUI capability..."
if command -v glxinfo >/dev/null 2>&1; then
    echo "OpenGL info:"
    glxinfo | grep "OpenGL version" || echo "No OpenGL info available"
else
    echo "glxinfo not installed, install with: sudo apt install mesa-utils"
fi

# Navigate to workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws

# Source environment
echo "🔧 Sourcing ROS2 environment..."
source /opt/ros/humble/setup.bash
source install/setup.bash

# Test ROS2 setup
echo "🧪 Testing ROS2 setup..."
ros2 pkg list | grep stretch_moveit_config >/dev/null
if [ $? -eq 0 ]; then
    echo "✅ stretch_moveit_config package found"
else
    echo "❌ stretch_moveit_config package not found"
    exit 1
fi

# Check for required files
echo "🧪 Checking launch files..."
if [ -f "src/stretch_moveit_config/launch/stretch_gazebo_moveit.launch.py" ]; then
    echo "✅ Main launch file exists"
else
    echo "❌ Main launch file missing"
    exit 1
fi

# Try launching with explicit GUI settings
echo "🚀 Starting simulation with debug output..."
echo "   - If Gazebo window doesn't appear, check your display settings"
echo "   - If you're using SSH, you may need X11 forwarding: ssh -X"
echo "   - If you're using Wayland, try: export QT_QPA_PLATFORM=wayland"
echo ""

# Launch with timeout for testing
timeout 30s ros2 launch stretch_moveit_config stretch_gazebo_moveit.launch.py
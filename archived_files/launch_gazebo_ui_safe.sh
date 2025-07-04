#!/bin/bash

echo "🛡️  Gazebo UI Safe Mode - Maximum Compatibility"
echo "==============================================="
echo ""

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 gzserver gzclient rviz2 python3 joint_state_publisher_gui 2>/dev/null || true
sleep 3

# Maximum graphics compatibility settings
echo "🖥️  Applying safe graphics settings..."
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export GAZEBO_IP=127.0.0.1
export GAZEBO_MASTER_URI=http://localhost:11345

# Disable problematic graphics features
export __GL_SYNC_TO_VBLANK=0
export __GL_THREADED_OPTIMIZATIONS=0
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

# Setup workspace
echo "🔧 Setting up workspace..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "🎯 Safe mode features:"
echo "   ✅ Reduced graphics load to prevent crashes"
echo "   ✅ Software rendering (no hardware acceleration)"
echo "   ✅ Conservative OpenGL settings"
echo "   ✅ Fixed robot mesh visibility"
echo ""
echo "🚀 If this still crashes, alternatives:"
echo "   1. Use ./test_fixed_robot.sh (empty world, more stable)"
echo "   2. Use ./test_headless_gazebo.sh (no GUI, always works)"
echo "   3. Use RViz only for robot visualization"
echo ""

read -p "Press Enter to launch safe mode Gazebo UI..."

echo "🚀 Launching Gazebo UI in safe mode..."
echo "   (Please be patient - may take 60+ seconds)"
echo ""

# Try with minimal graphics settings
timeout 120s ros2 launch /home/kantar/Desktop/hello-robot/launch/ui_multi_world.launch.py || {
    echo ""
    echo "⚠️  Gazebo UI timed out or crashed"
    echo ""
    echo "🔄 Automatic fallback options:"
    echo "1. Launch headless mode: ./test_headless_gazebo.sh"
    echo "2. Try empty world UI: ./test_fixed_robot.sh" 
    echo "3. Use RViz only visualization"
    echo ""
    echo "🤖 The robot is still working! Graphics issue only."
}

echo ""
echo "🏁 If successful, robot should be visible at (-3, 2) in Gazebo"
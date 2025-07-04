#!/bin/bash

echo "🧪 Simple Robot Test - Empty World"
echo "=================================="
echo ""

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 gzserver gzclient rviz2 python3 joint_state_publisher_gui 2>/dev/null || true
sleep 3

# Set environment variables for VM
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Setup workspace
echo "🔧 Setting up workspace..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "📋 This test will:"
echo "   ✅ Launch Gazebo with EMPTY world (faster, simpler)"
echo "   ✅ Spawn Stretch robot at position (0, 0, 1.0)"
echo "   ✅ Robot will be 1 meter ABOVE ground - very visible!"
echo "   ✅ Joint State Publisher GUI for testing movement"
echo ""
echo "⏰ Expected timeline:"
echo "   • Gazebo opens: 10-20 seconds"
echo "   • Robot spawns: +5 seconds"
echo "   • Should see robot floating 1m above ground"
echo ""
echo "🎯 Success criteria:"
echo "   • Robot visible in Gazebo at center (0,0) position"
echo "   • Robot appears 1 meter above the ground plane"
echo "   • Joint sliders control robot movement"
echo "   • No underground/invisible robot issues"
echo ""

read -p "Press Enter to launch empty world test..."

echo "🚀 Launching empty world with robot test..."
ros2 launch /home/kantar/Desktop/hello-robot/launch/test_empty_world.launch.py
#!/bin/bash

echo "🚀 Simple Gazebo Test - Minimal Setup"
echo "====================================="
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
echo "📋 This will launch:"
echo "   ✅ Gazebo with multi-world (5 obstacles + table + glass)"
echo "   ✅ Stretch robot using basic URDF (more stable)"
echo "   ✅ Joint state publisher GUI for manual control"
echo "   ✅ RViz for visualization"
echo ""
echo "⏰ Startup sequence:"
echo "   1. Gazebo starts (15-30 seconds)"
echo "   2. Robot spawns after 5 seconds"
echo "   3. RViz launches after 8 seconds"
echo ""
echo "🎮 Control options:"
echo "   • Joint State Publisher GUI - Manual joint control"
echo "   • Second terminal: python3 robot_pick_place_control.py"
echo ""
echo "⚠️  If robot not visible in Gazebo:"
echo "   • Check Gazebo Models panel for 'stretch_robot'"
echo "   • Wait up to 60 seconds for full loading"
echo "   • Robot should appear at position (-3, 2)"
echo ""

read -p "Press Enter to launch simple Gazebo setup..."

echo "🚀 Launching simple Gazebo setup..."
ros2 launch /home/kantar/Desktop/hello-robot/launch/simple_gazebo.launch.py
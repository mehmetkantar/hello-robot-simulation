#!/bin/bash

echo "🎮 Gazebo UI Pick & Place - Graphics Optimized"
echo "=============================================="
echo ""

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 gzserver gzclient rviz2 python3 joint_state_publisher_gui 2>/dev/null || true
sleep 3

# Enhanced graphics settings for VM stability
echo "🖥️  Applying graphics optimizations..."
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export GAZEBO_IP=127.0.0.1
export GAZEBO_MASTER_URI=http://localhost:11345

# Reduce graphics load
export __GL_SYNC_TO_VBLANK=0
export __GL_THREADED_OPTIMIZATIONS=1

# Setup workspace
echo "🔧 Setting up workspace..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "🎯 This will launch:"
echo "   ✅ Gazebo UI with multi-world (5 obstacles + table + glass)"
echo "   ✅ Stretch robot with FIXED mesh visibility"
echo "   ✅ Robot at safe starting position (-3.0, 2.0, 0.5)"
echo "   ✅ Joint State Publisher GUI for manual control"
echo "   ✅ RViz as backup visualization"
echo ""
echo "🎮 After launch:"
echo "   • Robot should be VISIBLE in Gazebo at position (-3, 2)"
echo "   • Use Joint State Publisher GUI to test movement"
echo "   • Second terminal: python3 robot_pick_place_control.py"
echo ""
echo "⚠️  Graphics handling:"
echo "   • If Gazebo GUI crashes → RViz will still show robot"
echo "   • If graphics freeze → Ctrl+C and try headless mode"
echo "   • Robot physics runs independently of GUI"
echo ""
echo "🎲 World contents:"
echo "   • 5 colored obstacles for navigation"
echo "   • Central table (1.6m x 1.0m) at height 0.8m"
echo "   • Glass of water on table for pick & place"
echo "   • Additional small objects"
echo ""

read -p "Press Enter to launch Gazebo UI with fixed robot..."

echo "🚀 Launching Gazebo UI with pick & place world..."
echo "   (This may take 30-60 seconds to fully load)"
echo ""

# Launch with error handling
ros2 launch /home/kantar/Desktop/hello-robot/launch/ui_multi_world.launch.py

echo ""
echo "🏁 Launch completed. Check Gazebo Models panel for 'stretch_pick_place_robot'"
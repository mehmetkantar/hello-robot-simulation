#!/bin/bash

echo "🤖 Stretch Robot Pick & Place Simulation"
echo "======================================="
echo ""
echo "🌍 World Features:"
echo "   • 5 Different Obstacles (2 boxes, 2 cylinders, 1 L-shaped)"
echo "   • Main table with glass for pick and place"
echo "   • Side table with additional objects"
echo "   • Room with walls for navigation challenges"
echo ""
echo "🎯 Pick & Place Features:"
echo "   • Full automated pick and place sequence"
echo "   • Individual pose control"
echo "   • Manual joint control"
echo "   • Navigation presets"
echo "   • Emergency stop controls"
echo ""

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
sleep 2

# Setup workspace
echo "🔧 Setting up workspace..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Launch the simulation
echo "🚀 Launching pick and place simulation..."
echo ""
echo "📋 Usage Instructions:"
echo "   1. Wait for Gazebo to fully load"
echo "   2. Run the robot control in a second terminal:"
echo "      cd /home/kantar/Desktop/hello-robot"
echo "      python3 robot_pick_place_control.py"
echo ""
echo "🎮 Control Options:"
echo "   • Pick & Place Tab: Automated sequences"
echo "   • Navigation Tab: Manual driving"
echo "   • Manual Tab: Individual joint control"
echo ""
echo "⚠️  Robot starts at position (-3.0, 2.0) away from obstacles"
echo "    Use 'Navigate to Table' to position for pick and place"
echo ""

ros2 launch /home/kantar/Desktop/hello-robot/launch/multi_world_gazebo.launch.py
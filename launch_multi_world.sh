#!/bin/bash

echo "🌍 Multi-World Stretch Robot Simulation"
echo "======================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
sleep 2

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Launch the multi-world simulation
echo "🚀 Launching multi-world simulation..."
echo "   - Room with multiple obstacles"
echo "   - Main table with glass for pick and place"
echo "   - Side table with additional objects"
echo "   - Robot spawned at (-3.0, 2.0, 0.1)"
echo ""
echo "Use the second terminal to run robot control!"

ros2 launch /home/kantar/Desktop/hello-robot/launch/multi_world.launch.py
#!/bin/bash

echo "🎯 Minimal Gazebo Test - Focus on Robot Spawning"
echo "=============================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 gazebo 2>/dev/null || true
sleep 2

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🚀 Launching minimal setup for robot spawning test..."
echo "   - Gazebo with world"
echo "   - Robot description publisher"
echo "   - Robot spawn with 3-second delay"
echo "   - Robot should appear in Models list on left side"
echo "   - Press Ctrl+C to stop"
echo ""

# Launch minimal version
ros2 launch /home/kantar/Desktop/hello-robot/launch/minimal_robot_gazebo.launch.py
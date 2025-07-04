#!/bin/bash

echo "🤖 ROS2 Gazebo Test - Proper Robot Spawning"
echo "=========================================="

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

echo "🚀 Launching ROS2 Gazebo with proper robot spawning..."
echo "   - Uses ROS2 launch system for proper plugin loading"
echo "   - Robot will appear in Gazebo models list"
echo "   - Robot spawned at safe location (-5, 4)"
echo "   - Press Ctrl+C to stop"
echo ""

# Launch using ROS2 system
ros2 launch /home/kantar/Desktop/hello-robot/launch/multi_world.launch.py
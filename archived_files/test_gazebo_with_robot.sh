#!/bin/bash

echo "🤖 Testing Gazebo World + Robot (Fixed)"
echo "======================================"

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

# Set Gazebo resource path
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/worlds

echo "🚀 Launching Gazebo, Robot Description, and Spawner..."
echo "   - This will start Gazebo, load the robot model, and spawn it."
echo "   - Press Ctrl+C to stop."
echo ""

# Use a single ROS 2 launch file to coordinate everything
ros2 launch /home/kantar/Desktop/hello-robot/launch/obstacle_world.launch.py

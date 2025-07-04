#!/bin/bash

echo "🏠 Obstacle Room Stretch Robot Simulation"
echo "=========================================="

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

# Launch the simulation
ros2 launch /home/kantar/Desktop/hello-robot/launch/obstacle_world.launch.py
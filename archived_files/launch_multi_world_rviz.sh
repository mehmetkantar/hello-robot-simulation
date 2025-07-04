#!/bin/bash

echo "🌍 Multi-World Stretch Robot Simulation (RViz Only)"
echo "=================================================="

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

echo "🚀 Launching RViz-based simulation..."
echo "   - Gazebo server (headless) for physics"
echo "   - RViz for visualization with world markers"
echo "   - Robot spawned at (-3.0, 2.0, 0.1)"
echo ""
echo "In second terminal run: python3 robot_car_control.py"
echo "In third terminal run: python3 world_visualizer.py"
echo ""

# Launch only Gazebo server (no GUI) and RViz
ros2 launch /home/kantar/Desktop/hello-robot/launch/multi_world_headless.launch.py
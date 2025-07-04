#!/bin/bash

echo "🧪 Testing Gazebo World Only"
echo "============================"

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 gazebo 2>/dev/null || true
sleep 2

echo "🚀 Launching Gazebo with world file..."
echo "   - Should show room with walls, obstacles, table, and glass"
echo "   - Press Ctrl+C to stop"
echo ""

# Launch Gazebo directly with world
gazebo /home/kantar/Desktop/hello-robot/worlds/multi_world_simple.world --verbose
#!/bin/bash

echo "🎯 Stable Gazebo Test - Realistic Robot Model"
echo "============================================"

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 gazebo 2>/dev/null || true
sleep 2

echo "🚀 Launching Gazebo with stable robot model..."
echo "   - Room with walls, obstacles, table, and glass"
echo "   - Stretch-like robot that won't crash Gazebo"
echo "   - Robot components:"
echo "     • White cylindrical base with black wheels"
echo "     • Gray mast (telescoping pole)"
echo "     • Red arm base with yellow telescoping arm"
echo "     • Green gripper and blue head/camera"
echo "   - Robot at safe location (-5, 4)"
echo "   - Press Ctrl+C to stop"
echo ""

# Launch Gazebo with stable robot model
gazebo /home/kantar/Desktop/hello-robot/worlds/multi_world_better_robot.world --verbose
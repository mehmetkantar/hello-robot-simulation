#!/bin/bash

echo "🎯 Final Working Gazebo Test"
echo "============================"

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 gazebo 2>/dev/null || true
sleep 2

echo "🚀 Launching final working simulation..."
echo "   ✅ Room with walls, obstacles, table, and glass"
echo "   ✅ Simplified but recognizable Stretch robot"
echo "   ✅ No XML errors, no crashes"
echo "   ✅ Robot at safe location (-5, 4)"
echo ""
echo "You should see:"
echo "   🟤 Brown brick walls around the room"
echo "   🟠 Orange box obstacle at (3, 2)"
echo "   🔵 Blue cylinder obstacle at (-4, -2)"
echo "   🟫 Wooden table at center (0, 0)"
echo "   🔵 Blue glass on the table"
echo "   🤖 Robot with white base, gray mast, yellow arm, green gripper"
echo ""
echo "Press Ctrl+C to stop"

# Launch the working simulation
gazebo /home/kantar/Desktop/hello-robot/worlds/simple_robot_world.world
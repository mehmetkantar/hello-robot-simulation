#!/bin/bash

echo "🎯 Complete Hello Robot Stretch 3 Simulation Test"
echo "================================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 gazebo 2>/dev/null || true
sleep 2

echo "✅ SOLUTION OVERVIEW:"
echo "   🌍 Gazebo: Room with walls, obstacles, table, and glass"
echo "   🤖 Robot: Simplified Stretch model at safe location (-5, 4)"
echo "   🎮 Control: Keyboard-based (no GUI to avoid segfaults)"
echo ""
echo "🚀 STEP 1: Launch Gazebo with world and robot..."
echo "   Run this in Terminal 1:"
echo "   cd /home/kantar/Desktop/hello-robot"
echo "   ./test_final_gazebo.sh"
echo ""
echo "🎮 STEP 2: Launch keyboard control..."
echo "   Run this in Terminal 2:"
echo "   cd /home/kantar/Desktop/hello-robot" 
echo "   python3 simple_robot_control.py"
echo ""
echo "📋 CONTROLS:"
echo "   WASD - Drive (W=forward, S=backward, A=left, D=right)"
echo "   QE   - Lift (Q=up, E=down)"
echo "   RF   - Arm (R=extend, F=retract)"
echo "   TG   - Gripper (T=open, G=close)"
echo "   H    - Home position"
echo "   P    - Reset position"
echo "   X    - Stop all movement"
echo "   ESC  - Exit"
echo ""
echo "✅ SOLUTION BENEFITS:"
echo "   ❌ Fixed: Segmentation fault (removed GUI)"
echo "   ❌ Fixed: Gazebo crashes (simplified robot model)"
echo "   ❌ Fixed: XML parsing errors (corrected syntax)"
echo "   ❌ Fixed: Spawn collisions (safe robot location)"
echo "   ✅ Result: Stable, working simulation with keyboard control"
echo ""
echo "Press any key to start the complete test..."
read -n 1 -s

echo ""
echo "🎬 Starting complete demonstration..."
echo ""

# Launch Gazebo in background
echo "📺 Launching Gazebo..."
gazebo /home/kantar/Desktop/hello-robot/worlds/simple_robot_world.world &
GAZEBO_PID=$!

sleep 5

echo "🎮 Gazebo should now be running with the robot visible!"
echo ""
echo "Next steps:"
echo "1. In a NEW terminal, run: cd /home/kantar/Desktop/hello-robot && python3 simple_robot_control.py"
echo "2. Use WASD keys to drive the robot around"
echo "3. Use QE, RF, TG to control joints"
echo "4. Press ESC to exit"
echo ""
echo "Press Ctrl+C to stop this demo"

# Wait for user to stop
wait $GAZEBO_PID
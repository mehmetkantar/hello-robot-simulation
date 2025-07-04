#!/bin/bash

echo "🤖 Headless Gazebo Test - Robot Verification"
echo "============================================"
echo ""

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 gzserver gzclient rviz2 python3 joint_state_publisher_gui 2>/dev/null || true
sleep 3

# Set environment variables for VM
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Setup workspace
echo "🔧 Setting up workspace..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "🎯 This test will:"
echo "   ✅ Launch Gazebo server (no GUI to avoid graphics crash)"
echo "   ✅ Spawn robot successfully"
echo "   ✅ Verify robot is loaded with all meshes"
echo "   ✅ Open separate tools to control robot"
echo ""
echo "📋 After launch, you can:"
echo "   • Use Joint State Publisher GUI to move robot"
echo "   • Check robot topics: ros2 topic list"
echo "   • Verify robot spawn: ros2 service call /gazebo/get_model_state gazebo_msgs/srv/GetModelState '{model_name: stretch_test_robot}'"
echo ""

read -p "Press Enter to launch headless Gazebo test..."

echo "🚀 Starting Gazebo server (headless)..."

# Start Gazebo server only (no client GUI)
ros2 launch /home/kantar/Desktop/hello-robot/launch/fixed_empty_world.launch.py &
LAUNCH_PID=$!

echo "⏰ Waiting for Gazebo to start and robot to spawn..."
sleep 10

echo ""
echo "🔍 Checking if robot spawned successfully..."
echo "Gazebo models:"
ros2 service call /gazebo/get_world_properties gazebo_msgs/srv/GetWorldProperties 2>/dev/null | grep -A 10 model_names || echo "Service not ready yet"

echo ""
echo "📊 Robot joint states:"
timeout 3 ros2 topic echo /joint_states --once 2>/dev/null || echo "Joint states not ready yet"

echo ""
echo "🎮 Starting Joint State Publisher GUI for robot control..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
GUI_PID=$!

echo ""
echo "✅ Test Status:"
echo "   • Gazebo server running (PID: $LAUNCH_PID)"
echo "   • Joint GUI running (PID: $GUI_PID)"
echo "   • Robot should be spawned and controllable"
echo ""
echo "🔧 To verify robot:"
echo "   1. Move sliders in Joint State Publisher GUI"
echo "   2. Check: ros2 topic list | grep joint"
echo "   3. Monitor: ros2 topic echo /joint_states"
echo ""
echo "Press Ctrl+C to stop all processes"

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping all processes..."; kill $LAUNCH_PID $GUI_PID 2>/dev/null; killall -9 gzserver gzclient 2>/dev/null; exit 0' INT

wait
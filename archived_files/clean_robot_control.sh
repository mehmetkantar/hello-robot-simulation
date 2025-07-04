#!/bin/bash

echo "🤖 Clean Robot Control - Stop Unwanted Movement"
echo "================================================"
echo ""

# Kill ALL existing robot control processes
echo "🧹 Stopping all robot control processes..."
killall -9 python3 2>/dev/null || true
killall -9 robot_state_publisher 2>/dev/null || true
killall -9 joint_state_publisher 2>/dev/null || true
killall -9 joint_state_publisher_gui 2>/dev/null || true
sleep 3

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🔍 Checking what's controlling the robot..."
echo "Current ROS topics:"
ros2 topic list

echo ""
echo "📡 Starting CLEAN robot state publisher..."

# Use a simple approach - just the URDF file path
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -p robot_description:="$(cat /home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf)" \
  -p use_sim_time:=true &

RSP_PID=$!
echo "Robot state publisher started (PID: $RSP_PID)"

sleep 3

echo "🎮 Starting joint control GUI..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui \
  --ros-args -p use_sim_time:=true &

GUI_PID=$!
echo "Joint GUI started (PID: $GUI_PID)"

sleep 2

echo ""
echo "🔍 Checking for unwanted controllers..."
echo "Active topics:"
ros2 topic list | grep -E "(cmd|control|twist|joint)" || echo "No control topics found"

echo ""
echo "📊 Robot joint states:"
timeout 3 ros2 topic echo /joint_states --once 2>/dev/null || echo "Joint states not ready yet"

echo ""
echo "✅ Clean control setup complete!"
echo ""
echo "🎯 To stop robot camera/head movement:"
echo "   1. Use the Joint State Publisher GUI sliders"
echo "   2. Set head_pan and head_tilt to 0.0"
echo "   3. Keep them at 0.0 to stop movement"
echo ""
echo "🎮 How to control robot:"
echo "   • Move sliders in Joint State Publisher GUI"
echo "   • Robot should respond immediately in Gazebo"
echo "   • If head keeps moving, set head joints to 0"
echo ""

echo "Press Ctrl+C to stop clean control system"

# Monitor and report unwanted movement
trap 'echo ""; echo "🛑 Stopping clean control..."; kill $RSP_PID $GUI_PID 2>/dev/null; exit 0' INT

monitor_count=0
while ps -p $RSP_PID > /dev/null && ps -p $GUI_PID > /dev/null; do
    ((monitor_count++))
    
    if [ $((monitor_count % 6)) -eq 0 ]; then
        echo "✅ Clean control active... ($(date '+%H:%M:%S'))"
        
        # Check for unwanted movement every minute
        echo "🔍 Checking head joint values..."
        timeout 2 ros2 topic echo /joint_states --once 2>/dev/null | grep -A 20 "name:" | grep -E "(head_pan|head_tilt)" || true
    fi
    
    sleep 10
done

echo "🤖 Clean control system stopped"
#!/bin/bash

echo "🤖 Starting Robot Control System"
echo "================================"
echo ""

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🔧 Setting up robot control components..."

# Kill any existing control processes
killall -9 python3 joint_state_publisher_gui 2>/dev/null || true
sleep 2

# Start robot state publisher with correct URDF
echo "📡 Starting robot state publisher..."
robot_description_file="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

# Fix mesh paths in URDF
urdf_content=$(cat "$robot_description_file" | sed 's|package://stretch_description/meshes/|file:///home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/meshes/|g')

ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$urdf_content" -p use_sim_time:=true &
RSP_PID=$!

sleep 3

# Start joint state publisher GUI for manual control
echo "🎮 Starting joint control GUI..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui --ros-args -p use_sim_time:=true &
GUI_PID=$!

sleep 3

# Check if topics are working
echo "📊 Checking robot topics..."
timeout 5 ros2 topic list | grep -E "(joint|robot)" || echo "Topics not ready yet..."

sleep 2

echo ""
echo "🎯 Robot control is ready!"
echo ""
echo "🎮 How to control the robot:"
echo ""
echo "1. 📱 Joint State Publisher GUI (recommended):"
echo "   • Should have opened automatically"
echo "   • Use sliders to move robot joints"
echo "   • Changes appear immediately in Gazebo"
echo ""
echo "2. 🤖 Python Pick & Place Control:"
echo "   cd /home/kantar/Desktop/hello-robot"
echo "   python3 robot_pick_place_control.py"
echo ""
echo "3. 📋 Manual joint commands:"
echo "   ros2 topic pub /joint_states sensor_msgs/msg/JointState ..."
echo ""

echo "📺 Camera movement in Gazebo:"
echo "   • Auto-follow is normal Gazebo behavior"
echo "   • Right-click + drag to rotate view"
echo "   • Middle mouse to pan"
echo "   • Scroll wheel to zoom"
echo "   • Press 'r' to reset camera"
echo ""

echo "🔍 Current running processes:"
echo "   Robot State Publisher: PID $RSP_PID"
echo "   Joint GUI: PID $GUI_PID"
echo ""

echo "✅ Setup complete! Try moving the sliders in the Joint State Publisher GUI"
echo "   You should see the robot move in Gazebo immediately!"
echo ""
echo "Press Ctrl+C to stop robot control system"

# Keep running and monitor
trap 'echo ""; echo "🛑 Stopping robot control..."; kill $RSP_PID $GUI_PID 2>/dev/null; exit 0' INT

while true; do
    if ! ps -p $RSP_PID > /dev/null; then
        echo "⚠️  Robot state publisher stopped"
        break
    fi
    if ! ps -p $GUI_PID > /dev/null; then
        echo "⚠️  Joint GUI stopped"
        break
    fi
    
    echo "✅ Robot control active... ($(date '+%H:%M:%S'))"
    sleep 10
done

echo "🤖 Robot control system stopped"
#!/bin/bash

echo "🛑 Stop Robot Camera/Head Movement"
echo "=================================="
echo ""

# Kill everything that might be controlling the robot
echo "🧹 Killing all robot control processes..."

# Kill Python scripts
pkill -f robot_pick_place_control
pkill -f simple_robot_controller
pkill -f robot_car_control
pkill -f python3

# Kill ROS control nodes
pkill -f robot_state_publisher
pkill -f joint_state_publisher
pkill -f joint_state_publisher_gui

echo "✅ All robot control processes stopped"
echo ""

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🤖 Starting minimal robot control..."

# Start ONLY robot state publisher (no extra controllers)
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -p robot_description:="$(cat install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf)" &

RSP_PID=$!

sleep 3

# Start joint publisher GUI for manual control only
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
GUI_PID=$!

sleep 2

echo ""
echo "✅ Minimal control started!"
echo ""
echo "🎯 To stop robot head/camera movement:"
echo ""
echo "1. 📱 In the Joint State Publisher GUI window:"
echo "   • Find 'head_pan' slider → set to 0.0"
echo "   • Find 'head_tilt' slider → set to 0.0"
echo "   • Keep them at 0.0 to prevent movement"
echo ""
echo "2. 🎮 Manual control command:"
echo "   ros2 topic pub /joint_states sensor_msgs/msg/JointState \\"
echo "   '{name: [joint_head_pan, joint_head_tilt], position: [0.0, 0.0]}'"
echo ""
echo "3. 🔍 Check what's moving the robot:"
echo "   ros2 topic echo /joint_states"
echo ""

echo "🤖 Robot should now be controllable ONLY through GUI sliders"
echo "   No automatic movement should occur"
echo ""
echo "Press Ctrl+C to stop all control"

trap 'echo ""; echo "🛑 Stopping control..."; kill $RSP_PID $GUI_PID 2>/dev/null; exit 0' INT

# Keep running
while ps -p $RSP_PID > /dev/null && ps -p $GUI_PID > /dev/null; do
    echo "✅ Manual control only... ($(date '+%H:%M:%S'))"
    sleep 15
done

echo "Control stopped"
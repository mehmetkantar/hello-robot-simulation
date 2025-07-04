#!/bin/bash

echo "🤖 Simple Robot State Publisher Test"
echo "===================================="

# Kill everything
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
sleep 2

# Setup
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Check URDF
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF not found: $URDF_FILE"
    exit 1
fi

echo "✅ URDF found"
echo "File size: $(wc -l < "$URDF_FILE") lines"

# Start robot state publisher only
echo ""
echo "🤖 Starting robot state publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat "$URDF_FILE")" &
RSP_PID=$!

sleep 5

echo ""
echo "🔍 Testing ROS2 communication..."

# Test ROS2 is working
echo "1. ROS2 nodes:"
timeout 5s ros2 node list || echo "❌ ROS2 node list failed"

echo ""
echo "2. ROS2 topics:"
timeout 5s ros2 topic list || echo "❌ ROS2 topic list failed"

echo ""
echo "3. Robot description topic:"
timeout 5s ros2 topic info /robot_description || echo "❌ Robot description topic not found"

echo ""
echo "4. Joint states:"
timeout 5s ros2 topic echo /joint_states --once || echo "❌ No joint states"

echo ""
echo "🎯 If above commands work, start RViz:"
echo "rviz2"
echo "Then add RobotModel display with topic: /robot_description"

echo ""
echo "Press Ctrl+C to stop..."

trap 'kill $RSP_PID 2>/dev/null || true' SIGINT SIGTERM
wait $RSP_PID
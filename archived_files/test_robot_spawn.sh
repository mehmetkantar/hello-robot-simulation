#!/bin/bash

echo "🔍 Testing Robot Spawn System"
echo "============================="

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Check if URDF file exists
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

echo "📋 Checking prerequisites..."

if [ -f "$URDF_FILE" ]; then
    echo "✅ URDF file found: $URDF_FILE"
    echo "   Size: $(wc -l < "$URDF_FILE") lines"
else
    echo "❌ URDF file not found at $URDF_FILE"
    echo "Available URDF files:"
    ls /home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/*.urdf
fi

# Check world file
WORLD_FILE="/home/kantar/Desktop/hello-robot/worlds/obstacle_room.world"
if [ -f "$WORLD_FILE" ]; then
    echo "✅ World file found: $WORLD_FILE"
else
    echo "❌ World file not found at $WORLD_FILE"
    echo "Available world files:"
    ls /home/kantar/Desktop/hello-robot/worlds/*.world
fi

# Check ROS2 packages
echo ""
echo "📦 Checking ROS2 packages..."
if ros2 pkg list | grep -q gazebo_ros; then
    echo "✅ gazebo_ros package available"
else
    echo "❌ gazebo_ros package not found"
fi

if ros2 pkg list | grep -q robot_state_publisher; then
    echo "✅ robot_state_publisher package available"
else
    echo "❌ robot_state_publisher package not found"
fi

echo ""
echo "🎯 Summary:"
echo "   The launch_stable_simulation.sh script should now:"
echo "   1. Load the obstacle_room.world in Gazebo"
echo "   2. Start robot_state_publisher with the Stretch URDF"
echo "   3. Spawn the robot at (-3, 3, 0.1)"
echo "   4. Launch RViz for visualization"
echo ""
echo "If all checks above show ✅, the robot should appear in Gazebo!"
#!/bin/bash

echo "🔍 Quick Robot Verification"
echo "==========================="

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "1. Checking ROS2 nodes:"
ros2 node list

echo ""
echo "2. Checking robot topics:"
ros2 topic list | grep -E "(robot_description|joint_states|tf)"

echo ""
echo "3. Testing joint states:"
echo "Getting one joint state message..."
timeout 3s ros2 topic echo /joint_states --once

echo ""
echo "4. Checking Gazebo models:"
if ros2 service list | grep -q "/gazebo/get_world_properties"; then
    ros2 service call /gazebo/get_world_properties gazebo_msgs/srv/GetWorldProperties "{}"
else
    echo "Gazebo service not available"
fi

echo ""
echo "✅ If you see joint_states messages and robot topics,"
echo "   the robot should be visible in RViz and Gazebo!"
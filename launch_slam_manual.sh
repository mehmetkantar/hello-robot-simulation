#!/bin/bash

# Manual SLAM Launch - Step by step
# Use this if the automatic launcher has issues

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_header "MANUAL SLAM LAUNCH"

echo "This script will guide you through launching SLAM step by step."
echo "You'll need to run each command in a separate terminal."
echo

print_step "1. First, make sure ROS2 is sourced:"
echo "source /opt/ros/humble/setup.bash"
echo "source ~/stretch_ros2/install/setup.bash"
echo

print_step "2. Launch the SLAM Bridge (Terminal 1):"
echo "cd /home/user/hello-robot-simulation"
echo "python3 stretch_slam_bridge_improved.py"
echo

print_step "3. Launch Robot State Publisher (Terminal 2):"
echo "cd /home/user/hello-robot-simulation"

# Create simple URDF file
cat > /tmp/stretch_simple.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="stretch">
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder radius="0.15" length="0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
  </link>
  
  <link name="laser">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="laser_joint" type="fixed">
    <parent link="base_link"/>
    <child link="laser"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
  </joint>
</robot>
EOF

echo "ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:=\"\$(cat /tmp/stretch_simple.urdf)\" -p use_sim_time:=true"
echo

print_step "4. Launch SLAM Toolbox (Terminal 3):"
echo "cd /home/user/hello-robot-simulation"
echo "ros2 run slam_toolbox async_slam_toolbox_node --ros-args --params-file config/mapper_params_online_async.yaml -p use_sim_time:=true"
echo

print_step "5. Launch RViz (Terminal 4):"
echo "cd /home/user/hello-robot-simulation"
echo "ros2 run rviz2 rviz2 -d rviz/stretch_slam.rviz"
echo

print_step "6. Control the robot (Terminal 5):"
echo "ros2 run teleop_twist_keyboard teleop_twist_keyboard"
echo

print_step "7. Monitor topics (Optional - Terminal 6):"
echo "ros2 topic list"
echo "ros2 topic echo /scan"
echo "ros2 topic echo /odom"
echo

print_header "QUICK COMMANDS"
echo
echo "Check if everything is working:"
echo "  ros2 topic list | grep -E '(scan|odom|map)'"
echo "  ros2 node list"
echo
echo "Debug commands:"
echo "  ros2 run tf2_tools view_frames"
echo "  ros2 topic hz /scan"
echo "  ros2 topic hz /odom"
echo
echo "Save map when done:"
echo "  ros2 run nav2_map_server map_saver_cli -f my_map"
echo

print_header "TROUBLESHOOTING"
echo
echo "If RViz doesn't start:"
echo "  - Try: ros2 run rviz2 rviz2 (without config file)"
echo "  - Or use the default RViz config"
echo
echo "If no laser data:"
echo "  - Check: ros2 topic echo /scan"
echo "  - Verify bridge is running"
echo
echo "If SLAM not working:"
echo "  - Check: ros2 topic echo /map"
echo "  - Verify all topics are publishing"
echo
echo "If robot not moving:"
echo "  - Check: ros2 topic echo /cmd_vel"
echo "  - Verify teleop is running"
echo

print_status "Ready to start SLAM manually!"
echo "Open terminals and run the commands above in order."
#!/bin/bash

echo "🔧 Properly Fix Robot Display in RViz"
echo "====================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 gazebo gzserver gzclient robot_state_publisher 2>/dev/null || true
sleep 2

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🔧 Method 1: Using ROS2 launch to properly load robot..."

# Create a proper launch file for robot display
cat > /tmp/robot_display.launch.py << 'EOF'
#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Get the URDF file
    pkg_stretch_description = get_package_share_directory('stretch_description')
    urdf_file = os.path.join(pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf')
    
    # Read the URDF content
    with open(urdf_file, 'r') as infp:
        robot_description_content = infp.read()
    
    robot_description = {'robot_description': robot_description_content}

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Joint state publisher (for manual control)
    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node
    ])
EOF

echo "🚀 Launching robot description properly..."
ros2 launch /tmp/robot_display.launch.py &
LAUNCH_PID=$!

sleep 5

echo "🔍 Checking if robot_description is now available..."
ros2 topic list | grep robot_description
if [ $? -eq 0 ]; then
    echo "✅ robot_description topic is now available!"
    
    # Check the content
    echo "📊 Checking robot_description content..."
    timeout 3s ros2 topic echo /robot_description --once | head -5
    
else
    echo "❌ Still no robot_description topic"
fi

echo ""
echo "🚀 Starting RViz with robot visualization..."

# Create a simpler RViz config
cat > /tmp/simple_robot.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Enabled: true
      Name: Grid
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: RobotModel
      Value: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 2
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Name: Current View
      Pitch: 0.5
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

rviz2 -d /tmp/simple_robot.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎯 Robot Should Now Be Visible in RViz!"
echo "========================================"
echo ""
echo "If you STILL don't see the robot, try these in RViz:"
echo ""
echo "1. 🔍 In the Displays panel (left side):"
echo "   - Look at 'RobotModel' - should have green checkmark ✅"
echo "   - If red ❌, click on it to see the error message"
echo ""
echo "2. 🎯 Try different Fixed Frames:"
echo "   - Global Options → Fixed Frame"
echo "   - Try: 'base_link', 'world', 'odom'"
echo ""
echo "3. 🔄 Reset the view:"
echo "   - Mouse wheel to zoom out"
echo "   - Drag with left mouse to rotate"
echo "   - Try 'Views' → 'Current' → reset button"
echo ""
echo "4. 📊 Check what's actually loaded:"
echo "   - Expand 'RobotModel' in displays"
echo "   - Look at the 'Links' section"
echo "   - You should see: base_link, mast, arm_l0, etc."
echo ""

# Show joint state publisher GUI info
echo "🎮 Joint State Publisher GUI:"
echo "   - A separate window should open"
echo "   - It shows sliders to move robot joints"
echo "   - This confirms the robot model is loaded"
echo ""

echo "Press ENTER when you've checked RViz..."
read

# Method 2: If still not working, try with a simple test robot
echo ""
echo "🧪 If robot still not visible, testing with simple robot..."

# Create a very simple test robot
cat > /tmp/test_simple_robot.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="test_robot">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.3 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
  </link>

  <link name="arm">
    <visual>
      <origin xyz="0.25 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.05 0.05"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0.25 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.05 0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <joint name="base_to_arm" type="revolute">
    <parent link="base_link"/>
    <child link="arm"/>
    <origin xyz="0.25 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="1"/>
  </joint>
</robot>
EOF

echo "🔄 Testing with simple robot URDF..."
killall robot_state_publisher 2>/dev/null
sleep 1

ros2 run robot_state_publisher robot_state_publisher /tmp/test_simple_robot.urdf &
SIMPLE_RSP_PID=$!

sleep 2

echo "✅ Simple robot loaded. Check RViz - you should see:"
echo "   🔵 Blue box (base_link)"
echo "   🔴 Red bar (arm)"
echo ""
echo "If you see the simple robot but not Stretch, the issue is with"
echo "the Stretch URDF mesh files or complexity."
echo ""

echo "Press ENTER to finish..."
read

# Cleanup
kill $LAUNCH_PID $RVIZ_PID $SIMPLE_RSP_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true

echo "🏁 Robot display test completed!"
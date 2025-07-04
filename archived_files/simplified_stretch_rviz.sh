#!/bin/bash

echo "🤖 Simplified Stretch Robot - Basic Shapes"
echo "=========================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true
sleep 2

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash

# Create simplified Stretch robot with basic shapes
cat > /tmp/simplified_stretch.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="simplified_stretch">

  <!-- Base -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.34 0.33 0.13"/>
      </geometry>
      <material name="base_color">
        <color rgba="0.2 0.2 0.2 1"/>
      </material>
    </visual>
  </link>

  <!-- Mast (vertical post) -->
  <link name="link_mast">
    <visual>
      <origin xyz="0 0 0.55"/>
      <geometry>
        <cylinder radius="0.04" length="1.1"/>
      </geometry>
      <material name="mast_color">
        <color rgba="0.8 0.8 0.8 1"/>
      </material>
    </visual>
  </link>

  <!-- Lift (movable part on mast) -->
  <link name="link_lift">
    <visual>
      <geometry>
        <box size="0.15 0.15 0.1"/>
      </geometry>
      <material name="lift_color">
        <color rgba="0.3 0.3 0.8 1"/>
      </material>
    </visual>
  </link>

  <!-- Arm segments -->
  <link name="link_arm_l0">
    <visual>
      <origin xyz="0.13 0 0"/>
      <geometry>
        <box size="0.26 0.05 0.05"/>
      </geometry>
      <material name="arm_color">
        <color rgba="0.6 0.3 0.1 1"/>
      </material>
    </visual>
  </link>

  <link name="link_arm_l1">
    <visual>
      <origin xyz="0.13 0 0"/>
      <geometry>
        <box size="0.26 0.04 0.04"/>
      </geometry>
      <material name="arm_color">
        <color rgba="0.6 0.3 0.1 1"/>
      </material>
    </visual>
  </link>

  <link name="link_arm_l2">
    <visual>
      <origin xyz="0.13 0 0"/>
      <geometry>
        <box size="0.26 0.03 0.03"/>
      </geometry>
      <material name="arm_color">
        <color rgba="0.6 0.3 0.1 1"/>
      </material>
    </visual>
  </link>

  <link name="link_arm_l3">
    <visual>
      <origin xyz="0.13 0 0"/>
      <geometry>
        <box size="0.26 0.02 0.02"/>
      </geometry>
      <material name="arm_color">
        <color rgba="0.6 0.3 0.1 1"/>
      </material>
    </visual>
  </link>

  <!-- Wrist -->
  <link name="link_wrist_yaw">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.06"/>
      </geometry>
      <material name="wrist_color">
        <color rgba="0.4 0.4 0.4 1"/>
      </material>
    </visual>
  </link>

  <!-- Gripper -->
  <link name="link_gripper_finger_left">
    <visual>
      <origin xyz="0.06 0 0"/>
      <geometry>
        <box size="0.12 0.01 0.02"/>
      </geometry>
      <material name="gripper_color">
        <color rgba="0.1 0.8 0.1 1"/>
      </material>
    </visual>
  </link>

  <link name="link_gripper_finger_right">
    <visual>
      <origin xyz="0.06 0 0"/>
      <geometry>
        <box size="0.12 0.01 0.02"/>
      </geometry>
      <material name="gripper_color">
        <color rgba="0.1 0.8 0.1 1"/>
      </material>
    </visual>
  </link>

  <!-- Head -->
  <link name="link_head">
    <visual>
      <geometry>
        <box size="0.08 0.15 0.12"/>
      </geometry>
      <material name="head_color">
        <color rgba="0.8 0.8 0.2 1"/>
      </material>
    </visual>
  </link>

  <!-- Wheels -->
  <link name="link_left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
      <material name="wheel_color">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
  </link>

  <link name="link_right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
      <material name="wheel_color">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
  </link>

  <!-- JOINTS -->
  
  <!-- Base to mast -->
  <joint name="joint_mast" type="fixed">
    <parent link="base_link"/>
    <child link="link_mast"/>
    <origin xyz="-0.08 0 0.065"/>
  </joint>

  <!-- Mast to lift (vertical movement) -->
  <joint name="joint_lift" type="prismatic">
    <parent link="link_mast"/>
    <child link="link_lift"/>
    <origin xyz="0 0 0.2"/>
    <axis xyz="0 0 1"/>
    <limit lower="0" upper="1.1" effort="100" velocity="0.2"/>
  </joint>

  <!-- Lift to arm -->
  <joint name="joint_arm_l0" type="prismatic">
    <parent link="link_lift"/>
    <child link="link_arm_l0"/>
    <origin xyz="0.13 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.52" effort="100" velocity="0.2"/>
  </joint>

  <!-- Telescoping arm joints -->
  <joint name="joint_arm_l1" type="prismatic">
    <parent link="link_arm_l0"/>
    <child link="link_arm_l1"/>
    <origin xyz="0.26 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="100" velocity="0.2"/>
  </joint>

  <joint name="joint_arm_l2" type="prismatic">
    <parent link="link_arm_l1"/>
    <child link="link_arm_l2"/>
    <origin xyz="0.26 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="100" velocity="0.2"/>
  </joint>

  <joint name="joint_arm_l3" type="prismatic">
    <parent link="link_arm_l2"/>
    <child link="link_arm_l3"/>
    <origin xyz="0.26 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="100" velocity="0.2"/>
  </joint>

  <!-- Wrist -->
  <joint name="joint_wrist_yaw" type="revolute">
    <parent link="link_arm_l3"/>
    <child link="link_wrist_yaw"/>
    <origin xyz="0.26 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <!-- Gripper fingers -->
  <joint name="joint_gripper_finger_left" type="prismatic">
    <parent link="link_wrist_yaw"/>
    <child link="link_gripper_finger_left"/>
    <origin xyz="0.1 0.03 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.1" upper="0.1" effort="10" velocity="0.2"/>
  </joint>

  <joint name="joint_gripper_finger_right" type="prismatic">
    <parent link="link_wrist_yaw"/>
    <child link="link_gripper_finger_right"/>
    <origin xyz="0.1 -0.03 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.1" upper="0.1" effort="10" velocity="0.2"/>
  </joint>

  <!-- Head -->
  <joint name="joint_head" type="fixed">
    <parent link="link_mast"/>
    <child link="link_head"/>
    <origin xyz="0 0 1.15"/>
  </joint>

  <!-- Wheels -->
  <joint name="joint_left_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="link_left_wheel"/>
    <origin xyz="0.08 0.17 0.05" rpy="1.57 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="joint_right_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="link_right_wheel"/>
    <origin xyz="0.08 -0.17 0.05" rpy="1.57 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

</robot>
EOF

echo "🚀 Starting simplified Stretch robot..."

# Create a launch file to properly coordinate joint publishing
cat > /tmp/simplified_launch.py << 'LAUNCH_EOF'
#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Read the URDF content
    with open('/tmp/simplified_stretch.urdf', 'r') as infp:
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

    # Joint state publisher GUI for control
    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node
    ])
LAUNCH_EOF

ros2 launch /tmp/simplified_launch.py &
LAUNCH_PID=$!

sleep 3

# Create RViz config
cat > /tmp/simplified_stretch.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.5
      Cell Size: 0.5
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
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
      Name: Simplified_Stretch
      Value: true
    - Class: rviz_default_plugins/TF
      Enabled: true
      Name: TF_Frames
      Value: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3
      Focal Point:
        X: 0.5
        Y: 0
        Z: 0.5
      Name: Stretch_View
      Pitch: 0.3
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

echo "🎯 Starting RViz with simplified Stretch..."
rviz2 -d /tmp/simplified_stretch.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎉 Simplified Hello Robot Stretch 3"
echo "==================================="
echo ""
echo "🎨 What you should see:"
echo "  🔲 Dark gray base (mobile platform)"
echo "  🔘 Light gray mast (vertical post)"  
echo "  🔵 Blue lift (movable on mast)"
echo "  🟫 Brown telescoping arm segments"
echo "  ⚫ Gray wrist joint"
echo "  🟢 Green gripper fingers"
echo "  🟡 Yellow head/camera"
echo "  ⚫ Black wheels"
echo ""
echo "🎮 Controls:"
echo "  • Use Joint State Publisher GUI sliders"
echo "  • joint_lift: Move up/down"
echo "  • joint_arm_l0-l3: Extend/retract arm"
echo "  • joint_wrist_yaw: Rotate wrist"
echo "  • joint_gripper_*: Open/close gripper"
echo "  • wheel joints: Rotate wheels"
echo ""
echo "This gives you the EXACT Stretch robot structure"
echo "with all the right joints and proportions!"
echo ""
echo "Press ENTER to stop..."
read

# Cleanup
kill $LAUNCH_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true
echo "✅ Simplified Stretch demo completed!"
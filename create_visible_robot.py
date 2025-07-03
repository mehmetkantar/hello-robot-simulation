#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os

def create_visible_robot_urdf():
    """Create a simplified, guaranteed visible version of the Stretch robot"""
    
    urdf_content = '''<?xml version="1.0"?>
<robot name="stretch_visible">
  
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.3 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.3 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
  </link>

  <!-- Mast (vertical spine) -->
  <link name="mast">
    <visual>
      <origin xyz="0 0 0.4" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.8"/>
      </geometry>
      <material name="orange">
        <color rgba="1 0.5 0 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.4" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.08 0.8"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
  </link>

  <!-- Arm extending horizontally -->
  <link name="arm">
    <visual>
      <origin xyz="0.25 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.06 0.06"/>
      </geometry>
      <material name="orange">
        <color rgba="1 0.5 0 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0.25 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.06 0.06"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
  </link>

  <!-- Gripper at end of arm -->
  <link name="gripper">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.12 0.08"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.08 0.12 0.08"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Head on top of mast -->
  <link name="head">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.15 0.1 0.08"/>
      </geometry>
      <material name="green">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.15 0.1 0.08"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Left Wheel -->
  <link name="left_wheel">
    <visual>
      <origin xyz="0 0 0" rpy="1.57 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.04"/>
      </geometry>
      <material name="gray">
        <color rgba="0.3 0.3 0.3 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="1.57 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.04"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Right Wheel -->
  <link name="right_wheel">
    <visual>
      <origin xyz="0 0 0" rpy="1.57 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.04"/>
      </geometry>
      <material name="gray">
        <color rgba="0.3 0.3 0.3 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="1.57 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.04"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="base_to_mast" type="fixed">
    <parent link="base_link"/>
    <child link="mast"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
  </joint>

  <joint name="mast_to_arm" type="fixed">
    <parent link="mast"/>
    <child link="arm"/>
    <origin xyz="0 0 0.5" rpy="0 0 0"/>
  </joint>

  <joint name="arm_to_gripper" type="fixed">
    <parent link="arm"/>
    <child link="gripper"/>
    <origin xyz="0.5 0 0" rpy="0 0 0"/>
  </joint>

  <joint name="mast_to_head" type="fixed">
    <parent link="mast"/>
    <child link="head"/>
    <origin xyz="0 0 0.8" rpy="0 0 0"/>
  </joint>

  <joint name="base_to_left_wheel" type="fixed">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.18 0.05" rpy="0 0 0"/>
  </joint>

  <joint name="base_to_right_wheel" type="fixed">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.18 0.05" rpy="0 0 0"/>
  </joint>

</robot>'''
    
    # Save the simplified URDF
    urdf_file = "/tmp/stretch_visible.urdf"
    with open(urdf_file, 'w') as f:
        f.write(urdf_content)
    
    print(f"✅ Created visible robot URDF: {urdf_file}")
    return urdf_file

def test_visible_robot():
    """Test the visible robot in Gazebo"""
    
    urdf_file = create_visible_robot_urdf()
    
    print("🚀 Testing guaranteed visible robot...")
    print("This robot uses only basic shapes with bright colors")
    
    # Create test script
    test_script = f"""#!/bin/bash
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 2

echo "🌍 Starting Gazebo..."
gzserver --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
sleep 8
gzclient &
sleep 5

echo "🤖 Spawning GUARANTEED VISIBLE robot..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run gazebo_ros spawn_entity.py \\
    -file {urdf_file} \\
    -entity stretch_visible \\
    -x 0 -y 0 -z 0.1

echo ""
echo "🎯 You should now see a COLORFUL ROBOT made of:"
echo "   🔵 Blue base (rectangular)"
echo "   🟠 Orange vertical mast"
echo "   🟠 Orange horizontal arm" 
echo "   🔴 Red gripper (at end of arm)"
echo "   🟢 Green head (on top)"
echo "   ⚫ Gray wheels (on sides)"
echo ""
echo "This robot is IMPOSSIBLE to miss!"
echo "Press ENTER to close..."
read

killall -9 gzserver gzclient gazebo 2>/dev/null || true
"""
    
    script_file = "/tmp/test_visible_robot.sh"
    with open(script_file, 'w') as f:
        f.write(test_script)
    
    os.chmod(script_file, 0o755)
    print(f"✅ Created test script: {script_file}")
    
    return script_file

if __name__ == "__main__":
    print("🎨 Creating Guaranteed Visible Robot")
    print("===================================")
    
    script_file = test_visible_robot()
    
    print(f"\n🚀 Run the test: {script_file}")
    print("\nThis robot uses ONLY basic geometric shapes with bright colors.")
    print("It's designed to be visible in ANY environment, including VMs.")
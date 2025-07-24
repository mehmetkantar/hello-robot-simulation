#!/usr/bin/env python3
"""
Simple Robot State Publisher for Stretch URDF
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import subprocess
import os

def main():
    # Read the URDF file
    urdf_path = "/home/user/ament_ws/install/stretch_description/share/stretch_description/urdf/stretch.urdf"
    
    try:
        with open(urdf_path, 'r') as f:
            urdf_content = f.read()
    except:
        # Fallback to simple URDF if the full one can't be read
        urdf_content = '''<?xml version="1.0"?>
<robot name="stretch">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.3 0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
  </link>
  <link name="link_lift">
    <visual>
      <origin xyz="0 0 0.5"/>
      <geometry>
        <cylinder radius="0.05" length="1.0"/>
      </geometry>
      <material name="silver">
        <color rgba="0.8 0.8 0.8 1"/>
      </material>  
    </visual>
  </link>
  <joint name="joint_lift" type="prismatic">
    <parent link="base_link"/>
    <child link="link_lift"/>
    <origin xyz="0.0 0.0 0.0"/>
    <axis xyz="0 0 1"/>
    <limit effort="30" velocity="1" lower="0.0" upper="1.1"/>
  </joint>
</robot>'''

    # Launch robot_state_publisher with the URDF
    cmd = [
        'ros2', 'run', 'robot_state_publisher', 'robot_state_publisher',
        '--ros-args', '-p', 'use_sim_time:=true',
        '-p', f'robot_description:={urdf_content}'
    ]
    
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
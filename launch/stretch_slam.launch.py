#!/usr/bin/env python3
"""
Launch file for Stretch SLAM with MuJoCo simulation

This launch file starts:
1. MuJoCo simulation bridge
2. Robot state publisher
3. SLAM Toolbox for mapping
4. RViz for visualization

Usage:
    ros2 launch stretch_slam.launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    slam_params_file_arg = DeclareLaunchArgument(
        'slam_params_file',
        default_value='mapper_params_online_async.yaml',
        description='SLAM parameters file'
    )
    
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value='stretch_slam.rviz',
        description='RViz configuration file'
    )
    
    # Get parameters
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    rviz_config = LaunchConfiguration('rviz_config')
    
    # Path to configuration files
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
    rviz_dir = os.path.join(os.path.dirname(__file__), '..', 'rviz')
    
    # SLAM Bridge Node
    slam_bridge_node = Node(
        package='stretch_slam',  # This would be your package name
        executable='stretch_slam_bridge.py',
        name='stretch_slam_bridge',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        remappings=[
            ('/cmd_vel', '/cmd_vel'),
            ('/scan', '/scan'),
            ('/odom', '/odom'),
        ]
    )
    
    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': get_stretch_urdf()
        }]
    )
    
    # SLAM Toolbox Node
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            os.path.join(config_dir, slam_params_file),
            {'use_sim_time': use_sim_time}
        ],
        remappings=[
            ('/scan', '/scan'),
            ('/map', '/map'),
            ('/odom', '/odom'),
        ]
    )
    
    # RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(rviz_dir, rviz_config)],
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )
    
    # Joint State Publisher (for missing joints)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        slam_params_file_arg,
        rviz_config_arg,
        slam_bridge_node,
        robot_state_publisher_node,
        joint_state_publisher_node,
        slam_toolbox_node,
        rviz_node,
    ])

def get_stretch_urdf():
    """Get simplified Stretch URDF for visualization"""
    urdf_content = """<?xml version="1.0"?>
<robot name="stretch">
  
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder radius="0.15" length="0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.15" length="0.1"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Laser Link -->
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
  
  <!-- Camera Links -->
  <link name="cam_d405_rgb_frame">
    <visual>
      <geometry>
        <box size="0.03 0.03 0.02"/>
      </geometry>
      <material name="green">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="cam_d405_joint" type="fixed">
    <parent link="base_link"/>
    <child link="cam_d405_rgb_frame"/>
    <origin xyz="0.0 0.0 1.0" rpy="0 0 0"/>
  </joint>
  
  <link name="cam_d435i_rgb_frame">
    <visual>
      <geometry>
        <box size="0.03 0.03 0.02"/>
      </geometry>
      <material name="green">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="cam_d435i_joint" type="fixed">
    <parent link="base_link"/>
    <child link="cam_d435i_rgb_frame"/>
    <origin xyz="0.0 0.0 1.0" rpy="0 0 0"/>
  </joint>
  
  <link name="cam_nav_rgb_frame">
    <visual>
      <geometry>
        <box size="0.03 0.03 0.02"/>
      </geometry>
      <material name="green">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="cam_nav_joint" type="fixed">
    <parent link="base_link"/>
    <child link="cam_nav_rgb_frame"/>
    <origin xyz="0.0 0.0 0.5" rpy="0 0 0"/>
  </joint>
  
</robot>"""
    return urdf_content
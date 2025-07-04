#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Get package directories
    pkg_stretch_description = get_package_share_directory('stretch_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # Path to xacro file for Gazebo
    xacro_file = os.path.join(pkg_stretch_description, 'urdf', 'stretch_gazebo.urdf.xacro')
    
    # Check if Gazebo xacro exists, fallback to regular URDF
    if os.path.exists(xacro_file):
        # Generate robot description from xacro
        robot_description_content = Command([
            'xacro ', xacro_file,
            ' robot_name:=stretch',
            ' use_gazebo:=true',
            ' use_lidar:=true',
            ' use_camera:=true'
        ])
        print(f"✅ Using Gazebo xacro file: {xacro_file}")
    else:
        # Fallback to URDF file
        urdf_file = os.path.join(pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf')
        try:
            with open(urdf_file, 'r') as infp:
                robot_description_content = infp.read()
            print(f"⚠️  Using basic URDF file: {urdf_file}")
        except FileNotFoundError:
            print(f"❌ ERROR: No robot description found!")
            return LaunchDescription([])
    
    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time
        }],
        arguments=['--ros-args', '--log-level', 'info']
    )
    
    # Joint state publisher (for simulation)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )
    
    # Gazebo controllers (if available)
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        name='controller_manager',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time
        }],
        condition=lambda: os.path.exists('/opt/ros/humble/lib/controller_manager/ros2_control_node')
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time if true'
        ),
        robot_state_publisher_node,
        joint_state_publisher_node,
        # controller_manager_node,  # Uncomment if ros2_control is available
    ])
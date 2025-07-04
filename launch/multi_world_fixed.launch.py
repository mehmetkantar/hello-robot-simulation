#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    # Get package directories
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_stretch_description = get_package_share_directory('stretch_description')
    pkg_hello_robot = '/home/kantar/Desktop/hello-robot'
    
    # Launch configuration
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = os.path.join(pkg_hello_robot, 'worlds', 'multi_world.world')
    
    # Start Gazebo with the world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_file,
            'verbose': 'false',
            'gui': 'true',
            'server': 'true',
            'physics': 'ode',
            'use_sim_time': 'true'
        }.items()
    )
    
    # Robot description - try Gazebo xacro first
    xacro_file = os.path.join(pkg_stretch_description, 'urdf', 'stretch_gazebo.urdf.xacro')
    
    if os.path.exists(xacro_file):
        print(f"✅ Using Gazebo xacro: {xacro_file}")
        robot_description_content = Command([
            'xacro ', xacro_file,
            ' robot_name:=stretch',
            ' use_gazebo:=true',
            ' use_lidar:=true',
            ' use_camera:=true'
        ])
    else:
        print("⚠️  Gazebo xacro not found, using basic URDF")
        urdf_file = os.path.join(pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf')
        try:
            with open(urdf_file, 'r') as infp:
                robot_description_content = infp.read()
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
    
    # Joint state publisher for simulation
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )
    
    # Spawn robot in Gazebo at starting position
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'stretch',
            '-x', '-3.0',
            '-y', '2.0', 
            '-z', '0.1',
            '-Y', '0.0'
        ],
        output='screen',
    )
    
    # RViz with multi world configuration
    rviz_config = os.path.join(pkg_hello_robot, 'launch', 'multi_world.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time if true'
        ),
        gazebo,
        robot_state_publisher_node,
        joint_state_publisher_node,
        spawn_entity,
        rviz,
    ])
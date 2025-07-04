#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    # Get package directories
    try:
        pkg_stretch_description = get_package_share_directory('stretch_description')
        pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    except Exception as e:
        print(f"Error finding packages: {e}")
        return LaunchDescription([])

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Start Gazebo with EMPTY world
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'verbose': 'true',
            'pause': 'false',
            'gui': 'true',
            'server': 'true'
        }.items()
    )

    # Robot description - use the basic URDF
    robot_description_file = os.path.join(
        pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf'
    )
    
    try:
        with open(robot_description_file, 'r') as infp:
            robot_description_content = infp.read()
        print(f"✅ Using URDF: {robot_description_file}")
    except FileNotFoundError:
        print(f"❌ URDF file not found: {robot_description_file}")
        return LaunchDescription([])
    
    robot_description = {'robot_description': robot_description_content}

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': use_sim_time}
        ]
    )

    # Joint state publisher GUI for manual control
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Spawn robot in Gazebo - HIGHER POSITION
    spawn_entity_cmd = TimerAction(
        period=5.0,  # Wait 5 seconds for Gazebo to start
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-topic', 'robot_description',
                    '-entity', 'stretch_test_robot',
                    '-x', '0.0',      # Center of empty world
                    '-y', '0.0',
                    '-z', '1.0',      # 1 meter above ground - should be very visible!
                    '-Y', '0.0',
                    '-timeout', '30.0'
                ],
                output='screen'
            )
        ]
    )

    # Static transform for world frame
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'odom'],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Create the launch description
    ld = LaunchDescription()

    # Add the commands to the launch description
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(start_gazebo_cmd)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_gui_node)
    ld.add_action(spawn_entity_cmd)
    ld.add_action(static_tf_node)

    return ld
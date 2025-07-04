#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
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
    
    pkg_hello_robot = '/home/kantar/Desktop/hello-robot'

    # Set environment variables for better graphics compatibility
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=os.path.join(pkg_stretch_description, '..')
    )
    
    set_gazebo_resource_path = SetEnvironmentVariable(
        name='GAZEBO_RESOURCE_PATH',
        value=f"{pkg_stretch_description}:/opt/ros/humble/share/gazebo-11/media"
    )
    
    # Graphics optimization for VM
    set_libgl = SetEnvironmentVariable(name='LIBGL_ALWAYS_SOFTWARE', value='1')
    set_qt_platform = SetEnvironmentVariable(name='QT_QPA_PLATFORM', value='xcb')
    set_session_type = SetEnvironmentVariable(name='XDG_SESSION_TYPE', value='x11')

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Start Gazebo with multi-world
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(pkg_hello_robot, 'worlds', 'multi_world.world'),
            'verbose': 'false',
            'pause': 'false',
            'gui': 'true',
            'server': 'true',
            'physics': 'ode'
        }.items()
    )

    # Robot description with FIXED mesh paths
    robot_description_file = os.path.join(
        pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf'
    )
    
    try:
        with open(robot_description_file, 'r') as infp:
            robot_description_content = infp.read()
        print(f"✅ Using URDF: {robot_description_file}")
        
        # Fix mesh paths - replace package:// with proper absolute paths
        meshes_path = os.path.join(pkg_stretch_description, 'meshes')
        robot_description_content = robot_description_content.replace(
            'package://stretch_description/meshes/', 
            f'file://{meshes_path}/'
        )
        print(f"✅ Fixed mesh paths to: {meshes_path}")
        
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

    # Spawn robot in Gazebo - SAFE STARTING POSITION
    spawn_entity_cmd = TimerAction(
        period=5.0,  # Wait 5 seconds for Gazebo to start
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-topic', 'robot_description',
                    '-entity', 'stretch_pick_place_robot',
                    '-x', '-3.0',     # Starting position away from obstacles
                    '-y', '2.0',
                    '-z', '0.5',      # Well above ground - visible!
                    '-Y', '0.0',      # Facing toward table
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

    # RViz as backup visualization
    rviz_config = os.path.join(pkg_hello_robot, 'launch', 'multi_world.rviz')
    rviz_node = TimerAction(
        period=8.0,  # Start RViz after Gazebo
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
                output='screen',
                parameters=[{'use_sim_time': use_sim_time}]
            )
        ]
    )

    # Create the launch description
    ld = LaunchDescription()

    # Add environment variables first
    ld.add_action(set_libgl)
    ld.add_action(set_qt_platform) 
    ld.add_action(set_session_type)
    ld.add_action(set_gazebo_model_path)
    ld.add_action(set_gazebo_resource_path)
    
    # Add the commands to the launch description
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(start_gazebo_cmd)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_gui_node)
    ld.add_action(spawn_entity_cmd)
    ld.add_action(static_tf_node)
    ld.add_action(rviz_node)

    return ld
#!/usr/bin/env python3

import os
import subprocess
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
    pkg_stretch_moveit_config = get_package_share_directory('stretch_moveit_config')
    pkg_stretch_description = get_package_share_directory('stretch_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_hello_robot = '/home/kantar/Desktop/hello-robot'

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Start Gazebo with our custom world
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

    # Robot description - use Gazebo URDF with proper plugins
    gazebo_urdf_file = os.path.join(
        pkg_stretch_description, 'urdf', 'stretch_gazebo.urdf.xacro'
    )
    
    # Use xacro to process the file and include Gazebo plugins
    try:
        print(f"✅ Processing Gazebo xacro: {gazebo_urdf_file}")
        robot_description_content = subprocess.check_output([
            'xacro', gazebo_urdf_file,
            'use_gazebo:=true',
            'use_lidar:=true',
            'use_camera:=true'
        ]).decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error processing xacro file: {e}")
        # Fallback to static URDF
        robot_description_file = os.path.join(
            pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf'
        )
        with open(robot_description_file, 'r') as infp:
            robot_description_content = infp.read()
        print(f"⚠️  Using fallback URDF: {robot_description_file}")
    
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

    # Joint state publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Spawn robot in Gazebo at starting position with delay
    spawn_entity_cmd = TimerAction(
        period=3.0,  # Wait 3 seconds for Gazebo to start
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-topic', 'robot_description',
                    '-entity', 'stretch_robot',
                    '-x', '-3.0',     # Starting position away from table
                    '-y', '2.0',
                    '-z', '0.5',      # Well above ground
                    '-Y', '0.0',      # Facing forward
                    '-timeout', '60.0'
                ],
                output='screen'
            )
        ]
    )

    # Static transform publisher for world -> odom (for MoveIt and navigation)
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'odom'],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # RViz with multi world configuration
    rviz_config = os.path.join(pkg_hello_robot, 'launch', 'multi_world.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Add the commands to the launch description
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(start_gazebo_cmd)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(spawn_entity_cmd)
    ld.add_action(static_tf_node)
    ld.add_action(rviz_node)

    return ld
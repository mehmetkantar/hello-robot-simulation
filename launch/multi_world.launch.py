import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_stretch_moveit_config = get_package_share_directory('stretch_moveit_config')
    pkg_hello_robot = '/home/kantar/Desktop/hello-robot'

    # Start Gazebo with proper ROS integration
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(pkg_hello_robot, 'worlds', 'multi_world_simple.world'),
            'verbose': 'false',
            'gui': 'true',
            'server': 'true'
        }.items()
    )

    # Robot description
    robot_description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_stretch_moveit_config, 'launch', 'simple_robot.launch.py'),
        )
    )

    # Spawn robot at a safe starting position (northwest corner, away from obstacles)
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot_description', '-entity', 'stretch', '-x', '-5.0', '-y', '4.0', '-z', '0.1', '-Y', '0.0'],
        output='screen',
    )

    # RViz with multi world configuration
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_hello_robot, 'launch', 'multi_world.rviz')],
        output='screen',
    )

    return LaunchDescription([
        gazebo,
        robot_description_launch,
        spawn_entity,
        rviz,
    ])
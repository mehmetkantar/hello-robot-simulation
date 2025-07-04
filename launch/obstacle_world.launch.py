import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_stretch_moveit_config = get_package_share_directory('stretch_moveit_config')
    pkg_hello_robot = '/home/kantar/Desktop/hello-robot'

    # Start Gazebo server
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': os.path.join(pkg_hello_robot, 'worlds', 'obstacle_room.world')}.items()
    )

    # Start Gazebo client
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # Robot description
    robot_description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_stretch_moveit_config, 'launch', 'simple_robot.launch.py'),
        )
    )

    # Define the spawner node
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot_description', '-entity', 'stretch', '-x', '-2.0', '-y', '0.0', '-z', '0.1'],
        output='screen',
    )

    # Spawn robot after a delay
    spawn_entity_delayed = TimerAction(
        period=5.0,  # Wait for 5 seconds
        actions=[spawn_entity],
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_hello_robot, 'launch', 'obstacle_room.rviz')],
        output='screen',
    )

    return LaunchDescription([
        gzserver,
        gzclient,
        robot_description_launch,
        spawn_entity_delayed,
        rviz,
    ])

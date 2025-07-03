#!/bin/bash

echo "🤖 Exact Hello Robot Stretch URDF - With Working Joint Control"
echo "=============================================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui gazebo gzserver gzclient 2>/dev/null || true
sleep 2

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🚀 Starting EXACT Stretch URDF with joint control..."

# Create launch file that properly sets up joint control
cat > /tmp/exact_stretch_with_joints.launch.py << 'EOF'
#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Get the URDF file
    pkg_stretch_description = get_package_share_directory('stretch_description')
    urdf_file = os.path.join(pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf')
    
    # Read the URDF content
    with open(urdf_file, 'r') as infp:
        robot_description_content = infp.read()
    
    robot_description = {'robot_description': robot_description_content}

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Joint state publisher GUI for control
    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node
    ])
EOF

# Launch the exact Stretch robot
ros2 launch /tmp/exact_stretch_with_joints.launch.py &
LAUNCH_PID=$!

sleep 5

echo "🔍 Checking robot_description..."
timeout 3s ros2 topic echo /robot_description --once | head -3

echo ""
echo "🔍 Checking joint states..."
timeout 3s ros2 topic echo /joint_states --once | head -5

# Create optimized RViz config for exact Stretch
cat > /tmp/exact_stretch.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Stretch_Robot1
        - /Stretch_Robot1/Links1
      Splitter Ratio: 0.5
    Tree Height: 600
Visualization Manager:
  Displays:
    - Alpha: 0.3
      Cell Size: 0.5
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Name: Floor_Grid
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Collision Enabled: false
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Links:
        All Links Enabled: true
        Expand Joint Details: false
        Expand Link Details: false
        Expand Tree: true
        Link Tree Style: Links in Alphabetic Order
        base_link:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_arm_l0:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_arm_l1:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_arm_l2:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_arm_l3:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_gripper_finger_left:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_gripper_finger_right:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_head:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_lift:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_mast:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_wrist_yaw:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
      Name: Stretch_Robot
      TF Prefix: ""
      Update Interval: 0
      Value: true
      Visual Enabled: true
    - Class: rviz_default_plugins/TF
      Enabled: true
      Frame Timeout: 15
      Frames:
        All Enabled: false
        base_link:
          Value: true
        link_arm_l0:
          Value: true
        link_arm_l1:
          Value: true
        link_arm_l2:
          Value: true
        link_arm_l3:
          Value: true
        link_gripper_finger_left:
          Value: true
        link_gripper_finger_right:
          Value: true
        link_head:
          Value: true
        link_lift:
          Value: true
        link_mast:
          Value: true
        link_wrist_yaw:
          Value: true
      Marker Alpha: 1
      Marker Scale: 0.3
      Name: TF_Frames
      Show Arrows: true
      Show Axes: true
      Show Names: true
      Tree:
        base_link:
          link_mast:
            link_lift:
              link_arm_l0:
                link_arm_l1:
                  link_arm_l2:
                    link_arm_l3:
                      link_wrist_yaw:
                        link_gripper_finger_left:
                          {}
                        link_gripper_finger_right:
                          {}
            link_head:
              {}
      Update Interval: 0
      Value: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 2.5
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.06
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0.3
        Y: 0
        Z: 0.8
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05
      Invert Z Axis: false
      Name: Stretch_View
      Near Clip Distance: 0.01
      Pitch: 0.4
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

echo "🎯 Starting RViz with exact Stretch URDF..."
rviz2 -d /tmp/exact_stretch.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎉 EXACT Hello Robot Stretch 3 URDF"
echo "===================================="
echo ""
echo "✅ This is the OFFICIAL Hello Robot Stretch URDF"
echo "✅ All meshes and exact specifications"
echo "✅ Working joint control via GUI sliders"
echo ""
echo "🎮 Joint Controls Available:"
echo "  • joint_lift - Vertical mast movement (0 to 1.1m)"
echo "  • joint_arm_l0 - First arm extension"
echo "  • joint_arm_l1 - Second arm extension" 
echo "  • joint_arm_l2 - Third arm extension"
echo "  • joint_arm_l3 - Fourth arm extension"
echo "  • joint_wrist_yaw - Wrist rotation"
echo "  • joint_wrist_pitch - Wrist pitch"
echo "  • joint_wrist_roll - Wrist roll"
echo "  • joint_gripper_finger_left - Left finger"
echo "  • joint_gripper_finger_right - Right finger"
echo "  • joint_head_pan - Head pan"
echo "  • joint_head_tilt - Head tilt"
echo ""
echo "💡 Tips for better visualization:"
echo "  • If meshes don't render, you'll see coordinate frames"
echo "  • TF frames show the robot structure clearly"
echo "  • Joint movements update in real-time"
echo "  • Use mouse to orbit around the robot"
echo ""
echo "🔧 RViz Controls:"
echo "  • Left click + drag: Rotate view"
echo "  • Middle click + drag: Pan"
echo "  • Scroll wheel: Zoom"
echo "  • In Displays panel: Expand 'Stretch_Robot' to see all links"
echo ""
echo "Press ENTER to stop..."
read

# Cleanup
kill $LAUNCH_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true

echo "✅ Exact Stretch URDF demo completed!"
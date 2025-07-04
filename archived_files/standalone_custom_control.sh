#!/bin/bash

echo "🎨 Standalone Custom Stretch Control"
echo "===================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes to avoid conflicts
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui joint_state_publisher 2>/dev/null || true
sleep 2

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🚀 Starting robot state publisher only..."

# Create minimal launch file (robot state publisher only, no joint publisher GUI)
cat > /tmp/robot_only.launch.py << 'EOF'
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

    # Only robot state publisher (no joint state publisher GUI to avoid conflicts)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    return LaunchDescription([
        robot_state_publisher_node
    ])
EOF

ros2 launch /tmp/robot_only.launch.py &
ROBOT_PID=$!

sleep 3

echo "🎯 Starting enhanced RViz..."

# Use the same great RViz config from enhanced script
cat > /tmp/enhanced_stretch.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Stretch_Robot1
        - /Stretch_Robot1/Links1
        - /Joint_Controls1
      Splitter Ratio: 0.4
    Tree Height: 700
  - Class: rviz_common/Selection
    Name: Selection
  - Class: rviz_common/Tool Properties
    Expanded:
      - /2D Pose Estimate1
      - /2D Nav Goal1
    Name: Tool Properties
    Splitter Ratio: 0.5897196531295776
  - Class: rviz_common/Views
    Expanded:
      - /Current View1
    Name: Views
    Splitter Ratio: 0.5
Visualization Manager:
  Displays:
    - Alpha: 0.3
      Cell Size: 0.5
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Line Style:
        Line Width: 0.029999999329447746
        Value: Lines
      Name: Floor_Grid
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
        Z: 0
      Plane: XY
      Plane Cell Count: 20
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Collision Enabled: false
      Description Source: Topic
      Description Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /robot_description
      Enabled: true
      Links:
        All Links Enabled: true
        Expand Joint Details: true
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
          Show Axes: true
          Show Trail: false
          Value: true
        link_arm_l1:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_arm_l2:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_arm_l3:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_gripper_finger_left:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_gripper_finger_right:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_head:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_lift:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_mast:
          Alpha: 1
          Show Axes: false
          Show Trail: false
          Value: true
        link_wrist_yaw:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_wrist_pitch:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
        link_wrist_roll:
          Alpha: 1
          Show Axes: true
          Show Trail: false
          Value: true
      Mass Properties:
        Inertia: false
        Mass: false
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
        link_wrist_pitch:
          Value: true
        link_wrist_roll:
          Value: true
      Marker Alpha: 1
      Marker Scale: 0.2
      Name: Joint_Frames
      Show Arrows: true
      Show Axes: true
      Show Names: true
      Tree:
        base_link:
          link_mast:
            link_lift:
              link_arm_l4:
                link_arm_l3:
                  link_arm_l2:
                    link_arm_l1:
                      link_arm_l0:
                        link_wrist_yaw:
                          link_wrist_pitch:
                            link_wrist_roll:
                              link_gripper_finger_left:
                                {}
                              link_gripper_finger_right:
                                {}
            link_head:
              {}
      Update Interval: 0
      Value: true
  Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Tools:
    - Class: rviz_default_plugins/Interact
      Hide Inactive Objects: true
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/Select
    - Class: rviz_default_plugins/FocusCamera
    - Class: rviz_default_plugins/Measure
      Line color: 128; 128; 0
  Transformation:
    Current:
      Class: rviz_default_plugins/TF
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.06
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0.5
        Y: 0
        Z: 0.8
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05
      Invert Z Axis: false
      Name: Stretch_View
      Near Clip Distance: 0.01
      Pitch: 0.3
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

rviz2 -d /tmp/enhanced_stretch.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎨 Standalone Custom Control Ready!"
echo "=================================="
echo ""
echo "✅ **Robot State Publisher**: Running (publishes robot description)"
echo "✅ **RViz**: Running (enhanced visualization)"
echo "❌ **No conflicting joint publishers**: Clean setup"
echo ""
echo "🚀 **Now start the custom controller:**"
echo ""
echo "   python3 /home/kantar/Desktop/hello-robot/custom_joint_control.py"
echo ""
echo "💡 **How this works:**"
echo "   • Only robot_state_publisher is running (no GUI conflicts)"
echo "   • Custom Python controller has exclusive joint control"
echo "   • Enhanced RViz visualization shows the robot perfectly"
echo "   • No competing publishers = stable movement"
echo ""
echo "🎯 **Expected behavior:**"
echo "   • Robot should be visible in RViz"
echo "   • Custom GUI sliders move robot smoothly"
echo "   • No jumping or conflicting movements"
echo ""
echo "Press ENTER when you're done with custom control to stop..."
read

# Cleanup
kill $ROBOT_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui python3 2>/dev/null || true

echo "✅ Standalone custom control stopped!"
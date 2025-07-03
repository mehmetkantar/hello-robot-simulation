#!/bin/bash

echo "🎮 Enhanced Stretch Robot - Full Joint Control"
echo "=============================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui joint_state_publisher 2>/dev/null || true
sleep 2

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🔧 Creating enhanced joint control setup..."

# Create a working launch file
echo "🚀 Creating proper launch file..."
cat > /tmp/stretch_control.launch.py << 'EOF'
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

    # Joint state publisher GUI
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node
    ])
EOF

echo "🚀 Starting robot with proper launch file..."
ros2 launch /tmp/stretch_control.launch.py &
LAUNCH_PID=$!

sleep 5

echo "🔍 Checking available joints..."
echo "==================================="
timeout 5s ros2 topic echo /joint_states --once | grep -A 20 "name:"

echo ""
echo "🔍 Testing joint control..."
echo "==========================="

# Create a simple joint command publisher for testing
python3 -c "
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class JointTester(Node):
    def __init__(self):
        super().__init__('joint_tester')
        self.pub = self.create_publisher(JointState, '/joint_states', 10)
        
    def publish_test_pose(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # Define all the main controllable joints
        msg.name = [
            'joint_lift',
            'joint_arm_l0', 'joint_arm_l1', 'joint_arm_l2', 'joint_arm_l3',
            'joint_wrist_yaw', 'joint_wrist_pitch', 'joint_wrist_roll',
            'joint_gripper_finger_left', 'joint_gripper_finger_right',
            'joint_head_pan', 'joint_head_tilt',
            'joint_left_wheel', 'joint_right_wheel'
        ]
        
        # Set some test positions
        msg.position = [
            0.5,    # lift
            0.1, 0.05, 0.03, 0.02,  # arm segments
            0.0, 0.0, 0.0,  # wrist
            0.02, -0.02,    # gripper (slightly open)
            0.0, 0.0,       # head
            0.0, 0.0        # wheels
        ]
        
        msg.velocity = [0.0] * len(msg.name)
        msg.effort = [0.0] * len(msg.name)
        
        self.pub.publish(msg)
        print('Published test joint positions')

def main():
    rclpy.init()
    node = JointTester()
    node.publish_test_pose()
    time.sleep(1)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
" &

sleep 3

# Create comprehensive RViz config with better joint visualization
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

echo "🎯 Starting enhanced RViz with joint controls..."
rviz2 -d /tmp/enhanced_stretch.rviz &
RVIZ_PID=$!

sleep 4

echo ""
echo "🎮 Enhanced Hello Robot Stretch Control"
echo "======================================="
echo ""
echo "✅ Multiple Joint Control Methods Available:"
echo ""
echo "1. 🖱️  **Joint State Publisher GUI** (Should open automatically)"
echo "   • Sliders for all movable joints"
echo "   • Real-time robot movement"
echo "   • Randomize/Center buttons"
echo ""
echo "2. 🎯 **Command Line Joint Control**"
echo "   You can also control joints programmatically:"
echo ""
echo "   ros2 topic pub /joint_states sensor_msgs/msg/JointState \\"
echo "   '{header: {stamp: {sec: 0, nanosec: 0}, frame_id: \"\"}, \\"
echo "    name: [joint_lift, joint_arm_l0], \\"
echo "    position: [0.5, 0.1], \\"
echo "    velocity: [], effort: []}'"
echo ""
echo "3. 📊 **Available Controllable Joints:**"
echo "   • joint_lift (0.0 to 1.1) - Vertical mast movement"
echo "   • joint_arm_l0 (0.0 to 0.13) - First arm segment"  
echo "   • joint_arm_l1 (0.0 to 0.13) - Second arm segment"
echo "   • joint_arm_l2 (0.0 to 0.13) - Third arm segment"
echo "   • joint_arm_l3 (0.0 to 0.13) - Fourth arm segment"
echo "   • joint_wrist_yaw (-1.57 to 1.57) - Wrist rotation"
echo "   • joint_wrist_pitch (-0.4 to 0.4) - Wrist pitch"
echo "   • joint_wrist_roll (-1.57 to 1.57) - Wrist roll"
echo "   • joint_gripper_finger_left/right - Gripper control"
echo "   • joint_head_pan/tilt - Head movement"
echo "   • joint_left_wheel/right_wheel - Wheel rotation"
echo ""
echo "4. 🔧 **Troubleshooting Joint Control:**"
echo "   If sliders don't work:"
echo "   • Check if Joint State Publisher GUI window opened"
echo "   • Try clicking 'Randomize' then 'Center' buttons"
echo "   • Ensure the GUI window has focus"
echo "   • Look for error messages in terminal"
echo ""
echo "5. 🎨 **RViz Features:**"
echo "   • TF frames show joint coordinate systems"
echo "   • Expand 'Stretch_Robot' to see all links"
echo "   • Joint axes are visible on moving parts"
echo ""
echo "Press ENTER to stop the enhanced control system..."
read

# Cleanup
kill $LAUNCH_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true

echo "✅ Enhanced Stretch control system stopped!"
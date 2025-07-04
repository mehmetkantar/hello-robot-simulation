#!/bin/bash

echo "🎮 Working Stretch Robot - Full Joint Control"
echo "============================================="

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

echo "🚀 Starting robot state publisher..."

# Start robot state publisher with URDF
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF file not found: $URDF_FILE"
    exit 1
fi

echo "📁 Using URDF: $URDF_FILE"

# Start robot state publisher
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(cat $URDF_FILE)" &
RSP_PID=$!

sleep 3

echo "🎮 Starting joint state publisher GUI..."
# Start joint state publisher GUI
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
JSP_PID=$!

sleep 3

echo "🔍 Checking joint states..."
timeout 5s ros2 topic echo /joint_states --once | head -20

# Create simple RViz config with joint visualization
cat > /tmp/working_stretch.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Stretch_Robot1
        - /TF1
      Splitter Ratio: 0.5
    Tree Height: 500
Visualization Manager:
  Displays:
    - Alpha: 0.3
      Cell Size: 0.5
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Name: Grid
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Links:
        All Links Enabled: true
        Expand Joint Details: true
        Expand Link Details: false
        Expand Tree: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/TF
      Enabled: true
      Frame Timeout: 15
      Frames:
        All Enabled: true
      Marker Alpha: 1
      Marker Scale: 0.3
      Name: TF
      Show Arrows: true
      Show Axes: true
      Show Names: true
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
      Distance: 3
      Focal Point:
        X: 0.5
        Y: 0
        Z: 0.8
      Name: Current View
      Pitch: 0.4
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

echo "🎯 Starting RViz..."
rviz2 -d /tmp/working_stretch.rviz &
RVIZ_PID=$!

sleep 4

echo ""
echo "🎉 Working Stretch Robot Control"
echo "================================"
echo ""
echo "✅ What should be running:"
echo "  1. 🤖 Robot State Publisher (publishes robot description)"
echo "  2. 🎮 Joint State Publisher GUI (control window with sliders)"
echo "  3. 🎯 RViz (visualization)"
echo ""
echo "🔍 Check for Joint State Publisher GUI window:"
echo "  • Should show a separate window with joint sliders"
echo "  • Look for window titled 'Joint State Publisher'"
echo "  • If you don't see it, it might be behind other windows"
echo ""
echo "🎮 Available Joint Controls (if GUI is working):"
echo "  • joint_lift: 0.0 to 1.1 (lift up/down mast)"
echo "  • joint_arm_l0: 0.0 to 0.13 (extend first arm segment)"
echo "  • joint_arm_l1: 0.0 to 0.13 (extend second arm segment)"
echo "  • joint_arm_l2: 0.0 to 0.13 (extend third arm segment)"
echo "  • joint_arm_l3: 0.0 to 0.13 (extend fourth arm segment)"
echo "  • joint_wrist_yaw: -1.57 to 1.57 (rotate wrist)"
echo "  • joint_gripper_finger_left/right: gripper control"
echo "  • joint_head_pan/tilt: head movement"
echo "  • joint_left_wheel/right_wheel: wheel rotation"
echo ""
echo "🔧 Manual Joint Control (if GUI doesn't work):"
echo "   You can control joints manually with commands like:"
echo ""
echo "   # Move lift to middle position"
echo "   ros2 topic pub --once /joint_states sensor_msgs/msg/JointState \\"
echo "   '{name: [joint_lift], position: [0.5]}'"
echo ""
echo "   # Extend first arm segment"
echo "   ros2 topic pub --once /joint_states sensor_msgs/msg/JointState \\"
echo "   '{name: [joint_arm_l0], position: [0.1]}'"
echo ""
echo "🐛 Troubleshooting:"
echo "  • If no GUI window: Check if joint_state_publisher_gui is installed"
echo "  • If sliders don't move robot: Check /joint_states topic is publishing"
echo "  • If robot not visible: Check Fixed Frame in RViz is 'base_link'"
echo ""

# Create a test joint movement script
cat > /tmp/test_joints.py << 'EOF'
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time
import math

class JointTester(Node):
    def __init__(self):
        super().__init__('joint_movement_tester')
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.1, self.publish_joints)
        self.start_time = time.time()
        
    def publish_joints(self):
        elapsed = time.time() - self.start_time
        
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # Animate the robot
        lift_pos = 0.5 + 0.3 * math.sin(elapsed * 0.5)  # Oscillate lift
        arm_pos = 0.05 + 0.03 * math.sin(elapsed * 0.7)  # Oscillate arm extension
        wrist_pos = 0.5 * math.sin(elapsed * 1.0)  # Rotate wrist
        
        msg.name = [
            'joint_lift',
            'joint_arm_l0', 'joint_arm_l1', 'joint_arm_l2', 'joint_arm_l3',
            'joint_wrist_yaw',
            'joint_head_pan'
        ]
        
        msg.position = [
            lift_pos,
            arm_pos, arm_pos*0.8, arm_pos*0.6, arm_pos*0.4,
            wrist_pos,
            wrist_pos * 0.5
        ]
        
        self.publisher.publish(msg)

def main():
    rclpy.init()
    tester = JointTester()
    try:
        rclpy.spin(tester)
    except KeyboardInterrupt:
        pass
    finally:
        tester.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
EOF

echo "🎪 To test automatic joint movement, run in another terminal:"
echo "   python3 /tmp/test_joints.py"
echo ""
echo "Press ENTER to stop..."
read

# Cleanup
kill $RSP_PID $JSP_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true

echo "✅ Stretch control system stopped!"
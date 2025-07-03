#!/bin/bash

echo "🔍 Testing RViz Object Visibility"
echo "================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true
sleep 2

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🚀 Starting robot state publisher..."

# Create launch file
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

    # Only robot state publisher
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

echo "🎯 Publishing test objects..."

# Simple test object publisher
python3 -c "
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import MarkerArray, Marker
import time

class TestObjectPublisher(Node):
    def __init__(self):
        super().__init__('test_object_publisher')
        self.marker_pub = self.create_publisher(MarkerArray, '/test_objects', 10)
        self.timer = self.create_timer(1.0, self.publish_objects)
        
    def create_marker(self, id, x, y, z, sx, sy, sz, r, g, b, marker_type=Marker.CUBE):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'test_objects'
        marker.id = id
        marker.type = marker_type
        marker.action = Marker.ADD
        marker.lifetime.sec = 0  # Persistent
        
        marker.pose.position.x = float(x)
        marker.pose.position.y = float(y)
        marker.pose.position.z = float(z)
        marker.pose.orientation.w = 1.0
        
        marker.scale.x = float(sx)
        marker.scale.y = float(sy)
        marker.scale.z = float(sz)
        
        marker.color.r = float(r)
        marker.color.g = float(g)
        marker.color.b = float(b)
        marker.color.a = 1.0
        
        return marker

    def publish_objects(self):
        markers = MarkerArray()
        
        # Big red cube (should be very visible)
        markers.markers.append(
            self.create_marker(1, 2.0, 0.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0, Marker.CUBE)
        )
        
        # Green sphere
        markers.markers.append(
            self.create_marker(2, 1.0, 1.0, 0.3, 0.3, 0.3, 0.3, 0.0, 1.0, 0.0, Marker.SPHERE)
        )
        
        # Blue cylinder
        markers.markers.append(
            self.create_marker(3, 1.0, -1.0, 0.25, 0.2, 0.2, 0.5, 0.0, 0.0, 1.0, Marker.CYLINDER)
        )
        
        # Yellow arrow pointing up
        markers.markers.append(
            self.create_marker(4, 0.5, 0.5, 1.0, 0.1, 0.1, 0.5, 1.0, 1.0, 0.0, Marker.ARROW)
        )
        
        self.marker_pub.publish(markers)
        self.get_logger().info('Published test objects')

def main():
    rclpy.init()
    node = TestObjectPublisher()
    try:
        rclpy.spin_once(node, timeout_sec=3.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
" &

MARKER_PID=$!

sleep 2

echo "🎯 Starting RViz with simple test config..."

# Simple RViz config to test objects
cat > /tmp/test_objects.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.5
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
      Name: Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Test_Objects
      Topic:
        Value: /test_objects
      Value: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 4
      Focal Point:
        X: 1
        Y: 0
        Z: 0.5
      Name: Current View
      Pitch: 0.3
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

rviz2 -d /tmp/test_objects.rviz &
RVIZ_PID=$!

sleep 4

echo ""
echo "🔍 Object Visibility Test"
echo "========================="
echo ""
echo "✅ **What You Should See in RViz:**"
echo "   🤖 **Stretch Robot** (exact URDF model)"
echo "   🔴 **Big Red Cube** (2m in front of robot)"
echo "   🟢 **Green Sphere** (1m front-right)"
echo "   🔵 **Blue Cylinder** (1m front-left)"
echo "   🟡 **Yellow Arrow** (pointing up)"
echo ""
echo "🔧 **If You Don't See Objects:**"
echo "   1. Check 'Test_Objects' is enabled (✓) in Displays panel"
echo "   2. Expand 'Test_Objects' to see individual markers"
echo "   3. Look for red error messages in Displays panel"
echo "   4. Try zooming out with mouse scroll wheel"
echo "   5. Check Fixed Frame is set to 'base_link'"
echo ""
echo "📊 **In Terminal - Topic Check:**"
echo "   Run: ros2 topic echo /test_objects --once"
echo "   This should show marker data"
echo ""
echo "Press ENTER when you've checked visibility..."
read

# Cleanup
kill $ROBOT_PID $MARKER_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher python3 2>/dev/null || true

echo "✅ Test completed!"
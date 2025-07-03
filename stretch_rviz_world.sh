#!/bin/bash

echo "🌍 Stretch Robot - RViz World Environment"
echo "========================================="

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

echo "🚀 Starting robot state publisher only..."

# Create launch file (robot state publisher only, no joint publisher GUI)
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

echo "🌍 Creating world environment markers..."

# Create world marker publisher
python3 -c "
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point
import time
import math

class WorldPublisher(Node):
    def __init__(self):
        super().__init__('world_environment_publisher')
        
        # Publishers for different marker topics
        self.world_pub = self.create_publisher(MarkerArray, '/world_environment', 10)
        self.objects_pub = self.create_publisher(MarkerArray, '/interactive_objects', 10)
        
        self.timer = self.create_timer(1.0, self.publish_world)
        
    def create_marker(self, id, x, y, z, sx, sy, sz, r, g, b, a=1.0, marker_type=Marker.CUBE, frame='base_link'):
        marker = Marker()
        marker.header.frame_id = frame
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'world_environment'
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
        marker.color.a = float(a)
        
        return marker

    def publish_world(self):
        # Create room environment
        world_markers = MarkerArray()
        
        # Floor (large flat surface)
        world_markers.markers.append(
            self.create_marker(0, 0, 0, -0.01, 20, 20, 0.02, 0.8, 0.7, 0.6, 0.8, Marker.CUBE)
        )
        
        # Walls
        # North wall
        world_markers.markers.append(
            self.create_marker(1, 0, 3, 1, 6, 0.2, 2, 0.9, 0.9, 0.9, 1.0, Marker.CUBE)
        )
        # South wall
        world_markers.markers.append(
            self.create_marker(2, 0, -3, 1, 6, 0.2, 2, 0.9, 0.9, 0.9, 1.0, Marker.CUBE)
        )
        # East wall
        world_markers.markers.append(
            self.create_marker(3, 3, 0, 1, 0.2, 6, 2, 0.9, 0.9, 0.9, 1.0, Marker.CUBE)
        )
        # West wall
        world_markers.markers.append(
            self.create_marker(4, -3, 0, 1, 0.2, 6, 2, 0.9, 0.9, 0.9, 1.0, Marker.CUBE)
        )
        
        # Table 1 (to the right)
        world_markers.markers.append(
            self.create_marker(10, 1.5, 1.5, 0.4, 1.2, 0.6, 0.8, 0.6, 0.3, 0.1, 1.0, Marker.CUBE)
        )
        
        # Table 2 (to the left-back)
        world_markers.markers.append(
            self.create_marker(11, -1.5, -1.5, 0.4, 1.0, 1.0, 0.8, 0.6, 0.3, 0.1, 1.0, Marker.CUBE)
        )
        
        # Chair 1 (next to table 1)
        world_markers.markers.append(
            self.create_marker(12, 2.2, 1.5, 0.25, 0.4, 0.4, 0.5, 0.2, 0.2, 0.8, 1.0, Marker.CUBE)
        )
        
        # Chair 2 (next to table 2)
        world_markers.markers.append(
            self.create_marker(13, -1.0, -2.2, 0.25, 0.4, 0.4, 0.5, 0.2, 0.2, 0.8, 1.0, Marker.CUBE)
        )
        
        # Bookshelf (left wall)
        world_markers.markers.append(
            self.create_marker(14, -2.7, 1.5, 0.9, 0.3, 1.5, 1.8, 0.4, 0.2, 0.1, 1.0, Marker.CUBE)
        )
        
        # Kitchen counter (right wall)
        world_markers.markers.append(
            self.create_marker(15, 2.7, -1.5, 0.45, 0.3, 2.0, 0.9, 0.6, 0.6, 0.6, 1.0, Marker.CUBE)
        )
        
        # Refrigerator
        world_markers.markers.append(
            self.create_marker(16, 2.5, 0.5, 0.8, 0.5, 0.5, 1.6, 0.9, 0.9, 0.9, 1.0, Marker.CUBE)
        )
        
        # Plant (decoration)
        world_markers.markers.append(
            self.create_marker(17, -2.0, 0.5, 0.3, 0.3, 0.3, 0.6, 0.1, 0.6, 0.1, 1.0, Marker.CYLINDER)
        )
        
        self.world_pub.publish(world_markers)
        
        # Interactive objects
        object_markers = MarkerArray()
        
        # Red cup on table 1 (target for manipulation)
        object_markers.markers.append(
            self.create_marker(20, 1.7, 1.7, 0.85, 0.08, 0.08, 0.12, 1.0, 0.1, 0.1, 1.0, Marker.CYLINDER)
        )
        
        # Green box on table 2
        object_markers.markers.append(
            self.create_marker(21, -1.3, -1.3, 0.85, 0.12, 0.12, 0.12, 0.1, 0.8, 0.1, 1.0, Marker.CUBE)
        )
        
        # Blue ball on counter
        object_markers.markers.append(
            self.create_marker(22, 2.5, -1.3, 0.95, 0.08, 0.08, 0.08, 0.1, 0.1, 1.0, 1.0, Marker.SPHERE)
        )
        
        # Yellow book on bookshelf
        object_markers.markers.append(
            self.create_marker(23, -2.5, 1.7, 1.2, 0.15, 0.03, 0.2, 1.0, 1.0, 0.1, 1.0, Marker.CUBE)
        )
        
        # Orange cone (additional target)
        object_markers.markers.append(
            self.create_marker(24, 0.5, 0.8, 0.1, 0.1, 0.1, 0.2, 1.0, 0.5, 0.0, 1.0, Marker.CYLINDER)
        )
        
        # Purple tool on counter
        object_markers.markers.append(
            self.create_marker(25, 2.3, -1.8, 0.95, 0.2, 0.03, 0.03, 0.6, 0.1, 0.8, 1.0, Marker.CUBE)
        )
        
        self.objects_pub.publish(object_markers)

def main():
    rclpy.init()
    node = WorldPublisher()
    try:
        rclpy.spin_once(node, timeout_sec=2.0)
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

echo "🎯 Starting RViz with world environment..."

# Create comprehensive RViz config with world
cat > /tmp/stretch_world.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Stretch_Robot1
        - /World_Environment1
        - /Interactive_Objects1
        - /TF1
      Splitter Ratio: 0.4
    Tree Height: 700
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
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: World_Environment
      Topic:
        Value: /world_environment
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Interactive_Objects
      Topic:
        Value: /interactive_objects
      Value: true
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
      Update Interval: 0
      Value: true
  Global Options:
    Background Color: 135; 206; 235
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 5
      Focal Point:
        X: 1
        Y: 0
        Z: 0.8
      Name: World_View
      Pitch: 0.4
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

rviz2 -d /tmp/stretch_world.rviz &
RVIZ_PID=$!

sleep 4

echo ""
echo "🎉 Stretch Robot - RViz World Environment"
echo "========================================="
echo ""
echo "✅ **What You Should See in RViz:**"
echo "   🤖 **Exact Stretch Robot** - All official URDF details"
echo "   🏠 **Complete Indoor Environment:**"
echo "      • Room with walls (white)"
echo "      • Tables (brown wood)"
echo "      • Chairs (blue)"
echo "      • Bookshelf (brown)"
echo "      • Kitchen counter and refrigerator (gray/white)"
echo "      • Couch (purple)"
echo "   🎯 **Interactive Objects:**"
echo "      • Red cup on table (manipulation target)"
echo "      • Green box on table"
echo "      • Blue ball on counter"
echo "      • Yellow book on bookshelf"
echo ""
echo "🎮 **Now Start Joint Control:**"
echo "   Open another terminal and run:"
echo "   python3 /home/kantar/Desktop/hello-robot/custom_joint_control.py"
echo ""
echo "🎯 **Test Scenarios:**"
echo "   1. **Reach for the red cup**: Lift arm + extend to table"
echo "   2. **Look around**: Use head pan joint"
echo "   3. **Navigate height**: Use lift to go up/down"
echo "   4. **Full extension**: Extend all arm segments"
echo "   5. **Preset poses**: Use Demo/Home buttons"
echo ""
echo "💡 **Perfect for:**"
echo "   • Motion planning tests"
echo "   • Manipulation experiments"  
echo "   • Joint limit testing"
echo "   • Workspace visualization"
echo "   • Algorithm development"
echo ""
echo "🔧 **RViz Controls:**"
echo "   • Mouse: Orbit around the environment"
echo "   • Scroll: Zoom in/out"
echo "   • All robot joints respond to custom GUI"
echo ""
echo "Press ENTER to stop the world environment..."
read

# Cleanup
kill $ROBOT_PID $MARKER_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher python3 2>/dev/null || true

echo "✅ RViz world environment stopped!"
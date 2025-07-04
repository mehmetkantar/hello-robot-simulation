#!/bin/bash

echo "🔍 Simple RViz Test - Basic Shapes"
echo "=================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui 2>/dev/null || true
sleep 2

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash

# Create a very simple robot with just basic shapes
cat > /tmp/simple_shapes.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="simple_test">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
  </link>
  
  <link name="arm_link">
    <visual>
      <origin xyz="0.3 0 0"/>
      <geometry>
        <box size="0.6 0.05 0.05"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="arm_joint" type="revolute">
    <parent link="base_link"/>
    <child link="arm_link"/>
    <origin xyz="0.25 0 0.1"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="1"/>
  </joint>
</robot>
EOF

echo "🚀 Starting simple robot test..."
ros2 run robot_state_publisher robot_state_publisher /tmp/simple_shapes.urdf &
RSP_PID=$!

sleep 2

# Create minimal RViz config
cat > /tmp/simple_test.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.5
      Cell Size: 1
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
      Name: RobotModel
      Value: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 2
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Name: Current View
      Pitch: 0.5
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF

echo "🎯 Starting RViz with simple shapes..."
rviz2 -d /tmp/simple_test.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "🔍 What you should see in RViz:"
echo "  🔵 BLUE BOX (base_link)"
echo "  🔴 RED BAR (arm_link)" 
echo ""
echo "If you see these shapes, RViz is working!"
echo "If not, there might be a graphics/VM issue."
echo ""
echo "Press ENTER to finish..."
read

# Cleanup
kill $RSP_PID $RVIZ_PID 2>/dev/null
echo "✅ Simple test completed!"
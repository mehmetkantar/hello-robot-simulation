#!/bin/bash

echo "🤖 Working Stretch Robot Control"
echo "================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher python3 2>/dev/null || true
sleep 2

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🚀 Starting robot state publisher via launch file..."

# Launch robot state publisher
ros2 launch stretch_moveit_config simple_robot.launch.py &
LAUNCH_PID=$!

echo "✅ Launch started (PID: $LAUNCH_PID)"
sleep 4

# Check if the system is working
echo "🔍 Checking system status..."

# Check topics
echo -n "📡 /robot_description topic: "
if timeout 5s ros2 topic echo /robot_description --once >/dev/null 2>&1; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi

echo -n "📡 TF base_link frame: "
if timeout 5s ros2 run tf2_ros tf2_echo base_link base_link >/dev/null 2>&1; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi

# Start RViz with simple config
echo "🎯 Starting RViz..."

cat > /tmp/working_stretch.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Robot Model1
      Splitter Ratio: 0.5
    Tree Height: 500
Visualization Manager:
  Class: ""
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
      Collision Enabled: false
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Robot Model
      Value: true
      Visual Enabled: true
  Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 2.5
      Focal Point:
        X: 0.5
        Y: 0
        Z: 0.6
      Name: Current View
      Pitch: 0.4
      Yaw: 0.8
    Saved: ~
EOF

rviz2 -d /tmp/working_stretch.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "✅ **System Ready!**"
echo "==================="
echo ""
echo "🎮 **Start the joint controller in another terminal:**"
echo ""
echo "   python3 /home/kantar/Desktop/hello-robot/simple_robot_control.py"
echo ""
echo "💡 **Expected behavior:**"
echo "   • Robot should be visible in RViz"
echo "   • No 'Fixed Frame' errors"
echo "   • Robot moves when you move sliders"
echo ""

# Wait for user
echo "Press ENTER to stop..."
read

# Cleanup
echo "🧹 Cleaning up..."
kill $LAUNCH_PID $RVIZ_PID 2>/dev/null || true
killall -9 rviz2 robot_state_publisher python3 ros2 2>/dev/null || true

echo "✅ System stopped!"
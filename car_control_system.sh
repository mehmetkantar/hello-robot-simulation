#!/bin/bash

echo "🚗 Stretch Robot Car Control System"
echo "===================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher python3 2>/dev/null || true
sleep 2

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🚀 Starting robot state publisher..."

# Launch robot state publisher
ros2 launch stretch_moveit_config simple_robot.launch.py &
LAUNCH_PID=$!

sleep 4

# Check system status
echo "🔍 Checking system status..."

if ! kill -0 $LAUNCH_PID 2>/dev/null; then
    echo "❌ Robot state publisher failed to start!"
    exit 1
fi

echo -n "📡 /robot_description topic: "
if timeout 3s ros2 topic echo /robot_description --once >/dev/null 2>&1; then
    echo "✅ Available"
else
    echo "❌ Not available"
fi

# Create RViz config with world frame
echo "🎯 Starting RViz with car control config..."

cat > /tmp/car_control.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Robot Model1
        - /TF1
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
    - Class: rviz_default_plugins/TF
      Enabled: true
      Frame Timeout: 15
      Frames:
        All Enabled: false
        base_link:
          Value: true
        world:
          Value: true
      Marker Alpha: 1
      Marker Scale: 0.3
      Name: TF
      Show Arrows: true
      Show Axes: true
      Show Names: true
      Tree:
        world:
          base_link:
            {}
      Update Interval: 0
      Value: true
  Enabled: true
  Global Options:
    Background Color: 20; 20; 20
    Fixed Frame: world
    Frame Rate: 30
  Name: root
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 4.0
      Focal Point:
        X: 0.0
        Y: 0.0
        Z: 0.5
      Name: Car View
      Pitch: 0.6
      Yaw: 1.57
    Saved: ~
EOF

rviz2 -d /tmp/car_control.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "✅ **Car Control System Ready!**"
echo "================================="
echo ""
echo "🚗 **Start the car controller:**"
echo ""
echo "   python3 /home/kantar/Desktop/hello-robot/robot_car_control.py"
echo ""
echo "💡 **Features:**"
echo "   • 🚗 Car-like driving with odometry"
echo "   • 📍 Real-time position tracking"
echo "   • 🎮 Intuitive driving controls"
echo "   • 🦾 Full joint control"
echo "   • 🔄 Robot actually moves in RViz!"
echo ""
echo "🎯 **Usage:**"
echo "   • Use Drive tab for car controls"
echo "   • Adjust speed with sliders"
echo "   • Watch robot move in RViz"
echo "   • Use Joints tab for arm control"
echo ""

# Wait for user input
echo "Press ENTER to stop the system..."
read

# Cleanup
echo "🧹 Cleaning up..."
kill $LAUNCH_PID $RVIZ_PID 2>/dev/null || true
killall -9 rviz2 robot_state_publisher python3 2>/dev/null || true

echo "✅ Car control system stopped!"
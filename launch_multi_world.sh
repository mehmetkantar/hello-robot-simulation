#!/bin/bash

echo "🌍 Multi-World Stretch Robot Control System"
echo "============================================"

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

# Create enhanced RViz config with environment markers
echo "🎯 Starting RViz with multi-world support..."

cat > /tmp/multi_world.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Robot Model1
        - /Environment1
        - /TF1
      Splitter Ratio: 0.4
    Tree Height: 500
Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.3
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 120; 120; 120
      Enabled: true
      Line Style:
        Line Width: 0.03
        Value: Lines
      Name: Grid
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
        Expand Joint Details: false
        Expand Link Details: false
        Expand Tree: false
        Link Tree Style: Links in Alphabetic Order
      Mass Properties:
        Inertia: false
        Mass: false
      Name: Robot Model
      TF Prefix: ""
      Update Interval: 0
      Value: true
      Visual Enabled: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Marker Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /environment_markers
      Name: Environment
      Namespaces:
        environment: true
      Queue Size: 100
      Value: true
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
      Show Arrows: false
      Show Axes: true
      Show Names: false
      Tree:
        world:
          base_link:
            {}
      Update Interval: 0
      Value: true
  Enabled: true
  Global Options:
    Background Color: 25; 25; 35
    Fixed Frame: world
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
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 8.0
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.06
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0.0
        Y: 0.0
        Z: 0.5
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05
      Invert Z Axis: false
      Name: World View
      Near Clip Distance: 0.01
      Pitch: 0.8
      Target Frame: <Fixed Frame>
      Yaw: 2.3
    Saved: ~
EOF

rviz2 -d /tmp/multi_world.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "✅ **Multi-World System Ready!**"
echo "================================="
echo ""
echo "🌍 **Available Worlds:**"
echo "   🌫️  Empty World - Open space for basic testing"
echo "   🏢  Office - Navigate through office furniture"
echo "   📦  Warehouse - Maneuver around storage racks"
echo "   🏠  Home - Explore domestic environment"
echo "   🧩  Maze - Challenge navigation skills"
echo "   🌳  Garden - Peaceful outdoor environment"
echo "   🏭  Factory - Industrial setting with machines"
echo ""
echo "🚗 **Start the multi-world controller:**"
echo ""
echo "   python3 /home/kantar/Desktop/hello-robot/multi_world_control.py"
echo ""
echo "🎮 **Features:**"
echo "   • Switch between 7 different environments"
echo "   • World-specific demo drives"
echo "   • Detailed world information and missions"
echo "   • Real-time environment visualization"
echo "   • Car-like driving with odometry"
echo "   • Full robot arm and joint control"
echo ""
echo "💡 **How to use:**"
echo "   1. Select a world from the dropdown or quick buttons"
echo "   2. Read the world info and suggested missions"
echo "   3. Use the Drive tab for car-like movement"
echo "   4. Try the world-specific demo drives"
echo "   5. Watch the robot navigate in RViz!"
echo ""

# Wait for user input
echo "Press ENTER to stop the system..."
read

# Cleanup
echo "🧹 Cleaning up..."
kill $LAUNCH_PID $RVIZ_PID 2>/dev/null || true
killall -9 rviz2 robot_state_publisher python3 2>/dev/null || true

echo "✅ Multi-world system stopped!"
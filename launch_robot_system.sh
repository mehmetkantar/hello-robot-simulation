#!/bin/bash

echo "🤖 Launching Complete Stretch Robot System"
echo "==========================================="

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

echo "🔍 Checking available URDF files..."
ls -la src/stretch_ros2/stretch_description/stretch_description_*.urdf

# Use the working URDF file
URDF_FILE="src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF file not found: $URDF_FILE"
    exit 1
fi

echo "✅ Using URDF file: $URDF_FILE"

# Check if URDF file has content
if [ ! -s "$URDF_FILE" ]; then
    echo "❌ URDF file is empty!"
    exit 1
fi

echo "✅ URDF file has content ($(wc -l < "$URDF_FILE") lines)"

echo "🚀 Starting robot_state_publisher..."

# Start robot_state_publisher with explicit URDF loading
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(cat $URDF_FILE)" &
RSP_PID=$!

echo "✅ Robot state publisher started (PID: $RSP_PID)"

sleep 3

# Check if robot_state_publisher is running
if ! kill -0 $RSP_PID 2>/dev/null; then
    echo "❌ Robot state publisher failed to start!"
    exit 1
fi

echo "🎯 Starting RViz..."

# Create simple RViz config
cat > /tmp/stretch_simple.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Robot Model1
      Splitter Ratio: 0.5
    Tree Height: 746
Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Line Style:
        Line Width: 0.029999999329447746
        Value: Lines
      Name: Grid
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
        Z: 0
      Plane: XY
      Plane Cell Count: 10
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
  Value: true
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
        X: 0.5
        Y: 0
        Z: 0.6
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.01
      Pitch: 0.4
      Target Frame: <Fixed Frame>
      Yaw: 0.8
    Saved: ~
EOF

# Start RViz
rviz2 -d /tmp/stretch_simple.rviz &
RVIZ_PID=$!

sleep 3

echo ""
echo "✅ **System Status Check**"
echo "========================="

# Check if robot_description topic exists
echo -n "🔍 Checking /robot_description topic: "
if ros2 topic list | grep -q "/robot_description"; then
    echo "✅ Found"
else
    echo "❌ Missing"
fi

# Check if joint_states topic exists
echo -n "🔍 Checking /joint_states topic: "
if ros2 topic list | grep -q "/joint_states"; then
    echo "✅ Found"
else
    echo "❌ Missing"
fi

# Check TF frames
echo -n "🔍 Checking TF frames: "
TF_COUNT=$(ros2 run tf2_tools view_frames.py 2>/dev/null | grep -c "^Node" || echo "0")
if [ "$TF_COUNT" -gt "0" ]; then
    echo "✅ Found $TF_COUNT frames"
else
    echo "❌ No frames found"
fi

echo ""
echo "🎮 **Now start the joint controller:**"
echo ""
echo "   python3 /home/kantar/Desktop/hello-robot/simple_robot_control.py"
echo ""
echo "💡 **What you should see:**"
echo "   • Robot model visible in RViz"
echo "   • No 'Fixed Frame' errors"
echo "   • Robot moves when you adjust sliders"
echo ""

# Wait for user input
echo "Press ENTER to stop the system..."
read

# Cleanup
echo "🧹 Cleaning up..."
kill $RSP_PID $RVIZ_PID 2>/dev/null || true
killall -9 rviz2 robot_state_publisher python3 2>/dev/null || true

echo "✅ System stopped!"
#!/bin/bash

echo "🔧 Fixing Robot Visualization in RViz"
echo "====================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 gazebo gzserver gzclient 2>/dev/null || true
sleep 2

echo "🔍 Diagnosing RViz robot display issues..."

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Check if robot_description is being published
echo "🧪 Test 1: Checking robot_description topic..."
timeout 5s ros2 topic list | grep robot_description
if [ $? -eq 0 ]; then
    echo "✅ robot_description topic exists"
else
    echo "❌ robot_description topic not found"
    echo "🔄 Starting robot_state_publisher..."
    
    # Start robot state publisher with a known good URDF
    URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
    
    if [ -f "$URDF_FILE" ]; then
        echo "📁 Using URDF: $URDF_FILE"
        ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat $URDF_FILE)" &
        RSP_PID=$!
        sleep 3
    else
        echo "❌ URDF file not found: $URDF_FILE"
        exit 1
    fi
fi

echo ""
echo "🧪 Test 2: Starting RViz with robot visualization..."

# Create a minimal RViz config for robot display
cat > /tmp/robot_display.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /RobotModel1
      Splitter Ratio: 0.5
    Tree Height: 400
Visualization Manager:
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
      Description File: ""
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
      Name: RobotModel
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
  Transformation:
    Current:
      Class: rviz_default_plugins/TF
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 2.5
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.05999999865889549
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05000000074505806
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.009999999776482582
      Pitch: 0.4603982269763947
      Target Frame: <Fixed Frame>
      Value: Orbit (rviz_default_plugins)
      Yaw: 0.785398006439209
    Saved: ~
EOF

echo "🚀 Starting RViz with robot display configuration..."
rviz2 -d /tmp/robot_display.rviz &
RVIZ_PID=$!

sleep 5

echo ""
echo "🔍 Diagnostic Information:"
echo "=========================="

# Check if robot_description is being published
echo "📊 Robot description topic:"
timeout 3s ros2 topic echo /robot_description --once | head -3

echo ""
echo "📊 Available topics:"
ros2 topic list | grep -E "(robot|description|joint|tf)"

echo ""
echo "📊 TF frames:"
timeout 3s ros2 run tf2_tools view_frames.py 2>/dev/null || echo "No TF frames available"

echo ""
echo "🎯 RViz Troubleshooting:"
echo "========================"
echo "If you still don't see the robot in RViz:"
echo ""
echo "1. 🔍 Check RViz Displays panel:"
echo "   - Expand 'RobotModel' in the left panel"
echo "   - Look for error messages (red text)"
echo "   - Check if 'Description Topic' shows /robot_description"
echo ""
echo "2. 🎯 Check Fixed Frame:"
echo "   - In Global Options, try setting Fixed Frame to:"
echo "     • base_link"
echo "     • world" 
echo "     • odom"
echo ""
echo "3. 🔴 Look for red/error indicators:"
echo "   - Red status means the model failed to load"
echo "   - Check for missing mesh files or URDF errors"
echo ""
echo "4. 🔄 Reset view:"
echo "   - Use mouse to zoom out (scroll wheel)"
echo "   - Right-click and drag to rotate"
echo "   - Try Views → Current → Reset"
echo ""
echo "Press ENTER to stop RViz and continue..."
read

# Clean up
kill $RVIZ_PID $RSP_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher 2>/dev/null || true

echo "🏁 RViz test completed!"
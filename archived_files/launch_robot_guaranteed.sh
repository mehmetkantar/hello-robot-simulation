#!/bin/bash

echo "🚀 GUARANTEED Robot Visibility Launch"
echo "====================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill ALL existing processes thoroughly
echo "🧹 Cleaning up existing processes..."
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
pkill -f gazebo 2>/dev/null || true
pkill -f rviz 2>/dev/null || true
sleep 5

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Verify critical files exist
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
WORLD_FILE="/home/kantar/Desktop/hello-robot/worlds/simple_robot_world.world"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ CRITICAL: URDF file missing: $URDF_FILE"
    exit 1
fi

if [ ! -f "$WORLD_FILE" ]; then
    echo "❌ CRITICAL: World file missing: $WORLD_FILE"
    exit 1
fi

echo "✅ All files verified"

# Create a minimal world without static robot for dynamic spawning
CLEAN_WORLD="/tmp/robot_world_clean.world"
cat > "$CLEAN_WORLD" << 'EOF'
<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="robot_world">
    
    <!-- Physics -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    
    <!-- Sun -->
    <light type="directional" name="sun">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>20 20</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>20 20</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

    <!-- Simple table for reference -->
    <model name="table">
      <static>true</static>
      <pose>2 0 0 0 0 0</pose>
      <link name="table_top">
        <pose>0 0 0.8 0 0 0</pose>
        <collision name="collision">
          <geometry><box><size>1.0 0.6 0.05</size></box></geometry>
        </collision>
        <visual name="visual">
          <geometry><box><size>1.0 0.6 0.05</size></box></geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Wood</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

  </world>
</sdf>
EOF

echo "🌍 STEP 1: Starting Gazebo..."
timeout 30s ros2 launch gazebo_ros gazebo.launch.py world:="$CLEAN_WORLD" verbose:=false &
GAZEBO_PID=$!

echo "⏳ Waiting for Gazebo to fully start..."
sleep 15

# Verify Gazebo is responding
if ! pgrep -f gzserver > /dev/null; then
    echo "❌ CRITICAL: Gazebo server failed to start"
    exit 1
fi

echo "✅ Gazebo started successfully"

echo "🤖 STEP 2: Starting Robot State Publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat "$URDF_FILE")" &
RSP_PID=$!

echo "⏳ Waiting for robot description to be published..."
sleep 8

# Verify robot_description topic exists
timeout 10s bash -c 'while ! ros2 topic list | grep -q "/robot_description"; do sleep 1; done'

if ! ros2 topic list | grep -q "/robot_description"; then
    echo "❌ CRITICAL: /robot_description topic not available"
    kill $GAZEBO_PID $RSP_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Robot description published successfully"

echo "🎯 STEP 3: Spawning robot..."
ros2 run gazebo_ros spawn_entity.py \
    -topic /robot_description \
    -entity stretch_robot \
    -x 0.0 \
    -y 0.0 \
    -z 0.1 \
    -timeout 30.0 &
SPAWN_PID=$!

echo "⏳ Waiting for robot spawn to complete..."
sleep 10

echo "🔍 STEP 4: Verifying robot presence..."

# Check if robot was spawned successfully
if ros2 topic list | grep -q "/joint_states"; then
    echo "✅ Robot spawned - joint_states topic available"
else
    echo "⚠️ Robot spawn may have failed - no joint_states topic"
fi

echo "📺 STEP 5: Starting RViz with proper config..."

# Create RViz config that shows the robot
RVIZ_CONFIG="/tmp/robot_display.rviz"
cat > "$RVIZ_CONFIG" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
  - Class: rviz_common/Views
    Name: Views

Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Name: Grid
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
      Name: RobotModel
      TF Prefix: ""
      Update Interval: 0
      Value: true
      Visual Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: base_link
    Frame Rate: 30
  Tools:
    - Class: rviz_default_plugins/MoveCamera
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3.0
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.06
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0
        Y: 0
        Z: 1
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.01
      Pitch: 0.3
      Target Frame: <Fixed Frame>
      Yaw: 0.8
      Value: Orbit (rviz_default_plugins)
EOF

rviz2 -d "$RVIZ_CONFIG" &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎉 ROBOT LAUNCH COMPLETE!"
echo "=========================="
echo ""
echo "✅ What you should see:"
echo "   🌍 Gazebo: Simple world with table"
echo "   🤖 Robot: Full Stretch robot at (0, 0, 0.1)"
echo "   📺 RViz: Robot model displayed"
echo ""
echo "🔍 Verification commands:"
echo "   ros2 topic list | grep robot"
echo "   ros2 topic echo /joint_states --once"
echo "   ros2 run tf2_tools view_frames.py"
echo ""
echo "🎮 Start GUI control:"
echo "   python3 /home/kantar/Desktop/hello-robot/stable_robot_control.py"
echo ""
echo "Press Ctrl+C to stop everything."

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all processes..."
    kill $GAZEBO_PID $RSP_PID $SPAWN_PID $RVIZ_PID 2>/dev/null || true
    killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
    rm -f "$CLEAN_WORLD" "$RVIZ_CONFIG"
    exit 0
}

trap cleanup SIGINT SIGTERM
wait $GAZEBO_PID
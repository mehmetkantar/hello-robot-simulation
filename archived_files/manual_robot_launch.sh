#!/bin/bash

echo "🔧 Manual Step-by-Step Robot Launch"
echo "===================================="

# Kill everything first
echo "Step 0: Killing all existing processes..."
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 gazebo 2>/dev/null || true
pkill -f ros2 2>/dev/null || true
sleep 3

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "✅ ROS2 environment sourced"

# Check if files exist
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF file not found: $URDF_FILE"
    echo "Available files:"
    ls -la /home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/*.urdf
    exit 1
fi

echo "✅ URDF file found: $URDF_FILE"

# Create the simplest possible world
SIMPLE_WORLD="/tmp/minimal_world.world"
cat > "$SIMPLE_WORLD" << 'EOF'
<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="minimal_world">
    <light type="directional" name="sun">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
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
  </world>
</sdf>
EOF

echo "✅ Created minimal world file"

# Step 1: Start Gazebo manually
echo ""
echo "🌍 Step 1: Starting Gazebo..."
echo "Starting Gazebo server..."
gzserver "$SIMPLE_WORLD" --verbose &
GAZEBO_PID=$!

echo "Waiting 10 seconds for Gazebo to start..."
sleep 10

# Check if Gazebo started
if ! pgrep -f gzserver > /dev/null; then
    echo "❌ Gazebo server failed to start"
    exit 1
fi

echo "✅ Gazebo server running"

echo "Starting Gazebo client..."
gzclient &
GZCLIENT_PID=$!

sleep 5

echo "✅ Gazebo client should be visible now"

# Step 2: Start robot state publisher
echo ""
echo "🤖 Step 2: Starting Robot State Publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat "$URDF_FILE")" &
RSP_PID=$!

echo "Waiting 5 seconds for robot state publisher..."
sleep 5

echo "✅ Robot state publisher started"

# Step 3: Spawn robot
echo ""
echo "🎯 Step 3: Spawning robot..."
ros2 run gazebo_ros spawn_entity.py -topic /robot_description -entity stretch_robot -x 0 -y 0 -z 0.1 &
SPAWN_PID=$!

echo "Waiting 8 seconds for robot spawn..."
sleep 8

echo "✅ Robot spawn command completed"

# Step 4: Start RViz
echo ""
echo "📺 Step 4: Starting RViz..."
rviz2 &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎉 MANUAL LAUNCH COMPLETE!"
echo "=========================="
echo ""
echo "Manual verification:"
echo "1. Check if Gazebo window is open with ground plane"
echo "2. Look for robot in Gazebo at center (0, 0)"
echo "3. In RViz, add Robot Model display:"
echo "   - Click 'Add' button"
echo "   - Select 'RobotModel'"
echo "   - Set Topic to '/robot_description'"
echo ""
echo "If robot still not visible, run these commands in a NEW terminal:"
echo ""
echo "cd /home/kantar/Desktop/hello-robot/stretch_ws"
echo "source /opt/ros/humble/setup.bash"
echo "source install/setup.bash"
echo "ros2 topic list"
echo "ros2 topic echo /joint_states --once"
echo ""
echo "Press Enter to check status or Ctrl+C to stop everything..."

read -p ""

echo ""
echo "🔍 Status Check:"
echo "================"

# Quick status check
if pgrep -f gzserver > /dev/null; then
    echo "✅ Gazebo server: RUNNING"
else
    echo "❌ Gazebo server: NOT RUNNING"
fi

if pgrep -f robot_state_publisher > /dev/null; then
    echo "✅ Robot state publisher: RUNNING"
else
    echo "❌ Robot state publisher: NOT RUNNING"
fi

if pgrep -f rviz > /dev/null; then
    echo "✅ RViz: RUNNING"
else
    echo "❌ RViz: NOT RUNNING"
fi

echo ""
echo "Press Ctrl+C to stop everything or Enter to keep running..."
read -p ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all processes..."
    kill $GAZEBO_PID $GZCLIENT_PID $RSP_PID $SPAWN_PID $RVIZ_PID 2>/dev/null || true
    killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
    rm -f "$SIMPLE_WORLD"
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
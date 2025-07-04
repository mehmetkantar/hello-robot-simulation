#!/bin/bash

echo "🚀 Launching Stable Stretch Simulation"
echo "======================================"

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
sleep 2

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Set Gazebo resource path
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/worlds
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/stretch_urdf
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/stretch_ws/install/hello-robot-stretch-urdf/lib/python3.10/site-packages/stretch_urdf
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description

# Check if world file exists
WORLD_FILE="/home/kantar/Desktop/hello-robot/worlds/obstacle_room.world"
if [ ! -f "$WORLD_FILE" ]; then
    echo "❌ World file not found at $WORLD_FILE"
    echo "Available world files:"
    ls /home/kantar/Desktop/hello-robot/worlds/*.world
    exit 1
fi

# Launch Gazebo with the world
echo "🌍 Starting Gazebo server..."
gzserver "$WORLD_FILE" --verbose &
GAZEBO_PID=$!

# Wait for Gazebo to be fully up and its services available
echo "⏳ Waiting for Gazebo services..."
timeout 30s bash -c 'until ros2 topic list | grep -q /clock; do sleep 1; done'

if ! ros2 topic list | grep -q /clock; then
    echo "❌ Gazebo server not responding"
    exit 1
fi

echo "🖥️ Starting Gazebo client..."
gzclient &
GZCLIENT_PID=$!

# Start Robot State Publisher with direct URDF file
echo "🤖 Starting Robot State Publisher..."
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF file not found at $URDF_FILE"
    echo "Available URDF files:"
    ls /home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/*.urdf
    exit 1
fi

# Launch robot state publisher directly with URDF file
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat $URDF_FILE)" &
RSP_PID=$!

# Wait for /robot_description topic to be published
echo "⏳ Waiting for /robot_description topic..."
timeout 30s bash -c 'until ros2 topic list | grep -q /robot_description; do sleep 1; done'

if ! ros2 topic list | grep -q /robot_description; then
    echo "❌ /robot_description topic not available"
    exit 1
fi

# Wait for the /spawn_entity service to be available
echo "⏳ Waiting for /spawn_entity service..."
timeout 30s bash -c 'until ros2 service list | grep -q /spawn_entity; do sleep 1; done'

if ! ros2 service list | grep -q /spawn_entity; then
    echo "❌ /spawn_entity service not available"
    exit 1
fi

# Spawn the robot in a safe location
echo "🤖 Spawning robot at a safe location (-3, 3, 0.1)..."
ros2 run gazebo_ros spawn_entity.py -topic /robot_description -entity stretch -x -3.0 -y 3.0 -z 0.1 &
SPAWN_PID=$!

# Wait a bit for spawning to complete
sleep 3

# Launch RViz
echo "📺 Starting RViz..."
RVIZ_CONFIG="/home/kantar/Desktop/hello-robot/launch/obstacle_room.rviz"
if [ ! -f "$RVIZ_CONFIG" ]; then
    echo "⚠️ RViz config not found, using default"
    rviz2 &
else
    rviz2 -d "$RVIZ_CONFIG" &
fi
RVIZ_PID=$!

echo ""
echo "✅ Simulation is running!"
echo "   🌍 Gazebo: World with obstacles loaded"
echo "   🤖 Robot: Should be visible at (-3, 3, 0.1)"
echo "   📺 RViz: Robot visualization"
echo ""
echo "🎮 In a new terminal, run the controller:"
echo "   cd /home/kantar/Desktop/hello-robot"
echo "   python3 simple_robot_control.py"
echo ""
echo "🔍 To check if robot spawned successfully:"
echo "   ros2 topic echo /joint_states"
echo "   ros2 model list (in Gazebo)"
echo ""
echo "Press Ctrl+C in this terminal to stop everything."

# Wait for user to stop
wait $GAZEBO_PID

# Cleanup
kill $GZCLIENT_PID $RSP_PID $SPAWN_PID $RVIZ_PID 2>/dev/null || true

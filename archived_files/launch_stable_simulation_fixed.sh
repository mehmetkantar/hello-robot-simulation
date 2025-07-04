#!/bin/bash

echo "🚀 Launching Stable Stretch Simulation (Fixed Version)"
echo "====================================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill existing processes
killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
sleep 3

# Setup workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Set Gazebo resource path
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/worlds
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description

# Check if world file exists
WORLD_FILE="/home/kantar/Desktop/hello-robot/worlds/obstacle_room.world"
if [ ! -f "$WORLD_FILE" ]; then
    echo "❌ World file not found at $WORLD_FILE"
    exit 1
fi

# Check URDF file
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF file not found at $URDF_FILE"
    exit 1
fi

echo "✅ All files found, starting simulation..."

# Step 1: Launch Gazebo with ROS integration using ros2 launch
echo "🌍 Step 1: Starting Gazebo with ROS integration..."
ros2 launch gazebo_ros gazebo.launch.py world:="$WORLD_FILE" verbose:=true &
GAZEBO_PID=$!

# Wait for Gazebo to initialize
echo "⏳ Waiting for Gazebo to initialize..."
sleep 10

# Step 2: Start Robot State Publisher
echo "🤖 Step 2: Starting Robot State Publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat "$URDF_FILE")" &
RSP_PID=$!

# Wait for robot description to be published
echo "⏳ Waiting for robot description..."
sleep 5

# Step 3: Spawn the robot
echo "🎯 Step 3: Spawning robot at (-3, 3, 0.1)..."
ros2 run gazebo_ros spawn_entity.py -topic /robot_description -entity stretch -x -3.0 -y 3.0 -z 0.1 &
SPAWN_PID=$!

# Wait for spawn to complete
sleep 5

# Step 4: Launch RViz (optional)
echo "📺 Step 4: Starting RViz..."
rviz2 &
RVIZ_PID=$!

echo ""
echo "✅ Simulation launched successfully!"
echo ""
echo "🎮 You should see:"
echo "   1. Gazebo window with obstacle room"
echo "   2. Stretch robot at position (-3, 3, 0.1)"
echo "   3. RViz window for robot visualization"
echo ""
echo "🎮 To control the robot, run in a new terminal:"
echo "   cd /home/kantar/Desktop/hello-robot"
echo "   python3 simple_robot_control.py"
echo ""
echo "🔍 To verify robot is spawned:"
echo "   ros2 topic echo /joint_states"
echo ""
echo "Press Ctrl+C to stop everything."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping simulation..."
    kill $GAZEBO_PID $RSP_PID $SPAWN_PID $RVIZ_PID 2>/dev/null || true
    killall -9 rviz2 robot_state_publisher gzserver gzclient python3 2>/dev/null || true
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait $GAZEBO_PID
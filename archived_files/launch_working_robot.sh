#!/bin/bash

echo "🚀 Launching Working Robot Simulation"
echo "===================================="

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

# Check files
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
WORLD_FILE="/home/kantar/Desktop/hello-robot/worlds/simple_robot_world.world"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF not found: $URDF_FILE"
    exit 1
fi

if [ ! -f "$WORLD_FILE" ]; then
    echo "❌ World not found: $WORLD_FILE" 
    echo "Available worlds:"
    ls /home/kantar/Desktop/hello-robot/worlds/*.world
    exit 1
fi

echo "✅ Files found, starting simulation..."

# Use the world that we know works (has static robot) but replace it with dynamic spawn
# First, create a clean world without the static robot
CLEAN_WORLD="/tmp/clean_world.world"
cp "$WORLD_FILE" "$CLEAN_WORLD"

# Remove the static robot model from the world file
sed -i '/<!-- Simple robot -->/,/^  <\/world>$/{ /^  <\/world>$/!d; }' "$CLEAN_WORLD"
echo "  </world>" >> "$CLEAN_WORLD"
echo "</sdf>" >> "$CLEAN_WORLD"

echo "🌍 Starting Gazebo with clean world..."
ros2 launch gazebo_ros gazebo.launch.py world:="$CLEAN_WORLD" verbose:=false &
GAZEBO_PID=$!

echo "⏳ Waiting for Gazebo..."
sleep 8

echo "🤖 Starting robot state publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat "$URDF_FILE")" &
RSP_PID=$!

echo "⏳ Waiting for robot description..."
sleep 3

echo "🎯 Spawning robot at (-5, 4, 0.1)..."
ros2 run gazebo_ros spawn_entity.py -topic /robot_description -entity stretch -x -5.0 -y 4.0 -z 0.1 &
SPAWN_PID=$!

echo "⏳ Waiting for spawn..."
sleep 3

echo "📺 Starting RViz..."
rviz2 &
RVIZ_PID=$!

echo ""
echo "✅ SIMULATION READY!"
echo ""
echo "🎯 You should see:"
echo "   1. Gazebo: Room with walls, obstacles, table, glass"
echo "   2. Robot: Full Stretch robot at (-5, 4, 0.1)"
echo "   3. RViz: Robot visualization"
echo ""
echo "🎮 Control the robot with GUI:"
echo "   cd /home/kantar/Desktop/hello-robot"
echo "   python3 stable_robot_control.py"
echo ""
echo "Or use the enhanced GUI:"
echo "   python3 robot_car_control_stable.py"
echo ""
echo "Press Ctrl+C to stop."

# Cleanup function
cleanup() {
    echo "🛑 Stopping..."
    kill $GAZEBO_PID $RSP_PID $SPAWN_PID $RVIZ_PID 2>/dev/null || true
    rm -f "$CLEAN_WORLD"
    exit 0
}

trap cleanup SIGINT SIGTERM
wait $GAZEBO_PID
#!/bin/bash

echo "🎮 Force Gazebo UI - No Matter What!"
echo "==================================="
echo ""

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 gzserver gzclient rviz2 python3 joint_state_publisher_gui 2>/dev/null || true
sleep 3

# Try multiple graphics configurations to maximize compatibility
echo "🖥️  Trying maximum graphics compatibility..."

# Configuration 1: Force software rendering
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

# Configuration 2: X11 settings
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export DISPLAY=:0

# Configuration 3: Gazebo specific
export GAZEBO_IP=127.0.0.1
export GAZEBO_MASTER_URI=http://localhost:11345
export OGRE_RTShader_Write_Debug_Info=false

# Configuration 4: Disable problematic features
export __GL_SYNC_TO_VBLANK=0
export __GL_THREADED_OPTIMIZATIONS=0
export GAZEBO_MODEL_DATABASE_URI=""

# Setup workspace
echo "🔧 Setting up workspace..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "🎯 Strategy: Launch Gazebo step by step"
echo "   1. Start Gazebo server first"
echo "   2. Wait for full startup"
echo "   3. Start Gazebo client separately"
echo "   4. Spawn robot after UI is stable"
echo ""

# Step 1: Start Gazebo server only
echo "🚀 Step 1: Starting Gazebo server..."
gzserver /home/kantar/Desktop/hello-robot/worlds/multi_world.world --verbose &
SERVER_PID=$!

echo "⏰ Waiting for Gazebo server to fully start..."
sleep 10

# Step 2: Start robot description
echo "🤖 Step 2: Starting robot description..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat /home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf | sed 's|package://stretch_description/meshes/|file:///home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description/meshes/|g')" &
RSP_PID=$!

sleep 3

# Step 3: Try to start Gazebo client with maximum tolerance
echo "🎮 Step 3: Starting Gazebo client (UI)..."
echo "   This is where crashes usually happen..."
echo "   If it crashes, we'll try different approaches"

# Try approach 1: Standard client
timeout 30 gzclient --verbose 2>&1 | tee /tmp/gazebo_ui.log &
CLIENT_PID=$!

sleep 15

# Check if client is still running
if ps -p $CLIENT_PID > /dev/null; then
    echo "✅ Gazebo UI is running! Proceeding to spawn robot..."
    
    # Step 4: Spawn robot
    echo "🤖 Step 4: Spawning robot..."
    ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity stretch_ui_robot -x -3.0 -y 2.0 -z 0.5 -Y 0.0 &
    
    echo "🎉 SUCCESS! Gazebo UI should be visible with robot!"
    echo "   • Robot at position (-3, 2, 0.5)"
    echo "   • Look for 'stretch_ui_robot' in Models panel"
    echo "   • World has 5 obstacles + table + glass"
    
else
    echo "❌ Gazebo UI crashed. Trying alternative approach..."
    
    # Alternative approach: Different rendering
    echo "🔄 Trying alternative rendering..."
    export LIBGL_ALWAYS_INDIRECT=1
    export GALLIUM_DRIVER=softpipe
    
    timeout 30 gzclient --verbose &
    CLIENT_PID2=$!
    
    sleep 10
    
    if ps -p $CLIENT_PID2 > /dev/null; then
        echo "✅ Alternative approach worked! Spawning robot..."
        ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity stretch_ui_robot -x -3.0 -y 2.0 -z 0.5 -Y 0.0 &
    else
        echo "💡 UI keeps crashing, but server is running!"
        echo "   You can still:"
        echo "   1. Try opening gzclient manually later"
        echo "   2. Use RViz: rviz2"
        echo "   3. Control robot via python3 robot_pick_place_control.py"
    fi
fi

echo ""
echo "🎮 Manual controls available:"
echo "   • Joint control: ros2 run joint_state_publisher_gui joint_state_publisher_gui"
echo "   • Robot control: python3 robot_pick_place_control.py"
echo "   • RViz viewer: rviz2"

echo ""
echo "Press Ctrl+C to stop everything, or leave running to continue using"

# Keep alive
trap 'echo ""; echo "🛑 Stopping all processes..."; kill $SERVER_PID $RSP_PID $CLIENT_PID $CLIENT_PID2 2>/dev/null; killall -9 gzserver gzclient 2>/dev/null; exit 0' INT

wait
#!/bin/bash

echo "🔧 Simple Gazebo Robot Test"
echo "============================"

# Kill any existing processes
echo "🧹 Cleaning up..."
killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 2

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Test 1: Check if Gazebo can start at all
echo "🧪 Test 1: Testing basic Gazebo startup..."
echo "Gazebo version:"
gazebo --version | head -5
echo "✅ Gazebo version check completed"

# Test 2: Start Gazebo with minimal world
echo "🧪 Test 2: Starting Gazebo with empty world..."
gazebo --verbose /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
GAZEBO_PID=$!

# Give it time to start (longer for VM)
echo "⏳ Waiting 20 seconds for Gazebo to fully start (VM needs extra time)..."
sleep 20

# Check if Gazebo is still running
if kill -0 $GAZEBO_PID 2>/dev/null; then
    echo "✅ Gazebo is running successfully!"
    echo "🎯 You should see an empty Gazebo world window"
    echo "   The world should be responsive (you can rotate the view)"
    echo ""
    echo "Press ENTER to continue with robot loading test..."
    read
    
    # Test 3: Try to spawn robot using gz tool
    echo "🧪 Test 3: Attempting to spawn robot model..."
    
    # Set up environment
    export GAZEBO_MODEL_PATH="$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description"
    
    # Try to spawn the robot
    gz model --spawn-file=/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf --model-name=stretch_robot -x 0 -y 0 -z 0
    
    if [ $? -eq 0 ]; then
        echo "✅ Robot spawned successfully!"
        echo "🎯 You should now see the Stretch robot in Gazebo"
    else
        echo "⚠️  Robot spawn failed, but Gazebo is working"
        echo "   This might be due to URDF format issues"
    fi
    
    echo ""
    echo "Press ENTER to exit and close Gazebo..."
    read
    
    # Clean shutdown
    kill $GAZEBO_PID
    sleep 2
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    
else
    echo "❌ Gazebo crashed or failed to start properly"
    echo "   This indicates a more fundamental issue with Gazebo"
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    exit 1
fi

echo "🏁 Test completed!"
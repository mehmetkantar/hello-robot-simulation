#!/bin/bash

echo "🚀 Final Working Robot Test"
echo "=========================="

# Apply all VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export GAZEBO_MODEL_PATH="$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description:/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description"

# Clean up
killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 3

echo "🔧 Using ROS2 gazebo_ros spawn_entity instead of complex launch..."

# Start basic Gazebo first
echo "🌍 Starting Gazebo with empty world..."
gazebo --verbose /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
GAZEBO_PID=$!

# Wait for Gazebo to fully start
echo "⏳ Waiting 20 seconds for stable Gazebo startup..."
sleep 20

# Check if Gazebo is stable
if kill -0 $GAZEBO_PID 2>/dev/null; then
    echo "✅ Gazebo is running stably"
    
    # Source ROS2 environment
    cd /home/kantar/Desktop/hello-robot/stretch_ws
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    
    echo "🤖 Spawning robot using ROS2 spawn_entity..."
    echo "   This should work better than the complex launch files"
    
    # Use ros2 run instead of launch for more stability
    ros2 run gazebo_ros spawn_entity.py \
        -file /home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf \
        -entity stretch_robot \
        -x 0 -y 0 -z 0.1 \
        -timeout 60
    
    if [ $? -eq 0 ]; then
        echo "🎉 SUCCESS! Robot should now be visible in Gazebo!"
        echo ""
        echo "🎯 Look in Gazebo for:"
        echo "   - A robot at the center of the world (origin)"
        echo "   - If you can't see it, try:"
        echo "     • Mouse wheel to zoom out"
        echo "     • View → Reset View"
        echo "     • Look in World panel for 'stretch_robot'"
        echo ""
        echo "🔍 The robot may appear as basic shapes due to mesh loading issues"
        echo "   but the structure should be visible!"
        
        echo ""
        echo "Press ENTER to keep Gazebo running for testing..."
        read
        
        echo "Press ENTER again to close Gazebo..."
        read
        
    else
        echo "❌ Robot spawn failed, but Gazebo is working"
        echo "   Let's try with a simplified robot model"
        
        # Try with a simple test model
        echo "🧪 Testing with simple box model..."
        ros2 run gazebo_ros spawn_entity.py \
            -entity test_box \
            -x 0 -y 0 -z 1 \
            -b  # This spawns a simple box
        
        echo "Press ENTER to close..."
        read
    fi
    
    # Clean shutdown
    kill $GAZEBO_PID 2>/dev/null
    sleep 2
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    
else
    echo "❌ Gazebo failed to start stably"
    echo "   This suggests hardware/VM limitations"
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
fi

echo "🏁 Test completed!"
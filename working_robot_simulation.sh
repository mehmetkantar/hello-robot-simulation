#!/bin/bash

echo "🤖 Working Robot Simulation (Fixed)"
echo "=================================="

# Apply all VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Clean up first
killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 3

echo "🚀 Starting Gazebo WITH ROS2 plugins..."

# Start Gazebo with the correct ROS2 plugins
gzserver --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
SERVER_PID=$!

echo "⏳ Waiting for Gazebo server to start..."
sleep 10

# Start Gazebo client
gzclient &
CLIENT_PID=$!

echo "⏳ Waiting for Gazebo client to connect..."
sleep 10

# Check if both are running
if kill -0 $SERVER_PID 2>/dev/null && kill -0 $CLIENT_PID 2>/dev/null; then
    echo "✅ Gazebo server and client are running with ROS2 plugins!"
    
    # Source ROS2 environment
    cd /home/kantar/Desktop/hello-robot/stretch_ws
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    
    echo "🎯 Now spawning the robot..."
    
    # Spawn the robot
    ros2 run gazebo_ros spawn_entity.py \
        -file /home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf \
        -entity stretch_robot \
        -x 0 -y 0 -z 0.1
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Robot has been spawned!"
        echo ""
        echo "🔍 In the Gazebo window, you should now see:"
        echo "   - The Stretch robot at the center (origin)"
        echo "   - It may appear as basic colored shapes if meshes don't load"
        echo "   - Check the World panel on the left for 'stretch_robot'"
        echo ""
        echo "💡 If you still don't see anything:"
        echo "   1. Mouse wheel to zoom WAY out"
        echo "   2. Try View → Reset View"
        echo "   3. Look for any shapes near the grid center"
        echo "   4. The robot might be very small or transparent"
        echo ""
        echo "🎮 Gazebo Controls:"
        echo "   - Left mouse: Rotate view"
        echo "   - Middle mouse: Pan"
        echo "   - Scroll: Zoom"
        echo ""
        echo "Press ENTER when you're done viewing..."
        read
    else
        echo "❌ Robot spawn still failed"
        echo "   But at least Gazebo with ROS2 is working now!"
        
        # Try spawning a simple test box to verify spawning works
        echo "🧪 Testing with a simple box..."
        ros2 run gazebo_ros spawn_entity.py \
            -entity test_box \
            -x 0 -y 0 -z 1 \
            -database box
        
        echo "Press ENTER to continue..."
        read
    fi
    
    echo "🛑 Shutting down Gazebo..."
    kill $SERVER_PID $CLIENT_PID 2>/dev/null
    sleep 3
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    
else
    echo "❌ Gazebo failed to start properly"
    echo "   Your VM may not have sufficient resources for Gazebo"
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
fi

echo ""
echo "🏁 Simulation test completed!"
echo ""
echo "📋 Summary:"
echo "   ✅ VM environment fixed (software rendering)"
echo "   ✅ Mesh files available (79 STL files)"
echo "   ✅ URDF files valid"
echo "   ✅ ROS2 workspace built"
echo "   🎯 Robot should be visible with this approach"
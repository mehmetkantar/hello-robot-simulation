#!/bin/bash

echo "🔧 Minimal Gazebo Test for Hello Robot Stretch"
echo "==============================================="

# Kill any existing processes
killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 2

# Check if we have the URDF file
URDF_FILE="/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

if [ ! -f "$URDF_FILE" ]; then
    echo "❌ URDF file not found: $URDF_FILE"
    exit 1
fi

echo "✅ Found URDF file"

# Test 1: Check URDF syntax
echo "🧪 Test 1: Checking URDF syntax..."
if command -v check_urdf >/dev/null 2>&1; then
    if check_urdf "$URDF_FILE" >/dev/null 2>&1; then
        echo "✅ URDF syntax is valid"
    else
        echo "❌ URDF has syntax errors"
        check_urdf "$URDF_FILE"
        exit 1
    fi
else
    echo "⚠️  check_urdf not available, skipping syntax check"
fi

# Test 2: Start Gazebo with just empty world
echo "🧪 Test 2: Testing basic Gazebo functionality..."
echo "   Starting Gazebo with empty world..."
gazebo /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
GAZEBO_PID=$!

# Wait for startup
echo "⏳ Waiting 15 seconds for Gazebo to start..."
sleep 15

# Check if Gazebo is responsive
if kill -0 $GAZEBO_PID 2>/dev/null; then
    echo "✅ Gazebo is running"
    echo "🎯 Gazebo window should be visible and responsive"
    echo "   You should be able to:"
    echo "   - Rotate the view with mouse"
    echo "   - See a grid ground plane"
    echo "   - See the Insert tab in the left panel"
    echo ""
    echo "Is Gazebo working properly? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "✅ Basic Gazebo test passed"
        
        # Test 3: Try to load robot manually
        echo ""
        echo "🧪 Test 3: Manual robot loading test"
        echo "   In the Gazebo window:"
        echo "   1. Click the 'Insert' tab in the left panel"
        echo "   2. Look for any robot models"
        echo "   3. Try inserting a simple model (like a box)"
        echo ""
        echo "Can you insert models from the Insert tab? (y/n)"
        read -r response2
        
        if [[ "$response2" =~ ^[Yy]$ ]]; then
            echo "✅ Gazebo model insertion works"
            echo ""
            echo "🎯 The issue might be specific to the Stretch robot URDF"
            echo "   or the ROS2 integration. Gazebo itself is working."
        else
            echo "❌ Gazebo model insertion not working"
            echo "   This suggests a deeper Gazebo configuration issue"
        fi
    else
        echo "❌ Basic Gazebo test failed"
        echo "   Gazebo is not responding properly"
    fi
    
    echo ""
    echo "Press ENTER to close Gazebo and exit..."
    read
    
    # Clean shutdown
    kill $GAZEBO_PID 2>/dev/null
    sleep 2
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    
else
    echo "❌ Gazebo failed to start or crashed"
    echo "   Check system resources and graphics drivers"
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    exit 1
fi

echo "🏁 Test completed!"
echo ""
echo "📋 Test Summary:"
echo "   - URDF file exists: ✅"
echo "   - Gazebo can start: ✅"
echo "   - Next step: Debug robot-specific loading issues"
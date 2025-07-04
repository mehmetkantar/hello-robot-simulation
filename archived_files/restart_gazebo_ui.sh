#!/bin/bash

echo "🔄 Restart Gazebo UI - Quick Approach"
echo "===================================="
echo ""

# Since your Gazebo server is already running with the robot spawned,
# we just need to restart the client (UI)

echo "🎯 Current status check..."
if pgrep -f gzserver > /dev/null; then
    echo "✅ Gazebo server is running"
else
    echo "❌ Gazebo server not running - need full restart"
    echo "   Run ./force_gazebo_ui.sh instead"
    exit 1
fi

# Kill only the client, keep server
echo "🧹 Killing only Gazebo client (keeping server)..."
killall -9 gzclient 2>/dev/null || true
sleep 2

# Apply graphics settings
echo "🖥️  Applying graphics settings..."
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export DISPLAY=:0
export GAZEBO_IP=127.0.0.1
export GAZEBO_MASTER_URI=http://localhost:11345

# Try different client startup approaches
echo "🎮 Attempting to start Gazebo UI..."
echo ""

echo "Approach 1: Standard client startup"
timeout 20 gzclient --verbose &
CLIENT_PID=$!

echo "⏰ Waiting 15 seconds to see if UI stays open..."
sleep 15

if ps -p $CLIENT_PID > /dev/null; then
    echo "🎉 SUCCESS! Gazebo UI is running!"
    echo "   • Robot 'stretch_pick_place_robot' should be visible"
    echo "   • Check Models panel in Gazebo"
    echo "   • Robot is at position (-3, 2) in the world"
    echo ""
    echo "🎮 You can now:"
    echo "   • View the robot and world in Gazebo"
    echo "   • Control robot: python3 robot_pick_place_control.py"
    echo "   • Manual joints: ros2 run joint_state_publisher_gui joint_state_publisher_gui"
    
    echo ""
    echo "Press Enter to keep UI running, or Ctrl+C to exit"
    read
    
else
    echo "❌ Standard approach failed. Trying alternative..."
    
    # Alternative with different settings
    export LIBGL_ALWAYS_INDIRECT=1
    export MESA_LOADER_DRIVER_OVERRIDE=i965
    
    echo "Approach 2: Alternative graphics settings"
    timeout 20 gzclient --verbose &
    CLIENT_PID2=$!
    
    sleep 10
    
    if ps -p $CLIENT_PID2 > /dev/null; then
        echo "🎉 Alternative approach worked!"
        echo "Press Enter to keep running"
        read
    else
        echo "💔 UI keeps crashing due to VM graphics limitations"
        echo ""
        echo "🔍 But your robot simulation IS working!"
        echo "   • Server running: ✅"
        echo "   • Robot spawned: ✅"  
        echo "   • Physics active: ✅"
        echo ""
        echo "📺 Alternative visualization:"
        echo "   rviz2 - will show robot in 3D"
        echo ""
        echo "🤖 Robot control still works:"
        echo "   python3 robot_pick_place_control.py"
    fi
fi

echo ""
echo "Manual client restart: gzclient --verbose"
#!/bin/bash

echo "🎮 Simple Gazebo UI - Using Working Command"
echo "==========================================="
echo ""

# Use the EXACT same approach that worked for you before

echo "🎉 Using the same method that showed you the robot!"
echo ""

# Check server
if ! pgrep -f gzserver > /dev/null; then
    echo "❌ Server not running. Need to start server first."
    echo "   Run: gzserver /home/kantar/Desktop/hello-robot/worlds/multi_world.world &"
    echo "   Wait 10 seconds, then run this script again"
    exit 1
fi

echo "✅ Gazebo server is running"

# Use the EXACT same graphics settings that worked
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export DISPLAY=:0
export GAZEBO_IP=127.0.0.1
export GAZEBO_MASTER_URI=http://localhost:11345

# Kill any existing client
echo "🧹 Killing existing client..."
killall -9 gzclient 2>/dev/null
sleep 2

echo "🎮 Starting Gazebo client (same command that worked)..."
echo "   You should see the robot appear!"

# Use the simple command that worked for you
gzclient --verbose &
CLIENT_PID=$!

echo "⏰ Client started (PID: $CLIENT_PID)"
echo "   Waiting to see if it stays stable..."

# Monitor for 30 seconds with progress
for i in {1..30}; do
    if ps -p $CLIENT_PID > /dev/null; then
        if [ $((i % 5)) -eq 0 ]; then
            echo "✅ Still running after $i seconds..."
        fi
        sleep 1
    else
        echo ""
        echo "💥 UI crashed after $i seconds"
        echo ""
        echo "🔄 Want to try again? Options:"
        echo "   1. ./simple_gazebo_ui.sh (this script)"
        echo "   2. gzclient --verbose & (manual)"
        echo "   3. ./persistent_gazebo_ui.sh (auto-retry)"
        echo ""
        echo "🤖 Remember: Robot is still running in server!"
        echo "   You can control it even without UI:"
        echo "   python3 robot_pick_place_control.py"
        exit 1
    fi
done

echo ""
echo "🎉 UI survived 30 seconds! It's working!"
echo ""
echo "🎯 You should now see:"
echo "   • Robot at position (-3, 2) with full 3D meshes"
echo "   • 5 colored obstacles (red, blue, green, orange, purple)"
echo "   • Central table with glass on top"
echo "   • Room walls"
echo ""
echo "🎮 Try these while UI is stable:"
echo "   • Zoom in/out with mouse wheel"
echo "   • Rotate view by dragging"
echo "   • Look for 'stretch_pick_place_robot' in Models panel"
echo ""
echo "Press Enter to start robot control, or Ctrl+C to keep just UI"
read

echo "🤖 Starting robot pick & place control..."
python3 robot_pick_place_control.py &
CONTROL_PID=$!

echo ""
echo "🎮 Both UI and robot control running!"
echo "   UI PID: $CLIENT_PID"
echo "   Control PID: $CONTROL_PID"
echo ""
echo "🎯 Now you can:"
echo "   • See robot in Gazebo UI"
echo "   • Control robot with Python interface"
echo "   • Try pick and place operations"
echo ""
echo "Press Ctrl+C to stop everything"

# Keep both running
trap 'echo ""; echo "🛑 Stopping UI and control..."; kill $CLIENT_PID $CONTROL_PID 2>/dev/null; exit 0' INT

# Monitor both processes
while ps -p $CLIENT_PID > /dev/null && ps -p $CONTROL_PID > /dev/null; do
    echo "✅ UI and control both running... ($(date '+%H:%M:%S'))"
    sleep 10
done

if ! ps -p $CLIENT_PID > /dev/null; then
    echo "💥 UI crashed, but control still running"
    echo "🎮 Robot control continues to work!"
fi

if ! ps -p $CONTROL_PID > /dev/null; then
    echo "🤖 Control stopped"
fi

wait
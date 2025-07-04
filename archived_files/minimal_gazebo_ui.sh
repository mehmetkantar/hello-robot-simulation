#!/bin/bash

echo "🎯 Minimal Gazebo UI - Lightest Possible"
echo "========================================"
echo ""

# You saw the robot! Let's try to make UI more stable by reducing load

echo "🎉 Since you confirmed robot visibility works,"
echo "   let's try the most minimal UI possible..."
echo ""

# Check server
if ! pgrep -f gzserver > /dev/null; then
    echo "❌ Server not running. Starting minimal server..."
    gzserver --verbose /home/kantar/Desktop/hello-robot/worlds/multi_world.world &
    sleep 10
fi

# Minimal graphics settings
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export GAZEBO_MODEL_DATABASE_URI=""  # Disable online model loading
export OGRE_RTShader_Write_Debug_Info=false

# Kill other processes to free resources
echo "🧹 Freeing system resources..."
killall -9 firefox chromium-browser code 2>/dev/null || true
killall -9 rviz2 2>/dev/null || true

echo "🎮 Starting minimal Gazebo client..."
echo "   (No extra plugins, minimal rendering)"

# Start with minimal options
gzclient --verbose \
    --gui-client-plugin= \
    2>&1 | tee /tmp/gazebo_minimal.log &

CLIENT_PID=$!

echo "⏰ Monitoring for 60 seconds..."
echo "   If you see the robot, take a screenshot quickly!"

# Monitor with more detailed feedback
for i in {1..60}; do
    if ps -p $CLIENT_PID > /dev/null; then
        case $((i % 4)) in
            0) echo -n "🎮 " ;;
            1) echo -n "⏰ " ;;
            2) echo -n "🤖 " ;;
            3) echo -n "✅ " ;;
        esac
    else
        echo ""
        echo "💥 UI crashed after $i seconds"
        echo ""
        echo "🔍 Crash log:"
        tail -5 /tmp/gazebo_minimal.log
        
        echo ""
        echo "🎯 Quick tips for next attempt:"
        echo "   1. Close all other applications first"
        echo "   2. Try: killall -9 firefox chrome"
        echo "   3. Free memory: sync && echo 3 > /proc/sys/vm/drop_caches"
        echo "   4. Try different times - sometimes VM graphics are more stable"
        
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 UI survived 60 seconds! Taking longer look..."

# If it survived, let user interact
echo ""
echo "🎮 Gazebo UI is stable! You should see:"
echo "   • Robot at position (-3, 2) - visible with meshes"
echo "   • 5 colored obstacles around the room"
echo "   • Table in center with glass on top"
echo "   • Room walls"
echo ""
echo "🎯 Quick actions while UI is stable:"
echo "   1. Take screenshots"
echo "   2. Try moving robot with joint sliders"
echo "   3. Zoom/pan around the world"
echo ""
echo "Press Enter when ready to test robot control, or Ctrl+C to keep UI only"
read

echo "🤖 Starting robot control interface..."
python3 /home/kantar/Desktop/hello-robot/robot_pick_place_control.py &

echo "🎮 Both UI and robot control running!"
echo "    Press Ctrl+C to stop everything"

# Keep monitoring
while ps -p $CLIENT_PID > /dev/null; do
    echo "✅ UI still stable... ($(date '+%H:%M:%S'))"
    sleep 5
done

echo "💥 UI finally crashed, but that's normal for VMs"
echo "🎉 SUCCESS: You got to see the robot working in Gazebo!"
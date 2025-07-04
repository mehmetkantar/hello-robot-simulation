#!/bin/bash

echo "🔄 Persistent Gazebo UI - Auto-Restart on Crash"
echo "==============================================="
echo ""

# Since you confirmed the robot IS VISIBLE, we just need to keep the UI alive!

echo "🎉 Great news! You confirmed robot is visible in Gazebo!"
echo "   Now let's keep the UI running as long as possible..."
echo ""

# Check server status
if pgrep -f gzserver > /dev/null; then
    echo "✅ Gazebo server running - robot is there!"
else
    echo "❌ Need to start server first"
    echo "   Run ./force_gazebo_ui.sh instead"
    exit 1
fi

# Graphics settings that worked for you
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export DISPLAY=:0
export GAZEBO_IP=127.0.0.1
export GAZEBO_MASTER_URI=http://localhost:11345

# Function to start UI
start_ui() {
    echo "🎮 Starting Gazebo UI (attempt $1)..."
    gzclient --verbose 2>/dev/null &
    CLIENT_PID=$!
    echo "   Client PID: $CLIENT_PID"
    return $CLIENT_PID
}

# Function to monitor UI
monitor_ui() {
    local pid=$1
    local attempt=$2
    
    echo "⏰ Monitoring UI for 30 seconds..."
    
    for i in {1..30}; do
        if ps -p $pid > /dev/null; then
            echo -n "."
            sleep 1
        else
            echo ""
            echo "💥 UI crashed after $i seconds (attempt $attempt)"
            return 1
        fi
    done
    
    echo ""
    echo "🎉 UI survived 30 seconds! It's stable!"
    
    # If stable, keep monitoring
    while ps -p $pid > /dev/null; do
        echo "✅ UI still running... ($(date))"
        sleep 10
    done
    
    echo "💥 UI eventually crashed"
    return 1
}

# Main loop - keep trying to restart UI
attempt=1
max_attempts=10

echo "🚀 Starting persistent UI with auto-restart..."
echo "   Will try up to $max_attempts times"
echo "   Press Ctrl+C to stop"
echo ""

while [ $attempt -le $max_attempts ]; do
    echo "--- Attempt $attempt/$max_attempts ---"
    
    # Kill any existing client
    killall -9 gzclient 2>/dev/null
    sleep 2
    
    # Start UI
    start_ui $attempt
    client_pid=$!
    
    # Monitor it
    if monitor_ui $client_pid $attempt; then
        echo "🎉 UI is stable!"
        break
    else
        echo "🔄 Will restart in 3 seconds..."
        sleep 3
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo ""
    echo "💔 UI keeps crashing after $max_attempts attempts"
    echo ""
    echo "🎯 But you confirmed the robot IS VISIBLE when it works!"
    echo "   The fix is working - it's just a graphics stability issue"
    echo ""
    echo "🛠️  Alternatives:"
    echo "   1. Manual restart: gzclient --verbose"
    echo "   2. Use RViz: rviz2" 
    echo "   3. Control robot: python3 robot_pick_place_control.py"
    echo "   4. Reduce graphics load: close other applications"
    echo ""
    echo "💡 Try running this script again after closing other programs"
fi

echo ""
echo "🤖 Robot simulation continues running in background!"
echo "    Server PID: $(pgrep gzserver)"
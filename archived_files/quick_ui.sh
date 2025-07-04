#!/bin/bash

# Quick UI restart - one command that worked for you

echo "🚀 Quick Gazebo UI restart..."

# Set working environment
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill and restart
killall -9 gzclient 2>/dev/null
sleep 1

echo "🎮 Starting UI..."
gzclient --verbose &

echo "✅ Started! Watch for robot at (-3, 2)"
echo "   Ctrl+C to stop, or run again if it crashes"
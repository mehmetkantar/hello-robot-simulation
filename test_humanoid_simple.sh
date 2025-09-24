#!/bin/bash

# Simple test of dual robot system

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

print_color "🧪 Testing Dual Robot System..." $GREEN

# ROS2 setup
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

# Start bridge in background
print_color "Starting dual robot bridge..." $GREEN
python3 stretch_slam_bridge_with_humanoid.py &
BRIDGE_PID=$!

# Wait for initialization
sleep 15

# Check if topics are published
print_color "Checking ROS2 topics..." $GREEN
STRETCH_TOPICS=$(ros2 topic list | grep "/stretch/" | wc -l)
HUMANOID_TOPICS=$(ros2 topic list | grep "/humanoid/" | wc -l)

print_color "Stretch topics: $STRETCH_TOPICS" $GREEN
print_color "Humanoid topics: $HUMANOID_TOPICS" $GREEN

if [ "$STRETCH_TOPICS" -gt 0 ] && [ "$HUMANOID_TOPICS" -gt 0 ]; then
    print_color "✅ SUCCESS: Both robots publishing topics!" $GREEN
else
    print_color "❌ FAILED: Missing robot topics" $RED
fi

# Test web controller
print_color "Starting web controller..." $GREEN
python3 dual_robot_web_controller.py &
WEB_PID=$!
sleep 3

# Check if web server is running
if curl -s http://localhost:8082 > /dev/null; then
    print_color "✅ SUCCESS: Web controller accessible at http://localhost:8082" $GREEN
else
    print_color "❌ FAILED: Web controller not accessible" $RED
fi

# Cleanup
print_color "Cleaning up..." $GREEN
kill $BRIDGE_PID 2>/dev/null || true
kill $WEB_PID 2>/dev/null || true

print_color "🧪 Test completed!" $GREEN
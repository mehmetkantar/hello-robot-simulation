#!/bin/bash

# Navigation Debug Script - Step by step SLAM diagnosis

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

print_color "🔧 NAVIGATION DEBUG - STEP BY STEP" $GREEN

# Clean everything
print_color "1. Cleaning all processes..." $YELLOW
pkill -f stretch_slam_bridge 2>/dev/null || true
pkill -f slam_toolbox 2>/dev/null || true
pkill -f navigation 2>/dev/null || true
pkill -f rviz 2>/dev/null || true
sleep 3

# Check ROS2
if [ -z "$ROS_DISTRO" ]; then
    source /opt/ros/humble/setup.bash
    export ROS_DOMAIN_ID=0
fi

# Start bridge ONCE
print_color "2. Starting SINGLE MuJoCo bridge..." $GREEN
python3 stretch_slam_bridge_improved.py --complex-office --headless &
BRIDGE_PID=$!
print_color "Bridge PID: $BRIDGE_PID" $YELLOW

sleep 8

# Check topics
print_color "3. Checking topics after bridge start..." $GREEN
ros2 topic list | grep -E "(scan|odom|map)" || echo "No topics found"

print_color "4. Checking scan publishers..." $GREEN
ros2 topic info /scan

# Start SLAM manually
print_color "5. Starting SLAM Toolbox manually..." $GREEN
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file config/mapper_params_online_async.yaml &
SLAM_PID=$!
print_color "SLAM PID: $SLAM_PID" $YELLOW

sleep 8

# Check map
print_color "6. Checking if map is now available..." $GREEN
ros2 topic list | grep map || echo "No map topic"
ros2 topic info /map 2>/dev/null || echo "Map topic not found"

print_color "7. Final node list:" $GREEN
ros2 node list

print_color "" $NC
print_color "🎯 DIAGNOSIS COMPLETE" $GREEN
print_color "Bridge PID: $BRIDGE_PID" $YELLOW  
print_color "SLAM PID: $SLAM_PID" $YELLOW
print_color "" $NC
print_color "Keep this running and test in another terminal:" $GREEN
print_color "ros2 topic echo /map --once" $YELLOW

# Keep running
while true; do
    sleep 30
    if ! kill -0 $BRIDGE_PID 2>/dev/null; then
        print_color "❌ Bridge died" $RED
        break
    fi
    if ! kill -0 $SLAM_PID 2>/dev/null; then
        print_color "❌ SLAM died" $RED
        break
    fi
    print_color "✅ Both processes running..." $GREEN
done
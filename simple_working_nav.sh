#!/bin/bash

# Ultra Simple Working Navigation - Just Get Goal Selection Working

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

cleanup() {
    print_color "Cleaning up..." $YELLOW
    pkill -f stretch_slam_bridge 2>/dev/null || true
    pkill -f slam_toolbox 2>/dev/null || true
    pkill -f nav2 2>/dev/null || true
    pkill -f rviz2 2>/dev/null || true
    sleep 2
}

trap cleanup EXIT INT TERM

print_color "🚀 SIMPLE WORKING NAVIGATION" $GREEN

# ROS2 setup
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

cleanup

print_color "1. Starting Bridge with MuJoCo viewer..." $GREEN
python3 stretch_slam_bridge_improved.py --complex-office &
print_color "   Waiting for MuJoCo to fully initialize..." $YELLOW
sleep 15  # More time for MuJoCo to start

print_color "2. Starting SLAM..." $GREEN
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file config/mapper_params_online_async.yaml &
sleep 8

print_color "3. Starting Nav2 Bringup with HIGH SPEED config..." $GREEN
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true \
    params_file:=config/nav2_high_speed.yaml &
sleep 12

print_color "4. Starting RViz..." $GREEN
rviz2 -d rviz/stretch_navigation.rviz --ros-args -p use_sim_time:=true &
sleep 5

print_color "✅ TESTING SYSTEM..." $GREEN

# Test navigation action
sleep 5
ACTION_SERVERS=$(ros2 action info /navigate_to_pose 2>/dev/null | grep "Action servers:" | cut -d: -f2 | xargs || echo "0")
MAP_PUBLISHERS=$(ros2 topic info /map 2>/dev/null | grep "Publisher count:" | cut -d: -f2 | xargs || echo "0")

print_color "Map Publishers: $MAP_PUBLISHERS" $YELLOW
print_color "Navigate Servers: $ACTION_SERVERS" $YELLOW

if [ "$ACTION_SERVERS" = "1" ] && [ "$MAP_PUBLISHERS" = "1" ]; then
    print_color "🎉 SUCCESS! Use RViz 2D Goal Pose tool to navigate!" $GREEN
    print_color "Click the goal tool and click on white areas of the map" $GREEN
else
    print_color "⚠️  System still starting, wait 30 more seconds..." $YELLOW
fi

print_color "Press Ctrl+C to stop" $RED

# Keep running
while true; do
    sleep 60
    print_color "System running..." $GREEN
done
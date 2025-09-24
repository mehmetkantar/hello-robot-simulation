#!/bin/bash

# Dual Robot Navigation - Stretch + Humanoid in Same Environment

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

cleanup() {
    print_color "Cleaning up dual robot system..." $YELLOW
    pkill -f stretch_slam_bridge_with_humanoid 2>/dev/null || true
    pkill -f dual_robot_slam_bridge 2>/dev/null || true
    pkill -f slam_toolbox 2>/dev/null || true
    pkill -f nav2 2>/dev/null || true
    pkill -f rviz2 2>/dev/null || true
    pkill -f dual_robot_web_controller 2>/dev/null || true
    sleep 2
}

trap cleanup EXIT INT TERM

print_color "🤖🚶 DUAL ROBOT NAVIGATION SYSTEM" $GREEN
print_color "Stretch Robot + Humanoid Robot in Same Environment" $BLUE

# ROS2 setup
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

cleanup

print_color "1. Starting Dual Robot Bridge with MuJoCo viewer..." $GREEN
python3 stretch_slam_bridge_with_humanoid.py &
print_color "   Waiting for dual robot scene to fully initialize..." $YELLOW
sleep 20  # More time for complex dual robot scene

print_color "2. Starting SLAM (Stretch robot sensors)..." $GREEN
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file config/mapper_params_online_async.yaml &
sleep 10

print_color "3. Starting Nav2 Bringup with HIGH SPEED config..." $GREEN
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true \
    params_file:=config/nav2_high_speed.yaml &
sleep 15

print_color "4. Starting RViz for dual robot visualization..." $GREEN
rviz2 -d rviz/stretch_navigation.rviz --ros-args -p use_sim_time:=true &
sleep 5

print_color "5. Starting Dual Robot Web Controller..." $GREEN
python3 dual_robot_web_controller.py &
sleep 3

print_color "✅ TESTING DUAL ROBOT SYSTEM..." $GREEN

# Test navigation action
sleep 5
ACTION_SERVERS=$(ros2 action info /navigate_to_pose 2>/dev/null | grep "Action servers:" | cut -d: -f2 | xargs || echo "0")
MAP_PUBLISHERS=$(ros2 topic info /map 2>/dev/null | grep "Publisher count:" | cut -d: -f2 | xargs || echo "0")
SCAN_PUBLISHERS=$(ros2 topic info /scan 2>/dev/null | grep "Publisher count:" | cut -d: -f2 | xargs || echo "0")
HUMANOID_TOPICS=$(ros2 topic info /humanoid/odom 2>/dev/null | grep "Publisher count:" | cut -d: -f2 | xargs || echo "0")

print_color "Map Publishers: $MAP_PUBLISHERS" $YELLOW
print_color "Scan Publishers: $SCAN_PUBLISHERS" $YELLOW
print_color "Humanoid Topics: $HUMANOID_TOPICS" $YELLOW
print_color "Navigate Servers: $ACTION_SERVERS" $YELLOW

if [ "$ACTION_SERVERS" = "1" ] && [ "$MAP_PUBLISHERS" = "1" ] && [ "$SCAN_PUBLISHERS" = "1" ] && [ "$HUMANOID_TOPICS" = "1" ]; then
    print_color "🎉 SUCCESS! Dual robot system ready!" $GREEN
    print_color "🤖 Stretch Robot: Navigation, SLAM mapping with sensors" $GREEN
    print_color "🚶 Humanoid Robot: Bipedal walking in same environment" $GREEN
    print_color "🌐 Dual Robot Web Controller: http://localhost:8082" $GREEN
    print_color "📱 Use web browser to control both robots!" $GREEN
    print_color "🗺️ Use RViz 2D Goal Pose tool for Stretch navigation!" $GREEN
else
    print_color "⚠️  System still starting, wait 30 more seconds..." $YELLOW
fi

print_color "🤖🚶 DUAL ROBOT FEATURES:" $BLUE
print_color "• Stretch: Full manipulation + SLAM + Navigation" $BLUE
print_color "• Humanoid: Bipedal locomotion + Walking patterns" $BLUE
print_color "• Same environment: Complex office scene" $BLUE
print_color "• Dual control: Separate web panels for each robot" $BLUE
print_color "• Visualization: Both robots visible in MuJoCo + RViz" $BLUE
print_color "" $NC
print_color "Press Ctrl+C to stop all systems" $RED

# Keep running
while true; do
    sleep 60
    print_color "Dual robot system running..." $GREEN
done
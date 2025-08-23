#!/bin/bash

echo "🔧 SLAM MAP FIX SCRIPT"
echo "====================="

# Kill all conflicting processes
echo "1. Cleaning up duplicate processes..."
pkill -f stretch_slam_bridge_improved
pkill -f slam_toolbox
pkill -f navigation
sleep 3

# Start SLAM Toolbox separately first
echo "2. Starting SLAM Toolbox..."
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file config/mapper_params_online_async.yaml &

sleep 5

# Check if SLAM is publishing map
echo "3. Checking map publication..."
timeout 3s ros2 topic hz /map

# Start single bridge
echo "4. Starting single SLAM bridge..."
python3 stretch_slam_bridge_improved.py --complex-office &

echo "5. Wait 10 seconds then check:"
echo "   ros2 topic info /map"
echo "   Should show: Publisher count: 1"
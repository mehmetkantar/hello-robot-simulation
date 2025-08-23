#!/bin/bash

# Fixed Navigation with MuJoCo Viewer and Working Costmaps

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
    print_color "🛑 Cleaning up..." $YELLOW
    pkill -f stretch_slam_bridge 2>/dev/null || true
    pkill -f slam_toolbox 2>/dev/null || true
    pkill -f nav2 2>/dev/null || true
    pkill -f rviz2 2>/dev/null || true
    pkill -f controller_server 2>/dev/null || true
    pkill -f planner_server 2>/dev/null || true
    pkill -f bt_navigator 2>/dev/null || true
    sleep 3
}

trap cleanup EXIT INT TERM

print_color "🚀 FIXED NAVIGATION WITH MUJOCO" $GREEN

# ROS2 setup
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

cleanup

print_color "Step 1: Starting MuJoCo Bridge (WITH VIEWER)..." $GREEN
python3 stretch_slam_bridge_improved.py --complex-office &
BRIDGE_PID=$!
sleep 12

print_color "Step 2: Starting Robot State Publisher..." $GREEN
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p use_sim_time:=true \
    -p robot_description:="$(cat /tmp/stretch_slam.urdf 2>/dev/null || echo '<?xml version="1.0"?><robot name="stretch"><link name="base_link"><visual><geometry><box size="0.3 0.3 0.1"/></geometry></visual></link></robot>')" &
sleep 3

print_color "Step 3: Starting SLAM Toolbox..." $GREEN
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file config/mapper_params_online_async.yaml &
sleep 8

# Move robot to generate map data
print_color "Step 4: Moving robot to generate map data..." $YELLOW
print_color "Publishing movement commands to generate mapped areas..." $BLUE

# Publish some movement commands to create map data
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' &
sleep 2
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}' &
sleep 2
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: -0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' &
sleep 2
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -0.5}}' &
sleep 2
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}' &

print_color "Step 5: Waiting for map to populate..." $GREEN
sleep 5

# Check if map has non-unknown data
MAP_DATA=$(ros2 topic echo /map --once | grep -A100 "data:" | grep -v "^-1$" | wc -l)
print_color "Map populated areas: $MAP_DATA" $BLUE

print_color "Step 6: Creating costmap-friendly nav2 params..." $GREEN

# Create nav2 params that work with SLAM-generated maps
cat > /tmp/nav2_slam_friendly.yaml << 'EOF'
controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 10.0
    controller_plugins: ["FollowPath"]
    
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: False
      min_vel_x: 0.0
      max_vel_x: 2.0
      max_vel_theta: 1.0
      acc_lim_x: 2.5
      acc_lim_theta: 3.2
      sim_time: 1.7
      critics: ["BaseObstacle", "GoalAlign", "PathAlign"]

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: True
      rolling_window: true
      width: 4
      height: 4
      resolution: 0.05
      plugins: ["obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          data_type: "LaserScan"
          clearing: True
          marking: True
          max_obstacle_height: 2.0
          obstacle_range: 2.0
          raytrace_range: 3.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 10.0
        inflation_radius: 0.3
      always_send_full_costmap: True

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: True
      track_unknown_space: false
      plugins: ["obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          data_type: "LaserScan"
          clearing: True
          marking: True
          max_obstacle_height: 2.0
          obstacle_range: 5.0
          raytrace_range: 6.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 10.0
        inflation_radius: 0.3
      always_send_full_costmap: True

planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: True
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    navigators: ['navigate_to_pose']
    navigate_to_pose:
      plugin: "nav2_bt_navigator/NavigateToPoseNavigator"
EOF

print_color "Step 7: Starting Nav2 components with SLAM-friendly config..." $GREEN

# Start Nav2 with our custom config
ros2 run nav2_controller controller_server \
    --ros-args --params-file /tmp/nav2_slam_friendly.yaml &

ros2 run nav2_planner planner_server \
    --ros-args --params-file /tmp/nav2_slam_friendly.yaml &

ros2 run nav2_bt_navigator bt_navigator \
    --ros-args --params-file /tmp/nav2_slam_friendly.yaml &

# Lifecycle manager
ros2 run nav2_lifecycle_manager lifecycle_manager \
    --ros-args -p use_sim_time:=true \
    -p autostart:=true \
    -p node_names:="['controller_server', 'planner_server', 'bt_navigator']" &

sleep 10

print_color "Step 8: Starting RViz..." $GREEN
rviz2 -d rviz/stretch_navigation.rviz --ros-args -p use_sim_time:=true &
sleep 8

print_color "✅ SYSTEM STATUS CHECK..." $GREEN

# System status
ACTION_SERVERS=$(ros2 action info /navigate_to_pose 2>/dev/null | grep "Action servers:" | cut -d: -f2 | xargs || echo "0")
MAP_PUBLISHERS=$(ros2 topic info /map 2>/dev/null | grep "Publisher count:" | cut -d: -f2 | xargs || echo "0")

print_color "Map Publishers: $MAP_PUBLISHERS" $YELLOW  
print_color "Navigate Action Servers: $ACTION_SERVERS" $YELLOW

# Check costmaps
LOCAL_COSTMAP=$(ros2 topic list | grep local_costmap/costmap || echo "none")
GLOBAL_COSTMAP=$(ros2 topic list | grep global_costmap/costmap || echo "none")

print_color "Local Costmap: $LOCAL_COSTMAP" $YELLOW
print_color "Global Costmap: $GLOBAL_COSTMAP" $YELLOW

print_color "" $NC
print_color "🎯 INSTRUCTIONS:" $BLUE
print_color "1. You should see MuJoCo window with office environment" $NC
print_color "2. In RViz, use '2D Goal Pose' tool" $NC  
print_color "3. Click on open areas (not walls) in the map" $NC
print_color "4. Robot should navigate autonomously" $NC
print_color "" $NC

if [ "$ACTION_SERVERS" = "1" ]; then
    print_color "🎉 NAVIGATION READY!" $GREEN
else
    print_color "⚠️  Still starting up, wait 30 seconds..." $YELLOW
fi

print_color "🛑 Press Ctrl+C to stop" $RED

# Keep running
while true; do
    sleep 30
    if ! kill -0 $BRIDGE_PID 2>/dev/null; then
        print_color "❌ MuJoCo bridge died" $RED
        break
    fi
    print_color "✅ System running with MuJoCo viewer..." $GREEN
done
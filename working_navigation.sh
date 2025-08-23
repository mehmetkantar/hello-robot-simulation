#!/bin/bash

# Working Navigation System - Simplified and Fixed
# Focus: Get RViz goal selection working

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

cleanup_all() {
    print_color "🛑 Cleaning up..." $YELLOW
    pkill -f stretch_slam_bridge 2>/dev/null || true
    pkill -f slam_toolbox 2>/dev/null || true
    pkill -f controller_server 2>/dev/null || true
    pkill -f planner_server 2>/dev/null || true
    pkill -f bt_navigator 2>/dev/null || true
    pkill -f lifecycle_manager 2>/dev/null || true
    pkill -f rviz2 2>/dev/null || true
    sleep 3
}

trap cleanup_all EXIT INT TERM

print_color "🚀 WORKING NAVIGATION SYSTEM" $GREEN

# ROS2 setup
if [ -z "$ROS_DISTRO" ]; then
    source /opt/ros/humble/setup.bash
    export ROS_DOMAIN_ID=0
fi

cleanup_all

print_color "Step 1: Starting MuJoCo Bridge..." $GREEN
python3 stretch_slam_bridge_improved.py --complex-office --headless &
BRIDGE_PID=$!
sleep 8

print_color "Step 2: Starting Robot State Publisher..." $GREEN
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p use_sim_time:=true \
    -p robot_description:="$(cat /tmp/stretch_slam.urdf 2>/dev/null || echo '<?xml version="1.0"?><robot name="stretch"><link name="base_link"><visual><geometry><box size="0.3 0.3 0.1"/></geometry></visual></link></robot>')" &
sleep 3

print_color "Step 3: Starting SLAM Toolbox..." $GREEN
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file config/mapper_params_online_async.yaml &
sleep 6

# Wait for map to be published
print_color "Step 4: Waiting for map..." $GREEN
timeout 15s bash -c 'until ros2 topic echo /map --once >/dev/null 2>&1; do sleep 1; done' || print_color "Map timeout" $YELLOW

print_color "Step 5: Creating working Nav2 config..." $GREEN
cat > /tmp/nav2_working.yaml << 'EOF'
bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    action_server_result_timeout: 900.0
    navigators: ['navigate_to_pose', 'navigate_through_poses']
    navigate_to_pose:
      plugin: "nav2_bt_navigator/NavigateToPoseNavigator"
    navigate_through_poses:
      plugin: "nav2_bt_navigator/NavigateThroughPosesNavigator"

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 10.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]
    
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
    
    general_goal_checker:
      stateful: True
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      debug_trajectory_details: False
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 2.0
      max_vel_y: 0.0
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 2.0
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 5
      vtheta_samples: 20
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25
      trans_stopped_velocity: 0.25
      short_circuit_trajectory_evaluation: True
      stateful: True
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: True
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      robot_radius: 0.22
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 16
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      always_send_full_costmap: True

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: True
      robot_radius: 0.22
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_layer: 0.55
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
EOF

print_color "Step 6: Starting Nav2 components..." $GREEN

# Start lifecycle manager
ros2 run nav2_lifecycle_manager lifecycle_manager \
    --ros-args -p use_sim_time:=true \
    -p autostart:=true \
    -p node_names:="['controller_server', 'planner_server', 'bt_navigator']" &
sleep 2

# Start Nav2 servers
ros2 run nav2_controller controller_server \
    --ros-args --params-file /tmp/nav2_working.yaml &

ros2 run nav2_planner planner_server \
    --ros-args --params-file /tmp/nav2_working.yaml &

ros2 run nav2_bt_navigator bt_navigator \
    --ros-args --params-file /tmp/nav2_working.yaml &

sleep 8

print_color "Step 7: Starting RViz..." $GREEN
rviz2 -d rviz/stretch_navigation.rviz --ros-args -p use_sim_time:=true &
sleep 5

print_color "✅ SYSTEM READY!" $GREEN
print_color "" $NC
print_color "🎯 TEST NAVIGATION:" $YELLOW
print_color "1. In RViz: Click '2D Goal Pose' tool" $NC
print_color "2. Click on WHITE areas of the map" $NC
print_color "3. Robot should navigate autonomously" $NC
print_color "" $NC
print_color "📊 SYSTEM STATUS:" $YELLOW

# Check system status
sleep 3
ACTION_COUNT=$(ros2 action info /navigate_to_pose 2>/dev/null | grep "Action servers:" | cut -d: -f2 | xargs || echo "0")
MAP_PUBS=$(ros2 topic info /map 2>/dev/null | grep "Publisher count:" | cut -d: -f2 | xargs || echo "0")

print_color "Map publishers: $MAP_PUBS" $NC
print_color "Navigate action servers: $ACTION_COUNT" $NC

if [ "$ACTION_COUNT" = "1" ] && [ "$MAP_PUBS" = "1" ]; then
    print_color "🎉 NAVIGATION READY! Use RViz 2D Goal Pose tool" $GREEN
else
    print_color "⚠️  System starting up, wait 30 seconds and try again" $YELLOW
fi

print_color "" $NC
print_color "🛑 To stop: Press Ctrl+C" $RED

# Monitor
while true; do
    sleep 30
    if ! kill -0 $BRIDGE_PID 2>/dev/null; then
        print_color "❌ Bridge died" $RED
        break
    fi
    print_color "✅ System running..." $GREEN
done
#!/bin/bash

# Lightweight Navigation System - Performance Optimized
# Reduced resource usage for stable navigation

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

# Cleanup
cleanup_all() {
    print_color "🛑 Cleaning up..." $YELLOW
    pkill -f "stretch_slam_bridge" 2>/dev/null || true
    pkill -f "slam_toolbox" 2>/dev/null || true
    pkill -f "rviz2" 2>/dev/null || true
    pkill -f "bt_navigator" 2>/dev/null || true
    pkill -f "controller_server" 2>/dev/null || true
    pkill -f "planner_server" 2>/dev/null || true
    sleep 2
}

trap cleanup_all EXIT INT TERM

print_color "🚀 STRETCH ROBOT NAVIGATION - LITE MODE" $GREEN
print_color "Optimized for performance and stability" $YELLOW

# Check ROS2
if [ -z "$ROS_DISTRO" ]; then
    source /opt/ros/humble/setup.bash
    export ROS_DOMAIN_ID=0
fi

# Performance optimization - reduce GPU load
export MUJOCO_GL=osmesa                     # Software rendering
export MUJOCO_GPU_DEVICE_ID=""              # Disable GPU for MuJoCo
unset __NV_PRIME_RENDER_OFFLOAD             # Disable NVIDIA rendering
unset __GLX_VENDOR_LIBRARY_NAME

# Reduce CPU usage
CPU_CORES=$(nproc)
REDUCED_CORES=$((CPU_CORES/2))              # Use half cores
export OMP_NUM_THREADS=$REDUCED_CORES       

print_color "🔧 Using software rendering for stability" $YELLOW
print_color "🔧 CPU cores limited to $REDUCED_CORES/$CPU_CORES" $YELLOW

cleanup_all

print_color "🎯 Step 1: Starting MuJoCo simulation (HEADLESS)..." $GREEN
python3 stretch_slam_bridge_improved.py --complex-office --headless &
SLAM_PID=$!
sleep 8  # More time for stability

if ! kill -0 $SLAM_PID 2>/dev/null; then
    print_color "❌ Failed to start simulation" $RED
    exit 1
fi

print_color "🎯 Step 2: Starting robot state publisher..." $GREEN
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p use_sim_time:=true \
    -p robot_description:="$(cat /tmp/stretch_slam.urdf 2>/dev/null || echo '<?xml version="1.0"?><robot name="stretch"><link name="base_link"><visual><geometry><box size="0.3 0.3 0.1"/></geometry></visual></link></robot>')" &
RSP_PID=$!
sleep 3

print_color "🎯 Step 3: Starting SLAM Toolbox (REDUCED RATE)..." $GREEN
# Create performance-optimized SLAM config
cat > /tmp/slam_lite.yaml << EOF
slam_toolbox:
  ros__parameters:
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_loss_function: None
    
    odom_frame: odom
    map_frame: map
    base_frame: base_link
    scan_topic: /scan
    mode: mapping
    
    # Performance optimized settings
    debug_logging: false
    throttle_scans: 3                      # Process every 3rd scan (reduced load)
    transform_publish_period: 0.2          # 5 Hz instead of 10 Hz
    map_update_interval: 5.0               # Update every 5 seconds
    resolution: 0.06                       # Lower resolution for speed
    max_laser_range: 8.0                   # Reduced range
    minimum_time_interval: 0.5             # Less frequent updates
    transform_timeout: 0.3
    tf_buffer_duration: 10.0               # Smaller buffer
    stack_size_to_use: 40000000            # 40MB instead of 80MB
    enable_interactive_mode: true
    
    use_scan_matching: true
    use_scan_barycenter: true
    minimum_travel_distance: 0.5          # Less frequent mapping
    minimum_travel_heading: 0.6           # Less frequent mapping
    scan_buffer_size: 5                   # Smaller buffer
    scan_buffer_maximum_scan_distance: 6.0
    link_match_minimum_response_fine: 0.2
    link_scan_maximum_distance: 1.0
    loop_search_maximum_distance: 2.0
    do_loop_closing: false                # Disable for performance
    
    # Reduced correlation search
    correlation_search_space_dimension: 0.3
    correlation_search_space_resolution: 0.02
    correlation_search_space_smear_deviation: 0.05
    
    distance_variance_penalty: 0.5
    angle_variance_penalty: 1.0
    fine_search_angle_offset: 0.00349
    coarse_search_angle_offset: 0.349
    coarse_angle_resolution: 0.0349
    minimum_angle_penalty: 0.9
    minimum_distance_penalty: 0.5
    use_response_expansion: false         # Disable for performance
EOF

ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file /tmp/slam_lite.yaml &
SLAM_TOOLBOX_PID=$!
sleep 5

print_color "🎯 Step 4: Starting simplified navigation stack..." $GREEN

# Lifecycle Manager with reduced nodes
ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -p use_sim_time:=true \
    -p autostart:=true \
    -p node_names:="['controller_server', 'planner_server', 'bt_navigator']" &
LIFECYCLE_PID=$!
sleep 2

# Start core Nav2 components with reduced CPU usage
taskset -c 0-$((REDUCED_CORES-1)) ros2 run nav2_controller controller_server \
    --ros-args -p use_sim_time:=true --params-file config/nav2_params.yaml &
CONTROLLER_PID=$!

taskset -c 0-$((REDUCED_CORES-1)) ros2 run nav2_planner planner_server \
    --ros-args -p use_sim_time:=true --params-file config/nav2_params.yaml &
PLANNER_PID=$!

taskset -c 0-$((REDUCED_CORES-1)) ros2 run nav2_bt_navigator bt_navigator \
    --ros-args -p use_sim_time:=true --params-file config/nav2_params.yaml &
BT_NAVIGATOR_PID=$!

sleep 8  # Wait for Nav2 to stabilize

print_color "🎯 Step 5: Starting lightweight RViz..." $GREEN
# Start RViz with minimal configuration (software rendering)
DISPLAY=:0 rviz2 -d rviz/stretch_navigation.rviz \
    --ros-args -p use_sim_time:=true &
RVIZ_PID=$!

print_color "✅ NAVIGATION SYSTEM READY (LITE MODE)" $GREEN
print_color "" $NC
print_color "🎯 NAVIGATION CONTROLS:" $YELLOW
print_color "  • Use RViz '2D Goal Pose' tool for navigation" $NC
print_color "  • Goals will be processed with 5m/s max speed" $NC
print_color "  • System optimized for stability over performance" $NC

print_color "" $NC
print_color "🔧 PERFORMANCE OPTIMIZATIONS ACTIVE:" $YELLOW
print_color "  • Software rendering (no GPU overload)" $NC  
print_color "  • Reduced SLAM frequency (every 3rd scan)" $NC
print_color "  • Lower map resolution for speed" $NC
print_color "  • Simplified navigation stack" $NC

print_color "" $NC
print_color "📊 TO TEST NAVIGATION:" $YELLOW
print_color "  python3 simple_goal_sender.py 2.0 1.0 0.0" $NC

print_color "" $NC
print_color "🛑 TO STOP: Press Ctrl+C" $RED

# Monitor critical processes
PIDS="$SLAM_PID $RSP_PID $SLAM_TOOLBOX_PID $CONTROLLER_PID $PLANNER_PID $BT_NAVIGATOR_PID"

while true; do
    sleep 15
    
    for pid in $PIDS; do
        if [ ! -z "$pid" ] && ! kill -0 $pid 2>/dev/null; then
            print_color "⚠️  Critical process $pid died" $YELLOW
        fi
    done
    
    if ! kill -0 $SLAM_PID 2>/dev/null; then
        print_color "❌ Simulation died - exiting" $RED
        break
    fi
done
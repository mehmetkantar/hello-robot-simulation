#!/bin/bash

# Complete Stretch Robot Navigation System Launcher
# Starts: MuJoCo + SLAM + Nav2 Stack + RViz + Web Controller
# High-speed autonomous navigation with 5m/s capability

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_color() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

# Cleanup function
cleanup_all() {
    print_color "🛑 Shutting down all navigation components..." $YELLOW
    
    # Kill all related processes
    pkill -f "stretch_slam_bridge" 2>/dev/null || true
    pkill -f "simple_web_controller" 2>/dev/null || true
    pkill -f "stretch_dual_gui" 2>/dev/null || true
    pkill -f "robot_state_publisher" 2>/dev/null || true
    pkill -f "slam_toolbox" 2>/dev/null || true
    pkill -f "rviz2" 2>/dev/null || true
    
    # Kill Nav2 processes
    pkill -f "bt_navigator" 2>/dev/null || true
    pkill -f "controller_server" 2>/dev/null || true
    pkill -f "planner_server" 2>/dev/null || true
    pkill -f "behavior_server" 2>/dev/null || true
    pkill -f "smoother_server" 2>/dev/null || true
    pkill -f "velocity_smoother" 2>/dev/null || true
    pkill -f "waypoint_follower" 2>/dev/null || true
    pkill -f "lifecycle_manager" 2>/dev/null || true
    
    # Free up port 8081
    lsof -ti:8081 | xargs -r kill -9 2>/dev/null || true
    
    sleep 3
    print_color "✅ Navigation cleanup complete" $GREEN
}

# Set trap to cleanup on script exit
trap cleanup_all EXIT INT TERM

print_header "🚀 STRETCH ROBOT AUTONOMOUS NAVIGATION"
print_color "Components: MuJoCo + SLAM + Nav2 + RViz + Web Controller" $CYAN
print_color "Max Speed: 5.0 m/s with advanced obstacle avoidance" $YELLOW

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    print_color "📡 Sourcing ROS2..." $YELLOW
    source /opt/ros/humble/setup.bash
    export ROS_DOMAIN_ID=0
fi

# Set environment variables for GUI stability
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
unset CV2_QT_PATH

# Enable NVIDIA PRIME render offload for MAXIMUM GPU performance
export __NV_PRIME_RENDER_OFFLOAD=1      # Use NVIDIA GPU for rendering
export __GLX_VENDOR_LIBRARY_NAME=nvidia # Use NVIDIA OpenGL library
export MUJOCO_GL=egl                    # Use EGL backend for GPU acceleration
export MUJOCO_GPU_DEVICE_ID=0           # Use first GPU

# Maximum GPU utilization settings
export __GL_THREADED_OPTIMIZATIONS=1    # Enable threaded optimizations
export __GL_SYNC_TO_VBLANK=0            # Disable VSync for performance
export __GL_YIELD=NOTHING               # Don't yield GPU resources
export __GL_SHADER_DISK_CACHE=1         # Enable shader cache
export __GL_SHADER_DISK_CACHE_PATH=/tmp/gl_shader_cache

# CUDA optimizations for ULTRA GPU utilization
export CUDA_LAUNCH_BLOCKING=0           # Non-blocking CUDA calls
export CUDA_VISIBLE_DEVICES=0           # Use first CUDA device
export CUDA_DEVICE_ORDER=PCI_BUS_ID     # Consistent device ordering
export CUDA_CACHE_MAXSIZE=6442450944    # 6GB CUDA cache (ultra)
export CUDA_MALLOC_HEAP_SIZE=2147483648 # 2GB heap (ultra)
export CUDA_MEMORY_POOL_ENABLE=1        # Enable memory pool
export CUDA_DEVICE_MAX_CONNECTIONS=64   # Ultra GPU connections
export CUDA_FORCE_PTX_JIT=1             # Force JIT compilation
export CUDA_AUTO_BOOST=1                # Auto boost clocks
export __GL_MaxFramesAllowed=0          # No frame limiting
export __GL_FSAA_MODE=16                # 16x antialiasing

# CPU-GPU optimization for ULTRA throughput - Dynamic based on hardware
CPU_CORES=$(nproc)                      # Get actual CPU cores
export OMP_NUM_THREADS=$CPU_CORES       # Use all available cores
export MKL_NUM_THREADS=$CPU_CORES       # Intel MKL full utilization
export OPENBLAS_NUM_THREADS=$CPU_CORES  # OpenBLAS full utilization
export NUMEXPR_NUM_THREADS=$CPU_CORES   # NumExpr threading
export VECLIB_MAXIMUM_THREADS=$CPU_CORES # macOS Accelerate
export OMP_DYNAMIC=TRUE                 # Dynamic thread adjustment
export OMP_PROC_BIND=spread             # Spread threads across cores
export OMP_PLACES=cores                 # Bind to physical cores
export OMP_SCHEDULE=dynamic,1           # Dynamic scheduling

# Additional NVIDIA optimizations
export NVIDIA_TF32_OVERRIDE=0           # Use full precision

# MuJoCo specific performance optimizations
export MUJOCO_THREAD_POOL_SIZE=$CPU_CORES    # MuJoCo thread pool
export MUJOCO_BATCH_SIZE=1024                # Larger batch size
export MUJOCO_TIMESTEP=0.001                 # Faster timestep (1ms)
export MUJOCO_NITER=4                        # Fewer solver iterations for speed
export MUJOCO_TOLERANCE=1e-6                 # Looser tolerance

# System priority optimizations
export PRIORITY_CLASS=high                   # High process priority
export CPU_AFFINITY_MASK=0xFFF               # Use all CPU cores

print_color "🚀 CPU Optimization: Using all $CPU_CORES cores" $GREEN
print_color "⚡ Performance Mode: MAXIMUM + NAVIGATION" $YELLOW

print_color "🧹 Cleaning up any existing processes..." $YELLOW
cleanup_all
sleep 2

# Parse arguments
ENVIRONMENT="--complex-office"
NO_RVIZ=false
NO_WEB=false
HEADLESS=false
WEB_PORT=8081
USE_SAVED_MAP=false
MAP_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --simple)
            ENVIRONMENT="--simple"
            shift
            ;;
        --kitchen)
            ENVIRONMENT="--kitchen-world"
            shift
            ;;
        --complex-office)
            ENVIRONMENT="--complex-office"
            shift
            ;;
        --no-rviz)
            NO_RVIZ=true
            shift
            ;;
        --no-web)
            NO_WEB=true
            shift
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --port)
            WEB_PORT="$2"
            shift 2
            ;;
        --map)
            USE_SAVED_MAP=true
            MAP_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --simple           Use simple environment"
            echo "  --kitchen          Use kitchen environment"  
            echo "  --complex-office   Use complex office environment (default)"
            echo "  --no-rviz          Don't start RViz"
            echo "  --no-web           Don't start web controller"
            echo "  --headless         Run MuJoCo in headless mode (better performance)"
            echo "  --port N           Web controller port (default: 8081)"
            echo "  --map FILE         Use saved map for localization mode"
            echo "  -h, --help         Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_header "🚀 STARTING NAVIGATION SYSTEM"

# Step 1: Start MuJoCo SLAM Bridge with maximum priority
print_color "🔧 Step 1: Starting MuJoCo simulation with SLAM bridge (MAX PRIORITY)..." $GREEN
if [ "$HEADLESS" = "true" ]; then
    nice -n -20 taskset -c 0-$((CPU_CORES-1)) python3 stretch_slam_bridge_improved.py $ENVIRONMENT --headless &
else
    nice -n -20 taskset -c 0-$((CPU_CORES-1)) python3 stretch_slam_bridge_improved.py $ENVIRONMENT &
fi
SLAM_PID=$!
sleep 6  # Wait for simulation to stabilize

if ! kill -0 $SLAM_PID 2>/dev/null; then
    print_color "❌ Failed to start MuJoCo simulation" $RED
    exit 1
fi

print_color "✅ MuJoCo simulation started (PID: $SLAM_PID)" $GREEN

# Step 2: Start Robot State Publisher with high priority
print_color "🔧 Step 2: Starting robot state publisher (HIGH PRIORITY)..." $GREEN
nice -n -15 taskset -c 0-$((CPU_CORES/2-1)) ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p use_sim_time:=true \
    -p robot_description:="$(cat /tmp/stretch_slam.urdf 2>/dev/null || echo '<?xml version="1.0"?><robot name="stretch"><link name="base_link"><visual><geometry><box size="0.3 0.3 0.1"/></geometry></visual></link></robot>')" &
RSP_PID=$!
sleep 2

print_color "✅ Robot state publisher started (PID: $RSP_PID)" $GREEN

# Step 3: Start SLAM Toolbox or Map Server based on mode
if [ "$USE_SAVED_MAP" = "true" ]; then
    print_color "🔧 Step 3: Starting Map Server with saved map: $MAP_FILE..." $GREEN
    ros2 run nav2_map_server map_server --ros-args -p use_sim_time:=true -p yaml_filename:=$MAP_FILE &
    MAP_SERVER_PID=$!
    sleep 2
    
    # Start AMCL for localization
    print_color "🔧 Step 3b: Starting AMCL for localization..." $GREEN
    ros2 run nav2_amcl amcl --ros-args -p use_sim_time:=true &
    AMCL_PID=$!
    sleep 3
    
    print_color "✅ Map server and AMCL started" $GREEN
else
    print_color "🔧 Step 3: Starting SLAM Toolbox (FIXED)..." $GREEN
    # Start SLAM Toolbox without problematic nice/taskset commands
    ros2 run slam_toolbox async_slam_toolbox_node \
        --ros-args -p use_sim_time:=true \
        --params-file config/mapper_params_online_async.yaml \
        --log-level WARN &
    SLAM_TOOLBOX_PID=$!
    sleep 8  # More time for SLAM to initialize properly
    
    print_color "✅ SLAM Toolbox started with queue optimization (PID: $SLAM_TOOLBOX_PID)" $GREEN
fi

# Step 4: Start Nav2 Lifecycle Manager
print_color "🔧 Step 4: Starting Nav2 Lifecycle Manager..." $GREEN
ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -p use_sim_time:=true \
    -p autostart:=true \
    -p node_names:="['controller_server', 'planner_server', 'behavior_server', 'bt_navigator', 'waypoint_follower', 'velocity_smoother', 'smoother_server']" &
LIFECYCLE_PID=$!
sleep 2

print_color "✅ Lifecycle Manager started (PID: $LIFECYCLE_PID)" $GREEN

# Step 5: Start Nav2 Core Components
print_color "🔧 Step 5: Starting Nav2 core navigation components..." $GREEN

# Controller Server (DWB Local Planner)
ros2 run nav2_controller controller_server --ros-args -p use_sim_time:=true \
    --params-file config/nav2_params.yaml &
CONTROLLER_PID=$!

# Planner Server (Global Path Planner) 
ros2 run nav2_planner planner_server --ros-args -p use_sim_time:=true \
    --params-file config/nav2_params.yaml &
PLANNER_PID=$!

# Behavior Server (Recovery Behaviors)
ros2 run nav2_behaviors behavior_server --ros-args -p use_sim_time:=true \
    --params-file config/nav2_params.yaml &
BEHAVIOR_PID=$!

# BT Navigator (Main Navigation Logic)
ros2 run nav2_bt_navigator bt_navigator --ros-args -p use_sim_time:=true \
    --params-file config/nav2_params.yaml &
BT_NAVIGATOR_PID=$!

# Waypoint Follower
ros2 run nav2_waypoint_follower waypoint_follower --ros-args -p use_sim_time:=true \
    --params-file config/nav2_params.yaml &
WAYPOINT_PID=$!

# Velocity Smoother for 5m/s operation
ros2 run nav2_velocity_smoother velocity_smoother --ros-args -p use_sim_time:=true \
    --params-file config/nav2_params.yaml &
VELOCITY_SMOOTHER_PID=$!

# Path Smoother for high-speed navigation
ros2 run nav2_smoother smoother_server --ros-args -p use_sim_time:=true \
    --params-file config/nav2_params.yaml &
SMOOTHER_PID=$!

sleep 5  # Give Nav2 components time to start

print_color "✅ Nav2 navigation stack started" $GREEN

# Step 6: Start RViz with Navigation Configuration (if not disabled)
if [ "$NO_RVIZ" != "true" ]; then
    print_color "🔧 Step 6: Starting RViz with Navigation visualization..." $GREEN
    # Use Intel GPU for RViz compatibility
    env -u __NV_PRIME_RENDER_OFFLOAD -u __GLX_VENDOR_LIBRARY_NAME \
        rviz2 -d rviz/stretch_navigation.rviz --ros-args -p use_sim_time:=true &
    RVIZ_PID=$!
    sleep 3
    print_color "✅ RViz navigation started (PID: $RVIZ_PID)" $GREEN
else
    print_color "⏭️  Step 6: RViz disabled" $YELLOW
fi

# Step 7: Start Web Controller (if not disabled)
if [ "$NO_WEB" != "true" ]; then
    print_color "🔧 Step 7: Starting web controller..." $GREEN
    
    # Update port in web controller if different
    if [ "$WEB_PORT" != "8081" ]; then
        sed -i "s/localhost, 808[0-9]/localhost, $WEB_PORT/g" simple_web_controller.py
        sed -i "s/localhost:808[0-9]/localhost:$WEB_PORT/g" simple_web_controller.py
    fi
    
    # Ensure port is free before starting
    lsof -ti:$WEB_PORT | xargs -r kill -9 2>/dev/null || true
    sleep 1
    
    python3 simple_web_controller.py &
    WEB_PID=$!
    sleep 5
    
    if kill -0 $WEB_PID 2>/dev/null; then
        print_color "✅ Web controller started (PID: $WEB_PID)" $GREEN
    else
        print_color "⚠️  Web controller failed to start" $YELLOW
        WEB_PID=""
    fi
else
    print_color "⏭️  Step 7: Web controller disabled" $YELLOW
fi

print_header "🎉 AUTONOMOUS NAVIGATION SYSTEM READY!"

print_color "" $NC
print_color "📺 WINDOWS YOU SHOULD SEE:" $PURPLE
print_color "  🏢 MuJoCo: 3D physics simulation with robot in office environment" $CYAN
if [ "$USE_SAVED_MAP" = "true" ]; then
    print_color "  📊 RViz: Robot model, costmaps, global/local plans, and localization" $CYAN
else
    print_color "  📊 RViz: Robot model, costmaps, global/local plans, and real-time mapping" $CYAN
fi
if [ "$NO_WEB" != "true" ]; then
    print_color "  🌐 Web Browser: http://localhost:$WEB_PORT (robot control interface)" $CYAN
fi

print_color "" $NC
print_color "🎯 AUTONOMOUS NAVIGATION:" $PURPLE
print_color "  • Use RViz '2D Nav Goal' tool to set navigation targets" $CYAN
print_color "  • Robot will autonomously navigate avoiding obstacles" $CYAN
print_color "  • Max speed: 5.0 m/s with advanced path planning" $CYAN
print_color "  • Real-time obstacle avoidance with DWB local planner" $CYAN

print_color "" $NC
print_color "🎮 MANUAL CONTROL (if needed):" $PURPLE
if [ "$NO_WEB" != "true" ]; then
    print_color "  • Web interface: http://localhost:$WEB_PORT" $CYAN
else
    print_color "  • Use: ros2 run teleop_twist_keyboard teleop_twist_keyboard" $CYAN
fi

print_color "" $NC
print_color "📍 MAPPING & LOCALIZATION:" $PURPLE
if [ "$USE_SAVED_MAP" = "true" ]; then
    print_color "  • Using saved map: $MAP_FILE" $CYAN
    print_color "  • AMCL provides localization in known environment" $CYAN
else
    print_color "  • Simultaneous mapping and navigation (SLAM)" $CYAN
    print_color "  • Save map: ros2 run nav2_map_server map_saver_cli -f my_nav_map" $CYAN
fi

print_color "" $NC
print_color "🧭 NAVIGATION COMMANDS:" $PURPLE
print_color "  • Set goal in RViz: Click '2D Nav Goal' tool and click on map" $CYAN
print_color "  • Terminal goal: ros2 action send_goal /navigate_to_pose ..." $CYAN
print_color "  • Cancel goal: ros2 action send_goal /navigate_to_pose --cancel" $CYAN

print_color "" $NC
print_color "🔧 DEBUGGING:" $PURPLE
print_color "  • Monitor topics: ros2 topic list | grep nav" $CYAN
print_color "  • Check costmaps: ros2 topic echo /local_costmap/costmap" $CYAN
print_color "  • View plans: ros2 topic echo /plan" $CYAN
print_color "  • Navigation status: ros2 topic echo /navigate_to_pose/_action/status" $CYAN

print_color "" $NC
print_color "🛑 TO STOP: Press Ctrl+C in this terminal" $RED
print_color "" $NC

# Monitor all processes and keep running
print_color "⏳ Monitoring navigation system... Press Ctrl+C to stop" $GREEN

# Store all PIDs for monitoring
PIDS="$SLAM_PID $RSP_PID $LIFECYCLE_PID $CONTROLLER_PID $PLANNER_PID $BEHAVIOR_PID $BT_NAVIGATOR_PID $WAYPOINT_PID $VELOCITY_SMOOTHER_PID $SMOOTHER_PID"

if [ "$USE_SAVED_MAP" = "true" ]; then
    PIDS="$PIDS $MAP_SERVER_PID $AMCL_PID"
else
    PIDS="$PIDS $SLAM_TOOLBOX_PID"
fi

[ "$NO_RVIZ" != "true" ] && PIDS="$PIDS $RVIZ_PID"
[ "$NO_WEB" != "true" ] && [ ! -z "$WEB_PID" ] && PIDS="$PIDS $WEB_PID"

# System monitoring loop
while true; do
    sleep 10
    
    # Check if critical processes are still running
    for pid in $PIDS; do
        if [ ! -z "$pid" ] && ! kill -0 $pid 2>/dev/null; then
            print_color "⚠️  Process $pid died unexpectedly" $YELLOW
        fi
    done
    
    # Check if SLAM bridge (most critical) is still running
    if ! kill -0 $SLAM_PID 2>/dev/null; then
        print_color "❌ MuJoCo simulation died - navigation system cannot continue" $RED
        break
    fi
    
    # Check if BT Navigator is running (critical for navigation)
    if ! kill -0 $BT_NAVIGATOR_PID 2>/dev/null; then
        print_color "⚠️  BT Navigator died - autonomous navigation disabled" $YELLOW
    fi
done
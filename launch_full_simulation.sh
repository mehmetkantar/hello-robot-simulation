#!/bin/bash

# Complete Stretch Robot Simulation Launcher
# Starts: MuJoCo + SLAM + RViz + Web Controller

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
    print_color "🛑 Shutting down all simulation components..." $YELLOW
    
    # Kill all related processes
    pkill -f "stretch_slam_bridge" 2>/dev/null || true
    pkill -f "simple_web_controller" 2>/dev/null || true
    pkill -f "stretch_dual_gui" 2>/dev/null || true
    pkill -f "robot_state_publisher" 2>/dev/null || true
    pkill -f "slam_toolbox" 2>/dev/null || true
    pkill -f "rviz2" 2>/dev/null || true
    
    # Free up port 8081
    lsof -ti:8081 | xargs -r kill -9 2>/dev/null || true
    
    sleep 3
    print_color "✅ Simulation cleanup complete" $GREEN
}

# Set trap to cleanup on script exit
trap cleanup_all EXIT INT TERM

print_header "🤖 STRETCH ROBOT FULL SIMULATION"
print_color "Components: MuJoCo + SLAM + RViz + Web Controller" $CYAN

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

# CPU-GPU optimization for ULTRA throughput
export OMP_NUM_THREADS=16               # Ultra multi-threading
export MKL_NUM_THREADS=16               # Intel MKL ultra threading
export OPENBLAS_NUM_THREADS=16          # OpenBLAS ultra threading
export OMP_DYNAMIC=TRUE                 # Dynamic thread adjustment

# Additional NVIDIA optimizations
export NVIDIA_TF32_OVERRIDE=0           # Use full precision

print_color "🧹 Cleaning up any existing processes..." $YELLOW
cleanup_all
sleep 2

# Parse arguments
ENVIRONMENT="--complex-office"
NO_RVIZ=false
NO_WEB=false
HEADLESS=false
WEB_PORT=8081

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
            echo "  -h, --help         Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_header "🚀 STARTING SIMULATION COMPONENTS"

# Step 1: Start MuJoCo SLAM Bridge
print_color "🔧 Step 1: Starting MuJoCo simulation with SLAM bridge..." $GREEN
if [ "$HEADLESS" = "true" ]; then
    python3 stretch_slam_bridge_improved.py $ENVIRONMENT --headless &
else
    python3 stretch_slam_bridge_improved.py $ENVIRONMENT &
fi
SLAM_PID=$!
sleep 8

if ! kill -0 $SLAM_PID 2>/dev/null; then
    print_color "❌ Failed to start MuJoCo simulation" $RED
    exit 1
fi

print_color "✅ MuJoCo simulation started (PID: $SLAM_PID)" $GREEN

# Step 2: Start Robot State Publisher
print_color "🔧 Step 2: Starting robot state publisher..." $GREEN
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p use_sim_time:=true \
    -p robot_description:="$(cat /tmp/stretch_slam.urdf 2>/dev/null || echo '<?xml version="1.0"?><robot name="stretch"><link name="base_link"><visual><geometry><box size="0.3 0.3 0.1"/></geometry></visual></link></robot>')" &
RSP_PID=$!
sleep 3

print_color "✅ Robot state publisher started (PID: $RSP_PID)" $GREEN

# Step 3: Start SLAM Toolbox
print_color "🔧 Step 3: Starting SLAM Toolbox..." $GREEN
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args -p use_sim_time:=true \
    --params-file config/mapper_params_online_async.yaml &
SLAM_TOOLBOX_PID=$!
sleep 4

print_color "✅ SLAM Toolbox started (PID: $SLAM_TOOLBOX_PID)" $GREEN

# Step 4: Start RViz (if not disabled) - Use Intel GPU for compatibility
if [ "$NO_RVIZ" != "true" ]; then
    print_color "🔧 Step 4: Starting RViz visualization (Intel GPU)..." $GREEN
    # Temporarily disable NVIDIA PRIME for RViz to avoid compatibility issues
    env -u __NV_PRIME_RENDER_OFFLOAD -u __GLX_VENDOR_LIBRARY_NAME \
        rviz2 -d rviz/stretch_slam.rviz --ros-args -p use_sim_time:=true &
    RVIZ_PID=$!
    sleep 3
    print_color "✅ RViz started with Intel GPU (PID: $RVIZ_PID)" $GREEN
else
    print_color "⏭️  Step 4: RViz disabled" $YELLOW
fi

# Step 5: Start Web Controller (if not disabled)
if [ "$NO_WEB" != "true" ]; then
    print_color "🔧 Step 5: Starting web controller..." $GREEN
    
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
    sleep 5  # Give more time for web controller to start
    
    if kill -0 $WEB_PID 2>/dev/null; then
        print_color "✅ Web controller started (PID: $WEB_PID)" $GREEN
    else
        print_color "⚠️  Web controller failed to start" $YELLOW
        WEB_PID=""
    fi
else
    print_color "⏭️  Step 5: Web controller disabled" $YELLOW
fi

print_header "🎉 FULL SIMULATION READY!"

print_color "" $NC
print_color "📺 WINDOWS YOU SHOULD SEE:" $PURPLE
print_color "  🏢 MuJoCo: 3D physics simulation with robot in office environment" $CYAN
print_color "  📊 RViz: Robot model, laser scans, and real-time map building" $CYAN
if [ "$NO_WEB" != "true" ]; then
    print_color "  🌐 Web Browser: http://localhost:$WEB_PORT (robot control interface)" $CYAN
fi

print_color "" $NC
print_color "🎮 ROBOT CONTROL:" $PURPLE
if [ "$NO_WEB" != "true" ]; then
    print_color "  • Open http://localhost:$WEB_PORT in your web browser" $CYAN
    print_color "  • Use the control buttons to move the robot" $CYAN
    print_color "  • Adjust speed with the slider" $CYAN
else
    print_color "  • Use: ros2 run teleop_twist_keyboard teleop_twist_keyboard" $CYAN
fi

print_color "" $NC
print_color "📍 SLAM MAPPING:" $PURPLE
print_color "  • Drive the robot around to explore the environment" $CYAN
print_color "  • Watch the map being built in RViz in real-time" $CYAN
print_color "  • Save map: ros2 run nav2_map_server map_saver_cli -f my_map" $CYAN

print_color "" $NC
print_color "🔧 DEBUGGING:" $PURPLE
print_color "  • Monitor topics: ros2 topic list" $CYAN
print_color "  • Check laser: ros2 topic echo /scan" $CYAN
print_color "  • Check odometry: ros2 topic echo /odom" $CYAN

print_color "" $NC
print_color "🛑 TO STOP: Press Ctrl+C in this terminal" $RED
print_color "" $NC

# Monitor all processes and keep running
print_color "⏳ Monitoring simulation... Press Ctrl+C to stop" $GREEN

# Store all PIDs for monitoring
PIDS="$SLAM_PID $RSP_PID $SLAM_TOOLBOX_PID"
[ "$NO_RVIZ" != "true" ] && PIDS="$PIDS $RVIZ_PID"
[ "$NO_WEB" != "true" ] && [ ! -z "$WEB_PID" ] && PIDS="$PIDS $WEB_PID"

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
        print_color "❌ MuJoCo simulation died - restarting simulation recommended" $RED
        break
    fi
done
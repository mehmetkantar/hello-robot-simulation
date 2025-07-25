#!/bin/bash

# Optimized Stretch Robot Launcher
# Uses copied assets from ~/Downloads/assets/

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
    print_color "🛑 Shutting down optimized robot simulation..." $YELLOW
    
    # Kill processes
    pkill -f "stretch_optimized_bridge" 2>/dev/null || true
    pkill -f "robot_state_publisher" 2>/dev/null || true
    pkill -f "slam_toolbox" 2>/dev/null || true
    pkill -f "rviz2" 2>/dev/null || true
    
    sleep 2
    print_color "✅ Optimized robot cleanup complete" $GREEN
}

# Set trap to cleanup on script exit
trap cleanup_all EXIT INT TERM

print_header "🚀 OPTIMIZED STRETCH ROBOT"
print_color "Assets: Using copied meshes from ~/Downloads/assets/" $CYAN
print_color "Expected: 5-20x faster than original robot" $CYAN

# Check if assets exist
if [ ! -d "$HOME/Downloads/assets" ]; then
    print_color "❌ Assets not found at ~/Downloads/assets/" $RED
    print_color "Please run the asset copying process first." $RED
    exit 1
fi

# Check asset count
ASSET_COUNT=$(ls ~/Downloads/assets/*.obj ~/Downloads/assets/*.stl 2>/dev/null | wc -l)
print_color "📁 Found $ASSET_COUNT mesh files in ~/Downloads/assets/" $CYAN

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    print_color "📡 Sourcing ROS2..." $YELLOW
    source /opt/ros/humble/setup.bash
    export ROS_DOMAIN_ID=0
fi

# Parse arguments
HEADLESS=false
NO_RVIZ=false
NO_SLAM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless)
            HEADLESS=true
            shift
            ;;
        --no-rviz)
            NO_RVIZ=true
            shift
            ;;
        --no-slam)
            NO_SLAM=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --headless         Run without MuJoCo viewer (fastest)"
            echo "  --no-rviz          Don't start RViz"
            echo "  --no-slam          Don't start SLAM (robot only)"
            echo "  -h, --help         Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_color "🧹 Cleaning up any existing processes..." $YELLOW
cleanup_all
sleep 1

print_header "🚀 STARTING OPTIMIZED SIMULATION"

# Step 1: Start Optimized Stretch Robot
print_color "🔧 Step 1: Starting optimized Stretch robot..." $GREEN
if [ "$HEADLESS" = "true" ]; then
    python3 stretch_optimized_bridge.py --headless &
else
    python3 stretch_optimized_bridge.py &
fi
ROBOT_PID=$!
sleep 4

if ! kill -0 $ROBOT_PID 2>/dev/null; then
    print_color "❌ Failed to start optimized robot" $RED
    exit 1
fi

print_color "✅ Optimized robot started (PID: $ROBOT_PID)" $GREEN

# Step 2: Start Robot State Publisher (if SLAM enabled)
if [ "$NO_SLAM" != "true" ]; then
    print_color "🔧 Step 2: Starting robot state publisher..." $GREEN
    
    # Create optimized URDF on the fly
    cat > /tmp/stretch_optimized.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="stretch_optimized">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.68 0.5 0.3"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.6 0.8 1"/>
      </material>
    </visual>
  </link>
  <link name="laser">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.03"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
  </link>
  <joint name="laser_joint" type="fixed">
    <parent link="base_link"/>
    <child link="laser"/>
    <origin xyz="0.05 0 0.3"/>
  </joint>
</robot>
EOF
    
    ros2 run robot_state_publisher robot_state_publisher \
        --ros-args -p use_sim_time:=false \
        -p robot_description:="$(cat /tmp/stretch_optimized.urdf)" &
    RSP_PID=$!
    sleep 2
    
    print_color "✅ Robot state publisher started (PID: $RSP_PID)" $GREEN
    
    # Step 3: Start SLAM Toolbox
    print_color "🔧 Step 3: Starting SLAM Toolbox..." $GREEN
    ros2 run slam_toolbox async_slam_toolbox_node \
        --ros-args -p use_sim_time:=false \
        --params-file config/mapper_params_online_async.yaml &
    SLAM_PID=$!
    sleep 3
    
    print_color "✅ SLAM Toolbox started (PID: $SLAM_PID)" $GREEN
fi

# Step 4: Start RViz (if requested)
if [ "$NO_RVIZ" != "true" ] && [ "$NO_SLAM" != "true" ]; then
    print_color "🔧 Step 4: Starting RViz..." $GREEN
    rviz2 -d rviz/stretch_slam.rviz --ros-args -p use_sim_time:=false &
    RVIZ_PID=$!
    sleep 2
    print_color "✅ RViz started (PID: $RVIZ_PID)" $GREEN
else
    print_color "⏭️  Step 4: RViz/SLAM disabled" $YELLOW
fi

print_header "🎉 OPTIMIZED STRETCH READY!"

print_color "" $NC
print_color "📺 YOU SHOULD SEE:" $PURPLE
if [ "$HEADLESS" != "true" ]; then
    print_color "  🤖 MuJoCo: Optimized Stretch robot (reduced mesh complexity)" $CYAN
fi
if [ "$NO_RVIZ" != "true" ] && [ "$NO_SLAM" != "true" ]; then
    print_color "  📊 RViz: Robot model and laser scans" $CYAN
fi

print_color "" $NC
print_color "🎮 ROBOT CONTROL:" $PURPLE
print_color "  • ros2 run teleop_twist_keyboard teleop_twist_keyboard" $CYAN
print_color "  • Use arrow keys to move the robot" $CYAN

if [ "$NO_SLAM" != "true" ]; then
    print_color "" $NC
    print_color "📍 SLAM MAPPING:" $PURPLE
    print_color "  • Drive robot around to map the environment" $CYAN
    print_color "  • Watch map building in RViz" $CYAN
    print_color "  • Save map: ros2 run nav2_map_server map_saver_cli -f optimized_map" $CYAN
fi

print_color "" $NC
print_color "🔧 PERFORMANCE MONITORING:" $PURPLE
print_color "  • Check terminal for real-time performance ratios" $CYAN
print_color "  • Expected: 0.5x - 5.0x real-time (much faster!)" $CYAN
print_color "  • Assets from: ~/Downloads/assets/ (can be mesh-optimized)" $CYAN

print_color "" $NC
print_color "💡 OPTIMIZATION TIPS:" $PURPLE
print_color "  • Use --headless for maximum speed" $CYAN
print_color "  • Optimize meshes at: https://myminifactory.github.io/Fast-Quadric-Mesh-Simplification/" $CYAN
print_color "  • Replace large .obj files in ~/Downloads/assets/" $CYAN

print_color "" $NC
print_color "🛑 TO STOP: Press Ctrl+C in this terminal" $RED
print_color "" $NC

# Monitor processes
print_color "⏳ Monitoring optimized robot... Press Ctrl+C to stop" $GREEN

while true; do
    sleep 5
    
    # Check if robot is still running
    if ! kill -0 $ROBOT_PID 2>/dev/null; then
        print_color "❌ Optimized robot died - exiting" $RED
        break
    fi
done
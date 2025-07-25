#!/bin/bash

# Hybrid Stretch Robot Full Simulation Launcher
# Simplified cylindrical base + Original upper components
# Expected: 2-10x performance improvement

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
    print_color "🛑 Shutting down hybrid simulation..." $YELLOW
    
    # Kill all related processes - more aggressive approach
    pkill -f "stretch_hybrid_slam_bridge" 2>/dev/null || true
    pkill -f "stretch_hybrid_bridge" 2>/dev/null || true
    pkill -f "simple_web_controller" 2>/dev/null || true
    pkill -f "robot_state_publisher" 2>/dev/null || true
    pkill -f "slam_toolbox" 2>/dev/null || true
    pkill -f "rviz2" 2>/dev/null || true
    
    sleep 2
    
    # Force kill any remaining processes
    ps aux | grep -E "(stretch_hybrid|robot_state|slam_toolbox|rviz2|simple_web_controller)" | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true
    
    # Free up port 8081
    lsof -ti:8081 | xargs -r kill -9 2>/dev/null || true
    
    # Clean ROS2 daemon
    ros2 daemon stop 2>/dev/null || true
    sleep 1
    ros2 daemon start 2>/dev/null || true
    
    sleep 2
    print_color "✅ Hybrid simulation cleanup complete" $GREEN
}

# Function to check for existing processes
check_existing_processes() {
    EXISTING=$(ps aux | grep -E "(stretch_hybrid|robot_state|slam_toolbox|rviz2)" | grep -v grep | wc -l)
    if [ "$EXISTING" -gt 0 ]; then
        print_color "⚠️  Found $EXISTING existing simulation processes - cleaning up..." $YELLOW
        cleanup_all
        sleep 3
    fi
}

# Set trap to cleanup on script exit
trap cleanup_all EXIT INT TERM

print_header "🤖 HYBRID STRETCH ROBOT SIMULATION"
print_color "Architecture: Simplified Base + Original Upper Components" $CYAN
print_color "Expected Performance: 2-10x improvement" $CYAN

# Check for existing processes first
check_existing_processes

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
            echo "  --headless         Run MuJoCo in headless mode (best performance)"
            echo "  --port N           Web controller port (default: 8081)"
            echo "  -h, --help         Show this help"
            echo ""
            echo "🤖 HYBRID MODEL: Simplified base + original upper robot"
            echo "Expected: 2-10x performance improvement over full model"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_header "🚀 STARTING HYBRID SIMULATION COMPONENTS"

# Step 1: Start Hybrid SLAM Bridge (stretch_mujoco + hybrid model)
print_color "🔧 Step 1: Starting hybrid SLAM bridge..." $GREEN
if [ "$HEADLESS" = "true" ]; then
    python3 stretch_hybrid_slam_bridge.py $ENVIRONMENT --headless &
else
    python3 stretch_hybrid_slam_bridge.py $ENVIRONMENT &
fi
HYBRID_PID=$!
sleep 8

if ! kill -0 $HYBRID_PID 2>/dev/null; then
    print_color "❌ Failed to start hybrid simulation" $RED
    exit 1
fi

print_color "✅ Hybrid simulation started (PID: $HYBRID_PID)" $GREEN

# Step 2: Start Robot State Publisher
print_color "🔧 Step 2: Starting robot state publisher..." $GREEN

# Use original Stretch URDF for proper RViz visualization
URDF_PATH="/home/user/.local/lib/python3.10/site-packages/stretch_urdf/SE3/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"

if [ -f "$URDF_PATH" ]; then
    print_color "✅ Using original Stretch URDF for full robot visualization" $GREEN
    ros2 run robot_state_publisher robot_state_publisher \
        --ros-args -p use_sim_time:=true \
        -p robot_description:="$(cat $URDF_PATH)" &
else
    print_color "⚠️  Original URDF not found, using simplified version" $YELLOW
    # Fallback URDF with all major components
    cat > /tmp/stretch_hybrid_full.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="stretch_hybrid">
  <!-- Base link -->
  <link name="base_link"/>
  
  <!-- Mast -->
  <link name="link_mast"/>
  <joint name="joint_mast" type="fixed">
    <parent link="base_link"/>
    <child link="link_mast"/>
    <origin xyz="-0.067 0.135 0.0284"/>
  </joint>
  
  <!-- Lift -->
  <link name="link_lift"/>
  <joint name="joint_lift" type="prismatic">
    <parent link="link_mast"/>  
    <child link="link_lift"/>
    <origin xyz="-0.037385 -0.000001 0.17159"/>
    <axis xyz="0 0 1"/>
    <limit lower="0.0" upper="1.1" effort="50" velocity="0.2"/>
  </joint>
  
  <!-- Head pan -->
  <link name="link_head_pan"/>
  <joint name="joint_head_pan" type="revolute">
    <parent link="link_lift"/>
    <child link="link_head_pan"/>
    <origin xyz="0.13395 -0.000005 1.1568"/>
    <axis xyz="0 0 1"/>
    <limit lower="-4.04" upper="1.73" effort="10" velocity="1.0"/>
  </joint>
  
  <!-- Head tilt -->
  <link name="link_head_tilt"/>
  <joint name="joint_head_tilt" type="revolute">
    <parent link="link_head_pan"/>
    <child link="link_head_tilt"/>
    <origin xyz="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.53" upper="0.79" effort="10" velocity="1.0"/>
  </joint>
  
  <!-- LIDAR -->
  <link name="laser">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.06"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
  </link>
  <joint name="laser_joint" type="fixed">
    <parent link="base_link"/>
    <child link="laser"/>
    <origin xyz="0.004 0 0.1664"/>
  </joint>
  
  <!-- Arm l4 -->
  <link name="link_arm_l4"/>
  <joint name="joint_arm_l4" type="prismatic">
    <parent link="link_lift"/>
    <child link="link_arm_l4"/>
    <origin xyz="0.06478 0.000003 0.41821"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="56" velocity="0.2"/>
  </joint>
  
  <!-- Arm l3 -->
  <link name="link_arm_l3"/>
  <joint name="joint_arm_l3" type="prismatic">
    <parent link="link_arm_l4"/>
    <child link="link_arm_l3"/>
    <origin xyz="0.13 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="56" velocity="0.2"/>
  </joint>
  
  <!-- Arm l2 -->
  <link name="link_arm_l2"/>
  <joint name="joint_arm_l2" type="prismatic">
    <parent link="link_arm_l3"/>
    <child link="link_arm_l2"/>
    <origin xyz="0.13 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="56" velocity="0.2"/>
  </joint>
  
  <!-- Arm l1 -->
  <link name="link_arm_l1"/>
  <joint name="joint_arm_l1" type="prismatic">
    <parent link="link_arm_l2"/>
    <child link="link_arm_l1"/>
    <origin xyz="0.13 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="56" velocity="0.2"/>
  </joint>
  
  <!-- Arm l0 -->
  <link name="link_arm_l0"/>
  <joint name="joint_arm_l0" type="prismatic">
    <parent link="link_arm_l1"/>
    <child link="link_arm_l0"/>
    <origin xyz="0.13 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.13" effort="56" velocity="0.2"/>
  </joint>
  
  <!-- Wrist yaw -->
  <link name="link_wrist_yaw"/>
  <joint name="joint_wrist_yaw" type="revolute">
    <parent link="link_arm_l0"/>
    <child link="link_wrist_yaw"/>
    <origin xyz="0.13 0 0"/>
    <axis xyz="0 0 -1"/>
    <limit lower="-1.39" upper="4.42" effort="20" velocity="1.0"/>
  </joint>
  
  <!-- Wrist pitch -->
  <link name="link_wrist_pitch"/>
  <joint name="joint_wrist_pitch" type="revolute">
    <parent link="link_wrist_yaw"/>
    <child link="link_wrist_pitch"/>
    <origin xyz="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="0.56" effort="50" velocity="1.0"/>
  </joint>
  
  <!-- Wrist roll -->
  <link name="link_wrist_roll"/>
  <joint name="joint_wrist_roll" type="revolute">
    <parent link="link_wrist_pitch"/>
    <child link="link_wrist_roll"/>
    <origin xyz="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.75" upper="1.61" effort="30" velocity="1.0"/>
  </joint>
  
  <!-- Gripper -->
  <link name="link_gripper"/>
  <joint name="joint_gripper_slide" type="prismatic">
    <parent link="link_wrist_roll"/>
    <child link="link_gripper"/>
    <origin xyz="0.043 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-0.02" upper="0.04" effort="100" velocity="0.1"/>
  </joint>
  
  <!-- D435i Camera frames -->
  <link name="camera_link"/>
  <joint name="camera_joint" type="fixed">
    <parent link="link_head_tilt"/>
    <child link="camera_link"/>
    <origin xyz="0.0406 0.0053 0.0307"/>
  </joint>
  
  <link name="camera_color_frame"/>
  <joint name="camera_color_joint" type="fixed">
    <parent link="camera_link"/>
    <child link="camera_color_frame"/>
    <origin xyz="0 0.015 0" rpy="1.57 -1.57 0"/>
  </joint>
  
  <!-- D405 Gripper Camera -->
  <link name="gripper_camera_link"/>
  <joint name="gripper_camera_joint" type="fixed">
    <parent link="link_gripper"/>
    <child link="gripper_camera_link"/>
    <origin xyz="0.05 -0.03068 0" rpy="1.57 0 0"/>
  </joint>
  
  <!-- Nav Camera -->
  <link name="nav_camera_link"/>
  <joint name="nav_camera_joint" type="fixed">
    <parent link="link_head_tilt"/>
    <child link="nav_camera_link"/>
    <origin xyz="0.04 -0.0412 -0.0246" rpy="0 1.5707963 0"/>
  </joint>
</robot>
EOF
    ros2 run robot_state_publisher robot_state_publisher \
        --ros-args -p use_sim_time:=true \
        -p robot_description:="$(cat /tmp/stretch_hybrid_full.urdf)" &
fi
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

# Step 4: Start RViz
if [ "$NO_RVIZ" != "true" ]; then
    print_color "🔧 Step 4: Starting RViz visualization..." $GREEN
    rviz2 -d rviz/stretch_slam.rviz --ros-args -p use_sim_time:=true &
    RVIZ_PID=$!
    sleep 3
    print_color "✅ RViz started (PID: $RVIZ_PID)" $GREEN
else
    print_color "⏭️  Step 4: RViz disabled" $YELLOW
fi

# Step 5: Start Web Controller
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
    sleep 5
    
    if kill -0 $WEB_PID 2>/dev/null; then
        print_color "✅ Web controller started (PID: $WEB_PID)" $GREEN
    else
        print_color "⚠️  Web controller failed to start" $YELLOW
        WEB_PID=""
    fi
else
    print_color "⏭️  Step 5: Web controller disabled" $YELLOW
fi

print_header "🎉 HYBRID STRETCH ROBOT READY!"

print_color "" $NC
print_color "📺 WINDOWS YOU SHOULD SEE:" $PURPLE
print_color "  🤖 MuJoCo: Hybrid robot (simple base + full upper robot)" $CYAN
print_color "  📊 RViz: Robot model, laser scans, and real-time SLAM map" $CYAN
if [ "$NO_WEB" != "true" ]; then
    print_color "  🌐 Web Browser: http://localhost:$WEB_PORT (robot control)" $CYAN
fi

print_color "" $NC
print_color "🚀 HYBRID OPTIMIZATION:" $PURPLE
print_color "  • Base: Single cylinder (massive performance boost)" $CYAN
print_color "  • Upper: Full original robot (cameras, arm, sensors)" $CYAN
print_color "  • LIDAR: 180 rays (2° resolution) for balanced performance" $CYAN
print_color "  • Expected: 2-10x faster than original robot" $CYAN

print_color "" $NC
print_color "🎮 ROBOT CONTROL:" $PURPLE
if [ "$NO_WEB" != "true" ]; then
    print_color "  • Web: http://localhost:$WEB_PORT (recommended)" $CYAN
else
    print_color "  • Terminal: ros2 run teleop_twist_keyboard teleop_twist_keyboard" $CYAN
fi
print_color "  • All original robot joints and sensors active" $CYAN

print_color "" $NC
print_color "📍 SLAM MAPPING:" $PURPLE
print_color "  • Drive robot to explore $ENVIRONMENT environment" $CYAN
print_color "  • Watch real-time map building in RViz" $CYAN
print_color "  • Save map: ros2 run nav2_map_server map_saver_cli -f hybrid_map" $CYAN

print_color "" $NC
print_color "🔧 MONITORING:" $PURPLE
print_color "  • Performance: Check terminal for real-time ratios" $CYAN
print_color "  • Topics: ros2 topic list" $CYAN
print_color "  • Laser: ros2 topic echo /scan" $CYAN
print_color "  • Joints: ros2 topic echo /joint_states" $CYAN

print_color "" $NC
print_color "💡 PERFORMANCE NOTES:" $PURPLE
print_color "  • Simplified base: 129 meshes → 1 cylinder" $CYAN
print_color "  • Upper robot: All original components preserved" $CYAN
print_color "  • Best performance: Use --headless flag" $CYAN
print_color "  • All cameras and sensors fully functional" $CYAN

print_color "" $NC
print_color "🛑 TO STOP: Press Ctrl+C in this terminal" $RED
print_color "" $NC

# Monitor all processes and keep running
print_color "⏳ Monitoring hybrid simulation... Press Ctrl+C to stop" $GREEN

# Store all PIDs for monitoring
PIDS="$HYBRID_PID $RSP_PID $SLAM_TOOLBOX_PID"
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
    
    # Check if hybrid bridge (most critical) is still running
    if ! kill -0 $HYBRID_PID 2>/dev/null; then
        print_color "❌ Hybrid simulation died - exiting" $RED
        break
    fi
done
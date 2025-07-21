#!/bin/bash

# Comprehensive SLAM Launcher for Stretch Robot with MuJoCo
# This script launches the complete SLAM pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

# Check if ROS2 is sourced
check_ros2_setup() {
    if [ -z "$ROS_DISTRO" ]; then
        print_error "ROS2 is not sourced. Please run:"
        echo "source /opt/ros/humble/setup.bash"
        echo "source ~/stretch_ros2/install/setup.bash"
        exit 1
    fi
    print_status "ROS2 ($ROS_DISTRO) is properly sourced"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check ROS2 packages
    required_packages=("slam_toolbox" "rviz2" "robot_state_publisher" "tf2_ros")
    for package in "${required_packages[@]}"; do
        if ! ros2 pkg list 2>/dev/null | grep -q "$package"; then
            print_error "Required package $package not found"
            print_status "Install with: sudo apt install ros-humble-$package"
            exit 1
        fi
    done
    
    # Check Python packages
    python3 -c "import rclpy, tf2_ros, sensor_msgs, nav_msgs" 2>/dev/null || {
        print_error "Required Python packages not found"
        exit 1
    }
    
    # Check stretch_mujoco
    python3 -c "from stretch_mujoco import StretchMujocoSimulator" 2>/dev/null || {
        print_error "stretch_mujoco not found"
        exit 1
    }
    
    print_status "All dependencies satisfied"
}

# Kill existing processes
cleanup_processes() {
    print_status "Cleaning up existing processes..."
    
    # Kill any existing ROS2 nodes
    pkill -f "ros2" 2>/dev/null || true
    pkill -f "rviz2" 2>/dev/null || true
    pkill -f "slam_toolbox" 2>/dev/null || true
    pkill -f "stretch_slam_bridge" 2>/dev/null || true
    
    # Wait for processes to terminate
    sleep 2
    print_status "Cleanup completed"
}

# Launch individual components
launch_slam_bridge() {
    print_status "Starting SLAM bridge..."
    cd "$(dirname "$0")"
    
    # Build bridge command with environment options
    BRIDGE_CMD="python3 stretch_slam_bridge_improved.py"
    
    # Add kitchen environment options if specified
    if [ "$KITCHEN_LAYOUT" != "" ]; then
        BRIDGE_CMD="$BRIDGE_CMD --layout $KITCHEN_LAYOUT"
    fi
    
    if [ "$KITCHEN_STYLE" != "" ]; then
        BRIDGE_CMD="$BRIDGE_CMD --style $KITCHEN_STYLE"
    fi
    
    if [ "$SIMPLE_ENV" = true ]; then
        BRIDGE_CMD="$BRIDGE_CMD --simple"
    elif [ "$KITCHEN_WORLD" = true ]; then
        BRIDGE_CMD="$BRIDGE_CMD --kitchen-world"
    elif [ "$COMPLEX_OFFICE" = true ]; then
        BRIDGE_CMD="$BRIDGE_CMD --complex-office"
    fi
    
    print_status "Bridge command: $BRIDGE_CMD"
    $BRIDGE_CMD &
    BRIDGE_PID=$!
    sleep 5  # Give more time for RoboCasa environment generation
    
    if kill -0 $BRIDGE_PID 2>/dev/null; then
        print_status "SLAM bridge started successfully (PID: $BRIDGE_PID)"
    else
        print_error "Failed to start SLAM bridge"
        exit 1
    fi
}

launch_robot_state_publisher() {
    print_status "Starting robot state publisher with real Stretch URDF..."
    
    # Use the actual Stretch URDF from the workspace (but create a simplified version)
    STRETCH_URDF="/home/user/ament_ws/src/stretch_description/urdf/stretch.urdf"
    
    if [ -f "$STRETCH_URDF" ]; then
        print_status "Found real Stretch URDF, creating SLAM-optimized version..."
        # Create a proper URDF that matches the MuJoCo model
        SLAM_URDF="/tmp/stretch_slam.urdf"
        cat > "$SLAM_URDF" << 'EOF'
<?xml version="1.0"?>
<robot name="stretch">
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.025" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.175" length="0.05"/>
      </geometry>
      <material name="base_color">
        <color rgba="0.2 0.2 0.2 1"/>
      </material>
    </visual>
  </link>

  <!-- Mast -->
  <link name="link_mast">
    <visual>
      <origin xyz="0 0 0.27" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.025" length="0.54"/>
      </geometry>
      <material name="mast_color">
        <color rgba="0.7 0.7 0.7 1"/>
      </material>
    </visual>
  </link>
  <joint name="joint_lift" type="prismatic">
    <parent link="base_link"/>
    <child link="link_mast"/>
    <origin xyz="0.0 0.0 0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="0" upper="1.09" effort="100" velocity="0.1"/>
  </joint>

  <!-- Head -->
  <link name="link_head">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.1 0.08 0.06"/>
      </geometry>
      <material name="head_color">
        <color rgba="0.2 0.2 0.2 1"/>
      </material>
    </visual>
  </link>
  <joint name="joint_head_pan" type="revolute">
    <parent link="link_mast"/>
    <child link="link_head"/>
    <origin xyz="0.0 0.0 0.54" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="100" velocity="1.0"/>
  </joint>

  <!-- Arm -->
  <link name="link_arm_l0">
    <visual>
      <origin xyz="0.1 0 0" rpy="0 1.57 0"/>
      <geometry>
        <cylinder radius="0.025" length="0.2"/>
      </geometry>
      <material name="arm_color">
        <color rgba="0.9 0.6 0.2 1"/>
      </material>
    </visual>
  </link>
  <joint name="joint_arm_l0" type="prismatic">
    <parent link="link_mast"/>
    <child link="link_arm_l0"/>
    <origin xyz="0.13 0.0 0.4" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.52" effort="100" velocity="0.1"/>
  </joint>

  <!-- Gripper -->
  <link name="link_gripper">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.05 0.03 0.02"/>
      </geometry>
      <material name="gripper_color">
        <color rgba="0.3 0.3 0.3 1"/>
      </material>
    </visual>
  </link>
  <joint name="joint_wrist_yaw" type="revolute">
    <parent link="link_arm_l0"/>
    <child link="link_gripper"/>
    <origin xyz="0.2 0.0 0.0" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1.0"/>
  </joint>

  <!-- Laser -->
  <link name="laser">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
      <material name="laser_color">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
  </link>
  <joint name="laser_joint" type="fixed">
    <parent link="base_link"/>
    <child link="laser"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
  </joint>

  <!-- Cameras -->
  <link name="cam_d405_rgb_frame">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.03 0.03 0.02"/>
      </geometry>
      <material name="camera_color">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>
  <joint name="cam_d405_joint" type="fixed">
    <parent link="link_head"/>
    <child link="cam_d405_rgb_frame"/>
    <origin xyz="0.05 0.0 0.0" rpy="0 0 0"/>
  </joint>

  <link name="cam_d435i_rgb_frame">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.04 0.02 0.02"/>
      </geometry>
      <material name="camera2_color">
        <color rgba="0 0.5 1 1"/>
      </material>
    </visual>
  </link>
  <joint name="cam_d435i_joint" type="fixed">
    <parent link="link_head"/>
    <child link="cam_d435i_rgb_frame"/>
    <origin xyz="0.0 0.0 0.05" rpy="0 0 0"/>
  </joint>

  <link name="cam_nav_rgb_frame">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.02 0.02 0.01"/>
      </geometry>
      <material name="camera3_color">
        <color rgba="1 1 0 1"/>
      </material>
    </visual>
  </link>
  <joint name="cam_nav_joint" type="fixed">
    <parent link="base_link"/>
    <child link="cam_nav_rgb_frame"/>
    <origin xyz="0.0 0.0 0.5" rpy="0 0 0"/>
  </joint>
</robot>
EOF

        ros2 run robot_state_publisher robot_state_publisher \
            --ros-args -p robot_description:="$(cat $SLAM_URDF)" \
            -p use_sim_time:=true &
        RSP_PID=$!
    else
        print_warning "Real Stretch URDF not found, using simplified model..."
        # Fallback to simple model
        URDF_FILE="/tmp/stretch_simple.urdf"
        cat > "$URDF_FILE" << 'EOF'
<?xml version="1.0"?>
<robot name="stretch">
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder radius="0.15" length="0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
  </link>
  
  <link name="laser">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="laser_joint" type="fixed">
    <parent link="base_link"/>
    <child link="laser"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
  </joint>
  
  <link name="cam_d405_rgb_frame">
    <visual>
      <geometry>
        <box size="0.03 0.03 0.02"/>
      </geometry>
      <material name="green">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="cam_d405_joint" type="fixed">
    <parent link="base_link"/>
    <child link="cam_d405_rgb_frame"/>
    <origin xyz="0.0 0.0 1.0" rpy="0 0 0"/>
  </joint>
</robot>
EOF
        
        ros2 run robot_state_publisher robot_state_publisher \
            --ros-args -p robot_description:="$(cat $URDF_FILE)" \
            -p use_sim_time:=true &
        RSP_PID=$!
    fi
    
    sleep 2
    
    if kill -0 $RSP_PID 2>/dev/null; then
        print_status "Robot state publisher started (PID: $RSP_PID)"
    else
        print_error "Failed to start robot state publisher"
        exit 1
    fi
}

launch_slam_toolbox() {
    print_status "Starting SLAM Toolbox..."
    
    CONFIG_FILE="$(dirname "$0")/config/mapper_params_online_async.yaml"
    
    ros2 run slam_toolbox async_slam_toolbox_node \
        --ros-args -p use_sim_time:=true \
        --params-file "$CONFIG_FILE" &
    SLAM_PID=$!
    sleep 3
    
    if kill -0 $SLAM_PID 2>/dev/null; then
        print_status "SLAM Toolbox started (PID: $SLAM_PID)"
    else
        print_error "Failed to start SLAM Toolbox"
        exit 1
    fi
}

launch_rviz() {
    print_status "Starting RViz..."
    
    RVIZ_CONFIG="$(dirname "$0")/rviz/stretch_slam.rviz"
    
    # Fix: Use correct ROS2 argument format for RViz
    ros2 run rviz2 rviz2 \
        -d "$RVIZ_CONFIG" \
        --ros-args -p use_sim_time:=true &
    RVIZ_PID=$!
    sleep 3
    
    if kill -0 $RVIZ_PID 2>/dev/null; then
        print_status "RViz started (PID: $RVIZ_PID)"
    else
        print_warning "RViz may have failed to start - checking..."
        # Try alternative launch method
        ros2 run rviz2 rviz2 -d "$RVIZ_CONFIG" &
        RVIZ_PID=$!
        sleep 2
        if kill -0 $RVIZ_PID 2>/dev/null; then
            print_status "RViz started with alternative method (PID: $RVIZ_PID)"
        else
            print_warning "RViz startup failed - continuing without RViz"
            RVIZ_PID=""
        fi
    fi
}

# Monitor processes
monitor_processes() {
    print_status "Monitoring processes..."
    
    while true; do
        # Check if critical processes are still running
        if ! kill -0 $BRIDGE_PID 2>/dev/null; then
            print_error "SLAM bridge died unexpectedly"
            cleanup_and_exit 1
        fi
        
        if ! kill -0 $RSP_PID 2>/dev/null; then
            print_error "Robot state publisher died unexpectedly"
            cleanup_and_exit 1
        fi
        
        if ! kill -0 $SLAM_PID 2>/dev/null; then
            print_error "SLAM Toolbox died unexpectedly"
            cleanup_and_exit 1
        fi
        
        sleep 5
    done
}

# Cleanup and exit
cleanup_and_exit() {
    local exit_code=${1:-0}
    
    print_status "Shutting down SLAM system..."
    
    # Kill processes if they exist
    [ ! -z "$BRIDGE_PID" ] && kill $BRIDGE_PID 2>/dev/null || true
    [ ! -z "$RSP_PID" ] && kill $RSP_PID 2>/dev/null || true
    [ ! -z "$SLAM_PID" ] && kill $SLAM_PID 2>/dev/null || true
    [ ! -z "$RVIZ_PID" ] && [ "$RVIZ_PID" != "" ] && kill $RVIZ_PID 2>/dev/null || true
    
    # Cleanup temporary files
    rm -f /tmp/stretch_simple.urdf
    
    # Final cleanup
    cleanup_processes
    
    print_status "SLAM system shutdown complete"
    exit $exit_code
}

# Signal handlers
trap 'cleanup_and_exit 130' INT TERM

# Main execution
main() {
    print_header "STRETCH ROBOT SLAM LAUNCHER"
    
    print_status "Starting complete SLAM pipeline..."
    echo
    
    # Setup checks
    check_ros2_setup
    check_dependencies
    cleanup_processes
    
    echo
    print_status "Launching components..."
    
    # Launch all components
    launch_slam_bridge
    launch_robot_state_publisher
    launch_slam_toolbox
    launch_rviz
    
    echo
    print_header "SLAM SYSTEM READY"
    echo
    print_status "System Status:"
    echo "  ✓ SLAM Bridge: Publishing sensor data from MuJoCo"
    echo "  ✓ Robot State Publisher: Broadcasting robot TF tree"
    echo "  ✓ SLAM Toolbox: Building map in real-time"
    echo "  ✓ RViz: Visualizing robot and map"
    echo
    print_status "Available Topics:"
    echo "  /scan - Laser scan data"
    echo "  /odom - Odometry data"
    echo "  /map - SLAM-generated map"
    echo "  /joint_states - Robot joint states"
    echo "  /camera/*/color/image_raw - Camera feeds"
    echo
    print_status "Controls:"
    echo "  • Use RViz to visualize the robot and map"
    echo "  • Drive the robot using: ros2 run teleop_twist_keyboard teleop_twist_keyboard"
    echo "  • Save map using: ros2 run nav2_map_server map_saver_cli -f my_map"
    echo "  • Press Ctrl+C to stop the system"
    echo
    print_warning "You can now drive the robot to explore and build a map!"
    
    # Monitor processes
    monitor_processes
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --help, -h        Show this help message"
    echo "  --no-rviz         Don't start RViz"
    echo "  --debug           Enable debug output"
    echo "  --layout N        Kitchen layout (0-9):"
    echo "                      0=One wall, 1=One wall w/ island, 2=L-shaped (default)"
    echo "                      3=L-shaped w/ island, 4=Galley, 5=U-shaped"
    echo "                      6=U-shaped w/ island, 7=G-shaped, 8=G-shaped (large)"
    echo "                      9=Wraparound"
    echo "  --style N         Kitchen style (0-11):"
    echo "                      0=Industrial, 1=Scandinavian (default), 2=Coastal"
    echo "                      3=Modern_1, 4=Modern_2, 5=Traditional_1, 6=Traditional_2"
    echo "                      7=Farmhouse, etc."
    echo "  --simple          Use simple environment instead of RoboCasa kitchen"
    echo "  --kitchen-world   Use visible kitchen world with cabinets and appliances"
    echo "  --complex-office  Use complex office environment with visible robot and realistic LIDAR"
    echo
    echo "Examples:"
    echo "  $0                           # Start with L-shaped Scandinavian kitchen"
    echo "  $0 --layout 5 --style 7     # Start with U-shaped Farmhouse kitchen"
    echo "  $0 --simple                 # Start with simple environment" 
    echo "  $0 --kitchen-world          # Start with visible kitchen world"
    echo "  $0 --complex-office         # Start with complex office environment (RECOMMENDED)"
    echo "  $0 --no-rviz --layout 1     # Start One wall w/ island kitchen without RViz"
    echo
}

# Parse command line arguments
NO_RVIZ=false
DEBUG=false
KITCHEN_LAYOUT=""
KITCHEN_STYLE=""
SIMPLE_ENV=false
KITCHEN_WORLD=false
COMPLEX_OFFICE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_usage
            exit 0
            ;;
        --no-rviz)
            NO_RVIZ=true
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --layout)
            KITCHEN_LAYOUT="$2"
            shift 2
            ;;
        --style)
            KITCHEN_STYLE="$2"
            shift 2
            ;;
        --simple)
            SIMPLE_ENV=true
            shift
            ;;
        --kitchen-world)
            KITCHEN_WORLD=true
            shift
            ;;
        --complex-office)
            COMPLEX_OFFICE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Override RViz launch if requested
if [ "$NO_RVIZ" = true ]; then
    launch_rviz() {
        print_status "Skipping RViz (--no-rviz flag)"
    }
fi

# Enable debug if requested
if [ "$DEBUG" = true ]; then
    set -x
fi

# Run main function
main
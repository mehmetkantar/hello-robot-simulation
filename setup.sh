#!/bin/bash

# Hello Robot Stretch Simulation Setup Script
# Automatically installs all dependencies and configures the system

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

print_header "🤖 HELLO ROBOT STRETCH SIMULATION SETUP"

# Check if running on supported OS
if ! grep -q "22.04" /etc/os-release 2>/dev/null; then
    print_color "⚠️  Warning: This setup is optimized for Ubuntu 22.04" $YELLOW
    print_color "Other versions may work but are not fully tested" $YELLOW
    echo
fi

# Check if script is run as root
if [[ $EUID -eq 0 ]]; then
   print_color "❌ This script should not be run as root (don't use sudo)" $RED
   print_color "Run as regular user: ./setup.sh" $RED
   exit 1
fi

print_color "🔍 Checking system requirements..." $CYAN

# Update package list
print_color "📦 Updating package list..." $YELLOW
sudo apt update -qq

# Install system dependencies
print_color "🔧 Installing system dependencies..." $YELLOW

# Essential packages
sudo apt install -y \
    wget \
    curl \
    git \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    lsof

# ROS2 Humble installation check
print_color "🤖 Checking ROS2 Humble installation..." $CYAN

if [ ! -f "/opt/ros/humble/setup.bash" ]; then
    print_color "📡 ROS2 Humble not found. Installing ROS2 Humble..." $YELLOW
    
    # Add ROS2 apt repository
    sudo apt install -y software-properties-common
    sudo add-apt-repository universe -y
    sudo apt update -qq
    
    # Install ROS2 key
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
    
    sudo apt update -qq
    
    # Install ROS2 Humble
    sudo apt install -y \
        ros-humble-desktop \
        ros-humble-slam-toolbox \
        ros-humble-navigation2 \
        ros-humble-nav2-bringup \
        ros-humble-robot-state-publisher \
        ros-humble-joint-state-publisher \
        ros-humble-tf2-tools \
        ros-humble-cv-bridge \
        python3-rosdep \
        python3-colcon-common-extensions
    
    # Initialize rosdep
    if [ ! -f "/etc/ros/rosdep/sources.list.d/20-default.list" ]; then
        sudo rosdep init
    fi
    rosdep update
    
    print_color "✅ ROS2 Humble installed successfully" $GREEN
else
    print_color "✅ ROS2 Humble already installed" $GREEN
fi

# Install Python dependencies
print_color "🐍 Installing Python dependencies..." $YELLOW
pip3 install --user -r requirements.txt

# Create ROS2 workspace if it doesn't exist
ROS_WS="$HOME/stretch_ros2"
if [ ! -d "$ROS_WS" ]; then
    print_color "📁 Creating ROS2 workspace at $ROS_WS..." $YELLOW
    mkdir -p "$ROS_WS/src"
fi

# Source ROS2 in bashrc if not already done
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
    print_color "🔧 Adding ROS2 to bashrc..." $YELLOW
    echo "" >> ~/.bashrc
    echo "# ROS2 Humble setup" >> ~/.bashrc
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc
    
    # Add stretch_ros2 workspace if it exists
    if [ -f "$ROS_WS/install/setup.bash" ]; then
        echo "source $ROS_WS/install/setup.bash" >> ~/.bashrc
    fi
    
    print_color "✅ ROS2 environment added to bashrc" $GREEN
else
    print_color "✅ ROS2 already configured in bashrc" $GREEN
fi

# Set execute permissions on scripts
print_color "🔧 Setting execute permissions on scripts..." $YELLOW
chmod +x *.sh
chmod +x *.py

# Create config and rviz directories if they don't exist
print_color "📁 Creating configuration directories..." $YELLOW
mkdir -p config rviz worlds logs

# Create basic SLAM configuration if it doesn't exist
if [ ! -f "config/mapper_params_online_async.yaml" ]; then
    print_color "📝 Creating default SLAM configuration..." $YELLOW
    cat > config/mapper_params_online_async.yaml << 'EOF'
slam_toolbox:
  ros__parameters:
    
    # Plugin params
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_loss_function: None
    
    # ROS Parameters
    odom_frame: odom
    map_frame: map
    base_frame: base_link
    scan_topic: /scan
    use_map_saver: true
    mode: mapping
    
    # if you'd like to immediately start continuing a map at a given pose
    # or at the dock, but they are mutually exclusive, if pose is given
    # will use pose
    #map_file_name: test_steve
    #map_start_pose: [0.0, 0.0, 0.0]
    #map_start_at_dock: true
    
    debug_logging: false
    throttle_scans: 1
    transform_publish_period: 0.02 #if 0 never publishes odometry
    map_update_interval: 5.0
    resolution: 0.05
    max_laser_range: 20.0 #for rastering images
    minimum_time_interval: 0.5
    transform_timeout: 0.2
    tf_buffer_duration: 30.
    stack_size_to_use: 40000000 #// program needs a larger stack size to serialize large maps
    enable_interactive_mode: true
    
    # General Parameters
    use_scan_matching: true
    use_scan_barycenter: true
    minimum_travel_distance: 0.5
    minimum_travel_heading: 0.5
    scan_buffer_size: 10
    scan_buffer_maximum_scan_distance: 10.0
    link_match_minimum_response_fine: 0.1  
    link_scan_maximum_distance: 1.5
    loop_search_maximum_distance: 3.0
    do_loop_closing: true 
    loop_match_minimum_chain_size: 10           
    loop_match_maximum_variance_coarse: 3.0  
    loop_match_minimum_response_coarse: 0.35    
    loop_match_minimum_response_fine: 0.45
    
    # Correlation Parameters - Correlation Parameters
    correlation_search_space_dimension: 0.5
    correlation_search_space_resolution: 0.01
    correlation_search_space_smear_deviation: 0.1 
    
    # Correlation Parameters - Loop Closure Parameters
    loop_search_space_dimension: 8.0
    loop_search_space_resolution: 0.05
    loop_search_space_smear_deviation: 0.03
    
    # Scan Matcher Parameters
    distance_variance_penalty: 0.5      
    angle_variance_penalty: 1.0    
    
    fine_search_angle_offset: 0.00349     
    coarse_search_angle_offset: 0.349   
    coarse_angle_resolution: 0.0349        
    minimum_angle_penalty: 0.9
    minimum_distance_penalty: 0.5
    use_response_expansion: true
EOF
    print_color "✅ Default SLAM configuration created" $GREEN
fi

# Create basic RViz configuration if it doesn't exist
if [ ! -f "rviz/stretch_slam.rviz" ]; then
    print_color "📝 Creating default RViz configuration..." $YELLOW
    mkdir -p rviz
    cat > rviz/stretch_slam.rviz << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Help Height: 78
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /Status1
        - /RobotModel1
        - /LaserScan1
        - /Map1
      Splitter Ratio: 0.5
    Tree Height: 775
  - Class: rviz_common/Selection
    Name: Selection
  - Class: rviz_common/Tool Properties
    Expanded:
      - /2D Pose Estimate1
      - /2D Nav Goal1
      - /Publish Point1
    Name: Tool Properties
    Splitter Ratio: 0.5886790156364441
  - Class: rviz_common/Views
    Expanded:
      - /Current View1
    Name: Views
    Splitter Ratio: 0.5
Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Line Style:
        Line Width: 0.029999999329447746
        Value: Lines
      Name: Grid
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
        Z: 0
      Plane: XY
      Plane Cell Count: 10
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Collision Enabled: false
      Description File: ""
      Description Source: Topic
      Description Topic:
        Depth: 5
        Durability Policy: Volatile
        Filter size: 10
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /robot_description
      Enabled: true
      Links:
        All Links Enabled: true
        Expand Joint Details: false
        Expand Link Details: false
        Expand Tree: false
        Link Tree Style: Links in Alphabetic Order
      Name: RobotModel
      TF Prefix: ""
      Update Interval: 0
      Value: true
      Visual Enabled: true
    - Alpha: 1
      Autocompute Intensity Bounds: true
      Autocompute Value Bounds:
        Max Value: 10
        Min Value: -10
        Value: true
      Axis: Z
      Channel Name: intensity
      Class: rviz_default_plugins/LaserScan
      Color: 255; 255; 255
      Color Transformer: Intensity
      Decay Time: 0
      Enabled: true
      Invert Rainbow: false
      Max Color: 255; 255; 255
      Min Color: 0; 0; 0
      Name: LaserScan
      Position Transformer: XYZ
      Selectable: true
      Size (Pixels): 3
      Size (m): 0.10000000149011612
      Style: Flat Squares
      Topic:
        Depth: 5
        Durability Policy: Volatile
        Filter size: 10
        History Policy: Keep Last
        Reliability Policy: Best Effort
        Value: /scan
      Use Fixed Frame: true
      Use rainbow: true
      Value: true
    - Alpha: 0.699999988079071
      Class: rviz_default_plugins/Map
      Color Scheme: map
      Draw Behind: false
      Enabled: true
      Name: Map
      Topic:
        Depth: 5
        Durability Policy: Volatile
        Filter size: 10
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /map
      Update Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /map_updates
      Use Timestamp: false
      Value: true
  Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Default Light: true
    Fixed Frame: map
    Frame Rate: 30
  Name: root
  Tools:
    - Class: rviz_default_plugins/Interact
      Hide Inactive Objects: true
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/Select
    - Class: rviz_default_plugins/FocusCamera
    - Class: rviz_default_plugins/Measure
      Line color: 128; 128; 0
    - Class: rviz_default_plugins/SetInitialPose
      Covariance x: 0.25
      Covariance y: 0.25
      Covariance yaw: 0.06853891909122467
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /initialpose
    - Class: rviz_default_plugins/SetGoal
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /goal_pose
    - Class: rviz_default_plugins/PublishPoint
      Single click: true
      Topic:
        Depth: 5
        Durability Policy: Volatile
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /clicked_point
  Transformation:
    Current:
      Class: rviz_default_plugins/TF
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 10
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.05999999865889549
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05000000074505806
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.009999999776482582
      Pitch: 1.5697963237762451
      Target Frame: <Fixed Frame>
      Value: Orbit (rviz_default_plugins)
      Yaw: 4.71238899230957
    Saved: ~
Window Geometry:
  Displays:
    collapsed: false
  Height: 1016
  Hide Left Dock: false
  Hide Right Dock: false
  QMainWindow State: 000000ff00000000fd0000000400000000000001560000035afc0200000008fb0000001200530065006c0065006300740069006f006e00000001e10000009b0000005c00fffffffb0000001e0054006f006f006c002000500072006f007000650072007400690065007302000001ed000001df00000185000000a3fb000000120056006900650077007300200054006f006f02000001df000002110000018500000122fb000000200054006f006f006c002000500072006f0070006500720074006900650073003203000002880000011d000002210000017afb000000100044006900730070006c006100790073010000003d0000035a000000c900fffffffb0000002000730065006c0065006300740069006f006e00200062007500660066006500720200000138000000aa0000023a00000294fb00000014005700690064006500200053007400650072006500
  Selection:
    collapsed: false
  Tool Properties:
    collapsed: false
  Views:
    collapsed: false
  Width: 1848
  X: 72
  Y: 27
EOF
    print_color "✅ Default RViz configuration created" $GREEN
fi

# Check for Hello Robot MuJoCo
print_color "🤖 Checking Hello Robot Stretch MuJoCo..." $CYAN
if [ ! -d "/home/user/stretch_mujoco" ] && [ ! -d "$HOME/stretch_mujoco" ]; then
    print_color "⚠️  Hello Robot Stretch MuJoCo not found!" $YELLOW
    print_color "📖 Please install it manually:" $CYAN
    print_color "   1. Follow Hello Robot's MuJoCo installation guide" $CYAN
    print_color "   2. Clone to ~/stretch_mujoco or update the path in CLAUDE.md" $CYAN
    print_color "   3. Ensure stretch_mujoco package is in Python path" $CYAN
else
    print_color "✅ Hello Robot Stretch MuJoCo found" $GREEN
fi

# Test basic imports
print_color "🧪 Testing Python imports..." $CYAN
python3 -c "import rclpy; print('✅ ROS2 Python client OK')" 2>/dev/null || print_color "⚠️  rclpy import failed" $YELLOW
python3 -c "import numpy; print('✅ NumPy OK')" 2>/dev/null || print_color "⚠️  NumPy import failed" $YELLOW
python3 -c "import cv2; print('✅ OpenCV OK')" 2>/dev/null || print_color "⚠️  OpenCV import failed" $YELLOW

print_header "🎉 SETUP COMPLETE"

print_color "" $NC
print_color "✅ Installation completed successfully!" $GREEN
print_color "" $NC
print_color "📋 NEXT STEPS:" $PURPLE
print_color "1. Source ROS2 environment: source ~/.bashrc" $CYAN
print_color "2. Launch the simulation: ./launch_full_simulation.sh --complex-office" $CYAN
print_color "3. Open web browser: http://localhost:8081" $CYAN
print_color "" $NC
print_color "📖 For more information, check:" $PURPLE
print_color "   • README.md - Full documentation" $CYAN
print_color "   • CLAUDE.md - Development guide" $CYAN
print_color "" $NC
print_color "🐛 If you encounter issues:" $PURPLE
print_color "   • Check system dependencies installation" $CYAN
print_color "   • Verify Hello Robot MuJoCo setup" $CYAN
print_color "   • Review troubleshooting section in README.md" $CYAN
print_color "" $NC
print_color "🚀 Happy robot simulation!" $GREEN
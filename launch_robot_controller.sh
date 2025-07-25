#!/bin/bash

# Enhanced Stretch Robot Controller Launcher
# Starts GUI controller, RViz, MuJoCo simulation, and SLAM simultaneously

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    echo -e "${2}${1}${NC}"
}

# Function to check if a process is running
is_running() {
    pgrep -f "$1" >/dev/null 2>&1
}

# Function to cleanup processes on exit
cleanup() {
    print_color "🛑 Shutting down all processes..." $YELLOW
    
    # Kill all spawned processes
    pkill -f "stretch_robot_controller.py" 2>/dev/null || true
    pkill -f "stretch_controller_bridge.py" 2>/dev/null || true
    pkill -f "stretch_slam_bridge" 2>/dev/null || true  
    pkill -f "rviz2" 2>/dev/null || true
    pkill -f "slam_toolbox" 2>/dev/null || true
    pkill -f "joint_state_publisher" 2>/dev/null || true
    
    sleep 2
    print_color "✅ Cleanup complete" $GREEN
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

print_color "🤖 Starting Stretch Robot Controller System" $BLUE
print_color "=========================================" $BLUE

# Check if ROS2 is sourced
if [ -z "$ROS_DISTRO" ]; then
    print_color "⚠️  ROS2 not sourced. Sourcing..." $YELLOW
    source /opt/ros/humble/setup.bash
fi

# Set environment for GUI (fix OpenCV Qt conflicts)
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
export QT_QPA_PLATFORM=xcb
# Remove OpenCV Qt plugins to avoid conflicts
unset CV2_QT_PATH

# Parse command line arguments
ENVIRONMENT="demo_complex"
HEADLESS=false
NO_GUI=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --kitchen-world)
            ENVIRONMENT="kitchen_scene"
            shift
            ;;
        --simple-world)
            ENVIRONMENT="simple_office"
            shift
            ;;
        --complex-world)
            ENVIRONMENT="demo_complex"
            shift
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --no-gui)
            NO_GUI=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --kitchen-world    Use kitchen environment"
            echo "  --simple-world     Use simple office environment" 
            echo "  --complex-world    Use complex demo environment (default)"
            echo "  --headless         Run MuJoCo in headless mode"
            echo "  --no-gui           Don't start the robot controller GUI"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_color "📋 Configuration:" $BLUE
print_color "   Environment: $ENVIRONMENT" $BLUE
print_color "   Headless: $HEADLESS" $BLUE  
print_color "   GUI Controller: $([ "$NO_GUI" = "true" ] && echo "Disabled" || echo "Enabled")" $BLUE
echo

# Step 1: Start MuJoCo simulation with SLAM bridge
print_color "🔧 Step 1: Starting MuJoCo simulation and SLAM bridge..." $GREEN

if [ "$HEADLESS" = "true" ]; then
    python3 stretch_slam_bridge_improved.py --environment=$ENVIRONMENT --headless &
else
    python3 stretch_slam_bridge_improved.py --environment=$ENVIRONMENT &
fi

SLAM_PID=$!
sleep 3

# Check if MuJoCo started successfully
if ! kill -0 $SLAM_PID 2>/dev/null; then
    print_color "❌ Failed to start MuJoCo simulation" $RED
    exit 1
fi

print_color "✅ MuJoCo simulation started (PID: $SLAM_PID)" $GREEN

# Step 2: Start SLAM Toolbox
print_color "🔧 Step 2: Starting SLAM Toolbox..." $GREEN

ros2 launch slam_toolbox online_async_launch.py \
    slam_params_file:=$(pwd)/config/slam_params.yaml &

SLAM_TOOLBOX_PID=$!
sleep 3

print_color "✅ SLAM Toolbox started (PID: $SLAM_TOOLBOX_PID)" $GREEN

# Step 3: Start RViz2
print_color "🔧 Step 3: Starting RViz2..." $GREEN

rviz2 -d $(pwd)/rviz/stretch_slam.rviz &
RVIZ_PID=$!
sleep 2

print_color "✅ RViz2 started (PID: $RVIZ_PID)" $GREEN

# Step 4: Start Robot Controller GUI (if not disabled)
if [ "$NO_GUI" != "true" ]; then
    print_color "🔧 Step 4: Starting Robot Controller GUI..." $GREEN
    
    # Make sure the controller script is executable
    chmod +x stretch_robot_controller_simple.py
    
    # Start the GUI controller (simple version to avoid Qt/OpenCV conflicts)
    python3 stretch_robot_controller_simple.py &
    GUI_PID=$!
    sleep 2
    
    if kill -0 $GUI_PID 2>/dev/null; then
        print_color "✅ Robot Controller GUI started (PID: $GUI_PID)" $GREEN
    else
        print_color "⚠️  Robot Controller GUI failed to start" $YELLOW
    fi
else
    print_color "⏭️  Step 4: Robot Controller GUI disabled" $YELLOW
fi

# Step 5: Start controller bridge (connects GUI to simulation)
print_color "🔧 Step 5: Starting controller bridge..." $GREEN

python3 stretch_controller_bridge.py &
BRIDGE_PID=$!
sleep 2

if kill -0 $BRIDGE_PID 2>/dev/null; then
    print_color "✅ Controller bridge started (PID: $BRIDGE_PID)" $GREEN
else
    print_color "⚠️  Controller bridge failed to start" $YELLOW
fi

# Step 6: Start joint state publisher (for RViz visualization)
print_color "🔧 Step 6: Starting joint state publisher..." $GREEN

ros2 run joint_state_publisher joint_state_publisher &
JSP_PID=$!

print_color "✅ Joint state publisher started (PID: $JSP_PID)" $GREEN

print_color "" $NC
print_color "🎉 All systems started successfully!" $GREEN
print_color "=========================================" $GREEN
print_color "🎮 Robot Controller GUI: Modern control interface with joystick" $BLUE
print_color "🗺️  RViz2: Real-time mapping and visualization" $BLUE  
print_color "🔬 MuJoCo: Physics simulation environment" $BLUE
print_color "📡 SLAM: Simultaneous Localization and Mapping" $BLUE
print_color "" $NC

if [ "$NO_GUI" != "true" ]; then
    print_color "💡 GUI Controller Features:" $YELLOW
    print_color "   • Virtual joystick for base movement" $YELLOW
    print_color "   • Sliders for all arm joints (lift, extension, wrist, gripper)" $YELLOW  
    print_color "   • Real-time camera feeds display" $YELLOW
    print_color "   • Robot status monitoring" $YELLOW
    print_color "   • Emergency stop and quick position buttons" $YELLOW
    print_color "" $NC
fi

print_color "🎯 Usage Tips:" $YELLOW
print_color "   • Use the virtual joystick to drive the robot around" $YELLOW
print_color "   • Adjust arm position with the sliders" $YELLOW
print_color "   • Watch the map being built in RViz" $YELLOW
print_color "   • See robot movement in MuJoCo physics simulation" $YELLOW
print_color "   • Press Ctrl+C to shutdown all processes" $YELLOW
print_color "" $NC

print_color "⏳ System running... Press Ctrl+C to shutdown" $GREEN

# Wait for user interrupt
wait
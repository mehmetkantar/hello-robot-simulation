#!/bin/bash

echo "🔧 Fixed Robot Test - Mesh Path Resolution"
echo "=========================================="
echo ""

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."
killall -9 gzserver gzclient rviz2 python3 joint_state_publisher_gui 2>/dev/null || true
sleep 3

# Set environment variables for VM
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Setup workspace
echo "🔧 Setting up workspace..."
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "🛠️  This fixed version will:"
echo "   ✅ Set proper Gazebo model paths"
echo "   ✅ Fix mesh file references in URDF"
echo "   ✅ Use absolute file:// paths for meshes"
echo "   ✅ Spawn robot at visible height (1m above ground)"
echo ""
echo "🎯 Expected results:"
echo "   • Robot appears with FULL 3D meshes (not wireframe)"
echo "   • All robot parts visible (base, lift, arm, gripper, etc.)"
echo "   • NO mesh loading errors in console"
echo "   • Robot at center of empty world, 1m above ground"
echo ""
echo "📂 Mesh files found at:"
find /home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/meshes -name "*.STL" | wc -l
echo "   STL files in meshes directory"
echo ""

read -p "Press Enter to launch fixed robot test..."

echo "🚀 Launching fixed robot with mesh path resolution..."
ros2 launch /home/kantar/Desktop/hello-robot/launch/fixed_empty_world.launch.py
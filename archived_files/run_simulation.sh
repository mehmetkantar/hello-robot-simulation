#!/bin/bash

echo "🚀 Starting Hello Robot Stretch 3 Simulation..."

# Navigate to workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws

# Source ROS2 and workspace
source /opt/ros/humble/setup.bash
source install/setup.bash

# Check if workspace is built
if [ ! -d "install" ]; then
    echo "❌ Workspace not built! Please run ./build_workspace.sh first"
    exit 1
fi

# Validate setup
echo "🔍 Validating setup..."
cd src/stretch_moveit_config
python3 test_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Setup validation failed!"
    exit 1
fi

cd ../../

echo "🎯 Starting simulation components..."
echo "This will launch:"
echo "  - Gazebo with Stretch 3 robot"
echo "  - MoveIt2 motion planning"
echo "  - RViz visualization"
echo ""
echo "⏳ Please wait 30-60 seconds for all components to initialize..."
echo ""

# Launch the complete simulation
ros2 launch stretch_moveit_config stretch_gazebo_moveit.launch.py
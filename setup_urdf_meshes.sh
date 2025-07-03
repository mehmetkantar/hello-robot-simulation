#!/bin/bash

echo "🔧 Setting up URDF Meshes (Official Hello Robot Method)"
echo "====================================================="

# Apply VM fixes first
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Navigate to workspace
cd /home/kantar/Desktop/hello-robot

echo "📦 Step 1: Installing hello-robot-stretch-urdf package..."
python3 -m pip install -U hello-robot-stretch-urdf

echo "📁 Step 2: Cloning stretch_urdf repository..."
if [ ! -d "/tmp/stretch_urdf" ]; then
    git clone https://github.com/hello-robot/stretch_urdf.git --depth 1 /tmp/stretch_urdf
else
    echo "Repository already exists, pulling latest..."
    cd /tmp/stretch_urdf && git pull
    cd /home/kantar/Desktop/hello-robot
fi

echo "🔧 Step 3: Installing stretch-body package..."
python3 -m pip install hello-robot-stretch-body

echo "🔄 Step 4: Running URDF update script..."
python3 /tmp/stretch_urdf/tools/stretch_urdf_ros_update.py

echo "🔄 Step 5: Running ROS2 rebuild..."
python3 /tmp/stretch_urdf/tools/stretch_urdf_ros_update.py --ros2_rebuild

echo "✅ URDF setup completed!"

# Check if meshes are now available
echo ""
echo "🔍 Checking mesh files..."
MESH_DIR="/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/meshes"
if [ -d "$MESH_DIR" ]; then
    MESH_COUNT=$(find "$MESH_DIR" -name "*.STL" | wc -l)
    echo "Found $MESH_COUNT mesh files in $MESH_DIR"
    
    if [ "$MESH_COUNT" -gt 0 ]; then
        echo "✅ Mesh files are available!"
        ls "$MESH_DIR" | head -5
        echo "... (and more)"
    else
        echo "⚠️  Mesh directory exists but no STL files found"
    fi
else
    echo "❌ Mesh directory not found: $MESH_DIR"
fi

echo ""
echo "🏗️  Rebuilding workspace with new URDF files..."
cd stretch_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install

echo ""
echo "✅ Setup complete! Testing robot simulation..."
echo "🚀 Launching simulation with proper URDF meshes..."

source install/setup.bash
timeout 60s ros2 launch stretch_moveit_config stretch_gazebo.launch.py

echo ""
echo "🎯 The robot should now be visible with proper meshes!"
echo "   If you still don't see it, the mesh paths may need adjustment"
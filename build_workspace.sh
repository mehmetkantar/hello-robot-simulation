#!/bin/bash

echo "🔨 Building Hello Robot Stretch 3 Workspace..."

# Navigate to workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws

# Source ROS2
source /opt/ros/humble/setup.bash

# Initialize rosdep if needed
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    echo "🔧 Initializing rosdep..."
    sudo rosdep init
fi

rosdep update

# Install dependencies
echo "📦 Installing workspace dependencies..."
rosdep install --from-paths src --ignore-src -r -y

# Build the workspace
echo "🔨 Building workspace..."
colcon build --symlink-install

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Workspace built successfully!"
    echo ""
    echo "🎯 To run the simulation:"
    echo "   ./run_simulation.sh"
else
    echo "❌ Build failed! Check the error messages above."
    exit 1
fi
#!/bin/bash

echo "🤖 Hello Robot Stretch 3 - Complete Setup and Launch"
echo "======================================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists ros2; then
    echo "❌ ROS2 not found! Please install ROS2 Humble first."
    echo "   Follow: https://docs.ros.org/en/humble/Installation.html"
    exit 1
fi

if ! command_exists colcon; then
    echo "⚠️  colcon not found. Installing..."
    sudo apt update
    sudo apt install -y python3-colcon-common-extensions
fi

echo "✅ Prerequisites check passed!"

# Step 1: Install dependencies
echo ""
echo "📦 Step 1: Installing dependencies..."
if [ ! -f ".deps_installed" ]; then
    ./install_dependencies.sh
    if [ $? -eq 0 ]; then
        touch .deps_installed
        echo "✅ Dependencies installed and marked as complete"
    else
        echo "❌ Dependency installation failed"
        exit 1
    fi
else
    echo "✅ Dependencies already installed (delete .deps_installed to reinstall)"
fi

# Step 2: Build workspace
echo ""
echo "🔨 Step 2: Building workspace..."
if [ ! -d "stretch_ws/install" ]; then
    ./build_workspace.sh
    if [ $? -ne 0 ]; then
        echo "❌ Workspace build failed"
        exit 1
    fi
else
    echo "✅ Workspace already built (delete stretch_ws/install to rebuild)"
fi

# Step 3: Run simulation
echo ""
echo "🚀 Step 3: Launching simulation..."
echo ""
echo "🎯 Starting Hello Robot Stretch 3 Simulation!"
echo "   This will open:"
echo "   - Gazebo (robot physics simulation)"
echo "   - RViz (visualization and motion planning)"
echo ""
echo "⏳ Please wait 30-60 seconds for startup..."
echo "🎮 Use RViz Motion Planning tab to control the robot!"
echo ""
read -p "Press ENTER to start the simulation..."

./run_simulation.sh
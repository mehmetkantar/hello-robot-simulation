#!/bin/bash

echo "🚀 Installing Hello Robot Stretch 3 Simulation Dependencies..."

# Update package list
sudo apt update

# Install essential ROS2 packages
echo "📦 Installing ROS2 packages..."
sudo apt install -y \
    ros-humble-moveit \
    ros-humble-moveit-planners \
    ros-humble-moveit-simple-controller-manager \
    ros-humble-moveit-configs-utils \
    ros-humble-moveit-ros-planning-interface \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-robot-state-publisher \
    ros-humble-tf2-ros \
    ros-humble-tf2-tools \
    ros-humble-xacro \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool

# Install additional tools
echo "🔧 Installing additional tools..."
sudo apt install -y \
    python3-pip \
    git \
    curl \
    wget

echo "✅ Dependencies installed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Run: chmod +x install_dependencies.sh && ./install_dependencies.sh"
echo "2. Run: ./build_workspace.sh"
echo "3. Run: ./run_simulation.sh"
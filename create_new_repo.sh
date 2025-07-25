#!/bin/bash

# Create New Repository Script
# Prepares all files for a clean new GitHub repository

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_header "📦 CREATE NEW REPOSITORY"

# Create a clean directory for the new repo
REPO_NAME="hello-robot-stretch-simulation"
NEW_DIR="/tmp/$REPO_NAME"

print_color "🗂️  Creating clean repository structure..." $YELLOW
rm -rf "$NEW_DIR"
mkdir -p "$NEW_DIR"

# Core files to include
print_color "📋 Copying essential files..." $CYAN

# Main system files
cp stretch_slam_bridge_improved.py "$NEW_DIR/"
cp simple_web_controller.py "$NEW_DIR/"
cp launch_full_simulation.sh "$NEW_DIR/"
cp direct_robot_test.py "$NEW_DIR/"
cp test_web_controller_connection.py "$NEW_DIR/"
cp test_ros_connection.py "$NEW_DIR/"

# Documentation and setup
cp README.md "$NEW_DIR/"
cp CLAUDE.md "$NEW_DIR/"
cp requirements.txt "$NEW_DIR/"
cp setup.sh "$NEW_DIR/"

# Configuration directories
mkdir -p "$NEW_DIR/config"
mkdir -p "$NEW_DIR/rviz" 
mkdir -p "$NEW_DIR/worlds"
mkdir -p "$NEW_DIR/logs"

# Copy configuration files if they exist
if [ -f "config/mapper_params_online_async.yaml" ]; then
    cp config/mapper_params_online_async.yaml "$NEW_DIR/config/"
fi

if [ -f "rviz/stretch_slam.rviz" ]; then
    cp rviz/stretch_slam.rviz "$NEW_DIR/rviz/"
fi

# Create LICENSE file
print_color "📄 Creating LICENSE file..." $CYAN
cat > "$NEW_DIR/LICENSE" << 'EOF'
MIT License

Copyright (c) 2025 Hello Robot Stretch Simulation Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Create .gitignore
print_color "🙈 Creating .gitignore file..." $CYAN
cat > "$NEW_DIR/.gitignore" << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# ROS2 build files
build/
install/
log/
logs/

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Simulation logs and temporary files
*.log
*.tmp
/tmp/
simulation.log

# MuJoCo temporary files
*.mjb
*.mjcf~

# Python virtual environments
venv/
env/
.env

# RViz config backups
*.rviz~

# Map files (optional - uncomment if you want to track maps)
# *.pgm
# *.yaml

# Backup files
*.bak
*.backup
*~
EOF

# Initialize git repository
print_color "🔧 Initializing git repository..." $CYAN
cd "$NEW_DIR"
git init
git branch -M main

# Configure git user for this repo
git config user.email "mehmetkantar@example.com"
git config user.name "Mehmet Kantar"

git add .

# Create initial commit
print_color "💾 Creating initial commit..." $CYAN
git commit -m "$(cat <<'EOF'
Initial commit: Hello Robot Stretch Simulation with Web Teleop

Complete simulation system featuring:

## 🤖 Core Features
- Full MuJoCo physics simulation of Hello Robot Stretch
- Web-based teleoperation interface for all robot joints
- Real-time SLAM mapping with SLAM Toolbox integration
- RViz visualization of robot state and sensor data
- Multiple environment support (office, kitchen, custom)

## 🎮 Robot Control
- Base movement (forward, backward, rotation, strafing)
- Lift control (0-1.1m vertical positioning)
- Arm extension (0-0.52m reach control)  
- Head pan/tilt control for camera positioning
- Wrist and gripper manipulation
- Adjustable speed control via web interface

## 🏗️ System Architecture
- stretch_slam_bridge_improved.py: ROS2-MuJoCo integration bridge
- simple_web_controller.py: HTTP-based teleoperation interface
- launch_full_simulation.sh: Complete system launcher
- Comprehensive testing suite and debugging tools

## 🚀 Quick Start
1. Install dependencies: ./setup.sh
2. Launch system: ./launch_full_simulation.sh --complex-office  
3. Open web interface: http://localhost:8081
4. Control robot via browser interface
5. Watch real-time SLAM mapping in RViz

## 🔧 Technical Details
- ROS2 Humble integration with proper topic mapping
- MuJoCo Actuators enum usage for reliable joint control
- Safety limits and error handling throughout
- Configurable environments and performance options
- Full documentation and setup automation

Ready for immediate deployment and development!

🤖 Generated with Claude Code - AI-assisted robotics development

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

print_header "✅ REPOSITORY READY"

print_color "" $NC
print_color "🎉 New repository created successfully!" $GREEN
print_color "📁 Location: $NEW_DIR" $CYAN
print_color "" $NC
print_color "📋 NEXT STEPS TO PUSH TO GITHUB:" $PURPLE
print_color "" $NC
print_color "1️⃣  Create new repository on GitHub:" $YELLOW
print_color "   • Go to https://github.com/new" $CYAN
print_color "   • Repository name: hello-robot-stretch-simulation" $CYAN
print_color "   • Description: Hello Robot Stretch simulation with web teleop" $CYAN
print_color "   • Make it public" $CYAN
print_color "   • DON'T initialize with README (we have our own)" $CYAN
print_color "" $NC
print_color "2️⃣  Push to GitHub:" $YELLOW
print_color "   cd $NEW_DIR" $CYAN
print_color "   git remote add origin https://github.com/YOUR_USERNAME/hello-robot-stretch-simulation.git" $CYAN
print_color "   git branch -M main" $CYAN
print_color "   git push -u origin main" $CYAN
print_color "" $NC
print_color "3️⃣  Or use our push script:" $YELLOW
print_color "   cd $NEW_DIR" $CYAN
print_color "   # Copy push script from original directory" $CYAN
print_color "   cp /home/user/hello-robot-simulation/fix_merge_and_push.sh ." $CYAN
print_color "   ./fix_merge_and_push.sh YOUR_GITHUB_TOKEN" $CYAN
print_color "" $NC
print_color "📊 REPOSITORY STATS:" $PURPLE
echo "Files included: $(find "$NEW_DIR" -type f | wc -l)"
echo "Total size: $(du -sh "$NEW_DIR" | cut -f1)"
print_color "" $NC
print_color "🚀 Your complete robot simulation system is ready to share!" $GREEN
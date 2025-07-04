#!/bin/bash

echo "🔍 Debugging Robot Visibility in Gazebo"
echo "======================================"
echo ""

# Check if required files exist
echo "📁 Checking required files..."
files=(
    "stretch_ws/src/stretch_ros2/stretch_description/urdf/stretch_gazebo.urdf.xacro"
    "worlds/multi_world.world"
    "launch/multi_world_gazebo.launch.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - Found"
    else
        echo "❌ $file - Missing"
    fi
done

echo ""
echo "🔧 Checking ROS2 environment..."
source /opt/ros/humble/setup.bash
cd stretch_ws && source install/setup.bash

echo ""
echo "📦 Checking required packages..."
packages=("gazebo_ros" "robot_state_publisher" "joint_state_publisher" "stretch_description")

for pkg in "${packages[@]}"; do
    if ros2 pkg list | grep -q "^$pkg$"; then
        echo "✅ $pkg - Available"
    else
        echo "❌ $pkg - Missing"
    fi
done

echo ""
echo "🤖 Testing xacro processing..."
cd /home/kantar/Desktop/hello-robot
xacro_file="stretch_ws/src/stretch_ros2/stretch_description/urdf/stretch_gazebo.urdf.xacro"
if [ -f "$xacro_file" ]; then
    echo "Testing xacro file: $xacro_file"
    if xacro "$xacro_file" > /tmp/test_robot.urdf 2>/dev/null; then
        echo "✅ Xacro processing successful"
        echo "Generated URDF size: $(wc -l < /tmp/test_robot.urdf) lines"
        
        # Check for Gazebo plugins
        if grep -q "gazebo_ros" /tmp/test_robot.urdf; then
            echo "✅ Gazebo plugins found in URDF"
        else
            echo "⚠️  No Gazebo plugins found in URDF"
        fi
        
        # Check for physics properties
        if grep -q "collision" /tmp/test_robot.urdf; then
            echo "✅ Collision geometry found"
        else
            echo "⚠️  No collision geometry found"
        fi
        
        rm -f /tmp/test_robot.urdf
    else
        echo "❌ Xacro processing failed"
        echo "Trying manual xacro processing..."
        xacro "$xacro_file" 2>&1 | head -10
    fi
else
    echo "❌ Xacro file not found"
fi

echo ""
echo "🔍 Common Issues and Solutions:"
echo "1. Robot not visible in Gazebo but visible in RViz:"
echo "   → URDF missing Gazebo plugins or collision geometry"
echo "   → Robot spawned outside world boundaries"
echo "   → Gazebo materials not loading properly"
echo ""
echo "2. Robot pose not updating between RViz and Gazebo:"
echo "   → Missing joint_state_publisher or robot_state_publisher"
echo "   → /joint_states topic not being published correctly"
echo "   → ros2_control integration missing"
echo ""
echo "3. Robot appears as wireframe or transparent:"
echo "   → Missing material definitions in URDF"
echo "   → Gazebo visual elements not properly defined"
echo ""
echo "🚀 To fix robot visibility:"
echo "   1. Use the new launch file: ./launch_pick_place_world.sh"
echo "   2. Wait for Gazebo to fully load (may take 30+ seconds)"
echo "   3. Check Gazebo Models panel - robot should appear as 'stretch_robot'"
echo "   4. If still not visible, try: gz model --verbose --model=stretch_robot"
echo ""
echo "📊 Current status check:"
if pgrep -f "gzserver" > /dev/null; then
    echo "✅ Gazebo server is running"
else
    echo "❌ Gazebo server not running"
fi

if pgrep -f "robot_state_publisher" > /dev/null; then
    echo "✅ Robot state publisher is running"
else
    echo "❌ Robot state publisher not running"
fi

echo ""
echo "💡 Next steps:"
echo "   1. Kill all existing processes: killall -9 gzserver gzclient rviz2"
echo "   2. Launch with new script: ./launch_pick_place_world.sh"
echo "   3. Wait for complete startup (30-60 seconds)"
echo "   4. Check Gazebo World panel for 'stretch_robot' model"
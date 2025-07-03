#!/bin/bash

echo "🔍 Debug Robot Spawn in Gazebo"
echo "==============================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export GAZEBO_MODEL_PATH="$GAZEBO_MODEL_PATH:/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description:/home/kantar/Desktop/hello-robot/stretch_ws/install/stretch_description/share/stretch_description"

# Clean up
killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 2

echo "🚀 Starting Gazebo..."
gazebo --verbose /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
GAZEBO_PID=$!

echo "⏳ Waiting for Gazebo to start..."
sleep 15

if kill -0 $GAZEBO_PID 2>/dev/null; then
    echo "✅ Gazebo is running"
    
    # Check what models are available
    echo "🔍 Checking available models in Gazebo..."
    gz model --list
    
    echo ""
    echo "🧪 Testing simple box spawn first..."
    gz model --spawn-sdf --sdf-string='<?xml version="1.0"?>
<sdf version="1.6">
  <model name="test_box">
    <pose>0 0 1 0 0 0</pose>
    <static>false</static>
    <link name="link">
      <collision name="collision">
        <geometry>
          <box>
            <size>1 1 1</size>
          </box>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <box>
            <size>1 1 1</size>
          </box>
        </geometry>
        <material>
          <ambient>1 0 0 1</ambient>
          <diffuse>1 0 0 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>' --model-name test_box
    
    if [ $? -eq 0 ]; then
        echo "✅ Test box spawned successfully!"
        echo "🎯 You should see a RED BOX floating above the ground"
        echo "   If you can see the box, Gazebo spawning works"
    else
        echo "❌ Even simple box spawn failed"
    fi
    
    echo ""
    echo "Press ENTER to continue..."
    read
    
    # Try robot with simplified approach
    echo "🤖 Now testing robot spawn with debug info..."
    echo "Robot URDF file:"
    ls -la /home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf
    
    echo ""
    echo "Attempting robot spawn..."
    gz model --spawn-file=/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf --model-name=stretch_robot --pose-x=0 --pose-y=0 --pose-z=0.1
    
    if [ $? -eq 0 ]; then
        echo "✅ Robot spawn command completed"
        echo "🎯 Check Gazebo for robot (might be very small or at origin)"
        echo ""
        echo "🔍 Tips for finding the robot:"
        echo "   1. Look at the origin (center of grid)"
        echo "   2. Try zooming out (scroll wheel)"
        echo "   3. Reset view: View → Reset View"
        echo "   4. Look in World panel on left for 'stretch_robot'"
    else
        echo "❌ Robot spawn failed"
    fi
    
    echo ""
    echo "🔍 Current models in world:"
    gz model --list
    
    echo ""
    echo "Press ENTER to exit..."
    read
    
    kill $GAZEBO_PID
    sleep 2
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    
else
    echo "❌ Gazebo failed to start"
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
fi

echo "🏁 Debug completed!"
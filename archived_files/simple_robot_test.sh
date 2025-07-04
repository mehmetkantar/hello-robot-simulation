#!/bin/bash

echo "🤖 Simple Robot Test with Basic Shapes"
echo "======================================"

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Clean up
killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 2

echo "🔧 Creating simplified robot world..."

# Create a world with a simple robot representation
cat > /tmp/simple_robot_world.world << 'EOF'
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="simple_robot_world">
    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Simple Robot Representation -->
    <model name="simple_stretch">
      <pose>0 0 0.1 0 0 0</pose>
      <static>false</static>
      
      <!-- Base -->
      <link name="base">
        <pose>0 0 0.1 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.5 0.3 0.2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.5 0.3 0.2</size>
            </box>
          </geometry>
          <material>
            <ambient>0 0 1 1</ambient>
            <diffuse>0 0 1 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Mast -->
      <link name="mast">
        <pose>0 0 0.5 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.1 0.1 0.8</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.1 0.1 0.8</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0.5 0 1</ambient>
            <diffuse>1 0.5 0 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Arm -->
      <link name="arm">
        <pose>0.3 0 0.7 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.4 0.08 0.08</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.4 0.08 0.08</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0.5 0 1</ambient>
            <diffuse>1 0.5 0 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Gripper -->
      <link name="gripper">
        <pose>0.6 0 0.7 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.1 0.15 0.1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.1 0.15 0.1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Head -->
      <link name="head">
        <pose>0 0 1.0 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 0.15 0.1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 0.15 0.1</size>
            </box>
          </geometry>
          <material>
            <ambient>0 1 0 1</ambient>
            <diffuse>0 1 0 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Left Wheel -->
      <link name="left_wheel">
        <pose>0 0.2 0.05 1.57 0 0</pose>
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.05</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.05</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.3 1</ambient>
            <diffuse>0.3 0.3 0.3 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Right Wheel -->
      <link name="right_wheel">
        <pose>0 -0.2 0.05 1.57 0 0</pose>
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.05</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.05</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.3 1</ambient>
            <diffuse>0.3 0.3 0.3 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Joints would go here in a real robot -->
    </model>

    <!-- Reference objects for scale -->
    <model name="scale_reference">
      <pose>2 0 0.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 1 0 1</ambient>
            <diffuse>1 1 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Lighting -->
    <light name="sun" type="directional">
      <cast_shadows>1</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
  </world>
</sdf>
EOF

echo "🚀 Starting Gazebo with simple robot..."
gazebo /tmp/simple_robot_world.world &
GAZEBO_PID=$!

echo "⏳ Waiting for Gazebo to load..."
sleep 15

if kill -0 $GAZEBO_PID 2>/dev/null; then
    echo "✅ Gazebo is running!"
    echo ""
    echo "🎯 You should now see a colorful robot made of basic shapes:"
    echo "   🔵 Blue base (rectangular)"
    echo "   🟠 Orange mast (vertical bar)"
    echo "   🟠 Orange arm (horizontal bar extending right)"
    echo "   🔴 Red gripper (at end of arm)"
    echo "   🟢 Green head (on top of mast)"
    echo "   ⚫ Gray wheels (on sides)"
    echo "   🟡 Yellow reference cube (for scale)"
    echo ""
    echo "Can you see this colorful robot? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🎉 Excellent! Robot visibility works!"
        echo "   Now we know the real robot can be made visible"
        echo "   The issue is with the mesh files in the original URDF"
    else
        echo "🤔 Hmm, still not visible. Try:"
        echo "   1. Mouse wheel to zoom out"
        echo "   2. Look around the origin (center of grid)"
        echo "   3. View → Reset View in Gazebo menu"
    fi
    
    echo ""
    echo "Press ENTER to close and test the real robot simulation..."
    read
    
    kill $GAZEBO_PID
    sleep 2
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    
    echo ""
    echo "🚀 Now testing your real robot simulation..."
    echo "   This should work now that we know visibility is OK"
    
    cd /home/kantar/Desktop/hello-robot
    source ~/.bashrc
    ./start_stretch_simulation.sh
    
else
    echo "❌ Gazebo failed to start"
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
fi
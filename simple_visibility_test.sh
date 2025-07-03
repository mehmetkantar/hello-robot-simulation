#!/bin/bash

echo "🔍 Simple Visibility Test"
echo "========================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Clean up
killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 2

echo "🚀 Starting Gazebo with a simple test world..."

# Create a simple world with visible objects
cat > /tmp/test_world.world << 'EOF'
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="test_world">
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

    <!-- Test Box -->
    <model name="test_box">
      <pose>0 0 1 0 0 0</pose>
      <static>false</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>2 2 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>2 2 2</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
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

echo "Starting Gazebo with test world..."
gazebo /tmp/test_world.world &
GAZEBO_PID=$!

echo "⏳ Waiting 15 seconds for Gazebo to load..."
sleep 15

if kill -0 $GAZEBO_PID 2>/dev/null; then
    echo "✅ Gazebo is running!"
    echo ""
    echo "🎯 What you should see in Gazebo window:"
    echo "   - Gray ground plane (grid)"
    echo "   - Large RED CUBE floating 1 meter above ground"
    echo "   - You should be able to rotate view with mouse"
    echo ""
    echo "Can you see the RED CUBE? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "✅ Great! Gazebo visibility works"
        echo "   The issue is specifically with robot model loading"
    else
        echo "❌ Visibility issue detected"
        echo "   This suggests a graphics/rendering problem"
        echo ""
        echo "🔍 Try these in Gazebo window:"
        echo "   1. Use mouse wheel to zoom out"
        echo "   2. Click and drag to rotate view"
        echo "   3. Try View → Reset View in menu"
        echo "   4. Check if World panel shows 'test_box' model"
    fi
    
    echo ""
    echo "Press ENTER to close Gazebo..."
    read
    
    kill $GAZEBO_PID
    sleep 2
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
    
else
    echo "❌ Gazebo failed to start"
    killall -9 gzserver gzclient gazebo 2>/dev/null || true
fi

echo "🏁 Test completed!"
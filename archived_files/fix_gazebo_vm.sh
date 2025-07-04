#!/bin/bash

echo "🔧 Gazebo VM Fix Script"
echo "======================="

# Fix 1: Install graphics utilities
echo "📦 Installing graphics utilities..."
sudo apt update
sudo apt install -y mesa-utils

# Fix 2: Set environment for VM/Wayland compatibility
echo "🌊 Setting up Wayland/VM compatibility..."
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Fix 3: Test with software rendering
echo "🧪 Testing Gazebo with software rendering..."
echo "Environment variables set:"
echo "  LIBGL_ALWAYS_SOFTWARE=1 (forces software rendering)"
echo "  QT_QPA_PLATFORM=xcb (uses X11 backend)"
echo "  XDG_SESSION_TYPE=x11 (forces X11 mode)"

# Test basic OpenGL
echo ""
echo "🎮 Testing OpenGL capabilities:"
glxinfo | grep -i "renderer\|version" | head -5

# Test Gazebo with new settings
echo ""
echo "🚀 Testing Gazebo with VM-friendly settings..."
echo "This should work in your VM environment:"

timeout 10s gazebo --verbose /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
GAZEBO_PID=$!

sleep 8

if kill -0 $GAZEBO_PID 2>/dev/null; then
    echo "✅ Gazebo started successfully with VM settings!"
    echo "🎯 You should see Gazebo window (may be slow in VM)"
    echo "Press ENTER to continue..."
    read
    kill $GAZEBO_PID
else
    echo "❌ Still having issues. Trying alternative approach..."
    
    # Alternative: headless mode first
    echo "🔄 Trying headless mode..."
    timeout 5s gzserver /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
    SERVER_PID=$!
    
    sleep 3
    
    if kill -0 $SERVER_PID 2>/dev/null; then
        echo "✅ Gazebo server works in headless mode"
        kill $SERVER_PID
        
        echo "🎮 Now trying client..."
        gzserver /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
        SERVER_PID=$!
        sleep 2
        
        gzclient &
        CLIENT_PID=$!
        
        echo "✅ Started server and client separately"
        echo "Press ENTER to stop..."
        read
        
        kill $SERVER_PID $CLIENT_PID 2>/dev/null
    else
        echo "❌ Even headless mode fails"
        echo "This suggests a deeper Gazebo installation issue"
    fi
fi

# Cleanup
killall -9 gzserver gzclient gazebo 2>/dev/null || true

echo ""
echo "💡 Permanent Fix Instructions:"
echo "Add these lines to your ~/.bashrc:"
echo "export LIBGL_ALWAYS_SOFTWARE=1"
echo "export QT_QPA_PLATFORM=xcb" 
echo "export XDG_SESSION_TYPE=x11"
echo ""
echo "Then run: source ~/.bashrc"
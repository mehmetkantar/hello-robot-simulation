#!/bin/bash

echo "🔍 Gazebo Debug Diagnostic"
echo "=========================="

# Check system info
echo "🖥️  System Information:"
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"

# Check graphics
echo ""
echo "🎮 Graphics Information:"
if command -v glxinfo >/dev/null 2>&1; then
    echo "OpenGL Renderer: $(glxinfo | grep "OpenGL renderer" | cut -d: -f2)"
    echo "OpenGL Version: $(glxinfo | grep "OpenGL version" | cut -d: -f2)"
else
    echo "⚠️  glxinfo not installed. Install with: sudo apt install mesa-utils"
fi

echo "Display: $DISPLAY"
echo "Session Type: $XDG_SESSION_TYPE"

# Check Gazebo installation
echo ""
echo "🔧 Gazebo Installation Check:"
echo "Gazebo executable: $(which gazebo)"
echo "Gazebo version (direct):"
gazebo --version 2>&1 | head -5

# Check if Gazebo can start at all
echo ""
echo "🧪 Testing Gazebo Startup (5 second timeout):"
echo "Starting gazebo with no arguments..."

timeout 5s gazebo --help >/dev/null 2>&1
if [ $? -eq 124 ]; then
    echo "❌ Gazebo help command timed out"
    echo "   This suggests Gazebo has a fundamental startup issue"
elif [ $? -eq 0 ]; then
    echo "✅ Gazebo help command works"
else
    echo "❌ Gazebo help command failed with error code $?"
fi

# Test gzserver separately
echo ""
echo "🧪 Testing Gazebo Server Only:"
echo "Starting gzserver (no GUI) for 5 seconds..."

timeout 5s gzserver --version >/dev/null 2>&1
if [ $? -eq 124 ]; then
    echo "❌ gzserver timed out"
elif [ $? -eq 0 ]; then
    echo "✅ gzserver version works"
else
    echo "❌ gzserver failed"
fi

# Check for common issues
echo ""
echo "🔍 Checking for Common Issues:"

# Check if running in virtual machine
if [ -f /proc/cpuinfo ]; then
    if grep -qi "hypervisor\|vmware\|virtualbox" /proc/cpuinfo; then
        echo "⚠️  Running in virtual machine - 3D acceleration may be disabled"
    fi
fi

# Check memory
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
echo "Available Memory: ${MEMORY_GB}GB"
if [ "$MEMORY_GB" -lt 4 ]; then
    echo "⚠️  Low memory - Gazebo needs at least 4GB RAM"
fi

# Check for conflicting processes
echo ""
echo "🔍 Checking for Gazebo processes:"
if pgrep -f gazebo >/dev/null; then
    echo "⚠️  Gazebo processes still running:"
    pgrep -f gazebo | while read pid; do
        echo "   PID $pid: $(ps -p $pid -o cmd --no-headers)"
    done
    echo "   Run: killall -9 gzserver gzclient gazebo"
else
    echo "✅ No Gazebo processes running"
fi

echo ""
echo "🎯 Recommendations:"
echo "1. If this is a VM, enable 3D acceleration"
echo "2. If low memory, close other applications"
echo "3. Try: sudo apt update && sudo apt install --reinstall gazebo11"
echo "4. Try: export LIBGL_ALWAYS_SOFTWARE=1 (software rendering)"
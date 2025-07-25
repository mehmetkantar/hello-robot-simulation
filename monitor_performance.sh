#!/bin/bash

# Performance Monitoring Script
# Monitors GPU usage, FPS, and SLAM performance

echo "🔍 Performance Monitoring Dashboard"
echo "=================================="

# Function to monitor GPU with detailed info
monitor_gpu_detailed() {
    echo "📊 GPU Performance Monitor"
    echo "-------------------------"
    
    while true; do
        # Get detailed GPU info
        GPU_INFO=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu,clocks.current.graphics,clocks.current.memory --format=csv,noheader,nounits)
        
        if [ ! -z "$GPU_INFO" ]; then
            echo "$GPU_INFO" | awk -F', ' '{
                printf "\r⚡ GPU: %s%% | Memory: %s/%sMB (%.1f%%) | Power: %sW | Temp: %s°C | GPU Clock: %sMHz | Mem Clock: %sMHz", 
                $1, $2, $3, ($2/$3)*100, $4, $5, $6, $7
            }'
        fi
        
        sleep 2
    done
}

# Function to check ROS2 topic rates
check_topic_rates() {
    echo -e "\n📡 ROS2 Topic Rates"
    echo "-------------------"
    
    TOPICS=("/scan" "/odom" "/joint_states" "/camera/d405/color/image_raw")
    
    for topic in "${TOPICS[@]}"; do
        # Check if topic exists and get rate
        if ros2 topic list 2>/dev/null | grep -q "^$topic$"; then
            echo -n "• $topic: "
            timeout 5s ros2 topic hz "$topic" 2>/dev/null | grep "average rate:" | head -1 | awk '{print $3}' | xargs printf "%.1f Hz\n" || echo "No data"
        else
            echo "• $topic: Not available"
        fi
    done
}

# Function to monitor system resources
monitor_system() {
    echo -e "\n💻 System Resources"
    echo "-------------------"
    
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    echo "• CPU Usage: ${CPU_USAGE}%"
    
    # Memory usage
    MEM_INFO=$(free -h | grep "Mem:")
    MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
    MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
    echo "• Memory: $MEM_USED / $MEM_TOTAL"
    
    # Load average
    LOAD=$(uptime | awk -F'load average:' '{print $2}')
    echo "• Load Average:$LOAD"
}

# Main monitoring function
main_monitor() {
    echo "🚀 Starting comprehensive performance monitoring..."
    echo "💡 Press Ctrl+C to stop"
    echo ""
    
    # Start GPU monitoring in background
    monitor_gpu_detailed &
    GPU_PID=$!
    
    # Check ROS2 topics every 10 seconds
    while true; do
        sleep 5
        clear
        echo "🔍 Performance Monitoring Dashboard - $(date)"
        echo "=============================================="
        
        # Show current GPU info (will be updated by background process)
        echo ""
        
        # Check ROS2 topics
        check_topic_rates
        
        # System resources
        monitor_system
        
        echo ""
        echo "🎯 Performance Targets:"
        echo "• GPU Usage: >80% (currently monitoring above)"
        echo "• GPU Memory: >3GB (currently monitoring above)" 
        echo "• LiDAR Rate: ~5Hz"
        echo "• Camera Rate: ~20Hz"
        echo "• No SLAM queue overflow warnings"
        
        sleep 5
    done
}

# Cleanup function
cleanup() {
    echo -e "\n🛑 Stopping monitoring..."
    if [ ! -z "$GPU_PID" ]; then
        kill $GPU_PID 2>/dev/null
    fi
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Check if ROS2 is available
if ! command -v ros2 &> /dev/null; then
    echo "⚠️  ROS2 not found - GPU monitoring only"
    echo ""
    monitor_gpu_detailed
else
    echo "✅ ROS2 found - Full monitoring available"
    echo ""
    main_monitor
fi
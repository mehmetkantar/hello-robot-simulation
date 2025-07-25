#!/bin/bash

# Test script for maximum GPU utilization
# Monitors performance while running simulation

echo "🚀 Testing Maximum GPU Utilization"
echo "=================================="

# Apply maximum GPU optimizations
python3 max_gpu_optimization.py

echo ""
echo "📊 Starting GPU monitoring..."

# Function to monitor GPU in background
monitor_gpu() {
    while true; do
        nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu \
                   --format=csv,noheader,nounits | \
        awk -F', ' '{printf "⚡ GPU: %s%% | Memory: %s/%sMB | Power: %sW | Temp: %s°C\n", $1, $2, $3, $4, $5}'
        sleep 5
    done
}

# Start monitoring in background
monitor_gpu &
MONITOR_PID=$!

echo "🎯 GPU monitoring started (PID: $MONITOR_PID)"
echo "💡 To stop monitoring: kill $MONITOR_PID"
echo ""
echo "📈 Expected improvements:"
echo "   • GPU Usage: 37% → 60-80%"
echo "   • Memory: 931MB → 2-4GB"  
echo "   • Performance: Additional 2x boost"
echo ""
echo "🚀 Ready to launch simulation with maximum GPU utilization!"
echo "   Run: ./launch_full_simulation.sh"
echo ""
echo "Press Ctrl+C to stop monitoring"

# Keep script running
wait $MONITOR_PID
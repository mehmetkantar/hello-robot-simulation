#!/usr/bin/env python3
"""
High FPS SLAM Performance Test
Tests the improved sensor rates and SLAM performance
"""

import os
import sys
import time
import subprocess
import threading

def monitor_topics():
    """Monitor ROS2 topic rates"""
    topics_to_monitor = [
        '/scan',
        '/odom', 
        '/joint_states',
        '/camera/d405/color/image_raw',
        '/tf'
    ]
    
    print("📊 Monitoring ROS2 topic rates...")
    
    for topic in topics_to_monitor:
        try:
            # Check if topic exists
            result = subprocess.run(['ros2', 'topic', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            
            if topic in result.stdout:
                print(f"✅ {topic} - Available")
                
                # Get topic rate (run in background)
                threading.Thread(target=check_topic_rate, args=(topic,), daemon=True).start()
            else:
                print(f"❌ {topic} - Not available")
                
        except Exception as e:
            print(f"⚠️ Error checking {topic}: {e}")

def check_topic_rate(topic):
    """Check individual topic rate"""
    try:
        result = subprocess.run(['ros2', 'topic', 'hz', topic], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            # Extract rate from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'average rate:' in line:
                    rate = line.split('average rate:')[1].strip()
                    print(f"📈 {topic}: {rate}")
                    break
    except Exception as e:
        print(f"⚠️ Error measuring {topic} rate: {e}")

def test_slam_performance():
    """Test SLAM performance with high rates"""
    print("🎯 High-Rate SLAM Performance Test")
    print("=" * 40)
    
    print("\n🚀 Improved Sensor Rates:")
    print("• Joint States: 2 Hz → 20 Hz (10x increase)")
    print("• Odometry: 2 Hz → 20 Hz (10x increase)")  
    print("• LiDAR Scan: 2 Hz → 10 Hz (5x increase)")
    print("• Camera Feeds: 1 Hz → 30 Hz (30x increase)")
    print("• TF Updates: 2 Hz → 20 Hz (10x increase)")
    
    print("\n📡 LiDAR Improvements:")
    print("• Resolution: 5° → 1° (360 rays vs 72)")
    print("• Range: 10m → 12m (extended mapping)")
    print("• Min range: 0.1m → 0.05m (better close detection)")
    
    print("\n🗺️ SLAM Toolbox Optimizations:")
    print("• Transform updates: 5 Hz → 20 Hz")
    print("• Map updates: 5s → 2s intervals")
    print("• Resolution: 0.05m → 0.03m (higher detail)")
    print("• Scan processing: Every 2nd → Every scan")
    
    print("\n📊 Expected Performance Impact:")
    print("• More accurate localization")
    print("• Smoother robot movement visualization") 
    print("• Higher quality maps")
    print("• Better real-time SLAM performance")
    print("• Increased CPU/GPU usage for processing")
    
    print("\n💡 Monitor with:")
    print("ros2 topic hz /scan")
    print("ros2 topic hz /odom")
    print("ros2 topic hz /joint_states")
    
    # Monitor topics if ROS2 is available
    try:
        result = subprocess.run(['ros2', 'topic', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("\n🔍 Checking current topic rates...")
            monitor_topics()
        else:
            print("\n⚠️ ROS2 not running - start simulation first")
    except:
        print("\n⚠️ ROS2 not available - install ROS2 first")

if __name__ == "__main__":
    test_slam_performance()
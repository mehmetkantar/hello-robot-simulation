#!/usr/bin/env python3
"""
Direct command tester to check MuJoCo response
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

def main():
    rclpy.init()
    node = Node('direct_command_test')
    
    # Publisher
    cmd_pub = node.create_publisher(Twist, '/cmd_vel', 10)
    
    print("🤖 Testing direct MuJoCo commands...")
    time.sleep(2)  # Let publisher connect
    
    # Test 1: Move forward
    print("📍 Test 1: Moving forward...")
    twist = Twist()
    twist.linear.x = 0.3
    for i in range(20):  # Publish for 2 seconds
        cmd_pub.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.1)
        
    # Stop
    twist.linear.x = 0.0
    cmd_pub.publish(twist)
    print("✅ Forward motion test complete")
    
    time.sleep(2)
    
    # Test 2: Turn
    print("📍 Test 2: Turning...")
    twist.angular.z = 0.5
    for i in range(20):  # Publish for 2 seconds
        cmd_pub.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.1)
        
    # Stop
    twist.angular.z = 0.0
    cmd_pub.publish(twist)
    print("✅ Turning test complete")
    
    print("🎉 Direct command tests complete!")
    print("💡 Check MuJoCo window to see if robot moved")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
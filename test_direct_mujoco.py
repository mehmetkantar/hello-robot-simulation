#!/usr/bin/env python3
"""
Direct test to MuJoCo simulation - bypass all bridges
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

def main():
    rclpy.init()
    node = Node('direct_mujoco_test')
    
    # Publish directly to what MuJoCo should be listening to
    cmd_pub = node.create_publisher(Twist, '/cmd_vel', 10)
    
    print("🤖 Direct MuJoCo test - bypassing all bridges...")
    time.sleep(2)  # Let publisher connect
    
    print("📍 Sending strong forward command directly to /cmd_vel...")
    twist = Twist()
    twist.linear.x = 1.0  # Strong command
    
    for i in range(100):  # Send for 10 seconds
        cmd_pub.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.01)
        time.sleep(0.1)
        
        if i % 10 == 0:
            print(f"Sending: linear.x={twist.linear.x}")
    
    # Stop
    twist.linear.x = 0.0
    cmd_pub.publish(twist)
    
    print("✅ Direct test complete!")
    print("💡 Check MuJoCo window - if robot moved, bridges are the issue")
    print("💡 If robot didn't move, MuJoCo simulation has a problem")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Test GUI command pathway to MuJoCo
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import time

def main():
    rclpy.init()
    node = Node('gui_command_test')
    
    # Publishers to GUI topics (same as GUI uses)
    cmd_pub = node.create_publisher(Twist, '/stretch/cmd_vel', 10)
    lift_pub = node.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
    arm_pub = node.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
    
    print("🤖 Testing GUI command pathway...")
    time.sleep(2)  # Let publishers connect
    
    # Test base movement (larger command)
    print("📍 Test 1: Base movement via GUI pathway...")
    twist = Twist()
    twist.linear.x = 0.5  # Larger command
    for i in range(30):  # 3 seconds of commands
        cmd_pub.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.1)
        
    # Stop
    twist.linear.x = 0.0
    cmd_pub.publish(twist)
    print("✅ Base movement test complete")
    
    time.sleep(2)
    
    # Test lift movement
    print("📍 Test 2: Lift movement...")
    lift_msg = Float64()
    lift_msg.data = 0.8  # Raise lift
    lift_pub.publish(lift_msg)
    time.sleep(3)
    
    lift_msg.data = 0.5  # Lower lift
    lift_pub.publish(lift_msg)
    print("✅ Lift test complete")
    
    time.sleep(2)
    
    # Test arm extension
    print("📍 Test 3: Arm extension...")
    arm_msg = Float64()
    arm_msg.data = 0.3  # Extend arm
    arm_pub.publish(arm_msg)
    time.sleep(3)
    
    arm_msg.data = 0.1  # Retract arm
    arm_pub.publish(arm_msg)
    print("✅ Arm extension test complete")
    
    print("🎉 GUI pathway tests complete!")
    print("💡 Check MuJoCo window - robot should have moved base, lift, and arm")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
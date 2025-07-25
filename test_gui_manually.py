#!/usr/bin/env python3
"""
Manual test of GUI publishing - sends commands like the GUI would
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import time

def main():
    rclpy.init()
    node = Node('manual_gui_test')
    
    # Publishers to the exact same topics as GUI
    cmd_vel_pub = node.create_publisher(Twist, '/stretch/cmd_vel', 10)
    lift_pub = node.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
    arm_pub = node.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
    
    print("🤖 Manual GUI simulation test...")
    time.sleep(2)
    
    # Simulate joystick being moved forward
    print("📍 Simulating forward joystick movement...")
    twist = Twist()
    twist.linear.x = 0.3
    
    for i in range(50):  # Publish like GUI would (20Hz for 2.5 seconds)
        cmd_vel_pub.publish(twist)
        rclpy.spin_once(node, timeout_sec=0.01)
        time.sleep(0.05)  # 20Hz like GUI
        
        if i % 10 == 0:
            print(f"Publishing: linear.x={twist.linear.x}")
    
    # Stop
    print("📍 Stopping...")
    twist.linear.x = 0.0
    cmd_vel_pub.publish(twist)
    
    time.sleep(2)
    
    # Simulate lift movement
    print("📍 Simulating lift movement...")
    lift_msg = Float64()
    lift_msg.data = 0.7
    lift_pub.publish(lift_msg)
    print(f"Published lift: {lift_msg.data}")
    
    time.sleep(3)
    
    # Simulate arm movement  
    print("📍 Simulating arm extension...")
    arm_msg = Float64()
    arm_msg.data = 0.25
    arm_pub.publish(arm_msg)
    print(f"Published arm: {arm_msg.data}")
    
    print("🎉 Manual GUI test complete!")
    print("💡 If this moves the robot but GUI doesn't, then GUI has a bug")
    print("💡 If this doesn't move robot either, then MuJoCo has an issue")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
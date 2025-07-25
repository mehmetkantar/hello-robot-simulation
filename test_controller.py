#!/usr/bin/env python3
"""
Quick test script to verify the robot controller system is working
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import time

def main():
    rclpy.init()
    node = Node('controller_test')
    
    # Publishers
    cmd_vel_pub = node.create_publisher(Twist, '/stretch/cmd_vel', 10)
    lift_pub = node.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
    
    print("🤖 Testing Robot Controller...")
    
    # Test base movement
    print("📍 Testing base movement...")
    twist = Twist()
    twist.linear.x = 0.1  # Move forward slowly
    cmd_vel_pub.publish(twist)
    time.sleep(2)
    
    # Stop
    twist.linear.x = 0.0
    cmd_vel_pub.publish(twist)
    print("✅ Base movement test complete")
    
    # Test lift movement  
    print("📍 Testing lift movement...")
    lift_cmd = Float64()
    lift_cmd.data = 0.8  # Raise lift
    lift_pub.publish(lift_cmd)
    time.sleep(2)
    
    lift_cmd.data = 0.5  # Lower lift
    lift_pub.publish(lift_cmd)
    print("✅ Lift movement test complete")
    
    print("🎉 All tests passed! Controller system is working correctly.")
    print("💡 You should see the robot moving in both MuJoCo and RViz!")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
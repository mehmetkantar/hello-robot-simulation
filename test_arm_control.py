#!/usr/bin/env python3
"""
Test arm control by sending direct joint commands
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time

def main():
    rclpy.init()
    node = Node('arm_control_test')
    
    # Publishers for arm control
    lift_pub = node.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
    arm_pub = node.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
    wrist_yaw_pub = node.create_publisher(Float64, '/stretch_controller/wrist_yaw/command', 10)
    gripper_pub = node.create_publisher(Float64, '/stretch_controller/gripper_joint/command', 10)
    
    print("🦾 Testing arm control commands...")
    time.sleep(2)  # Let publishers connect
    
    # Test lift
    print("🏗️ Test 1: Moving lift up...")
    lift_msg = Float64()
    lift_msg.data = 0.8
    for i in range(10):
        lift_pub.publish(lift_msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.1)
    
    time.sleep(3)
    
    # Test arm extension
    print("🦾 Test 2: Extending arm...")
    arm_msg = Float64()
    arm_msg.data = 0.3
    for i in range(10):
        arm_pub.publish(arm_msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.1)
    
    time.sleep(3)
    
    # Test wrist yaw
    print("🔄 Test 3: Rotating wrist...")
    wrist_msg = Float64()
    wrist_msg.data = 1.0
    for i in range(10):
        wrist_yaw_pub.publish(wrist_msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.1)
    
    time.sleep(3)
    
    # Test gripper
    print("✋ Test 4: Opening gripper...")
    gripper_msg = Float64()
    gripper_msg.data = 0.4
    for i in range(10):
        gripper_pub.publish(gripper_msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.1)
    
    time.sleep(2)
    
    # Return to home
    print("🏠 Returning to home position...")
    lift_msg.data = 0.5
    arm_msg.data = 0.1
    wrist_msg.data = 0.0
    gripper_msg.data = 0.0
    
    for i in range(20):
        lift_pub.publish(lift_msg)
        arm_pub.publish(arm_msg) 
        wrist_yaw_pub.publish(wrist_msg)
        gripper_pub.publish(gripper_msg)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(0.1)
    
    print("🎉 Arm control test complete!")
    print("💡 Check MuJoCo window - robot arms should have moved!")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
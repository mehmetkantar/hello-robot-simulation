#!/usr/bin/env python3
"""
Simple Robot Movement Test
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class RobotMovementTest(Node):
    def __init__(self):
        super().__init__('robot_movement_test')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Robot Movement Test Node Started")
        
    def move_forward(self, speed=0.3, duration=2.0):
        """Move robot forward for specified duration"""
        twist = Twist()
        twist.linear.x = speed
        
        self.get_logger().info(f"Moving forward at {speed} m/s for {duration} seconds")
        
        start_time = time.time()
        rate = self.create_rate(10)  # 10 Hz
        
        while (time.time() - start_time) < duration:
            self.cmd_vel_pub.publish(twist)
            rate.sleep()
            
        # Stop robot
        twist.linear.x = 0.0
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info("Movement complete, robot stopped")
        
    def rotate_left(self, speed=0.5, duration=2.0):
        """Rotate robot left for specified duration"""
        twist = Twist()
        twist.angular.z = speed
        
        self.get_logger().info(f"Rotating left at {speed} rad/s for {duration} seconds")
        
        start_time = time.time()
        rate = self.create_rate(10)
        
        while (time.time() - start_time) < duration:
            self.cmd_vel_pub.publish(twist)
            rate.sleep()
            
        # Stop robot
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info("Rotation complete, robot stopped")

def main():
    rclpy.init()
    
    test_node = RobotMovementTest()
    
    try:
        print("🤖 Testing robot movement...")
        print("1. Moving forward...")
        test_node.move_forward(speed=0.3, duration=3.0)
        
        time.sleep(1)
        
        print("2. Rotating left...")
        test_node.rotate_left(speed=0.5, duration=2.0)
        
        time.sleep(1)
        
        print("3. Moving forward again...")
        test_node.move_forward(speed=0.3, duration=2.0)
        
        print("✅ Movement test complete!")
        print("Watch MuJoCo and RViz windows to see if robot moved")
        
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        test_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
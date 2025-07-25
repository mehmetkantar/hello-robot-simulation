#!/usr/bin/env python3
"""
Debug GUI output - shows what the GUI is actually publishing
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class DebugSubscriber(Node):
    def __init__(self):
        super().__init__('debug_gui_output')
        
        # Subscribers to GUI topics
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/stretch/cmd_vel', self.cmd_vel_callback, 10)
        self.lift_sub = self.create_subscription(
            Float64, '/stretch_controller/lift_joint/command', self.lift_callback, 10)
        self.arm_sub = self.create_subscription(
            Float64, '/stretch_controller/arm_joint/command', self.arm_callback, 10)
        self.wrist_yaw_sub = self.create_subscription(
            Float64, '/stretch_controller/wrist_yaw/command', self.wrist_yaw_callback, 10)
        self.gripper_sub = self.create_subscription(
            Float64, '/stretch_controller/gripper_joint/command', self.gripper_callback, 10)
        
        self.get_logger().info("🔍 Debug subscriber started - monitoring GUI outputs...")
        self.get_logger().info("📱 Use the GUI joystick and sliders to see their output here")
    
    def cmd_vel_callback(self, msg):
        if abs(msg.linear.x) > 0.001 or abs(msg.angular.z) > 0.001:
            self.get_logger().info(f"🚗 Base cmd: linear={msg.linear.x:.3f}, angular={msg.angular.z:.3f}")
    
    def lift_callback(self, msg):
        self.get_logger().info(f"⬆️ Lift: {msg.data:.3f}")
    
    def arm_callback(self, msg):
        self.get_logger().info(f"🦾 Arm: {msg.data:.3f}")
    
    def wrist_yaw_callback(self, msg):
        self.get_logger().info(f"🔄 Wrist Yaw: {msg.data:.3f}")
    
    def gripper_callback(self, msg):
        self.get_logger().info(f"✋ Gripper: {msg.data:.3f}")

def main():
    rclpy.init()
    debug_node = DebugSubscriber()
    
    print("🔍 Debug Monitor Running...")
    print("📱 Move the GUI joystick and sliders to see their output")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        rclpy.spin(debug_node)
    except KeyboardInterrupt:
        print("\n🛑 Debug monitor stopped")
    
    debug_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
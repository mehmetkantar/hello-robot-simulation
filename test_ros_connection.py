#!/usr/bin/env python3
"""
Test ROS2 connection and cmd_vel publishing
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class ROS2DiagnosticTest(Node):
    def __init__(self):
        super().__init__('ros2_diagnostic_test')
        
        # Publisher
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscriber to see if our own messages come back
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_received, 10)
        
        self.messages_sent = 0
        self.messages_received = 0
        
        print("🔍 ROS2 Diagnostic Test Started")
        print("Testing cmd_vel topic publishing and receiving...")
        
    def cmd_vel_received(self, msg):
        """Callback when we receive a cmd_vel message"""
        self.messages_received += 1
        print(f"📥 Received cmd_vel: linear.x={msg.linear.x:.3f}, angular.z={msg.angular.z:.3f}")
        
    def send_test_command(self, linear_x=0.0, angular_z=0.0):
        """Send a test movement command"""
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        
        self.cmd_vel_pub.publish(twist)
        self.messages_sent += 1
        
        print(f"📤 Sent cmd_vel #{self.messages_sent}: linear.x={linear_x:.3f}, angular.z={angular_z:.3f}")

def main():
    rclpy.init()
    
    test_node = ROS2DiagnosticTest()
    
    try:
        print("\n🚀 Starting ROS2 cmd_vel diagnostic test...")
        print("=" * 50)
        
        # Spin once to initialize
        rclpy.spin_once(test_node, timeout_sec=1.0)
        
        # Test 1: Send forward command
        print("\n🔧 Test 1: Sending forward command...")
        test_node.send_test_command(linear_x=0.3)
        
        # Wait and spin
        for i in range(10):
            rclpy.spin_once(test_node, timeout_sec=0.1)
            time.sleep(0.1)
        
        # Test 2: Send rotation command
        print("\n🔧 Test 2: Sending rotation command...")
        test_node.send_test_command(angular_z=0.5)
        
        # Wait and spin
        for i in range(10):
            rclpy.spin_once(test_node, timeout_sec=0.1)
            time.sleep(0.1)
        
        # Test 3: Send stop command
        print("\n🔧 Test 3: Sending stop command...")
        test_node.send_test_command(linear_x=0.0, angular_z=0.0)
        
        # Final wait
        for i in range(10):
            rclpy.spin_once(test_node, timeout_sec=0.1)
            time.sleep(0.1)
        
        # Results
        print("\n📊 DIAGNOSTIC RESULTS:")
        print(f"   Messages sent: {test_node.messages_sent}")
        print(f"   Messages received back: {test_node.messages_received}")
        
        if test_node.messages_received >= test_node.messages_sent:
            print("✅ ROS2 cmd_vel topic is working correctly")
            print("   Issue is likely in the SLAM bridge receiving/processing messages")
        elif test_node.messages_received > 0:
            print("⚠️  Some messages are getting through")
            print("   Possible timing or QoS issue")
        else:
            print("❌ No messages received back")
            print("   ROS2 topic system may not be working properly")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        test_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
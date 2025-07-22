#!/usr/bin/env python3
"""
Test Web Controller Connection to Robot
Verifies the complete command flow: Web Controller → ROS2 Topics → SLAM Bridge → MuJoCo
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import time

class WebControllerConnectionTest(Node):
    def __init__(self):
        super().__init__('web_controller_connection_test')
        
        # Publishers matching web controller topics
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lift_pub = self.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
        self.arm_pub = self.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
        self.head_pan_pub = self.create_publisher(Float64, '/stretch_controller/head_pan_joint/command', 10)
        self.head_tilt_pub = self.create_publisher(Float64, '/stretch_controller/head_tilt_joint/command', 10)
        
        print("🧪 Web Controller Connection Test")
        print("=" * 50)
        
    def test_base_control(self):
        """Test base movement commands"""
        print("\n🚗 Testing Base Control...")
        
        # Forward
        twist = Twist()
        twist.linear.x = 0.3
        self.cmd_vel_pub.publish(twist)
        print("   ✅ Sent forward command (linear.x = 0.3)")
        time.sleep(2)
        
        # Stop
        twist = Twist()
        self.cmd_vel_pub.publish(twist)
        print("   ✅ Sent stop command")
        time.sleep(1)
        
        # Rotate
        twist = Twist()
        twist.angular.z = 0.5
        self.cmd_vel_pub.publish(twist)
        print("   ✅ Sent rotation command (angular.z = 0.5)")
        time.sleep(2)
        
        # Stop
        twist = Twist()
        self.cmd_vel_pub.publish(twist)
        print("   ✅ Sent final stop command")
        
    def test_manipulator_control(self):
        """Test arm and lift commands"""
        print("\n🦾 Testing Manipulator Control...")
        
        # Lift
        lift_msg = Float64()
        lift_msg.data = 0.8
        self.lift_pub.publish(lift_msg)
        print("   ✅ Sent lift command (0.8m)")
        time.sleep(3)
        
        # Arm extension
        arm_msg = Float64()
        arm_msg.data = 0.3
        self.arm_pub.publish(arm_msg)
        print("   ✅ Sent arm extension command (0.3m)")
        time.sleep(3)
        
        # Head pan
        head_pan_msg = Float64()
        head_pan_msg.data = 0.5
        self.head_pan_pub.publish(head_pan_msg)
        print("   ✅ Sent head pan command (0.5 rad)")
        time.sleep(2)
        
        # Head tilt
        head_tilt_msg = Float64()
        head_tilt_msg.data = 0.2
        self.head_tilt_pub.publish(head_tilt_msg)
        print("   ✅ Sent head tilt command (0.2 rad)")
        time.sleep(2)
        
    def test_return_to_home(self):
        """Return robot to home position"""
        print("\n🏠 Returning to Home Position...")
        
        # Retract arm
        arm_msg = Float64()
        arm_msg.data = 0.0
        self.arm_pub.publish(arm_msg)
        time.sleep(2)
        
        # Lower lift
        lift_msg = Float64()
        lift_msg.data = 0.2
        self.lift_pub.publish(lift_msg)
        time.sleep(2)
        
        # Center head
        head_pan_msg = Float64()
        head_pan_msg.data = 0.0
        self.head_pan_pub.publish(head_pan_msg)
        
        head_tilt_msg = Float64()
        head_tilt_msg.data = 0.0
        self.head_tilt_pub.publish(head_tilt_msg)
        
        print("   ✅ Robot returned to home position")

def main():
    print("🔗 Testing Web Controller → Robot Connection")
    print("Make sure the SLAM bridge is running with: ./launch_full_simulation.sh")
    print("Press Enter to start test...")
    input()
    
    rclpy.init()
    
    test_node = WebControllerConnectionTest()
    
    try:
        # Allow node to initialize
        rclpy.spin_once(test_node, timeout_sec=1.0)
        
        # Run tests
        test_node.test_base_control()
        time.sleep(2)
        
        test_node.test_manipulator_control()
        time.sleep(2)
        
        test_node.test_return_to_home()
        
        print("\n" + "=" * 50)
        print("🎉 Connection Test Complete!")
        print("If you saw robot movement in MuJoCo and RViz, the connection is working!")
        print("The web controller should work the same way at: http://localhost:8081")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        test_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Test Integrated System
Quick test to verify MuJoCo + RViz + ROS2 integration works
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
import time
import subprocess
import threading
import sys
import os

# Add MuJoCo path
sys.path.append('./stretch_mujoco')

class SystemTester(Node):
    """Test the integrated system"""
    
    def __init__(self):
        super().__init__('system_tester')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lift_pub = self.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
        self.arm_pub = self.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
        self.wrist_yaw_pub = self.create_publisher(Float64, '/stretch_controller/wrist_yaw/command', 10)
        self.gripper_pub = self.create_publisher(Float64, '/stretch_controller/gripper_joint/command', 10)
        
        self.get_logger().info("🧪 System Tester Ready")
    
    def test_arm_control(self):
        """Test arm control through ROS2"""
        print("🧪 Testing arm control...")
        
        # Test lift
        print("  🏗️ Testing lift...")
        lift_msg = Float64()
        lift_msg.data = 0.8
        self.lift_pub.publish(lift_msg)
        time.sleep(3)
        
        # Test arm extension
        print("  🦾 Testing arm extension...")
        arm_msg = Float64()
        arm_msg.data = 0.3
        self.arm_pub.publish(arm_msg)
        time.sleep(3)
        
        # Test wrist
        print("  🔄 Testing wrist yaw...")
        wrist_msg = Float64()
        wrist_msg.data = 1.0
        self.wrist_yaw_pub.publish(wrist_msg)
        time.sleep(3)
        
        # Test gripper
        print("  ✋ Testing gripper...")
        gripper_msg = Float64()
        gripper_msg.data = 0.4
        self.gripper_pub.publish(gripper_msg)
        time.sleep(3)
        
        print("✅ Arm control test completed")
    
    def test_base_control(self):
        """Test base control through ROS2"""
        print("🧪 Testing base control...")
        
        # Move forward
        print("  ➡️ Moving forward...")
        twist = Twist()
        twist.linear.x = 0.2
        self.cmd_vel_pub.publish(twist)
        time.sleep(2)
        
        # Stop
        print("  🛑 Stopping...")
        twist.linear.x = 0.0
        self.cmd_vel_pub.publish(twist)
        time.sleep(1)
        
        # Turn
        print("  🔄 Turning...")
        twist.angular.z = 0.3
        self.cmd_vel_pub.publish(twist)
        time.sleep(2)
        
        # Stop
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        
        print("✅ Base control test completed")

def start_bridge():
    """Start the integrated bridge"""
    print("🚀 Starting integrated bridge...")
    bridge_process = subprocess.Popen(['python3', 'stretch_integrated_controller.py'])
    time.sleep(10)  # Wait for bridge to initialize
    return bridge_process

def main():
    """Main test function"""
    print("="*60)
    print("🧪 INTEGRATED SYSTEM TEST")
    print("="*60)
    print("🎯 This test will:")
    print("  1. Start MuJoCo + ROS2 bridge")
    print("  2. Send robot control commands")
    print("  3. Verify robot moves in MuJoCo")
    print("="*60)
    
    # Start bridge
    bridge_process = start_bridge()
    
    try:
        # Initialize ROS2
        rclpy.init()
        tester = SystemTester()
        
        # Start ROS spinning in background
        spin_thread = threading.Thread(target=lambda: rclpy.spin(tester), daemon=True)
        spin_thread.start()
        
        print("\n🧪 Running automated tests...")
        print("📺 Watch the robot move in MuJoCo window!")
        
        # Wait a bit for everything to initialize
        time.sleep(3)
        
        # Test arm control
        tester.test_arm_control()
        
        # Test base control  
        tester.test_base_control()
        
        print("\n🎉 ALL TESTS COMPLETED!")
        print("💡 If you saw the robot moving in MuJoCo, the integration is working!")
        print("🔧 You can now use the terminal controller or create your own GUI")
        
        # Keep running for a bit to observe
        print("\n⏳ Keeping system running for 10 seconds for observation...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        try:
            tester.destroy_node()
            rclpy.shutdown()
        except:
            pass
            
        try:
            bridge_process.terminate()
            bridge_process.wait(timeout=5)
        except:
            try:
                bridge_process.kill()
            except:
                pass
        
        print("✅ Test completed")

if __name__ == "__main__":
    main()
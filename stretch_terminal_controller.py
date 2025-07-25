#!/usr/bin/env python3
"""
Stretch Terminal Controller
Simple terminal-based interface that publishes ROS2 commands
Works with the integrated bridge to control robot in MuJoCo + RViz
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import threading
import time
import sys

class StretchTerminalController(Node):
    """Terminal-based controller for Stretch robot"""
    
    def __init__(self):
        super().__init__('stretch_terminal_controller')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lift_pub = self.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
        self.arm_pub = self.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
        self.wrist_yaw_pub = self.create_publisher(Float64, '/stretch_controller/wrist_yaw/command', 10)
        self.wrist_pitch_pub = self.create_publisher(Float64, '/stretch_controller/wrist_pitch/command', 10)
        self.gripper_pub = self.create_publisher(Float64, '/stretch_controller/gripper_joint/command', 10)
        
        # Current joint positions
        self.lift_pos = 0.5
        self.arm_pos = 0.1
        self.wrist_yaw_pos = 0.0
        self.wrist_pitch_pos = 0.0
        self.gripper_pos = 0.0
        
        self.get_logger().info("🎮 Terminal Controller Ready!")
        
    def publish_joint_command(self, joint, value):
        """Publish joint command"""
        msg = Float64()
        msg.data = value
        
        if joint == 'lift':
            self.lift_pos = value
            self.lift_pub.publish(msg)
        elif joint == 'arm':
            self.arm_pos = value
            self.arm_pub.publish(msg)
        elif joint == 'wrist_yaw':
            self.wrist_yaw_pos = value
            self.wrist_yaw_pub.publish(msg)
        elif joint == 'wrist_pitch':
            self.wrist_pitch_pos = value
            self.wrist_pitch_pub.publish(msg)
        elif joint == 'gripper':
            self.gripper_pos = value
            self.gripper_pub.publish(msg)
            
        self.get_logger().info(f"🔧 {joint}: {value:.3f}")
    
    def publish_base_command(self, linear, angular):
        """Publish base velocity command"""
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.cmd_vel_pub.publish(msg)
        self.get_logger().info(f"🚗 Base: linear={linear:.2f}, angular={angular:.2f}")
    
    def print_status(self):
        """Print current status"""
        print("\n" + "="*50)
        print("🤖 STRETCH ROBOT STATUS")
        print("="*50)
        print(f"🏗️  Lift:        {self.lift_pos:.3f} m")
        print(f"🦾 Arm:         {self.arm_pos:.3f} m") 
        print(f"🔄 Wrist Yaw:   {self.wrist_yaw_pos:.3f} rad")
        print(f"↕️  Wrist Pitch: {self.wrist_pitch_pos:.3f} rad")
        print(f"✋ Gripper:     {self.gripper_pos:.3f} m")
        print("="*50)

def print_menu():
    """Print control menu"""
    print("\n" + "="*60)
    print("🎮 STRETCH ROBOT TERMINAL CONTROLLER")
    print("="*60)
    print("📺 Watch robot move in MuJoCo window and RViz!")
    print("\nCOMMANDS:")
    print("  Base Movement:")
    print("    w - Forward    s - Backward")  
    print("    a - Turn Left  d - Turn Right")
    print("    x - Stop Base")
    print("\n  Arm Control:")
    print("    1 - Lift Up    2 - Lift Down")
    print("    3 - Arm Out    4 - Arm In")
    print("    5 - Wrist Yaw+ 6 - Wrist Yaw-")
    print("    7 - Wrist Up   8 - Wrist Down")
    print("    9 - Gripper Open  0 - Gripper Close")
    print("\n  Presets:")
    print("    h - Home Position")
    print("    t - Stow Position")
    print("\n  Other:")
    print("    p - Print Status")
    print("    m - Show Menu")
    print("    q - Quit")
    print("="*60)

def main():
    """Main function"""
    rclpy.init()
    
    controller = StretchTerminalController()
    
    # Start ROS spinning in background thread
    spin_thread = threading.Thread(target=lambda: rclpy.spin(controller), daemon=True)
    spin_thread.start()
    
    print_menu()
    
    try:
        while True:
            command = input("\n🤖 Enter command: ").strip().lower()
            
            if command == 'q':
                break
            elif command == 'm':
                print_menu()
            elif command == 'p':
                controller.print_status()
            
            # Base movement
            elif command == 'w':
                controller.publish_base_command(0.2, 0.0)
            elif command == 's':
                controller.publish_base_command(-0.2, 0.0)
            elif command == 'a':
                controller.publish_base_command(0.0, 0.3)
            elif command == 'd':
                controller.publish_base_command(0.0, -0.3)
            elif command == 'x':
                controller.publish_base_command(0.0, 0.0)
            
            # Arm control
            elif command == '1':  # Lift up
                new_pos = min(1.1, controller.lift_pos + 0.1)
                controller.publish_joint_command('lift', new_pos)
            elif command == '2':  # Lift down
                new_pos = max(0.0, controller.lift_pos - 0.1)
                controller.publish_joint_command('lift', new_pos)
            elif command == '3':  # Arm out
                new_pos = min(0.5, controller.arm_pos + 0.05)
                controller.publish_joint_command('arm', new_pos)
            elif command == '4':  # Arm in
                new_pos = max(0.0, controller.arm_pos - 0.05)
                controller.publish_joint_command('arm', new_pos)
            elif command == '5':  # Wrist yaw +
                new_pos = min(1.57, controller.wrist_yaw_pos + 0.2)
                controller.publish_joint_command('wrist_yaw', new_pos)
            elif command == '6':  # Wrist yaw -
                new_pos = max(-1.57, controller.wrist_yaw_pos - 0.2)
                controller.publish_joint_command('wrist_yaw', new_pos)
            elif command == '7':  # Wrist up
                new_pos = min(0.5, controller.wrist_pitch_pos + 0.2)
                controller.publish_joint_command('wrist_pitch', new_pos)
            elif command == '8':  # Wrist down
                new_pos = max(-0.5, controller.wrist_pitch_pos - 0.2)
                controller.publish_joint_command('wrist_pitch', new_pos)
            elif command == '9':  # Gripper open
                new_pos = min(0.6, controller.gripper_pos + 0.1)
                controller.publish_joint_command('gripper', new_pos)
            elif command == '0':  # Gripper close
                new_pos = max(-0.1, controller.gripper_pos - 0.1)
                controller.publish_joint_command('gripper', new_pos)
            
            # Presets
            elif command == 'h':  # Home
                print("🏠 Moving to home position...")
                controller.publish_joint_command('lift', 0.9)
                time.sleep(0.1)
                controller.publish_joint_command('arm', 0.0)
                time.sleep(0.1)
                controller.publish_joint_command('wrist_yaw', 0.0)
                time.sleep(0.1)
                controller.publish_joint_command('wrist_pitch', 0.0)
                time.sleep(0.1)
                controller.publish_joint_command('gripper', 0.0)
            elif command == 't':  # Stow
                print("📦 Moving to stow position...")
                controller.publish_joint_command('lift', 0.2)
                time.sleep(0.1)
                controller.publish_joint_command('arm', 0.0)
                time.sleep(0.1)
                controller.publish_joint_command('wrist_yaw', 0.0)
                time.sleep(0.1)
                controller.publish_joint_command('wrist_pitch', -0.3)
                time.sleep(0.1)
                controller.publish_joint_command('gripper', 0.0)
            
            else:
                print("❓ Unknown command. Type 'm' for menu.")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping controller...")
    
    finally:
        controller.destroy_node()
        rclpy.shutdown()
        print("✅ Terminal controller stopped")

if __name__ == "__main__":
    main()
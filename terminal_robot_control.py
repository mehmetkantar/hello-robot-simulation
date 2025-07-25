#!/usr/bin/env python3
"""
Terminal-based Robot Controller
Simple keyboard control for robot base and arm
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
import sys
import tty
import termios
import threading
import time

class TerminalRobotController(Node):
    def __init__(self):
        super().__init__('terminal_robot_controller')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.joint_pub = self.create_publisher(JointState, '/stretch/joint_commands', 10)
        
        # Robot state
        self.linear_speed = 0.3
        self.angular_speed = 0.5
        self.arm_speed = 0.1
        
        # Current joint positions (will be updated by robot feedback)
        self.joint_positions = {
            'joint_lift': 0.5,
            'joint_arm_l0': 0.0,
            'wrist_extension': 0.0,
            'joint_wrist_yaw': 0.0,
            'joint_gripper_finger_left': 0.0
        }
        
        print("🤖 Terminal Robot Controller Ready!")
        self.print_controls()
        
    def print_controls(self):
        print("\n" + "="*50)
        print("🎮 ROBOT CONTROLS:")
        print("="*50)
        print("BASE MOVEMENT:")
        print("  w/s    - Forward/Backward")
        print("  a/d    - Rotate Left/Right")
        print("  q/e    - Strafe Left/Right")
        print()
        print("ARM CONTROL:")
        print("  i/k    - Lift Up/Down")
        print("  j/l    - Arm Extend/Retract")
        print("  u/o    - Wrist Rotate Left/Right")
        print("  n/m    - Gripper Open/Close")
        print()
        print("SPEED CONTROL:")
        print("  +/-    - Increase/Decrease speed")
        print()
        print("OTHER:")
        print("  SPACE  - Emergency Stop")
        print("  h      - Show this help")
        print("  x      - Exit")
        print("="*50)
        print(f"Current speeds: Linear={self.linear_speed:.1f} Angular={self.angular_speed:.1f}")
        print("Press keys to control robot...")
    
    def move_base(self, linear_x=0.0, linear_y=0.0, angular_z=0.0):
        """Send base movement command"""
        twist = Twist()
        twist.linear.x = linear_x * self.linear_speed
        twist.linear.y = linear_y * self.linear_speed
        twist.angular.z = angular_z * self.angular_speed
        
        self.cmd_vel_pub.publish(twist)
        
        if linear_x != 0 or linear_y != 0 or angular_z != 0:
            self.get_logger().info(f'Base: linear=({linear_x:.1f}, {linear_y:.1f}), angular={angular_z:.1f}')
    
    def move_joint(self, joint_name, delta):
        """Move a specific joint by delta amount"""
        if joint_name in self.joint_positions:
            self.joint_positions[joint_name] += delta * self.arm_speed
            
            # Apply limits
            limits = {
                'joint_lift': (0.0, 1.1),
                'joint_arm_l0': (0.0, 0.5),
                'wrist_extension': (0.0, 0.5),
                'joint_wrist_yaw': (-1.57, 1.57),
                'joint_gripper_finger_left': (-0.6, 0.6)
            }
            
            if joint_name in limits:
                min_val, max_val = limits[joint_name]
                self.joint_positions[joint_name] = max(min_val, min(max_val, self.joint_positions[joint_name]))
            
            # Publish joint command
            joint_msg = JointState()
            joint_msg.header.stamp = self.get_clock().now().to_msg()
            joint_msg.name = list(self.joint_positions.keys())
            joint_msg.position = list(self.joint_positions.values())
            
            self.joint_pub.publish(joint_msg)
            
            self.get_logger().info(f'Joint {joint_name}: {self.joint_positions[joint_name]:.2f}')
    
    def emergency_stop(self):
        """Stop all movement immediately"""
        self.move_base(0, 0, 0)
        print("🛑 EMERGENCY STOP!")
    
    def adjust_speed(self, factor):
        """Adjust movement speeds"""
        self.linear_speed = max(0.1, min(1.0, self.linear_speed * factor))
        self.angular_speed = max(0.1, min(2.0, self.angular_speed * factor))
        self.arm_speed = max(0.05, min(0.5, self.arm_speed * factor))
        print(f"⚡ Speeds: Linear={self.linear_speed:.1f} Angular={self.angular_speed:.1f} Arm={self.arm_speed:.2f}")

def get_key():
    """Get single keypress without Enter"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.cbreak(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def main():
    rclpy.init()
    
    controller = TerminalRobotController()
    
    # Start ROS spinning in background
    def spin_ros():
        rclpy.spin(controller)
    
    ros_thread = threading.Thread(target=spin_ros, daemon=True)
    ros_thread.start()
    
    try:
        while True:
            key = get_key().lower()
            
            # Base movement
            if key == 'w':
                controller.move_base(linear_x=1.0)
            elif key == 's':
                controller.move_base(linear_x=-1.0)
            elif key == 'a':
                controller.move_base(angular_z=1.0)
            elif key == 'd':
                controller.move_base(angular_z=-1.0)
            elif key == 'q':
                controller.move_base(linear_y=1.0)
            elif key == 'e':
                controller.move_base(linear_y=-1.0)
            
            # Arm movement
            elif key == 'i':
                controller.move_joint('joint_lift', 1.0)
            elif key == 'k':
                controller.move_joint('joint_lift', -1.0)
            elif key == 'j':
                controller.move_joint('joint_arm_l0', -1.0)
            elif key == 'l':
                controller.move_joint('joint_arm_l0', 1.0)
            elif key == 'u':
                controller.move_joint('joint_wrist_yaw', 1.0)
            elif key == 'o':
                controller.move_joint('joint_wrist_yaw', -1.0)
            elif key == 'n':
                controller.move_joint('joint_gripper_finger_left', 1.0)
            elif key == 'm':
                controller.move_joint('joint_gripper_finger_left', -1.0)
            
            # Speed control
            elif key == '+' or key == '=':
                controller.adjust_speed(1.2)
            elif key == '-':
                controller.adjust_speed(0.8)
            
            # Control commands
            elif key == ' ':
                controller.emergency_stop()
            elif key == 'h':
                controller.print_controls()
            elif key == 'x':
                print("👋 Exiting robot controller...")
                break
            elif key == '\x03':  # Ctrl+C
                break
                
    except KeyboardInterrupt:
        pass
    
    print("\n🛑 Shutting down robot controller...")
    controller.emergency_stop()
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
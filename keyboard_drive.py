#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import time
import math
import sys
import tty
import termios
import select

class KeyboardDrive(Node):
    def __init__(self):
        super().__init__('keyboard_drive')
        
        # Publishers
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Robot state
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        self.last_time = time.time()
        
        # Movement
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        self.speed = 0.5  # Default speed
        
        # Joints
        self.joints = {
            'joint_lift': 0.0,
            'joint_arm_l0': 0.0,
            'joint_arm_l1': 0.0,
            'joint_arm_l2': 0.0,
            'joint_arm_l3': 0.0,
            'joint_wrist_yaw': 0.0,
            'joint_wrist_pitch': 0.0,
            'joint_wrist_roll': 0.0,
            'joint_gripper_finger_left': 0.0,
            'joint_gripper_finger_right': 0.0,
            'joint_head_pan': 0.0,
            'joint_head_tilt': 0.0,
            'joint_left_wheel': 0.0,
            'joint_right_wheel': 0.0
        }
        
        # Timer
        self.timer = self.create_timer(0.1, self.update_robot)
        
        print("✅ Keyboard drive ready")
        self.print_instructions()

    def print_instructions(self):
        print("\n🎮 Keyboard Controls:")
        print("===================")
        print("w/s - Forward/Backward")
        print("a/d - Turn Left/Right")
        print("x   - Stop")
        print("r   - Reset position")
        print("+/- - Increase/Decrease speed")
        print("q   - Quit")
        print("\nPress keys to drive the robot!")
        print(f"Current speed: {self.speed:.1f}")

    def get_key(self):
        """Get single keypress"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def process_key(self, key):
        """Process keyboard input"""
        if key == 'w':
            self.linear_speed = self.speed
            self.angular_speed = 0.0
            self.is_moving = True
            print(f"⬆️  Forward at {self.speed:.1f}")
            
        elif key == 's':
            self.linear_speed = -self.speed
            self.angular_speed = 0.0
            self.is_moving = True
            print(f"⬇️  Backward at {self.speed:.1f}")
            
        elif key == 'a':
            self.linear_speed = 0.0
            self.angular_speed = self.speed
            self.is_moving = True
            print(f"⬅️  Left at {self.speed:.1f}")
            
        elif key == 'd':
            self.linear_speed = 0.0
            self.angular_speed = -self.speed
            self.is_moving = True
            print(f"➡️  Right at {self.speed:.1f}")
            
        elif key == 'x':
            self.linear_speed = 0.0
            self.angular_speed = 0.0
            self.is_moving = False
            print("🛑 Stopped")
            
        elif key == 'r':
            self.robot_x = 0.0
            self.robot_y = 0.0
            self.robot_theta = 0.0
            self.joints['joint_left_wheel'] = 0.0
            self.joints['joint_right_wheel'] = 0.0
            self.linear_speed = 0.0
            self.angular_speed = 0.0
            self.is_moving = False
            print("📍 Reset position")
            
        elif key == '+' or key == '=':
            self.speed = min(1.0, self.speed + 0.1)
            print(f"⚡ Speed: {self.speed:.1f}")
            
        elif key == '-':
            self.speed = max(0.1, self.speed - 0.1)
            print(f"⚡ Speed: {self.speed:.1f}")
            
        elif key == 'q':
            print("👋 Goodbye!")
            return False
            
        else:
            print(f"❓ Unknown key: {key}")
            
        return True

    def update_robot(self):
        """Update robot state"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        if self.is_moving:
            self.robot_x += self.linear_speed * math.cos(self.robot_theta) * dt
            self.robot_y += self.linear_speed * math.sin(self.robot_theta) * dt
            self.robot_theta += self.angular_speed * dt
            
            # Update wheels
            left_speed = self.linear_speed - (self.angular_speed * 0.33 / 2.0)
            right_speed = self.linear_speed + (self.angular_speed * 0.33 / 2.0)
            
            self.joints['joint_left_wheel'] += (left_speed / 0.05) * dt
            self.joints['joint_right_wheel'] += (right_speed / 0.05) * dt
        
        self.publish_transforms()
        self.publish_joint_states()

    def publish_transforms(self):
        """Publish robot transform"""
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = self.robot_x
        t.transform.translation.y = self.robot_y
        t.transform.translation.z = 0.0
        
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(self.robot_theta / 2.0)
        t.transform.rotation.w = math.cos(self.robot_theta / 2.0)
        
        self.tf_broadcaster.sendTransform(t)

    def publish_joint_states(self):
        """Publish joint states"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        
        msg.name = list(self.joints.keys())
        msg.position = list(self.joints.values())
        msg.velocity = [0.0] * len(msg.name)
        msg.effort = [0.0] * len(msg.name)
        
        self.joint_pub.publish(msg)

    def run(self):
        """Main control loop"""
        try:
            while True:
                # Check for keyboard input
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = self.get_key()
                    if not self.process_key(key):
                        break
                        
                # Print position occasionally
                if int(time.time()) % 5 == 0 and time.time() - int(time.time()) < 0.1:
                    print(f"📍 Position: ({self.robot_x:.1f}, {self.robot_y:.1f}) θ={math.degrees(self.robot_theta):.0f}°")
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

def main():
    rclpy.init()
    
    try:
        print("🚀 Starting keyboard drive...")
        controller = KeyboardDrive()
        controller.run()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
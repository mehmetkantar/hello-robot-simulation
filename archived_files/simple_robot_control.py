#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped, Twist
from tf2_ros import TransformBroadcaster
import time
import math
import sys
import select
import termios
import tty
import threading

class SimpleStretchControl(Node):
    def __init__(self):
        super().__init__('simple_stretch_control')
        
        # Publishers
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Robot state
        self.robot_x = -5.0  # Start at safe location
        self.robot_y = 4.0
        self.robot_theta = 0.0
        self.last_time = time.time()
        
        # Wheel parameters
        self.wheel_base = 0.4  # Distance between wheels (meters)
        self.wheel_radius = 0.05  # Wheel radius (meters)
        
        # Simplified joint definitions
        self.joints = {
            'lift': {'min': 0.0, 'max': 0.5, 'current': 0.0, 'step': 0.05},
            'arm_extension': {'min': 0.0, 'max': 0.3, 'current': 0.0, 'step': 0.02},
            'gripper': {'min': -0.1, 'max': 0.1, 'current': 0.0, 'step': 0.01},
        }
        
        # Wheel joints (tracked separately for odometry)
        self.wheel_positions = {
            'left_wheel': 0.0,
            'right_wheel': 0.0
        }
        
        # Movement state
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.max_linear_speed = 0.5
        self.max_angular_speed = 1.0
        
        # Timer for publishing
        self.timer = self.create_timer(0.1, self.update_robot)  # 10Hz
        
        # Keyboard settings
        self.old_settings = None
        self.setup_keyboard()
        
        print("🤖 Simple Stretch Control Started")
        print(f"📍 Starting position: ({self.robot_x}, {self.robot_y})")
        print("\n🎮 Controls:")
        print("  WASD - Drive (W=forward, S=backward, A=left, D=right)")
        print("  QE   - Lift (Q=up, E=down)")
        print("  RF   - Arm (R=extend, F=retract)")
        print("  TG   - Gripper (T=open, G=close)")
        print("  H    - Home position")
        print("  P    - Reset position")
        print("  X    - Stop all movement")
        print("  ESC  - Exit")
        print("\n✅ Ready! Press keys to control the robot...")
    
    def setup_keyboard(self):
        """Setup keyboard for non-blocking input"""
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        except:
            print("⚠️ Could not setup keyboard input")
    
    def restore_keyboard(self):
        """Restore keyboard settings"""
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def get_key(self):
        """Get a single keypress"""
        if select.select([sys.stdin], [], [], 0.01) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return None
    
    def handle_keyboard(self):
        """Handle keyboard input"""
        key = self.get_key()
        if key is None:
            return True
        
        # Convert to lowercase for consistency
        key = key.lower()
        
        # Drive controls
        if key == 'w':
            self.linear_speed = self.max_linear_speed
            self.angular_speed = 0.0
            print("⬆️ Forward")
        elif key == 's':
            self.linear_speed = -self.max_linear_speed
            self.angular_speed = 0.0
            print("⬇️ Backward")
        elif key == 'a':
            self.linear_speed = 0.0
            self.angular_speed = self.max_angular_speed
            print("⬅️ Left")
        elif key == 'd':
            self.linear_speed = 0.0
            self.angular_speed = -self.max_angular_speed
            print("➡️ Right")
        elif key == 'x':
            self.linear_speed = 0.0
            self.angular_speed = 0.0
            print("🛑 Stop")
        
        # Joint controls
        elif key == 'q':
            self.adjust_joint('lift', 1)
        elif key == 'e':
            self.adjust_joint('lift', -1)
        elif key == 'r':
            self.adjust_joint('arm_extension', 1)
        elif key == 'f':
            self.adjust_joint('arm_extension', -1)
        elif key == 't':
            self.adjust_joint('gripper', 1)
        elif key == 'g':
            self.adjust_joint('gripper', -1)
        
        # Special commands
        elif key == 'h':
            self.go_home()
        elif key == 'p':
            self.reset_position()
        elif key == '\x1b':  # ESC key
            print("\n👋 Exiting...")
            return False
        
        return True
    
    def adjust_joint(self, joint_name, direction):
        """Adjust joint position"""
        if joint_name not in self.joints:
            return
        
        joint = self.joints[joint_name]
        new_pos = joint['current'] + (direction * joint['step'])
        new_pos = max(joint['min'], min(joint['max'], new_pos))
        
        if new_pos != joint['current']:
            joint['current'] = new_pos
            action = "⬆️" if direction > 0 else "⬇️"
            print(f"{action} {joint_name.replace('_', ' ').title()}: {new_pos:.3f}")
    
    def go_home(self):
        """Reset all joints to home position"""
        for joint_name in self.joints:
            self.joints[joint_name]['current'] = 0.0
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        print("🏠 Home position")
    
    def reset_position(self):
        """Reset robot position to starting location"""
        self.robot_x = -5.0
        self.robot_y = 4.0
        self.robot_theta = 0.0
        self.wheel_positions['left_wheel'] = 0.0
        self.wheel_positions['right_wheel'] = 0.0
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        print("📍 Position reset to start")
    
    def update_robot(self):
        """Update robot state and publish transforms"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Update robot position based on movement
        if abs(self.linear_speed) > 0.01 or abs(self.angular_speed) > 0.01:
            # Update robot pose
            self.robot_x += self.linear_speed * math.cos(self.robot_theta) * dt
            self.robot_y += self.linear_speed * math.sin(self.robot_theta) * dt
            self.robot_theta += self.angular_speed * dt
            
            # Normalize angle
            self.robot_theta = math.atan2(math.sin(self.robot_theta), math.cos(self.robot_theta))
            
            # Update wheel positions for visual feedback
            left_wheel_speed = self.linear_speed - (self.angular_speed * self.wheel_base / 2.0)
            right_wheel_speed = self.linear_speed + (self.angular_speed * self.wheel_base / 2.0)
            
            self.wheel_positions['left_wheel'] += (left_wheel_speed / self.wheel_radius) * dt
            self.wheel_positions['right_wheel'] += (right_wheel_speed / self.wheel_radius) * dt
        
        # Publish transforms and joint states
        self.publish_transforms()
        self.publish_joint_states()
        self.publish_cmd_vel()
    
    def publish_transforms(self):
        """Publish the robot base transform"""
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = self.robot_x
        t.transform.translation.y = self.robot_y
        t.transform.translation.z = 0.0
        
        # Convert angle to quaternion
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
        
        # Add simplified joints
        joint_names = list(self.joints.keys())
        joint_positions = [self.joints[name]['current'] for name in joint_names]
        
        # Add wheel joints
        joint_names.extend(['left_wheel', 'right_wheel'])
        joint_positions.extend([
            self.wheel_positions['left_wheel'],
            self.wheel_positions['right_wheel']
        ])
        
        msg.name = joint_names
        msg.position = joint_positions
        msg.velocity = [0.0] * len(joint_names)
        msg.effort = [0.0] * len(joint_names)
        
        self.joint_pub.publish(msg)
    
    def publish_cmd_vel(self):
        """Publish velocity commands"""
        msg = Twist()
        msg.linear.x = self.linear_speed
        msg.angular.z = self.angular_speed
        self.cmd_vel_pub.publish(msg)

def main():
    # Initialize ROS2
    try:
        rclpy.init()
    except:
        print("❌ Failed to initialize ROS2. Make sure ROS2 is properly setup.")
        return
    
    controller = None
    try:
        controller = SimpleStretchControl()
        
        # Run keyboard handling in main thread
        print("\n🎮 Starting keyboard control...")
        
        # Main loop combining keyboard and ROS2
        while True:
            # Handle keyboard input
            if not controller.handle_keyboard():
                break
            
            # Spin ROS2 once to handle messages
            try:
                rclpy.spin_once(controller, timeout_sec=0.01)
            except:
                print("⚠️ ROS2 spin error")
            
            time.sleep(0.01)  # Small delay
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if controller:
            try:
                controller.restore_keyboard()
                controller.destroy_node()
            except:
                pass
        try:
            rclpy.shutdown()
        except:
            pass

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import tkinter as tk
import threading
import time
import math
import sys

class MinimalRobotControl(Node):
    def __init__(self):
        super().__init__('minimal_robot_control')
        
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
        
        # Joints (minimal)
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
        
        print("✅ Minimal robot control ready")

    def setup_minimal_gui(self):
        """Ultra-simple GUI"""
        self.root = tk.Tk()
        self.root.title("Robot Control")
        self.root.geometry("300x400")
        self.root.configure(bg='gray')
        
        # Title
        tk.Label(self.root, text="Robot Control", font=('Arial', 14), bg='gray').pack(pady=10)
        
        # Status
        self.status = tk.Label(self.root, text="Ready", bg='gray')
        self.status.pack(pady=5)
        
        # Drive buttons
        tk.Button(self.root, text="Forward", command=self.forward, width=10).pack(pady=2)
        tk.Button(self.root, text="Left", command=self.left, width=10).pack(pady=2)
        tk.Button(self.root, text="Right", command=self.right, width=10).pack(pady=2)
        tk.Button(self.root, text="Backward", command=self.backward, width=10).pack(pady=2)
        tk.Button(self.root, text="STOP", command=self.stop, width=10, bg='red').pack(pady=5)
        
        # Reset
        tk.Button(self.root, text="Reset", command=self.reset, width=10).pack(pady=2)
        
        print("✅ Minimal GUI ready")

    def forward(self):
        self.linear_speed = 0.3
        self.angular_speed = 0.0
        self.is_moving = True
        self.status.config(text="Forward")

    def backward(self):
        self.linear_speed = -0.3
        self.angular_speed = 0.0
        self.is_moving = True
        self.status.config(text="Backward")

    def left(self):
        self.linear_speed = 0.0
        self.angular_speed = 1.0
        self.is_moving = True
        self.status.config(text="Left")

    def right(self):
        self.linear_speed = 0.0
        self.angular_speed = -1.0
        self.is_moving = True
        self.status.config(text="Right")

    def stop(self):
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        self.status.config(text="Stopped")

    def reset(self):
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        self.stop()
        self.status.config(text="Reset")

    def update_robot(self):
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
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        
        msg.name = list(self.joints.keys())
        msg.position = list(self.joints.values())
        msg.velocity = [0.0] * len(msg.name)
        msg.effort = [0.0] * len(msg.name)
        
        self.joint_pub.publish(msg)

    def run(self):
        if self.root:
            self.root.mainloop()

def main():
    # Initialize ROS2 FIRST
    rclpy.init()
    
    try:
        print("🚀 Starting minimal control...")
        
        # Create controller
        controller = MinimalRobotControl()
        
        # Setup GUI after ROS2 is ready
        controller.setup_minimal_gui()
        
        # Start ROS2 spinning in background
        def spin_ros():
            try:
                rclpy.spin(controller)
            except:
                pass
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        # Give ROS2 time to start
        time.sleep(0.5)
        
        print("🎮 Starting GUI...")
        controller.run()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            controller.destroy_node()
            rclpy.shutdown()
        except:
            pass

if __name__ == '__main__':
    main()
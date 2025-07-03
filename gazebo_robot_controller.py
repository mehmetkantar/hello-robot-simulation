#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import tkinter as tk
from tkinter import ttk
import threading
import time

class GazeboStretchController(Node):
    def __init__(self):
        super().__init__('gazebo_stretch_controller')
        
        # Publishers for movement and joints
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lift_pub = self.create_publisher(Float64, '/joint_lift/command', 10)
        self.arm_pub = self.create_publisher(Float64, '/joint_arm/command', 10)
        self.gripper_pub = self.create_publisher(Float64, '/joint_gripper/command', 10)
        self.head_pub = self.create_publisher(Float64, '/joint_head/command', 10)
        
        # Current joint positions
        self.joint_positions = {
            'lift': 0.0,
            'arm': 0.0,
            'gripper': 0.0,
            'head': 0.0
        }
        
        # Movement state
        self.moving = False
        self.current_twist = Twist()
        
        self.setup_gui()
        
        # Timer for continuous movement
        self.timer = self.create_timer(0.1, self.publish_commands)
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🤖 Gazebo Stretch Robot Controller")
        self.root.geometry("700x600")
        self.root.configure(bg='#2b2b2b')
        
        # Title
        title = tk.Label(self.root, text="🤖 Stretch Robot - Gazebo Controller", 
                        font=('Arial', 16, 'bold'), fg='white', bg='#2b2b2b')
        title.pack(pady=10)
        
        # Movement controls
        movement_frame = tk.Frame(self.root, bg='#2b2b2b', relief='groove', bd=2)
        movement_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(movement_frame, text="🚗 Robot Movement (Real Physics!)", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2b2b2b').pack(pady=5)
        
        # Movement buttons
        move_grid = tk.Frame(movement_frame, bg='#2b2b2b')
        move_grid.pack(pady=5)
        
        tk.Button(move_grid, text="⬆️\nForward", command=self.move_forward,
                 bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'), 
                 width=10, height=3).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(move_grid, text="⬅️\nLeft", command=self.turn_left,
                 bg='#2196F3', fg='white', font=('Arial', 12, 'bold'), 
                 width=10, height=3).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(move_grid, text="⏹️\nSTOP", command=self.stop_robot,
                 bg='#F44336', fg='white', font=('Arial', 12, 'bold'), 
                 width=10, height=3).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(move_grid, text="➡️\nRight", command=self.turn_right,
                 bg='#2196F3', fg='white', font=('Arial', 12, 'bold'), 
                 width=10, height=3).grid(row=1, column=2, padx=5, pady=5)
        
        tk.Button(move_grid, text="⬇️\nBackward", command=self.move_backward,
                 bg='#FF9800', fg='white', font=('Arial', 12, 'bold'), 
                 width=10, height=3).grid(row=2, column=1, padx=5, pady=5)
        
        # Speed controls
        speed_frame = tk.Frame(movement_frame, bg='#2b2b2b')
        speed_frame.pack(pady=10)
        
        tk.Label(speed_frame, text="Linear Speed:", font=('Arial', 10), 
                fg='white', bg='#2b2b2b').grid(row=0, column=0, padx=5)
        self.linear_speed = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1, 
                                   orient=tk.HORIZONTAL, length=150, bg='#2b2b2b', fg='white')
        self.linear_speed.set(0.5)
        self.linear_speed.grid(row=0, column=1, padx=5)
        
        tk.Label(speed_frame, text="Angular Speed:", font=('Arial', 10), 
                fg='white', bg='#2b2b2b').grid(row=1, column=0, padx=5)
        self.angular_speed = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1, 
                                    orient=tk.HORIZONTAL, length=150, bg='#2b2b2b', fg='white')
        self.angular_speed.set(1.0)
        self.angular_speed.grid(row=1, column=1, padx=5)
        
        # Joint controls
        joint_frame = tk.Frame(self.root, bg='#2b2b2b', relief='groove', bd=2)
        joint_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        tk.Label(joint_frame, text="🦾 Joint Controls", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2b2b2b').pack(pady=5)
        
        # Create joint sliders
        self.sliders = {}
        
        joints = [
            ('lift', 'Lift (Up/Down)', 0.0, 1.0, self.update_lift),
            ('arm', 'Arm (Extend)', 0.0, 0.5, self.update_arm),
            ('gripper', 'Gripper (Rotate)', -1.57, 1.57, self.update_gripper),
            ('head', 'Head (Pan)', -1.57, 1.57, self.update_head)
        ]
        
        for joint_name, label, min_val, max_val, callback in joints:
            frame = tk.Frame(joint_frame, bg='#2b2b2b')
            frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(frame, text=label, font=('Arial', 11, 'bold'), 
                    fg='white', bg='#2b2b2b', width=15, anchor='w').pack(side=tk.LEFT)
            
            slider = tk.Scale(frame, from_=min_val, to=max_val, resolution=0.01,
                            orient=tk.HORIZONTAL, length=300, bg='#2b2b2b', fg='white',
                            command=callback)
            slider.pack(side=tk.LEFT, padx=10)
            slider.set(0.0)
            
            self.sliders[joint_name] = slider
        
        # Preset buttons
        preset_frame = tk.Frame(self.root, bg='#2b2b2b')
        preset_frame.pack(pady=10)
        
        tk.Button(preset_frame, text="🏠 Home", command=self.home_position,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(preset_frame, text="🥤 Reach Table", command=self.reach_table,
                 bg='#E91E63', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(preset_frame, text="📏 Tall", command=self.tall_position,
                 bg='#9C27B0', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready - Robot will move in Gazebo!",
                                   fg='#4CAF50', bg='#2b2b2b', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=10)
        
    # Movement functions
    def move_forward(self):
        self.moving = True
        self.current_twist.linear.x = self.linear_speed.get()
        self.current_twist.angular.z = 0.0
        self.status_label.config(text=f"⬆️ Moving forward at {self.linear_speed.get():.1f} m/s")
    
    def move_backward(self):
        self.moving = True
        self.current_twist.linear.x = -self.linear_speed.get()
        self.current_twist.angular.z = 0.0
        self.status_label.config(text=f"⬇️ Moving backward at {self.linear_speed.get():.1f} m/s")
    
    def turn_left(self):
        self.moving = True
        self.current_twist.linear.x = 0.0
        self.current_twist.angular.z = self.angular_speed.get()
        self.status_label.config(text=f"⬅️ Turning left at {self.angular_speed.get():.1f} rad/s")
    
    def turn_right(self):
        self.moving = True
        self.current_twist.linear.x = 0.0
        self.current_twist.angular.z = -self.angular_speed.get()
        self.status_label.config(text=f"➡️ Turning right at {self.angular_speed.get():.1f} rad/s")
    
    def stop_robot(self):
        self.moving = False
        self.current_twist.linear.x = 0.0
        self.current_twist.angular.z = 0.0
        self.status_label.config(text="⏹️ Robot stopped")
    
    # Joint update functions
    def update_lift(self, value):
        self.joint_positions['lift'] = float(value)
        self.status_label.config(text=f"🔧 Lift: {float(value):.2f}m")
    
    def update_arm(self, value):
        self.joint_positions['arm'] = float(value)
        self.status_label.config(text=f"🔧 Arm: {float(value):.2f}m")
    
    def update_gripper(self, value):
        self.joint_positions['gripper'] = float(value)
        self.status_label.config(text=f"🔧 Gripper: {float(value):.2f}rad")
    
    def update_head(self, value):
        self.joint_positions['head'] = float(value)
        self.status_label.config(text=f"🔧 Head: {float(value):.2f}rad")
    
    # Preset positions
    def home_position(self):
        positions = {'lift': 0.0, 'arm': 0.0, 'gripper': 0.0, 'head': 0.0}
        self.set_joint_positions(positions)
        self.status_label.config(text="🏠 Moved to home position")
    
    def reach_table(self):
        positions = {'lift': 0.7, 'arm': 0.3, 'gripper': 0.0, 'head': 0.5}
        self.set_joint_positions(positions)
        self.status_label.config(text="🥤 Positioned to reach table")
    
    def tall_position(self):
        positions = {'lift': 1.0, 'arm': 0.1, 'gripper': 0.0, 'head': 0.0}
        self.set_joint_positions(positions)
        self.status_label.config(text="📏 Extended to tall position")
    
    def set_joint_positions(self, positions):
        for joint, position in positions.items():
            self.joint_positions[joint] = position
            if joint in self.sliders:
                self.sliders[joint].set(position)
    
    def publish_commands(self):
        # Publish movement commands
        self.cmd_vel_pub.publish(self.current_twist)
        
        # Publish joint commands
        lift_msg = Float64()
        lift_msg.data = self.joint_positions['lift']
        self.lift_pub.publish(lift_msg)
        
        arm_msg = Float64()
        arm_msg.data = self.joint_positions['arm']
        self.arm_pub.publish(arm_msg)
        
        gripper_msg = Float64()
        gripper_msg.data = self.joint_positions['gripper']
        self.gripper_pub.publish(gripper_msg)
        
        head_msg = Float64()
        head_msg.data = self.joint_positions['head']
        self.head_pub.publish(head_msg)
    
    def run_gui(self):
        self.root.mainloop()

def main():
    rclpy.init()
    
    controller = GazeboStretchController()
    
    # Run ROS2 in a separate thread
    def spin_ros():
        try:
            rclpy.spin(controller)
        except:
            pass
    
    ros_thread = threading.Thread(target=spin_ros, daemon=True)
    ros_thread.start()
    
    # Run GUI in main thread
    try:
        controller.run_gui()
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
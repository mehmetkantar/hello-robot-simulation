#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
import tkinter as tk
from tkinter import ttk
import threading
import time

class EnhancedStretchController(Node):
    def __init__(self):
        super().__init__('enhanced_stretch_controller')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Subscriber for joint feedback
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_feedback_callback, 10)
        
        # Exact Stretch robot joints (same as official URDF)
        self.joints = {
            'joint_lift': {'min': 0.0, 'max': 1.1, 'current': 0.0},
            'joint_arm_l0': {'min': 0.0, 'max': 0.13, 'current': 0.0},
            'joint_arm_l1': {'min': 0.0, 'max': 0.13, 'current': 0.0},
            'joint_arm_l2': {'min': 0.0, 'max': 0.13, 'current': 0.0},
            'joint_arm_l3': {'min': 0.0, 'max': 0.13, 'current': 0.0},
            'joint_wrist_yaw': {'min': -1.57, 'max': 1.57, 'current': 0.0},
            'joint_wrist_pitch': {'min': -0.4, 'max': 0.4, 'current': 0.0},
            'joint_wrist_roll': {'min': -1.57, 'max': 1.57, 'current': 0.0},
            'joint_gripper_finger_left': {'min': -0.1, 'max': 0.1, 'current': 0.0},
            'joint_gripper_finger_right': {'min': -0.1, 'max': 0.1, 'current': 0.0},
            'joint_head_pan': {'min': -1.57, 'max': 1.57, 'current': 0.0},
            'joint_head_tilt': {'min': -0.79, 'max': 0.23, 'current': 0.0},
            'joint_left_wheel': {'min': -10.0, 'max': 10.0, 'current': 0.0},
            'joint_right_wheel': {'min': -10.0, 'max': 10.0, 'current': 0.0}
        }
        
        # Movement state
        self.current_twist = Twist()
        self.moving = False
        
        # UI elements
        self.sliders = {}
        self.value_labels = {}
        
        self.setup_gui()
        
        # Timer for publishing
        self.timer = self.create_timer(0.1, self.publish_commands)
        
    def joint_feedback_callback(self, msg):
        """Update joint positions from feedback"""
        for i, name in enumerate(msg.name):
            if name in self.joints and i < len(msg.position):
                self.joints[name]['current'] = msg.position[i]
                # Update UI
                if name in self.value_labels:
                    self.value_labels[name].config(text=f"{msg.position[i]:.3f}")
                if name in self.sliders:
                    # Update slider without triggering callback
                    self.sliders[name].set(msg.position[i])
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🤖 Enhanced Stretch Robot Controller")
        self.root.geometry("900x800")
        self.root.configure(bg='#2b2b2b')
        
        # Title
        title = tk.Label(self.root, text="🤖 Hello Robot Stretch 3 - Enhanced Controller", 
                        font=('Arial', 16, 'bold'), fg='white', bg='#2b2b2b')
        title.pack(pady=10)
        
        # Movement controls
        movement_frame = tk.Frame(self.root, bg='#2b2b2b', relief='groove', bd=2)
        movement_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(movement_frame, text="🚗 Robot Movement (Gazebo Physics)", 
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
        
        # Create notebook for organized joint controls
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Arm & Lift tab
        arm_frame = ttk.Frame(notebook)
        notebook.add(arm_frame, text="🦾 Arm & Lift")
        self.create_joint_controls(arm_frame, [
            'joint_lift', 'joint_arm_l0', 'joint_arm_l1', 'joint_arm_l2', 'joint_arm_l3'
        ])
        
        # Wrist & Gripper tab
        wrist_frame = ttk.Frame(notebook)
        notebook.add(wrist_frame, text="🤏 Wrist & Gripper")
        self.create_joint_controls(wrist_frame, [
            'joint_wrist_yaw', 'joint_wrist_pitch', 'joint_wrist_roll',
            'joint_gripper_finger_left', 'joint_gripper_finger_right'
        ])
        
        # Head & Wheels tab
        head_frame = ttk.Frame(notebook)
        notebook.add(head_frame, text="🎯 Head & Wheels")
        self.create_joint_controls(head_frame, [
            'joint_head_pan', 'joint_head_tilt', 'joint_left_wheel', 'joint_right_wheel'
        ])
        
        # Preset buttons
        preset_frame = tk.Frame(self.root, bg='#2b2b2b')
        preset_frame.pack(pady=10)
        
        tk.Button(preset_frame, text="🏠 Home", command=self.home_position,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(preset_frame, text="🥤 Reach Table", command=self.reach_table,
                 bg='#E91E63', fg='white', font=('Arial', 10, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(preset_frame, text="📏 Tall", command=self.tall_position,
                 bg='#9C27B0', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(preset_frame, text="📦 Compact", command=self.compact_position,
                 bg='#607D8B', fg='white', font=('Arial', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready - Exact Stretch Robot in Gazebo & RViz!",
                                   fg='#4CAF50', bg='#2b2b2b', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=10)
        
    def create_joint_controls(self, parent, joint_names):
        for i, joint_name in enumerate(joint_names):
            joint_info = self.joints[joint_name]
            
            # Frame for this joint
            frame = tk.Frame(parent, bg='white', relief='groove', bd=1)
            frame.pack(fill='x', padx=10, pady=5)
            
            # Joint name and current value
            header_frame = tk.Frame(frame, bg='white')
            header_frame.pack(fill='x', padx=5, pady=2)
            
            tk.Label(header_frame, text=joint_name.replace('joint_', '').replace('_', ' ').title(),
                    font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
            
            # Current value (updated from feedback)
            value_label = tk.Label(header_frame, text=f"{joint_info['current']:.3f}",
                                 font=('Arial', 10), bg='white', fg='blue')
            value_label.pack(side=tk.RIGHT)
            self.value_labels[joint_name] = value_label
            
            # Target value
            target_label = tk.Label(header_frame, text="Target: 0.000",
                                  font=('Arial', 9), bg='white', fg='green')
            target_label.pack(side=tk.RIGHT, padx=(0, 10))
            
            # Slider
            slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                            resolution=0.001, orient=tk.HORIZONTAL, length=400,
                            command=lambda val, jname=joint_name, tlabel=target_label: self.update_joint(jname, val, tlabel))
            slider.pack(fill='x', padx=5, pady=2)
            slider.set(joint_info['current'])
            
            self.sliders[joint_name] = slider
            
            # Range info
            tk.Label(frame, text=f"Range: {joint_info['min']:.2f} to {joint_info['max']:.2f}",
                    font=('Arial', 8), bg='white', fg='gray').pack()
    
    def update_joint(self, joint_name, value, target_label):
        self.joints[joint_name]['current'] = float(value)
        target_label.config(text=f"Target: {float(value):.3f}")
        self.status_label.config(text=f"🎯 {joint_name.replace('joint_', '')} → {float(value):.3f}")
    
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
    
    # Preset positions
    def home_position(self):
        positions = {
            'joint_lift': 0.0, 'joint_arm_l0': 0.0, 'joint_arm_l1': 0.0, 
            'joint_arm_l2': 0.0, 'joint_arm_l3': 0.0, 'joint_wrist_yaw': 0.0,
            'joint_wrist_pitch': 0.0, 'joint_wrist_roll': 0.0,
            'joint_gripper_finger_left': 0.0, 'joint_gripper_finger_right': 0.0,
            'joint_head_pan': 0.0, 'joint_head_tilt': 0.0
        }
        self.set_joint_positions(positions)
        self.status_label.config(text="🏠 Moved to home position")
    
    def reach_table(self):
        positions = {
            'joint_lift': 0.6, 'joint_arm_l0': 0.08, 'joint_arm_l1': 0.06,
            'joint_arm_l2': 0.04, 'joint_arm_l3': 0.02, 'joint_wrist_yaw': 0.0,
            'joint_wrist_pitch': -0.2, 'joint_head_pan': 0.5
        }
        self.set_joint_positions(positions)
        self.status_label.config(text="🥤 Positioned to reach table")
    
    def tall_position(self):
        positions = {
            'joint_lift': 1.0, 'joint_arm_l0': 0.05, 'joint_arm_l1': 0.03,
            'joint_arm_l2': 0.02, 'joint_arm_l3': 0.01, 'joint_head_tilt': -0.3
        }
        self.set_joint_positions(positions)
        self.status_label.config(text="📏 Extended to tall position")
    
    def compact_position(self):
        positions = {
            'joint_lift': 0.2, 'joint_arm_l0': 0.0, 'joint_arm_l1': 0.0,
            'joint_arm_l2': 0.0, 'joint_arm_l3': 0.0, 'joint_wrist_yaw': 0.0,
            'joint_head_pan': 0.0, 'joint_head_tilt': 0.0
        }
        self.set_joint_positions(positions)
        self.status_label.config(text="📦 Compacted for navigation")
    
    def set_joint_positions(self, positions):
        for joint, position in positions.items():
            if joint in self.joints:
                self.joints[joint]['current'] = position
                if joint in self.sliders:
                    self.sliders[joint].set(position)
    
    def publish_commands(self):
        # Publish movement
        self.cmd_vel_pub.publish(self.current_twist)
        
        # Publish joint states
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self.joints.keys())
        msg.position = [self.joints[name]['current'] for name in msg.name]
        msg.velocity = [0.0] * len(msg.name)
        msg.effort = [0.0] * len(msg.name)
        
        self.joint_pub.publish(msg)
    
    def run_gui(self):
        self.root.mainloop()

def main():
    rclpy.init()
    
    controller = EnhancedStretchController()
    
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
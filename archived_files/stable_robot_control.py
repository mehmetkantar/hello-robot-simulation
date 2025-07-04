#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped, Twist
from tf2_ros import TransformBroadcaster
import tkinter as tk
from tkinter import ttk
import threading
import time
import signal
import sys
import math

class StableStretchControl(Node):
    def __init__(self):
        super().__init__('stable_stretch_control')
        
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
            'lift': {'min': 0.0, 'max': 0.5, 'current': 0.0},
            'arm_extension': {'min': 0.0, 'max': 0.3, 'current': 0.0},
            'gripper': {'min': -0.1, 'max': 0.1, 'current': 0.0},
        }
        
        # Wheel joints (tracked separately for odometry)
        self.wheel_positions = {
            'left_wheel': 0.0,
            'right_wheel': 0.0
        }
        
        # Movement state
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        
        self.sliders = {}
        self.root = None
        
        # Timer for publishing
        self.timer = self.create_timer(0.1, self.update_robot)  # 10Hz
        
        print("✅ Stable Stretch control initialized")
        print(f"   Starting position: ({self.robot_x}, {self.robot_y})")
    
    def setup_gui(self):
        """Setup the GUI with simplified controls"""
        self.root = tk.Tk()
        self.root.title("🤖 Stable Stretch Robot Control")
        self.root.geometry("600x700")
        self.root.configure(bg='#1a1a1a')
        
        # Title
        title = tk.Label(self.root, text="🤖 Stable Stretch Robot Control", 
                        font=('Arial', 18, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=15)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready to control stable robot!",
                                   fg='#00ff00', bg='#1a1a1a', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        # Position display
        self.position_label = tk.Label(self.root, text=f"📍 Position: ({self.robot_x:.1f}, {self.robot_y:.1f}) θ=0.0°",
                                     fg='#ffff00', bg='#1a1a1a', font=('Arial', 11))
        self.position_label.pack(pady=5)
        
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a')
        style.configure('TNotebook.Tab', background='#333333', foreground='white')
        
        notebook = ttk.Notebook(self.root)
        
        # Driving tab
        drive_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(drive_frame, text="🚗 Drive")
        self.create_drive_tab(drive_frame)
        
        # Joint control tab
        joint_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(joint_frame, text="🦾 Joints")
        self.create_joint_tab(joint_frame)
        
        notebook.pack(expand=True, fill='both', padx=15, pady=10)
        
        # Control buttons
        self.create_control_buttons()
        
        print("✅ GUI setup complete")
    
    def create_drive_tab(self, parent):
        """Create the car driving interface"""
        # Speed controls
        speed_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        speed_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(speed_frame, text="🏎️ Speed Controls", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        # Linear speed
        linear_frame = tk.Frame(speed_frame, bg='#2d2d2d')
        linear_frame.pack(pady=5, fill='x', padx=10)
        
        tk.Label(linear_frame, text="Linear Speed (m/s):", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.linear_scale = tk.Scale(linear_frame, from_=0.0, to=0.5, resolution=0.1,
                                   orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white')
        self.linear_scale.set(0.2)
        self.linear_scale.pack(side=tk.RIGHT, padx=10)
        
        # Angular speed
        angular_frame = tk.Frame(speed_frame, bg='#2d2d2d')
        angular_frame.pack(pady=5, fill='x', padx=10)
        
        tk.Label(angular_frame, text="Turn Speed (rad/s):", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.angular_scale = tk.Scale(angular_frame, from_=0.0, to=1.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white')
        self.angular_scale.set(0.5)
        self.angular_scale.pack(side=tk.RIGHT, padx=10)
        
        # Driving controls
        drive_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        drive_frame.pack(pady=15, padx=20)
        
        tk.Label(drive_frame, text="🎮 Drive Controls", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        # Button grid
        button_grid = tk.Frame(drive_frame, bg='#2d2d2d')
        button_grid.pack(pady=15)
        
        btn_style = {
            'font': ('Arial', 14, 'bold'), 
            'fg': 'white', 
            'width': 8, 
            'height': 2,
            'relief': 'raised',
            'bd': 3
        }
        
        # Forward
        tk.Button(button_grid, text="⬆️\nForward", bg='#4CAF50', **btn_style,
                 command=self.drive_forward).grid(row=0, column=1, padx=5, pady=5)
        
        # Left and Right
        tk.Button(button_grid, text="⬅️\nLeft", bg='#2196F3', **btn_style,
                 command=self.drive_left).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(button_grid, text="🛑\nSTOP", bg='#F44336', **btn_style,
                 command=self.drive_stop).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(button_grid, text="➡️\nRight", bg='#2196F3', **btn_style,
                 command=self.drive_right).grid(row=1, column=2, padx=5, pady=5)
        
        # Backward
        tk.Button(button_grid, text="⬇️\nBackward", bg='#FF9800', **btn_style,
                 command=self.drive_backward).grid(row=2, column=1, padx=5, pady=5)
    
    def create_joint_tab(self, parent):
        """Create joint control tab"""
        for joint_name in self.joints:
            self.create_joint_control(parent, joint_name)
    
    def create_joint_control(self, parent, joint_name):
        """Create control for one joint"""
        joint_info = self.joints[joint_name]
        
        frame = tk.Frame(parent, bg='#3d3d3d', relief='raised', bd=2)
        frame.pack(fill='x', padx=10, pady=10)
        
        # Header
        header = tk.Frame(frame, bg='#3d3d3d')
        header.pack(fill='x', padx=8, pady=5)
        
        name_label = tk.Label(header, 
                            text=joint_name.replace('_', ' ').title(),
                            font=('Arial', 12, 'bold'), bg='#3d3d3d', fg='white')
        name_label.pack(side=tk.LEFT)
        
        value_label = tk.Label(header, text=f"{joint_info['current']:.3f}",
                             font=('Arial', 12, 'bold'), bg='#3d3d3d', fg='#00ff00')
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                        resolution=0.01, orient=tk.HORIZONTAL, length=400,
                        bg='#3d3d3d', fg='white', activebackground='#555555',
                        command=lambda val, jname=joint_name, vlabel=value_label: 
                               self.update_joint(jname, val, vlabel))
        slider.pack(fill='x', padx=8, pady=5)
        slider.set(joint_info['current'])
        
        self.sliders[joint_name] = slider
        
        # Range info
        range_label = tk.Label(frame, 
                             text=f"Range: {joint_info['min']:.2f} to {joint_info['max']:.2f}",
                             font=('Arial', 10), bg='#3d3d3d', fg='#888888')
        range_label.pack(pady=2)
    
    def create_control_buttons(self):
        """Create preset and control buttons"""
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="🏠 Home Position", command=self.go_home,
                 bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'), 
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="📍 Reset Position", command=self.reset_position,
                 bg='#607D8B', fg='white', font=('Arial', 12, 'bold'), 
                 width=15, height=2).pack(side=tk.LEFT, padx=10)
    
    def update_joint(self, joint_name, value, value_label):
        """Update joint position"""
        self.joints[joint_name]['current'] = float(value)
        value_label.config(text=f"{float(value):.3f}")
        self.status_label.config(text=f"🎮 {joint_name.replace('_', ' ')} = {float(value):.3f}")
    
    # Drive commands
    def drive_forward(self):
        self.linear_speed = self.linear_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.status_label.config(text="⬆️ Driving forward")
    
    def drive_backward(self):
        self.linear_speed = -self.linear_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.status_label.config(text="⬇️ Driving backward")
    
    def drive_left(self):
        self.linear_speed = 0.0
        self.angular_speed = self.angular_scale.get()
        self.is_moving = True
        self.status_label.config(text="⬅️ Turning left")
    
    def drive_right(self):
        self.linear_speed = 0.0
        self.angular_speed = -self.angular_scale.get()
        self.is_moving = True
        self.status_label.config(text="➡️ Turning right")
    
    def drive_stop(self):
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        self.status_label.config(text="🛑 Stopped")
    
    def go_home(self):
        """Reset all joints to home position"""
        for joint_name in self.joints:
            self.joints[joint_name]['current'] = 0.0
            if joint_name in self.sliders:
                self.sliders[joint_name].set(0.0)
        self.drive_stop()
        self.status_label.config(text="🏠 Home position")
    
    def reset_position(self):
        """Reset robot position to starting location"""
        self.robot_x = -5.0
        self.robot_y = 4.0
        self.robot_theta = 0.0
        self.wheel_positions['left_wheel'] = 0.0
        self.wheel_positions['right_wheel'] = 0.0
        self.drive_stop()
        self.status_label.config(text="📍 Position reset to start")
    
    def update_robot(self):
        """Update robot state and publish transforms"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Update robot position based on movement
        if self.is_moving:
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
        
        # Update position display
        self.position_label.config(
            text=f"📍 Position: ({self.robot_x:.2f}, {self.robot_y:.2f}) θ={math.degrees(self.robot_theta):.1f}°"
        )
        
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
    
    def run_gui(self):
        """Run the GUI"""
        if self.root:
            try:
                self.root.mainloop()
            except Exception as e:
                print(f"GUI error: {e}")

def signal_handler(sig, frame):
    print("\nShutting down...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    rclpy.init()
    
    controller = None
    try:
        controller = StableStretchControl()
        controller.setup_gui()
        
        # Run ROS2 in background
        def spin_ros():
            try:
                rclpy.spin(controller)
            except:
                pass
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        print("🤖 Stable robot control GUI starting...")
        controller.run_gui()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if controller:
            controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
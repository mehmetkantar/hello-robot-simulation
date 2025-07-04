#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import tkinter as tk
from tkinter import ttk
import threading
import time

class SimpleRobotController(Node):
    def __init__(self):
        super().__init__('simple_robot_controller')
        
        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Joint definitions for the Stretch robot
        self.joints = {
            'joint_lift': {'min': 0.0, 'max': 1.1, 'current': 0.2},
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
            'joint_right_wheel': {'min': -10.0, 'max': 10.0, 'current': 0.0},
            'joint_left_wheel': {'min': -10.0, 'max': 10.0, 'current': 0.0},
        }
        
        self.sliders = {}
        self.root = None
        
        # Timer for publishing joint states
        self.timer = self.create_timer(0.1, self.publish_joint_states)
        
        print("✅ Simple robot controller initialized")
    
    def setup_gui(self):
        """Setup the control GUI"""
        self.root = tk.Tk()
        self.root.title("🤖 Simple Stretch Robot Controller")
        self.root.geometry("600x800")
        self.root.configure(bg='#2d2d2d')
        
        # Title
        title = tk.Label(self.root, text="🤖 Stretch Robot Controller", 
                        font=('Arial', 16, 'bold'), fg='#00ff00', bg='#2d2d2d')
        title.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready to control robot in Gazebo!",
                                   fg='#00ff00', bg='#2d2d2d', font=('Arial', 12))
        self.status_label.pack(pady=5)
        
        # Create scrollable frame for joint controls
        canvas = tk.Canvas(self.root, bg='#2d2d2d', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d2d2d')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add joint controls
        for joint_name in self.joints:
            self.create_joint_control(scrollable_frame, joint_name)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Preset buttons
        self.create_preset_buttons()
        
        print("✅ GUI setup complete")
    
    def create_joint_control(self, parent, joint_name):
        """Create control for one joint"""
        joint_info = self.joints[joint_name]
        
        frame = tk.Frame(parent, bg='#3d3d3d', relief='raised', bd=2)
        frame.pack(fill='x', padx=5, pady=3)
        
        # Header
        header = tk.Frame(frame, bg='#3d3d3d')
        header.pack(fill='x', padx=8, pady=3)
        
        name_label = tk.Label(header, 
                            text=joint_name.replace('joint_', '').replace('_', ' ').title(),
                            font=('Arial', 10, 'bold'), bg='#3d3d3d', fg='white')
        name_label.pack(side=tk.LEFT)
        
        value_label = tk.Label(header, text=f"{joint_info['current']:.3f}",
                             font=('Arial', 10, 'bold'), bg='#3d3d3d', fg='#00ff00')
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                        resolution=0.01, orient=tk.HORIZONTAL, length=350,
                        bg='#3d3d3d', fg='white', activebackground='#555555',
                        command=lambda val, jname=joint_name, vlabel=value_label: 
                               self.update_joint(jname, val, vlabel))
        slider.pack(fill='x', padx=8, pady=3)
        slider.set(joint_info['current'])
        
        self.sliders[joint_name] = slider
    
    def create_preset_buttons(self):
        """Create preset position buttons"""
        button_frame = tk.Frame(self.root, bg='#2d2d2d')
        button_frame.pack(pady=10)
        
        btn_style = {
            'font': ('Arial', 10, 'bold'), 
            'fg': 'white', 
            'width': 12, 
            'height': 2
        }
        
        tk.Button(button_frame, text="🏠 Home", command=self.go_home,
                 bg='#4CAF50', **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🦾 Extend Arm", command=self.extend_arm,
                 bg='#2196F3', **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="⬆️ Lift Up", command=self.lift_up,
                 bg='#FF9800', **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🤏 Open Gripper", command=self.open_gripper,
                 bg='#9C27B0', **btn_style).pack(side=tk.LEFT, padx=5)
    
    def update_joint(self, joint_name, value, value_label):
        """Update joint position"""
        self.joints[joint_name]['current'] = float(value)
        if value_label:
            value_label.config(text=f"{float(value):.3f}")
        self.status_label.config(text=f"Moving {joint_name.replace('joint_', '')} to {float(value):.3f}")
    
    def go_home(self):
        """Move robot to home position"""
        positions = {
            'joint_lift': 0.2,
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
        }
        self.set_positions(positions)
        self.status_label.config(text="🏠 Moving to home position")
    
    def extend_arm(self):
        """Extend the robot arm"""
        positions = {
            'joint_arm_l0': 0.1,
            'joint_arm_l1': 0.1,
            'joint_arm_l2': 0.1,
            'joint_arm_l3': 0.1,
        }
        self.set_positions(positions)
        self.status_label.config(text="🦾 Extending arm")
    
    def lift_up(self):
        """Lift the robot up"""
        self.set_positions({'joint_lift': 0.8})
        self.status_label.config(text="⬆️ Lifting up")
    
    def open_gripper(self):
        """Open the gripper"""
        positions = {
            'joint_gripper_finger_left': 0.08,
            'joint_gripper_finger_right': -0.08,
        }
        self.set_positions(positions)
        self.status_label.config(text="🤏 Opening gripper")
    
    def set_positions(self, positions):
        """Set multiple joint positions"""
        for joint_name, position in positions.items():
            if joint_name in self.joints:
                self.joints[joint_name]['current'] = position
                if joint_name in self.sliders:
                    self.sliders[joint_name].set(position)
    
    def publish_joint_states(self):
        """Publish current joint states"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        
        # Add all joints
        joint_names = list(self.joints.keys())
        joint_positions = [self.joints[name]['current'] for name in joint_names]
        
        msg.name = joint_names
        msg.position = joint_positions
        msg.velocity = [0.0] * len(joint_names)
        msg.effort = [0.0] * len(joint_names)
        
        self.joint_pub.publish(msg)
    
    def run_gui(self):
        """Run the GUI"""
        if self.root:
            try:
                self.root.mainloop()
            except Exception as e:
                print(f"GUI error: {e}")

def main():
    rclpy.init()
    
    controller = None
    try:
        controller = SimpleRobotController()
        controller.setup_gui()
        
        # Run ROS2 in background
        def spin_ros():
            try:
                rclpy.spin(controller)
            except:
                pass
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        print("🤖 Simple robot controller starting...")
        print("✅ You should see robot moving in Gazebo when you use sliders!")
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
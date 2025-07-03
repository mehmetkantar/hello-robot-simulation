#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import tkinter as tk
from tkinter import ttk
import threading
import time
import signal
import sys

class StretchJointController(Node):
    def __init__(self):
        super().__init__('stretch_joint_controller')
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        
        # Joint limits and current positions
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
        
        self.sliders = {}
        self.root = None
        
        # Timer to publish joint states
        self.timer = self.create_timer(0.1, self.publish_joint_states)
        
        # Robot position tracking (for visualization)
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        
        # Movement state
        self.moving = False
        self.move_direction = 'stop'
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🤖 Stretch Robot - Joint Controller")
        self.root.geometry("600x800")
        self.root.configure(bg='#2b2b2b')
        
        # Title
        title = tk.Label(self.root, text="🤖 Hello Robot Stretch 3 - Joint Control", 
                        font=('Arial', 16, 'bold'), fg='white', bg='#2b2b2b')
        title.pack(pady=10)
        
        # Create notebook for organized tabs
        notebook = ttk.Notebook(self.root)
        
        # Arm control tab
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
        
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        # First row of buttons
        button_row1 = tk.Frame(button_frame, bg='#2b2b2b')
        button_row1.pack(pady=2)
        
        tk.Button(button_row1, text="🏠 Home", command=self.home_position,
                 bg='#4CAF50', fg='white', font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_row1, text="🥤 Reach Table", command=self.reach_table_position,
                 bg='#E91E63', fg='white', font=('Arial', 9, 'bold'), width=10).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_row1, text="📏 Tall", command=self.tall_position,
                 bg='#9C27B0', fg='white', font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_row1, text="📦 Compact", command=self.compact_position,
                 bg='#607D8B', fg='white', font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=2)
        
        # Second row of buttons
        button_row2 = tk.Frame(button_frame, bg='#2b2b2b')
        button_row2.pack(pady=2)
        
        tk.Button(button_row2, text="🎯 Demo", command=self.demo_position,
                 bg='#2196F3', fg='white', font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(button_row2, text="🎲 Random", command=self.randomize_position,
                 bg='#FF9800', fg='white', font=('Arial', 9, 'bold'), width=8).pack(side=tk.LEFT, padx=2)
        
        # Third row - Movement controls
        movement_frame = tk.Frame(self.root, bg='#2b2b2b', relief='groove', bd=2)
        movement_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(movement_frame, text="🚗 Robot Movement Controls", 
                font=('Arial', 12, 'bold'), fg='white', bg='#2b2b2b').pack(pady=5)
        
        # Movement buttons in a grid
        move_grid = tk.Frame(movement_frame, bg='#2b2b2b')
        move_grid.pack(pady=5)
        
        # Top row - Forward
        tk.Button(move_grid, text="⬆️\nForward", command=self.move_forward,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), 
                 width=8, height=2).grid(row=0, column=1, padx=2, pady=2)
        
        # Middle row - Turn left, Stop, Turn right
        tk.Button(move_grid, text="⬅️\nTurn Left", command=self.turn_left,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'), 
                 width=8, height=2).grid(row=1, column=0, padx=2, pady=2)
        
        tk.Button(move_grid, text="⏹️\nSTOP", command=self.stop_robot,
                 bg='#F44336', fg='white', font=('Arial', 10, 'bold'), 
                 width=8, height=2).grid(row=1, column=1, padx=2, pady=2)
        
        tk.Button(move_grid, text="➡️\nTurn Right", command=self.turn_right,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'), 
                 width=8, height=2).grid(row=1, column=2, padx=2, pady=2)
        
        # Bottom row - Backward
        tk.Button(move_grid, text="⬇️\nBackward", command=self.move_backward,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'), 
                 width=8, height=2).grid(row=2, column=1, padx=2, pady=2)
        
        # Speed control
        speed_frame = tk.Frame(movement_frame, bg='#2b2b2b')
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, text="Speed:", font=('Arial', 10), fg='white', bg='#2b2b2b').pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1, 
                                  orient=tk.HORIZONTAL, length=200, bg='#2b2b2b', fg='white')
        self.speed_scale.set(0.5)  # Default speed
        self.speed_scale.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready - Move sliders to control robot",
                                   fg='#4CAF50', bg='#2b2b2b', font=('Arial', 10))
        self.status_label.pack(pady=5)
        
    def create_joint_controls(self, parent, joint_names):
        for i, joint_name in enumerate(joint_names):
            joint_info = self.joints[joint_name]
            
            # Frame for this joint
            frame = tk.Frame(parent, bg='white', relief='groove', bd=1)
            frame.pack(fill='x', padx=10, pady=5)
            
            # Joint name and value
            header_frame = tk.Frame(frame, bg='white')
            header_frame.pack(fill='x', padx=5, pady=2)
            
            tk.Label(header_frame, text=joint_name.replace('joint_', '').replace('_', ' ').title(),
                    font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT)
            
            value_label = tk.Label(header_frame, text=f"{joint_info['current']:.3f}",
                                 font=('Arial', 10), bg='white', fg='blue')
            value_label.pack(side=tk.RIGHT)
            
            # Slider
            slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                            resolution=0.001, orient=tk.HORIZONTAL, length=400,
                            command=lambda val, jname=joint_name, vlabel=value_label: self.update_joint(jname, val, vlabel))
            slider.pack(fill='x', padx=5, pady=2)
            slider.set(joint_info['current'])
            
            self.sliders[joint_name] = slider
            
            # Range info
            tk.Label(frame, text=f"Range: {joint_info['min']:.2f} to {joint_info['max']:.2f}",
                    font=('Arial', 8), bg='white', fg='gray').pack()
    
    def update_joint(self, joint_name, value, value_label):
        self.joints[joint_name]['current'] = float(value)
        value_label.config(text=f"{float(value):.3f}")
        self.status_label.config(text=f"🎮 Updated {joint_name.replace('joint_', '')} = {float(value):.3f}")
    
    def home_position(self):
        """Set all joints to home/zero position"""
        for joint_name in self.joints:
            self.joints[joint_name]['current'] = 0.0
            if joint_name in self.sliders:
                self.sliders[joint_name].set(0.0)
        self.status_label.config(text="🏠 Moved to home position")
    
    def demo_position(self):
        """Set a nice demo position"""
        demo_positions = {
            'joint_lift': 0.6,
            'joint_arm_l0': 0.08,
            'joint_arm_l1': 0.06,
            'joint_arm_l2': 0.04,
            'joint_arm_l3': 0.02,
            'joint_wrist_yaw': 0.3,
            'joint_head_pan': 0.2
        }
        
        for joint_name, position in demo_positions.items():
            if joint_name in self.joints:
                self.joints[joint_name]['current'] = position
                if joint_name in self.sliders:
                    self.sliders[joint_name].set(position)
        self.status_label.config(text="🎯 Moved to demo position")
    
    def reach_table_position(self):
        """Position robot to reach table objects"""
        table_positions = {
            'joint_lift': 0.7,
            'joint_arm_l0': 0.10,
            'joint_arm_l1': 0.08,
            'joint_arm_l2': 0.06,
            'joint_arm_l3': 0.04,
            'joint_wrist_yaw': 0.0,
            'joint_wrist_pitch': -0.2,
            'joint_head_pan': 0.5
        }
        
        for joint_name, position in table_positions.items():
            if joint_name in self.joints:
                self.joints[joint_name]['current'] = position
                if joint_name in self.sliders:
                    self.sliders[joint_name].set(position)
        self.status_label.config(text="🥤 Positioned to reach table objects")
    
    def tall_position(self):
        """Extend robot to maximum safe height"""
        tall_positions = {
            'joint_lift': 1.0,
            'joint_arm_l0': 0.05,
            'joint_arm_l1': 0.03,
            'joint_arm_l2': 0.02,
            'joint_arm_l3': 0.01,
            'joint_wrist_yaw': 0.0,
            'joint_head_pan': 0.0,
            'joint_head_tilt': -0.3
        }
        
        for joint_name, position in tall_positions.items():
            if joint_name in self.joints:
                self.joints[joint_name]['current'] = position
                if joint_name in self.sliders:
                    self.sliders[joint_name].set(position)
        self.status_label.config(text="📏 Extended to tall position")
    
    def compact_position(self):
        """Compact robot for navigation"""
        compact_positions = {
            'joint_lift': 0.2,
            'joint_arm_l0': 0.0,
            'joint_arm_l1': 0.0,
            'joint_arm_l2': 0.0,
            'joint_arm_l3': 0.0,
            'joint_wrist_yaw': 0.0,
            'joint_wrist_pitch': 0.0,
            'joint_head_pan': 0.0,
            'joint_head_tilt': 0.0
        }
        
        for joint_name, position in compact_positions.items():
            if joint_name in self.joints:
                self.joints[joint_name]['current'] = position
                if joint_name in self.sliders:
                    self.sliders[joint_name].set(position)
        self.status_label.config(text="📦 Compacted for navigation")
    
    def randomize_position(self):
        """Set random positions within safe ranges"""
        import random
        
        safe_ranges = {
            'joint_lift': (0.2, 0.9),
            'joint_arm_l0': (0.0, 0.1),
            'joint_arm_l1': (0.0, 0.08),
            'joint_arm_l2': (0.0, 0.06),
            'joint_arm_l3': (0.0, 0.04),
            'joint_wrist_yaw': (-0.5, 0.5),
            'joint_wrist_pitch': (-0.2, 0.2),
            'joint_head_pan': (-0.5, 0.5),
            'joint_head_tilt': (-0.2, 0.1)
        }
        
        for joint_name, (min_val, max_val) in safe_ranges.items():
            if joint_name in self.joints:
                position = random.uniform(min_val, max_val)
                self.joints[joint_name]['current'] = position
                if joint_name in self.sliders:
                    self.sliders[joint_name].set(position)
        self.status_label.config(text="🎲 Randomized to safe position")
    
    # Movement control functions
    def move_forward(self):
        """Move robot forward"""
        self.move_direction = 'forward'
        self.moving = True
        speed = self.speed_scale.get()
        self.update_wheel_movement(speed, speed)
        self.status_label.config(text=f"⬆️ Moving forward at speed {speed:.1f}")
    
    def move_backward(self):
        """Move robot backward"""
        self.move_direction = 'backward'
        self.moving = True
        speed = self.speed_scale.get()
        self.update_wheel_movement(-speed, -speed)
        self.status_label.config(text=f"⬇️ Moving backward at speed {speed:.1f}")
    
    def turn_left(self):
        """Turn robot left"""
        self.move_direction = 'left'
        self.moving = True
        speed = self.speed_scale.get()
        self.update_wheel_movement(-speed*0.5, speed*0.5)
        self.status_label.config(text=f"⬅️ Turning left at speed {speed:.1f}")
    
    def turn_right(self):
        """Turn robot right"""
        self.move_direction = 'right'
        self.moving = True
        speed = self.speed_scale.get()
        self.update_wheel_movement(speed*0.5, -speed*0.5)
        self.status_label.config(text=f"➡️ Turning right at speed {speed:.1f}")
    
    def stop_robot(self):
        """Stop all robot movement"""
        self.move_direction = 'stop'
        self.moving = False
        self.update_wheel_movement(0.0, 0.0)
        self.status_label.config(text="⏹️ Robot stopped")
    
    def update_wheel_movement(self, left_speed, right_speed):
        """Update wheel joint positions to simulate movement"""
        import time
        import math
        
        # Create a timer that will automatically stop after a short movement
        if not hasattr(self, 'movement_timer'):
            self.movement_timer = None
        
        # Update wheel positions based on speed
        current_time = time.time()
        if not hasattr(self, 'last_time'):
            self.last_time = current_time
        
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Only move for a short burst unless it's stopped
        if left_speed != 0 or right_speed != 0:
            # Simulate wheel rotation
            wheel_radius = 0.05  # 5cm wheel radius
            left_rotation = left_speed * 0.1  # Short burst movement
            right_rotation = right_speed * 0.1
            
            # Update wheel joint positions
            if 'joint_left_wheel' in self.joints:
                current_left = self.joints['joint_left_wheel']['current']
                new_left = current_left + left_rotation
                self.joints['joint_left_wheel']['current'] = new_left
                if 'joint_left_wheel' in self.sliders:
                    self.sliders['joint_left_wheel'].set(new_left % 6.28)
            
            if 'joint_right_wheel' in self.joints:
                current_right = self.joints['joint_right_wheel']['current']
                new_right = current_right + right_rotation
                self.joints['joint_right_wheel']['current'] = new_right
                if 'joint_right_wheel' in self.sliders:
                    self.sliders['joint_right_wheel'].set(new_right % 6.28)
        
        # Note: In RViz, wheels rotate but robot doesn't move through space
        # This is normal - RViz is for visualization, not physics simulation
    
    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        msg.name = list(self.joints.keys())
        msg.position = [self.joints[name]['current'] for name in msg.name]
        msg.velocity = [0.0] * len(msg.name)
        msg.effort = [0.0] * len(msg.name)
        
        self.publisher.publish(msg)
    
    def run_gui(self):
        if self.root:
            try:
                self.root.mainloop()
            except Exception as e:
                print(f"GUI error: {e}")
            finally:
                if self.root:
                    try:
                        self.root.quit()
                        self.root.destroy()
                    except:
                        pass

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize ROS2 first
    rclpy.init()
    
    controller = None
    try:
        controller = StretchJointController()
        print("✅ ROS2 controller initialized")
        
        # Setup GUI after ROS2 initialization
        controller.setup_gui()
        print("✅ GUI initialized")
        
        # Run ROS2 in a separate thread
        def spin_ros():
            try:
                rclpy.spin(controller)
            except Exception as e:
                print(f"ROS2 spinning error: {e}")
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        print("✅ ROS2 spinning in background")
        
        # Small delay to ensure ROS2 is running
        time.sleep(0.2)
        
        # Run GUI in main thread
        print("🚀 Starting GUI...")
        controller.run_gui()
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        try:
            if controller:
                controller.destroy_node()
        except Exception as e:
            print(f"Warning during cleanup: {e}")
        try:
            rclpy.shutdown()
        except Exception as e:
            print(f"Warning during ROS2 shutdown: {e}")

if __name__ == '__main__':
    main()
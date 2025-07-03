#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import String
from tf2_ros import TransformBroadcaster
import tkinter as tk
from tkinter import ttk
import threading
import time
import signal
import sys
import math
import subprocess

class StableWorldControl(Node):
    def __init__(self):
        super().__init__('stable_world_control')
        
        # Publishers
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Robot state
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        self.last_time = time.time()
        
        # Wheel parameters
        self.wheel_base = 0.33
        self.wheel_radius = 0.05
        
        # Joint definitions
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
        }
        
        # Wheel joints
        self.wheel_positions = {
            'joint_left_wheel': 0.0,
            'joint_right_wheel': 0.0
        }
        
        # Movement state
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        
        # Available worlds
        self.worlds = ["empty", "office", "warehouse", "home", "maze", "garden", "factory"]
        self.current_world = "empty"
        
        self.sliders = {}
        self.root = None
        
        # Timer for updates
        self.timer = self.create_timer(0.05, self.update_robot)
        
        print("✅ Stable world control initialized")
    
    def setup_gui(self):
        """Setup simplified GUI"""
        try:
            self.root = tk.Tk()
            self.root.title("🌍 Stretch Robot - World Control")
            self.root.geometry("700x800")
            self.root.configure(bg='#1a1a1a')
            
            # Title
            title = tk.Label(self.root, text="🌍 Stretch Robot - World Control", 
                            font=('Arial', 18, 'bold'), fg='#00ff00', bg='#1a1a1a')
            title.pack(pady=10)
            
            # Status
            self.status_label = tk.Label(self.root, text="✅ Ready to drive!",
                                       fg='#00ff00', bg='#1a1a1a', font=('Arial', 12))
            self.status_label.pack(pady=5)
            
            # Position display
            self.position_label = tk.Label(self.root, text="📍 Position: (0.0, 0.0) θ=0.0°",
                                         fg='#ffff00', bg='#1a1a1a', font=('Arial', 11))
            self.position_label.pack(pady=5)
            
            # World selection
            self.create_world_selector()
            
            # Drive controls
            self.create_drive_controls()
            
            # Basic joint controls
            self.create_basic_joint_controls()
            
            # Control buttons
            self.create_control_buttons()
            
            print("✅ GUI setup complete")
            
        except Exception as e:
            print(f"GUI setup error: {e}")
            return False
        
        return True
    
    def create_world_selector(self):
        """Simple world selection"""
        world_frame = tk.Frame(self.root, bg='#2d2d2d', relief='raised', bd=2)
        world_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(world_frame, text="🌍 Select World", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=5)
        
        # Current world display
        self.world_label = tk.Label(world_frame, text=f"Current: {self.current_world.title()}", 
                                   font=('Arial', 12), fg='#00ff00', bg='#2d2d2d')
        self.world_label.pack(pady=5)
        
        # World buttons in rows
        button_frame = tk.Frame(world_frame, bg='#2d2d2d')
        button_frame.pack(pady=10)
        
        worlds = [
            ("Empty", "empty"), ("Office", "office"), ("Warehouse", "warehouse"),
            ("Home", "home"), ("Maze", "maze"), ("Garden", "garden"), ("Factory", "factory")
        ]
        
        for i, (name, key) in enumerate(worlds):
            row = i // 3
            col = i % 3
            
            if col == 0:
                if not hasattr(self, f'world_row_{row}'):
                    setattr(self, f'world_row_{row}', tk.Frame(button_frame, bg='#2d2d2d'))
                    getattr(self, f'world_row_{row}').pack(pady=2)
            
            parent = getattr(self, f'world_row_{row}')
            
            btn = tk.Button(parent, text=name, 
                          command=lambda w=key: self.switch_world(w),
                          bg='#4CAF50', fg='white', font=('Arial', 10),
                          width=8, height=1)
            btn.pack(side=tk.LEFT, padx=2)
    
    def create_drive_controls(self):
        """Create driving controls"""
        drive_frame = tk.Frame(self.root, bg='#2d2d2d', relief='raised', bd=2)
        drive_frame.pack(pady=10, padx=20)
        
        tk.Label(drive_frame, text="🚗 Drive Controls", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=5)
        
        # Speed controls
        speed_frame = tk.Frame(drive_frame, bg='#2d2d2d')
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, text="Speed:", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.speed_scale = tk.Scale(speed_frame, from_=0.1, to=1.0, resolution=0.1,
                                  orient=tk.HORIZONTAL, length=200, bg='#2d2d2d', fg='white')
        self.speed_scale.set(0.5)
        self.speed_scale.pack(side=tk.LEFT, padx=10)
        
        # Drive buttons
        button_grid = tk.Frame(drive_frame, bg='#2d2d2d')
        button_grid.pack(pady=10)
        
        # Forward
        tk.Button(button_grid, text="⬆️", command=self.drive_forward,
                 bg='#4CAF50', fg='white', font=('Arial', 16), 
                 width=4, height=2).grid(row=0, column=1, padx=5, pady=5)
        
        # Left, Stop, Right
        tk.Button(button_grid, text="⬅️", command=self.drive_left,
                 bg='#2196F3', fg='white', font=('Arial', 16), 
                 width=4, height=2).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(button_grid, text="🛑", command=self.drive_stop,
                 bg='#F44336', fg='white', font=('Arial', 16), 
                 width=4, height=2).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(button_grid, text="➡️", command=self.drive_right,
                 bg='#2196F3', fg='white', font=('Arial', 16), 
                 width=4, height=2).grid(row=1, column=2, padx=5, pady=5)
        
        # Backward
        tk.Button(button_grid, text="⬇️", command=self.drive_backward,
                 bg='#FF9800', fg='white', font=('Arial', 16), 
                 width=4, height=2).grid(row=2, column=1, padx=5, pady=5)
    
    def create_basic_joint_controls(self):
        """Create basic joint controls for main joints only"""
        joint_frame = tk.Frame(self.root, bg='#2d2d2d', relief='raised', bd=2)
        joint_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(joint_frame, text="🦾 Main Joint Controls", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=5)
        
        # Only show main joints to avoid GUI complexity
        main_joints = ['joint_lift', 'joint_arm_l0', 'joint_wrist_yaw', 'joint_head_pan']
        
        for joint_name in main_joints:
            self.create_simple_joint_control(joint_frame, joint_name)
    
    def create_simple_joint_control(self, parent, joint_name):
        """Create simple joint control"""
        joint_info = self.joints[joint_name]
        
        frame = tk.Frame(parent, bg='#3d3d3d', relief='groove', bd=1)
        frame.pack(fill='x', padx=5, pady=2)
        
        # Header
        header = tk.Frame(frame, bg='#3d3d3d')
        header.pack(fill='x', padx=5, pady=2)
        
        name = joint_name.replace('joint_', '').replace('_', ' ').title()
        tk.Label(header, text=name, font=('Arial', 10), bg='#3d3d3d', fg='white').pack(side=tk.LEFT)
        
        value_label = tk.Label(header, text=f"{joint_info['current']:.2f}",
                             font=('Arial', 10), bg='#3d3d3d', fg='#00ff00')
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                        resolution=0.05, orient=tk.HORIZONTAL, length=300,
                        bg='#3d3d3d', fg='white',
                        command=lambda val, jname=joint_name, vlabel=value_label: 
                               self.update_joint(jname, val, vlabel))
        slider.pack(fill='x', padx=5, pady=2)
        slider.set(joint_info['current'])
        
        self.sliders[joint_name] = slider
    
    def create_control_buttons(self):
        """Create control buttons"""
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=10)
        
        buttons = [
            ("🏠 Home", self.go_home, "#4CAF50"),
            ("🎯 Demo", self.demo_drive, "#E91E63"), 
            ("📍 Reset", self.reset_position, "#607D8B"),
            ("🔄 Start Env", self.start_environment, "#9C27B0")
        ]
        
        for text, command, color in buttons:
            tk.Button(button_frame, text=text, command=command,
                     bg=color, fg='white', font=('Arial', 10, 'bold'), 
                     width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    def switch_world(self, world_name):
        """Switch to a different world"""
        if world_name in self.worlds:
            self.current_world = world_name
            self.world_label.config(text=f"Current: {world_name.title()}")
            self.status_label.config(text=f"🌍 Switched to {world_name} world")
            
            # Send command to world environment node
            self.send_world_command(world_name)
            print(f"🌍 Switched to {world_name} world")
    
    def send_world_command(self, world_name):
        """Send command to change world (simplified)"""
        try:
            # Simple topic publish command
            cmd = f'timeout 2s bash -c "source /opt/ros/humble/setup.bash && ros2 topic pub --once /world_command std_msgs/String \\"data: {world_name}\\""'
            subprocess.run(cmd, shell=True, capture_output=True)
        except Exception as e:
            print(f"Failed to send world command: {e}")
    
    def start_environment(self):
        """Start the world environment node"""
        try:
            cmd = 'python3 /home/kantar/Desktop/hello-robot/world_environments.py &'
            subprocess.Popen(cmd, shell=True)
            self.status_label.config(text="🔄 Started world environment")
            time.sleep(1)
            self.send_world_command(self.current_world)
        except Exception as e:
            print(f"Failed to start environment: {e}")
    
    # Movement methods
    def drive_forward(self):
        self.linear_speed = self.speed_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.status_label.config(text="⬆️ Moving forward")
    
    def drive_backward(self):
        self.linear_speed = -self.speed_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.status_label.config(text="⬇️ Moving backward")
    
    def drive_left(self):
        self.linear_speed = 0.0
        self.angular_speed = self.speed_scale.get()
        self.is_moving = True
        self.status_label.config(text="⬅️ Turning left")
    
    def drive_right(self):
        self.linear_speed = 0.0
        self.angular_speed = -self.speed_scale.get()
        self.is_moving = True
        self.status_label.config(text="➡️ Turning right")
    
    def drive_stop(self):
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        self.status_label.config(text="🛑 Stopped")
    
    def go_home(self):
        for joint_name in self.joints:
            self.joints[joint_name]['current'] = 0.0
            if joint_name in self.sliders:
                self.sliders[joint_name].set(0.0)
        self.drive_stop()
        self.status_label.config(text="🏠 Home position")
    
    def reset_position(self):
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        self.wheel_positions['joint_left_wheel'] = 0.0
        self.wheel_positions['joint_right_wheel'] = 0.0
        self.drive_stop()
        self.status_label.config(text="📍 Position reset")
    
    def demo_drive(self):
        """Simple demo drive"""
        self.status_label.config(text="🎯 Demo drive...")
        
        def drive_pattern():
            # Simple square pattern
            moves = [(0.3, 0.0, 1.5), (0.0, -1.57, 1), (0.3, 0.0, 1.5), (0.0, -1.57, 1),
                     (0.3, 0.0, 1.5), (0.0, -1.57, 1), (0.3, 0.0, 1.5), (0.0, -1.57, 1)]
            
            for linear, angular, duration in moves:
                self.linear_speed = linear
                self.angular_speed = angular
                self.is_moving = linear != 0 or angular != 0
                time.sleep(duration)
            
            self.drive_stop()
            self.status_label.config(text="✅ Demo complete")
        
        threading.Thread(target=drive_pattern, daemon=True).start()
    
    def update_joint(self, joint_name, value, value_label):
        self.joints[joint_name]['current'] = float(value)
        value_label.config(text=f"{float(value):.2f}")
    
    def update_robot(self):
        """Update robot state"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        if self.is_moving:
            self.robot_x += self.linear_speed * math.cos(self.robot_theta) * dt
            self.robot_y += self.linear_speed * math.sin(self.robot_theta) * dt
            self.robot_theta += self.angular_speed * dt
            self.robot_theta = math.atan2(math.sin(self.robot_theta), math.cos(self.robot_theta))
            
            left_wheel_speed = self.linear_speed - (self.angular_speed * self.wheel_base / 2.0)
            right_wheel_speed = self.linear_speed + (self.angular_speed * self.wheel_base / 2.0)
            
            self.wheel_positions['joint_left_wheel'] += (left_wheel_speed / self.wheel_radius) * dt
            self.wheel_positions['joint_right_wheel'] += (right_wheel_speed / self.wheel_radius) * dt
        
        if hasattr(self, 'position_label'):
            self.position_label.config(
                text=f"📍 Position: ({self.robot_x:.2f}, {self.robot_y:.2f}) θ={math.degrees(self.robot_theta):.1f}°"
            )
        
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
        
        joint_names = list(self.joints.keys())
        joint_positions = [self.joints[name]['current'] for name in joint_names]
        
        joint_names.extend(['joint_left_wheel', 'joint_right_wheel'])
        joint_positions.extend([
            self.wheel_positions['joint_left_wheel'],
            self.wheel_positions['joint_right_wheel']
        ])
        
        msg.name = joint_names
        msg.position = joint_positions
        msg.velocity = [0.0] * len(joint_names)
        msg.effort = [0.0] * len(joint_names)
        
        self.joint_pub.publish(msg)
    
    def run_gui(self):
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
    
    # Initialize ROS2 first
    rclpy.init()
    
    controller = None
    try:
        print("🚀 Starting stable world control...")
        controller = StableWorldControl()
        
        # Setup GUI with error handling
        if not controller.setup_gui():
            print("❌ GUI setup failed")
            return
        
        # Run ROS2 in background thread
        def spin_ros():
            try:
                rclpy.spin(controller)
            except Exception as e:
                print(f"ROS2 error: {e}")
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        # Small delay for ROS2 to start
        time.sleep(0.3)
        
        print("🎮 GUI starting...")
        controller.run_gui()
        
    except KeyboardInterrupt:
        print("\nReceived interrupt")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        if controller:
            try:
                controller.destroy_node()
            except:
                pass
        try:
            rclpy.shutdown()
        except:
            pass

if __name__ == '__main__':
    main()
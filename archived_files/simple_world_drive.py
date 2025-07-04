#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import tkinter as tk
import threading
import time
import signal
import sys
import math
import subprocess

class SimpleWorldDrive(Node):
    def __init__(self):
        super().__init__('simple_world_drive')
        
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
        
        # Simple joint definitions
        self.joints = {
            'joint_lift': {'current': 0.0},
            'joint_arm_l0': {'current': 0.0},
            'joint_arm_l1': {'current': 0.0},
            'joint_arm_l2': {'current': 0.0},
            'joint_arm_l3': {'current': 0.0},
            'joint_wrist_yaw': {'current': 0.0},
            'joint_wrist_pitch': {'current': 0.0},
            'joint_wrist_roll': {'current': 0.0},
            'joint_gripper_finger_left': {'current': 0.0},
            'joint_gripper_finger_right': {'current': 0.0},
            'joint_head_pan': {'current': 0.0},
            'joint_head_tilt': {'current': 0.0},
        }
        
        # Wheel joints
        self.wheel_positions = {'joint_left_wheel': 0.0, 'joint_right_wheel': 0.0}
        
        # Movement
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        
        # Current world
        self.current_world = "empty"
        self.worlds = ["empty", "office", "warehouse", "home", "maze", "garden", "factory"]
        
        self.root = None
        
        # Timer
        self.timer = self.create_timer(0.05, self.update_robot)
        
        print("✅ Simple world drive initialized")
    
    def setup_gui(self):
        """Setup minimal GUI"""
        self.root = tk.Tk()
        self.root.title("🌍 Simple World Drive")
        self.root.geometry("500x600")
        self.root.configure(bg='#2b2b2b')
        
        # Title
        tk.Label(self.root, text="🌍 Simple World Drive", 
                font=('Arial', 16, 'bold'), fg='white', bg='#2b2b2b').pack(pady=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready!",
                                   fg='#00ff00', bg='#2b2b2b', font=('Arial', 12))
        self.status_label.pack(pady=5)
        
        # Position
        self.position_label = tk.Label(self.root, text="📍 Position: (0.0, 0.0)",
                                     fg='#ffff00', bg='#2b2b2b', font=('Arial', 11))
        self.position_label.pack(pady=5)
        
        # World selection
        world_frame = tk.Frame(self.root, bg='#3d3d3d', relief='raised', bd=2)
        world_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(world_frame, text="🌍 World", font=('Arial', 12, 'bold'), 
                fg='white', bg='#3d3d3d').pack(pady=5)
        
        # World buttons
        world_grid = tk.Frame(world_frame, bg='#3d3d3d')
        world_grid.pack(pady=5)
        
        worlds = ["empty", "office", "warehouse", "home", "maze", "garden", "factory"]
        colors = ["#607D8B", "#3F51B5", "#FF9800", "#4CAF50", "#9C27B0", "#2E7D32", "#795548"]
        
        for i, (world, color) in enumerate(zip(worlds, colors)):
            row, col = i // 3, i % 3
            
            if col == 0:
                row_frame = tk.Frame(world_grid, bg='#3d3d3d')
                row_frame.pack(pady=2)
            
            btn = tk.Button(row_frame, text=world.title(), 
                          command=lambda w=world: self.switch_world(w),
                          bg=color, fg='white', font=('Arial', 9), width=8)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Speed control
        speed_frame = tk.Frame(self.root, bg='#3d3d3d', relief='raised', bd=2)
        speed_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(speed_frame, text="⚡ Speed", font=('Arial', 12, 'bold'), 
                fg='white', bg='#3d3d3d').pack(pady=5)
        
        self.speed_scale = tk.Scale(speed_frame, from_=0.1, to=1.0, resolution=0.1,
                                  orient=tk.HORIZONTAL, length=250, bg='#3d3d3d', fg='white')
        self.speed_scale.set(0.5)
        self.speed_scale.pack(pady=5)
        
        # Drive controls
        drive_frame = tk.Frame(self.root, bg='#3d3d3d', relief='raised', bd=2)
        drive_frame.pack(pady=10, padx=20)
        
        tk.Label(drive_frame, text="🚗 Drive", font=('Arial', 12, 'bold'), 
                fg='white', bg='#3d3d3d').pack(pady=5)
        
        # Drive buttons
        drive_grid = tk.Frame(drive_frame, bg='#3d3d3d')
        drive_grid.pack(pady=10)
        
        # Forward
        tk.Button(drive_grid, text="⬆️", command=self.drive_forward,
                 bg='#4CAF50', fg='white', font=('Arial', 20), 
                 width=3, height=1).grid(row=0, column=1, padx=5, pady=5)
        
        # Left, Stop, Right  
        tk.Button(drive_grid, text="⬅️", command=self.drive_left,
                 bg='#2196F3', fg='white', font=('Arial', 20), 
                 width=3, height=1).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(drive_grid, text="🛑", command=self.drive_stop,
                 bg='#F44336', fg='white', font=('Arial', 20), 
                 width=3, height=1).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(drive_grid, text="➡️", command=self.drive_right,
                 bg='#2196F3', fg='white', font=('Arial', 20), 
                 width=3, height=1).grid(row=1, column=2, padx=5, pady=5)
        
        # Backward
        tk.Button(drive_grid, text="⬇️", command=self.drive_backward,
                 bg='#FF9800', fg='white', font=('Arial', 20), 
                 width=3, height=1).grid(row=2, column=1, padx=5, pady=5)
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#2b2b2b')
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="🏠 Home", command=self.go_home,
                 bg='#4CAF50', fg='white', font=('Arial', 10), 
                 width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="📍 Reset", command=self.reset_position,
                 bg='#607D8B', fg='white', font=('Arial', 10), 
                 width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="🎯 Demo", command=self.demo_drive,
                 bg='#E91E63', fg='white', font=('Arial', 10), 
                 width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="🔄 Start Env", command=self.start_env,
                 bg='#9C27B0', fg='white', font=('Arial', 10), 
                 width=8).pack(side=tk.LEFT, padx=5)
        
        print("✅ Simple GUI ready")
    
    def switch_world(self, world_name):
        """Switch world"""
        self.current_world = world_name
        self.status_label.config(text=f"🌍 Switched to {world_name}")
        
        # Send world command
        try:
            cmd = f'timeout 2s bash -c "source /opt/ros/humble/setup.bash && ros2 topic pub --once /world_command std_msgs/String \\"data: {world_name}\\""'
            subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass
    
    def start_env(self):
        """Start environment"""
        try:
            subprocess.Popen('python3 /home/kantar/Desktop/hello-robot/world_environments.py &', shell=True)
            self.status_label.config(text="🔄 Started environment")
            time.sleep(1)
            self.switch_world(self.current_world)
        except Exception as e:
            print(f"Failed to start env: {e}")
    
    # Drive methods
    def drive_forward(self):
        self.linear_speed = self.speed_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.status_label.config(text="⬆️ Forward")
    
    def drive_backward(self):
        self.linear_speed = -self.speed_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.status_label.config(text="⬇️ Backward")
    
    def drive_left(self):
        self.linear_speed = 0.0
        self.angular_speed = self.speed_scale.get()
        self.is_moving = True
        self.status_label.config(text="⬅️ Left")
    
    def drive_right(self):
        self.linear_speed = 0.0
        self.angular_speed = -self.speed_scale.get()
        self.is_moving = True
        self.status_label.config(text="➡️ Right")
    
    def drive_stop(self):
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        self.status_label.config(text="🛑 Stop")
    
    def go_home(self):
        for joint_name in self.joints:
            self.joints[joint_name]['current'] = 0.0
        self.drive_stop()
        self.status_label.config(text="🏠 Home")
    
    def reset_position(self):
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_theta = 0.0
        self.wheel_positions = {'joint_left_wheel': 0.0, 'joint_right_wheel': 0.0}
        self.drive_stop()
        self.status_label.config(text="📍 Reset")
    
    def demo_drive(self):
        """Simple demo"""
        self.status_label.config(text="🎯 Demo...")
        
        def demo():
            moves = [(0.3, 0.0, 1), (0.0, -1.57, 1), (0.3, 0.0, 1), (0.0, -1.57, 1)]
            for linear, angular, duration in moves:
                self.linear_speed = linear
                self.angular_speed = angular
                self.is_moving = True
                time.sleep(duration)
            self.drive_stop()
        
        threading.Thread(target=demo, daemon=True).start()
    
    def update_robot(self):
        """Update robot"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        if self.is_moving:
            self.robot_x += self.linear_speed * math.cos(self.robot_theta) * dt
            self.robot_y += self.linear_speed * math.sin(self.robot_theta) * dt
            self.robot_theta += self.angular_speed * dt
            
            left_speed = self.linear_speed - (self.angular_speed * self.wheel_base / 2.0)
            right_speed = self.linear_speed + (self.angular_speed * self.wheel_base / 2.0)
            
            self.wheel_positions['joint_left_wheel'] += (left_speed / self.wheel_radius) * dt
            self.wheel_positions['joint_right_wheel'] += (right_speed / self.wheel_radius) * dt
        
        if hasattr(self, 'position_label'):
            self.position_label.config(
                text=f"📍 Position: ({self.robot_x:.1f}, {self.robot_y:.1f}) θ={math.degrees(self.robot_theta):.0f}°"
            )
        
        self.publish_transforms()
        self.publish_joint_states()
    
    def publish_transforms(self):
        """Publish transforms"""
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
        
        names = list(self.joints.keys()) + ['joint_left_wheel', 'joint_right_wheel']
        positions = [self.joints[n]['current'] for n in self.joints.keys()]
        positions.extend([self.wheel_positions['joint_left_wheel'], self.wheel_positions['joint_right_wheel']])
        
        msg.name = names
        msg.position = positions
        msg.velocity = [0.0] * len(names)
        msg.effort = [0.0] * len(names)
        
        self.joint_pub.publish(msg)
    
    def run_gui(self):
        """Run GUI"""
        if self.root:
            self.root.mainloop()

def signal_handler(sig, frame):
    print("\nShutting down...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    rclpy.init()
    
    try:
        print("🚀 Starting simple world drive...")
        controller = SimpleWorldDrive()
        
        # Setup GUI
        controller.setup_gui()
        
        # ROS2 thread
        def spin_ros():
            rclpy.spin(controller)
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        time.sleep(0.2)
        print("🎮 GUI starting...")
        
        controller.run_gui()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
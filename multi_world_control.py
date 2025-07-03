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

class MultiWorldStretchControl(Node):
    def __init__(self):
        super().__init__('multi_world_stretch_control')
        
        # Publishers
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.world_cmd_pub = self.create_publisher(String, '/world_command', 10)
        
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
        self.worlds = {
            "empty": "🌫️ Empty World",
            "office": "🏢 Office Environment", 
            "warehouse": "📦 Warehouse",
            "home": "🏠 Home Environment",
            "maze": "🧩 Maze Challenge",
            "garden": "🌳 Garden Park",
            "factory": "🏭 Factory Floor"
        }
        
        self.current_world = "empty"
        self.world_process = None
        
        self.sliders = {}
        self.root = None
        
        # Timer for updates
        self.timer = self.create_timer(0.05, self.update_robot)
        
        print("✅ Multi-world stretch control initialized")
    
    def setup_gui(self):
        """Setup the GUI with world selection"""
        self.root = tk.Tk()
        self.root.title("🌍 Stretch Robot - Multi-World Control")
        self.root.geometry("800x1000")
        self.root.configure(bg='#0a0a0a')
        
        # Title
        title = tk.Label(self.root, text="🌍 Stretch Robot - Multi-World Control", 
                        font=('Arial', 20, 'bold'), fg='#00ff00', bg='#0a0a0a')
        title.pack(pady=15)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready to explore worlds!",
                                   fg='#00ff00', bg='#0a0a0a', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        # Position display
        self.position_label = tk.Label(self.root, text="📍 Position: (0.0, 0.0) θ=0.0°",
                                     fg='#ffff00', bg='#0a0a0a', font=('Arial', 11))
        self.position_label.pack(pady=5)
        
        # World selection
        self.create_world_selection()
        
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#0a0a0a')
        style.configure('TNotebook.Tab', background='#333333', foreground='white')
        
        notebook = ttk.Notebook(self.root)
        
        # World info tab
        world_frame = tk.Frame(notebook, bg='#0a0a0a')
        notebook.add(world_frame, text="🌍 Worlds")
        self.create_world_info_tab(world_frame)
        
        # Driving tab
        drive_frame = tk.Frame(notebook, bg='#0a0a0a')
        notebook.add(drive_frame, text="🚗 Drive")
        self.create_drive_tab(drive_frame)
        
        # Joint control tab
        joint_frame = tk.Frame(notebook, bg='#0a0a0a')
        notebook.add(joint_frame, text="🦾 Joints")
        self.create_joint_tab(joint_frame)
        
        notebook.pack(expand=True, fill='both', padx=15, pady=10)
        
        # Control buttons
        self.create_control_buttons()
        
        print("✅ GUI setup complete")
    
    def create_world_selection(self):
        """Create world selection interface"""
        world_frame = tk.Frame(self.root, bg='#1a1a1a', relief='raised', bd=2)
        world_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(world_frame, text="🌍 Select World Environment", 
                font=('Arial', 14, 'bold'), fg='white', bg='#1a1a1a').pack(pady=10)
        
        # World selection dropdown
        selection_frame = tk.Frame(world_frame, bg='#1a1a1a')
        selection_frame.pack(pady=10)
        
        tk.Label(selection_frame, text="Current World:", 
                font=('Arial', 12), fg='white', bg='#1a1a1a').pack(side=tk.LEFT, padx=10)
        
        self.world_var = tk.StringVar(value=self.worlds[self.current_world])
        world_dropdown = ttk.Combobox(selection_frame, textvariable=self.world_var,
                                    values=list(self.worlds.values()), state="readonly",
                                    font=('Arial', 11), width=25)
        world_dropdown.pack(side=tk.LEFT, padx=10)
        world_dropdown.bind('<<ComboboxSelected>>', self.on_world_change)
        
        # Quick world buttons
        quick_frame = tk.Frame(world_frame, bg='#1a1a1a')
        quick_frame.pack(pady=10)
        
        world_buttons = [
            ("🏢 Office", "office", "#3f51b5"),
            ("📦 Warehouse", "warehouse", "#ff9800"), 
            ("🏠 Home", "home", "#4caf50"),
            ("🧩 Maze", "maze", "#9c27b0"),
            ("🌳 Garden", "garden", "#2e7d32"),
            ("🏭 Factory", "factory", "#607d8b")
        ]
        
        for i, (text, world_key, color) in enumerate(world_buttons):
            if i % 3 == 0:
                row_frame = tk.Frame(quick_frame, bg='#1a1a1a')
                row_frame.pack(pady=2)
            
            btn = tk.Button(row_frame, text=text, 
                          command=lambda w=world_key: self.switch_world(w),
                          bg=color, fg='white', font=('Arial', 10, 'bold'),
                          width=12, height=1)
            btn.pack(side=tk.LEFT, padx=2)
    
    def create_world_info_tab(self, parent):
        """Create world information tab"""
        info_frame = tk.Frame(parent, bg='#0a0a0a')
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Current world info
        self.world_info_label = tk.Label(info_frame, 
                                        text=f"Current World: {self.worlds[self.current_world]}",
                                        font=('Arial', 14, 'bold'), fg='#00ff00', bg='#0a0a0a')
        self.world_info_label.pack(pady=10)
        
        # World descriptions
        descriptions = {
            "empty": "A clean empty space perfect for testing basic robot movements and getting familiar with controls.",
            "office": "Navigate through a typical office environment with desks, chairs, and cubicle walls. Practice precision movement in tight spaces.",
            "warehouse": "Maneuver around storage racks and boxes in a warehouse setting. Great for practicing navigation around obstacles.",
            "home": "Explore a home environment with living room, kitchen, and furniture. Perfect for domestic robot scenarios.",
            "maze": "Challenge your navigation skills in a complex maze. Find the green goal marker while avoiding walls!",
            "garden": "A peaceful outdoor environment with trees, flower beds, and winding paths. Enjoy nature while driving.",
            "factory": "Industrial environment with machines, conveyor belts, and control panels. Experience a working factory floor."
        }
        
        self.description_label = tk.Label(info_frame, 
                                        text=descriptions[self.current_world],
                                        font=('Arial', 11), fg='white', bg='#0a0a0a',
                                        wraplength=600, justify='left')
        self.description_label.pack(pady=10)
        
        # World features
        features_frame = tk.Frame(info_frame, bg='#2d2d2d', relief='raised', bd=2)
        features_frame.pack(pady=20, fill='x')
        
        tk.Label(features_frame, text="🎯 World Features", 
                font=('Arial', 12, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        features = {
            "empty": ["• Open space for free movement", "• Grid floor for reference", "• No obstacles"],
            "office": ["• Desks and office furniture", "• Cubicle walls", "• Realistic office layout"],
            "warehouse": ["• Storage racks", "• Stacked boxes", "• Industrial environment"],
            "home": ["• Living room with sofa", "• Kitchen area", "• Realistic home furniture"],
            "maze": ["• Complex wall layout", "• Navigation challenge", "• Goal-finding mission"],
            "garden": ["• Trees and vegetation", "• Flower beds", "• Winding garden paths"],
            "factory": ["• Industrial machines", "• Conveyor belts", "• Factory equipment"]
        }
        
        self.features_label = tk.Label(features_frame, 
                                     text="\n".join(features[self.current_world]),
                                     font=('Arial', 10), fg='white', bg='#2d2d2d',
                                     justify='left')
        self.features_label.pack(pady=10)
        
        # Mission suggestions
        missions_frame = tk.Frame(info_frame, bg='#3d2d2d', relief='raised', bd=2)
        missions_frame.pack(pady=20, fill='x')
        
        tk.Label(missions_frame, text="🎮 Suggested Missions", 
                font=('Arial', 12, 'bold'), fg='white', bg='#3d2d2d').pack(pady=10)
        
        missions = {
            "empty": ["• Practice basic movement", "• Test all joint controls", "• Try the demo drive"],
            "office": ["• Navigate to each desk", "• Move between cubicles", "• Practice tight turns"],
            "warehouse": ["• Visit each storage rack", "• Navigate around boxes", "• Find optimal paths"],
            "home": ["• Tour each room", "• Approach furniture safely", "• Practice home service tasks"],
            "maze": ["• Find the green goal", "• Map the maze layout", "• Time your navigation"],
            "garden": ["• Follow the garden path", "• Visit each tree", "• Enjoy the scenery"],
            "factory": ["• Inspect each machine", "• Follow conveyor routes", "• Avoid industrial hazards"]
        }
        
        self.missions_label = tk.Label(missions_frame, 
                                     text="\n".join(missions[self.current_world]),
                                     font=('Arial', 10), fg='white', bg='#3d2d2d',
                                     justify='left')
        self.missions_label.pack(pady=10)
    
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
        
        self.linear_scale = tk.Scale(linear_frame, from_=0.0, to=1.5, resolution=0.1,
                                   orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white')
        self.linear_scale.set(0.5)
        self.linear_scale.pack(side=tk.RIGHT, padx=10)
        
        # Angular speed
        angular_frame = tk.Frame(speed_frame, bg='#2d2d2d')
        angular_frame.pack(pady=5, fill='x', padx=10)
        
        tk.Label(angular_frame, text="Turn Speed (rad/s):", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.angular_scale = tk.Scale(angular_frame, from_=0.0, to=2.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white')
        self.angular_scale.set(1.0)
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
            'font': ('Arial', 16, 'bold'), 
            'fg': 'white', 
            'width': 6, 
            'height': 2,
            'relief': 'raised',
            'bd': 3
        }
        
        # Drive buttons
        tk.Button(button_grid, text="⬆️\nForward", bg='#4CAF50', **btn_style,
                 command=self.drive_forward).grid(row=0, column=1, padx=8, pady=8)
        
        tk.Button(button_grid, text="⬅️\nLeft", bg='#2196F3', **btn_style,
                 command=self.drive_left).grid(row=1, column=0, padx=8, pady=8)
        
        tk.Button(button_grid, text="🛑\nSTOP", bg='#F44336', **btn_style,
                 command=self.drive_stop).grid(row=1, column=1, padx=8, pady=8)
        
        tk.Button(button_grid, text="➡️\nRight", bg='#2196F3', **btn_style,
                 command=self.drive_right).grid(row=1, column=2, padx=8, pady=8)
        
        tk.Button(button_grid, text="⬇️\nBackward", bg='#FF9800', **btn_style,
                 command=self.drive_backward).grid(row=2, column=1, padx=8, pady=8)
    
    def create_joint_tab(self, parent):
        """Create joint control tab"""
        canvas = tk.Canvas(parent, bg='#0a0a0a', highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0a0a0a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for joint_name in self.joints:
            self.create_joint_control(scrollable_frame, joint_name)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def create_joint_control(self, parent, joint_name):
        """Create control for one joint"""
        joint_info = self.joints[joint_name]
        
        frame = tk.Frame(parent, bg='#3d3d3d', relief='raised', bd=2)
        frame.pack(fill='x', padx=5, pady=5)
        
        header = tk.Frame(frame, bg='#3d3d3d')
        header.pack(fill='x', padx=8, pady=5)
        
        name_label = tk.Label(header, 
                            text=joint_name.replace('joint_', '').replace('_', ' ').title(),
                            font=('Arial', 11, 'bold'), bg='#3d3d3d', fg='white')
        name_label.pack(side=tk.LEFT)
        
        value_label = tk.Label(header, text=f"{joint_info['current']:.3f}",
                             font=('Arial', 11, 'bold'), bg='#3d3d3d', fg='#00ff00')
        value_label.pack(side=tk.RIGHT)
        
        slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                        resolution=0.01, orient=tk.HORIZONTAL, length=400,
                        bg='#3d3d3d', fg='white', activebackground='#555555',
                        command=lambda val, jname=joint_name, vlabel=value_label: 
                               self.update_joint(jname, val, vlabel))
        slider.pack(fill='x', padx=8, pady=5)
        slider.set(joint_info['current'])
        
        self.sliders[joint_name] = slider
    
    def create_control_buttons(self):
        """Create control buttons"""
        button_frame = tk.Frame(self.root, bg='#0a0a0a')
        button_frame.pack(pady=15)
        
        buttons = [
            ("🏠 Home", self.go_home, "#4CAF50"),
            ("🎯 Demo Drive", self.demo_drive, "#E91E63"), 
            ("📍 Reset Position", self.reset_position, "#607D8B"),
            ("🔄 Reload World", self.reload_world, "#9C27B0")
        ]
        
        for text, command, color in buttons:
            tk.Button(button_frame, text=text, command=command,
                     bg=color, fg='white', font=('Arial', 11, 'bold'), 
                     width=15, height=2).pack(side=tk.LEFT, padx=5)
    
    def on_world_change(self, event):
        """Handle world selection change"""
        selected_world_name = self.world_var.get()
        for key, name in self.worlds.items():
            if name == selected_world_name:
                self.switch_world(key)
                break
    
    def switch_world(self, world_name):
        """Switch to a different world"""
        if world_name in self.worlds:
            self.current_world = world_name
            self.world_var.set(self.worlds[world_name])
            self.status_label.config(text=f"🌍 Switched to {self.worlds[world_name]}")
            
            # Update world info tab
            self.world_info_label.config(text=f"Current World: {self.worlds[world_name]}")
            self.update_world_info()
            
            # Start world environment node
            self.start_world_environment()
            
            print(f"🌍 Switched to {world_name} world")
    
    def update_world_info(self):
        """Update world information display"""
        descriptions = {
            "empty": "A clean empty space perfect for testing basic robot movements and getting familiar with controls.",
            "office": "Navigate through a typical office environment with desks, chairs, and cubicle walls. Practice precision movement in tight spaces.",
            "warehouse": "Maneuver around storage racks and boxes in a warehouse setting. Great for practicing navigation around obstacles.",
            "home": "Explore a home environment with living room, kitchen, and furniture. Perfect for domestic robot scenarios.",
            "maze": "Challenge your navigation skills in a complex maze. Find the green goal marker while avoiding walls!",
            "garden": "A peaceful outdoor environment with trees, flower beds, and winding paths. Enjoy nature while driving.",
            "factory": "Industrial environment with machines, conveyor belts, and control panels. Experience a working factory floor."
        }
        
        features = {
            "empty": ["• Open space for free movement", "• Grid floor for reference", "• No obstacles"],
            "office": ["• Desks and office furniture", "• Cubicle walls", "• Realistic office layout"],
            "warehouse": ["• Storage racks", "• Stacked boxes", "• Industrial environment"],
            "home": ["• Living room with sofa", "• Kitchen area", "• Realistic home furniture"],
            "maze": ["• Complex wall layout", "• Navigation challenge", "• Goal-finding mission"],
            "garden": ["• Trees and vegetation", "• Flower beds", "• Winding garden paths"],
            "factory": ["• Industrial machines", "• Conveyor belts", "• Factory equipment"]
        }
        
        missions = {
            "empty": ["• Practice basic movement", "• Test all joint controls", "• Try the demo drive"],
            "office": ["• Navigate to each desk", "• Move between cubicles", "• Practice tight turns"],
            "warehouse": ["• Visit each storage rack", "• Navigate around boxes", "• Find optimal paths"],
            "home": ["• Tour each room", "• Approach furniture safely", "• Practice home service tasks"],
            "maze": ["• Find the green goal", "• Map the maze layout", "• Time your navigation"],
            "garden": ["• Follow the garden path", "• Visit each tree", "• Enjoy the scenery"],
            "factory": ["• Inspect each machine", "• Follow conveyor routes", "• Avoid industrial hazards"]
        }
        
        self.description_label.config(text=descriptions[self.current_world])
        self.features_label.config(text="\n".join(features[self.current_world]))
        self.missions_label.config(text="\n".join(missions[self.current_world]))
    
    def start_world_environment(self):
        """Start the world environment node"""
        try:
            # Kill existing world process
            if self.world_process:
                self.world_process.terminate()
                self.world_process.wait()
            
            # Start new world environment
            cmd = f'python3 /home/kantar/Desktop/hello-robot/world_environments.py'
            self.world_process = subprocess.Popen(cmd, shell=True)
            
            # Send world change command
            time.sleep(0.5)  # Give it time to start
            self.send_world_command(self.current_world)
            
        except Exception as e:
            print(f"Failed to start world environment: {e}")
    
    def send_world_command(self, world_name):
        """Send command to change world"""
        try:
            subprocess.run([
                'bash', '-c', 
                f'source /opt/ros/humble/setup.bash && ros2 topic pub --once /world_command std_msgs/String "data: \'{world_name}\'"'
            ], check=True, capture_output=True)
        except:
            pass
    
    def reload_world(self):
        """Reload the current world"""
        self.start_world_environment()
        self.status_label.config(text=f"🔄 Reloaded {self.worlds[self.current_world]}")
    
    # Movement methods (same as before)
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
        self.status_label.config(text="📍 Position reset to origin")
    
    def demo_drive(self):
        """Demonstrate driving based on current world"""
        patterns = {
            "empty": self.demo_square_pattern,
            "office": self.demo_office_tour,
            "warehouse": self.demo_warehouse_nav,
            "home": self.demo_home_tour,
            "maze": self.demo_maze_exploration,
            "garden": self.demo_garden_stroll,
            "factory": self.demo_factory_inspection
        }
        
        if self.current_world in patterns:
            self.status_label.config(text=f"🎯 Demo drive in {self.worlds[self.current_world]}...")
            threading.Thread(target=patterns[self.current_world], daemon=True).start()
    
    def demo_square_pattern(self):
        """Square driving pattern for empty world"""
        moves = [(0.3, 0.0, 2), (0.0, -1.57, 1), (0.3, 0.0, 2), (0.0, -1.57, 1), 
                 (0.3, 0.0, 2), (0.0, -1.57, 1), (0.3, 0.0, 2), (0.0, -1.57, 1)]
        for linear, angular, duration in moves:
            self.linear_speed = linear
            self.angular_speed = angular
            self.is_moving = True
            time.sleep(duration)
        self.drive_stop()
    
    def demo_office_tour(self):
        """Office navigation demo"""
        moves = [(0.2, 0.0, 2), (0.0, 1.57, 1), (0.2, 0.0, 1.5), 
                 (0.0, -1.57, 1), (0.2, 0.0, 2), (0.0, 1.57, 1)]
        for linear, angular, duration in moves:
            self.linear_speed = linear
            self.angular_speed = angular
            self.is_moving = True
            time.sleep(duration)
        self.drive_stop()
    
    def demo_warehouse_nav(self):
        """Warehouse navigation demo"""
        moves = [(0.3, 0.0, 1), (0.0, 0.5, 2), (0.3, 0.0, 1), 
                 (0.0, -0.5, 2), (0.3, 0.0, 1)]
        for linear, angular, duration in moves:
            self.linear_speed = linear
            self.angular_speed = angular
            self.is_moving = True
            time.sleep(duration)
        self.drive_stop()
    
    def demo_home_tour(self):
        """Home tour demo"""
        moves = [(0.15, 0.0, 2), (0.0, 0.8, 1.5), (0.15, 0.0, 1.5), 
                 (0.0, -0.8, 1.5), (0.15, 0.0, 2)]
        for linear, angular, duration in moves:
            self.linear_speed = linear
            self.angular_speed = angular
            self.is_moving = True
            time.sleep(duration)
        self.drive_stop()
    
    def demo_maze_exploration(self):
        """Maze exploration demo"""
        moves = [(0.2, 0.0, 1), (0.0, 1.57, 1), (0.2, 0.0, 0.5), 
                 (0.0, -1.57, 1), (0.2, 0.0, 1), (0.0, 1.57, 1)]
        for linear, angular, duration in moves:
            self.linear_speed = linear
            self.angular_speed = angular
            self.is_moving = True
            time.sleep(duration)
        self.drive_stop()
    
    def demo_garden_stroll(self):
        """Garden stroll demo"""
        moves = [(0.1, 0.2, 3), (0.1, -0.2, 3), (0.1, 0.2, 3), 
                 (0.1, -0.2, 3)]  # Gentle curves
        for linear, angular, duration in moves:
            self.linear_speed = linear
            self.angular_speed = angular
            self.is_moving = True
            time.sleep(duration)
        self.drive_stop()
    
    def demo_factory_inspection(self):
        """Factory inspection demo"""
        moves = [(0.25, 0.0, 2), (0.0, 1.57, 1), (0.25, 0.0, 1), 
                 (0.0, 1.57, 1), (0.25, 0.0, 2)]
        for linear, angular, duration in moves:
            self.linear_speed = linear
            self.angular_speed = angular
            self.is_moving = True
            time.sleep(duration)
        self.drive_stop()
    
    def update_joint(self, joint_name, value, value_label):
        self.joints[joint_name]['current'] = float(value)
        value_label.config(text=f"{float(value):.3f}")
    
    def update_robot(self):
        """Update robot state and publish transforms"""
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
            finally:
                if self.world_process:
                    self.world_process.terminate()

def signal_handler(sig, frame):
    print("\nShutting down...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    rclpy.init()
    
    controller = None
    try:
        controller = MultiWorldStretchControl()
        controller.setup_gui()
        
        def spin_ros():
            try:
                rclpy.spin(controller)
            except:
                pass
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        print("🌍 Multi-world control GUI starting...")
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
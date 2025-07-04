#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import tkinter as tk
from tkinter import ttk
import threading
import time
import signal
import sys
import math

class StretchPickPlaceControl(Node):
    def __init__(self):
        super().__init__('stretch_pick_place_control')
        
        # Publishers
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Robot state
        self.robot_x = -3.0  # Start away from table
        self.robot_y = 2.0
        self.robot_theta = 0.0
        self.last_time = time.time()
        
        # Wheel parameters
        self.wheel_base = 0.33  # Distance between wheels (meters)
        self.wheel_radius = 0.05  # Wheel radius (meters)
        
        # Joint definitions with pick and place optimized ranges
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
        
        # Pick and place states
        self.pick_place_state = "idle"
        self.target_object = "glass"
        
        # Predefined poses for pick and place
        self.poses = {
            'home': {
                'joint_lift': 0.2,
                'arm_extension': 0.0,
                'joint_wrist_yaw': 0.0,
                'joint_wrist_pitch': 0.0,
                'joint_wrist_roll': 0.0,
                'gripper_open': 0.0,
            },
            'approach_table': {
                'joint_lift': 0.6,  # Raise to table height
                'arm_extension': 0.3,  # Extend arm
                'joint_wrist_yaw': 0.0,
                'joint_wrist_pitch': -0.2,  # Point down slightly
                'joint_wrist_roll': 0.0,
                'gripper_open': 0.08,  # Open gripper
            },
            'grasp_glass': {
                'joint_lift': 0.67,  # Table height + glass height
                'arm_extension': 0.4,  # Reach over table
                'joint_wrist_yaw': 0.0,
                'joint_wrist_pitch': -0.1,
                'joint_wrist_roll': 0.0,
                'gripper_open': 0.02,  # Close around glass
            },
            'lift_glass': {
                'joint_lift': 0.85,  # Lift glass up
                'arm_extension': 0.4,
                'joint_wrist_yaw': 0.0,
                'joint_wrist_pitch': 0.0,
                'joint_wrist_roll': 0.0,
                'gripper_open': 0.02,  # Keep gripping
            },
            'transport': {
                'joint_lift': 0.8,  # Safe transport height
                'arm_extension': 0.2,  # Bring closer to body
                'joint_wrist_yaw': 0.0,
                'joint_wrist_pitch': 0.0,
                'joint_wrist_roll': 0.0,
                'gripper_open': 0.02,
            },
            'place_position': {
                'joint_lift': 0.7,  # Lower to place
                'arm_extension': 0.35,
                'joint_wrist_yaw': 0.0,
                'joint_wrist_pitch': -0.1,
                'joint_wrist_roll': 0.0,
                'gripper_open': 0.02,
            },
            'release': {
                'joint_lift': 0.7,
                'arm_extension': 0.35,
                'joint_wrist_yaw': 0.0,
                'joint_wrist_pitch': -0.1,
                'joint_wrist_roll': 0.0,
                'gripper_open': 0.08,  # Release object
            }
        }
        
        self.sliders = {}
        self.root = None
        
        # Timer for publishing
        self.timer = self.create_timer(0.05, self.update_robot)  # 20Hz
        
        print("✅ Stretch pick and place control initialized")
    
    def setup_gui(self):
        """Setup the GUI with pick and place controls"""
        self.root = tk.Tk()
        self.root.title("🤖 Stretch Robot - Pick & Place Control")
        self.root.geometry("800x1000")
        self.root.configure(bg='#1a1a1a')
        
        # Title
        title = tk.Label(self.root, text="🤖 Stretch Robot - Pick & Place Control", 
                        font=('Arial', 18, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=15)
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Ready for pick and place operations!",
                                   fg='#00ff00', bg='#1a1a1a', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        # Position display
        self.position_label = tk.Label(self.root, text="📍 Position: (-3.0, 2.0) θ=0.0°",
                                     fg='#ffff00', bg='#1a1a1a', font=('Arial', 11))
        self.position_label.pack(pady=5)
        
        # State display
        self.state_label = tk.Label(self.root, text="🔄 State: idle",
                                   fg='#ff8800', bg='#1a1a1a', font=('Arial', 11, 'bold'))
        self.state_label.pack(pady=5)
        
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a')
        style.configure('TNotebook.Tab', background='#333333', foreground='white')
        
        notebook = ttk.Notebook(self.root)
        
        # Pick and place tab
        pick_place_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(pick_place_frame, text="🎯 Pick & Place")
        self.create_pick_place_tab(pick_place_frame)
        
        # Navigation tab
        nav_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(nav_frame, text="🚗 Navigation")
        self.create_navigation_tab(nav_frame)
        
        # Manual control tab
        manual_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(manual_frame, text="🎮 Manual")
        self.create_manual_tab(manual_frame)
        
        notebook.pack(expand=True, fill='both', padx=15, pady=10)
        
        # Emergency stop
        self.create_emergency_controls()
        
        print("✅ GUI setup complete")
    
    def create_pick_place_tab(self, parent):
        """Create the pick and place interface"""
        # Mission control
        mission_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        mission_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(mission_frame, text="🎯 Pick & Place Mission Control", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        # Object selection
        obj_frame = tk.Frame(mission_frame, bg='#2d2d2d')
        obj_frame.pack(pady=10, fill='x', padx=10)
        
        tk.Label(obj_frame, text="Target Object:", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.object_var = tk.StringVar(value="glass")
        object_combo = ttk.Combobox(obj_frame, textvariable=self.object_var, 
                                   values=["glass", "small_box", "small_cylinder"], 
                                   state="readonly", width=15)
        object_combo.pack(side=tk.LEFT, padx=10)
        
        # Automated sequences
        sequence_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        sequence_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(sequence_frame, text="🤖 Automated Sequences", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        btn_grid = tk.Frame(sequence_frame, bg='#2d2d2d')
        btn_grid.pack(pady=15)
        
        btn_style = {
            'font': ('Arial', 12, 'bold'), 
            'fg': 'white', 
            'width': 18, 
            'height': 2,
            'relief': 'raised',
            'bd': 3
        }
        
        # Row 1
        tk.Button(btn_grid, text="🎯 Full Pick & Place", bg='#4CAF50', **btn_style,
                 command=self.full_pick_place_sequence).grid(row=0, column=0, padx=5, pady=5)
        
        tk.Button(btn_grid, text="🚗 Navigate to Table", bg='#2196F3', **btn_style,
                 command=self.navigate_to_table).grid(row=0, column=1, padx=5, pady=5)
        
        # Row 2
        tk.Button(btn_grid, text="🦾 Prepare to Grasp", bg='#FF9800', **btn_style,
                 command=self.prepare_to_grasp).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(btn_grid, text="🤏 Pick Up Object", bg='#9C27B0', **btn_style,
                 command=self.pick_up_object).grid(row=1, column=1, padx=5, pady=5)
        
        # Row 3
        tk.Button(btn_grid, text="📦 Place Object", bg='#607D8B', **btn_style,
                 command=self.place_object).grid(row=2, column=0, padx=5, pady=5)
        
        tk.Button(btn_grid, text="🏠 Return Home", bg='#795548', **btn_style,
                 command=self.return_home).grid(row=2, column=1, padx=5, pady=5)
        
        # Individual pose controls
        pose_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        pose_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(pose_frame, text="🎭 Individual Poses", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        pose_grid = tk.Frame(pose_frame, bg='#2d2d2d')
        pose_grid.pack(pady=10)
        
        pose_btn_style = {
            'font': ('Arial', 10, 'bold'), 
            'fg': 'white', 
            'width': 12, 
            'height': 1,
            'relief': 'raised',
            'bd': 2
        }
        
        poses = [
            ("🏠 Home", "home", '#4CAF50'),
            ("🎯 Approach", "approach_table", '#2196F3'),
            ("🤏 Grasp", "grasp_glass", '#FF9800'),
            ("⬆️ Lift", "lift_glass", '#9C27B0'),
            ("🚚 Transport", "transport", '#607D8B'),
            ("📦 Place", "place_position", '#795548'),
            ("🔓 Release", "release", '#E91E63')
        ]
        
        for i, (text, pose_name, color) in enumerate(poses):
            row = i // 4
            col = i % 4
            tk.Button(pose_grid, text=text, bg=color, **pose_btn_style,
                     command=lambda p=pose_name: self.go_to_pose(p)).grid(row=row, column=col, padx=2, pady=2)
    
    def create_navigation_tab(self, parent):
        """Create navigation controls"""
        # Speed controls
        speed_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        speed_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(speed_frame, text="🏎️ Navigation Speed", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        # Linear speed
        linear_frame = tk.Frame(speed_frame, bg='#2d2d2d')
        linear_frame.pack(pady=5, fill='x', padx=10)
        
        tk.Label(linear_frame, text="Linear Speed:", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.linear_scale = tk.Scale(linear_frame, from_=0.0, to=0.5, resolution=0.05,
                                   orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white')
        self.linear_scale.set(0.2)
        self.linear_scale.pack(side=tk.RIGHT, padx=10)
        
        # Angular speed
        angular_frame = tk.Frame(speed_frame, bg='#2d2d2d')
        angular_frame.pack(pady=5, fill='x', padx=10)
        
        tk.Label(angular_frame, text="Turn Speed:", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.angular_scale = tk.Scale(angular_frame, from_=0.0, to=1.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white')
        self.angular_scale.set(0.5)
        self.angular_scale.pack(side=tk.RIGHT, padx=10)
        
        # Movement controls
        move_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        move_frame.pack(pady=15, padx=20)
        
        tk.Label(move_frame, text="🎮 Movement Controls", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        # Button grid
        button_grid = tk.Frame(move_frame, bg='#2d2d2d')
        button_grid.pack(pady=15)
        
        btn_style = {
            'font': ('Arial', 14, 'bold'), 
            'fg': 'white', 
            'width': 6, 
            'height': 2,
            'relief': 'raised',
            'bd': 3
        }
        
        # Movement buttons
        tk.Button(button_grid, text="⬆️", bg='#4CAF50', **btn_style,
                 command=self.drive_forward).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(button_grid, text="⬅️", bg='#2196F3', **btn_style,
                 command=self.drive_left).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(button_grid, text="🛑", bg='#F44336', **btn_style,
                 command=self.drive_stop).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(button_grid, text="➡️", bg='#2196F3', **btn_style,
                 command=self.drive_right).grid(row=1, column=2, padx=5, pady=5)
        
        tk.Button(button_grid, text="⬇️", bg='#FF9800', **btn_style,
                 command=self.drive_backward).grid(row=2, column=1, padx=5, pady=5)
        
        # Preset positions
        preset_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        preset_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(preset_frame, text="📍 Preset Positions", 
                font=('Arial', 14, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        preset_grid = tk.Frame(preset_frame, bg='#2d2d2d')
        preset_grid.pack(pady=10)
        
        preset_btn_style = {
            'font': ('Arial', 11, 'bold'), 
            'fg': 'white', 
            'width': 15, 
            'height': 2,
            'relief': 'raised',
            'bd': 2
        }
        
        tk.Button(preset_grid, text="🎯 Table Position", bg='#4CAF50', **preset_btn_style,
                 command=self.go_to_table_position).grid(row=0, column=0, padx=5, pady=5)
        
        tk.Button(preset_grid, text="🏠 Starting Position", bg='#2196F3', **preset_btn_style,
                 command=self.go_to_start_position).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(preset_grid, text="📦 Drop Zone", bg='#FF9800', **preset_btn_style,
                 command=self.go_to_drop_zone).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(preset_grid, text="🔄 Reset Position", bg='#607D8B', **preset_btn_style,
                 command=self.reset_position).grid(row=1, column=1, padx=5, pady=5)
    
    def create_manual_tab(self, parent):
        """Create manual joint control tab"""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add joint controls
        for joint_name in self.joints:
            self.create_joint_control(scrollable_frame, joint_name)
        
        # Gripper control
        self.create_gripper_control(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def create_joint_control(self, parent, joint_name):
        """Create control for one joint"""
        joint_info = self.joints[joint_name]
        
        frame = tk.Frame(parent, bg='#3d3d3d', relief='raised', bd=2)
        frame.pack(fill='x', padx=5, pady=5)
        
        # Header
        header = tk.Frame(frame, bg='#3d3d3d')
        header.pack(fill='x', padx=8, pady=5)
        
        name_label = tk.Label(header, 
                            text=joint_name.replace('joint_', '').replace('_', ' ').title(),
                            font=('Arial', 11, 'bold'), bg='#3d3d3d', fg='white')
        name_label.pack(side=tk.LEFT)
        
        value_label = tk.Label(header, text=f"{joint_info['current']:.3f}",
                             font=('Arial', 11, 'bold'), bg='#3d3d3d', fg='#00ff00')
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
                             font=('Arial', 9), bg='#3d3d3d', fg='#888888')
        range_label.pack(pady=2)
    
    def create_gripper_control(self, parent):
        """Create gripper control"""
        frame = tk.Frame(parent, bg='#3d3d3d', relief='raised', bd=2)
        frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(frame, text="🤏 Gripper Control", 
                font=('Arial', 12, 'bold'), fg='white', bg='#3d3d3d').pack(pady=10)
        
        btn_frame = tk.Frame(frame, bg='#3d3d3d')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔓 Open", bg='#4CAF50', fg='white',
                 font=('Arial', 10, 'bold'), width=8, height=2,
                 command=self.open_gripper).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🤏 Close", bg='#F44336', fg='white',
                 font=('Arial', 10, 'bold'), width=8, height=2,
                 command=self.close_gripper).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🎯 Grasp", bg='#FF9800', fg='white',
                 font=('Arial', 10, 'bold'), width=8, height=2,
                 command=self.grasp_object).pack(side=tk.LEFT, padx=5)
    
    def create_emergency_controls(self):
        """Create emergency stop controls"""
        emergency_frame = tk.Frame(self.root, bg='#1a1a1a')
        emergency_frame.pack(pady=10)
        
        tk.Button(emergency_frame, text="🚨 EMERGENCY STOP", 
                 command=self.emergency_stop, bg='#F44336', fg='white',
                 font=('Arial', 16, 'bold'), width=20, height=2).pack(pady=5)
        
        reset_frame = tk.Frame(emergency_frame, bg='#1a1a1a')
        reset_frame.pack(pady=5)
        
        tk.Button(reset_frame, text="🔄 Reset All", command=self.reset_all,
                 bg='#607D8B', fg='white', font=('Arial', 12, 'bold'), 
                 width=10, height=1).pack(side=tk.LEFT, padx=5)
        
        tk.Button(reset_frame, text="🏠 Home All", command=self.home_all,
                 bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'), 
                 width=10, height=1).pack(side=tk.LEFT, padx=5)
    
    # Movement methods
    def drive_forward(self):
        self.linear_speed = self.linear_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.update_status("⬆️ Moving forward")
    
    def drive_backward(self):
        self.linear_speed = -self.linear_scale.get()
        self.angular_speed = 0.0
        self.is_moving = True
        self.update_status("⬇️ Moving backward")
    
    def drive_left(self):
        self.linear_speed = 0.0
        self.angular_speed = self.angular_scale.get()
        self.is_moving = True
        self.update_status("⬅️ Turning left")
    
    def drive_right(self):
        self.linear_speed = 0.0
        self.angular_speed = -self.angular_scale.get()
        self.is_moving = True
        self.update_status("➡️ Turning right")
    
    def drive_stop(self):
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        self.update_status("🛑 Stopped")
    
    # Position presets
    def go_to_table_position(self):
        self.navigate_to_position(0.0, 0.0, 0.0)
        self.update_status("🎯 Moving to table position")
    
    def go_to_start_position(self):
        self.navigate_to_position(-3.0, 2.0, 0.0)
        self.update_status("🏠 Returning to start position")
    
    def go_to_drop_zone(self):
        self.navigate_to_position(-2.0, 4.0, 0.0)
        self.update_status("📦 Moving to drop zone")
    
    def reset_position(self):
        self.robot_x = -3.0
        self.robot_y = 2.0
        self.robot_theta = 0.0
        self.drive_stop()
        self.update_status("🔄 Position reset")
    
    # Pick and place sequences
    def full_pick_place_sequence(self):
        """Execute the full pick and place sequence"""
        self.update_status("🤖 Starting full pick and place sequence...")
        self.pick_place_state = "full_sequence"
        
        def sequence():
            try:
                # Step 1: Navigate to table
                self.update_status("🚗 Step 1: Navigating to table...")
                self.navigate_to_table()
                time.sleep(3)
                
                # Step 2: Prepare to grasp
                self.update_status("🦾 Step 2: Preparing to grasp...")
                self.prepare_to_grasp()
                time.sleep(2)
                
                # Step 3: Pick up object
                self.update_status("🤏 Step 3: Picking up object...")
                self.pick_up_object()
                time.sleep(3)
                
                # Step 4: Navigate to drop zone
                self.update_status("🚚 Step 4: Transporting to drop zone...")
                self.navigate_to_position(-2.0, 4.0, 0.0)
                time.sleep(3)
                
                # Step 5: Place object
                self.update_status("📦 Step 5: Placing object...")
                self.place_object()
                time.sleep(2)
                
                # Step 6: Return home
                self.update_status("🏠 Step 6: Returning home...")
                self.return_home()
                time.sleep(2)
                
                self.update_status("✅ Pick and place sequence completed!")
                self.pick_place_state = "idle"
                
            except Exception as e:
                self.update_status(f"❌ Sequence failed: {str(e)}")
                self.pick_place_state = "idle"
        
        threading.Thread(target=sequence, daemon=True).start()
    
    def navigate_to_table(self):
        """Navigate to table position"""
        self.navigate_to_position(0.0, -1.0, 0.0)  # In front of table
    
    def prepare_to_grasp(self):
        """Prepare robot for grasping"""
        self.go_to_pose("approach_table")
    
    def pick_up_object(self):
        """Pick up the target object"""
        def pick_sequence():
            # Approach
            self.go_to_pose("approach_table")
            time.sleep(1)
            
            # Grasp
            self.go_to_pose("grasp_glass")
            time.sleep(1)
            
            # Lift
            self.go_to_pose("lift_glass")
            time.sleep(1)
            
            # Transport position
            self.go_to_pose("transport")
        
        threading.Thread(target=pick_sequence, daemon=True).start()
    
    def place_object(self):
        """Place the object"""
        def place_sequence():
            # Place position
            self.go_to_pose("place_position")
            time.sleep(1)
            
            # Release
            self.go_to_pose("release")
            time.sleep(1)
            
            # Retract
            self.go_to_pose("approach_table")
        
        threading.Thread(target=place_sequence, daemon=True).start()
    
    def return_home(self):
        """Return to home position"""
        self.go_to_pose("home")
        self.navigate_to_position(-3.0, 2.0, 0.0)
    
    def navigate_to_position(self, x, y, theta):
        """Navigate to a specific position"""
        def navigate():
            # Simple navigation - move to position
            target_x, target_y, target_theta = x, y, theta
            
            while True:
                # Calculate distance and angle to target
                dx = target_x - self.robot_x
                dy = target_y - self.robot_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 0.1:  # Close enough
                    break
                
                # Calculate target angle
                target_angle = math.atan2(dy, dx)
                angle_diff = target_angle - self.robot_theta
                
                # Normalize angle difference
                angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
                
                # Turn towards target
                if abs(angle_diff) > 0.1:
                    self.angular_speed = 0.3 * (1 if angle_diff > 0 else -1)
                    self.linear_speed = 0.0
                else:
                    # Move forward
                    self.angular_speed = 0.0
                    self.linear_speed = min(0.2, distance * 0.5)
                
                self.is_moving = True
                time.sleep(0.1)
            
            # Stop
            self.drive_stop()
        
        threading.Thread(target=navigate, daemon=True).start()
    
    def go_to_pose(self, pose_name):
        """Go to a predefined pose"""
        if pose_name not in self.poses:
            return
        
        pose = self.poses[pose_name]
        
        # Set lift position
        if 'joint_lift' in pose:
            self.joints['joint_lift']['current'] = pose['joint_lift']
            if 'joint_lift' in self.sliders:
                self.sliders['joint_lift'].set(pose['joint_lift'])
        
        # Set arm extension (sum of all arm segments)
        if 'arm_extension' in pose:
            ext_per_segment = pose['arm_extension'] / 4
            for i in range(4):
                joint_name = f'joint_arm_l{i}'
                if joint_name in self.joints:
                    self.joints[joint_name]['current'] = ext_per_segment
                    if joint_name in self.sliders:
                        self.sliders[joint_name].set(ext_per_segment)
        
        # Set wrist joints
        wrist_joints = ['joint_wrist_yaw', 'joint_wrist_pitch', 'joint_wrist_roll']
        for joint in wrist_joints:
            if joint in pose and joint in self.joints:
                self.joints[joint]['current'] = pose[joint]
                if joint in self.sliders:
                    self.sliders[joint].set(pose[joint])
        
        # Set gripper
        if 'gripper_open' in pose:
            gripper_pos = pose['gripper_open']
            self.joints['joint_gripper_finger_left']['current'] = gripper_pos
            self.joints['joint_gripper_finger_right']['current'] = -gripper_pos
            if 'joint_gripper_finger_left' in self.sliders:
                self.sliders['joint_gripper_finger_left'].set(gripper_pos)
            if 'joint_gripper_finger_right' in self.sliders:
                self.sliders['joint_gripper_finger_right'].set(-gripper_pos)
        
        self.update_status(f"🎭 Moving to {pose_name} pose")
    
    def open_gripper(self):
        """Open the gripper"""
        self.joints['joint_gripper_finger_left']['current'] = 0.08
        self.joints['joint_gripper_finger_right']['current'] = -0.08
        self.update_status("🔓 Gripper opened")
    
    def close_gripper(self):
        """Close the gripper"""
        self.joints['joint_gripper_finger_left']['current'] = 0.0
        self.joints['joint_gripper_finger_right']['current'] = 0.0
        self.update_status("🤏 Gripper closed")
    
    def grasp_object(self):
        """Grasp an object"""
        self.joints['joint_gripper_finger_left']['current'] = 0.02
        self.joints['joint_gripper_finger_right']['current'] = -0.02
        self.update_status("🎯 Grasping object")
    
    def update_joint(self, joint_name, value, value_label):
        """Update joint position"""
        self.joints[joint_name]['current'] = float(value)
        if value_label:
            value_label.config(text=f"{float(value):.3f}")
    
    def update_status(self, message):
        """Update status display"""
        if self.status_label:
            self.status_label.config(text=message)
        print(f"Status: {message}")
    
    def emergency_stop(self):
        """Emergency stop all motion"""
        self.drive_stop()
        self.pick_place_state = "emergency_stop"
        self.update_status("🚨 EMERGENCY STOP ACTIVATED")
    
    def reset_all(self):
        """Reset all systems"""
        self.drive_stop()
        self.pick_place_state = "idle"
        self.reset_position()
        self.update_status("🔄 All systems reset")
    
    def home_all(self):
        """Home all joints"""
        self.go_to_pose("home")
        self.reset_position()
        self.pick_place_state = "idle"
        self.update_status("🏠 All joints homed")
    
    def update_robot(self):
        """Update robot state and publish"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Update robot position
        if self.is_moving:
            self.robot_x += self.linear_speed * math.cos(self.robot_theta) * dt
            self.robot_y += self.linear_speed * math.sin(self.robot_theta) * dt
            self.robot_theta += self.angular_speed * dt
            
            # Normalize angle
            self.robot_theta = math.atan2(math.sin(self.robot_theta), math.cos(self.robot_theta))
            
            # Update wheel positions
            left_wheel_speed = self.linear_speed - (self.angular_speed * self.wheel_base / 2.0)
            right_wheel_speed = self.linear_speed + (self.angular_speed * self.wheel_base / 2.0)
            
            self.wheel_positions['joint_left_wheel'] += (left_wheel_speed / self.wheel_radius) * dt
            self.wheel_positions['joint_right_wheel'] += (right_wheel_speed / self.wheel_radius) * dt
        
        # Update displays
        if self.position_label:
            self.position_label.config(
                text=f"📍 Position: ({self.robot_x:.2f}, {self.robot_y:.2f}) θ={math.degrees(self.robot_theta):.1f}°"
            )
        
        if self.state_label:
            self.state_label.config(text=f"🔄 State: {self.pick_place_state}")
        
        # Publish states
        self.publish_transforms()
        self.publish_joint_states()
    
    def publish_transforms(self):
        """Publish robot transforms"""
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
        
        # Regular joints
        joint_names = list(self.joints.keys())
        joint_positions = [self.joints[name]['current'] for name in joint_names]
        
        # Wheel joints
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
        controller = StretchPickPlaceControl()
        controller.setup_gui()
        
        # Run ROS2 in background
        def spin_ros():
            try:
                rclpy.spin(controller)
            except:
                pass
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        print("🤖 Pick and place control GUI starting...")
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
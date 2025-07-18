#!/usr/bin/env python3
"""
Stretch Robot Dual GUI Control
Advanced GUI + Mujoco Viewer simultaneously
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
import os
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image, ImageTk
import cv2

# Add the stretch_mujoco path
sys.path.append('/home/user/stretch_mujoco')

try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.actuators import Actuators
    from stretch_mujoco.enums.stretch_cameras import StretchCameras
    STRETCH_MUJOCO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import stretch_mujoco: {e}")
    STRETCH_MUJOCO_AVAILABLE = False

# Import ROS2
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from sensor_msgs.msg import JointState
    from std_msgs.msg import Float64
    ROS2_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ROS2: {e}")
    ROS2_AVAILABLE = False

class StretchDualGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stretch Robot - Dual GUI Control")
        self.root.geometry("900x700")
        
        # Simulation state
        self.sim: Optional[StretchMujocoSimulator] = None
        self.is_running = False
        self.status_thread = None
        
        # Joint states
        self.joint_states = {}
        
        # GUI options
        self.mujoco_viewer = tk.BooleanVar(value=True)   # Enable Mujoco GUI
        self.cameras_enabled = tk.BooleanVar(value=True)  # Enable cameras
        self.fast_mode = tk.BooleanVar(value=False)      # Fast simulation mode
        self.camera_fps = tk.IntVar(value=10)            # Camera FPS (lower = faster sim)
        
        # Camera display
        self.camera_labels = {}
        self.camera_thread = None
        
        # Movement control state
        self.moving_keys = set()  # Track currently pressed movement keys
        self.button_click_counts = {}  # Track button click counts for velocity scaling
        self.last_button_click_time = {}  # Track timing for velocity scaling
        
        # Key bindings
        self.setup_key_bindings()
        
        self.setup_ui()
        
    def setup_key_bindings(self):
        """Set up keyboard shortcuts"""
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.focus_set()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Stretch Robot - Dual GUI Control", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Connection control
        self.setup_connection_controls(main_frame)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(10, 0))
        
        # Control tab
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text='Robot Control')
        self.setup_control_tab(control_frame)
        
        # Status tab
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text='Status & Monitor')
        self.setup_status_tab(status_frame)
        
        # Instructions tab
        instructions_frame = ttk.Frame(notebook)
        notebook.add(instructions_frame, text='Instructions')
        self.setup_instructions_tab(instructions_frame)
        
    def setup_connection_controls(self, parent):
        """Set up connection controls"""
        conn_frame = ttk.LabelFrame(parent, text="Simulation Control", padding="10")
        conn_frame.pack(fill='x', pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(conn_frame)
        button_frame.pack(fill='x')
        
        self.connect_button = ttk.Button(button_frame, text="Start Dual GUI Mode", 
                                        command=self.start_simulation, 
                                        style='Accent.TButton')
        self.connect_button.pack(side='left', padx=5)
        
        self.disconnect_button = ttk.Button(button_frame, text="Stop Simulation", 
                                           command=self.stop_simulation, 
                                           state='disabled')
        self.disconnect_button.pack(side='left', padx=5)
        
        self.connection_status = ttk.Label(button_frame, text="Status: Stopped", 
                                         foreground="red")
        self.connection_status.pack(side='left', padx=20)
        
        # Options
        options_frame = ttk.Frame(conn_frame)
        options_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="Enable Mujoco 3D Viewer", 
                       variable=self.mujoco_viewer).pack(side='left', padx=10)
        
        ttk.Checkbutton(options_frame, text="Enable Cameras", 
                       variable=self.cameras_enabled).pack(side='left', padx=10)
        
        ttk.Checkbutton(options_frame, text="Fast Mode (Disable cameras)", 
                       variable=self.fast_mode, command=self.toggle_fast_mode).pack(side='left', padx=10)
        
        # Camera FPS control
        fps_frame = ttk.Frame(options_frame)
        fps_frame.pack(side='left', padx=10)
        ttk.Label(fps_frame, text="Camera FPS:").pack(side='left')
        fps_spinbox = ttk.Spinbox(fps_frame, from_=1, to=30, width=5, textvariable=self.camera_fps)
        fps_spinbox.pack(side='left', padx=5)
        
        # Info
        info_label = ttk.Label(conn_frame, 
                              text="Tip: Enable 'Fast Mode' or lower Camera FPS for better simulation speed. Cameras reduce performance significantly.",
                              foreground="blue")
        info_label.pack(pady=(10, 0))
        
    def setup_control_tab(self, parent):
        """Set up the control tab"""
        # Create two columns
        left_frame = ttk.Frame(parent)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Left column - Movement controls
        self.setup_movement_controls(left_frame)
        
        # Right column - Status and presets
        self.setup_right_controls(right_frame)
        
    def setup_movement_controls(self, parent):
        """Set up movement controls"""
        # Base controls
        base_frame = ttk.LabelFrame(parent, text="Base Movement (WASD)", padding="10")
        base_frame.pack(fill='x', pady=(0, 10))
        
        base_grid = ttk.Frame(base_frame)
        base_grid.pack()
        
        ttk.Button(base_grid, text="↑ Forward (W)", 
                  command=lambda: self.move_base_scaled('w', 0.1, 0.0)).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(base_grid, text="↺ Left (A)", 
                  command=lambda: self.move_base_scaled('a', 0.0, 0.2)).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(base_grid, text="⊞ Stop", 
                  command=lambda: self.stop_base_movement()).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(base_grid, text="↻ Right (D)", 
                  command=lambda: self.move_base_scaled('d', 0.0, -0.2)).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(base_grid, text="↓ Backward (S)", 
                  command=lambda: self.move_base_scaled('s', -0.1, 0.0)).grid(row=2, column=1, padx=2, pady=2)
        
        # Arm controls
        arm_frame = ttk.LabelFrame(parent, text="Arm Control (IJKL)", padding="10")
        arm_frame.pack(fill='x', pady=(0, 10))
        
        # Lift
        lift_frame = ttk.Frame(arm_frame)
        lift_frame.pack(fill='x', pady=2)
        ttk.Label(lift_frame, text="Lift:").pack(side='left')
        ttk.Button(lift_frame, text="Up (I)", 
                  command=lambda: self.move_joint_relative('lift', 0.1)).pack(side='left', padx=2)
        ttk.Button(lift_frame, text="Down (K)", 
                  command=lambda: self.move_joint_relative('lift', -0.1)).pack(side='left', padx=2)
        
        # Arm extension
        arm_ext_frame = ttk.Frame(arm_frame)
        arm_ext_frame.pack(fill='x', pady=2)
        ttk.Label(arm_ext_frame, text="Arm:").pack(side='left')
        ttk.Button(arm_ext_frame, text="Retract (J)", 
                  command=lambda: self.move_joint_relative('arm', -0.05)).pack(side='left', padx=2)
        ttk.Button(arm_ext_frame, text="Extend (L)", 
                  command=lambda: self.move_joint_relative('arm', 0.05)).pack(side='left', padx=2)
        
        # Head controls
        head_frame = ttk.LabelFrame(parent, text="Head Control (TFGH)", padding="10")
        head_frame.pack(fill='x', pady=(0, 10))
        
        # Head controls in grid
        head_grid = ttk.Frame(head_frame)
        head_grid.pack()
        
        ttk.Button(head_grid, text="Tilt Up (T)", 
                  command=lambda: self.move_joint_relative('head_tilt', 0.2)).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(head_grid, text="Pan Left (F)", 
                  command=lambda: self.move_joint_relative('head_pan', 0.2)).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(head_grid, text="Pan Right (H)", 
                  command=lambda: self.move_joint_relative('head_pan', -0.2)).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(head_grid, text="Tilt Down (G)", 
                  command=lambda: self.move_joint_relative('head_tilt', -0.2)).grid(row=2, column=1, padx=2, pady=2)
        
        # Wrist controls
        wrist_frame = ttk.LabelFrame(parent, text="Wrist Control", padding="10")
        wrist_frame.pack(fill='x', pady=(0, 10))
        
        # Wrist controls in compact layout
        wrist_grid = ttk.Frame(wrist_frame)
        wrist_grid.pack()
        
        # Yaw
        ttk.Label(wrist_grid, text="Yaw:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        ttk.Button(wrist_grid, text="Left (O)", 
                  command=lambda: self.move_joint_relative('wrist_yaw', 0.2)).grid(row=0, column=1, padx=1)
        ttk.Button(wrist_grid, text="Right (P)", 
                  command=lambda: self.move_joint_relative('wrist_yaw', -0.2)).grid(row=0, column=2, padx=1)
        
        # Pitch
        ttk.Label(wrist_grid, text="Pitch:").grid(row=1, column=0, sticky='w', padx=(0, 5))
        ttk.Button(wrist_grid, text="Up (C)", 
                  command=lambda: self.move_joint_relative('wrist_pitch', 0.2)).grid(row=1, column=1, padx=1)
        ttk.Button(wrist_grid, text="Down (V)", 
                  command=lambda: self.move_joint_relative('wrist_pitch', -0.2)).grid(row=1, column=2, padx=1)
        
        # Roll
        ttk.Label(wrist_grid, text="Roll:").grid(row=2, column=0, sticky='w', padx=(0, 5))
        ttk.Button(wrist_grid, text="CCW (E)", 
                  command=lambda: self.move_joint_relative('wrist_roll', 0.2)).grid(row=2, column=1, padx=1)
        ttk.Button(wrist_grid, text="CW (R)", 
                  command=lambda: self.move_joint_relative('wrist_roll', -0.2)).grid(row=2, column=2, padx=1)
        
        # Gripper controls
        gripper_frame = ttk.LabelFrame(parent, text="Gripper Control (NM)", padding="10")
        gripper_frame.pack(fill='x', pady=(0, 10))
        
        gripper_buttons = ttk.Frame(gripper_frame)
        gripper_buttons.pack()
        ttk.Button(gripper_buttons, text="Open (N)", 
                  command=lambda: self.move_joint_relative('gripper', 0.07)).pack(side='left', padx=5)
        ttk.Button(gripper_buttons, text="Close (M)", 
                  command=lambda: self.move_joint_relative('gripper', -0.07)).pack(side='left', padx=5)
        
    def setup_right_controls(self, parent):
        """Set up right side controls"""
        # Preset commands
        preset_frame = ttk.LabelFrame(parent, text="Preset Commands", padding="10")
        preset_frame.pack(fill='x', pady=(0, 10))
        
        preset_grid = ttk.Frame(preset_frame)
        preset_grid.pack()
        
        ttk.Button(preset_grid, text="Home Position", 
                  command=self.home_robot).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(preset_grid, text="Stow Position", 
                  command=self.stow_robot).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(preset_grid, text="Print Status (Z)", 
                  command=self.print_status).grid(row=1, column=0, columnspan=2, pady=2)
        
        # Camera views display
        camera_frame = ttk.LabelFrame(parent, text="Live Camera Feeds", padding="10")
        camera_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Set up camera grid in the main control panel
        self.setup_main_camera_display(camera_frame)
        
        # Quick reference
        ref_frame = ttk.LabelFrame(parent, text="Quick Reference", padding="10")
        ref_frame.pack(fill='x')
        
        ref_text = """Keyboard Shortcuts:
WASD: Base movement
TFGH: Head movement  
IJKL: Arm movement
OPCV: Wrist yaw/pitch
ER: Wrist roll
NM: Gripper open/close
Z: Print status
Q: Stop simulation"""
        
        ttk.Label(ref_frame, text=ref_text, font=('Courier', 9)).pack()
        
    def setup_status_tab(self, parent):
        """Set up status tab"""
        # Detailed status
        status_frame = ttk.LabelFrame(parent, text="Detailed Status", padding="10")
        status_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.detailed_status_text = scrolledtext.ScrolledText(status_frame, height=15)
        self.detailed_status_text.pack(fill='both', expand=True)
        
        # Log output
        log_frame = ttk.LabelFrame(parent, text="Log Output", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill='both', expand=True)
        
    def setup_instructions_tab(self, parent):
        """Set up instructions tab"""
        instructions_text = """
DUAL GUI MODE INSTRUCTIONS
==========================

This mode gives you the best of both worlds:

1. ADVANCED GUI CONTROLS (This window)
   - Visual buttons for all robot controls
   - Real-time joint status display
   - Keyboard shortcuts
   - Preset commands (Home, Stow)
   - Status monitoring and logging

2. MUJOCO 3D VIEWER (Separate window)
   - Real-time 3D visualization of the robot
   - Physics simulation display
   - Camera views (if enabled)
   - Interactive 3D scene

USAGE:
1. Click "Start Dual GUI Mode" to launch both interfaces
2. Use THIS window for control and monitoring
3. Use the MUJOCO 3D window for visualization
4. Both windows work together seamlessly

CONTROLS:
- Use buttons in this GUI OR keyboard shortcuts
- All movements are reflected in real-time in the 3D viewer
- Status updates appear in both interfaces

KEYBOARD SHORTCUTS:
- WASD: Base movement (forward/left/back/right)
- TFGH: Head movement (tilt up/pan left/tilt down/pan right)
- IJKL: Arm movement (lift up/arm in/lift down/arm out)
- OPCV: Wrist yaw/pitch (yaw left/right, pitch up/down)
- ER: Wrist roll (counter-clockwise/clockwise)
- NM: Gripper (open/close)
- Z: Print detailed status
- Q: Stop simulation

TIPS:
- Focus this window to use keyboard shortcuts
- The 3D viewer shows real-time robot movements
- Monitor joint status in the right panel
- Use preset commands for quick positioning
- Check the log for detailed operation history

TROUBLESHOOTING:
- If 3D viewer doesn't appear, check "Enable Mujoco 3D Viewer"
- If controls don't work, ensure simulation is started
- If keyboard shortcuts don't work, click in this window first
"""
        
        # Create scrolled text widget for instructions
        instr_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=80, height=30)
        instr_text.pack(fill='both', expand=True, padx=10, pady=10)
        instr_text.insert(1.0, instructions_text)
        instr_text.config(state='disabled')  # Make it read-only
        
    def setup_main_camera_display(self, parent):
        """Set up camera display in main control panel"""
        # Create grid frame for cameras
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill='both', expand=True)
        
        # Configure grid weights for responsive layout
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_rowconfigure(1, weight=1)
        
        # Camera configurations (smaller layout for main panel)
        camera_configs = [
            ('cam_d405_rgb', 'D405 RGB', 0, 0),
            ('cam_d435i_rgb', 'D435i RGB', 0, 1),
            ('cam_nav_rgb', 'Navigation', 1, 0)
        ]
        
        # Create camera display areas
        for camera_name, display_name, row, col in camera_configs:
            # Camera frame with border
            camera_subframe = ttk.LabelFrame(grid_frame, text=display_name, padding="3")
            camera_subframe.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
            camera_subframe.grid_columnconfigure(0, weight=1)
            camera_subframe.grid_rowconfigure(0, weight=1)
            
            # Camera display label (smaller for main panel)
            camera_label = ttk.Label(camera_subframe, text="Camera not connected", anchor='center')
            camera_label.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
            
            self.camera_labels[camera_name] = camera_label
        
    def log_message(self, message: str):
        """Add message to log"""
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        
    def start_simulation(self):
        """Start the simulation with dual GUI mode"""
        if not STRETCH_MUJOCO_AVAILABLE:
            messagebox.showerror("Error", "stretch_mujoco not available!")
            return
            
        try:
            self.log_message("Starting Dual GUI Mode...")
            self.log_message("Launching Advanced GUI Controls + Mujoco 3D Viewer...")
            
            # Configure cameras based on performance settings
            if self.fast_mode.get():
                cameras_to_use = []  # No cameras for maximum speed
                self.log_message("Fast mode enabled - cameras disabled for performance")
            elif self.cameras_enabled.get():
                cameras_to_use = StretchCameras.rgb()  # RGB cameras only
                self.log_message(f"Cameras enabled with {self.camera_fps.get()} FPS")
            else:
                cameras_to_use = []
            
            # Initialize simulator
            self.sim = StretchMujocoSimulator(cameras_to_use=cameras_to_use)
            
            # Start with or without Mujoco viewer
            headless = not self.mujoco_viewer.get()
            self.sim.start(headless=headless)
            
            self.is_running = True
            self.start_status_thread()
            
            # Update UI
            self.connect_button.config(state='disabled')
            self.disconnect_button.config(state='normal')
            self.connection_status.config(text="Status: Dual GUI Running", foreground="green")
            
            # Start camera thread for the camera tab
            if self.cameras_enabled.get() and not self.fast_mode.get():
                self.debug_simulation_cameras()
                self.start_camera_thread()
            
            if self.mujoco_viewer.get():
                self.log_message("✓ Mujoco 3D Viewer window opened")
            else:
                self.log_message("✓ Running in headless mode")
                
            self.log_message("✓ Advanced GUI controls ready")
            self.log_message("✓ Dual GUI Mode started successfully!")
            
            # Show success message
            messagebox.showinfo("Success", 
                              "Dual GUI Mode started!\n\n" +
                              "• Advanced GUI controls in this window\n" +
                              ("• Mujoco 3D viewer in separate window\n" if self.mujoco_viewer.get() else "• Running in headless mode\n") +
                              "• Use keyboard shortcuts or buttons to control robot\n" +
                              "• Monitor status in real-time")
            
        except Exception as e:
            self.log_message(f"Error starting dual GUI mode: {e}")
            messagebox.showerror("Error", f"Failed to start dual GUI mode: {e}")
            
    def stop_simulation(self):
        """Stop the simulation"""
        try:
            self.log_message("Stopping simulation...")
            
            self.is_running = False
            
            if self.sim:
                self.sim.stop()
                self.sim = None
                
            # Update UI
            self.connect_button.config(state='normal')
            self.disconnect_button.config(state='disabled')
            self.connection_status.config(text="Status: Stopped", foreground="red")
            
            self.log_message("Simulation stopped successfully!")
            
        except Exception as e:
            self.log_message(f"Error stopping simulation: {e}")
            messagebox.showerror("Error", f"Failed to stop simulation: {e}")
            
    def start_status_thread(self):
        """Start status update thread"""
        self.status_thread = threading.Thread(target=self.status_update_loop, daemon=True)
        self.status_thread.start()
        
    def status_update_loop(self):
        """Status update loop"""
        while self.is_running and self.sim:
            try:
                if self.sim.is_running():
                    status = self.sim.pull_status()
                    self.update_display(status)
                time.sleep(0.1)
            except Exception as e:
                self.log_message(f"Status update error: {e}")
                break
                
    def update_display(self, status):
        """Update display with status"""
        # Update joint states
        self.joint_states = {}
        joint_attrs = ['lift', 'arm', 'head_pan', 'head_tilt', 'wrist_yaw', 'wrist_pitch', 'wrist_roll', 'gripper']
        for joint_name in joint_attrs:
            if hasattr(status, joint_name):
                joint_data = getattr(status, joint_name)
                if hasattr(joint_data, 'pos'):
                    self.joint_states[joint_name] = {
                        'position': joint_data.pos,
                        'velocity': joint_data.vel if hasattr(joint_data, 'vel') else 0.0
                    }
        
        
        # Update detailed status
        detailed_text = f"Time: {status.time:.2f}s, FPS: {status.fps:.1f}\n"
        detailed_text += f"Sim-to-Real: {status.sim_to_real_time_ratio_msg}\n\n"
        detailed_text += f"Base Position: x={status.base.x:.3f}, y={status.base.y:.3f}, θ={status.base.theta:.3f}\n"
        detailed_text += f"Base Velocity: x={status.base.x_vel:.3f}, θ={status.base.theta_vel:.3f}\n\n"
        detailed_text += "Joint States:\n"
        for joint_name, data in self.joint_states.items():
            detailed_text += f"  {joint_name:12}: pos={data['position']:8.3f}, vel={data['velocity']:8.3f}\n"
        
        self.detailed_status_text.delete(1.0, tk.END)
        self.detailed_status_text.insert(1.0, detailed_text)
        
    def move_base(self, linear_x, angular_z):
        """Move the base"""
        if self.sim and self.sim.is_running():
            self.sim.set_base_velocity(linear_x, angular_z)
            self.log_message(f"Base velocity: linear={linear_x:.2f}, angular={angular_z:.2f}")
        else:
            self.log_message("Simulation not running!")
            
    def move_base_scaled(self, button_key, base_linear, base_angular):
        """Move base with velocity scaling based on repeated clicks"""
        current_time = time.time()
        
        # Check if this is a repeated click within 1 second
        if button_key in self.last_button_click_time:
            time_diff = current_time - self.last_button_click_time[button_key]
            if time_diff < 1.0:  # Within 1 second
                self.button_click_counts[button_key] = self.button_click_counts.get(button_key, 0) + 1
            else:
                self.button_click_counts[button_key] = 1
        else:
            self.button_click_counts[button_key] = 1
            
        self.last_button_click_time[button_key] = current_time
        
        # Scale velocity based on click count (max 3x speed)
        click_count = self.button_click_counts[button_key]
        velocity_multiplier = min(click_count, 3)
        
        scaled_linear = base_linear * velocity_multiplier
        scaled_angular = base_angular * velocity_multiplier
        
        self.move_base(scaled_linear, scaled_angular)
        self.log_message(f"Click count: {click_count}, Velocity multiplier: {velocity_multiplier}x")
        
    def stop_base_movement(self):
        """Stop base movement and reset click counts"""
        self.move_base(0.0, 0.0)
        self.button_click_counts.clear()
        self.last_button_click_time.clear()
            
    def move_joint_relative(self, joint_name, increment):
        """Move a joint by relative amount"""
        if self.sim and self.sim.is_running():
            actuator_map = {
                'lift': Actuators.lift,
                'arm': Actuators.arm,
                'head_pan': Actuators.head_pan,
                'head_tilt': Actuators.head_tilt,
                'wrist_yaw': Actuators.wrist_yaw,
                'wrist_pitch': Actuators.wrist_pitch,
                'wrist_roll': Actuators.wrist_roll,
                'gripper': Actuators.gripper
            }
            if joint_name in actuator_map:
                self.sim.move_by(actuator_map[joint_name], increment)
                self.log_message(f"Moved {joint_name} by {increment:.3f}")
        else:
            self.log_message("Simulation not running!")
            
    def home_robot(self):
        """Home the robot"""
        if self.sim and self.sim.is_running():
            self.sim.home()
            self.log_message("Robot moved to home position")
        else:
            self.log_message("Simulation not running!")
            
    def stow_robot(self):
        """Stow the robot"""
        if self.sim and self.sim.is_running():
            self.sim.stow()
            self.log_message("Robot moved to stow position")
        else:
            self.log_message("Simulation not running!")
            
    def print_status(self):
        """Print detailed status"""
        if self.sim and self.sim.is_running():
            try:
                status = self.sim.pull_status()
                self.log_message("=== DETAILED STATUS ===")
                self.log_message(f"Time: {status.time:.2f}s, FPS: {status.fps:.1f}")
                self.log_message(f"Base: pos=({status.base.x:.3f}, {status.base.y:.3f}, {status.base.theta:.3f})")
                self.log_message(f"Base: vel=({status.base.x_vel:.3f}, {status.base.theta_vel:.3f})")
                
                for joint_name, data in self.joint_states.items():
                    self.log_message(f"{joint_name}: pos={data['position']:.3f}, vel={data['velocity']:.3f}")
                
                self.log_message("======================")
                
            except Exception as e:
                self.log_message(f"Error printing status: {e}")
        else:
            self.log_message("Simulation not running!")
            
    def on_key_press(self, event):
        """Handle key press events"""
        if not self.is_running:
            return
            
        key = event.char.lower()
        
        # Base movement - only start movement if key not already pressed
        if key == 'w' and key not in self.moving_keys:
            self.moving_keys.add(key)
            self.move_base(0.1, 0.0)
        elif key == 's' and key not in self.moving_keys:
            self.moving_keys.add(key)
            self.move_base(-0.1, 0.0)
        elif key == 'a' and key not in self.moving_keys:
            self.moving_keys.add(key)
            self.move_base(0.0, 0.2)
        elif key == 'd' and key not in self.moving_keys:
            self.moving_keys.add(key)
            self.move_base(0.0, -0.2)
        
        # Head movement
        elif key == 't':
            self.move_joint_relative('head_tilt', 0.2)
        elif key == 'g':
            self.move_joint_relative('head_tilt', -0.2)
        elif key == 'f':
            self.move_joint_relative('head_pan', 0.2)
        elif key == 'h':
            self.move_joint_relative('head_pan', -0.2)
        
        # Arm movement
        elif key == 'i':
            self.move_joint_relative('lift', 0.1)
        elif key == 'k':
            self.move_joint_relative('lift', -0.1)
        elif key == 'j':
            self.move_joint_relative('arm', -0.05)
        elif key == 'l':
            self.move_joint_relative('arm', 0.05)
        
        # Wrist movement
        elif key == 'o':
            self.move_joint_relative('wrist_yaw', 0.2)
        elif key == 'p':
            self.move_joint_relative('wrist_yaw', -0.2)
        elif key == 'c':
            self.move_joint_relative('wrist_pitch', 0.2)
        elif key == 'v':
            self.move_joint_relative('wrist_pitch', -0.2)
        elif key == 'e':
            self.move_joint_relative('wrist_roll', 0.2)
        elif key == 'r':
            self.move_joint_relative('wrist_roll', -0.2)
        
        # Gripper
        elif key == 'n':
            self.move_joint_relative('gripper', 0.07)
        elif key == 'm':
            self.move_joint_relative('gripper', -0.07)
        
        # Other commands
        elif key == 'z':
            self.print_status()
        elif key == 'q':
            self.stop_simulation()
            
    def on_key_release(self, event):
        """Handle key release events"""
        if not self.is_running:
            return
            
        key = event.char.lower()
        
        # Stop base movement on key release
        if key in ['w', 's', 'a', 'd']:
            self.moving_keys.discard(key)
            self.move_base(0.0, 0.0)
            
            
    def start_camera_thread(self):
        """Start camera update thread"""
        if self.camera_thread is None or not self.camera_thread.is_alive():
            self.camera_thread = threading.Thread(target=self.camera_update_loop, daemon=True)
            self.camera_thread.start()
            
    def debug_simulation_cameras(self):
        """Debug what camera methods are available in the simulation"""
        try:
            self.log_message("=== DEBUGGING CAMERA SETUP ===")
            self.log_message(f"Simulation object type: {type(self.sim)}")
            self.log_message(f"Cameras enabled: {self.cameras_enabled.get()}")
            
            if hasattr(self.sim, 'cameras_to_use'):
                self.log_message(f"Cameras configured to use: {self.sim.cameras_to_use}")
            
            # List all camera-related methods
            camera_methods = [method for method in dir(self.sim) if 'camera' in method.lower()]
            self.log_message(f"Available camera methods: {camera_methods}")
            
            # Test camera data retrieval
            try:
                self.log_message("Testing camera data retrieval...")
                camera_data = self.sim.pull_camera_data()
                if camera_data:
                    self.log_message(f"Camera data object type: {type(camera_data)}")
                    
                    # Try to get all camera data
                    all_cameras = camera_data.get_all(use_depth_color_map=False)
                    self.log_message(f"Available cameras in data: {list(all_cameras.keys())}")
                    
                    # Test each RGB camera
                    rgb_cameras = ['cam_d405_rgb', 'cam_d435i_rgb', 'cam_nav_rgb']
                    for cam_name in rgb_cameras:
                        if cam_name in all_cameras:
                            img_data = all_cameras[cam_name]
                            self.log_message(f"{cam_name}: shape={np.array(img_data).shape}, type={type(img_data)}")
                        else:
                            self.log_message(f"{cam_name}: NOT AVAILABLE")
                else:
                    self.log_message("No camera data returned from pull_camera_data()")
                    
            except Exception as cam_test_e:
                self.log_message(f"Camera data test failed: {cam_test_e}")
            
            self.log_message("=== END CAMERA DEBUG ===")
            
        except Exception as e:
            self.log_message(f"Error during camera debugging: {e}")
            
    def camera_update_loop(self):
        """Camera update loop"""
        while self.is_running and self.sim:
            try:
                if self.sim.is_running():
                    # Get camera images from simulation
                    for camera_name in self.camera_labels.keys():
                        try:
                            # Get camera image from simulation
                            img_array = self.get_camera_image(camera_name)
                            if img_array is not None:
                                self.update_camera_display(camera_name, img_array)
                        except Exception as e:
                            self.log_message(f"Error getting {camera_name} image: {e}")
                            
                # Configurable camera update rate
                fps = self.camera_fps.get()
                time.sleep(1.0 / fps)  # Update at configurable FPS
            except Exception as e:
                self.log_message(f"Camera update error: {e}")
                break
                
    def get_camera_image(self, camera_name):
        """Get camera image from simulation using correct stretch_mujoco API"""
        try:
            if self.sim and self.sim.is_running():
                # Map camera names to StretchCameras enum values
                camera_mapping = {
                    'cam_d405_rgb': StretchCameras.cam_d405_rgb,
                    'cam_d435i_rgb': StretchCameras.cam_d435i_rgb,
                    'cam_nav_rgb': StretchCameras.cam_nav_rgb
                }
                
                if camera_name in camera_mapping:
                    camera_enum = camera_mapping[camera_name]
                    
                    try:
                        # Method 1: Use pull_camera_data() - the correct stretch_mujoco method
                        camera_data = self.sim.pull_camera_data()
                        if camera_data:
                            # Get specific camera data
                            specific_camera_data = camera_data.get_camera_data(camera_enum)
                            if specific_camera_data is not None:
                                # Convert to numpy array and ensure correct format
                                img_array = np.array(specific_camera_data)
                                if img_array.size > 0:
                                    # Check if image needs rotation (some cameras are rotated)
                                    if camera_name == 'cam_d405_rgb':
                                        img_array = np.rot90(img_array, k=2)  # 180 degree rotation
                                    
                                    self.log_message(f"Successfully got {camera_name} image via pull_camera_data")
                                    return img_array
                        
                        # Method 2: Try getting all camera data and extract specific one
                        all_camera_data = self.sim.pull_camera_data().get_all(use_depth_color_map=False)
                        if camera_name in all_camera_data:
                            img_array = np.array(all_camera_data[camera_name])
                            if img_array.size > 0:
                                self.log_message(f"Successfully got {camera_name} image via get_all")
                                return img_array
                        
                        # Method 3: Check if camera is in the available cameras
                        if hasattr(self.sim, 'cameras_to_use') and camera_enum in self.sim.cameras_to_use:
                            self.log_message(f"{camera_name} is in cameras_to_use but no data received")
                        else:
                            self.log_message(f"{camera_name} not in cameras_to_use: {getattr(self.sim, 'cameras_to_use', 'No cameras_to_use attribute')}")
                        
                    except Exception as cam_e:
                        self.log_message(f"Error accessing {camera_name} from simulation: {cam_e}")
                
                # Create a notification image showing camera is not connected
                height, width = 480, 640
                img = np.zeros((height, width, 3), dtype=np.uint8)
                img.fill(30)  # Dark background
                
                # Add "Camera Not Connected" message
                cv2.putText(img, "CAMERA NOT CONNECTED", (width//2 - 150, height//2 - 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                cv2.putText(img, f"{camera_name.upper()}", (width//2 - 60, height//2 + 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(img, "Check camera configuration in main GUI", (width//2 - 180, height//2 + 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                return img
                
        except Exception as e:
            self.log_message(f"Error generating camera image for {camera_name}: {e}")
            
        return None
        
    def update_camera_display(self, camera_name, img_array):
        """Update camera display with new image"""
        try:
            if camera_name in self.camera_labels:
                # Convert numpy array to PIL Image
                img_pil = Image.fromarray(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))
                
                # Resize for display in main panel (smaller size for integration)
                img_pil = img_pil.resize((200, 150), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                img_tk = ImageTk.PhotoImage(img_pil)
                
                # Update label
                self.camera_labels[camera_name].configure(image=img_tk, text="")
                self.camera_labels[camera_name].image = img_tk  # Keep a reference
                
        except Exception as e:
            self.log_message(f"Error updating camera display for {camera_name}: {e}")

    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            self.stop_simulation()
        self.root.destroy()
        
    def toggle_fast_mode(self):
        """Toggle fast mode - automatically disable cameras when enabled"""
        if self.fast_mode.get():
            self.cameras_enabled.set(False)
            self.log_message("Fast mode enabled - cameras automatically disabled")

def main():
    """Main function"""
    root = tk.Tk()
    app = StretchDualGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
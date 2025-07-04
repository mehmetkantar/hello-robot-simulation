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
import subprocess
import os

class StretchRobotControl(Node):
    def __init__(self):
        super().__init__('stretch_robot_control')
        
        # Create joint state publisher
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Joint definitions with proper ranges
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
        
        # Create timer for publishing joint states
        self.timer = self.create_timer(0.1, self.publish_joint_states)
        
        # Start robot state publisher
        self.start_robot_state_publisher()
        
        print("✅ Robot control node initialized")
    
    def start_robot_state_publisher(self):
        """Start the robot state publisher subprocess"""
        try:
            # Source ROS2 and workspace
            env = os.environ.copy()
            env['PYTHONPATH'] = '/opt/ros/humble/lib/python3.10/site-packages:' + env.get('PYTHONPATH', '')
            
            # Create launch command
            launch_cmd = [
                'bash', '-c', 
                'cd /home/kantar/Desktop/hello-robot/stretch_ws && '
                'source /opt/ros/humble/setup.bash && '
                'source install/setup.bash && '
                'ros2 run robot_state_publisher robot_state_publisher '
                '--ros-args -p robot_description:="$(cat src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf)"'
            ]
            
            self.robot_state_proc = subprocess.Popen(
                launch_cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it time to start
            time.sleep(2)
            print("✅ Robot state publisher started")
            
        except Exception as e:
            print(f"❌ Failed to start robot state publisher: {e}")
            self.robot_state_proc = None
    
    def setup_gui(self):
        """Setup the GUI interface"""
        self.root = tk.Tk()
        self.root.title("🤖 Stretch Robot - Live Control")
        self.root.geometry("700x900")
        self.root.configure(bg='#1e1e1e')
        
        # Title
        title = tk.Label(self.root, text="🤖 Stretch Robot - Live Joint Control", 
                        font=('Arial', 18, 'bold'), fg='#00ff00', bg='#1e1e1e')
        title.pack(pady=15)
        
        # Status indicator
        self.status_label = tk.Label(self.root, text="🟢 Connected - Robot should move in RViz",
                                   fg='#00ff00', bg='#1e1e1e', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1e1e1e')
        style.configure('TNotebook.Tab', background='#333333', foreground='white')
        
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
        
        notebook.pack(expand=True, fill='both', padx=15, pady=10)
        
        # Preset buttons
        self.create_preset_buttons()
        
        # Movement test button
        test_frame = tk.Frame(self.root, bg='#1e1e1e')
        test_frame.pack(pady=10)
        
        tk.Button(test_frame, text="🎯 Test Movement", command=self.test_movement,
                 bg='#ff6b35', fg='white', font=('Arial', 12, 'bold'), 
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(test_frame, text="🏠 Reset All", command=self.reset_all,
                 bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'), 
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        print("✅ GUI setup complete")
    
    def create_joint_controls(self, parent, joint_names):
        """Create slider controls for joints"""
        for joint_name in joint_names:
            joint_info = self.joints[joint_name]
            
            # Frame for this joint
            frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
            frame.pack(fill='x', padx=10, pady=8)
            
            # Joint name and value
            header_frame = tk.Frame(frame, bg='#2d2d2d')
            header_frame.pack(fill='x', padx=8, pady=5)
            
            name_label = tk.Label(header_frame, 
                                text=joint_name.replace('joint_', '').replace('_', ' ').title(),
                                font=('Arial', 11, 'bold'), bg='#2d2d2d', fg='white')
            name_label.pack(side=tk.LEFT)
            
            value_label = tk.Label(header_frame, text=f"{joint_info['current']:.3f}",
                                 font=('Arial', 11, 'bold'), bg='#2d2d2d', fg='#00ff00')
            value_label.pack(side=tk.RIGHT)
            
            # Slider
            slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                            resolution=0.01, orient=tk.HORIZONTAL, length=450,
                            bg='#2d2d2d', fg='white', activebackground='#555555',
                            command=lambda val, jname=joint_name, vlabel=value_label: 
                                   self.update_joint(jname, val, vlabel))
            slider.pack(fill='x', padx=8, pady=5)
            slider.set(joint_info['current'])
            
            self.sliders[joint_name] = slider
            
            # Range info
            range_label = tk.Label(frame, 
                                 text=f"Range: {joint_info['min']:.2f} to {joint_info['max']:.2f}",
                                 font=('Arial', 9), bg='#2d2d2d', fg='#888888')
            range_label.pack(pady=2)
    
    def create_preset_buttons(self):
        """Create preset position buttons"""
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(pady=15)
        
        # Row 1
        row1 = tk.Frame(button_frame, bg='#1e1e1e')
        row1.pack(pady=5)
        
        tk.Button(row1, text="🏠 Home", command=self.go_home,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, height=2).pack(side=tk.LEFT, padx=3)
        
        tk.Button(row1, text="📏 Tall", command=self.go_tall,
                 bg='#9C27B0', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, height=2).pack(side=tk.LEFT, padx=3)
        
        tk.Button(row1, text="🥤 Reach", command=self.go_reach,
                 bg='#E91E63', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, height=2).pack(side=tk.LEFT, padx=3)
        
        # Row 2
        row2 = tk.Frame(button_frame, bg='#1e1e1e')
        row2.pack(pady=5)
        
        tk.Button(row2, text="📦 Compact", command=self.go_compact,
                 bg='#607D8B', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, height=2).pack(side=tk.LEFT, padx=3)
        
        tk.Button(row2, text="🎲 Random", command=self.go_random,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'), 
                 width=12, height=2).pack(side=tk.LEFT, padx=3)
    
    def update_joint(self, joint_name, value, value_label):
        """Update joint position"""
        self.joints[joint_name]['current'] = float(value)
        value_label.config(text=f"{float(value):.3f}")
        self.status_label.config(text=f"🎮 Updated {joint_name.replace('joint_', '')} = {float(value):.3f}")
    
    def publish_joint_states(self):
        """Publish current joint states"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        
        msg.name = list(self.joints.keys())
        msg.position = [self.joints[name]['current'] for name in msg.name]
        msg.velocity = [0.0] * len(msg.name)
        msg.effort = [0.0] * len(msg.name)
        
        self.joint_pub.publish(msg)
    
    def test_movement(self):
        """Test robot movement with a sequence"""
        self.status_label.config(text="🎯 Testing movement sequence...")
        
        # Test sequence
        test_positions = [
            {'joint_lift': 0.3, 'joint_arm_l0': 0.05},
            {'joint_lift': 0.6, 'joint_arm_l0': 0.1},
            {'joint_wrist_yaw': 0.5, 'joint_head_pan': 0.3},
            {'joint_lift': 0.4, 'joint_wrist_yaw': -0.5, 'joint_head_pan': -0.3},
            {'joint_lift': 0.0, 'joint_arm_l0': 0.0, 'joint_wrist_yaw': 0.0, 'joint_head_pan': 0.0}
        ]
        
        def animate_sequence():
            for i, positions in enumerate(test_positions):
                time.sleep(1)
                for joint_name, position in positions.items():
                    if joint_name in self.joints:
                        self.joints[joint_name]['current'] = position
                        if joint_name in self.sliders:
                            self.sliders[joint_name].set(position)
                self.status_label.config(text=f"🎯 Test step {i+1}/{len(test_positions)}")
            
            self.status_label.config(text="✅ Movement test complete!")
        
        # Run animation in thread
        threading.Thread(target=animate_sequence, daemon=True).start()
    
    def go_home(self):
        """Go to home position"""
        for joint_name in self.joints:
            self.joints[joint_name]['current'] = 0.0
            if joint_name in self.sliders:
                self.sliders[joint_name].set(0.0)
        self.status_label.config(text="🏠 Moved to home position")
    
    def go_tall(self):
        """Go to tall position"""
        positions = {
            'joint_lift': 0.9,
            'joint_arm_l0': 0.03,
            'joint_arm_l1': 0.02,
            'joint_head_tilt': -0.2
        }
        self.set_positions(positions)
        self.status_label.config(text="📏 Moved to tall position")
    
    def go_reach(self):
        """Go to reaching position"""
        positions = {
            'joint_lift': 0.6,
            'joint_arm_l0': 0.08,
            'joint_arm_l1': 0.06,
            'joint_arm_l2': 0.04,
            'joint_wrist_pitch': -0.2,
            'joint_head_pan': 0.3
        }
        self.set_positions(positions)
        self.status_label.config(text="🥤 Positioned for reaching")
    
    def go_compact(self):
        """Go to compact position"""
        positions = {
            'joint_lift': 0.1,
            'joint_arm_l0': 0.0,
            'joint_arm_l1': 0.0,
            'joint_arm_l2': 0.0,
            'joint_arm_l3': 0.0,
            'joint_wrist_yaw': 0.0,
            'joint_head_pan': 0.0
        }
        self.set_positions(positions)
        self.status_label.config(text="📦 Compacted for navigation")
    
    def go_random(self):
        """Go to random safe position"""
        import random
        safe_ranges = {
            'joint_lift': (0.2, 0.8),
            'joint_arm_l0': (0.0, 0.08),
            'joint_arm_l1': (0.0, 0.06),
            'joint_arm_l2': (0.0, 0.04),
            'joint_wrist_yaw': (-0.5, 0.5),
            'joint_wrist_pitch': (-0.2, 0.2),
            'joint_head_pan': (-0.5, 0.5),
            'joint_head_tilt': (-0.2, 0.1)
        }
        
        positions = {}
        for joint_name, (min_val, max_val) in safe_ranges.items():
            positions[joint_name] = random.uniform(min_val, max_val)
        
        self.set_positions(positions)
        self.status_label.config(text="🎲 Moved to random position")
    
    def set_positions(self, positions):
        """Set multiple joint positions"""
        for joint_name, position in positions.items():
            if joint_name in self.joints:
                self.joints[joint_name]['current'] = position
                if joint_name in self.sliders:
                    self.sliders[joint_name].set(position)
    
    def reset_all(self):
        """Reset all joints to zero"""
        self.go_home()
    
    def run_gui(self):
        """Run the GUI main loop"""
        if self.root:
            try:
                self.root.mainloop()
            except Exception as e:
                print(f"GUI error: {e}")
            finally:
                self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'robot_state_proc') and self.robot_state_proc:
                self.robot_state_proc.terminate()
                self.robot_state_proc.wait()
        except:
            pass
        
        try:
            if self.root:
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
    
    # Initialize ROS2
    rclpy.init()
    
    controller = None
    try:
        print("🚀 Starting Stretch Robot Control...")
        controller = StretchRobotControl()
        
        # Setup GUI
        controller.setup_gui()
        
        # Run ROS2 in background thread
        def spin_ros():
            try:
                rclpy.spin(controller)
            except Exception as e:
                print(f"ROS2 spinning error: {e}")
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        print("🎮 GUI starting - robot should move in RViz when you adjust sliders!")
        
        # Run GUI
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
                controller.cleanup()
                controller.destroy_node()
        except:
            pass
        try:
            rclpy.shutdown()
        except:
            pass

if __name__ == '__main__':
    main()
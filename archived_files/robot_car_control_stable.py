#!/usr/bin/env python3

import rclpy
import threading
import queue
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import time
#!/usr/bin/env python3

import rclpy
import threading
import queue
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import time
import math
from rclpy.executors import SingleThreadedExecutor
from rclpy.executors import SingleThreadedExecutor


class StretchCarControl(Node):
    def __init__(self):
        super().__init__('stretch_car_control_stable')
        
        # Publishers
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Robot state
        self.robot_x = -3.0 # Start at the safe spawn location
        self.robot_y = 3.0  # Start at the safe spawn location
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
        
        self.wheel_positions = {'joint_left_wheel': 0.0, 'joint_right_wheel': 0.0}
        self.linear_speed = 0.0
        self.angular_speed = 0.0
        self.is_moving = False
        self.sliders = {}
        self.root = None
        
        # Threading for ROS
        self.executor = rclpy.executors.SingleThreadedExecutor()
        self.executor.add_node(self)
        self.ros_thread = threading.Thread(target=self.executor.spin, daemon=True)
        self.ros_thread.start()
        
        print("✅ Stretch car control initialized")

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🚗 Stretch Robot Car Control (Stable)")
        # ... (rest of the GUI setup is identical to the original)
        self.root.geometry("700x900")
        self.root.configure(bg='#1a1a1a')
        
        title = tk.Label(self.root, text="🚗 Stretch Robot - Car Control", 
                        font=('Arial', 18, 'bold'), fg='#00ff00', bg='#1a1a1a')
        title.pack(pady=15)
        
        self.status_label = tk.Label(self.root, text="✅ Ready to drive!",
                                   fg='#00ff00', bg='#1a1a1a', font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        self.position_label = tk.Label(self.root, text=f"📍 Position: ({self.robot_x:.1f}, {self.robot_y:.1f}) θ=0.0°",
                                     fg='#ffff00', bg='#1a1a1a', font=('Arial', 11))
        self.position_label.pack(pady=5)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a')
        style.configure('TNotebook.Tab', background='#333333', foreground='white')
        
        notebook = ttk.Notebook(self.root)
        
        drive_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(drive_frame, text="🚗 Drive")
        self.create_drive_tab(drive_frame)
        
        joint_frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(joint_frame, text="🦾 Joints")
        self.create_joint_tab(joint_frame)
        
        notebook.pack(expand=True, fill='both', padx=15, pady=10)
        
        self.create_control_buttons()
        
        print("✅ GUI setup complete")
        # Schedule periodic updates for robot state and publishing
        self.root.after(50, self.update_robot_gui_and_ros)
        self.root.mainloop()

    def update_robot_gui_and_ros(self):
        """This function updates the GUI and publishes ROS messages."""
        self.update_robot() # Update robot state and publish transforms
        # Reschedule the callback
        self.root.after(50, self.update_robot_gui_and_ros)

    # ... (All other methods like create_drive_tab, update_joint, etc., are identical to the original)
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
        
        self.linear_scale = tk.Scale(linear_frame, from_=0.0, to=1.0, resolution=0.1,
                                   orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white',
                                   command=self.update_linear_speed)
        self.linear_scale.set(0.5)
        self.linear_scale.pack(side=tk.RIGHT, padx=10)
        
        # Angular speed
        angular_frame = tk.Frame(speed_frame, bg='#2d2d2d')
        angular_frame.pack(pady=5, fill='x', padx=10)
        
        tk.Label(angular_frame, text="Turn Speed (rad/s):", 
                font=('Arial', 11), fg='white', bg='#2d2d2d').pack(side=tk.LEFT)
        
        self.angular_scale = tk.Scale(angular_frame, from_=0.0, to=2.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, length=300, bg='#2d2d2d', fg='white',
                                    command=self.update_angular_speed)
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
        
        # Forward
        tk.Button(button_grid, text="⬆️\nForward", bg='#4CAF50', **btn_style,
                 command=self.drive_forward).grid(row=0, column=1, padx=8, pady=8)
        
        # Left and Right
        tk.Button(button_grid, text="⬅️\nLeft", bg='#2196F3', **btn_style,
                 command=self.drive_left).grid(row=1, column=0, padx=8, pady=8)
        
        tk.Button(button_grid, text="🛑\nSTOP", bg='#F44336', **btn_style,
                 command=self.drive_stop).grid(row=1, column=1, padx=8, pady=8)
        
        tk.Button(button_grid, text="➡️\nRight", bg='#2196F3', **btn_style,
                 command=self.drive_right).grid(row=1, column=2, padx=8, pady=8)
        
        # Backward
        tk.Button(button_grid, text="⬇️\nBackward", bg='#FF9800', **btn_style,
                 command=self.drive_backward).grid(row=2, column=1, padx=8, pady=8)
        
        # Advanced controls
        advanced_frame = tk.Frame(drive_frame, bg='#2d2d2d')
        advanced_frame.pack(pady=10)
        
        tk.Button(advanced_frame, text="🔄 Spin Left", bg='#9C27B0', 
                 font=('Arial', 10, 'bold'), fg='white', width=12, height=1,
                 command=self.spin_left).pack(side=tk.LEFT, padx=5)
        
        tk.Button(advanced_frame, text="🔄 Spin Right", bg='#9C27B0', 
                 font=('Arial', 10, 'bold'), fg='white', width=12, height=1,
                 command=self.spin_right).pack(side=tk.LEFT, padx=5)
    def create_joint_tab(self, parent):
        canvas = tk.Canvas(parent, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        for joint_name in self.joints:
            self.create_joint_control(scrollable_frame, joint_name)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
    def create_joint_control(self, parent, joint_name):
        joint_info = self.joints[joint_name]
        frame = tk.Frame(parent, bg='#3d3d3d', relief='raised', bd=2)
        frame.pack(fill='x', padx=5, pady=5)
        header = tk.Frame(frame, bg='#3d3d3d')
        header.pack(fill='x', padx=8, pady=5)
        name_label = tk.Label(header, text=joint_name.replace('joint_', '').replace('_', ' ').title(), font=('Arial', 11, 'bold'), bg='#3d3d3d', fg='white')
        name_label.pack(side=tk.LEFT)
        value_label = tk.Label(header, text=f"{joint_info['current']:.3f}", font=('Arial', 11, 'bold'), bg='#3d3d3d', fg='#00ff00')
        value_label.pack(side=tk.RIGHT)
        slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'], resolution=0.01, orient=tk.HORIZONTAL, length=400, bg='#3d3d3d', fg='white', activebackground='#555555', command=lambda val, jname=joint_name, vlabel=value_label: self.update_joint(jname, val, vlabel))
        slider.pack(fill='x', padx=8, pady=5)
        slider.set(joint_info['current'])
        self.sliders[joint_name] = slider
        range_label = tk.Label(frame, text=f"Range: {joint_info['min']:.2f} to {joint_info['max']:.2f}", font=('Arial', 9), bg='#3d3d3d', fg='#888888')
        range_label.pack(pady=2)
    def create_control_buttons(self):
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=15)
        row1 = tk.Frame(button_frame, bg='#1a1a1a')
        row1.pack(pady=5)
        tk.Button(row1, text="🏠 Home", command=self.go_home, bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'), width=12, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(row1, text="🎯 Demo Drive", command=self.demo_drive, bg='#E91E63', fg='white', font=('Arial', 11, 'bold'), width=12, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(row1, text="📍 Reset Position", command=self.reset_position, bg='#607D8B', fg='white', font=('Arial', 11, 'bold'), width=12, height=2).pack(side=tk.LEFT, padx=5)
    def update_linear_speed(self, value): self.max_linear = float(value); self.status_label.config(text=f"🏎️ Max linear speed: {self.max_linear:.1f} m/s")
    def update_angular_speed(self, value): self.max_angular = float(value); self.status_label.config(text=f"🔄 Max turn speed: {self.max_angular:.1f} rad/s")
    def update_joint(self, joint_name, value, value_label): self.joints[joint_name]['current'] = float(value); value_label.config(text=f"{float(value):.3f}"); self.status_label.config(text=f"🎮 {joint_name.replace('joint_', '')} = {float(value):.3f}")
    def drive_forward(self): self.linear_speed = self.linear_scale.get(); self.angular_speed = 0.0; self.is_moving = True; self.status_label.config(text="⬆️ Driving forward")
    def drive_backward(self): self.linear_speed = -self.linear_scale.get(); self.angular_speed = 0.0; self.is_moving = True; self.status_label.config(text="⬇️ Driving backward")
    def drive_left(self): self.linear_speed = 0.0; self.angular_speed = self.angular_scale.get(); self.is_moving = True; self.status_label.config(text="⬅️ Turning left")
    def drive_right(self): self.linear_speed = 0.0; self.angular_speed = -self.angular_scale.get(); self.is_moving = True; self.status_label.config(text="➡️ Turning right")
    def spin_left(self): self.linear_speed = 0.0; self.angular_speed = self.angular_scale.get() * 1.5; self.is_moving = True; self.status_label.config(text="🔄 Spinning left")
    def spin_right(self): self.linear_speed = 0.0; self.angular_speed = -self.angular_scale.get() * 1.5; self.is_moving = True; self.status_label.config(text="🔄 Spinning right")
    def drive_stop(self): self.linear_speed = 0.0; self.angular_speed = 0.0; self.is_moving = False; self.status_label.config(text="🛑 Stopped")
    def go_home(self):
        for joint_name in self.joints: self.joints[joint_name]['current'] = 0.0;
        if joint_name in self.sliders: self.sliders[joint_name].set(0.0)
        self.drive_stop(); self.status_label.config(text="🏠 Home position")
    def reset_position(self):
        self.robot_x = -3.0; self.robot_y = 3.0; self.robot_theta = 0.0
        self.wheel_positions['joint_left_wheel'] = 0.0; self.wheel_positions['joint_right_wheel'] = 0.0
        self.drive_stop(); self.status_label.config(text="📍 Position reset to safe spawn")
    def demo_drive(self):
        self.status_label.config(text="🎯 Demo drive not available in stable mode")
    def update_robot(self):
        current_time = time.time(); dt = current_time - self.last_time; self.last_time = current_time
        if self.is_moving:
            self.robot_x += self.linear_speed * math.cos(self.robot_theta) * dt
            self.robot_y += self.linear_speed * math.sin(self.robot_theta) * dt
            self.robot_theta += self.angular_speed * dt
            self.robot_theta = math.atan2(math.sin(self.robot_theta), math.cos(self.robot_theta))
            left_wheel_speed = self.linear_speed - (self.angular_speed * self.wheel_base / 2.0)
            right_wheel_speed = self.linear_speed + (self.angular_speed * self.wheel_base / 2.0)
            self.wheel_positions['joint_left_wheel'] += (left_wheel_speed / self.wheel_radius) * dt
            self.wheel_positions['joint_right_wheel'] += (right_wheel_speed / self.wheel_radius) * dt
        self.position_label.config(text=f"📍 Position: ({self.robot_x:.2f}, {self.robot_y:.2f}) θ={math.degrees(self.robot_theta):.1f}°")
        self.publish_transforms(); self.publish_joint_states()
    def publish_transforms(self):
        t = TransformStamped(); t.header.stamp = self.get_clock().now().to_msg(); t.header.frame_id = 'world'; t.child_frame_id = 'base_link'
        t.transform.translation.x = self.robot_x; t.transform.translation.y = self.robot_y; t.transform.translation.z = 0.1
        t.transform.rotation.z = math.sin(self.robot_theta / 2.0); t.transform.rotation.w = math.cos(self.robot_theta / 2.0)
        self.tf_broadcaster.sendTransform(t)
    def publish_joint_states(self):
        msg = JointState(); msg.header.stamp = self.get_clock().now().to_msg()
        joint_names = list(self.joints.keys()); joint_positions = [self.joints[name]['current'] for name in joint_names]
        joint_names.extend(['joint_left_wheel', 'joint_right_wheel']); joint_positions.extend([self.wheel_positions['joint_left_wheel'], self.wheel_positions['joint_right_wheel']])
        msg.name = joint_names; msg.position = joint_positions
        self.joint_pub.publish(msg)

def main():
    controller = StretchCarControl()
    try:
        controller.setup_gui()
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()

if __name__ == '__main__':
    rclpy.init()
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


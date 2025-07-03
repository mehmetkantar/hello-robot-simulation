import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist
import tkinter as tk
from tkinter import ttk
import threading
import time
import signal
import sys

class SimpleStretchControl(Node):
    def __init__(self):
        super().__init__('simple_stretch_control')
        
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
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
        
        self.sliders = {}
        self.root = None
        self.drive_speed = 0.5
        self.turn_speed = 0.5
        
        self.timer = self.create_timer(0.1, self.publish_joint_states)
        
        print("✅ Simple robot control node initialized")
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🤖 Simple Stretch Control")
        self.root.geometry("600x800")
        self.root.configure(bg='#2b2b2b')
        
        title = tk.Label(self.root, text="🤖 Simple Stretch Robot Control", 
                        font=('Arial', 16, 'bold'), fg='white', bg='#2b2b2b')
        title.pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="✅ Ready",
                                   fg='#4CAF50', bg='#2b2b2b', font=('Arial', 12))
        self.status_label.pack(pady=5)
        
        # Create Notebook for tabs
        notebook = ttk.Notebook(self.root)
        
        joint_tab = tk.Frame(notebook, bg='#2b2b2b')
        drive_tab = tk.Frame(notebook, bg='#2b2b2b')
        
        notebook.add(joint_tab, text='🔧 Joints')
        notebook.add(drive_tab, text='🚗 Drive')
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.create_joint_tab(joint_tab)
        self.create_drive_tab(drive_tab)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#2b2b2b')
        button_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        
        tk.Button(button_frame, text="🏠 Home", command=self.go_home,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), 
                 width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🎯 Test", command=self.test_movement,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'), 
                 width=10).pack(side=tk.LEFT, padx=5)
        
        print("✅ GUI setup complete")

    def create_joint_tab(self, parent):
        canvas = tk.Canvas(parent, bg='#2b2b2b', highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for joint_name in self.joints:
            self.create_joint_control(scrollable_frame, joint_name)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_drive_tab(self, parent):
        drive_frame = tk.Frame(parent, bg='#2b2b2b')
        drive_frame.pack(pady=20, padx=20)

        # Speed control
        speed_frame = tk.Frame(drive_frame, bg='#2b2b2b')
        speed_frame.pack(pady=10)
        tk.Label(speed_frame, text="Drive Speed:", font=('Arial', 12, 'bold'), fg='white', bg='#2b2b2b').pack(side=tk.LEFT)
        drive_speed_slider = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                length=200, bg='#3d3d3d', fg='white', command=self.update_drive_speed)
        drive_speed_slider.set(self.drive_speed)
        drive_speed_slider.pack(side=tk.LEFT, padx=10)

        turn_speed_frame = tk.Frame(drive_frame, bg='#2b2b2b')
        turn_speed_frame.pack(pady=10)
        tk.Label(turn_speed_frame, text="Turn Speed:", font=('Arial', 12, 'bold'), fg='white', bg='#2b2b2b').pack(side=tk.LEFT)
        turn_speed_slider = tk.Scale(turn_speed_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                                length=200, bg='#3d3d3d', fg='white', command=self.update_turn_speed)
        turn_speed_slider.set(self.turn_speed)
        turn_speed_slider.pack(side=tk.LEFT, padx=10)

        # Drive buttons
        button_grid = tk.Frame(drive_frame, bg='#2b2b2b')
        button_grid.pack(pady=20)

        btn_style = {'font': ('Arial', 14, 'bold'), 'fg': 'white', 'width': 5, 'height': 2}

        tk.Button(button_grid, text="⬆", **btn_style, bg='#444', command=self.drive_forward).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(button_grid, text="⬅", **btn_style, bg='#444', command=self.drive_left).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(button_grid, text="🛑", **btn_style, bg='#d32f2f', command=self.drive_stop).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(button_grid, text="➡", **btn_style, bg='#444', command=self.drive_right).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(button_grid, text="⬇", **btn_style, bg='#444', command=self.drive_backward).grid(row=2, column=1, padx=5, pady=5)

    def update_drive_speed(self, value):
        self.drive_speed = float(value)
        self.status_label.config(text=f"🚗 Drive speed set to {self.drive_speed:.1f}")

    def update_turn_speed(self, value):
        self.turn_speed = float(value)
        self.status_label.config(text=f"🚗 Turn speed set to {self.turn_speed:.1f}")

    def drive(self, linear, angular):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.cmd_vel_pub.publish(msg)

    def drive_forward(self):
        self.drive(self.drive_speed, 0.0)
        self.status_label.config(text="🚗 Driving forward")

    def drive_backward(self):
        self.drive(-self.drive_speed, 0.0)
        self.status_label.config(text="🚗 Driving backward")

    def drive_left(self):
        self.drive(0.0, self.turn_speed)
        self.status_label.config(text="🚗 Turning left")

    def drive_right(self):
        self.drive(0.0, -self.turn_speed)
        self.status_label.config(text="🚗 Turning right")

    def drive_stop(self):
        self.drive(0.0, 0.0)
        self.status_label.config(text="🛑 Drive stopped")
    
    def create_joint_control(self, parent, joint_name):
        joint_info = self.joints[joint_name]
        
        frame = tk.Frame(parent, bg='#3d3d3d', relief='groove', bd=2)
        frame.pack(fill='x', padx=5, pady=3)
        
        header = tk.Frame(frame, bg='#3d3d3d')
        header.pack(fill='x', padx=5, pady=3)
        
        tk.Label(header, text=joint_name.replace('joint_', '').replace('_', ' ').title(),
                font=('Arial', 10, 'bold'), bg='#3d3d3d', fg='white').pack(side=tk.LEFT)
        
        value_label = tk.Label(header, text=f"{joint_info['current']:.3f}",
                             font=('Arial', 10), bg='#3d3d3d', fg='#00ff00')
        value_label.pack(side=tk.RIGHT)
        
        slider = tk.Scale(frame, from_=joint_info['min'], to=joint_info['max'],
                        resolution=0.01, orient=tk.HORIZONTAL, length=400,
                        bg='#3d3d3d', fg='white',
                        command=lambda val, jname=joint_name, vlabel=value_label: 
                               self.update_joint(jname, val, vlabel))
        slider.pack(fill='x', padx=5, pady=3)
        slider.set(joint_info['current'])
        
        self.sliders[joint_name] = slider
    
    def update_joint(self, joint_name, value, value_label):
        self.joints[joint_name]['current'] = float(value)
        value_label.config(text=f"🎮 {joint_name.replace('joint_', '')} = {float(value):.3f}")
    
    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        
        msg.name = list(self.joints.keys())
        msg.position = [self.joints[name]['current'] for name in msg.name]
        msg.velocity = [0.0] * len(msg.name)
        msg.effort = [0.0] * len(msg.name)
        
        self.joint_pub.publish(msg)
    
    def go_home(self):
        for joint_name in self.joints:
            self.joints[joint_name]['current'] = 0.0
            if joint_name in self.sliders:
                self.sliders[joint_name].set(0.0)
        self.drive_stop()
        self.status_label.config(text="🏠 Moved to home position")
    
    def test_movement(self):
        self.status_label.config(text="🎯 Testing movement...")
        
        def animate():
            self.go_home()
            time.sleep(1)
            self.joints['joint_lift']['current'] = 0.5
            self.sliders['joint_lift'].set(0.5)
            time.sleep(1)
            self.joints['joint_arm_l0']['current'] = 0.08
            self.sliders['joint_arm_l0'].set(0.08)
            time.sleep(1)
            self.joints['joint_head_pan']['current'] = 0.5
            self.sliders['joint_head_pan'].set(0.5)
            time.sleep(1)
            self.go_home()
            self.status_label.config(text="✅ Test complete!")
        
        threading.Thread(target=animate, daemon=True).start()
    
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
    
    rclpy.init()
    
    controller = None
    try:
        controller = SimpleStretchControl()
        controller.setup_gui()
        
        def spin_ros():
            try:
                rclpy.spin(controller)
            except:
                pass
        
        ros_thread = threading.Thread(target=spin_ros, daemon=True)
        ros_thread.start()
        
        print("🚀 Starting GUI...")
        controller.run_gui()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if controller:
            controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

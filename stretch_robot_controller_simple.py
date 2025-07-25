#!/usr/bin/env python3
"""
Simple Stretch Robot Controller GUI (without camera feeds to avoid Qt/OpenCV conflicts)
A clean, modern interface for controlling the Hello Robot Stretch
"""

import sys
import time
import numpy as np
import os

# Fix Qt/OpenCV plugin conflicts before any Qt imports
os.environ['QT_QPA_PLATFORM'] = 'xcb'
cv_qt_plugin_path = '/home/user/.local/lib/python3.10/site-packages/cv2/qt/plugins'
if cv_qt_plugin_path in os.environ.get('QT_PLUGIN_PATH', ''):
    qt_plugin_path = os.environ['QT_PLUGIN_PATH']
    paths = [p for p in qt_plugin_path.split(':') if cv_qt_plugin_path not in p]
    os.environ['QT_PLUGIN_PATH'] = ':'.join(paths)
else:
    os.environ.pop('QT_PLUGIN_PATH', None)

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Try to import MuJoCo for direct control
sys.path.append('/home/user/stretch_mujoco')
try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.actuators import Actuators
    MUJOCO_AVAILABLE = True
    print("✅ MuJoCo available for direct control")
except ImportError as e:
    print(f"⚠️ MuJoCo not available: {e}")
    MUJOCO_AVAILABLE = False

# Keep ROS2 as backup
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from sensor_msgs.msg import JointState
    from std_msgs.msg import Float64
    ROS2_AVAILABLE = True
    print("✅ ROS2 available for backup control")
except ImportError as e:
    print(f"⚠️ ROS2 not available: {e}")
    ROS2_AVAILABLE = False


class ModernSlider(QWidget):
    """Custom modern-looking slider with value display"""
    valueChanged = pyqtSignal(float)
    
    def __init__(self, min_val, max_val, initial_val, label, unit="", parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Label with value display
        self.label = QLabel(f"{label}: {initial_val:.2f}{unit}")
        self.label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        # Custom slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(int(min_val * 100), int(max_val * 100))
        self.slider.setValue(int(initial_val * 100))
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: 1px solid #2980b9;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3498db, stop:1 #2980b9);
                border: 1px solid #2980b9;
                height: 8px;
                border-radius: 4px;
            }
        """)
        
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.base_label = label
        
        self.slider.valueChanged.connect(self._on_value_changed)
        
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)
    
    def _on_value_changed(self, value):
        real_value = value / 100.0
        self.label.setText(f"{self.base_label}: {real_value:.2f}{self.unit}")
        self.valueChanged.emit(real_value)
    
    def setValue(self, value):
        self.slider.setValue(int(value * 100))


class ModernButton(QPushButton):
    """Custom modern-looking button"""
    def __init__(self, text, color="#3498db", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(45)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.3)};
                transform: translateY(1px);
            }}
        """)
    
    def _darken_color(self, color, factor=0.1):
        """Darken a hex color by a factor"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * (1 - factor)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


class VirtualJoystick(QWidget):
    """Virtual joystick for base control"""
    positionChanged = pyqtSignal(float, float)  # x, y (-1 to 1)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.center_x = 100
        self.center_y = 100
        self.knob_x = 100
        self.knob_y = 100
        self.max_distance = 80
        self.dragging = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw outer circle
        painter.setBrush(QBrush(QColor(52, 73, 94)))
        painter.setPen(QPen(QColor(149, 165, 166), 3))
        painter.drawEllipse(20, 20, 160, 160)
        
        # Draw center cross
        painter.setPen(QPen(QColor(189, 195, 199), 2))
        painter.drawLine(100, 30, 100, 170)
        painter.drawLine(30, 100, 170, 100)
        
        # Draw knob
        painter.setBrush(QBrush(QColor(52, 152, 219)))
        painter.setPen(QPen(QColor(41, 128, 185), 2))
        painter.drawEllipse(self.knob_x - 15, self.knob_y - 15, 30, 30)
        
        # Properly end the painter to fix Qt warnings
        painter.end()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            distance = ((event.x() - self.center_x) ** 2 + (event.y() - self.center_y) ** 2) ** 0.5
            if distance <= self.max_distance:
                self.dragging = True
                self.knob_x = event.x()
                self.knob_y = event.y()
                self._emit_position()
                self.update()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            dx = event.x() - self.center_x
            dy = event.y() - self.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance <= self.max_distance:
                self.knob_x = event.x()
                self.knob_y = event.y()
            else:
                # Constrain to circle
                angle = np.arctan2(dy, dx)
                self.knob_x = self.center_x + self.max_distance * np.cos(angle)
                self.knob_y = self.center_y + self.max_distance * np.sin(angle)
            
            self._emit_position()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.knob_x = self.center_x
            self.knob_y = self.center_y
            self._emit_position()
            self.update()
    
    def _emit_position(self):
        # Convert to -1 to 1 range
        x = (self.knob_x - self.center_x) / self.max_distance
        y = -(self.knob_y - self.center_y) / self.max_distance  # Invert Y
        self.positionChanged.emit(x, y)


class StretchRobotController(QMainWindow):
    """Main robot controller window"""
    
    def __init__(self):
        super().__init__()
        self.node = None
        self.sim = None  # MuJoCo simulation reference
        
        # Initialize control systems
        if MUJOCO_AVAILABLE:
            self.init_mujoco_control()
        elif ROS2_AVAILABLE:
            self.init_ros()
        
        self.init_ui()
        
        # Control state
        self.base_linear = 0.0
        self.base_angular = 0.0
        self.joint_positions = {}
        
        # Timers
        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self.publish_controls)
        self.control_timer.start(50)  # 20Hz
        
    def init_mujoco_control(self):
        """Initialize MuJoCo simulation for direct control"""
        print("🤖 Initializing direct MuJoCo control...")
        try:
            # Connect to existing simulation by trying to find a running instance
            # This is a simple approach - we'll look for the simulation instance
            self.sim = None
            self.find_existing_simulation()
            
            if not self.sim:
                print("⚠️ No existing simulation found")
        except Exception as e:
            print(f"❌ Failed to initialize MuJoCo control: {e}")
    
    def find_existing_simulation(self):
        """Try to find an existing simulation instance"""
        # This is a placeholder - in a real system you'd implement proper simulation discovery
        # For now, we'll just note that simulation access will be set up externally
        print("🔍 Looking for existing MuJoCo simulation...")
        
    def init_ros(self):
        """Initialize ROS2 node and publishers/subscribers"""
        if not rclpy.ok():
            rclpy.init()
        
        self.node = Node('stretch_controller_gui_simple')
        
        # Publishers
        self.cmd_vel_pub = self.node.create_publisher(Twist, '/stretch/cmd_vel', 10)
        self.lift_pub = self.node.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
        self.arm_pub = self.node.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
        self.wrist_yaw_pub = self.node.create_publisher(Float64, '/stretch_controller/wrist_yaw/command', 10)
        self.wrist_pitch_pub = self.node.create_publisher(Float64, '/stretch_controller/wrist_pitch/command', 10)
        self.wrist_roll_pub = self.node.create_publisher(Float64, '/stretch_controller/wrist_roll/command', 10)
        self.gripper_pub = self.node.create_publisher(Float64, '/stretch_controller/gripper_joint/command', 10)
        
        # Subscribers
        self.joint_sub = self.node.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🤖 Stretch Robot Controller (Simple)")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎮 Stretch Robot Controller")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 15px;
                background-color: #3498db;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        main_layout = QHBoxLayout()
        
        # Left panel - Base controls
        left_panel = self.create_base_controls()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Arm controls  
        right_panel = self.create_arm_controls()
        main_layout.addWidget(right_panel, 1)
        
        layout.addLayout(main_layout)
        
        # Status panel
        status_panel = self.create_status_panel()
        layout.addWidget(status_panel)
        
        central_widget.setLayout(layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #34495e;
                color: white;
                font-weight: bold;
            }
        """)
        self.status_bar.showMessage("🟢 Robot Controller Ready")
    
    def create_base_controls(self):
        """Create base movement controls"""
        group = QGroupBox("🚗 Base Movement")
        layout = QVBoxLayout()
        
        # Virtual joystick
        joystick_label = QLabel("Virtual Joystick:")
        joystick_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(joystick_label)
        
        self.joystick = VirtualJoystick()
        self.joystick.positionChanged.connect(self.on_joystick_moved)
        joystick_container = QWidget()
        joystick_container_layout = QHBoxLayout()
        joystick_container_layout.addStretch()
        joystick_container_layout.addWidget(self.joystick)
        joystick_container_layout.addStretch()
        joystick_container.setLayout(joystick_container_layout)
        layout.addWidget(joystick_container)
        
        # Speed controls
        self.max_linear_speed = ModernSlider(0.0, 2.0, 0.5, "Max Linear Speed", " m/s")
        self.max_angular_speed = ModernSlider(0.0, 3.0, 1.0, "Max Angular Speed", " rad/s")
        layout.addWidget(self.max_linear_speed)
        layout.addWidget(self.max_angular_speed)
        
        # Emergency stop
        self.emergency_stop_btn = ModernButton("🛑 EMERGENCY STOP", "#e74c3c")
        self.emergency_stop_btn.clicked.connect(self.emergency_stop)
        layout.addWidget(self.emergency_stop_btn)
        
        group.setLayout(layout)
        return group
    
    def create_arm_controls(self):
        """Create arm control panel"""
        group = QGroupBox("🦾 Arm Control")
        layout = QVBoxLayout()
        
        # Lift control
        self.lift_slider = ModernSlider(0.0, 1.1, 0.5, "Lift Height", " m")
        self.lift_slider.valueChanged.connect(self.on_lift_changed)
        layout.addWidget(self.lift_slider)
        
        # Arm extension
        self.arm_slider = ModernSlider(0.0, 0.5, 0.1, "Arm Extension", " m")
        self.arm_slider.valueChanged.connect(self.on_arm_changed)
        layout.addWidget(self.arm_slider)
        
        # Wrist controls
        self.wrist_yaw_slider = ModernSlider(-1.57, 1.57, 0.0, "Wrist Yaw", " rad")
        self.wrist_yaw_slider.valueChanged.connect(self.on_wrist_yaw_changed)
        layout.addWidget(self.wrist_yaw_slider)
        
        self.wrist_pitch_slider = ModernSlider(-0.5, 0.5, 0.0, "Wrist Pitch", " rad")
        self.wrist_pitch_slider.valueChanged.connect(self.on_wrist_pitch_changed)
        layout.addWidget(self.wrist_pitch_slider)
        
        # Gripper control
        self.gripper_slider = ModernSlider(-0.1, 0.6, 0.0, "Gripper Opening", " m")
        self.gripper_slider.valueChanged.connect(self.on_gripper_changed)
        layout.addWidget(self.gripper_slider)
        
        # Quick actions
        quick_actions_layout = QHBoxLayout()
        self.home_btn = ModernButton("🏠 Home", "#27ae60")
        self.stow_btn = ModernButton("📦 Stow", "#f39c12")
        self.home_btn.clicked.connect(self.go_home)
        self.stow_btn.clicked.connect(self.stow_robot)
        quick_actions_layout.addWidget(self.home_btn)
        quick_actions_layout.addWidget(self.stow_btn)
        layout.addLayout(quick_actions_layout)
        
        group.setLayout(layout)
        return group
    
    def create_status_panel(self):
        """Create status panel"""
        group = QGroupBox("📊 Robot Status")
        layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(120)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.status_text.setReadOnly(True)
        self.status_text.append("🟢 System initialized")
        self.status_text.append("🔄 Waiting for joint states...")
        
        layout.addWidget(self.status_text)
        group.setLayout(layout)
        return group
    
    def on_joystick_moved(self, x, y):
        """Handle joystick movement"""
        max_linear = self.max_linear_speed.slider.value() / 100.0
        max_angular = self.max_angular_speed.slider.value() / 100.0
        
        self.base_linear = y * max_linear
        self.base_angular = -x * max_angular  # Negative for intuitive control
        
        # Debug: Print joystick values
        if abs(x) > 0.01 or abs(y) > 0.01:
            print(f"🕹️ Joystick moved: x={x:.3f}, y={y:.3f} -> linear={self.base_linear:.3f}, angular={self.base_angular:.3f}")
    
    def on_lift_changed(self, value):
        """Handle lift slider change"""
        print(f"🏗️ Lift command: {value:.3f}m")
        
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo control using relative movement
            try:
                # Get current position and calculate increment
                status = self.sim.pull_status()
                current_lift = status.lift.pos if hasattr(status, 'lift') and hasattr(status.lift, 'pos') else 0.5
                increment = value - current_lift
                
                if abs(increment) > 0.01:  # Only move if significant change
                    self.sim.move_by(Actuators.lift, increment)
                    print(f"✅ MuJoCo lift moved by: {increment:.3f}m (target: {value:.3f}m)")
            except Exception as e:
                print(f"❌ MuJoCo lift control error: {e}")
        elif ROS2_AVAILABLE and self.lift_pub:
            # ROS2 control
            msg = Float64()
            msg.data = value
            self.lift_pub.publish(msg)
    
    def on_arm_changed(self, value):
        """Handle arm extension slider change"""
        print(f"🦾 Arm command: {value:.3f}m")
        
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo control using relative movement
            try:
                # Get current position and calculate increment
                status = self.sim.pull_status()
                current_arm = status.arm.pos if hasattr(status, 'arm') and hasattr(status.arm, 'pos') else 0.1
                increment = value - current_arm
                
                if abs(increment) > 0.01:  # Only move if significant change
                    self.sim.move_by(Actuators.arm, increment)
                    print(f"✅ MuJoCo arm moved by: {increment:.3f}m (target: {value:.3f}m)")
            except Exception as e:
                print(f"❌ MuJoCo arm control error: {e}")
        elif ROS2_AVAILABLE and self.arm_pub:
            # ROS2 control
            msg = Float64()
            msg.data = value
            self.arm_pub.publish(msg)
    
    def on_wrist_yaw_changed(self, value):
        """Handle wrist yaw slider change"""
        print(f"🔄 Wrist Yaw: {value:.3f}rad")
        
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo control using relative movement
            try:
                # Get current position and calculate increment
                status = self.sim.pull_status()
                current_yaw = status.wrist_yaw.pos if hasattr(status, 'wrist_yaw') and hasattr(status.wrist_yaw, 'pos') else 0.0
                increment = value - current_yaw
                
                if abs(increment) > 0.01:  # Only move if significant change
                    self.sim.move_by(Actuators.wrist_yaw, increment)
                    print(f"✅ MuJoCo wrist yaw moved by: {increment:.3f}rad (target: {value:.3f}rad)")
            except Exception as e:
                print(f"❌ MuJoCo wrist yaw control error: {e}")
        elif ROS2_AVAILABLE and self.wrist_yaw_pub:
            # ROS2 control
            msg = Float64()
            msg.data = value
            self.wrist_yaw_pub.publish(msg)
    
    def on_wrist_pitch_changed(self, value):
        """Handle wrist pitch slider change"""
        print(f"↕️ Wrist Pitch: {value:.3f}rad")
        
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo control using relative movement
            try:
                # Get current position and calculate increment
                status = self.sim.pull_status()
                current_pitch = status.wrist_pitch.pos if hasattr(status, 'wrist_pitch') and hasattr(status.wrist_pitch, 'pos') else 0.0
                increment = value - current_pitch
                
                if abs(increment) > 0.01:  # Only move if significant change
                    self.sim.move_by(Actuators.wrist_pitch, increment)
                    print(f"✅ MuJoCo wrist pitch moved by: {increment:.3f}rad (target: {value:.3f}rad)")
            except Exception as e:
                print(f"❌ MuJoCo wrist pitch control error: {e}")
        elif ROS2_AVAILABLE and self.wrist_pitch_pub:
            # ROS2 control
            msg = Float64()
            msg.data = value
            self.wrist_pitch_pub.publish(msg)
    
    def on_gripper_changed(self, value):
        """Handle gripper slider change"""
        print(f"✋ Gripper: {value:.3f}m")
        
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo control using relative movement
            try:
                # Get current position and calculate increment
                status = self.sim.pull_status()
                current_gripper = status.gripper.pos if hasattr(status, 'gripper') and hasattr(status.gripper, 'pos') else 0.0
                increment = value - current_gripper
                
                if abs(increment) > 0.01:  # Only move if significant change
                    self.sim.move_by(Actuators.gripper, increment)
                    print(f"✅ MuJoCo gripper moved by: {increment:.3f}m (target: {value:.3f}m)")
            except Exception as e:
                print(f"❌ MuJoCo gripper control error: {e}")
        elif ROS2_AVAILABLE and self.gripper_pub:
            # ROS2 control
            msg = Float64()
            msg.data = value
            self.gripper_pub.publish(msg)
    
    def publish_controls(self):
        """Publish/send base movement controls"""
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo control for base
            if abs(self.base_linear) > 0.001 or abs(self.base_angular) > 0.001:
                try:
                    self.sim.set_base_velocity(self.base_linear, self.base_angular)
                except Exception as e:
                    print(f"❌ MuJoCo base control error: {e}")
        
        elif ROS2_AVAILABLE and self.node is not None:
            # ROS2 control for base
            rclpy.spin_once(self.node, timeout_sec=0.01)
            
            # Publish base velocity
            twist = Twist()
            twist.linear.x = self.base_linear
            twist.angular.z = self.base_angular
            self.cmd_vel_pub.publish(twist)
    
    def joint_state_callback(self, msg):
        """Handle joint state updates"""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]
        
        # Update status display
        status_text = f"📊 Joint Positions ({time.strftime('%H:%M:%S')}):\n"
        for name, pos in list(self.joint_positions.items())[:5]:  # Show first 5 joints
            status_text += f"  {name}: {pos:.3f}\n"
        
        # Update the status text
        self.status_text.clear()
        self.status_text.append(status_text)
    
    def emergency_stop(self):
        """Emergency stop - halt all movement"""
        self.base_linear = 0.0
        self.base_angular = 0.0
        
        # Reset joystick
        self.joystick.knob_x = self.joystick.center_x
        self.joystick.knob_y = self.joystick.center_y
        self.joystick.update()
        
        self.status_text.append("🛑 EMERGENCY STOP ACTIVATED")
        self.status_bar.showMessage("🔴 Emergency Stop - All Movement Halted")
    
    def go_home(self):
        """Move robot to home position"""
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo preset action
            try:
                self.sim.home()
                print("✅ MuJoCo home command sent")
            except Exception as e:
                print(f"❌ MuJoCo home error: {e}")
        
        # Also update GUI sliders
        self.lift_slider.setValue(0.9)
        self.arm_slider.setValue(0.0)
        self.wrist_yaw_slider.setValue(0.0)
        self.wrist_pitch_slider.setValue(0.0)
        self.gripper_slider.setValue(0.0)
        
        self.status_text.append("🏠 Moving to home position")
        self.status_bar.showMessage("🟡 Moving to Home Position")
    
    def stow_robot(self):
        """Stow the robot"""
        if MUJOCO_AVAILABLE and self.sim:
            # Direct MuJoCo preset action
            try:
                self.sim.stow()
                print("✅ MuJoCo stow command sent")
            except Exception as e:
                print(f"❌ MuJoCo stow error: {e}")
        
        # Also update GUI sliders
        self.lift_slider.setValue(0.2)
        self.arm_slider.setValue(0.0)
        self.wrist_yaw_slider.setValue(0.0)
        self.wrist_pitch_slider.setValue(-0.3)
        self.gripper_slider.setValue(0.0)
        
        self.status_text.append("📦 Stowing robot")
        self.status_bar.showMessage("🟡 Stowing Robot")
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.node is not None:
            self.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set application icon and title
    app.setApplicationName("Stretch Robot Controller")
    app.setOrganizationName("Hello Robot")
    
    controller = StretchRobotController()
    controller.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Advanced Stretch Robot Controller GUI
A modern, aesthetic interface for controlling the Hello Robot Stretch
with simultaneous RViz and MuJoCo visualization.
"""

#!/usr/bin/env python3
import os
# Fix OpenCV Qt conflict BEFORE importing anything else
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
import cv2
# Remove OpenCV's Qt plugins from sys.path to avoid conflicts
cv2_path = cv2.__file__
if 'site-packages' in cv2_path:
    import sys
    cv2_qt_path = os.path.join(os.path.dirname(cv2_path), 'qt', 'plugins')
    if cv2_qt_path in os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', ''):
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'].replace(cv2_qt_path, '')

import sys
import time
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState, Image
from std_msgs.msg import Float64
from cv_bridge import CvBridge


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


class CameraWidget(QLabel):
    """Widget to display camera feeds"""
    def __init__(self, camera_name, parent=None):
        super().__init__(parent)
        self.camera_name = camera_name
        self.setFixedSize(320, 240)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #2c3e50;
                color: white;
                font-size: 12px;
            }
        """)
        self.setText(f"{camera_name}\nNo Image")
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
    
    def update_image(self, cv_image):
        """Update the displayed image"""
        try:
            # Convert OpenCV image to Qt format
            if len(cv_image.shape) == 3:
                h, w, ch = cv_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(cv_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            else:
                h, w = cv_image.shape
                bytes_per_line = w
                qt_image = QImage(cv_image.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
            
            pixmap = QPixmap.fromImage(qt_image)
            self.setPixmap(pixmap)
        except Exception as e:
            self.setText(f"{self.camera_name}\nError: {str(e)}")


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
        self.bridge = CvBridge()
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
        
    def init_ros(self):
        """Initialize ROS2 node and publishers/subscribers"""
        if not rclpy.ok():
            rclpy.init()
        
        self.node = Node('stretch_controller_gui')
        
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
        self.d405_sub = self.node.create_subscription(
            Image, '/camera/d405_camera/color/image_raw', 
            lambda msg: self.image_callback(msg, 'D405'), 10)
        self.d435i_sub = self.node.create_subscription(
            Image, '/camera/d435i_camera/color/image_raw',
            lambda msg: self.image_callback(msg, 'D435i'), 10)
        self.nav_sub = self.node.create_subscription(
            Image, '/camera/nav_camera/color/image_raw',
            lambda msg: self.image_callback(msg, 'Nav'), 10)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🤖 Stretch Robot Controller")
        self.setGeometry(100, 100, 1400, 900)
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
        
        main_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Cameras and status
        right_panel = self.create_status_panel()
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        
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
    
    def create_control_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎮 Robot Controls")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Base Control Group
        base_group = QGroupBox("🚗 Base Movement")
        base_layout = QVBoxLayout()
        
        # Virtual joystick
        joystick_label = QLabel("Virtual Joystick:")
        joystick_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        base_layout.addWidget(joystick_label)
        
        self.joystick = VirtualJoystick()
        self.joystick.positionChanged.connect(self.on_joystick_moved)
        joystick_container = QWidget()
        joystick_container_layout = QHBoxLayout()
        joystick_container_layout.addStretch()
        joystick_container_layout.addWidget(self.joystick)
        joystick_container_layout.addStretch()
        joystick_container.setLayout(joystick_container_layout)
        base_layout.addWidget(joystick_container)
        
        # Speed controls
        self.max_linear_speed = ModernSlider(0.0, 2.0, 0.5, "Max Linear Speed", " m/s")
        self.max_angular_speed = ModernSlider(0.0, 3.0, 1.0, "Max Angular Speed", " rad/s")
        base_layout.addWidget(self.max_linear_speed)
        base_layout.addWidget(self.max_angular_speed)
        
        # Emergency stop
        self.emergency_stop_btn = ModernButton("🛑 EMERGENCY STOP", "#e74c3c")
        self.emergency_stop_btn.clicked.connect(self.emergency_stop)
        base_layout.addWidget(self.emergency_stop_btn)
        
        base_group.setLayout(base_layout)
        layout.addWidget(base_group)
        
        # Arm Control Group
        arm_group = QGroupBox("🦾 Arm Control")
        arm_layout = QVBoxLayout()
        
        # Lift control
        self.lift_slider = ModernSlider(0.0, 1.1, 0.5, "Lift Height", " m")
        self.lift_slider.valueChanged.connect(self.on_lift_changed)
        arm_layout.addWidget(self.lift_slider)
        
        # Arm extension
        self.arm_slider = ModernSlider(0.0, 0.5, 0.1, "Arm Extension", " m")
        self.arm_slider.valueChanged.connect(self.on_arm_changed)
        arm_layout.addWidget(self.arm_slider)
        
        # Wrist controls
        self.wrist_yaw_slider = ModernSlider(-1.57, 1.57, 0.0, "Wrist Yaw", " rad")
        self.wrist_yaw_slider.valueChanged.connect(self.on_wrist_yaw_changed)
        arm_layout.addWidget(self.wrist_yaw_slider)
        
        self.wrist_pitch_slider = ModernSlider(-0.5, 0.5, 0.0, "Wrist Pitch", " rad")
        self.wrist_pitch_slider.valueChanged.connect(self.on_wrist_pitch_changed)
        arm_layout.addWidget(self.wrist_pitch_slider)
        
        # Gripper control
        self.gripper_slider = ModernSlider(-0.1, 0.6, 0.0, "Gripper Opening", " m")
        self.gripper_slider.valueChanged.connect(self.on_gripper_changed)
        arm_layout.addWidget(self.gripper_slider)
        
        # Quick actions
        quick_actions_layout = QHBoxLayout()
        self.home_btn = ModernButton("🏠 Home Position", "#27ae60")
        self.stow_btn = ModernButton("📦 Stow", "#f39c12")
        self.home_btn.clicked.connect(self.go_home)
        self.stow_btn.clicked.connect(self.stow_robot)
        quick_actions_layout.addWidget(self.home_btn)
        quick_actions_layout.addWidget(self.stow_btn)
        arm_layout.addLayout(quick_actions_layout)
        
        arm_group.setLayout(arm_layout)
        layout.addWidget(arm_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_status_panel(self):
        """Create the right status and camera panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📊 Status & Cameras")
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                padding: 10px;
                background-color: #27ae60;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Camera feeds
        camera_group = QGroupBox("📷 Camera Feeds")
        camera_layout = QGridLayout()
        
        self.d405_camera = CameraWidget("D405 Camera")
        self.d435i_camera = CameraWidget("D435i Camera")
        self.nav_camera = CameraWidget("Navigation Camera")
        
        camera_layout.addWidget(self.d405_camera, 0, 0)
        camera_layout.addWidget(self.d435i_camera, 0, 1)
        camera_layout.addWidget(self.nav_camera, 1, 0, 1, 2)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Robot status
        status_group = QGroupBox("🤖 Robot Status")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)
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
        
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def on_joystick_moved(self, x, y):
        """Handle joystick movement"""
        max_linear = self.max_linear_speed.slider.value() / 100.0
        max_angular = self.max_angular_speed.slider.value() / 100.0
        
        self.base_linear = y * max_linear
        self.base_angular = -x * max_angular  # Negative for intuitive control
    
    def on_lift_changed(self, value):
        """Handle lift slider change"""
        msg = Float64()
        msg.data = value
        self.lift_pub.publish(msg)
    
    def on_arm_changed(self, value):
        """Handle arm extension slider change"""
        msg = Float64()
        msg.data = value
        self.arm_pub.publish(msg)
    
    def on_wrist_yaw_changed(self, value):
        """Handle wrist yaw slider change"""
        msg = Float64()
        msg.data = value
        self.wrist_yaw_pub.publish(msg)
    
    def on_wrist_pitch_changed(self, value):
        """Handle wrist pitch slider change"""
        msg = Float64()
        msg.data = value
        self.wrist_pitch_pub.publish(msg)
    
    def on_gripper_changed(self, value):
        """Handle gripper slider change"""
        msg = Float64()
        msg.data = value
        self.gripper_pub.publish(msg)
    
    def publish_controls(self):
        """Publish base movement controls"""
        if self.node is not None:
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
        status_text = f"📊 Joint Positions (recent update {time.strftime('%H:%M:%S')}):\n"
        for name, pos in self.joint_positions.items():
            status_text += f"  {name}: {pos:.3f}\n"
        
        # Update the last few lines of status
        cursor = self.status_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.status_text.setTextCursor(cursor)
        
        # Limit status text length
        if self.status_text.document().lineCount() > 50:
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 10)
            cursor.removeSelectedText()
    
    def image_callback(self, msg, camera_name):
        """Handle camera image updates"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            if camera_name == 'D405':
                self.d405_camera.update_image(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            elif camera_name == 'D435i':
                self.d435i_camera.update_image(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            elif camera_name == 'Nav':
                self.nav_camera.update_image(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
                
        except Exception as e:
            print(f"Error processing {camera_name} image: {e}")
    
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
        self.lift_slider.setValue(0.9)
        self.arm_slider.setValue(0.0)
        self.wrist_yaw_slider.setValue(0.0)
        self.wrist_pitch_slider.setValue(0.0)
        self.gripper_slider.setValue(0.0)
        
        self.status_text.append("🏠 Moving to home position")
        self.status_bar.showMessage("🟡 Moving to Home Position")
    
    def stow_robot(self):
        """Stow the robot"""
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
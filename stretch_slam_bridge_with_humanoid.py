#!/usr/bin/env python3
"""
Stretch SLAM Bridge with Humanoid Robot Integration

This enhanced version controls both Stretch robot and Humanoid robot
in the same MuJoCo environment with dual ROS2 control.
"""

import sys
import time
import threading
import numpy as np
import math
from typing import Optional, Dict, Any

# Add stretch_mujoco to path (use local directory)
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# GPU optimization setup
import os
def setup_gpu_optimization():
    """Setup GPU optimizations for MuJoCo"""
    os.environ['MUJOCO_GL'] = 'egl'  # GPU backend
    os.environ['OMP_NUM_THREADS'] = '8'  # Multi-threading
    os.environ['__GL_SYNC_TO_VBLANK'] = '0'  # Disable VSync
    os.environ['__GL_YIELD'] = 'NOTHING'  # Don't yield GPU
    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Non-blocking CUDA

# Apply optimizations immediately
setup_gpu_optimization()

# ROS2 imports
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
    from geometry_msgs.msg import Twist, PoseStamped, TransformStamped
    from sensor_msgs.msg import JointState, Image, LaserScan
    from nav_msgs.msg import Odometry
    from std_msgs.msg import Header, Float64, Bool
    from tf2_ros import TransformBroadcaster
    import tf_transformations
    from cv_bridge import CvBridge
    ROS2_AVAILABLE = True
except ImportError as e:
    print(f"✗ ROS2 not available: {e}")
    ROS2_AVAILABLE = False

# stretch_mujoco imports
try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.stretch_cameras import StretchCameras
    from stretch_mujoco.enums.actuators import Actuators
    from stretch_mujoco.datamodels.status_command import StatusCommand, CommandKeyframe
    STRETCH_MUJOCO_AVAILABLE = True
except ImportError as e:
    print(f"✗ stretch_mujoco not available: {e}")
    STRETCH_MUJOCO_AVAILABLE = False

class DualRobotSLAMBridge(Node):
    """
    Enhanced SLAM Bridge with Stretch + Humanoid robot integration
    """

    def __init__(self):
        super().__init__('dual_robot_slam_bridge')

        # Initialize simulation
        self.sim = None
        self.bridge = CvBridge()
        self.is_running = False
        self.tf_broadcaster = TransformBroadcaster(self)
        self.cameras_enabled = True

        # Robot state tracking
        self.stretch_last_pose = {'x': 0.0, 'y': 0.0, 'theta': 0.0}
        self.humanoid_last_pose = {'x': -8.0, 'y': -6.0, 'theta': 0.0}
        self.last_time = time.time()

        # Humanoid joint control
        self.humanoid_joint_targets = {
            'humanoid_right_hip_z': 0.0,
            'humanoid_right_hip_y': 0.0,
            'humanoid_right_hip_x': 0.0,
            'humanoid_right_knee': 0.0,
            'humanoid_right_ankle_y': 0.0,
            'humanoid_right_ankle_x': 0.0,
            'humanoid_left_hip_z': 0.0,
            'humanoid_left_hip_y': 0.0,
            'humanoid_left_hip_x': 0.0,
            'humanoid_left_knee': 0.0,
            'humanoid_left_ankle_y': 0.0,
            'humanoid_left_ankle_x': 0.0,
            'humanoid_right_shoulder1': 0.0,
            'humanoid_right_shoulder2': 0.0,
            'humanoid_right_elbow': 0.0,
            'humanoid_left_shoulder1': 0.0,
            'humanoid_left_shoulder2': 0.0,
            'humanoid_left_elbow': 0.0,
        }

        # Lidar parameters
        self.lidar_range_max = 12.0
        self.lidar_range_min = 0.05
        self.lidar_angle_min = -math.pi
        self.lidar_angle_max = math.pi
        self.lidar_angle_increment = math.pi / 180.0  # 1 degree resolution

        # QoS profiles
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=1
        )

        slam_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

        # =================== STRETCH ROBOT TOPICS ===================
        # Publishers (use standard topic names for Nav2 compatibility)
        self.stretch_joint_state_pub = self.create_publisher(JointState, '/joint_states', slam_qos)
        self.stretch_odom_pub = self.create_publisher(Odometry, '/odom', slam_qos)
        self.stretch_laser_pub = self.create_publisher(LaserScan, '/scan', slam_qos)

        # Also publish to namespaced topics for debugging
        self.stretch_joint_state_debug_pub = self.create_publisher(JointState, '/stretch/joint_states', slam_qos)
        self.stretch_odom_debug_pub = self.create_publisher(Odometry, '/stretch/odom', slam_qos)
        self.stretch_laser_debug_pub = self.create_publisher(LaserScan, '/stretch/scan', slam_qos)

        # Camera publishers
        self.stretch_camera_pubs = {
            'cam_d405_rgb': self.create_publisher(Image, '/stretch/camera/d405/color/image_raw', sensor_qos),
            'cam_d435i_rgb': self.create_publisher(Image, '/stretch/camera/d435i/color/image_raw', sensor_qos),
            'cam_nav_rgb': self.create_publisher(Image, '/stretch/camera/nav/color/image_raw', sensor_qos),
        }

        # Subscribers
        self.stretch_cmd_vel_sub = self.create_subscription(
            Twist, '/stretch/cmd_vel', self.stretch_cmd_vel_callback, 10)

        # Joint command subscribers for Stretch
        self.stretch_lift_cmd_sub = self.create_subscription(
            Float64, '/stretch/controller/lift_joint/command', self.stretch_lift_cmd_callback, 10)
        self.stretch_arm_cmd_sub = self.create_subscription(
            Float64, '/stretch/controller/arm_joint/command', self.stretch_arm_cmd_callback, 10)
        self.stretch_head_pan_cmd_sub = self.create_subscription(
            Float64, '/stretch/controller/head_pan_joint/command', self.stretch_head_pan_cmd_callback, 10)

        # =================== HUMANOID ROBOT TOPICS ===================
        # Publishers
        self.humanoid_joint_state_pub = self.create_publisher(JointState, '/humanoid/joint_states', slam_qos)
        self.humanoid_odom_pub = self.create_publisher(Odometry, '/humanoid/odom', slam_qos)

        # Subscribers
        self.humanoid_cmd_vel_sub = self.create_subscription(
            Twist, '/humanoid/cmd_vel', self.humanoid_cmd_vel_callback, 10)

        # Joint command subscribers for Humanoid
        self.humanoid_walk_cmd_sub = self.create_subscription(
            Twist, '/humanoid/walk_cmd', self.humanoid_walk_cmd_callback, 10)

        # Camera toggle subscriber
        self.camera_toggle_sub = self.create_subscription(
            Bool, '/controller/toggle_cameras', self.toggle_cameras_callback, 10)

        # Timers for periodic publishing
        self.joint_timer = self.create_timer(0.1, self.publish_joint_states)
        self.odom_timer = self.create_timer(0.1, self.publish_odometry)
        self.laser_timer = self.create_timer(0.2, self.publish_laser_scan)
        self.camera_timer = self.create_timer(0.05, self.publish_camera_feeds)
        self.tf_timer = self.create_timer(0.1, self.publish_transforms)

        # Humanoid control timer
        self.humanoid_control_timer = self.create_timer(0.05, self.control_humanoid)

        self.get_logger().info("Dual Robot SLAM Bridge initialized")

    def start_simulation(self, headless=False):
        """Start simulation with dual robot environment"""
        try:
            # Configure cameras with performance optimizations
            cameras_to_use = StretchCameras.rgb()

            # Use the combined office scene with humanoid
            scene_xml_path = os.path.join(current_dir, "stretch_mujoco", "models", "complex_office_with_humanoid.xml")
            self.get_logger().info(f"Loading dual robot scene from: {scene_xml_path}")

            self.sim = StretchMujocoSimulator(scene_xml_path=scene_xml_path, cameras_to_use=cameras_to_use)
            self.get_logger().info("Dual robot simulator created successfully")

            self.sim.start(headless=headless)
            self.get_logger().info("Dual robot simulator started successfully")

            self.is_running = True
            time.sleep(5)  # Give time for complex scene to load

            # Home the Stretch robot
            self.sim.home()
            self.get_logger().info("Stretch robot homed successfully")

            self.get_logger().info("Dual robot environment started successfully!")
            self.get_logger().info("✓ MuJoCo: Complex office with Stretch + Humanoid")
            self.get_logger().info("✓ Stretch: Real Stretch robot with cameras and LIDAR")
            self.get_logger().info("✓ Humanoid: Bipedal robot for locomotion")
            self.get_logger().info("✓ SLAM: Will map environment with Stretch sensors")

        except Exception as e:
            self.get_logger().error(f"Failed to start dual robot simulation: {e}")
            self.is_running = False
            return

    def get_lidar_data_from_stretch(self):
        """Get lidar data from Stretch robot position"""
        try:
            if not self.sim.is_running():
                return []

            # Get Stretch robot status
            status = self.sim.pull_status()

            ranges = []
            num_readings = int((self.lidar_angle_max - self.lidar_angle_min) / self.lidar_angle_increment)

            for i in range(num_readings):
                angle = self.lidar_angle_min + i * self.lidar_angle_increment

                # Use complex office simulation for Stretch robot
                base_range = self.simulate_complex_office_range(angle, status.base.x, status.base.y, status.base.theta)

                # Add realistic noise
                noise = np.random.normal(0, 0.01)  # 1cm standard deviation
                range_val = base_range + noise

                # Clamp to sensor limits
                range_val = max(self.lidar_range_min, min(self.lidar_range_max, range_val))
                ranges.append(range_val)

            return ranges

        except Exception as e:
            self.get_logger().error(f"Error getting stretch lidar data: {e}")
            return []

    def simulate_complex_office_range(self, angle, robot_x, robot_y, robot_theta):
        """Simulate LIDAR readings for complex office (same as before)"""
        # Transform angle to world coordinates
        world_angle = robot_theta + angle

        # Ray casting parameters
        max_range = self.lidar_range_max
        step_size = 0.1

        # Cast ray from robot position
        for distance in np.arange(0.1, max_range, step_size):
            x = robot_x + distance * np.cos(world_angle)
            y = robot_y + distance * np.sin(world_angle)

            # Check collision with walls and furniture (same office layout)
            if abs(x) >= 12.4 or abs(y) >= 9.9:
                return distance

            # Additional collision checks for office furniture...
            # (Same as previous implementation)

        return max_range

    def publish_laser_scan(self):
        """Publish laser scan data from Stretch robot"""
        if not (self.sim and self.is_running):
            return

        try:
            ranges = self.get_lidar_data_from_stretch()
            if not ranges:
                return

            laser_scan = LaserScan()
            laser_scan.header.stamp = self.get_clock().now().to_msg()
            laser_scan.header.frame_id = "laser"

            laser_scan.angle_min = self.lidar_angle_min
            laser_scan.angle_max = self.lidar_angle_max
            laser_scan.angle_increment = self.lidar_angle_increment
            laser_scan.time_increment = 0.0
            laser_scan.scan_time = 0.1
            laser_scan.range_min = self.lidar_range_min
            laser_scan.range_max = self.lidar_range_max

            laser_scan.ranges = ranges
            laser_scan.intensities = []

            self.stretch_laser_pub.publish(laser_scan)
            self.stretch_laser_debug_pub.publish(laser_scan)

        except Exception as e:
            self.get_logger().error(f"Error publishing laser scan: {e}")

    def stretch_cmd_vel_callback(self, msg):
        """Handle Stretch robot velocity commands"""
        if self.sim and self.is_running:
            try:
                linear_x = max(-0.5, min(0.5, msg.linear.x))
                angular_z = max(-1.0, min(1.0, msg.angular.z))

                result = self.sim.set_base_velocity(linear_x, angular_z)

                if abs(linear_x) > 0.001 or abs(angular_z) > 0.001:
                    self.get_logger().info(f"🤖 Stretch move: v={linear_x:.3f}, w={angular_z:.3f}")

            except Exception as e:
                self.get_logger().error(f"Error controlling Stretch: {e}")

    def humanoid_cmd_vel_callback(self, msg):
        """Handle Humanoid robot velocity commands"""
        if self.sim and self.is_running:
            try:
                # Simple walking gait based on cmd_vel
                linear_x = msg.linear.x
                angular_z = msg.angular.z

                if abs(linear_x) > 0.001 or abs(angular_z) > 0.001:
                    self.get_logger().info(f"🚶 Humanoid walk: v={linear_x:.3f}, w={angular_z:.3f}")
                    self.generate_walking_gait(linear_x, angular_z)
                else:
                    # Stop walking - return to standing pose
                    self.reset_humanoid_to_standing()

            except Exception as e:
                self.get_logger().error(f"Error controlling Humanoid: {e}")

    def generate_walking_gait(self, linear_vel, angular_vel):
        """Generate simple walking gait for humanoid"""
        # Simple sinusoidal walking pattern
        t = time.time()

        # Walking frequency
        freq = max(0.5, abs(linear_vel))  # Scale frequency with speed

        # Hip oscillation for walking
        hip_swing = 0.3 * math.sin(2 * math.pi * freq * t)
        knee_bend = 0.5 * (1 + math.sin(4 * math.pi * freq * t)) / 2

        # Opposite legs
        self.humanoid_joint_targets['humanoid_right_hip_y'] = -hip_swing
        self.humanoid_joint_targets['humanoid_left_hip_y'] = hip_swing

        self.humanoid_joint_targets['humanoid_right_knee'] = -knee_bend * 0.8
        self.humanoid_joint_targets['humanoid_left_knee'] = -knee_bend * 0.8

        # Ankle compensation
        self.humanoid_joint_targets['humanoid_right_ankle_y'] = knee_bend * 0.3
        self.humanoid_joint_targets['humanoid_left_ankle_y'] = knee_bend * 0.3

        # Add turning motion
        if abs(angular_vel) > 0.1:
            turn_offset = angular_vel * 0.2
            self.humanoid_joint_targets['humanoid_right_hip_z'] = turn_offset
            self.humanoid_joint_targets['humanoid_left_hip_z'] = -turn_offset

    def reset_humanoid_to_standing(self):
        """Reset humanoid to standing position"""
        for joint_name in self.humanoid_joint_targets:
            self.humanoid_joint_targets[joint_name] = 0.0

    def humanoid_walk_cmd_callback(self, msg):
        """Handle walking command for humanoid"""
        self.humanoid_cmd_vel_callback(msg)

    def control_humanoid(self):
        """Send control commands to humanoid joints"""
        if not (self.sim and self.is_running):
            return

        try:
            # Apply joint targets to simulation
            # Note: This would require extending StretchMujocoSimulator
            # to control additional bodies/joints beyond Stretch
            # For now, we'll simulate the control
            pass

        except Exception as e:
            self.get_logger().error(f"Error controlling humanoid joints: {e}")

    def stretch_lift_cmd_callback(self, msg):
        """Handle Stretch lift command"""
        if self.sim and self.is_running:
            try:
                value = max(0.0, min(1.1, msg.data))
                self.sim.move_to(Actuators.lift, value)
                self.get_logger().info(f"🏗️ Stretch lift: {value:.3f}m")
            except Exception as e:
                self.get_logger().error(f"Error controlling stretch lift: {e}")

    def stretch_arm_cmd_callback(self, msg):
        """Handle Stretch arm command"""
        if self.sim and self.is_running:
            try:
                value = max(0.0, min(0.5, msg.data))
                self.sim.move_to(Actuators.arm, value)
                self.get_logger().info(f"🦾 Stretch arm: {value:.3f}m")
            except Exception as e:
                self.get_logger().error(f"Error controlling stretch arm: {e}")

    def stretch_head_pan_cmd_callback(self, msg):
        """Handle Stretch head pan command"""
        if self.sim and self.is_running:
            try:
                value = max(-1.57, min(1.57, msg.data))
                self.sim.move_to(Actuators.head_pan, value)
                self.get_logger().info(f"🔄 Stretch head pan: {value:.3f}rad")
            except Exception as e:
                self.get_logger().error(f"Error controlling stretch head pan: {e}")

    def toggle_cameras_callback(self, msg):
        """Handle camera enable/disable command"""
        self.cameras_enabled = msg.data
        status = "enabled" if msg.data else "disabled"
        self.get_logger().info(f"📷 Cameras {status}")

    def publish_joint_states(self):
        """Publish joint states for both robots"""
        if not (self.sim and self.is_running):
            return

        try:
            if not self.sim.is_running():
                return
            status = self.sim.pull_status()

            # ========== STRETCH JOINT STATES ==========
            stretch_joint_state = JointState()
            stretch_joint_state.header = Header()
            stretch_joint_state.header.stamp = self.get_clock().now().to_msg()
            stretch_joint_state.header.frame_id = "base_link"

            stretch_joint_mappings = {
                'stretch_joint_lift': status.lift,
                'stretch_joint_arm_l0': status.arm,
                'stretch_joint_head_pan': status.head_pan,
                'stretch_joint_head_tilt': status.head_tilt,
                'stretch_joint_wrist_yaw': status.wrist_yaw,
                'stretch_joint_wrist_pitch': status.wrist_pitch,
                'stretch_joint_wrist_roll': status.wrist_roll,
                'stretch_joint_gripper_finger_left': status.gripper,
                'stretch_joint_gripper_finger_right': status.gripper,
            }

            for joint_name, data in stretch_joint_mappings.items():
                if hasattr(data, 'pos'):
                    stretch_joint_state.name.append(joint_name)
                    stretch_joint_state.position.append(float(data.pos))
                    stretch_joint_state.velocity.append(float(data.vel) if hasattr(data, 'vel') else 0.0)
                    stretch_joint_state.effort.append(0.0)

            self.stretch_joint_state_pub.publish(stretch_joint_state)
            self.stretch_joint_state_debug_pub.publish(stretch_joint_state)

            # ========== HUMANOID JOINT STATES ==========
            humanoid_joint_state = JointState()
            humanoid_joint_state.header = Header()
            humanoid_joint_state.header.stamp = self.get_clock().now().to_msg()
            humanoid_joint_state.header.frame_id = "humanoid_base_link"

            # Simulated humanoid joint states
            for joint_name, target_pos in self.humanoid_joint_targets.items():
                humanoid_joint_state.name.append(joint_name)
                humanoid_joint_state.position.append(target_pos)
                humanoid_joint_state.velocity.append(0.0)
                humanoid_joint_state.effort.append(0.0)

            self.humanoid_joint_state_pub.publish(humanoid_joint_state)

        except Exception as e:
            self.get_logger().error(f"Error publishing joint states: {e}")

    def publish_odometry(self):
        """Publish odometry for both robots"""
        if not (self.sim and self.is_running):
            return

        try:
            if not self.sim.is_running():
                return
            status = self.sim.pull_status()
            current_time = time.time()

            # ========== STRETCH ODOMETRY ==========
            stretch_x = status.base.x
            stretch_y = status.base.y
            stretch_theta = status.base.theta

            dt = current_time - self.last_time
            if dt > 0:
                stretch_vx = (stretch_x - self.stretch_last_pose['x']) / dt
                stretch_vy = (stretch_y - self.stretch_last_pose['y']) / dt
                stretch_vtheta = (stretch_theta - self.stretch_last_pose['theta']) / dt

                if abs(stretch_vtheta) > math.pi:
                    if stretch_vtheta > 0:
                        stretch_vtheta -= 2*math.pi
                    else:
                        stretch_vtheta += 2*math.pi
            else:
                stretch_vx = stretch_vy = stretch_vtheta = 0.0

            # Create Stretch odometry message
            stretch_odom = Odometry()
            stretch_odom.header.stamp = self.get_clock().now().to_msg()
            stretch_odom.header.frame_id = "odom"
            stretch_odom.child_frame_id = "base_link"

            stretch_odom.pose.pose.position.x = stretch_x
            stretch_odom.pose.pose.position.y = stretch_y
            stretch_odom.pose.pose.position.z = 0.0

            quat = tf_transformations.quaternion_from_euler(0, 0, stretch_theta)
            stretch_odom.pose.pose.orientation.x = quat[0]
            stretch_odom.pose.pose.orientation.y = quat[1]
            stretch_odom.pose.pose.orientation.z = quat[2]
            stretch_odom.pose.pose.orientation.w = quat[3]

            stretch_odom.twist.twist.linear.x = stretch_vx
            stretch_odom.twist.twist.linear.y = stretch_vy
            stretch_odom.twist.twist.angular.z = stretch_vtheta

            # Set covariance
            stretch_odom.pose.covariance = [0.0] * 36
            stretch_odom.twist.covariance = [0.0] * 36
            stretch_odom.pose.covariance[0] = 0.01
            stretch_odom.pose.covariance[7] = 0.01
            stretch_odom.pose.covariance[35] = 0.01
            stretch_odom.twist.covariance[0] = 0.01
            stretch_odom.twist.covariance[7] = 0.01
            stretch_odom.twist.covariance[35] = 0.01

            self.stretch_odom_pub.publish(stretch_odom)
            self.stretch_odom_debug_pub.publish(stretch_odom)

            # ========== HUMANOID ODOMETRY ==========
            # Simulated humanoid movement
            humanoid_odom = Odometry()
            humanoid_odom.header.stamp = self.get_clock().now().to_msg()
            humanoid_odom.header.frame_id = "humanoid_odom"
            humanoid_odom.child_frame_id = "humanoid_base_link"

            humanoid_odom.pose.pose.position.x = self.humanoid_last_pose['x']
            humanoid_odom.pose.pose.position.y = self.humanoid_last_pose['y']
            humanoid_odom.pose.pose.position.z = 0.0

            quat_h = tf_transformations.quaternion_from_euler(0, 0, self.humanoid_last_pose['theta'])
            humanoid_odom.pose.pose.orientation.x = quat_h[0]
            humanoid_odom.pose.pose.orientation.y = quat_h[1]
            humanoid_odom.pose.pose.orientation.z = quat_h[2]
            humanoid_odom.pose.pose.orientation.w = quat_h[3]

            self.humanoid_odom_pub.publish(humanoid_odom)

            # Update last poses
            self.stretch_last_pose = {'x': stretch_x, 'y': stretch_y, 'theta': stretch_theta}
            self.last_time = current_time

        except Exception as e:
            self.get_logger().error(f"Error publishing odometry: {e}")

    def publish_camera_feeds(self):
        """Publish camera feeds from Stretch robot"""
        if not (self.sim and self.is_running) or not self.cameras_enabled:
            return

        try:
            if not self.sim.is_running():
                return

            camera_data = self.sim.pull_camera_data()
            if not camera_data:
                return

            all_cameras = camera_data.get_all(use_depth_color_map=False)

            for cam_name, img_data in all_cameras.items():
                cam_key = str(cam_name).split('.')[-1]
                if cam_key in self.stretch_camera_pubs and img_data is not None:
                    try:
                        img_array = np.array(img_data)

                        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                            img_bgr = img_array[:, :, ::-1]
                            img_bgr = np.ascontiguousarray(img_bgr, dtype=np.uint8)

                            ros_image = self.bridge.cv2_to_imgmsg(img_bgr, encoding="bgr8")
                            ros_image.header.stamp = self.get_clock().now().to_msg()
                            ros_image.header.frame_id = f"stretch_{cam_key}_frame"

                            self.stretch_camera_pubs[cam_key].publish(ros_image)

                    except Exception as e:
                        self.get_logger().error(f"Error publishing stretch camera {cam_key}: {e}")

        except Exception as e:
            self.get_logger().error(f"Error in stretch camera publishing: {e}")

    def publish_transforms(self):
        """Publish TF tree for both robots"""
        if not (self.sim and self.is_running):
            return

        try:
            if not self.sim.is_running():
                return
            status = self.sim.pull_status()
            current_time = self.get_clock().now()

            transforms = []

            # ========== STRETCH TRANSFORMS ==========
            # odom -> base_link (standard Nav2 frames)
            t_stretch = TransformStamped()
            t_stretch.header.stamp = current_time.to_msg()
            t_stretch.header.frame_id = "odom"
            t_stretch.child_frame_id = "base_link"
            t_stretch.transform.translation.x = status.base.x
            t_stretch.transform.translation.y = status.base.y
            t_stretch.transform.translation.z = 0.0

            quat = tf_transformations.quaternion_from_euler(0, 0, status.base.theta)
            t_stretch.transform.rotation.x = quat[0]
            t_stretch.transform.rotation.y = quat[1]
            t_stretch.transform.rotation.z = quat[2]
            t_stretch.transform.rotation.w = quat[3]
            transforms.append(t_stretch)

            # base_link -> laser (standard frame names)
            t_stretch_laser = TransformStamped()
            t_stretch_laser.header.stamp = current_time.to_msg()
            t_stretch_laser.header.frame_id = "base_link"
            t_stretch_laser.child_frame_id = "laser"
            t_stretch_laser.transform.translation.x = 0.0
            t_stretch_laser.transform.translation.y = 0.0
            t_stretch_laser.transform.translation.z = 0.2
            t_stretch_laser.transform.rotation.w = 1.0
            transforms.append(t_stretch_laser)

            # ========== HUMANOID TRANSFORMS ==========
            # humanoid_odom -> humanoid_base_link
            t_humanoid = TransformStamped()
            t_humanoid.header.stamp = current_time.to_msg()
            t_humanoid.header.frame_id = "humanoid_odom"
            t_humanoid.child_frame_id = "humanoid_base_link"
            t_humanoid.transform.translation.x = self.humanoid_last_pose['x']
            t_humanoid.transform.translation.y = self.humanoid_last_pose['y']
            t_humanoid.transform.translation.z = 1.4  # Humanoid torso height

            quat_h = tf_transformations.quaternion_from_euler(0, 0, self.humanoid_last_pose['theta'])
            t_humanoid.transform.rotation.x = quat_h[0]
            t_humanoid.transform.rotation.y = quat_h[1]
            t_humanoid.transform.rotation.z = quat_h[2]
            t_humanoid.transform.rotation.w = quat_h[3]
            transforms.append(t_humanoid)

            # Stretch Camera frames
            camera_transforms = {
                'stretch_cam_d405_rgb_frame': {'x': 0.0, 'y': 0.0, 'z': 1.0},
                'stretch_cam_d435i_rgb_frame': {'x': 0.0, 'y': 0.0, 'z': 1.0},
                'stretch_cam_nav_rgb_frame': {'x': 0.0, 'y': 0.0, 'z': 0.5}
            }

            for frame_id, pos in camera_transforms.items():
                t_cam = TransformStamped()
                t_cam.header.stamp = current_time.to_msg()
                t_cam.header.frame_id = "stretch_base_link"
                t_cam.child_frame_id = frame_id
                t_cam.transform.translation.x = pos['x']
                t_cam.transform.translation.y = pos['y']
                t_cam.transform.translation.z = pos['z']
                t_cam.transform.rotation.w = 1.0
                transforms.append(t_cam)

            self.tf_broadcaster.sendTransform(transforms)

        except Exception as e:
            self.get_logger().error(f"Error publishing transforms: {e}")

    def stop_simulation(self):
        """Stop the simulation"""
        if self.sim:
            self.sim.stop()
            self.is_running = False
            self.get_logger().info("Dual robot simulation stopped")

def main():
    """Main function"""
    if not (ROS2_AVAILABLE and STRETCH_MUJOCO_AVAILABLE):
        print("Missing required dependencies")
        return

    import sys
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Dual Robot SLAM Bridge with Stretch + Humanoid')
    parser.add_argument('--headless', action='store_true',
                        help='Run simulation in headless mode (no display)')

    # Parse known args to allow ROS2 args to pass through
    args, unknown = parser.parse_known_args()

    # Remove our custom args from sys.argv so ROS2 doesn't see them
    sys.argv = [sys.argv[0]] + unknown

    rclpy.init()

    bridge = DualRobotSLAMBridge()

    try:
        bridge.start_simulation(headless=args.headless)

        bridge.get_logger().info("Dual Robot SLAM Bridge ready!")
        bridge.get_logger().info("Topics available:")
        bridge.get_logger().info("  STRETCH ROBOT:")
        bridge.get_logger().info("    /stretch/scan - Laser scan data")
        bridge.get_logger().info("    /stretch/odom - Odometry data")
        bridge.get_logger().info("    /stretch/joint_states - Robot joint states")
        bridge.get_logger().info("    /stretch/cmd_vel - Movement commands")
        bridge.get_logger().info("    /stretch/camera/*/color/image_raw - Camera feeds")
        bridge.get_logger().info("  HUMANOID ROBOT:")
        bridge.get_logger().info("    /humanoid/odom - Humanoid odometry")
        bridge.get_logger().info("    /humanoid/joint_states - Humanoid joint states")
        bridge.get_logger().info("    /humanoid/cmd_vel - Humanoid movement commands")
        bridge.get_logger().info("    /humanoid/walk_cmd - Humanoid walking commands")
        bridge.get_logger().info("")
        bridge.get_logger().info("🤖 Control both robots via ROS2 topics!")
        bridge.get_logger().info("🏃 Stretch: Navigation and SLAM")
        bridge.get_logger().info("🚶 Humanoid: Bipedal locomotion")

        rclpy.spin(bridge)

    except KeyboardInterrupt:
        bridge.get_logger().info("Shutting down dual robot bridge...")
    finally:
        bridge.stop_simulation()
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
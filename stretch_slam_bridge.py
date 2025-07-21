#!/usr/bin/env python3
"""
Stretch SLAM Bridge for MuJoCo Simulation

This bridge integrates the stretch_dual_gui.py MuJoCo simulation with ROS2 for SLAM.
It publishes robot state, sensor data, and provides a complete SLAM pipeline.
"""

import sys
import time
import threading
import numpy as np
import math
from typing import Optional, Dict, Any

# Add stretch_mujoco to path
sys.path.append('/home/user/stretch_mujoco')

# ROS2 imports
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
    from geometry_msgs.msg import Twist, PoseStamped, TransformStamped
    from sensor_msgs.msg import JointState, Image, LaserScan, PointCloud2
    from nav_msgs.msg import Odometry
    from std_msgs.msg import Header
    from tf2_ros import TransformBroadcaster
    import tf_transformations
    from cv_bridge import CvBridge
    ROS2_AVAILABLE = True
    print("✓ ROS2 imports successful")
except ImportError as e:
    print(f"✗ ROS2 not available: {e}")
    ROS2_AVAILABLE = False

# stretch_mujoco imports
try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.stretch_cameras import StretchCameras
    from stretch_mujoco.enums.actuators import Actuators
    STRETCH_MUJOCO_AVAILABLE = True
    print("✓ stretch_mujoco imports successful")
except ImportError as e:
    print(f"✗ stretch_mujoco not available: {e}")
    STRETCH_MUJOCO_AVAILABLE = False

class StretchSLAMBridge(Node):
    """
    ROS2 node that bridges MuJoCo simulation with ROS2 SLAM pipeline
    """
    
    def __init__(self):
        super().__init__('stretch_slam_bridge')
        
        # Initialize simulation
        self.sim = None
        self.bridge = CvBridge()
        self.is_running = False
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Robot state tracking
        self.last_base_pose = {'x': 0.0, 'y': 0.0, 'theta': 0.0}
        self.last_time = time.time()
        
        # QoS profiles
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=1
        )
        
        # ROS2 Publishers
        self.joint_state_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.laser_pub = self.create_publisher(LaserScan, '/scan', sensor_qos)
        
        # Camera publishers
        self.camera_pubs = {
            'cam_d405_rgb': self.create_publisher(Image, '/camera/d405/color/image_raw', sensor_qos),
            'cam_d435i_rgb': self.create_publisher(Image, '/camera/d435i/color/image_raw', sensor_qos),
            'cam_nav_rgb': self.create_publisher(Image, '/camera/nav/color/image_raw', sensor_qos),
        }
        
        # ROS2 Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Timers for periodic publishing
        self.joint_timer = self.create_timer(0.1, self.publish_joint_states)  # 10Hz
        self.odom_timer = self.create_timer(0.05, self.publish_odometry)  # 20Hz
        self.laser_timer = self.create_timer(0.1, self.publish_laser_scan)  # 10Hz
        self.camera_timer = self.create_timer(0.2, self.publish_camera_feeds)  # 5Hz
        self.tf_timer = self.create_timer(0.05, self.publish_transforms)  # 20Hz
        
        # SLAM-specific publishers
        self.map_pub = self.create_publisher(Image, '/map_image', 10)
        
        self.get_logger().info("Stretch SLAM Bridge initialized")
    
    def start_simulation(self, use_cameras=True, use_laser=True):
        """Start the stretch_mujoco simulation with sensors"""
        try:
            # Configure cameras for SLAM
            if use_cameras:
                cameras_to_use = StretchCameras.rgb()
                self.get_logger().info("Starting simulation with cameras enabled")
            else:
                cameras_to_use = []
                self.get_logger().info("Starting simulation without cameras")
            
            # Initialize simulator
            self.sim = StretchMujocoSimulator(cameras_to_use=cameras_to_use)
            self.sim.start(headless=True)  # Headless for ROS2 integration
            
            self.is_running = True
            self.get_logger().info("Simulation started successfully")
            
            # Wait for simulation to stabilize
            time.sleep(2)
            
            # Move to home position
            self.sim.home()
            self.get_logger().info("Robot moved to home position")
            
        except Exception as e:
            self.get_logger().error(f"Failed to start simulation: {e}")
    
    def stop_simulation(self):
        """Stop the simulation"""
        if self.sim:
            self.sim.stop()
            self.is_running = False
            self.get_logger().info("Simulation stopped")
    
    def cmd_vel_callback(self, msg):
        """Handle incoming velocity commands from navigation stack"""
        if self.sim and self.is_running:
            try:
                linear_x = msg.linear.x
                angular_z = msg.angular.z
                
                # Apply velocity commands to simulation
                self.sim.set_base_velocity(linear_x, angular_z)
                
                # Log occasionally
                if hasattr(self, '_last_cmd_log_time'):
                    if time.time() - self._last_cmd_log_time > 2.0:
                        self.get_logger().info(f"Nav cmd: linear={linear_x:.2f}, angular={angular_z:.2f}")
                        self._last_cmd_log_time = time.time()
                else:
                    self._last_cmd_log_time = time.time()
                    
            except Exception as e:
                self.get_logger().error(f"Error processing velocity command: {e}")
    
    def publish_joint_states(self):
        """Publish current joint states"""
        if not (self.sim and self.is_running):
            return
        
        try:
            status = self.sim.pull_status()
            
            joint_state = JointState()
            joint_state.header = Header()
            joint_state.header.stamp = self.get_clock().now().to_msg()
            joint_state.header.frame_id = "base_link"
            
            # Extract joint data from status
            joint_mappings = {
                'joint_lift': status.lift,
                'joint_arm_l0': status.arm,
                'joint_head_pan': status.head_pan,
                'joint_head_tilt': status.head_tilt,
                'joint_wrist_yaw': status.wrist_yaw,
                'joint_wrist_pitch': status.wrist_pitch,
                'joint_wrist_roll': status.wrist_roll,
                'joint_gripper_finger_left': status.gripper,
                'joint_gripper_finger_right': status.gripper,
            }
            
            for joint_name, data in joint_mappings.items():
                if hasattr(data, 'pos'):
                    joint_state.name.append(joint_name)
                    joint_state.position.append(float(data.pos))
                    joint_state.velocity.append(float(data.vel) if hasattr(data, 'vel') else 0.0)
                    joint_state.effort.append(0.0)
            
            self.joint_state_pub.publish(joint_state)
            
        except Exception as e:
            self.get_logger().error(f"Error publishing joint states: {e}")
    
    def publish_odometry(self):
        """Publish odometry data for SLAM"""
        if not (self.sim and self.is_running):
            return
        
        try:
            status = self.sim.pull_status()
            current_time = time.time()
            
            # Get base pose from simulation
            x = status.base.x
            y = status.base.y
            theta = status.base.theta
            
            # Calculate velocities
            dt = current_time - self.last_time
            if dt > 0:
                vx = (x - self.last_base_pose['x']) / dt
                vy = (y - self.last_base_pose['y']) / dt
                vtheta = (theta - self.last_base_pose['theta']) / dt
            else:
                vx = vy = vtheta = 0.0
            
            # Create odometry message
            odom = Odometry()
            odom.header.stamp = self.get_clock().now().to_msg()
            odom.header.frame_id = "odom"
            odom.child_frame_id = "base_link"
            
            # Position
            odom.pose.pose.position.x = x
            odom.pose.pose.position.y = y
            odom.pose.pose.position.z = 0.0
            
            # Orientation (quaternion from yaw)
            quat = tf_transformations.quaternion_from_euler(0, 0, theta)
            odom.pose.pose.orientation.x = quat[0]
            odom.pose.pose.orientation.y = quat[1]
            odom.pose.pose.orientation.z = quat[2]
            odom.pose.pose.orientation.w = quat[3]
            
            # Velocity
            odom.twist.twist.linear.x = vx
            odom.twist.twist.linear.y = vy
            odom.twist.twist.angular.z = vtheta
            
            # Covariance (simplified)
            odom.pose.covariance[0] = 0.1  # x
            odom.pose.covariance[7] = 0.1  # y
            odom.pose.covariance[35] = 0.1  # theta
            
            self.odom_pub.publish(odom)
            
            # Update last pose
            self.last_base_pose = {'x': x, 'y': y, 'theta': theta}
            self.last_time = current_time
            
        except Exception as e:
            self.get_logger().error(f"Error publishing odometry: {e}")
    
    def publish_laser_scan(self):
        """Publish laser scan data for SLAM"""
        if not (self.sim and self.is_running):
            return
        
        try:
            # Generate simulated laser scan (360 degrees)
            # In real implementation, this would come from the MuJoCo lidar sensor
            laser_scan = LaserScan()
            laser_scan.header.stamp = self.get_clock().now().to_msg()
            laser_scan.header.frame_id = "laser"
            
            # Laser parameters
            laser_scan.angle_min = -math.pi  # -180 degrees
            laser_scan.angle_max = math.pi   # 180 degrees
            laser_scan.angle_increment = math.pi / 180.0  # 1 degree
            laser_scan.time_increment = 0.0
            laser_scan.scan_time = 0.1
            laser_scan.range_min = 0.1
            laser_scan.range_max = 10.0
            
            # Generate simulated scan data
            # This is a placeholder - in real implementation, get from MuJoCo lidar
            num_readings = int((laser_scan.angle_max - laser_scan.angle_min) / laser_scan.angle_increment) + 1
            ranges = []
            
            for i in range(num_readings):
                angle = laser_scan.angle_min + i * laser_scan.angle_increment
                # Simple room simulation - walls at 5m with some variation
                base_range = 5.0
                noise = 0.1 * (np.random.random() - 0.5)  # Small noise
                
                # Add some obstacles
                if -0.5 < angle < 0.5:  # Front obstacle
                    range_val = 2.0 + noise
                elif abs(angle) > 2.5:  # Side walls closer
                    range_val = 3.0 + noise
                else:
                    range_val = base_range + noise
                
                ranges.append(max(laser_scan.range_min, min(laser_scan.range_max, range_val)))
            
            laser_scan.ranges = ranges
            laser_scan.intensities = []  # No intensity data
            
            self.laser_pub.publish(laser_scan)
            
        except Exception as e:
            self.get_logger().error(f"Error publishing laser scan: {e}")
    
    def publish_camera_feeds(self):
        """Publish camera images for visual SLAM"""
        if not (self.sim and self.is_running):
            return
        
        try:
            camera_data = self.sim.pull_camera_data()
            if not camera_data:
                return
            
            all_cameras = camera_data.get_all(use_depth_color_map=False)
            
            for cam_name, img_data in all_cameras.items():
                if cam_name in self.camera_pubs and img_data is not None:
                    try:
                        img_array = np.array(img_data)
                        
                        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                            # Convert RGB to BGR for ROS
                            img_bgr = img_array[:, :, ::-1]
                            
                            ros_image = self.bridge.cv2_to_imgmsg(img_bgr, encoding="bgr8")
                            ros_image.header.stamp = self.get_clock().now().to_msg()
                            ros_image.header.frame_id = f"{cam_name}_frame"
                            
                            self.camera_pubs[cam_name].publish(ros_image)
                            
                    except Exception as e:
                        self.get_logger().error(f"Error publishing {cam_name}: {e}")
                        
        except Exception as e:
            self.get_logger().error(f"Error in camera publishing: {e}")
    
    def publish_transforms(self):
        """Publish TF transforms for RViz visualization"""
        if not (self.sim and self.is_running):
            return
        
        try:
            status = self.sim.pull_status()
            current_time = self.get_clock().now()
            
            # Base transforms
            transforms = []
            
            # odom -> base_link transform
            t = TransformStamped()
            t.header.stamp = current_time.to_msg()
            t.header.frame_id = "odom"
            t.child_frame_id = "base_link"
            t.transform.translation.x = status.base.x
            t.transform.translation.y = status.base.y
            t.transform.translation.z = 0.0
            
            quat = tf_transformations.quaternion_from_euler(0, 0, status.base.theta)
            t.transform.rotation.x = quat[0]
            t.transform.rotation.y = quat[1]
            t.transform.rotation.z = quat[2]
            t.transform.rotation.w = quat[3]
            transforms.append(t)
            
            # base_link -> laser transform
            t_laser = TransformStamped()
            t_laser.header.stamp = current_time.to_msg()
            t_laser.header.frame_id = "base_link"
            t_laser.child_frame_id = "laser"
            t_laser.transform.translation.x = 0.0
            t_laser.transform.translation.y = 0.0
            t_laser.transform.translation.z = 0.2  # Laser height
            t_laser.transform.rotation.w = 1.0
            transforms.append(t_laser)
            
            # Camera transforms
            camera_transforms = {
                'cam_d405_rgb_frame': {'x': 0.0, 'y': 0.0, 'z': 1.0},
                'cam_d435i_rgb_frame': {'x': 0.0, 'y': 0.0, 'z': 1.0},
                'cam_nav_rgb_frame': {'x': 0.0, 'y': 0.0, 'z': 0.5}
            }
            
            for frame_id, pos in camera_transforms.items():
                t_cam = TransformStamped()
                t_cam.header.stamp = current_time.to_msg()
                t_cam.header.frame_id = "base_link"
                t_cam.child_frame_id = frame_id
                t_cam.transform.translation.x = pos['x']
                t_cam.transform.translation.y = pos['y']
                t_cam.transform.translation.z = pos['z']
                t_cam.transform.rotation.w = 1.0
                transforms.append(t_cam)
            
            # Publish all transforms
            self.tf_broadcaster.sendTransform(transforms)
            
        except Exception as e:
            self.get_logger().error(f"Error publishing transforms: {e}")

def main():
    """Main function for SLAM bridge"""
    if not ROS2_AVAILABLE:
        print("ROS2 is required but not available. Please install ROS2.")
        return
    
    if not STRETCH_MUJOCO_AVAILABLE:
        print("stretch_mujoco is required but not available.")
        return
    
    rclpy.init()
    
    # Create and start the bridge node
    bridge = StretchSLAMBridge()
    
    try:
        # Start simulation with sensors
        bridge.start_simulation(use_cameras=True, use_laser=True)
        
        bridge.get_logger().info("SLAM Bridge running. Use Ctrl+C to stop.")
        bridge.get_logger().info("Publishing:")
        bridge.get_logger().info("  - Joint states on /joint_states")
        bridge.get_logger().info("  - Odometry on /odom") 
        bridge.get_logger().info("  - Laser scan on /scan")
        bridge.get_logger().info("  - Camera feeds on /camera/*/color/image_raw")
        bridge.get_logger().info("  - TF transforms for RViz")
        bridge.get_logger().info("Subscribing:")
        bridge.get_logger().info("  - Velocity commands on /cmd_vel")
        bridge.get_logger().info("")
        bridge.get_logger().info("Ready for SLAM! Launch RViz and SLAM nodes now.")
        
        # Spin the node
        rclpy.spin(bridge)
        
    except KeyboardInterrupt:
        bridge.get_logger().info("Shutting down SLAM bridge...")
    except Exception as e:
        bridge.get_logger().error(f"Bridge error: {e}")
    finally:
        # Clean shutdown
        bridge.stop_simulation()
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
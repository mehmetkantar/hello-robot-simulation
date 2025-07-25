#!/usr/bin/env python3
"""
Ultra-Fast Simple Robot SLAM Bridge
Minimal overhead with basic geometric robot
"""

import sys
import time
import threading
import numpy as np
import math
from typing import Optional, Dict, Any

# ROS2 imports
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
    from geometry_msgs.msg import Twist, TransformStamped
    from sensor_msgs.msg import JointState, LaserScan
    from nav_msgs.msg import Odometry
    from std_msgs.msg import Header
    from tf2_ros import TransformBroadcaster
    import tf_transformations
    ROS2_AVAILABLE = True
except ImportError as e:
    print(f"✗ ROS2 not available: {e}")
    ROS2_AVAILABLE = False

# MuJoCo imports
try:
    import mujoco as mj
    import mujoco.viewer
    MUJOCO_AVAILABLE = True
except ImportError as e:
    print(f"✗ MuJoCo not available: {e}")
    MUJOCO_AVAILABLE = False

class SimpleFastRobot(Node):
    """
    Ultra-lightweight robot simulation for maximum performance
    """
    
    def __init__(self):
        super().__init__('simple_fast_robot')
        
        # MuJoCo setup
        self.model = None
        self.data = None
        self.viewer = None
        self.is_running = False
        
        # Robot state
        self.robot_x = 0.0
        self.robot_y = 0.0 
        self.robot_theta = 0.0
        self.last_time = time.time()
        
        # Control commands
        self.cmd_vel_x = 0.0
        self.cmd_vel_y = 0.0
        self.cmd_vel_theta = 0.0
        
        # LIDAR parameters (ultra-simple)
        self.lidar_rays = 36  # Only 36 rays (10° resolution)
        self.lidar_range = 5.0
        
        # Ultra-fast QoS
        fast_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=1
        )
        
        # Publishers (minimal)
        self.odom_pub = self.create_publisher(Odometry, '/odom', fast_qos)
        self.laser_pub = self.create_publisher(LaserScan, '/scan', fast_qos)
        self.joint_pub = self.create_publisher(JointState, '/joint_states', fast_qos)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Subscriber
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, fast_qos)
        
        # Ultra-fast timers (minimal frequency)
        self.odom_timer = self.create_timer(0.1, self.publish_odometry)      # 10 Hz
        self.laser_timer = self.create_timer(0.2, self.publish_laser_scan)   # 5 Hz  
        self.joint_timer = self.create_timer(0.2, self.publish_joint_states) # 5 Hz
        self.tf_timer = self.create_timer(0.1, self.publish_transforms)      # 10 Hz
        self.perf_timer = self.create_timer(3.0, self.log_performance)       # Every 3s
        
        # Simulation loop
        self.sim_thread = None
        
        self.get_logger().info("🚀 Simple Fast Robot initialized!")
        self.get_logger().info("   • Ultra-simple geometry: boxes + cylinders only")
        self.get_logger().info("   • LIDAR: 36 rays (10° resolution)")
        self.get_logger().info("   • Physics: 0.02s timestep, 10 iterations")
        self.get_logger().info("   • Expected: 2-10x faster than complex robot")
        
    def start_simulation(self, headless=False):
        """Start the simple MuJoCo simulation"""
        try:
            # Load simple model
            model_path = "worlds/simple_robot_fast.xml"
            self.model = mj.MjModel.from_xml_path(model_path)
            self.data = mj.MjData(self.model)
            
            # Start viewer if not headless
            if not headless:
                self.viewer = mujoco.viewer.launch_passive(self.model, self.data)
            
            self.is_running = True
            
            # Start simulation thread
            self.sim_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.sim_thread.start()
            
            self.get_logger().info("✅ Simple robot simulation started!")
            return True
            
        except Exception as e:
            self.get_logger().error(f"❌ Failed to start simulation: {e}")
            return False
    
    def simulation_loop(self):
        """Ultra-fast simulation loop"""
        while self.is_running:
            try:
                # Apply control commands
                if self.model and self.data:
                    # Simple control mapping
                    self.data.ctrl[0] = self.cmd_vel_x  # base_x
                    self.data.ctrl[1] = self.cmd_vel_y  # base_y  
                    self.data.ctrl[2] = self.cmd_vel_theta  # base_rot
                    
                    # Step simulation
                    mj.mj_step(self.model, self.data)
                    
                    # Update robot pose from simulation
                    robot_id = mj.mj_name2id(self.model, mj.mjtObj.mjOBJ_BODY, "robot")
                    if robot_id >= 0:
                        self.robot_x = self.data.xpos[robot_id][0]
                        self.robot_y = self.data.xpos[robot_id][1]
                        # Simple theta from quaternion
                        quat = self.data.xquat[robot_id]
                        self.robot_theta = 2 * math.atan2(quat[3], quat[0])
                    
                    # Update viewer
                    if self.viewer:
                        self.viewer.sync()
                
                # Fast loop - no sleep needed, MuJoCo controls timing
                        
            except Exception as e:
                self.get_logger().error(f"Simulation loop error: {e}")
                time.sleep(0.01)
    
    def cmd_vel_callback(self, msg):
        """Handle velocity commands"""
        self.cmd_vel_x = msg.linear.x * 0.5  # Scale down for stability
        self.cmd_vel_y = msg.linear.y * 0.5
        self.cmd_vel_theta = msg.angular.z * 0.3
    
    def publish_odometry(self):
        """Publish robot odometry"""
        if not self.is_running:
            return
            
        try:
            odom = Odometry()
            odom.header.stamp = self.get_clock().now().to_msg()
            odom.header.frame_id = "odom"
            odom.child_frame_id = "base_link"
            
            # Position
            odom.pose.pose.position.x = self.robot_x
            odom.pose.pose.position.y = self.robot_y
            odom.pose.pose.position.z = 0.1
            
            # Orientation
            q = tf_transformations.quaternion_from_euler(0, 0, self.robot_theta)
            odom.pose.pose.orientation.x = q[0]
            odom.pose.pose.orientation.y = q[1]
            odom.pose.pose.orientation.z = q[2]
            odom.pose.pose.orientation.w = q[3]
            
            # Simple velocity (approximate)
            current_time = time.time()
            dt = current_time - self.last_time
            if dt > 0:
                odom.twist.twist.linear.x = self.cmd_vel_x
                odom.twist.twist.linear.y = self.cmd_vel_y
                odom.twist.twist.angular.z = self.cmd_vel_theta
            
            self.last_time = current_time
            self.odom_pub.publish(odom)
            
        except Exception as e:
            pass  # Silent fail for performance
    
    def publish_laser_scan(self):
        """Publish ultra-simple LIDAR scan"""
        if not self.is_running or not self.model:
            return
            
        try:
            scan = LaserScan()
            scan.header.stamp = self.get_clock().now().to_msg()
            scan.header.frame_id = "lidar"
            
            scan.angle_min = -math.pi
            scan.angle_max = math.pi
            scan.angle_increment = 2 * math.pi / self.lidar_rays
            scan.range_min = 0.1
            scan.range_max = self.lidar_range
            
            # Ultra-simple raycast (much faster than complex geometry)
            ranges = []
            for i in range(self.lidar_rays):
                angle = scan.angle_min + i * scan.angle_increment
                world_angle = angle + self.robot_theta
                
                # Simple ray shooting with early termination
                hit_distance = self.lidar_range
                
                # Check only walls (fast box collision)
                ray_x = self.robot_x
                ray_y = self.robot_y
                dx = math.cos(world_angle) * 0.1
                dy = math.sin(world_angle) * 0.1
                
                # Shoot ray in steps
                for step in range(int(self.lidar_range / 0.1)):
                    ray_x += dx
                    ray_y += dy
                    
                    # Simple boundary check (walls at ±9.9)
                    if abs(ray_x) > 9.8 or abs(ray_y) > 9.8:
                        hit_distance = math.sqrt((ray_x - self.robot_x)**2 + 
                                               (ray_y - self.robot_y)**2)
                        break
                    
                    # Simple obstacle check
                    if self.check_simple_obstacles(ray_x, ray_y):
                        hit_distance = math.sqrt((ray_x - self.robot_x)**2 + 
                                               (ray_y - self.robot_y)**2)
                        break
                
                ranges.append(max(scan.range_min, min(hit_distance, scan.range_max)))
            
            scan.ranges = ranges
            self.laser_pub.publish(scan)
            
        except Exception as e:
            pass  # Silent fail for performance
    
    def check_simple_obstacles(self, x, y):
        """Ultra-fast obstacle checking"""
        # Only check the 3 simple obstacles from the world file
        obstacles = [
            {"pos": [2, 2], "size": [0.5, 0.5], "type": "box"},
            {"pos": [-2, 3], "size": [0.3, 0.3], "type": "cylinder"},
            {"pos": [3, -2], "size": [1, 0.2], "type": "box"}
        ]
        
        for obs in obstacles:
            if obs["type"] == "box":
                if (abs(x - obs["pos"][0]) < obs["size"][0] and 
                    abs(y - obs["pos"][1]) < obs["size"][1]):
                    return True
            elif obs["type"] == "cylinder":
                dist = math.sqrt((x - obs["pos"][0])**2 + (y - obs["pos"][1])**2)
                if dist < obs["size"][0]:
                    return True
        
        return False
    
    def publish_joint_states(self):
        """Publish minimal joint states"""
        if not self.is_running:
            return
            
        try:
            joint_state = JointState()
            joint_state.header.stamp = self.get_clock().now().to_msg()
            joint_state.name = ["base_x", "base_y", "base_rot", "arm_lift"]
            joint_state.position = [self.robot_x, self.robot_y, self.robot_theta, 0.0]
            joint_state.velocity = [0.0, 0.0, 0.0, 0.0]
            joint_state.effort = [0.0, 0.0, 0.0, 0.0]
            
            self.joint_pub.publish(joint_state)
            
        except Exception as e:
            pass
    
    def publish_transforms(self):
        """Publish TF transforms"""
        if not self.is_running:
            return
            
        try:
            # Odom -> base_link
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = "odom"
            t.child_frame_id = "base_link"
            t.transform.translation.x = self.robot_x
            t.transform.translation.y = self.robot_y
            t.transform.translation.z = 0.1
            
            q = tf_transformations.quaternion_from_euler(0, 0, self.robot_theta)
            t.transform.rotation.x = q[0]
            t.transform.rotation.y = q[1]
            t.transform.rotation.z = q[2]
            t.transform.rotation.w = q[3]
            
            # base_link -> lidar
            t2 = TransformStamped()
            t2.header.stamp = t.header.stamp
            t2.header.frame_id = "base_link"
            t2.child_frame_id = "lidar"
            t2.transform.translation.z = 0.2
            t2.transform.rotation.w = 1.0
            
            self.tf_broadcaster.sendTransform([t, t2])
            
        except Exception as e:
            pass
    
    def log_performance(self):
        """Log performance every 3 seconds"""
        if self.model and self.data:
            try:
                # Simple performance estimation
                sim_time = self.data.time
                real_time = time.time() - getattr(self, '_start_time', time.time())
                if real_time > 0:
                    ratio = sim_time / real_time
                    self.get_logger().info(f"🚀 Simple Robot Performance: {ratio:.3f}x real-time")
                else:
                    self.get_logger().info("🚀 Simple Robot Performance: Starting up...")
            except:
                pass
        
        if not hasattr(self, '_start_time'):
            self._start_time = time.time()
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        if self.viewer:
            self.viewer.close()
        self.get_logger().info("Simple robot simulation stopped")

def main():
    """Main function"""
    if not (ROS2_AVAILABLE and MUJOCO_AVAILABLE):
        print("Missing required dependencies")
        return
    
    rclpy.init()
    
    try:
        robot = SimpleFastRobot()
        
        # Parse arguments
        import sys
        headless = "--headless" in sys.argv
        
        # Start simulation
        if robot.start_simulation(headless=headless):
            robot.get_logger().info("🚀 Simple Fast Robot ready!")
            robot.get_logger().info("   • Control: ros2 run teleop_twist_keyboard teleop_twist_keyboard")
            robot.get_logger().info("   • Monitor: ros2 topic echo /scan")
            rclpy.spin(robot)
        else:
            robot.get_logger().error("Failed to start simulation")
    
    except KeyboardInterrupt:
        robot.get_logger().info("Shutting down...")
    finally:
        robot.stop_simulation()
        robot.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
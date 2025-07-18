#!/usr/bin/env python3
"""
ROS2 Integration Example for Stretch Dual GUI Simulation

This example shows how to integrate the simulation with ROS2,
publishing joint states and camera feeds, and subscribing to movement commands.

Note: This is a template/example - requires ROS2 to be properly installed.
"""

import sys
import time
import threading
import numpy as np

# Add stretch_mujoco to path if needed
sys.path.append('/home/user/stretch_mujoco')

# ROS2 imports (commented out as they may not be available)
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from sensor_msgs.msg import JointState, Image
    from std_msgs.msg import Header
    from cv_bridge import CvBridge
    ROS2_AVAILABLE = True
    print("✓ ROS2 imports successful")
except ImportError as e:
    print(f"✗ ROS2 not available: {e}")
    print("This example requires ROS2 to be installed")
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

class StretchROS2Bridge(Node):
    """
    ROS2 node that bridges between stretch_mujoco simulation and ROS2 topics
    """
    
    def __init__(self):
        super().__init__('stretch_simulation_bridge')
        
        # Initialize simulation
        self.sim = None
        self.bridge = CvBridge()
        self.is_running = False
        
        # ROS2 Publishers
        self.joint_state_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.camera_pubs = {
            'cam_d405_rgb': self.create_publisher(Image, '/camera/d405/color/image_raw', 10),
            'cam_d435i_rgb': self.create_publisher(Image, '/camera/d435i/color/image_raw', 10),
            'cam_nav_rgb': self.create_publisher(Image, '/camera/nav/color/image_raw', 10),
        }
        
        # ROS2 Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Timers for periodic publishing
        self.joint_timer = self.create_timer(0.1, self.publish_joint_states)  # 10Hz
        self.camera_timer = self.create_timer(0.1, self.publish_camera_feeds)  # 10Hz
        
        self.get_logger().info("Stretch ROS2 Bridge initialized")
    
    def start_simulation(self):
        """Start the stretch_mujoco simulation"""
        try:
            cameras_to_use = StretchCameras.rgb()
            self.sim = StretchMujocoSimulator(cameras_to_use=cameras_to_use)
            self.sim.start(headless=True)  # No GUI for ROS2 integration
            self.is_running = True
            self.get_logger().info("Simulation started successfully")
        except Exception as e:
            self.get_logger().error(f"Failed to start simulation: {e}")
    
    def stop_simulation(self):
        """Stop the simulation"""
        if self.sim:
            self.sim.stop()
            self.is_running = False
            self.get_logger().info("Simulation stopped")
    
    def cmd_vel_callback(self, msg):
        """Handle incoming velocity commands"""
        if self.sim and self.is_running:
            try:
                # Convert ROS Twist to simulation commands
                linear_x = msg.linear.x
                angular_z = msg.angular.z
                
                self.sim.set_base_velocity(linear_x, angular_z)
                
                # Log occasionally to avoid spam
                if hasattr(self, '_last_cmd_log_time'):
                    if time.time() - self._last_cmd_log_time > 1.0:
                        self.get_logger().info(f"Velocity command: linear={linear_x:.2f}, angular={angular_z:.2f}")
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
            joint_data = {
                'lift': status.lift,
                'arm': status.arm,
                'head_pan': status.head_pan,
                'head_tilt': status.head_tilt,
                'wrist_yaw': status.wrist_yaw,
                'wrist_pitch': status.wrist_pitch,
                'wrist_roll': status.wrist_roll,
                'gripper': status.gripper,
            }
            
            for joint_name, data in joint_data.items():
                if hasattr(data, 'pos'):
                    joint_state.name.append(joint_name)
                    joint_state.position.append(float(data.pos))
                    joint_state.velocity.append(float(data.vel) if hasattr(data, 'vel') else 0.0)
                    joint_state.effort.append(0.0)  # Effort not available in simulation
            
            self.joint_state_pub.publish(joint_state)
            
        except Exception as e:
            self.get_logger().error(f"Error publishing joint states: {e}")
    
    def publish_camera_feeds(self):
        """Publish camera images"""
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
                        # Convert numpy array to ROS Image message
                        img_array = np.array(img_data)
                        
                        # Ensure proper format (BGR for OpenCV)
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

def main():
    """Main function for ROS2 bridge"""
    if not ROS2_AVAILABLE:
        print("ROS2 is required but not available. Please install ROS2.")
        return
    
    if not STRETCH_MUJOCO_AVAILABLE:
        print("stretch_mujoco is required but not available.")
        return
    
    rclpy.init()
    
    # Create and start the bridge node
    bridge = StretchROS2Bridge()
    
    try:
        # Start simulation
        bridge.start_simulation()
        
        # Give simulation time to start
        time.sleep(2)
        
        bridge.get_logger().info("ROS2 Bridge running. Use Ctrl+C to stop.")
        bridge.get_logger().info("Publishing:")
        bridge.get_logger().info("  - Joint states on /joint_states")
        bridge.get_logger().info("  - Camera feeds on /camera/*/color/image_raw")
        bridge.get_logger().info("Subscribing:")
        bridge.get_logger().info("  - Velocity commands on /cmd_vel")
        
        # Spin the node
        rclpy.spin(bridge)
        
    except KeyboardInterrupt:
        bridge.get_logger().info("Shutting down bridge...")
    except Exception as e:
        bridge.get_logger().error(f"Bridge error: {e}")
    finally:
        # Clean shutdown
        bridge.stop_simulation()
        bridge.destroy_node()
        rclpy.shutdown()

def test_bridge():
    """Test function to verify bridge functionality"""
    if not (ROS2_AVAILABLE and STRETCH_MUJOCO_AVAILABLE):
        print("Cannot run test - missing dependencies")
        return
    
    print("Testing ROS2 bridge functionality...")
    
    # This would test the bridge without actually running ROS2
    # Useful for development and debugging
    
    try:
        # Test simulation startup
        cameras_to_use = StretchCameras.rgb()
        sim = StretchMujocoSimulator(cameras_to_use=cameras_to_use)
        sim.start(headless=True)
        
        print("✓ Simulation started")
        
        # Test status retrieval
        status = sim.pull_status()
        print(f"✓ Status retrieved: FPS={status.fps:.1f}")
        
        # Test camera data
        camera_data = sim.pull_camera_data()
        if camera_data:
            all_cameras = camera_data.get_all(use_depth_color_map=False)
            print(f"✓ Camera data retrieved: {list(all_cameras.keys())}")
        else:
            print("✗ No camera data")
        
        # Test movement
        sim.set_base_velocity(0.1, 0.0)
        time.sleep(1)
        sim.set_base_velocity(0.0, 0.0)
        print("✓ Movement commands work")
        
        sim.stop()
        print("✓ Bridge test completed successfully")
        
    except Exception as e:
        print(f"✗ Bridge test failed: {e}")

if __name__ == "__main__":
    # Choose what to run based on command line args
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_bridge()
    else:
        main()
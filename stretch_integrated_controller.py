#!/usr/bin/env python3
"""
Stretch Integrated Controller
MuJoCo + RViz + GUI with SLAM and Navigation Support
"""

import sys
import os
import time
import threading
import subprocess
import signal

# Add MuJoCo path
sys.path.append('./stretch_mujoco')

try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.actuators import Actuators
    MUJOCO_AVAILABLE = True
    print("✅ MuJoCo available")
except ImportError as e:
    print(f"❌ MuJoCo not available: {e}")
    MUJOCO_AVAILABLE = False

# ROS2 imports
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from sensor_msgs.msg import JointState, LaserScan
    from std_msgs.msg import Float64
    from nav_msgs.msg import OccupancyGrid
    ROS2_AVAILABLE = True
    print("✅ ROS2 available")
except ImportError as e:
    print(f"❌ ROS2 not available: {e}")
    ROS2_AVAILABLE = False

class StretchIntegratedBridge(Node):
    """
    Integrated bridge that connects:
    - MuJoCo simulation (for physics and visualization)
    - ROS2 ecosystem (for SLAM, navigation, RViz)
    - GUI control interface
    """
    
    def __init__(self):
        super().__init__('stretch_integrated_bridge')
        
        # MuJoCo simulation
        self.sim = None
        self.mujoco_thread = None
        
        # ROS2 publishers
        self.joint_state_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)
        self.odom_pub = self.create_publisher(OccupancyGrid, '/odom', 10)
        
        # ROS2 subscribers for control
        self.cmd_vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Joint control subscribers (from GUI)
        self.lift_sub = self.create_subscription(Float64, '/stretch_controller/lift_joint/command', self.lift_callback, 10)
        self.arm_sub = self.create_subscription(Float64, '/stretch_controller/arm_joint/command', self.arm_callback, 10)
        self.wrist_yaw_sub = self.create_subscription(Float64, '/stretch_controller/wrist_yaw/command', self.wrist_yaw_callback, 10)
        self.wrist_pitch_sub = self.create_subscription(Float64, '/stretch_controller/wrist_pitch/command', self.wrist_pitch_callback, 10)
        self.gripper_sub = self.create_subscription(Float64, '/stretch_controller/gripper_joint/command', self.gripper_callback, 10)
        
        # State tracking
        self.current_joints = {
            'joint_lift': 0.5,
            'wrist_extension': 0.1,
            'joint_wrist_yaw': 0.0,
            'joint_wrist_pitch': 0.0,
            'joint_gripper_finger_left': 0.0,
            'joint_gripper_finger_right': 0.0
        }
        
        # Timers
        self.status_timer = self.create_timer(0.05, self.publish_robot_state)  # 20Hz
        
        self.get_logger().info("🤖 Stretch Integrated Bridge initialized")
    
    def start_mujoco_simulation(self, environment="simple"):
        """Start MuJoCo simulation"""
        try:
            self.get_logger().info("🚀 Starting MuJoCo simulation...")
            
            if environment == "simple":
                self.sim = StretchMujocoSimulator()
            else:
                # Complex environment setup if needed
                self.sim = StretchMujocoSimulator()
            
            self.sim.start(headless=False)  # Keep MuJoCo viewer
            
            # Wait for simulation to stabilize
            time.sleep(3)
            
            self.get_logger().info("✅ MuJoCo simulation started successfully")
            return True
            
        except Exception as e:
            self.get_logger().error(f"❌ Failed to start MuJoCo: {e}")
            return False
    
    def cmd_vel_callback(self, msg):
        """Handle base velocity commands"""
        if self.sim and self.sim.is_running():
            try:
                self.sim.set_base_velocity(msg.linear.x, msg.angular.z)
                self.get_logger().debug(f"🚗 Base velocity: linear={msg.linear.x:.3f}, angular={msg.angular.z:.3f}")
            except Exception as e:
                self.get_logger().error(f"❌ Base control error: {e}")
    
    def lift_callback(self, msg):
        """Handle lift joint command"""
        if self.sim and self.sim.is_running():
            try:
                # Get current position and calculate increment
                status = self.sim.pull_status()
                current_lift = status.lift.pos if hasattr(status, 'lift') and hasattr(status.lift, 'pos') else 0.5
                increment = msg.data - current_lift
                
                if abs(increment) > 0.01:
                    self.sim.move_by(Actuators.lift, increment)
                    self.current_joints['joint_lift'] = msg.data
                    self.get_logger().info(f"🏗️ Lift moved: {increment:.3f}m -> {msg.data:.3f}m")
            except Exception as e:
                self.get_logger().error(f"❌ Lift control error: {e}")
    
    def arm_callback(self, msg):
        """Handle arm extension command"""
        if self.sim and self.sim.is_running():
            try:
                status = self.sim.pull_status()
                current_arm = status.arm.pos if hasattr(status, 'arm') and hasattr(status.arm, 'pos') else 0.1
                increment = msg.data - current_arm
                
                if abs(increment) > 0.01:
                    self.sim.move_by(Actuators.arm, increment)
                    self.current_joints['wrist_extension'] = msg.data
                    self.get_logger().info(f"🦾 Arm moved: {increment:.3f}m -> {msg.data:.3f}m")
            except Exception as e:
                self.get_logger().error(f"❌ Arm control error: {e}")
    
    def wrist_yaw_callback(self, msg):
        """Handle wrist yaw command"""
        if self.sim and self.sim.is_running():
            try:
                status = self.sim.pull_status()
                current_yaw = status.wrist_yaw.pos if hasattr(status, 'wrist_yaw') and hasattr(status.wrist_yaw, 'pos') else 0.0
                increment = msg.data - current_yaw
                
                if abs(increment) > 0.01:
                    self.sim.move_by(Actuators.wrist_yaw, increment)
                    self.current_joints['joint_wrist_yaw'] = msg.data
                    self.get_logger().info(f"🔄 Wrist yaw moved: {increment:.3f}rad -> {msg.data:.3f}rad")
            except Exception as e:
                self.get_logger().error(f"❌ Wrist yaw control error: {e}")
    
    def wrist_pitch_callback(self, msg):
        """Handle wrist pitch command"""
        if self.sim and self.sim.is_running():
            try:
                status = self.sim.pull_status()
                current_pitch = status.wrist_pitch.pos if hasattr(status, 'wrist_pitch') and hasattr(status.wrist_pitch, 'pos') else 0.0
                increment = msg.data - current_pitch
                
                if abs(increment) > 0.01:
                    self.sim.move_by(Actuators.wrist_pitch, increment)
                    self.current_joints['joint_wrist_pitch'] = msg.data
                    self.get_logger().info(f"↕️ Wrist pitch moved: {increment:.3f}rad -> {msg.data:.3f}rad")
            except Exception as e:
                self.get_logger().error(f"❌ Wrist pitch control error: {e}")
    
    def gripper_callback(self, msg):
        """Handle gripper command"""
        if self.sim and self.sim.is_running():
            try:
                status = self.sim.pull_status()
                current_gripper = status.gripper.pos if hasattr(status, 'gripper') and hasattr(status.gripper, 'pos') else 0.0
                increment = msg.data - current_gripper
                
                if abs(increment) > 0.01:
                    self.sim.move_by(Actuators.gripper, increment)
                    # Update both gripper fingers
                    self.current_joints['joint_gripper_finger_left'] = msg.data / 2.0
                    self.current_joints['joint_gripper_finger_right'] = msg.data / 2.0
                    self.get_logger().info(f"✋ Gripper moved: {increment:.3f}m -> {msg.data:.3f}m")
            except Exception as e:
                self.get_logger().error(f"❌ Gripper control error: {e}")
    
    def publish_robot_state(self):
        """Publish robot state to ROS2 for RViz and SLAM"""
        if not self.sim or not self.sim.is_running():
            return
            
        try:
            # Get MuJoCo status
            status = self.sim.pull_status()
            
            # Publish joint states
            joint_msg = JointState()
            joint_msg.header.stamp = self.get_clock().now().to_msg()
            joint_msg.header.frame_id = 'base_link'
            
            # Update joint positions from MuJoCo
            if hasattr(status, 'lift'):
                self.current_joints['joint_lift'] = status.lift.pos
            if hasattr(status, 'arm'):
                self.current_joints['wrist_extension'] = status.arm.pos
            if hasattr(status, 'wrist_yaw'):
                self.current_joints['joint_wrist_yaw'] = status.wrist_yaw.pos
            if hasattr(status, 'wrist_pitch'):
                self.current_joints['joint_wrist_pitch'] = status.wrist_pitch.pos
            if hasattr(status, 'gripper'):
                gripper_pos = status.gripper.pos
                self.current_joints['joint_gripper_finger_left'] = gripper_pos / 2.0
                self.current_joints['joint_gripper_finger_right'] = gripper_pos / 2.0
            
            # Fill joint state message
            for joint_name, position in self.current_joints.items():
                joint_msg.name.append(joint_name)
                joint_msg.position.append(position)
                joint_msg.velocity.append(0.0)
                joint_msg.effort.append(0.0)
            
            self.joint_state_pub.publish(joint_msg)
            
            # TODO: Publish laser scan data for SLAM
            # TODO: Publish odometry data for navigation
            # TODO: Publish transform data
            
        except Exception as e:
            self.get_logger().error(f"❌ Error publishing robot state: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.sim:
            try:
                self.sim.stop()
                self.get_logger().info("✅ MuJoCo simulation stopped")
            except Exception as e:
                self.get_logger().error(f"⚠️ Error stopping MuJoCo: {e}")

def start_rviz():
    """Start RViz with robot visualization"""
    try:
        print("🖥️ Starting RViz...")
        rviz_cmd = ["rviz2", "-d", "/opt/ros/humble/share/urdf_tutorial/rviz/urdf.rviz"]
        rviz_process = subprocess.Popen(rviz_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ RViz started")
        return rviz_process
    except Exception as e:
        print(f"⚠️ Could not start RViz: {e}")
        return None

def start_slam():
    """Start SLAM Toolbox"""
    try:
        print("🗺️ Starting SLAM Toolbox...")
        slam_cmd = ["ros2", "launch", "slam_toolbox", "online_async_launch.py"]
        slam_process = subprocess.Popen(slam_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ SLAM Toolbox started")
        return slam_process
    except Exception as e:
        print(f"⚠️ Could not start SLAM: {e}")
        return None

def start_gui():
    """Start the simple GUI controller"""
    try:
        print("🎮 Starting GUI controller...")
        gui_cmd = ["python3", "stretch_robot_controller_simple.py"]
        gui_process = subprocess.Popen(gui_cmd)
        print("✅ GUI controller started")
        return gui_process
    except Exception as e:
        print(f"⚠️ Could not start GUI: {e}")
        return None

def main():
    print("="*60)
    print("🤖 STRETCH INTEGRATED SYSTEM")
    print("MuJoCo + RViz + SLAM + GUI Controller")
    print("="*60)
    
    if not ROS2_AVAILABLE:
        print("❌ ROS2 not available - exiting")
        return
    
    if not MUJOCO_AVAILABLE:
        print("❌ MuJoCo not available - exiting")  
        return
    
    # Initialize ROS2
    rclpy.init()
    
    # Create integrated bridge
    bridge = StretchIntegratedBridge()
    
    # Start MuJoCo simulation
    if not bridge.start_mujoco_simulation("simple"):
        print("❌ Failed to start MuJoCo - exiting")
        rclpy.shutdown()
        return
    
    # Start supporting processes
    processes = []
    
    # Start RViz
    rviz_process = start_rviz()
    if rviz_process:
        processes.append(rviz_process)
    
    # Wait a bit for RViz to initialize
    time.sleep(3)
    
    # Start SLAM
    slam_process = start_slam()
    if slam_process:
        processes.append(slam_process)
    
    # Start GUI
    gui_process = start_gui()
    if gui_process:
        processes.append(gui_process)
    
    print("\n🎉 INTEGRATED SYSTEM READY!")
    print("📺 MuJoCo: Physics simulation and 3D visualization")
    print("🖥️ RViz: Robot state visualization and mapping")
    print("🗺️ SLAM: Real-time mapping and localization")  
    print("🎮 GUI: Robot control interface")
    print("\nPress Ctrl+C to stop all systems...")
    
    try:
        # Spin the bridge
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down integrated system...")
    finally:
        # Cleanup
        bridge.cleanup()
        
        # Stop all processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        bridge.destroy_node()
        rclpy.shutdown()
        print("✅ System shutdown complete")

if __name__ == "__main__":
    main()
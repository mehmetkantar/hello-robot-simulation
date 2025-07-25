#!/usr/bin/env python3
"""
Stretch Controller Bridge
Connects the GUI controller commands to the MuJoCo simulation
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
import numpy as np
import time


class StretchControllerBridge(Node):
    """Bridge between GUI controller and MuJoCo simulation"""
    
    def __init__(self):
        super().__init__('stretch_controller_bridge')
        
        # Joint limits (from Stretch robot specifications)
        self.joint_limits = {
            'lift': {'min': 0.0, 'max': 1.1},
            'arm': {'min': 0.0, 'max': 0.5},
            'wrist_yaw': {'min': -1.57, 'max': 1.57},
            'wrist_pitch': {'min': -0.5, 'max': 0.5},
            'wrist_roll': {'min': -1.57, 'max': 1.57},
            'gripper': {'min': -0.1, 'max': 0.6}
        }
        
        # Current joint positions
        self.current_joints = {
            'joint_lift': 0.5,
            'wrist_extension': 0.1,
            'joint_wrist_yaw': 0.0,
            'joint_wrist_pitch': 0.0,
            'joint_wrist_roll': 0.0,
            'joint_gripper_finger_left': 0.0,
            'joint_gripper_finger_right': 0.0
        }
        
        # Subscribers from GUI controller
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/stretch/cmd_vel', self.cmd_vel_callback, 10)
        self.lift_sub = self.create_subscription(
            Float64, '/stretch_controller/lift_joint/command', self.lift_callback, 10)
        self.arm_sub = self.create_subscription(
            Float64, '/stretch_controller/arm_joint/command', self.arm_callback, 10)
        self.wrist_yaw_sub = self.create_subscription(
            Float64, '/stretch_controller/wrist_yaw/command', self.wrist_yaw_callback, 10)
        self.wrist_pitch_sub = self.create_subscription(
            Float64, '/stretch_controller/wrist_pitch/command', self.wrist_pitch_callback, 10)
        self.wrist_roll_sub = self.create_subscription(
            Float64, '/stretch_controller/wrist_roll/command', self.wrist_roll_callback, 10)
        self.gripper_sub = self.create_subscription(
            Float64, '/stretch_controller/gripper_joint/command', self.gripper_callback, 10)
        
        # Publishers to simulation (MuJoCo expects these topics)
        self.joint_pub = self.create_publisher(JointState, '/joint_commands', 10)
        self.base_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Additional publisher for direct MuJoCo control
        self.mujoco_cmd_pub = self.create_publisher(Twist, '/stretch_diff_drive_controller/cmd_vel_unstamped', 10)
        
        # Publisher for joint states (feedback)
        self.joint_state_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Get reference to MuJoCo simulation from SLAM bridge
        self.sim = None
        self.get_mujoco_sim_timer = self.create_timer(1.0, self.try_get_mujoco_sim)
        
        # Timer for publishing joint states
        self.joint_timer = self.create_timer(0.05, self.publish_joint_states)  # 20Hz
        
        self.get_logger().info("🔗 Stretch Controller Bridge started")
        self.get_logger().info("📡 Bridging GUI commands to MuJoCo simulation")
    
    def try_get_mujoco_sim(self):
        """Try to get reference to MuJoCo simulation from SLAM bridge"""
        try:
            # Try to import and find the running simulation
            import rclpy
            for node_name in self.get_node_names():
                if 'stretch_slam_bridge' in node_name:
                    # Try to get simulation reference through a service or global variable
                    # For now, we'll use a different approach
                    pass
            
            # Alternative: Check if there's a way to access the simulation directly
            # This is a placeholder - we'll implement direct MuJoCo control
            
        except Exception as e:
            self.get_logger().debug(f"Could not get MuJoCo sim reference: {e}")
    
    def control_mujoco_joint(self, joint_type, value):
        """Send joint control command directly to MuJoCo if available"""
        try:
            # For now, we'll publish the joint command and let the SLAM bridge handle it
            # This is a placeholder for direct MuJoCo control
            self.get_logger().debug(f"Would control {joint_type}: {value}")
            
        except Exception as e:
            self.get_logger().error(f"Error controlling MuJoCo joint {joint_type}: {e}")
    
    def clamp_value(self, value, joint_name):
        """Clamp joint value to safe limits"""
        if joint_name in self.joint_limits:
            limits = self.joint_limits[joint_name]
            return max(limits['min'], min(limits['max'], value))
        return value
    
    def cmd_vel_callback(self, msg):
        """Forward base velocity commands"""
        self.get_logger().info(f"🔔 Received cmd_vel: linear={msg.linear.x:.3f}, angular={msg.angular.z:.3f}")
        
        # Clamp velocities to safe limits
        linear = max(-2.0, min(2.0, msg.linear.x))
        angular = max(-3.0, min(3.0, msg.angular.z))
        
        # Create new twist message
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        
        # Publish to simulation (both topics to ensure compatibility)
        self.base_pub.publish(twist)
        self.mujoco_cmd_pub.publish(twist)
        
        self.get_logger().info(f"🚗 Forwarded cmd: linear={linear:.3f}, angular={angular:.3f}")
        self.get_logger().info(f"📡 Published to /cmd_vel and /stretch_diff_drive_controller/cmd_vel_unstamped")
    
    def lift_callback(self, msg):
        """Handle lift joint command"""
        value = self.clamp_value(msg.data, 'lift')
        self.current_joints['joint_lift'] = value
        self.get_logger().info(f"🏗️ Bridge received lift: {value:.3f}m")
    
    def arm_callback(self, msg):
        """Handle arm extension command"""
        value = self.clamp_value(msg.data, 'arm')
        self.current_joints['wrist_extension'] = value
        self.get_logger().info(f"🦾 Bridge received arm: {value:.3f}m")
    
    def wrist_yaw_callback(self, msg):
        """Handle wrist yaw command"""
        value = self.clamp_value(msg.data, 'wrist_yaw')
        self.current_joints['joint_wrist_yaw'] = value
        self.get_logger().debug(f"Wrist yaw: {value:.3f}rad")
    
    def wrist_pitch_callback(self, msg):
        """Handle wrist pitch command"""
        value = self.clamp_value(msg.data, 'wrist_pitch')
        self.current_joints['joint_wrist_pitch'] = value
        self.get_logger().debug(f"Wrist pitch: {value:.3f}rad")
    
    def wrist_roll_callback(self, msg):
        """Handle wrist roll command"""
        value = self.clamp_value(msg.data, 'wrist_roll')
        self.current_joints['joint_wrist_roll'] = value
        self.get_logger().debug(f"Wrist roll: {value:.3f}rad")
    
    def gripper_callback(self, msg):
        """Handle gripper command"""
        value = self.clamp_value(msg.data, 'gripper')
        # Split gripper command to both fingers
        self.current_joints['joint_gripper_finger_left'] = value / 2.0
        self.current_joints['joint_gripper_finger_right'] = value / 2.0
        self.get_logger().debug(f"Gripper: {value:.3f}m")
    
    def publish_joint_states(self):
        """Publish current joint states only if we have actual joint data"""
        if not self.current_joints:
            return  # Don't publish empty joint states
            
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # Add all joint names and positions
        for joint_name, position in self.current_joints.items():
            msg.name.append(joint_name)
            msg.position.append(position)
            msg.velocity.append(0.0)
            msg.effort.append(0.0)
        
        # Only publish to joint commands (for simulation control)
        # Don't publish joint states to avoid conflicting with simulation
        self.joint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    
    bridge = StretchControllerBridge()
    
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        bridge.get_logger().info("🛑 Shutting down controller bridge...")
    finally:
        bridge.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Simple Goal Sender for Stretch Robot Navigation
Sends navigation goals via command line or interactive mode
"""

import sys
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.callback_groups import ReentrantCallbackGroup


class SimpleGoalSender(Node):
    def __init__(self):
        super().__init__('simple_goal_sender')
        
        # Create action client
        self._action_client = ActionClient(
            self, 
            NavigateToPose, 
            'navigate_to_pose',
            callback_group=ReentrantCallbackGroup()
        )
        
        self.get_logger().info("🎯 Simple Goal Sender Started")
        self.get_logger().info("⏳ Waiting for Nav2 action server...")
        
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("❌ Nav2 action server not available!")
            self.get_logger().error("   Make sure navigation.sh is running!")
            return
            
        self.get_logger().info("✅ Connected to Nav2 action server")
        self.current_goal_handle = None

    def send_goal(self, x, y, theta=0.0):
        """Send navigation goal"""
        goal_msg = NavigateToPose.Goal()
        
        # Set goal pose
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0
        
        # Convert angle to quaternion
        goal_msg.pose.pose.orientation.z = math.sin(theta / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(theta / 2.0)
        
        self.get_logger().info(f"🚀 Sending goal: x={x}, y={y}, theta={theta:.2f}")
        
        # Send goal
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error("❌ Goal rejected!")
            return False
            
        self.current_goal_handle = goal_handle
        self.get_logger().info("✅ Goal accepted! Robot navigating...")
        return True
    
    def cancel_goal(self):
        """Cancel current navigation goal"""
        if self.current_goal_handle:
            self.get_logger().info("🛑 Canceling current goal...")
            cancel_future = self.current_goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel_future)
            self.current_goal_handle = None
            self.get_logger().info("✅ Goal canceled")
        else:
            self.get_logger().warn("⚠️  No active goal to cancel")
    
    def feedback_callback(self, feedback_msg):
        """Handle navigation feedback"""
        feedback = feedback_msg.feedback
        distance = feedback.distance_remaining
        if distance > 0.1:
            self.get_logger().info(f"📍 Distance remaining: {distance:.2f}m")


def print_usage():
    print("\n🎯 STRETCH ROBOT GOAL SENDER")
    print("="*40)
    print("Usage:")
    print("  python3 simple_goal_sender.py <x> <y> [theta]")
    print("  python3 simple_goal_sender.py interactive")
    print("  python3 simple_goal_sender.py cancel")
    print("")
    print("Examples:")
    print("  python3 simple_goal_sender.py 2.0 1.5       # Go to (2,1.5)")
    print("  python3 simple_goal_sender.py 0 0 3.14      # Return to origin, face back")
    print("  python3 simple_goal_sender.py interactive   # Interactive mode")
    print("  python3 simple_goal_sender.py cancel        # Cancel current goal")
    print("")
    print("Coordinates are in meters relative to map origin")
    print("Theta is in radians (0=forward, 1.57=left, 3.14=back, -1.57=right)")
    print("="*40)


def interactive_mode(goal_sender):
    """Interactive goal sending mode"""
    print("\n🎮 INTERACTIVE NAVIGATION MODE")
    print("="*40)
    print("Enter coordinates or commands:")
    print("  Format: x y [theta]  (e.g., '2.0 1.5' or '1 2 3.14')")
    print("  Commands: 'quit', 'exit', 'cancel'")
    print("="*40)
    
    while True:
        try:
            user_input = input("\n🎯 Enter goal (x y [theta]) or command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'cancel':
                goal_sender.cancel_goal()
                continue
            elif user_input.lower() == 'help':
                print_usage()
                continue
            
            # Parse coordinates
            parts = user_input.split()
            if len(parts) < 2:
                print("❌ Please provide at least x and y coordinates")
                continue
                
            x = float(parts[0])
            y = float(parts[1])
            theta = float(parts[2]) if len(parts) > 2 else 0.0
            
            goal_sender.send_goal(x, y, theta)
            
        except ValueError:
            print("❌ Invalid input. Please enter numbers for coordinates.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    rclpy.init()
    
    if len(sys.argv) < 2:
        print_usage()
        return
    
    goal_sender = SimpleGoalSender()
    
    try:
        if sys.argv[1].lower() == 'interactive':
            interactive_mode(goal_sender)
        elif sys.argv[1].lower() == 'cancel':
            goal_sender.cancel_goal()
        elif sys.argv[1].lower() in ['help', '-h', '--help']:
            print_usage()
        else:
            # Parse command line coordinates
            x = float(sys.argv[1])
            y = float(sys.argv[2])
            theta = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
            
            success = goal_sender.send_goal(x, y, theta)
            
            if success:
                print("🎯 Goal sent! Monitor progress in RViz or check robot movement.")
                print("   Use 'python3 simple_goal_sender.py cancel' to stop navigation.")
            
    except ValueError:
        print("❌ Error: Please provide valid numbers for coordinates")
        print_usage()
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        goal_sender.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
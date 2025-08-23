#!/usr/bin/env python3
"""
Test Autonomous Navigation System
Tests Nav2 integration with Stretch robot simulation
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.executors import SingleThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup


class NavigationTester(Node):
    def __init__(self):
        super().__init__('navigation_tester')
        
        # Create action client for navigation
        self._action_client = ActionClient(
            self, 
            NavigateToPose, 
            'navigate_to_pose',
            callback_group=ReentrantCallbackGroup()
        )
        
        self.get_logger().info("🚀 Navigation Tester Node Started")
        self.get_logger().info("⏳ Waiting for Nav2 action server...")
        
        # Wait for action server
        if not self._action_client.wait_for_server(timeout_sec=30.0):
            self.get_logger().error("❌ Nav2 action server not available!")
            return
            
        self.get_logger().info("✅ Nav2 action server connected!")

    def send_goal(self, x, y, theta=0.0):
        """Send navigation goal to specified coordinates"""
        goal_msg = NavigateToPose.Goal()
        
        # Set goal pose
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0
        
        # Convert angle to quaternion (simplified for 2D)
        import math
        goal_msg.pose.pose.orientation.z = math.sin(theta / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(theta / 2.0)
        
        self.get_logger().info(f"🎯 Sending navigation goal: ({x}, {y}, {theta})")
        
        # Send goal
        send_goal_future = self._action_client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback
        )
        
        # Wait for goal acceptance
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error("❌ Goal rejected by Nav2")
            return False
            
        self.get_logger().info("✅ Goal accepted! Robot is navigating...")
        
        # Wait for result
        get_result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future)
        
        result = get_result_future.result().result
        if result:
            self.get_logger().info("🎉 Navigation completed successfully!")
            return True
        else:
            self.get_logger().error("❌ Navigation failed!")
            return False
    
    def feedback_callback(self, feedback_msg):
        """Handle navigation feedback"""
        feedback = feedback_msg.feedback
        distance = feedback.distance_remaining
        time_remaining = feedback.estimated_time_remaining.sec
        
        if distance > 0.1:  # Only log if meaningful distance remaining
            self.get_logger().info(
                f"📍 Navigation progress: {distance:.2f}m remaining, ~{time_remaining}s"
            )


def run_navigation_tests():
    """Run a series of navigation tests"""
    rclpy.init()
    
    navigator = NavigationTester()
    
    # Test waypoints (x, y, theta)
    test_goals = [
        (2.0, 0.0, 0.0),    # Forward 2 meters
        (2.0, 2.0, 1.57),   # Right 2 meters (90 degrees)
        (0.0, 2.0, 3.14),   # Back to left (180 degrees) 
        (0.0, 0.0, 0.0),    # Return to origin
    ]
    
    print("\n" + "="*50)
    print("🤖 STRETCH ROBOT NAVIGATION TESTS")
    print("="*50)
    print("Max Speed: 5.0 m/s")
    print("Navigation Stack: Nav2 + DWB Local Planner")
    print("Environment: Complex Office with Obstacles")
    print("="*50)
    
    success_count = 0
    
    for i, (x, y, theta) in enumerate(test_goals, 1):
        print(f"\n🧪 TEST {i}/4: Navigate to ({x}, {y}, {theta:.2f} rad)")
        print("-" * 30)
        
        start_time = time.time()
        success = navigator.send_goal(x, y, theta)
        end_time = time.time()
        
        if success:
            success_count += 1
            duration = end_time - start_time
            print(f"✅ Test {i} PASSED - Duration: {duration:.1f}s")
        else:
            print(f"❌ Test {i} FAILED")
        
        # Wait before next test
        if i < len(test_goals):
            print("⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Final results
    print("\n" + "="*50)
    print("📊 NAVIGATION TEST RESULTS")
    print("="*50)
    print(f"Tests Passed: {success_count}/{len(test_goals)}")
    print(f"Success Rate: {(success_count/len(test_goals)*100):.1f}%")
    
    if success_count == len(test_goals):
        print("🎉 ALL TESTS PASSED! Navigation system is working perfectly!")
    elif success_count > len(test_goals) // 2:
        print("⚠️  Most tests passed. Check failed tests for issues.")
    else:
        print("❌ Multiple test failures. Check Nav2 configuration.")
    
    print("="*50)
    
    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    try:
        run_navigation_tests()
    except KeyboardInterrupt:
        print("\n🛑 Navigation tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during navigation tests: {e}")
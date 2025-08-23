#!/usr/bin/env python3
"""
Navigation Fix Script
Diagnoses and fixes common Nav2 integration issues
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import time
import math

class NavigationFixer(Node):
    def __init__(self):
        super().__init__('navigation_fixer')
        
        # Create goal publisher to test connection
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        
        self.get_logger().info("🔧 Navigation Fixer Started")
        
    def test_goal_publishing(self):
        """Test if we can publish to goal_pose topic"""
        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.pose.position.x = 1.0
        goal.pose.position.y = 0.0
        goal.pose.position.z = 0.0
        goal.pose.orientation.w = 1.0
        
        self.get_logger().info("📤 Publishing test goal to /goal_pose...")
        self.goal_pub.publish(goal)
        return True

def main():
    rclpy.init()
    fixer = NavigationFixer()
    
    print("\n🔧 NAVIGATION SYSTEM DIAGNOSIS")
    print("="*40)
    
    # Test goal publishing
    if fixer.test_goal_publishing():
        print("✅ Goal publishing works")
    else:
        print("❌ Goal publishing failed")
    
    print("\n📋 MANUAL FIXES:")
    print("1. Restart navigation system:")
    print("   pkill -f navigation.sh")
    print("   ./navigation.sh --complex-office")
    print("")
    print("2. Try direct RViz goal:")
    print("   - Click 2D Goal Pose in toolbar") 
    print("   - Click on WHITE areas of map")
    print("   - Avoid black/dark areas")
    print("")
    print("3. Check if Nav2 actions are working:")
    print("   ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose \"goal: {pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0}}}}\"")
    
    # Keep node alive briefly for testing
    rclpy.spin_once(fixer, timeout_sec=2.0)
    
    fixer.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
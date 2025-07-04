#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import math

class WorldVisualizer(Node):
    def __init__(self):
        super().__init__('world_visualizer')
        
        # Publisher for markers
        self.marker_pub = self.create_publisher(MarkerArray, '/visualization_marker_array', 10)
        
        # Timer to publish markers
        self.timer = self.create_timer(1.0, self.publish_world_markers)
        
        print("✅ World visualizer started - publishing markers for RViz")
    
    def publish_world_markers(self):
        """Publish visualization markers for the world objects"""
        marker_array = MarkerArray()
        marker_id = 0
        
        # Ground plane marker
        ground = Marker()
        ground.header.frame_id = "world"
        ground.header.stamp = self.get_clock().now().to_msg()
        ground.ns = "world"
        ground.id = marker_id
        marker_id += 1
        ground.type = Marker.CUBE
        ground.action = Marker.ADD
        ground.pose.position.x = 0.0
        ground.pose.position.y = 0.0
        ground.pose.position.z = -0.01
        ground.pose.orientation.w = 1.0
        ground.scale.x = 20.0
        ground.scale.y = 20.0
        ground.scale.z = 0.02
        ground.color.r = 0.5
        ground.color.g = 0.5
        ground.color.b = 0.5
        ground.color.a = 0.3
        marker_array.markers.append(ground)
        
        # Room walls
        walls = [
            {"pos": [0, 6, 1.5], "size": [12, 0.2, 3], "color": [0.8, 0.4, 0.2]},  # North
            {"pos": [0, -6, 1.5], "size": [12, 0.2, 3], "color": [0.8, 0.4, 0.2]}, # South
            {"pos": [6, 0, 1.5], "size": [0.2, 12, 3], "color": [0.8, 0.4, 0.2]},  # East
            {"pos": [-6, 0, 1.5], "size": [0.2, 12, 3], "color": [0.8, 0.4, 0.2]}  # West
        ]
        
        for wall in walls:
            marker = Marker()
            marker.header.frame_id = "world"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "walls"
            marker.id = marker_id
            marker_id += 1
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = float(wall["pos"][0])
            marker.pose.position.y = float(wall["pos"][1])
            marker.pose.position.z = float(wall["pos"][2])
            marker.pose.orientation.w = 1.0
            marker.scale.x = float(wall["size"][0])
            marker.scale.y = float(wall["size"][1])
            marker.scale.z = float(wall["size"][2])
            marker.color.r = float(wall["color"][0])
            marker.color.g = float(wall["color"][1])
            marker.color.b = float(wall["color"][2])
            marker.color.a = 0.7
            marker_array.markers.append(marker)
        
        # Obstacles
        obstacles = [
            {"pos": [3, 2, 0.5], "size": [0.8, 0.8, 1], "color": [1.0, 0.5, 0.0], "type": "box"},    # Orange box
            {"pos": [-4, -2, 0.75], "size": [0.8, 0.8, 1.5], "color": [0.0, 0.5, 1.0], "type": "cylinder"}  # Blue cylinder
        ]
        
        for obs in obstacles:
            marker = Marker()
            marker.header.frame_id = "world"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "obstacles"
            marker.id = marker_id
            marker_id += 1
            marker.type = Marker.CUBE if obs["type"] == "box" else Marker.CYLINDER
            marker.action = Marker.ADD
            marker.pose.position.x = float(obs["pos"][0])
            marker.pose.position.y = float(obs["pos"][1])
            marker.pose.position.z = float(obs["pos"][2])
            marker.pose.orientation.w = 1.0
            marker.scale.x = float(obs["size"][0])
            marker.scale.y = float(obs["size"][1])
            marker.scale.z = float(obs["size"][2])
            marker.color.r = float(obs["color"][0])
            marker.color.g = float(obs["color"][1])
            marker.color.b = float(obs["color"][2])
            marker.color.a = 0.8
            marker_array.markers.append(marker)
        
        # Main table
        table_parts = [
            {"pos": [0, 0, 0.8], "size": [1.6, 1.0, 0.05], "color": [0.6, 0.3, 0.1]},  # Top
            {"pos": [-0.7, 0.4, 0.4], "size": [0.05, 0.05, 0.8], "color": [0.6, 0.3, 0.1]},  # Leg 1
            {"pos": [0.7, 0.4, 0.4], "size": [0.05, 0.05, 0.8], "color": [0.6, 0.3, 0.1]},   # Leg 2
            {"pos": [-0.7, -0.4, 0.4], "size": [0.05, 0.05, 0.8], "color": [0.6, 0.3, 0.1]}, # Leg 3
            {"pos": [0.7, -0.4, 0.4], "size": [0.05, 0.05, 0.8], "color": [0.6, 0.3, 0.1]}   # Leg 4
        ]
        
        for part in table_parts:
            marker = Marker()
            marker.header.frame_id = "world"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "table"
            marker.id = marker_id
            marker_id += 1
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = float(part["pos"][0])
            marker.pose.position.y = float(part["pos"][1])
            marker.pose.position.z = float(part["pos"][2])
            marker.pose.orientation.w = 1.0
            marker.scale.x = float(part["size"][0])
            marker.scale.y = float(part["size"][1])
            marker.scale.z = float(part["size"][2])
            marker.color.r = float(part["color"][0])
            marker.color.g = float(part["color"][1])
            marker.color.b = float(part["color"][2])
            marker.color.a = 0.9
            marker_array.markers.append(marker)
        
        # Glass on table
        glass = Marker()
        glass.header.frame_id = "world"
        glass.header.stamp = self.get_clock().now().to_msg()
        glass.ns = "pickup_objects"
        glass.id = marker_id
        marker_id += 1
        glass.type = Marker.CYLINDER
        glass.action = Marker.ADD
        glass.pose.position.x = 0.0
        glass.pose.position.y = 0.0
        glass.pose.position.z = 0.87
        glass.pose.orientation.w = 1.0
        glass.scale.x = 0.07
        glass.scale.y = 0.07
        glass.scale.z = 0.12
        glass.color.r = 0.0
        glass.color.g = 0.5
        glass.color.b = 1.0
        glass.color.a = 0.8
        marker_array.markers.append(glass)
        
        # Text label for glass
        text = Marker()
        text.header.frame_id = "world"
        text.header.stamp = self.get_clock().now().to_msg()
        text.ns = "labels"
        text.id = marker_id
        marker_id += 1
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = 0.0
        text.pose.position.y = 0.0
        text.pose.position.z = 1.0
        text.pose.orientation.w = 1.0
        text.scale.z = 0.1
        text.color.r = 1.0
        text.color.g = 1.0
        text.color.b = 1.0
        text.color.a = 1.0
        text.text = "PICKUP GLASS"
        marker_array.markers.append(text)
        
        # Publish the markers
        self.marker_pub.publish(marker_array)

def main():
    rclpy.init()
    
    try:
        visualizer = WorldVisualizer()
        print("🌍 World visualizer running - check RViz for world objects")
        print("   - MarkerArray topic: /visualization_marker_array")
        print("   - Press Ctrl+C to stop")
        rclpy.spin(visualizer)
    except KeyboardInterrupt:
        print("\n👋 World visualizer stopped")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
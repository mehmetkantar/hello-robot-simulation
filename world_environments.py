#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
from std_msgs.msg import String
import math
import random

class WorldEnvironments(Node):
    def __init__(self):
        super().__init__('world_environments')
        
        # Publisher for environment markers
        self.marker_pub = self.create_publisher(MarkerArray, '/environment_markers', 10)
        
        # Subscriber for world commands
        self.world_cmd_sub = self.create_subscription(
            String, '/world_command', self.world_command_callback, 10)
        
        # Timer to publish environment
        self.timer = self.create_timer(1.0, self.publish_environment)
        
        # Current world type
        self.current_world = "empty"
        
        # Available worlds
        self.worlds = {
            "empty": self.create_empty_world,
            "office": self.create_office_world,
            "warehouse": self.create_warehouse_world,
            "home": self.create_home_world,
            "maze": self.create_maze_world,
            "garden": self.create_garden_world,
            "factory": self.create_factory_world
        }
        
        print("✅ World environments node initialized")
    
    def world_command_callback(self, msg):
        """Handle world change commands"""
        world_name = msg.data
        self.set_world(world_name)
    
    def set_world(self, world_name):
        """Change the current world environment"""
        if world_name in self.worlds:
            self.current_world = world_name
            print(f"🌍 Switched to {world_name} world")
            self.publish_environment()
        else:
            print(f"❌ Unknown world: {world_name}")
    
    def publish_environment(self):
        """Publish the current environment markers"""
        if self.current_world in self.worlds:
            markers = self.worlds[self.current_world]()
            marker_array = MarkerArray()
            marker_array.markers = markers
            self.marker_pub.publish(marker_array)
    
    def create_empty_world(self):
        """Empty world with just a floor grid"""
        return []  # No additional markers needed
    
    def create_office_world(self):
        """Office environment with desks, chairs, and walls"""
        markers = []
        
        # Office walls
        walls = [
            # Outer walls
            {"pos": [5, 0, 1], "size": [0.2, 10, 2], "color": [0.8, 0.8, 0.8]},
            {"pos": [-5, 0, 1], "size": [0.2, 10, 2], "color": [0.8, 0.8, 0.8]},
            {"pos": [0, 5, 1], "size": [10, 0.2, 2], "color": [0.8, 0.8, 0.8]},
            {"pos": [0, -5, 1], "size": [10, 0.2, 2], "color": [0.8, 0.8, 0.8]},
            
            # Internal partition
            {"pos": [0, 2, 1], "size": [6, 0.2, 2], "color": [0.7, 0.7, 0.7]},
        ]
        
        # Office furniture
        furniture = [
            # Desks
            {"pos": [2, 3.5, 0.4], "size": [1.5, 0.8, 0.8], "color": [0.6, 0.4, 0.2]},
            {"pos": [-2, 3.5, 0.4], "size": [1.5, 0.8, 0.8], "color": [0.6, 0.4, 0.2]},
            {"pos": [2, -3, 0.4], "size": [1.5, 0.8, 0.8], "color": [0.6, 0.4, 0.2]},
            {"pos": [-2, -3, 0.4], "size": [1.5, 0.8, 0.8], "color": [0.6, 0.4, 0.2]},
            
            # Chairs
            {"pos": [2, 2.7, 0.4], "size": [0.5, 0.5, 0.8], "color": [0.2, 0.2, 0.8]},
            {"pos": [-2, 2.7, 0.4], "size": [0.5, 0.5, 0.8], "color": [0.2, 0.2, 0.8]},
            {"pos": [2, -2.2, 0.4], "size": [0.5, 0.5, 0.8], "color": [0.2, 0.2, 0.8]},
            {"pos": [-2, -2.2, 0.4], "size": [0.5, 0.5, 0.8], "color": [0.2, 0.2, 0.8]},
            
            # Filing cabinets
            {"pos": [4, 3.5, 0.6], "size": [0.6, 0.4, 1.2], "color": [0.5, 0.5, 0.5]},
            {"pos": [-4, 3.5, 0.6], "size": [0.6, 0.4, 1.2], "color": [0.5, 0.5, 0.5]},
        ]
        
        # Create markers
        marker_id = 0
        for items in [walls, furniture]:
            for item in items:
                marker = self.create_box_marker(marker_id, item["pos"], item["size"], item["color"])
                markers.append(marker)
                marker_id += 1
        
        return markers
    
    def create_warehouse_world(self):
        """Warehouse with storage racks and boxes"""
        markers = []
        marker_id = 0
        
        # Storage racks
        rack_positions = [
            [3, 2, 1.5], [3, 0, 1.5], [3, -2, 1.5],
            [-3, 2, 1.5], [-3, 0, 1.5], [-3, -2, 1.5],
            [0, 4, 1.5], [0, -4, 1.5]
        ]
        
        for pos in rack_positions:
            # Rack structure
            marker = self.create_box_marker(marker_id, pos, [0.8, 0.3, 3], [0.7, 0.5, 0.2])
            markers.append(marker)
            marker_id += 1
            
            # Boxes on racks
            for i in range(3):
                box_pos = [pos[0], pos[1], 0.5 + i * 0.6]
                marker = self.create_box_marker(marker_id, box_pos, [0.6, 0.25, 0.4], 
                                              [random.uniform(0.3, 0.9), random.uniform(0.3, 0.9), random.uniform(0.3, 0.9)])
                markers.append(marker)
                marker_id += 1
        
        # Floor boxes
        floor_boxes = [
            [1.5, 1, 0.2], [-1.5, 1, 0.2], [1.5, -1, 0.2], [-1.5, -1, 0.2],
            [0, 2.5, 0.2], [0, -2.5, 0.2]
        ]
        
        for pos in floor_boxes:
            marker = self.create_box_marker(marker_id, pos, [0.4, 0.4, 0.4], [0.8, 0.6, 0.4])
            markers.append(marker)
            marker_id += 1
        
        return markers
    
    def create_home_world(self):
        """Home environment with furniture"""
        markers = []
        marker_id = 0
        
        # Walls
        walls = [
            {"pos": [4, 0, 1], "size": [0.2, 8, 2], "color": [0.9, 0.9, 0.8]},
            {"pos": [-4, 0, 1], "size": [0.2, 8, 2], "color": [0.9, 0.9, 0.8]},
            {"pos": [0, 4, 1], "size": [8, 0.2, 2], "color": [0.9, 0.9, 0.8]},
            {"pos": [0, -4, 1], "size": [8, 0.2, 2], "color": [0.9, 0.9, 0.8]},
            {"pos": [1, 0, 1], "size": [0.2, 4, 2], "color": [0.9, 0.9, 0.8]},  # Room divider
        ]
        
        # Living room furniture
        furniture = [
            # Sofa
            {"pos": [-2, 2, 0.4], "size": [2, 0.8, 0.8], "color": [0.6, 0.3, 0.3]},
            # Coffee table
            {"pos": [-2, 0.5, 0.2], "size": [1, 0.6, 0.4], "color": [0.5, 0.3, 0.1]},
            # TV stand
            {"pos": [-3, -2.5, 0.3], "size": [1.5, 0.4, 0.6], "color": [0.3, 0.3, 0.3]},
            # Dining table
            {"pos": [2.5, 2, 0.4], "size": [1.2, 1.2, 0.8], "color": [0.6, 0.4, 0.2]},
            # Chairs
            {"pos": [2, 2.5, 0.4], "size": [0.4, 0.4, 0.8], "color": [0.6, 0.4, 0.2]},
            {"pos": [3, 2.5, 0.4], "size": [0.4, 0.4, 0.8], "color": [0.6, 0.4, 0.2]},
            {"pos": [2, 1.5, 0.4], "size": [0.4, 0.4, 0.8], "color": [0.6, 0.4, 0.2]},
            {"pos": [3, 1.5, 0.4], "size": [0.4, 0.4, 0.8], "color": [0.6, 0.4, 0.2]},
            # Kitchen counter
            {"pos": [2.5, -2, 0.4], "size": [2, 0.6, 0.8], "color": [0.8, 0.8, 0.9]},
        ]
        
        for items in [walls, furniture]:
            for item in items:
                marker = self.create_box_marker(marker_id, item["pos"], item["size"], item["color"])
                markers.append(marker)
                marker_id += 1
        
        return markers
    
    def create_maze_world(self):
        """Maze environment for navigation challenges"""
        markers = []
        marker_id = 0
        
        # Maze walls
        wall_positions = [
            # Outer boundary
            [5, 0, 1], [-5, 0, 1], [0, 5, 1], [0, -5, 1],
            # Inner maze walls
            [3, 3, 1], [3, 1, 1], [3, -1, 1], [3, -3, 1],
            [-3, 3, 1], [-3, 1, 1], [-3, -1, 1], [-3, -3, 1],
            [1, 3, 1], [1, -3, 1], [-1, 3, 1], [-1, -3, 1],
            [2, 2, 1], [2, 0, 1], [2, -2, 1],
            [-2, 2, 1], [-2, 0, 1], [-2, -2, 1],
            [0, 2, 1], [0, -2, 1], [4, 2, 1], [4, -2, 1],
            [-4, 2, 1], [-4, -2, 1]
        ]
        
        for pos in wall_positions:
            if pos[0] in [5, -5]:  # Outer walls
                size = [0.2, 10, 2]
            elif pos[1] in [5, -5]:  # Outer walls
                size = [10, 0.2, 2]
            else:  # Inner walls
                size = [0.3, 0.3, 2]
            
            marker = self.create_box_marker(marker_id, pos, size, [0.7, 0.7, 0.7])
            markers.append(marker)
            marker_id += 1
        
        # Goal marker
        goal_marker = self.create_sphere_marker(marker_id, [4.5, 4.5, 0.5], 0.3, [0, 1, 0])
        markers.append(goal_marker)
        
        return markers
    
    def create_garden_world(self):
        """Garden environment with trees and paths"""
        markers = []
        marker_id = 0
        
        # Trees (cylinders)
        tree_positions = [
            [3, 3], [3, -3], [-3, 3], [-3, -3],
            [1.5, 2], [1.5, -2], [-1.5, 2], [-1.5, -2],
            [4, 0], [-4, 0], [0, 4], [0, -4]
        ]
        
        for pos in tree_positions:
            # Tree trunk
            trunk = self.create_cylinder_marker(marker_id, [pos[0], pos[1], 1], 0.2, 2, [0.4, 0.2, 0.1])
            markers.append(trunk)
            marker_id += 1
            
            # Tree canopy
            canopy = self.create_sphere_marker(marker_id, [pos[0], pos[1], 2.5], 1.0, [0.2, 0.8, 0.2])
            markers.append(canopy)
            marker_id += 1
        
        # Flower beds
        flower_beds = [
            [2, 0], [-2, 0], [0, 2], [0, -2]
        ]
        
        for pos in flower_beds:
            bed = self.create_box_marker(marker_id, [pos[0], pos[1], 0.1], [0.8, 0.8, 0.2], [0.6, 0.4, 0.2])
            markers.append(bed)
            marker_id += 1
            
            # Flowers
            for i in range(5):
                flower_x = pos[0] + random.uniform(-0.3, 0.3)
                flower_y = pos[1] + random.uniform(-0.3, 0.3)
                flower = self.create_sphere_marker(marker_id, [flower_x, flower_y, 0.3], 0.1, 
                                                 [random.uniform(0.7, 1.0), random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)])
                markers.append(flower)
                marker_id += 1
        
        # Garden path
        path_points = [
            [-4.5, -4.5], [-2, -2], [0, 0], [2, 2], [4.5, 4.5]
        ]
        
        for i, point in enumerate(path_points):
            path_marker = self.create_cylinder_marker(marker_id, [point[0], point[1], 0.05], 0.4, 0.1, [0.8, 0.8, 0.6])
            markers.append(path_marker)
            marker_id += 1
        
        return markers
    
    def create_factory_world(self):
        """Factory environment with machines and conveyor belts"""
        markers = []
        marker_id = 0
        
        # Factory machines
        machines = [
            {"pos": [3, 2, 0.8], "size": [1.5, 1, 1.6], "color": [0.6, 0.6, 0.7]},
            {"pos": [3, -2, 0.8], "size": [1.5, 1, 1.6], "color": [0.6, 0.6, 0.7]},
            {"pos": [-3, 2, 0.8], "size": [1.5, 1, 1.6], "color": [0.6, 0.6, 0.7]},
            {"pos": [-3, -2, 0.8], "size": [1.5, 1, 1.6], "color": [0.6, 0.6, 0.7]},
        ]
        
        # Conveyor belts
        conveyors = [
            {"pos": [0, 1, 0.2], "size": [6, 0.4, 0.4], "color": [0.3, 0.3, 0.3]},
            {"pos": [0, -1, 0.2], "size": [6, 0.4, 0.4], "color": [0.3, 0.3, 0.3]},
            {"pos": [1, 0, 0.2], "size": [0.4, 2, 0.4], "color": [0.3, 0.3, 0.3]},
            {"pos": [-1, 0, 0.2], "size": [0.4, 2, 0.4], "color": [0.3, 0.3, 0.3]},
        ]
        
        # Control panels
        panels = [
            {"pos": [2, 2.8, 1], "size": [0.3, 0.2, 0.8], "color": [0.2, 0.2, 0.8]},
            {"pos": [2, -2.8, 1], "size": [0.3, 0.2, 0.8], "color": [0.2, 0.2, 0.8]},
            {"pos": [-2, 2.8, 1], "size": [0.3, 0.2, 0.8], "color": [0.2, 0.2, 0.8]},
            {"pos": [-2, -2.8, 1], "size": [0.3, 0.2, 0.8], "color": [0.2, 0.2, 0.8]},
        ]
        
        for items in [machines, conveyors, panels]:
            for item in items:
                marker = self.create_box_marker(marker_id, item["pos"], item["size"], item["color"])
                markers.append(marker)
                marker_id += 1
        
        # Warning lights (spheres)
        warning_positions = [[3, 2.5, 2.2], [3, -2.5, 2.2], [-3, 2.5, 2.2], [-3, -2.5, 2.2]]
        for pos in warning_positions:
            light = self.create_sphere_marker(marker_id, pos, 0.1, [1, 0.5, 0])
            markers.append(light)
            marker_id += 1
        
        return markers
    
    def create_box_marker(self, marker_id, position, size, color):
        """Create a box marker"""
        marker = Marker()
        marker.header.frame_id = "world"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "environment"
        marker.id = marker_id
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        
        marker.pose.position.x = float(position[0])
        marker.pose.position.y = float(position[1])
        marker.pose.position.z = float(position[2])
        marker.pose.orientation.w = 1.0
        
        marker.scale.x = float(size[0])
        marker.scale.y = float(size[1])
        marker.scale.z = float(size[2])
        
        marker.color.r = float(color[0])
        marker.color.g = float(color[1])
        marker.color.b = float(color[2])
        marker.color.a = 1.0
        
        return marker
    
    def create_sphere_marker(self, marker_id, position, radius, color):
        """Create a sphere marker"""
        marker = Marker()
        marker.header.frame_id = "world"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "environment"
        marker.id = marker_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        
        marker.pose.position.x = float(position[0])
        marker.pose.position.y = float(position[1])
        marker.pose.position.z = float(position[2])
        marker.pose.orientation.w = 1.0
        
        marker.scale.x = float(radius * 2)
        marker.scale.y = float(radius * 2)
        marker.scale.z = float(radius * 2)
        
        marker.color.r = float(color[0])
        marker.color.g = float(color[1])
        marker.color.b = float(color[2])
        marker.color.a = 1.0
        
        return marker
    
    def create_cylinder_marker(self, marker_id, position, radius, height, color):
        """Create a cylinder marker"""
        marker = Marker()
        marker.header.frame_id = "world"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "environment"
        marker.id = marker_id
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD
        
        marker.pose.position.x = float(position[0])
        marker.pose.position.y = float(position[1])
        marker.pose.position.z = float(position[2])
        marker.pose.orientation.w = 1.0
        
        marker.scale.x = float(radius * 2)
        marker.scale.y = float(radius * 2)
        marker.scale.z = float(height)
        
        marker.color.r = float(color[0])
        marker.color.g = float(color[1])
        marker.color.b = float(color[2])
        marker.color.a = 1.0
        
        return marker

def main():
    rclpy.init()
    
    world_env = WorldEnvironments()
    
    try:
        rclpy.spin(world_env)
    except KeyboardInterrupt:
        pass
    finally:
        world_env.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
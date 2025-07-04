#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os

def fix_robot_urdf():
    """Fix the robot URDF to make it visible in Gazebo"""
    
    urdf_file = "/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
    fixed_urdf = "/tmp/stretch_robot_fixed.urdf"
    
    print("🔧 Fixing robot URDF for better visibility...")
    
    # Read the original URDF
    tree = ET.parse(urdf_file)
    root = tree.getroot()
    
    # Find all visual elements and replace missing meshes with basic shapes
    visual_count = 0
    mesh_count = 0
    
    for visual in root.iter('visual'):
        visual_count += 1
        geometry = visual.find('geometry')
        
        if geometry is not None:
            mesh = geometry.find('mesh')
            if mesh is not None:
                mesh_count += 1
                # Get the parent link name
                link = visual.getparent()
                while link is not None and link.tag != 'link':
                    link = link.getparent()
                
                link_name = link.get('name') if link is not None else 'unknown'
                
                # Replace mesh with a colored box for visibility
                geometry.clear()
                box = ET.SubElement(geometry, 'box')
                
                # Size based on link type
                if 'base' in link_name.lower():
                    size = "0.5 0.3 0.2"  # Base
                elif 'wheel' in link_name.lower():
                    size = "0.1 0.1 0.05"  # Wheels
                elif 'arm' in link_name.lower():
                    size = "0.1 0.1 0.3"  # Arm segments
                elif 'gripper' in link_name.lower():
                    size = "0.05 0.02 0.1"  # Gripper
                elif 'head' in link_name.lower():
                    size = "0.15 0.1 0.1"  # Head
                else:
                    size = "0.1 0.1 0.1"  # Default
                
                box.set('size', size)
                
                # Add bright material for visibility
                material = visual.find('material')
                if material is None:
                    material = ET.SubElement(visual, 'material')
                    material.set('name', f"{link_name}_material")
                
                color = material.find('color')
                if color is None:
                    color = ET.SubElement(material, 'color')
                
                # Color code different parts
                if 'base' in link_name.lower():
                    color.set('rgba', '0 0 1 1')  # Blue base
                elif 'wheel' in link_name.lower():
                    color.set('rgba', '0.3 0.3 0.3 1')  # Gray wheels
                elif 'arm' in link_name.lower():
                    color.set('rgba', '1 0.5 0 1')  # Orange arm
                elif 'gripper' in link_name.lower():
                    color.set('rgba', '1 0 0 1')  # Red gripper
                elif 'head' in link_name.lower():
                    color.set('rgba', '0 1 0 1')  # Green head
                else:
                    color.set('rgba', '0.8 0.8 0.8 1')  # Light gray default
    
    print(f"✅ Processed {visual_count} visual elements, replaced {mesh_count} meshes with basic shapes")
    
    # Save the fixed URDF
    tree.write(fixed_urdf, encoding='utf-8', xml_declaration=True)
    
    print(f"💾 Saved fixed URDF to: {fixed_urdf}")
    
    return fixed_urdf

def create_test_world_with_robot(urdf_file):
    """Create a world file with the robot"""
    
    world_content = f'''<?xml version="1.0"?>
<sdf version="1.6">
  <world name="stretch_test_world">
    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Reference box for scale -->
    <model name="reference_box">
      <pose>2 0 0.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>1 1 0 1</ambient>
            <diffuse>1 1 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Lighting -->
    <light name="sun" type="directional">
      <cast_shadows>1</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Include the robot URDF -->
    <model name="stretch_robot">
      <pose>0 0 0.1 0 0 0</pose>
      <include>
        <uri>file://{urdf_file}</uri>
      </include>
    </model>
  </world>
</sdf>'''
    
    world_file = "/tmp/stretch_test_world.world"
    with open(world_file, 'w') as f:
        f.write(world_content)
    
    print(f"🌍 Created test world: {world_file}")
    return world_file

if __name__ == "__main__":
    print("🤖 Robot Display Fix Tool")
    print("=========================")
    
    # Fix the URDF
    fixed_urdf = fix_robot_urdf()
    
    # Create test world
    world_file = create_test_world_with_robot(fixed_urdf)
    
    print("")
    print("🚀 Ready to test! Run:")
    print(f"   gazebo {world_file}")
    print("")
    print("🎯 You should see:")
    print("   - Yellow reference cube (1x1x1 meter)")
    print("   - Colorful robot made of basic shapes:")
    print("     • Blue base")
    print("     • Orange arm segments") 
    print("     • Red gripper")
    print("     • Green head")
    print("     • Gray wheels")
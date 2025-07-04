#!/usr/bin/env python3

import os
import subprocess
import tempfile

def convert_urdf_to_sdf():
    """Convert URDF to SDF format for better Gazebo compatibility"""
    
    urdf_file = "/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
    
    if not os.path.exists(urdf_file):
        print(f"❌ URDF file not found: {urdf_file}")
        return None
    
    print("🔄 Converting URDF to SDF format...")
    
    # Use gz sdf tool to convert URDF to SDF
    try:
        result = subprocess.run([
            'gz', 'sdf', '-p', urdf_file
        ], capture_output=True, text=True, check=True)
        
        sdf_content = result.stdout
        
        # Save SDF file
        sdf_file = "/tmp/stretch_robot.sdf"
        with open(sdf_file, 'w') as f:
            f.write(sdf_content)
        
        print(f"✅ SDF file created: {sdf_file}")
        return sdf_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ URDF to SDF conversion failed: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ 'gz' command not found. Install with: sudo apt install gz-tools")
        return None

def test_sdf_in_gazebo(sdf_file):
    """Test the SDF file in Gazebo"""
    
    if not sdf_file or not os.path.exists(sdf_file):
        print("❌ No valid SDF file to test")
        return False
    
    print("🚀 Testing SDF file in Gazebo...")
    
    # Create a simple world file that includes our robot
    world_content = f"""<?xml version="1.0"?>
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

    <!-- Lighting -->
    <light name="sun" type="directional">
      <cast_shadows>1</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Include the robot -->
    <include>
      <uri>file://{sdf_file}</uri>
      <pose>0 0 0.1 0 0 0</pose>
    </include>
  </world>
</sdf>"""
    
    # Save world file
    world_file = "/tmp/stretch_test_world.world"
    with open(world_file, 'w') as f:
        f.write(world_content)
    
    print(f"📝 Created world file: {world_file}")
    print("🎯 Starting Gazebo with robot...")
    print("   This should open Gazebo with the Stretch robot visible")
    print("   Press Ctrl+C in this terminal to stop")
    
    try:
        # Start Gazebo with our world
        subprocess.run(['gazebo', '--verbose', world_file], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Gazebo...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gazebo failed: {e}")
        return False
    finally:
        # Cleanup
        subprocess.run(['killall', '-9', 'gzserver', 'gzclient', 'gazebo'], 
                      capture_output=True, check=False)
    
    return True

if __name__ == "__main__":
    print("🔧 URDF to SDF Conversion and Gazebo Test")
    print("=" * 45)
    
    # Kill any existing Gazebo processes
    subprocess.run(['killall', '-9', 'gzserver', 'gzclient', 'gazebo'], 
                   capture_output=True, check=False)
    
    # Convert URDF to SDF
    sdf_file = convert_urdf_to_sdf()
    
    if sdf_file:
        # Test in Gazebo
        test_sdf_in_gazebo(sdf_file)
    else:
        print("❌ Cannot proceed without valid SDF file")
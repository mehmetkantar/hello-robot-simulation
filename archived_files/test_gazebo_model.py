#!/usr/bin/env python3

import os
import sys
import subprocess
import tempfile
import time

def test_gazebo_model():
    print("🔧 Gazebo Model Test - Hello Robot Stretch 3")
    print("=" * 50)
    
    # Kill any existing Gazebo processes
    print("🧹 Cleaning up existing Gazebo processes...")
    subprocess.run(['killall', '-9', 'gzserver', 'gzclient', 'gazebo'], 
                   capture_output=True, check=False)
    time.sleep(2)
    
    # Find the URDF file
    urdf_file = "/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
    
    if not os.path.exists(urdf_file):
        print(f"❌ URDF file not found: {urdf_file}")
        return False
    
    print(f"✅ Found URDF file: {urdf_file}")
    
    # Test 1: Start Gazebo with empty world
    print("\n🧪 Test 1: Starting Gazebo with empty world...")
    try:
        # Start Gazebo server in background
        gazebo_process = subprocess.Popen([
            'gazebo', 
            '--verbose',
            '/opt/ros/humble/share/gazebo_ros/worlds/empty.world'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        print("⏳ Waiting 10 seconds for Gazebo to start...")
        time.sleep(10)
        
        if gazebo_process.poll() is None:
            print("✅ Gazebo started successfully!")
            
            # Test 2: Load robot model
            print("\n🧪 Test 2: Loading robot model...")
            
            # Create a simple world file with the robot
            world_content = f'''<?xml version="1.0"?>
<sdf version="1.6">
  <world name="stretch_test">
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://sun</uri>
    </include>
    
    <model name="stretch_robot">
      <pose>0 0 0 0 0 0</pose>
      <include>
        <uri>file://{urdf_file}</uri>
      </include>
    </model>
  </world>
</sdf>'''
            
            # Save world file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.world', delete=False) as f:
                f.write(world_content)
                world_file = f.name
            
            print(f"📝 Created test world file: {world_file}")
            
            # Kill current Gazebo and restart with robot
            gazebo_process.terminate()
            gazebo_process.wait()
            time.sleep(2)
            
            print("🚀 Starting Gazebo with robot model...")
            gazebo_with_robot = subprocess.Popen([
                'gazebo', 
                '--verbose',
                world_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("⏳ Waiting 15 seconds for robot to load...")
            time.sleep(15)
            
            if gazebo_with_robot.poll() is None:
                print("✅ Gazebo with robot model is running!")
                print("🎯 Check the Gazebo window - you should see the Stretch robot!")
                print("   Press Ctrl+C when done viewing")
                
                try:
                    gazebo_with_robot.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping Gazebo...")
                    gazebo_with_robot.terminate()
                    gazebo_with_robot.wait()
            else:
                print("❌ Gazebo with robot failed to start")
                stdout, stderr = gazebo_with_robot.communicate()
                print(f"Error: {stderr.decode()}")
                return False
                
            # Cleanup
            os.unlink(world_file)
            
        else:
            print("❌ Gazebo failed to start")
            stdout, stderr = gazebo_process.communicate()
            print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    
    print("✅ Test completed successfully!")
    return True

if __name__ == "__main__":
    test_gazebo_model()
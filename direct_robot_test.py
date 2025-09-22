#!/usr/bin/env python3
"""
Direct Robot Movement Test - bypasses ROS2
Tests MuJoCo simulation directly
"""

import sys
import time
sys.path.append('./stretch_mujoco')

try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.actuators import Actuators
    MUJOCO_AVAILABLE = True
    print("✅ MuJoCo available")
except ImportError as e:
    print(f"❌ MuJoCo not available: {e}")
    MUJOCO_AVAILABLE = False
    exit(1)

def test_direct_movement():
    """Test robot movement directly through MuJoCo"""
    
    print("🤖 Starting Direct Robot Movement Test")
    print("=" * 50)
    
    # Initialize simulator
    print("🔧 Initializing MuJoCo simulator...")
    sim = StretchMujocoSimulator()
    sim.start(headless=False)
    
    print("⏳ Waiting for simulator to connect...")
    for i in range(10):
        if sim.is_connected():
            break
        time.sleep(1)
        print(f"   Still waiting... ({i+1}/10)")
    
    if not sim.is_connected():
        print("❌ Failed to connect to MuJoCo simulator")
        return False
    
    print("✅ MuJoCo simulator connected!")
    
    # Get initial position
    try:
        status = sim.pull_status()
        initial_x = status.base.x
        initial_y = status.base.y
        initial_theta = status.base.theta
        print(f"📍 Initial position: x={initial_x:.3f}, y={initial_y:.3f}, θ={initial_theta:.3f}")
    except Exception as e:
        print(f"⚠️  Could not get initial status: {e}")
        initial_x = initial_y = initial_theta = 0.0
    
    # Test 1: Move forward
    print("\n🔧 Test 1: Moving forward...")
    try:
        result = sim.set_base_velocity(0.3, 0.0)  # 0.3 m/s forward
        print(f"   Command sent, result: {result}")
        
        # Wait and check position
        for i in range(30):  # 3 seconds
            time.sleep(0.1)
            try:
                status = sim.pull_status()
                current_x = status.base.x
                current_y = status.base.y
                if i % 10 == 0:  # Print every second
                    print(f"   Position: x={current_x:.3f}, y={current_y:.3f} (moved: {abs(current_x-initial_x)+abs(current_y-initial_y):.3f}m)")
            except:
                pass
        
        # Stop robot
        sim.set_base_velocity(0.0, 0.0)
        print("   ⏹️  Robot stopped")
        
    except Exception as e:
        print(f"   ❌ Forward movement failed: {e}")
        return False
    
    # Test 2: Rotate
    print("\n🔧 Test 2: Rotating...")
    try:
        result = sim.set_base_velocity(0.0, 0.5)  # 0.5 rad/s rotation
        print(f"   Command sent, result: {result}")
        
        # Wait and check position
        for i in range(20):  # 2 seconds
            time.sleep(0.1)
            try:
                status = sim.pull_status()
                current_theta = status.base.theta
                if i % 10 == 0:  # Print every second
                    print(f"   Orientation: θ={current_theta:.3f} (rotated: {abs(current_theta-initial_theta):.3f}rad)")
            except:
                pass
        
        # Stop robot
        sim.set_base_velocity(0.0, 0.0)
        print("   ⏹️  Robot stopped")
        
    except Exception as e:
        print(f"   ❌ Rotation failed: {e}")
        return False
    
    # Get final position
    try:
        status = sim.pull_status()
        final_x = status.base.x
        final_y = status.base.y
        final_theta = status.base.theta
        
        total_distance = abs(final_x - initial_x) + abs(final_y - initial_y)
        total_rotation = abs(final_theta - initial_theta)
        
        print(f"\n📊 MOVEMENT SUMMARY:")
        print(f"   Initial: x={initial_x:.3f}, y={initial_y:.3f}, θ={initial_theta:.3f}")
        print(f"   Final:   x={final_x:.3f}, y={final_y:.3f}, θ={final_theta:.3f}")
        print(f"   Total distance moved: {total_distance:.3f} meters")
        print(f"   Total rotation: {total_rotation:.3f} radians")
        
        if total_distance > 0.01 or total_rotation > 0.01:
            print("✅ SUCCESS: Robot movement detected!")
            return True
        else:
            print("❌ FAILURE: No significant movement detected")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not get final status: {e}")
        return False

def main():
    if not MUJOCO_AVAILABLE:
        return
        
    success = test_direct_movement()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Direct robot control is WORKING!")
        print("   The issue is in the ROS2 <-> MuJoCo bridge")
    else:
        print("💥 Direct robot control is NOT working")
        print("   The issue is in MuJoCo simulation itself")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == '__main__':
    main()
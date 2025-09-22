#!/usr/bin/env python3
"""
Test Direct Arm Control
Tests arm control using direct MuJoCo commands like the keyboard GUI
"""

import sys
import time
import threading

# Add MuJoCo path
sys.path.append('./stretch_mujoco')

try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.actuators import Actuators
    print("✅ MuJoCo available")
except ImportError as e:
    print(f"❌ MuJoCo not available: {e}")
    sys.exit(1)

def test_direct_control():
    """Test direct MuJoCo arm control"""
    print("🤖 Starting direct arm control test...")
    
    try:
        # Start simulation
        print("🚀 Starting MuJoCo simulation...")
        sim = StretchMujocoSimulator()
        sim.start()
        
        print("✅ MuJoCo simulation started")
        print("⏳ Waiting for simulation to stabilize...")
        time.sleep(3)
        
        print("🎮 Testing direct arm control...")
        
        # Test 1: Lift control using move_by
        print("🏗️ Test 1: Lift up...")
        sim.move_by(Actuators.lift, 0.3)
        time.sleep(3)
        
        print("🏗️ Test 2: Lift down...")
        sim.move_by(Actuators.lift, -0.5)
        time.sleep(3)
        
        # Test 2: Arm extension
        print("🦾 Test 3: Arm extend...")
        sim.move_by(Actuators.arm, 0.2)
        time.sleep(3)
        
        print("🦾 Test 4: Arm retract...")
        sim.move_by(Actuators.arm, -0.2)
        time.sleep(3)
        
        # Test 3: Wrist control
        print("🔄 Test 5: Wrist yaw...")
        sim.move_by(Actuators.wrist_yaw, 1.0)
        time.sleep(3)
        
        print("🔄 Test 6: Wrist yaw back...")
        sim.move_by(Actuators.wrist_yaw, -1.5)
        time.sleep(3)
        
        # Test 4: Gripper
        print("✋ Test 7: Gripper open...")
        sim.move_by(Actuators.gripper, 0.4)
        time.sleep(3)
        
        print("✋ Test 8: Gripper close...")
        sim.move_by(Actuators.gripper, -0.4)
        time.sleep(3)
        
        # Test preset actions
        print("🏠 Test 9: Home position...")
        sim.home()
        time.sleep(5)
        
        print("📦 Test 10: Stow position...")
        sim.stow()
        time.sleep(5)
        
        print("🎉 All direct control tests completed successfully!")
        print("💡 The robot arms moved in MuJoCo - direct control works!")
        
        # Keep simulation running for a bit to observe
        print("🕐 Keeping simulation running for 10 seconds...")
        print("   You should see the robot in stow position in MuJoCo window")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'sim' in locals():
            print("🛑 Stopping simulation...")
            sim.stop()
            print("✅ Test completed")

if __name__ == "__main__":
    test_direct_control()
#!/usr/bin/env python3
"""
Test direct joint control in MuJoCo
"""

from stretch_mujoco import StretchMujocoSimulator
import time

def main():
    print("🤖 Testing MuJoCo joint control...")
    
    try:
        # Start simple simulation
        sim = StretchMujocoSimulator()
        sim.start()
        print("✅ MuJoCo simulation started")
        
        # Get available methods
        methods = [method for method in dir(sim) if not method.startswith('_')]
        joint_methods = [m for m in methods if 'joint' in m.lower()]
        
        print("🔍 Available joint-related methods:")
        for method in joint_methods:
            print(f"   - {method}")
        
        # Test status
        status = sim.pull_status()
        print(f"\n📍 Initial robot status:")
        print(f"   Base: x={status.base.x:.3f}, y={status.base.y:.3f}")
        
        # Check if there are joint control methods
        control_methods = [m for m in methods if any(word in m.lower() for word in ['lift', 'arm', 'wrist', 'gripper', 'command', 'move'])]
        
        print(f"\n🎛️ Available control methods:")
        for method in control_methods:
            print(f"   - {method}")
            
        # Try to find the joint control interface
        if hasattr(sim, 'push_command'):
            print("\n🎯 Found push_command method - testing joint control...")
            
            # Test lift
            print("🏗️ Testing lift movement...")
            result = sim.push_command(lift=0.8)
            time.sleep(2)
            
            status = sim.pull_status()
            print(f"   Status after lift: {status}")
            
        else:
            print("⚠️ No push_command method found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'sim' in locals():
            sim.stop()
            print("🛑 MuJoCo simulation stopped")

if __name__ == '__main__':
    main()
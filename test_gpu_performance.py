#!/usr/bin/env python3
"""
GPU Performance Test for MuJoCo Simulation
Tests GPU utilization and performance improvements
"""

import os
import sys
import time
import subprocess
import threading

# Apply GPU optimizations
os.environ['MUJOCO_GL'] = 'egl'
os.environ['MUJOCO_GPU_DEVICE_ID'] = '0'
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['__GL_SYNC_TO_VBLANK'] = '0'
os.environ['__GL_YIELD'] = 'NOTHING'
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'

sys.path.append('/home/user/stretch_mujoco')

def monitor_gpu():
    """Monitor GPU usage in a separate thread"""
    print("🔍 Starting GPU monitoring...")
    while True:
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,power.draw', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_util, mem_used, mem_total, power = result.stdout.strip().split(', ')
                print(f"📊 GPU: {gpu_util}% | Memory: {mem_used}/{mem_total}MB | Power: {power}W")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ GPU monitoring error: {e}")
            time.sleep(5)

def test_mujoco_performance():
    """Test MuJoCo performance with GPU optimizations"""
    try:
        from stretch_mujoco import StretchMujocoSimulator
        from stretch_mujoco.enums.stretch_cameras import StretchCameras
        
        print("🚀 Starting high-performance MuJoCo test...")
        
        # Configure for maximum GPU usage
        cameras = StretchCameras.rgb()
        
        # Use complex office environment for GPU stress test
        scene_path = "/home/user/stretch_mujoco/stretch_mujoco/models/complex_office_scene.xml"
        
        print("🏢 Loading complex office environment...")
        sim = StretchMujocoSimulator(scene_xml_path=scene_path, cameras_to_use=cameras)
        
        print("🖥️ Starting simulation with GPU acceleration...")
        sim.start(headless=False)  # Use GUI for full GPU load
        
        print("🏠 Homing robot...")
        sim.home()
        
        print("🎯 Running performance test for 60 seconds...")
        start_time = time.time()
        
        # Perform intensive operations to stress GPU
        for i in range(1000):
            # Move robot to create dynamic scenes
            sim.step_action({'base_translate_mobile_base': 0.1 if i % 20 < 10 else -0.1})
            sim.step_action({'base_rotate_mobile_base': 0.1 if i % 30 < 15 else -0.1})
            
            # Get camera images (GPU intensive)
            try:
                images = sim.get_images()
                if i % 100 == 0:
                    print(f"✅ Step {i}: Got {len(images)} camera images")
            except:
                pass
                
            time.sleep(0.01)  # 100 FPS target
            
            # Stop after 60 seconds
            if time.time() - start_time > 60:
                break
        
        print("🏁 Performance test completed!")
        print(f"⏱️ Test duration: {time.time() - start_time:.1f} seconds")
        
        # Keep simulation running for monitoring
        print("🔄 Keeping simulation running for monitoring...")
        print("💡 Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎮 GPU Performance Test for MuJoCo Simulation")
    print("=" * 50)
    
    # Start GPU monitoring in background
    monitor_thread = threading.Thread(target=monitor_gpu, daemon=True)
    monitor_thread.start()
    
    # Wait a moment for monitoring to start
    time.sleep(2)
    
    # Run performance test
    test_mujoco_performance()
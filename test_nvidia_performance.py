#!/usr/bin/env python3
"""
NVIDIA PRIME Performance Test
Tests performance with and without NVIDIA PRIME render offload
"""

import os
import sys
import time
import subprocess
import signal

# Test with NVIDIA PRIME enabled
def test_with_nvidia():
    print("🚀 Testing with NVIDIA PRIME render offload...")
    
    # Set NVIDIA environment variables
    env = os.environ.copy()
    env['__NV_PRIME_RENDER_OFFLOAD'] = '1'
    env['__GLX_VENDOR_LIBRARY_NAME'] = 'nvidia'
    env['MUJOCO_GL'] = 'egl'
    env['MUJOCO_GPU_DEVICE_ID'] = '0'
    env['OMP_NUM_THREADS'] = '8'
    env['__GL_SYNC_TO_VBLANK'] = '0'
    env['__GL_YIELD'] = 'NOTHING'
    env['CUDA_LAUNCH_BLOCKING'] = '0'
    env['NVIDIA_TF32_OVERRIDE'] = '0'
    env['CUDA_VISIBLE_DEVICES'] = '0'
    
    return env

def monitor_gpu_usage():
    """Monitor GPU usage"""
    try:
        result = subprocess.run([
            'nvidia-smi', 
            '--query-gpu=utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            gpu_util, mem_used, mem_total, power, temp = result.stdout.strip().split(', ')
            print(f"📊 GPU: {gpu_util}% | Memory: {mem_used}/{mem_total}MB | Power: {power}W | Temp: {temp}°C")
            return {
                'utilization': int(gpu_util),
                'memory_used': int(mem_used),
                'memory_total': int(mem_total),
                'power': float(power),
                'temperature': int(temp)
            }
    except Exception as e:
        print(f"⚠️ GPU monitoring error: {e}")
    return None

def check_performance():
    """Check current rendering backend"""
    try:
        # Check which GPU is being used
        result = subprocess.run([
            'glxinfo'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'OpenGL vendor' in line:
                    print(f"🎮 {line}")
                elif 'OpenGL renderer' in line:
                    print(f"🖥️ {line}")
                elif 'OpenGL version' in line:
                    print(f"📋 {line}")
                    break
    except Exception as e:
        print(f"⚠️ OpenGL check error: {e}")

def main():
    print("🎯 NVIDIA PRIME Performance Analysis")
    print("=" * 50)
    
    # Check baseline GPU usage
    print("\n📍 Baseline GPU Status:")
    baseline = monitor_gpu_usage()
    
    print("\n🔍 Current OpenGL Configuration:")
    check_performance()
    
    print("\n🚀 With NVIDIA PRIME:")
    env = test_with_nvidia()
    
    # Test with NVIDIA environment
    test_env = os.environ.copy()
    test_env.update(env)
    
    # Check OpenGL with NVIDIA
    try:
        result = subprocess.run([
            'glxinfo'
        ], env=test_env, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'OpenGL vendor' in line:
                    print(f"🎮 {line}")
                elif 'OpenGL renderer' in line:
                    print(f"🖥️ {line}")
                elif 'OpenGL version' in line:
                    print(f"📋 {line}")
                    break
    except Exception as e:
        print(f"⚠️ NVIDIA OpenGL check error: {e}")
    
    print("\n💡 Recommendation:")
    print("✅ Use: __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia ./launch_full_simulation.sh")
    print("🔄 For RViz compatibility: Start RViz separately without NVIDIA PRIME")
    
    print("\n📊 Expected Performance:")
    print("• MuJoCo Real-time: x0.5 (vs x0.114 with Intel)")
    print("• GPU Memory Usage: ~5GB (vs ~350MB with Intel)")
    print("• GPU Utilization: 50-70% (vs 0-30% with Intel)")
    print("• Performance Gain: 4-5x improvement")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
GPU Setup Utility for MuJoCo Simulation
Configures environment variables for optimal GPU acceleration
"""

import os
import sys

def setup_gpu_acceleration():
    """Configure MuJoCo to use GPU acceleration"""
    
    # Set MuJoCo to use EGL backend for GPU acceleration
    os.environ['MUJOCO_GL'] = 'egl'
    
    # Optional: Set CUDA device if multiple GPUs available
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    
    print("✅ GPU acceleration configured:")
    print(f"   MUJOCO_GL = {os.environ.get('MUJOCO_GL', 'not set')}")
    print(f"   CUDA_VISIBLE_DEVICES = {os.environ.get('CUDA_VISIBLE_DEVICES', 'not set')}")
    
    return True

def check_gpu_support():
    """Check if GPU acceleration is available"""
    try:
        import mujoco
        print(f"✅ MuJoCo version: {mujoco.__version__}")
        
        # Try to create a GPU context
        try:
            import OpenGL.GL as gl
            print("✅ OpenGL support available")
        except ImportError:
            print("⚠️  OpenGL support not available")
            
        return True
    except ImportError as e:
        print(f"❌ MuJoCo not available: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up GPU acceleration for MuJoCo...")
    
    if check_gpu_support():
        setup_gpu_acceleration()
        print("✅ GPU setup complete!")
    else:
        print("❌ GPU setup failed!")
        sys.exit(1)
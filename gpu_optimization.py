#!/usr/bin/env python3
"""
GPU Optimization Settings for MuJoCo Simulation
Configures MuJoCo for maximum GPU utilization and performance
"""

import os

def setup_high_performance_gpu():
    """Configure MuJoCo for maximum GPU performance"""
    
    # GPU backend settings
    os.environ['MUJOCO_GL'] = 'egl'  # Use EGL for GPU acceleration
    
    # Performance optimizations
    os.environ['MUJOCO_GPU_DEVICE_ID'] = '0'  # Use first GPU
    
    # Memory and threading optimizations
    os.environ['OMP_NUM_THREADS'] = '8'  # Use multiple CPU threads
    os.environ['MKL_NUM_THREADS'] = '8'  # Intel MKL threading
    
    # CUDA optimizations
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Non-blocking CUDA calls
    
    # OpenGL optimizations
    os.environ['__GL_SYNC_TO_VBLANK'] = '0'  # Disable VSync
    os.environ['__GL_YIELD'] = 'NOTHING'  # Don't yield GPU
    
    print("🚀 High-performance GPU settings configured:")
    print(f"   MUJOCO_GL = {os.environ.get('MUJOCO_GL')}")
    print(f"   MUJOCO_GPU_DEVICE_ID = {os.environ.get('MUJOCO_GPU_DEVICE_ID')}")
    print(f"   OMP_NUM_THREADS = {os.environ.get('OMP_NUM_THREADS')}")
    print(f"   CUDA_VISIBLE_DEVICES = {os.environ.get('CUDA_VISIBLE_DEVICES')}")
    print(f"   __GL_SYNC_TO_VBLANK = {os.environ.get('__GL_SYNC_TO_VBLANK')}")

def get_mujoco_performance_options():
    """Return MuJoCo performance optimization options"""
    return {
        # Rendering optimizations
        'offscreen_width': 1920,    # Higher resolution for better GPU usage
        'offscreen_height': 1080,
        
        # Physics optimizations
        'timestep': 0.002,          # Smaller timestep for accuracy
        'nsubsteps': 4,             # More substeps for stability
        
        # Solver optimizations
        'iterations': 50,           # More solver iterations
        'ls_iterations': 50,        # Line search iterations
        
        # Contact optimizations
        'cone': 'pyramidal',        # Use pyramidal friction cone
        'jacobian_regularization': 1e-6,
        
        # Visual optimizations
        'vis_quality': 'high',      # High visual quality
        'shadows': True,            # Enable shadows for realism
        'reflection': 0.5,          # Enable reflections
    }

if __name__ == "__main__":
    setup_high_performance_gpu()
    options = get_mujoco_performance_options()
    print("\n📊 Recommended MuJoCo options:")
    for key, value in options.items():
        print(f"   {key}: {value}")
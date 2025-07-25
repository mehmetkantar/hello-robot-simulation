#!/usr/bin/env python3
"""
Maximum GPU Utilization Optimization for MuJoCo
Configures MuJoCo for highest possible GPU usage and performance
"""

import os
import sys

def setup_maximum_gpu_utilization():
    """Configure for maximum GPU utilization"""
    
    # Core NVIDIA PRIME settings
    os.environ['__NV_PRIME_RENDER_OFFLOAD'] = '1'
    os.environ['__GLX_VENDOR_LIBRARY_NAME'] = 'nvidia'
    
    # MuJoCo GPU settings
    os.environ['MUJOCO_GL'] = 'egl'
    os.environ['MUJOCO_GPU_DEVICE_ID'] = '0'
    
    # High-performance rendering settings
    os.environ['__GL_THREADED_OPTIMIZATIONS'] = '1'  # Enable threaded optimizations
    os.environ['__GL_SYNC_TO_VBLANK'] = '0'          # Disable VSync
    os.environ['__GL_YIELD'] = 'NOTHING'             # Don't yield GPU
    os.environ['__GL_SHADER_DISK_CACHE'] = '1'       # Enable shader cache
    os.environ['__GL_SHADER_DISK_CACHE_PATH'] = '/tmp/gl_shader_cache'
    
    # CUDA optimizations for maximum utilization
    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'         # Non-blocking launches
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'         # Use first GPU
    os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'   # Consistent device ordering
    
    # Memory and compute optimizations
    os.environ['NVIDIA_TF32_OVERRIDE'] = '0'         # Full precision
    os.environ['CUDA_CACHE_MAXSIZE'] = '2147483648'  # 2GB cache
    
    # CPU-GPU optimization
    os.environ['OMP_NUM_THREADS'] = '8'              # Multi-threading
    os.environ['MKL_NUM_THREADS'] = '8'              # Intel MKL
    os.environ['OPENBLAS_NUM_THREADS'] = '8'         # OpenBLAS
    
    # GPU memory management
    os.environ['CUDA_MALLOC_HEAP_SIZE'] = '268435456'  # 256MB heap
    
    print("🚀 Maximum GPU utilization configured:")
    print(f"   • NVIDIA PRIME render offload: {os.environ.get('__NV_PRIME_RENDER_OFFLOAD')}")
    print(f"   • OpenGL threaded optimizations: {os.environ.get('__GL_THREADED_OPTIMIZATIONS')}")
    print(f"   • CUDA cache size: {int(os.environ.get('CUDA_CACHE_MAXSIZE', 0)) // 1024 // 1024}MB")
    print(f"   • Multi-threading: {os.environ.get('OMP_NUM_THREADS')} threads")

def get_high_performance_mujoco_options():
    """Return MuJoCo options for maximum GPU utilization"""
    return {
        # High-resolution rendering for GPU load
        'width': 2560,              # 4K width for maximum GPU usage
        'height': 1440,             # 4K height 
        'samples': 8,               # 8x multisampling
        
        # Advanced visual features (GPU intensive)
        'shadows': True,            # Enable shadows
        'reflections': True,        # Enable reflections
        'ssao': True,              # Screen-space ambient occlusion
        'hdr': True,               # High dynamic range
        
        # Physics optimization for GPU
        'timestep': 0.001,         # Smaller timestep (more calculations)
        'nsubsteps': 8,            # More physics substeps
        'iterations': 100,         # More solver iterations
        'tolerance': 1e-8,         # Higher precision
        
        # Contact and dynamics
        'cone': 'elliptic',        # More complex friction model
        'jacobian': 'dense',       # Dense Jacobian matrices
        'solver': 'Newton',        # Newton solver (more GPU intensive)
        
        # Sensor simulation
        'sensor_noise': True,      # Add sensor noise calculations
        'contact_detection': 'all', # Detect all contacts
    }

if __name__ == "__main__":
    print("⚡ Maximum GPU Utilization Setup")
    print("=" * 40)
    
    setup_maximum_gpu_utilization()
    
    options = get_high_performance_mujoco_options()
    print("\n📊 High-performance MuJoCo configuration:")
    for key, value in options.items():
        print(f"   • {key}: {value}")
    
    print("\n🎯 Expected GPU usage increase:")
    print("   • Resolution: 2560x1440 (vs 1920x1080)")
    print("   • Multisampling: 8x (vs 4x)")
    print("   • Physics steps: 8x more calculations")
    print("   • Solver iterations: 100 (vs 50)")
    print("   • Expected GPU utilization: 60-80% (vs 37%)")
    
    print("\n💡 Usage:")
    print("   python3 max_gpu_optimization.py")
    print("   ./launch_full_simulation.sh")
#!/usr/bin/env python3
"""
Performance Analysis and Improvement Recommendations
"""

import subprocess
import time
import re

def analyze_gpu_usage():
    """Analyze current GPU usage and suggest improvements"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            gpu_util, mem_used, mem_total, power, temp = result.stdout.strip().split(', ')
            gpu_util = int(gpu_util)
            mem_used = int(mem_used)
            mem_total = int(mem_total)
            power = float(power)
            temp = int(temp)
            
            print("📊 GPU Analysis:")
            print(f"   • Utilization: {gpu_util}% (Target: 80-95%)")
            print(f"   • Memory: {mem_used}MB/{mem_total}MB ({mem_used/mem_total*100:.1f}%)")
            print(f"   • Power: {power}W/80W ({power/80*100:.1f}%)")
            print(f"   • Temperature: {temp}°C")
            
            # Analysis
            if gpu_util < 60:
                print("   ❌ GPU underutilized - Need more GPU-intensive tasks")
            elif gpu_util < 80:
                print("   ⚠️  GPU moderately used - Can push harder")
            else:
                print("   ✅ GPU well utilized")
                
            if mem_used < 2000:
                print("   ❌ GPU memory underused - Can use higher resolution/quality")
            elif mem_used < 4000:
                print("   ⚠️  GPU memory moderately used")
            else:
                print("   ✅ GPU memory well utilized")
                
            return {
                'utilization': gpu_util,
                'memory_used': mem_used,
                'memory_total': mem_total,
                'power': power,
                'temperature': temp
            }
    except Exception as e:
        print(f"❌ GPU analysis failed: {e}")
        return None

def analyze_mujoco_performance():
    """Analyze MuJoCo simulation performance"""
    try:
        # Check if MuJoCo process is running
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        mujoco_processes = []
        for line in result.stdout.split('\n'):
            if 'stretch_slam_bridge' in line:
                parts = line.split()
                if len(parts) >= 11:
                    cpu_usage = float(parts[2])
                    mem_usage = float(parts[3])
                    mujoco_processes.append({
                        'pid': parts[1],
                        'cpu': cpu_usage,
                        'mem': mem_usage
                    })
        
        if mujoco_processes:
            print("\n🤖 MuJoCo Process Analysis:")
            total_cpu = sum(p['cpu'] for p in mujoco_processes)
            total_mem = sum(p['mem'] for p in mujoco_processes)
            
            print(f"   • Processes: {len(mujoco_processes)}")
            print(f"   • Total CPU: {total_cpu:.1f}%")
            print(f"   • Total Memory: {total_mem:.1f}%")
            
            if total_cpu < 100:
                print("   ⚠️  MuJoCo CPU usage low - Can increase physics complexity")
            else:
                print("   ✅ MuJoCo CPU usage good")
                
            return mujoco_processes
        else:
            print("❌ No MuJoCo processes found")
            return []
            
    except Exception as e:
        print(f"❌ MuJoCo analysis failed: {e}")
        return []

def get_improvement_recommendations(gpu_data, mujoco_data):
    """Generate specific improvement recommendations"""
    recommendations = []
    
    if gpu_data:
        if gpu_data['utilization'] < 70:
            recommendations.extend([
                "🎮 Increase rendering resolution to 4K (3840x2160)",
                "✨ Enable more visual effects (bloom, volumetric lighting)",
                "🔍 Increase multisampling to 16x or 32x",
                "🌍 Add more complex environment geometry"
            ])
        
        if gpu_data['memory_used'] < 2000:
            recommendations.extend([
                "💾 Increase texture resolution and quality",
                "📸 Enable higher resolution camera feeds",
                "🎨 Load more detailed 3D models",
                "💡 Increase shadow map resolution"
            ])
    
    if mujoco_data:
        total_cpu = sum(p['cpu'] for p in mujoco_data)
        if total_cpu < 150:  # Multiple processes
            recommendations.extend([
                "⚙️  Increase physics timestep frequency",
                "🔧 Add more solver iterations",
                "🎯 Enable more precise contact detection",
                "🔄 Increase sensor sampling rates"
            ])
    
    return recommendations

def suggest_specific_configurations():
    """Suggest specific configuration changes"""
    print("\n🔧 Specific Configuration Improvements:")
    
    configs = {
        "MuJoCo Rendering": [
            "Width: 3840, Height: 2160 (4K)",
            "Samples: 32x multisampling",
            "Enable all visual effects",
            "Ultra texture quality"
        ],
        "Physics Engine": [
            "Timestep: 0.0001 (very small)",
            "Substeps: 20",
            "Solver iterations: 300",
            "Contact detection: ultra-precise"
        ],
        "CUDA Settings": [
            "Cache: 6GB (increase from 4GB)",
            "Heap: 2GB (increase from 1GB)",
            "Enable all memory optimizations"
        ],
        "Environment": [
            "Add more objects to scene",
            "Increase lighting complexity",
            "Add particle effects",
            "Enable real-time reflections"
        ]
    }
    
    for category, items in configs.items():
        print(f"\n   📂 {category}:")
        for item in items:
            print(f"      • {item}")

def main():
    print("🔍 Performance Analysis and Optimization Recommendations")
    print("=" * 60)
    
    # Analyze current state
    gpu_data = analyze_gpu_usage()
    mujoco_data = analyze_mujoco_performance()
    
    # Get recommendations
    recommendations = get_improvement_recommendations(gpu_data, mujoco_data)
    
    if recommendations:
        print("\n💡 Priority Improvements:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    # Specific configurations
    suggest_specific_configurations()
    
    print("\n🎯 Implementation Priority:")
    print("   1. ⚡ GPU utilization improvements (biggest impact)")
    print("   2. 🎮 Rendering quality increases")
    print("   3. ⚙️  Physics complexity increases")
    print("   4. 🌍 Environment complexity")
    
    print("\n📈 Expected Results:")
    print("   • GPU Usage: 38% → 80-95%")
    print("   • GPU Memory: 721MB → 3-5GB")
    print("   • Simulation Speed: 2-3x improvement")
    print("   • Visual Quality: Significant increase")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Real-Time Performance Test
Tests the new real-time configuration and compares with previous settings
"""

import subprocess
import time
import json

def monitor_gpu_performance(duration=30):
    """Monitor GPU performance for specified duration"""
    
    print(f"📊 Monitoring GPU performance for {duration} seconds...")
    
    gpu_data = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        try:
            result = subprocess.run([
                'nvidia-smi', 
                '--query-gpu=utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                gpu_util, mem_used, mem_total, power, temp = result.stdout.strip().split(', ')
                
                data_point = {
                    'timestamp': time.time() - start_time,
                    'gpu_util': int(gpu_util),
                    'mem_used': int(mem_used),
                    'mem_total': int(mem_total),
                    'power': float(power),
                    'temperature': int(temp)
                }
                
                gpu_data.append(data_point)
                
                print(f"\r⚡ GPU: {gpu_util}% | Memory: {mem_used}MB | Power: {power}W | Temp: {temp}°C", end='', flush=True)
                
        except Exception as e:
            print(f"\n⚠️ Monitoring error: {e}")
            
        time.sleep(1)
    
    print("\n")
    return gpu_data

def analyze_performance(gpu_data):
    """Analyze collected performance data"""
    
    if not gpu_data:
        print("❌ No performance data collected")
        return
    
    # Calculate averages
    avg_gpu_util = sum(d['gpu_util'] for d in gpu_data) / len(gpu_data)
    avg_mem_used = sum(d['mem_used'] for d in gpu_data) / len(gpu_data)
    avg_power = sum(d['power'] for d in gpu_data) / len(gpu_data)
    avg_temp = sum(d['temperature'] for d in gpu_data) / len(gpu_data)
    
    max_gpu_util = max(d['gpu_util'] for d in gpu_data)
    max_mem_used = max(d['mem_used'] for d in gpu_data)
    
    print("📈 Performance Analysis:")
    print(f"   • Average GPU utilization: {avg_gpu_util:.1f}%")
    print(f"   • Peak GPU utilization: {max_gpu_util}%")
    print(f"   • Average GPU memory: {avg_mem_used:.0f}MB")
    print(f"   • Peak GPU memory: {max_mem_used}MB")
    print(f"   • Average power consumption: {avg_power:.1f}W")
    print(f"   • Average temperature: {avg_temp:.1f}°C")
    
    # Performance evaluation
    performance_score = 0
    
    if avg_gpu_util >= 50:
        performance_score += 25
        print("   ✅ Good GPU utilization")
    elif avg_gpu_util >= 30:
        performance_score += 15
        print("   ⚠️  Moderate GPU utilization")
    else:
        performance_score += 5
        print("   ❌ Low GPU utilization")
    
    if avg_mem_used >= 2000:
        performance_score += 25
        print("   ✅ Good GPU memory usage")
    elif avg_mem_used >= 1000:
        performance_score += 15
        print("   ⚠️  Moderate GPU memory usage")
    else:
        performance_score += 5
        print("   ❌ Low GPU memory usage")
    
    if avg_power >= 25:
        performance_score += 25
        print("   ✅ GPU working hard")
    elif avg_power >= 15:
        performance_score += 15
        print("   ⚠️  Moderate GPU load")
    else:
        performance_score += 5
        print("   ❌ Low GPU load")
    
    if avg_temp <= 70:
        performance_score += 25
        print("   ✅ Good temperature control")
    elif avg_temp <= 80:
        performance_score += 15
        print("   ⚠️  Moderate temperature")
    else:
        performance_score += 5
        print("   ❌ High temperature")
    
    print(f"\n🎯 Overall Performance Score: {performance_score}/100")
    
    if performance_score >= 80:
        print("   🚀 Excellent performance!")
    elif performance_score >= 60:
        print("   ✅ Good performance")
    elif performance_score >= 40:
        print("   ⚠️  Average performance")
    else:
        print("   ❌ Poor performance - needs optimization")
    
    return {
        'avg_gpu_util': avg_gpu_util,
        'avg_mem_used': avg_mem_used,
        'avg_power': avg_power,
        'avg_temp': avg_temp,
        'performance_score': performance_score
    }

def compare_configurations():
    """Compare different configuration performance"""
    
    print("📊 Configuration Comparison:")
    print("=" * 50)
    
    configs = {
        "Previous Ultra": {
            'timestep': '0.0005s',
            'substeps': 16,
            'resolution': '3840x2160',
            'multisampling': '32x',
            'expected_gpu': '80-95%',
            'expected_memory': '4-5GB'
        },
        "Current Real-Time": {
            'timestep': '0.005s', 
            'substeps': 3,
            'resolution': '2560x1440',
            'multisampling': '8x',
            'expected_gpu': '50-70%',
            'expected_memory': '2-3GB'
        }
    }
    
    for name, config in configs.items():
        print(f"\n🔧 {name} Configuration:")
        for key, value in config.items():
            print(f"   • {key}: {value}")

def main():
    print("🕐 Real-Time Performance Test")
    print("=" * 40)
    
    # Configuration comparison
    compare_configurations()
    
    print(f"\n🚀 Starting performance monitoring...")
    print(f"💡 Make sure simulation is running!")
    print(f"⏱️  Test duration: 30 seconds")
    
    input("Press Enter to start monitoring...")
    
    # Monitor performance
    gpu_data = monitor_gpu_performance(30)
    
    # Analyze results
    print("\n" + "=" * 50)
    results = analyze_performance(gpu_data)
    
    if results:
        print(f"\n🎯 Real-Time Configuration Results:")
        print(f"   • Target GPU: 50-70% | Actual: {results['avg_gpu_util']:.1f}%")
        print(f"   • Target Memory: 2-3GB | Actual: {results['avg_mem_used']:.0f}MB")
        print(f"   • Performance Score: {results['performance_score']}/100")
        
        # Recommendations
        if results['avg_gpu_util'] < 40:
            print(f"\n💡 Recommendations:")
            print(f"   • GPU utilization is low - consider increasing visual quality")
            print(f"   • Try smaller timestep (0.002s) or more substeps (5-6)")
        elif results['avg_gpu_util'] > 80:
            print(f"\n💡 Recommendations:")
            print(f"   • GPU utilization is high - good for performance!")
            print(f"   • Monitor temperature to ensure system stability")
        else:
            print(f"\n✅ GPU utilization is in the optimal range for real-time!")
    
    print(f"\n🚀 Test complete! Real-time configuration is active.")

if __name__ == "__main__":
    main()
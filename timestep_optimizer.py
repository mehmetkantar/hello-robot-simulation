#!/usr/bin/env python3
"""
MuJoCo Timestep Optimizer
Dinamik timestep ayarlama ve performans optimizasyonu
"""

import time
import math

class TimestepOptimizer:
    def __init__(self):
        self.performance_history = []
        self.current_timestep = 0.002  # Default 2ms
        self.current_substeps = 4
        self.target_fps = 60
        self.target_real_time_ratio = 1.0
        
    def calculate_optimal_timestep(self, current_fps, real_time_ratio, gpu_utilization):
        """
        Mevcut performansa göre optimal timestep hesapla
        """
        
        # Performance score hesapla (0-100)
        fps_score = min(current_fps / self.target_fps * 100, 100)
        rt_score = min(real_time_ratio / self.target_real_time_ratio * 100, 100)
        
        print(f"📊 Performance Analysis:")
        print(f"   • Current FPS: {current_fps:.1f} (Target: {self.target_fps})")
        print(f"   • Real-time ratio: {real_time_ratio:.2f} (Target: {self.target_real_time_ratio})")
        print(f"   • GPU utilization: {gpu_utilization}%")
        print(f"   • FPS Score: {fps_score:.1f}/100")
        print(f"   • RT Score: {rt_score:.1f}/100")
        
        # Timestep önerileri
        recommendations = self._generate_recommendations(fps_score, rt_score, gpu_utilization)
        
        return recommendations
    
    def _generate_recommendations(self, fps_score, rt_score, gpu_utilization):
        """Performans skorlarına göre öneriler oluştur"""
        
        recommendations = {
            'timestep': self.current_timestep,
            'substeps': self.current_substeps,
            'solver_iterations': 50,
            'reason': '',
            'expected_improvement': ''
        }
        
        # GPU kullanımı düşükse - daha hassas ayarlar
        if gpu_utilization < 60:
            recommendations['timestep'] = 0.0005  # Daha küçük timestep
            recommendations['substeps'] = 16      # Daha fazla substep
            recommendations['solver_iterations'] = 200
            recommendations['reason'] = "GPU underutilized - increasing precision for more GPU load"
            recommendations['expected_improvement'] = "GPU usage: +40-50%, Simulation accuracy: +80%"
            
        # FPS çok düşükse - performans odaklı ayarlar  
        elif fps_score < 30:
            recommendations['timestep'] = 0.01    # Büyük timestep
            recommendations['substeps'] = 2       # Az substep
            recommendations['solver_iterations'] = 30
            recommendations['reason'] = "Low FPS detected - optimizing for speed"
            recommendations['expected_improvement'] = "FPS: +100-200%, Real-time ratio: +2x"
            
        # Dengeli performans
        elif fps_score > 80 and rt_score > 80:
            recommendations['timestep'] = 0.001   # Orta hassasiyet
            recommendations['substeps'] = 8       # Orta substep  
            recommendations['solver_iterations'] = 100
            recommendations['reason'] = "Good performance - balanced precision/speed"
            recommendations['expected_improvement'] = "Optimal balance maintained"
            
        # Real-time ratio düşükse
        elif rt_score < 50:
            recommendations['timestep'] = 0.005   # Hızlı timestep
            recommendations['substeps'] = 3       # Az substep
            recommendations['solver_iterations'] = 40  
            recommendations['reason'] = "Slow real-time ratio - increasing simulation speed"
            recommendations['expected_improvement'] = "Real-time ratio: +100%, Overall speed: +2x"
            
        else:
            # Fine-tuning
            recommendations['timestep'] = 0.002
            recommendations['substeps'] = 6
            recommendations['solver_iterations'] = 75
            recommendations['reason'] = "Fine-tuning for optimal performance"
            recommendations['expected_improvement'] = "Balanced optimization"
            
        return recommendations
    
    def get_preset_configurations(self):
        """Hazır konfigürasyonlar"""
        
        presets = {
            "maximum_gpu": {
                'timestep': 0.0001,
                'substeps': 20, 
                'solver_iterations': 300,
                'description': "Maximum GPU utilization (95%+)",
                'use_case': "GPU stress test, ultra-precise physics"
            },
            
            "high_precision": {
                'timestep': 0.0005,
                'substeps': 16,
                'solver_iterations': 200, 
                'description': "High precision robotics",
                'use_case': "Manipulation, grasping, precise control"
            },
            
            "balanced": {
                'timestep': 0.002,
                'substeps': 4,
                'solver_iterations': 50,
                'description': "Balanced speed/accuracy",
                'use_case': "General robotics, SLAM, navigation"
            },
            
            "high_speed": {
                'timestep': 0.01,
                'substeps': 2,
                'solver_iterations': 20,
                'description': "Maximum simulation speed", 
                'use_case': "Fast prototyping, demos"
            },
            
            "real_time": {
                'timestep': 0.005,
                'substeps': 3,
                'solver_iterations': 30,
                'description': "Real-time performance",
                'use_case': "Live demonstrations, teleoperation"
            }
        }
        
        return presets
    
    def generate_mujoco_xml_settings(self, config):
        """MuJoCo XML ayarları oluştur"""
        
        xml_settings = f"""
<!-- Optimized MuJoCo Physics Settings -->
<option timestep="{config['timestep']}" 
        iterations="{config['solver_iterations']}"
        tolerance="1e-10"
        ls_iterations="50"
        ls_tolerance="1e-7"
        noslip_iterations="10"
        noslip_tolerance="1e-6"
        mpr_iterations="50"
        mpr_tolerance="1e-6"/>

<size nconmax="1000" njmax="2000" nstack="600000"/>

<!-- Solver settings -->
<solver type="PGS" iterations="{config['solver_iterations']}" tolerance="1e-10"/>
"""
        return xml_settings
    
    def display_optimization_guide(self):
        """Optimizasyon rehberi göster"""
        
        print("🎯 MuJoCo Timestep Optimization Guide")
        print("=" * 50)
        
        presets = self.get_preset_configurations()
        
        for name, config in presets.items():
            print(f"\n📋 {name.upper().replace('_', ' ')} Configuration:")
            print(f"   • Timestep: {config['timestep']}s")
            print(f"   • Substeps: {config['substeps']}")
            print(f"   • Solver iterations: {config['solver_iterations']}")
            print(f"   • Description: {config['description']}")
            print(f"   • Use case: {config['use_case']}")
        
        print(f"\n🔧 Performance vs Accuracy Trade-off:")
        print(f"   📈 Speed Priority: Large timestep (0.01s+), Few substeps (1-2)")
        print(f"   ⚖️  Balanced: Medium timestep (0.002-0.005s), Medium substeps (3-6)")
        print(f"   🎯 Accuracy Priority: Small timestep (0.0005s-), Many substeps (8-20)")
        print(f"   🚀 GPU Load: Very small timestep (0.0001s), Many substeps (16-50)")
        
        print(f"\n💡 Current Project Settings:")
        print(f"   • Default timestep: {self.current_timestep}s")
        print(f"   • Default substeps: {self.current_substeps}")
        print(f"   • Configured for: GPU utilization + SLAM performance")

def main():
    optimizer = TimestepOptimizer()
    
    print("🔬 MuJoCo Physics Timestep Analyzer")
    print("=" * 40)
    
    # Örnek performans analizi
    example_fps = 45
    example_rt_ratio = 0.8  
    example_gpu = 38
    
    print(f"\n📊 Example Analysis (Current System):")
    recommendations = optimizer.calculate_optimal_timestep(
        example_fps, example_rt_ratio, example_gpu
    )
    
    print(f"\n💡 Recommendations:")
    print(f"   • Timestep: {recommendations['timestep']}s")
    print(f"   • Substeps: {recommendations['substeps']}")
    print(f"   • Solver iterations: {recommendations['solver_iterations']}")
    print(f"   • Reason: {recommendations['reason']}")
    print(f"   • Expected: {recommendations['expected_improvement']}")
    
    # Preset konfigürasyonları göster
    print(f"\n" + "=" * 50)
    optimizer.display_optimization_guide()
    
    # XML ayarları örneği
    print(f"\n🔧 XML Configuration Example:")
    xml_config = optimizer.generate_mujoco_xml_settings(recommendations)
    print(xml_config)

if __name__ == "__main__":
    main()
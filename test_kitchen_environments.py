#!/usr/bin/env python3
"""
Test script to explore different RoboCasa kitchen environments
"""

import sys
import time
sys.path.append('/home/user/stretch_mujoco')

from stretch_mujoco import StretchMujocoSimulator
from stretch_mujoco.enums.stretch_cameras import StretchCameras
from stretch_mujoco.robocasa_gen import model_generation_wizard

def test_kitchen_environments():
    """Test different kitchen layouts and styles"""
    
    # Kitchen layouts
    layouts = {
        0: "One wall",
        1: "One wall w/ island", 
        2: "L-shaped",
        3: "L-shaped w/ island",
        4: "Galley",
        5: "U-shaped",
        6: "U-shaped w/ island",
        7: "G-shaped",
        8: "G-shaped (large)",
        9: "Wraparound"
    }
    
    # Kitchen styles  
    styles = {
        0: "Industrial",
        1: "Scandinavian",
        2: "Coastal", 
        3: "Modern_1",
        4: "Modern_2",
        5: "Traditional_1",
        6: "Traditional_2",
        7: "Farmhouse"
    }
    
    print("Available Kitchen Layouts:")
    for k, v in layouts.items():
        print(f"  {k}: {v}")
    
    print("\nAvailable Kitchen Styles:")
    for k, v in styles.items():
        print(f"  {k}: {v}")
    
    print("\nTesting RoboCasa Kitchen Environment Generation...")
    
    # Test a kitchen environment
    layout = 2  # L-shaped
    style = 1   # Scandinavian
    
    try:
        print(f"\nGenerating kitchen: {layouts[layout]} with {styles[style]} style...")
        
        model, xml, objects_info = model_generation_wizard(
            task="PnPCounterToCab",
            layout=layout,
            style=style,
            write_to_file=None
        )
        
        print(f"✓ Kitchen environment generated successfully!")
        print(f"  Objects in scene: {len(objects_info) if objects_info else 0}")
        
        # Test with simulator
        print("\nTesting with simulator...")
        cameras_to_use = [StretchCameras.cam_d405_rgb]
        sim = StretchMujocoSimulator(model=model, cameras_to_use=cameras_to_use)
        
        print("Starting simulation...")
        sim.start(headless=True)
        
        print("Homing robot...")
        sim.home()
        
        print("✓ Simulation test successful!")
        
        # Test for a few seconds
        time.sleep(3)
        
        sim.stop()
        print("✓ Kitchen environment test completed!")
        
    except Exception as e:
        print(f"✗ Error testing kitchen environment: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_kitchen_environments()
    if success:
        print("\n🏠 Kitchen environments are ready for SLAM!")
        print("You can now use ./launch_slam.sh with --layout and --style options")
    else:
        print("\n⚠️  Kitchen environment test failed")
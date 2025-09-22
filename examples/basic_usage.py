#!/usr/bin/env python3
"""
Basic usage example for Stretch Dual GUI Simulation

This example shows how to programmatically control the simulation
without the GUI interface.
"""

import sys
import os
import time

# Add stretch_mujoco to path if needed
sys.path.append('./stretch_mujoco')

try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.stretch_cameras import StretchCameras
    from stretch_mujoco.enums.actuators import Actuators
    print("✓ stretch_mujoco imported successfully")
except ImportError as e:
    print(f"✗ Error importing stretch_mujoco: {e}")
    print("Please ensure stretch_mujoco is properly installed")
    sys.exit(1)

def basic_simulation_example():
    """
    Basic example showing how to:
    1. Initialize simulation with cameras
    2. Move the robot
    3. Get camera data
    4. Print status
    """
    print("Starting basic simulation example...")
    
    # Initialize simulation with RGB cameras
    cameras_to_use = StretchCameras.rgb()
    sim = StretchMujocoSimulator(cameras_to_use=cameras_to_use)
    
    try:
        # Start simulation in headless mode (no GUI viewer)
        print("Starting simulation...")
        sim.start(headless=True)
        
        # Wait for simulation to stabilize
        time.sleep(2)
        
        # Move robot to home position
        print("Moving to home position...")
        sim.home()
        time.sleep(2)
        
        # Get and print status
        status = sim.pull_status()
        print(f"Robot status - Time: {status.time:.2f}s, FPS: {status.fps:.1f}")
        print(f"Base position: x={status.base.x:.3f}, y={status.base.y:.3f}, θ={status.base.theta:.3f}")
        
        # Try to get camera data
        print("Getting camera data...")
        camera_data = sim.pull_camera_data()
        if camera_data:
            all_cameras = camera_data.get_all(use_depth_color_map=False)
            print(f"Available cameras: {list(all_cameras.keys())}")
            
            for cam_name, img_data in all_cameras.items():
                if img_data is not None:
                    print(f"{cam_name}: {img_data.shape if hasattr(img_data, 'shape') else 'No shape info'}")
        else:
            print("No camera data available")
        
        # Move the base forward
        print("Moving base forward...")
        sim.set_base_velocity(0.1, 0.0)  # Forward motion
        time.sleep(3)
        
        # Stop base movement
        sim.set_base_velocity(0.0, 0.0)
        
        # Move arm up
        print("Moving arm up...")
        sim.move_by(Actuators.lift, 0.2)
        time.sleep(2)
        
        # Move to stow position
        print("Moving to stow position...")
        sim.stow()
        time.sleep(3)
        
        print("Example completed successfully!")
        
    except Exception as e:
        print(f"Error during simulation: {e}")
    finally:
        # Always stop simulation
        print("Stopping simulation...")
        sim.stop()

def camera_only_example():
    """
    Example focusing on camera functionality
    """
    print("Starting camera-only example...")
    
    # Initialize with just one camera for testing
    cameras_to_use = [StretchCameras.cam_d405_rgb]
    sim = StretchMujocoSimulator(cameras_to_use=cameras_to_use)
    
    try:
        sim.start(headless=True)
        time.sleep(2)
        
        # Test camera data retrieval
        for i in range(5):
            print(f"Camera test {i+1}/5...")
            camera_data = sim.pull_camera_data()
            
            if camera_data:
                specific_camera = camera_data.get_camera_data(StretchCameras.cam_d405_rgb)
                if specific_camera is not None:
                    print(f"  ✓ Got camera data: {specific_camera.shape}")
                else:
                    print(f"  ✗ No data from cam_d405_rgb")
            else:
                print(f"  ✗ No camera data available")
            
            time.sleep(1)
            
    except Exception as e:
        print(f"Camera example error: {e}")
    finally:
        sim.stop()

def performance_test():
    """
    Test simulation performance with different configurations
    """
    print("Starting performance test...")
    
    configs = [
        ("No cameras", []),
        ("One camera", [StretchCameras.cam_d405_rgb]),
        ("All RGB cameras", StretchCameras.rgb()),
    ]
    
    for config_name, cameras in configs:
        print(f"\nTesting: {config_name}")
        sim = StretchMujocoSimulator(cameras_to_use=cameras)
        
        try:
            start_time = time.time()
            sim.start(headless=True)
            
            # Run for 10 seconds and measure performance
            test_duration = 10
            status_checks = 0
            
            end_time = start_time + test_duration
            while time.time() < end_time:
                status = sim.pull_status()
                status_checks += 1
                time.sleep(0.1)
            
            actual_duration = time.time() - start_time
            avg_fps = status_checks / actual_duration
            
            final_status = sim.pull_status()
            sim_speed = final_status.sim_to_real_time_ratio_msg if hasattr(final_status, 'sim_to_real_time_ratio_msg') else "Unknown"
            
            print(f"  Results: {avg_fps:.1f} status checks/sec, sim speed: {sim_speed}")
            
        except Exception as e:
            print(f"  Error: {e}")
        finally:
            sim.stop()

if __name__ == "__main__":
    print("Stretch Dual GUI Simulation - Basic Examples")
    print("=" * 50)
    
    # Run examples
    try:
        basic_simulation_example()
        print("\n" + "=" * 50)
        camera_only_example()
        print("\n" + "=" * 50)
        performance_test()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print("\nExamples completed!")
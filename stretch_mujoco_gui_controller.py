#!/usr/bin/env python3
"""
Integrated MuJoCo + GUI Controller
Starts MuJoCo simulation and GUI controller with direct communication
"""

import sys
import os
import time
import threading
import argparse

# Add MuJoCo path
sys.path.append('/home/user/stretch_mujoco')

try:
    from stretch_mujoco import StretchMujocoSimulator
    from stretch_mujoco.enums.actuators import Actuators
    MUJOCO_AVAILABLE = True
    print("✅ MuJoCo available")
except ImportError as e:
    print(f"❌ MuJoCo not available: {e}")
    MUJOCO_AVAILABLE = False
    sys.exit(1)

# Fix Qt/OpenCV plugin conflicts
os.environ['QT_QPA_PLATFORM'] = 'xcb'
cv_qt_plugin_path = '/home/user/.local/lib/python3.10/site-packages/cv2/qt/plugins'
if cv_qt_plugin_path in os.environ.get('QT_PLUGIN_PATH', ''):
    qt_plugin_path = os.environ['QT_PLUGIN_PATH']
    paths = [p for p in qt_plugin_path.split(':') if cv_qt_plugin_path not in p]
    os.environ['QT_PLUGIN_PATH'] = ':'.join(paths)
else:
    os.environ.pop('QT_PLUGIN_PATH', None)

from PyQt5.QtWidgets import QApplication
import sys

# Import our modified controller
from stretch_robot_controller_simple import StretchRobotController

class MuJoCoGUIBridge:
    """Bridge between MuJoCo simulation and GUI controller"""
    
    def __init__(self, headless=False, environment="simple"):
        self.sim = None
        self.controller = None
        self.headless = headless
        self.environment = environment
        
    def start_simulation(self):
        """Start MuJoCo simulation"""
        print("🤖 Starting MuJoCo simulation...")
        try:
            # Configure environment
            if self.environment == "simple":
                print("🏠 Using simple environment")
                self.sim = StretchMujocoSimulator()
            else:
                print("🏢 Using complex environment")
                # Add complex environment setup if needed
                self.sim = StretchMujocoSimulator()
            
            # Start simulation
            self.sim.start(headless=self.headless)
            print("✅ MuJoCo simulation started")
            
            # Give simulation time to initialize
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start simulation: {e}")
            return False
    
    def start_gui(self):
        """Start GUI controller"""
        print("🖥️ Starting GUI controller...")
        try:
            app = QApplication(sys.argv)
            app.setStyle('Fusion')  # Modern look
            
            # Create controller
            self.controller = StretchRobotController()
            
            # Connect simulation to controller
            if self.sim:
                self.controller.sim = self.sim
                print("✅ MuJoCo simulation connected to GUI")
                
                # Update status to show connection
                self.controller.status_text.append("🟢 MuJoCo simulation connected")
                self.controller.status_text.append("🎮 Direct control enabled")
                self.controller.status_bar.showMessage("🟢 MuJoCo Direct Control Ready")
            else:
                print("⚠️ No simulation connected")
            
            self.controller.show()
            
            print("✅ GUI controller started")
            return app
            
        except Exception as e:
            print(f"❌ Failed to start GUI: {e}")
            return None
    
    def run(self):
        """Run the integrated system"""
        print("🚀 Starting integrated MuJoCo + GUI system...")
        
        # Start simulation
        if not self.start_simulation():
            print("❌ Failed to start simulation - exiting")
            return False
        
        # Start GUI
        app = self.start_gui()
        if not app:
            print("❌ Failed to start GUI - exiting")
            return False
        
        print("🎉 System ready!")
        print("🎮 Use GUI controls to move the robot")
        print("👀 Watch movements in MuJoCo window")
        
        # Run Qt application
        try:
            app.exec_()
        except KeyboardInterrupt:
            print("🛑 Interrupted by user")
        finally:
            self.cleanup()
            
        return True
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        
        if self.sim:
            try:
                self.sim.stop()
                print("✅ MuJoCo simulation stopped")
            except Exception as e:
                print(f"⚠️ Error stopping simulation: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Integrated MuJoCo + GUI Controller")
    parser.add_argument("--headless", action="store_true", 
                       help="Run MuJoCo in headless mode (no 3D viewer)")
    parser.add_argument("--environment", choices=["simple", "complex"], default="simple",
                       help="Environment to use (default: simple)")
    
    args = parser.parse_args()
    
    print("="*50)
    print("🤖 STRETCH MUJOCO + GUI CONTROLLER")
    print("="*50)
    print(f"Environment: {args.environment}")
    print(f"Headless mode: {args.headless}")
    print("="*50)
    
    # Create and run bridge
    bridge = MuJoCoGUIBridge(headless=args.headless, environment=args.environment)
    success = bridge.run()
    
    if success:
        print("✅ System completed successfully")
    else:
        print("❌ System failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
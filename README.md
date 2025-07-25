# Hello Robot Stretch Simulation with Web Teleop

A comprehensive simulation system for the Hello Robot Stretch with MuJoCo physics, ROS2 SLAM integration, and web-based teleoperation control.

## ✨ Features

- **🤖 Complete Robot Simulation**: Full Stretch robot simulation in MuJoCo with realistic physics
- **🌐 Web Teleoperation**: Browser-based control interface for base movement and manipulator control
- **🗺️ Real-time SLAM**: Integrated SLAM Toolbox for mapping and localization
- **📊 RViz Visualization**: Live visualization of robot state, sensor data, and generated maps
- **🏢 Multiple Environments**: Office, kitchen, and custom environments for testing
- **🦾 Full Robot Control**: Base movement, lift, arm extension, head pan/tilt, wrist, and gripper control

## 🚀 Quick Start

### Prerequisites

- Ubuntu 22.04 with ROS2 Humble
- Python 3.10+
- Hello Robot Stretch MuJoCo package
- Web browser for teleoperation interface

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mehmetkantar/hello-robot-simulation.git
   cd hello-robot-simulation
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Launch the complete system:**
   ```bash
   ./launch_full_simulation.sh --complex-office
   ```

4. **Open web controller:**
   - Navigate to `http://localhost:8081` in your web browser
   - Use the interface to control the robot

## 🎮 Usage

### Launch Options

```bash
# Default (complex office environment)
./launch_full_simulation.sh

# Different environments
./launch_full_simulation.sh --simple           # Simple environment
./launch_full_simulation.sh --kitchen          # Kitchen environment
./launch_full_simulation.sh --complex-office   # Complex office (default)

# Performance options
./launch_full_simulation.sh --headless         # No MuJoCo GUI (better performance)
./launch_full_simulation.sh --no-rviz          # No RViz visualization
./launch_full_simulation.sh --no-web           # No web controller

# Custom port
./launch_full_simulation.sh --port 8080        # Use different port
```

### Web Interface Controls

- **🚗 Base Movement**: Forward, backward, left, right, rotate
- **🏗️ Lift Control**: Vertical positioning (0-1.1m)
- **🦾 Arm Extension**: Arm reach control (0-0.52m)
- **👁️ Head Control**: Pan (-1.57 to 1.57 rad) and tilt (-0.52 to 0.52 rad)
- **⚙️ Speed Control**: Adjustable movement speed

## 🧪 Testing

```bash
# Test web controller connection to robot
python3 test_web_controller_connection.py

# Test direct MuJoCo control
python3 direct_robot_test.py

# Test ROS2 connectivity
python3 test_ros_connection.py
```

## 📦 Dependencies

See `requirements.txt` and run `./setup.sh` for automatic installation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

---

**🤖 Built with Claude Code - AI-assisted development for robotics**
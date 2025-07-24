# Hello Robot Simulation - Setup Instructions

## 🚀 Quick Start Guide

After cloning this repository, follow these steps to set up the simulation environment.

## 📋 Prerequisites

### 1. ROS2 Humble Installation
```bash
# Source ROS2 (add to ~/.bashrc for permanent setup)
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0
```

### 2. Stretch Dependencies
```bash
# Ensure stretch_mujoco is installed
python3 -c "import stretch_mujoco; print('✅ stretch_mujoco OK')"

# Check stretch_description is available
ls /home/user/ament_ws/install/stretch_description/share/stretch_description/urdf/
```

### 3. Python Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

## 🛠️ Setup Steps

### 1. Make Scripts Executable
```bash
chmod +x *.sh
chmod +x *.py
```

### 2. Test Basic Functionality
```bash
# Test ROS2 connectivity
ros2 topic list

# Test SLAM Toolbox availability  
ros2 pkg list | grep slam_toolbox
```

## 🎮 Usage Options

### Option 1: RViz-Only Mode (Recommended for Performance)
```bash
# Maximum performance - no MuJoCo GUI
./launch_rviz_only_simulation.sh --complex-office

# Features:
# - Headless MuJoCo (5-20x faster)
# - RViz visualization only
# - Web control: http://localhost:8081
# - Camera disable/enable toggle
```

### Option 2: RViz with Exact Robot Model  
```bash
# Shows proper Stretch robot appearance
./launch_rviz_stretch_model.sh --complex-office

# Features:
# - Detailed robot model in RViz
# - Color-coded robot parts
# - Proper joint visualization
```

### Option 3: Full Simulation with Performance Controls
```bash
# Traditional mode with camera controls
./launch_full_simulation_optimized.sh --complex-office

# Features:
# - MuJoCo GUI + RViz
# - Camera disable button for performance
# - Complete visualization
```

## 🔧 Environment Options

All launchers support these environments:

```bash
--simple           # Simple environment (fastest)
--kitchen          # Kitchen environment  
--complex-office   # Complex office (recommended for SLAM)
```

## 🌐 Web Control Interface

After launching any simulation:

1. **Open browser**: Go to http://localhost:8081
2. **Robot Control**: Use movement buttons
3. **Camera Toggle**: Disable cameras for performance boost
4. **Speed Control**: Adjust robot speed (0.5-25 m/s)

### Web Interface Features:
- **Base Movement**: Forward, backward, left, right, rotate
- **Arm Control**: Lift height, arm extension  
- **Head Control**: Pan and tilt
- **Camera Toggle**: Enable/disable for performance
- **Speed Slider**: Ultra-fast exploration mode

## 🚨 Troubleshooting

### Common Issues:

#### 1. "stretch_mujoco not found"
```bash
# Install stretch_mujoco following Hello Robot guide
# Ensure it's in Python path
```

#### 2. "ROS2 not sourced"
```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0
```

#### 3. "Permission denied" on scripts
```bash
chmod +x *.sh *.py
```

#### 4. Web controller not accessible
```bash
# Check if port 8081 is free
lsof -i :8081

# Kill existing processes if needed
pkill -f web_controller
```

#### 5. No robot model in RViz
```bash
# Check URDF files exist
ls /home/user/ament_ws/install/stretch_description/share/stretch_description/urdf/

# Use the exact model launcher
./launch_rviz_stretch_model.sh --complex-office
```

## ⚡ Performance Tips

### Maximum Speed Setup:
1. **Use RViz-only mode**: `./launch_rviz_only_simulation.sh`
2. **Disable cameras**: Use web interface toggle
3. **Simple environment**: Use `--simple` flag
4. **Close unnecessary apps**: Free up system resources

### Expected Performance:
- **RViz-only + cameras disabled**: 5-20x faster
- **Full GUI + cameras disabled**: 2-5x faster  
- **Original mode**: 1x baseline speed

## 📊 Feature Comparison

| Feature | RViz-Only | Exact Model | Full Simulation |
|---------|-----------|-------------|-----------------|
| Performance | 🚀🚀🚀🚀🚀 | 🚀🚀🚀🚀 | 🚀🚀🚀 |
| MuJoCo GUI | ❌ | ❌ | ✅ |
| RViz Display | ✅ | ✅ | ✅ |
| Robot Model | Basic | Detailed | Detailed |
| Camera Control | ✅ | ✅ | ✅ |
| Web Interface | ✅ | ✅ | ✅ |

## 🎯 Recommended Workflow

1. **Development**: Use `launch_rviz_stretch_model.sh` for proper robot visualization
2. **Performance Testing**: Use `launch_rviz_only_simulation.sh` for maximum speed
3. **Demonstrations**: Use `launch_full_simulation_optimized.sh` for complete view
4. **SLAM Mapping**: All modes work well, RViz-only is fastest

## 🔗 Additional Resources

- **SLAM Toolbox**: For advanced mapping configuration
- **RViz**: For visualization customization  
- **Hello Robot Docs**: For stretch_mujoco setup
- **GitHub Issues**: For bug reports and feature requests

Happy simulating! 🤖
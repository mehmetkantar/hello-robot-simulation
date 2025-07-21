# Stretch Robot SLAM Integration Guide

Complete guide for running SLAM with MuJoCo simulation, ROS2, and RViz visualization.

## Overview

This integration provides:
- **MuJoCo Simulation**: Realistic physics and sensor simulation
- **ROS2 Bridge**: Converts simulation data to ROS2 topics
- **SLAM Toolbox**: Real-time mapping and localization
- **RViz Visualization**: Live robot and map visualization
- **Camera Feeds**: Multiple camera views for visual SLAM

## Quick Start

### 1. Prerequisites

Ensure you have all required components:
```bash
# Source ROS2 
source /opt/ros/humble/setup.bash
source ~/stretch_ros2/install/setup.bash

# Install missing packages if needed
sudo apt install ros-humble-slam-toolbox ros-humble-rviz2 ros-humble-robot-state-publisher
```

### 2. Launch Complete SLAM System

```bash
cd /home/user/hello-robot-simulation
./launch_slam.sh
```

This will start:
- MuJoCo simulation with sensor data
- ROS2 bridge publishing topics
- SLAM Toolbox for mapping
- RViz for visualization

### 3. Control the Robot

In a new terminal:
```bash
# Install teleop if not available
sudo apt install ros-humble-teleop-twist-keyboard

# Control the robot
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### 4. Save Your Map

```bash
# Save the generated map
ros2 run nav2_map_server map_saver_cli -f my_slam_map
```

## System Components

### 1. SLAM Bridge (`stretch_slam_bridge_improved.py`)

**Purpose**: Converts MuJoCo simulation data to ROS2 topics

**Published Topics**:
- `/scan` - Laser scan data (LaserScan)
- `/odom` - Robot odometry (Odometry)
- `/joint_states` - Robot joint states (JointState)
- `/camera/d405/color/image_raw` - D405 camera feed
- `/camera/d435i/color/image_raw` - D435i camera feed
- `/camera/nav/color/image_raw` - Navigation camera feed

**Subscribed Topics**:
- `/cmd_vel` - Velocity commands (Twist)

**TF Frames**:
- `odom` → `base_link`
- `base_link` → `laser`
- `base_link` → `cam_*_frame`

### 2. SLAM Toolbox Configuration

**File**: `config/mapper_params_online_async.yaml`

**Key Settings**:
- Real-time mapping mode
- 5cm resolution
- Loop closure enabled
- Optimized for indoor environments

### 3. RViz Configuration

**File**: `rviz/stretch_slam.rviz`

**Displays**:
- Robot model visualization
- Laser scan data
- Generated map
- Odometry path
- Camera feeds
- TF tree

## Advanced Usage

### Running Individual Components

1. **SLAM Bridge Only**:
```bash
python3 stretch_slam_bridge_improved.py
```

2. **SLAM Toolbox Only**:
```bash
ros2 run slam_toolbox async_slam_toolbox_node \
    --ros-args --params-file config/mapper_params_online_async.yaml
```

3. **RViz Only**:
```bash
ros2 run rviz2 rviz2 -d rviz/stretch_slam.rviz
```

### Alternative Launch Options

```bash
# Launch without RViz
./launch_slam.sh --no-rviz

# Launch with debug output
./launch_slam.sh --debug

# Get help
./launch_slam.sh --help
```

### Integration with Existing GUI

You can run the SLAM system alongside your existing GUI:

**Terminal 1**: Run MuJoCo GUI
```bash
python3 stretch_dual_gui.py
```

**Terminal 2**: Run SLAM Bridge
```bash
python3 stretch_slam_bridge_improved.py
```

**Terminal 3**: Run RViz
```bash
ros2 run rviz2 rviz2 -d rviz/stretch_slam.rviz
```

## Environment Configuration

### Available Environments

The system simulates realistic indoor environments:
- **Kitchen environment**: Counters, appliances, furniture
- **Office environment**: Desks, chairs, walls
- **Custom environments**: Modify `simulate_environment_range()` in the bridge

### Lidar Simulation

The bridge provides realistic lidar data:
- **360-degree coverage**: Full rotation laser scanner
- **Realistic obstacles**: Walls, furniture, objects
- **Noise simulation**: Realistic sensor noise
- **Range limits**: 10cm to 10m range

## Troubleshooting

### Common Issues

1. **"ROS2 is not sourced"**:
   ```bash
   source /opt/ros/humble/setup.bash
   source ~/stretch_ros2/install/setup.bash
   ```

2. **"stretch_mujoco not found"**:
   ```bash
   cd /home/user/stretch_mujoco
   pip install -e .
   ```

3. **"SLAM bridge died unexpectedly"**:
   - Check if MuJoCo simulation is running
   - Verify stretch_mujoco installation
   - Check Python dependencies

4. **"No laser scan data"**:
   - Ensure bridge is publishing to `/scan`
   - Check TF tree is complete
   - Verify laser frame exists

5. **"Map not updating"**:
   - Drive the robot around to collect data
   - Check SLAM Toolbox parameters
   - Verify odometry is publishing

### Debug Commands

```bash
# Check active topics
ros2 topic list

# Monitor laser scan
ros2 topic echo /scan

# Check TF tree
ros2 run tf2_tools view_frames

# Monitor SLAM status
ros2 topic echo /slam_toolbox/feedback

# Check node status
ros2 node list
```

## Performance Optimization

### For Better SLAM Performance

1. **Increase lidar resolution**:
   ```python
   # In stretch_slam_bridge_improved.py
   self.lidar_angle_increment = math.pi / 360.0  # 0.5 degree resolution
   ```

2. **Tune SLAM parameters**:
   ```yaml
   # In config/mapper_params_online_async.yaml
   resolution: 0.02  # Higher resolution (2cm)
   minimum_travel_distance: 0.1  # More frequent updates
   ```

3. **Optimize camera feeds**:
   ```python
   # Reduce camera update rate
   self.camera_timer = self.create_timer(0.5, self.publish_camera_feeds)  # 2Hz
   ```

### For Better Simulation Performance

1. **Disable cameras**:
   ```python
   # In start_simulation()
   cameras_to_use = []  # No cameras
   ```

2. **Reduce update rates**:
   ```python
   # Lower frequency timers
   self.laser_timer = self.create_timer(0.2, self.publish_laser_scan)  # 5Hz
   ```

## Integration with Navigation

### Add Nav2 for Autonomous Navigation

1. **Install Nav2**:
   ```bash
   sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
   ```

2. **Launch Nav2 with SLAM**:
   ```bash
   ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true
   ```

3. **Set navigation goals in RViz**:
   - Use "2D Nav Goal" tool
   - Click and drag to set destination

## API Reference

### SLAM Bridge Node

**Node Name**: `stretch_slam_bridge_improved`

**Parameters**:
- `use_sim_time` (bool): Use simulation time
- `lidar_range_max` (float): Maximum lidar range
- `lidar_range_min` (float): Minimum lidar range

**Services**:
- Standard ROS2 node services

**Actions**:
- None (publishes data continuously)

### Custom Environment Creation

To create custom environments, modify the `simulate_environment_range()` function:

```python
def simulate_environment_range(self, angle, robot_x, robot_y, robot_theta):
    # Add your custom obstacles here
    obstacles = [
        {'x': 1.0, 'y': 2.0, 'radius': 0.5},  # Custom obstacle
        # Add more obstacles...
    ]
    
    # Your environment logic here
    return calculated_range
```

## Support

For issues related to:
- **SLAM Bridge**: Check this repository's issues
- **SLAM Toolbox**: Check slam_toolbox documentation
- **stretch_mujoco**: Check Hello Robot documentation
- **ROS2 Integration**: Check ROS2 documentation

---

## Next Steps

1. **Test basic SLAM**: Run the system and drive around
2. **Save maps**: Create maps of different environments
3. **Add navigation**: Integrate with Nav2 for autonomous navigation
4. **Visual SLAM**: Experiment with camera-based SLAM
5. **Multi-robot SLAM**: Scale to multiple robots

**Happy SLAMming!** 🤖📍
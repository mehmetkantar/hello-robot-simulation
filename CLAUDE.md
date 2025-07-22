# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Hello Robot Stretch simulation system that integrates MuJoCo physics simulation with ROS2 SLAM capabilities and GUI control interfaces. The system provides realistic robot simulation with multiple complex environments for testing navigation, manipulation, and SLAM algorithms.

## Core Architecture

### Main Components

1. **GUI Controllers** - Interactive control interfaces
   - `stretch_dual_gui.py` - Main GUI with camera feeds and controls
   - `stretch_robot_controller.py` - Simple robot controller
   - `stretch_terminal_controller.py` - Terminal-based control

2. **ROS2 SLAM Bridge** - Simulation to ROS2 data pipeline
   - `stretch_slam_bridge_improved.py` - Enhanced bridge with real lidar integration
   - `stretch_slam_bridge.py` - Basic ROS2 bridge
   - Publishes: `/scan`, `/odom`, `/joint_states`, camera topics
   - Subscribes: `/cmd_vel`

3. **Integrated System** - Combined MuJoCo + ROS2 + GUI
   - `stretch_integrated_controller.py` - Unified system controller

4. **Environment Simulation**
   - Kitchen environments with RoboCasa integration
   - Complex office environments
   - Multiple world files in `worlds/` directory

### Data Flow

```
MuJoCo Simulation → SLAM Bridge → ROS2 Topics → SLAM Toolbox → Map
                 ↗               ↘
              GUI Control      Camera Feeds → RViz Visualization
```

## Development Commands

### Starting the System

**Quick Start (Complete SLAM System):**
```bash
./launch_slam.sh --complex-office  # Recommended environment
```

**Environment Options:**
```bash
./launch_slam.sh --simple                    # Simple environment
./launch_slam.sh --kitchen-world            # Kitchen with appliances  
./launch_slam.sh --layout 2 --style 1       # Custom kitchen (L-shaped, Scandinavian)
```

**GUI Only:**
```bash
./run_simulation.sh normal    # With cameras
./run_simulation.sh fast      # Performance mode
python3 stretch_dual_gui.py   # Direct launch
```

### Testing

**Run specific test suites:**
```bash
python3 test_integrated_system.py     # Full system test
python3 test_controller.py            # Basic controller test
python3 test_kitchen_environments.py  # Environment testing
python3 test_gui_integration.py       # GUI functionality
```

**Manual testing:**
```bash
python3 test_direct_mujoco.py         # Direct MuJoCo control
python3 test_arm_control.py           # Arm movement testing
```

### ROS2 Integration

**Prerequisites:**
```bash
source /opt/ros/humble/setup.bash
source ~/stretch_ros2/install/setup.bash
```

**Control robot via ROS2:**
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Monitor topics:**
```bash
ros2 topic list
ros2 topic echo /scan
ros2 topic echo /odom
```

**Save SLAM map:**
```bash
ros2 run nav2_map_server map_saver_cli -f my_slam_map
```

## Key Dependencies

- **stretch_mujoco**: Hello Robot's MuJoCo integration (install separately)
- **ROS2 Humble**: For SLAM and navigation
- **Python packages**: Listed in `requirements.txt` (tkinter, PIL, opencv-python, numpy)

## File Structure

### Launch Scripts
- `launch_slam.sh` - Complete SLAM system with environment options
- `run_simulation.sh` - GUI simulation launcher with modes
- `launch_integrated_system.sh` - Unified system launcher

### Configuration
- `config/mapper_params_online_async.yaml` - SLAM Toolbox parameters
- `rviz/stretch_slam.rviz` - RViz visualization config
- `worlds/*.xml` - MuJoCo environment definitions

### Controllers by Use Case
- **Research/SLAM**: Use `stretch_slam_bridge_improved.py` with `launch_slam.sh`
- **GUI Development**: Use `stretch_dual_gui.py` or `run_simulation.sh`
- **ROS2 Integration**: Use `stretch_integrated_controller.py`
- **Testing**: Use appropriate `test_*.py` files

## Environment Details

### Kitchen Environments (RoboCasa)
- 10 different layouts (0-9): One wall, L-shaped, Galley, U-shaped, etc.
- 12 different styles (0-11): Industrial, Scandinavian, Coastal, Modern, etc.
- Realistic appliances and obstacles for navigation testing

### Office Environments
- Complex office with desks, chairs, walls
- Realistic lidar simulation with proper obstacle detection

## Common Workflows

### Setting up SLAM
1. Source ROS2 environment
2. Launch with: `./launch_slam.sh --complex-office`
3. Drive robot using teleop or GUI controls
4. Monitor map building in RViz
5. Save map when satisfied

### GUI Development
1. Launch GUI: `python3 stretch_dual_gui.py`
2. Configure camera/performance options
3. Test controls and monitor status
4. Use Fast Mode for development (disables cameras)

### Testing Changes
1. Run relevant test file: `python3 test_*.py`
2. Check console output for errors
3. Verify robot behavior in simulation
4. Test SLAM integration if applicable

## Troubleshooting

### Common Issues
- **"stretch_mujoco not found"**: Install following Hello Robot guide
- **"ROS2 not sourced"**: Run setup commands above
- **Slow performance**: Enable Fast Mode or reduce camera FPS
- **SLAM not working**: Check topics with `ros2 topic list`

### Debug Commands
```bash
./launch_slam.sh --debug           # Enable debug output
ros2 node list                     # Check running nodes
ros2 run tf2_tools view_frames     # Inspect TF tree
```

## Performance Notes

- Enable Fast Mode in GUI for maximum simulation speed
- Complex environments may require more processing power
- Camera feeds can be disabled for better performance
- SLAM works best with the complex office environment
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete simulation environment for the Hello Robot Stretch 3 mobile manipulator using Gazebo physics simulation and MoveIt2 motion planning in ROS2 Humble. The project integrates the official Hello Robot ROS2 packages with custom Gazebo and MoveIt configurations.

## Build Commands

```bash
# Setup environment
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash

# Build workspace
colcon build --symlink-install

# Source the workspace
source install/setup.bash

# Validate setup
cd src/stretch_moveit_config
python3 test_setup.py
```

## Run Commands

### Quick Start
```bash
# One-click launch (recommended)
cd /home/kantar/Desktop/hello-robot
./start_stretch_simulation.sh

# Or step-by-step
./check_system.sh          # Check prerequisites
./install_dependencies.sh  # Install deps
./build_workspace.sh       # Build workspace
./run_simulation.sh        # Launch simulation
```

### Individual Launch Options
```bash
# Complete simulation (Gazebo + MoveIt + RViz)
ros2 launch stretch_moveit_config stretch_gazebo_moveit.launch.py

# Gazebo simulation only
ros2 launch stretch_moveit_config stretch_gazebo.launch.py

# MoveIt only (no simulation)
ros2 launch stretch_moveit_config stretch_moveit.launch.py
```

### Testing
```bash
# Validate complete setup
cd stretch_ws/src/stretch_moveit_config
python3 test_setup.py

# Test individual components
ros2 node list
ros2 topic list
ros2 control list_controllers
```

## Architecture

### Workspace Structure
- `stretch_ws/` - ROS2 workspace root
- `stretch_ws/src/stretch_ros2/` - Official Hello Robot packages
- `stretch_ws/src/stretch_moveit_config/` - Custom MoveIt configuration
- `stretch_urdf/` - URDF generation tools (separate from ROS workspace)

### Key Packages
- **stretch_core** - Hardware drivers and robot control
- **stretch_description** - Robot URDF models and meshes
- **stretch_moveit_config** - MoveIt motion planning configuration
- **stretch_simulation** - Alternative MuJoCo simulation
- **stretch_demos** - Example autonomous behaviors
- **hello_helpers** - Shared utilities across packages

### Robot Configuration
The Stretch 3 has these main components:
- **Mobile base** - Differential drive with 2 wheels
- **Lift** - Vertical prismatic joint (0-1.1m range)
- **Arm** - 4-segment telescoping arm (joint_arm_l0-l3)
- **Wrist** - 3-DOF wrist (yaw, pitch, roll)
- **Gripper** - 2-finger gripper or tool mount
- **Head** - 2-DOF camera mount (pan, tilt)
- **Sensors** - RPLidar, RealSense cameras, IMU

### MoveIt Planning Groups
- `manipulator` - Complete arm system (lift + arm + wrist)
- `arm` - Telescoping arm segments only
- `wrist` - Wrist joints (yaw, pitch, roll)
- `gripper` - Gripper finger control
- `head` - Head pan and tilt
- `mobile_base` - Wheel drive system

## Important Files

### Configuration Files
- `stretch_ws/src/stretch_moveit_config/config/stretch.srdf` - Robot semantic description
- `stretch_ws/src/stretch_moveit_config/config/joint_limits.yaml` - Motion limits
- `stretch_ws/src/stretch_moveit_config/config/kinematics.yaml` - IK solvers
- `stretch_ws/src/stretch_moveit_config/config/ompl_planning.yaml` - Motion planners
- `stretch_ws/src/stretch_moveit_config/config/moveit_controllers.yaml` - Controller interface

### Launch Files
- `stretch_ws/src/stretch_moveit_config/launch/stretch_gazebo_moveit.launch.py` - Main simulation launch
- `stretch_ws/src/stretch_moveit_config/launch/stretch_gazebo.launch.py` - Gazebo only
- `stretch_ws/src/stretch_moveit_config/launch/stretch_moveit.launch.py` - MoveIt only

### Robot Description
- `stretch_ws/src/stretch_ros2/stretch_description/urdf/stretch_gazebo.urdf.xacro` - Gazebo URDF
- `stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_*.urdf` - Robot variants

## Development Notes

### Dependencies
- Ubuntu 22.04 LTS
- ROS2 Humble Desktop
- MoveIt2 packages
- Gazebo Classic
- Python 3.10+

### Robot Variants
The project supports multiple Stretch configurations:
- SE3 - Stretch 3 base model
- RE1V0/RE2V0 - Previous generations
- Different tool configurations (gripper, dex wrist, tablet)

### Simulation vs Hardware
This codebase is primarily for simulation. For hardware operation, the stretch_core drivers interface with the actual robot hardware through the stretch_body Python API.

### Common Issues
- Ensure 16GB+ RAM for smooth Gazebo operation
- MoveIt planning may fail with unreachable goals - try smaller motions
- Controllers need proper Gazebo ros2_control plugin loading
- URDF files must be present in stretch_description package

## Python API Usage

The robot can be controlled programmatically using MoveIt's Python API:

```python
from moveit_commander import MoveGroupCommander, RobotCommander

# Initialize
robot = RobotCommander()
manipulator = MoveGroupCommander("manipulator")
gripper = MoveGroupCommander("gripper")

# Move to named poses
manipulator.set_named_target("home")
manipulator.go(wait=True)

# Joint space control
joint_goal = manipulator.get_current_joint_values()
joint_goal[0] = 0.5  # lift height
joint_goal[1] = 0.1  # arm extension
manipulator.set_joint_value_target(joint_goal)
manipulator.go(wait=True)
```

## Topics and Services

Key ROS2 interfaces:
- `/joint_states` - Current joint positions
- `/stretch_controller/follow_joint_trajectory` - Joint trajectory execution
- `/gripper_controller/follow_joint_trajectory` - Gripper control
- `/move_group/*` - MoveIt planning services
- `/camera/color/image_raw` - Camera streams
- `/scan` - Lidar data
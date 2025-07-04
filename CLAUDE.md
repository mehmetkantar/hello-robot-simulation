# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete simulation environment for the Hello Robot Stretch 3 mobile manipulator using Gazebo physics simulation and MoveIt2 motion planning in ROS2 Humble. The project features a working pick-and-place system with a custom multi-world environment containing 5 obstacles, a table, and a glass for autonomous manipulation tasks. The project integrates the official Hello Robot ROS2 packages with custom Gazebo configurations and optimized robot control systems.

## Build Commands

```bash
# Setup environment
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash

# Build workspace (clean build)
colcon build --symlink-install

# Build specific packages only
colcon build --symlink-install --packages-select stretch_moveit_config

# Source the workspace
source install/setup.bash

# Validate setup
cd src/stretch_moveit_config
python3 test_setup.py
```

## Debug Commands

```bash
# Check build logs for errors
colcon build --symlink-install --event-handlers console_direct+

# Rebuild after changes
colcon build --symlink-install --cmake-clean-cache

# Check package dependencies
rosdep check --from-paths src --ignore-src

# Install missing dependencies
rosdep install --from-paths src --ignore-src -r -y
```

## Run Commands

### Quick Start (Working System)
```bash
# Current working implementation - 4 main scripts
cd /home/kantar/Desktop/hello-robot

# Option 1: Direct Gazebo UI launch (recommended)
./simple_gazebo_ui.sh

# Option 2: Interactive mode selection
./choose_gazebo_mode.sh

# Robot control options (run in separate terminal after Gazebo is running)
python3 robot_car_control.py          # Basic driving with GUI
python3 robot_pick_place_control.py   # Advanced pick & place system
```

### Alternative Launch Options (ROS2 Native)
```bash
# Complete simulation (Gazebo + MoveIt + RViz)
ros2 launch stretch_moveit_config stretch_gazebo_moveit.launch.py

# Custom multi-world with fixed robot visibility
ros2 launch launch/ui_multi_world.launch.py

# Gazebo simulation only
ros2 launch stretch_moveit_config stretch_gazebo.launch.py

# MoveIt only (no simulation)
ros2 launch stretch_moveit_config stretch_moveit.launch.py
```

### Step-by-step Manual Launch
```bash
# Start Gazebo server with multi-world
gzserver /home/kantar/Desktop/hello-robot/worlds/multi_world.world &

# Wait 10 seconds, then start UI client
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
gzclient --verbose &

# Launch robot description and control
ros2 launch launch/ui_multi_world.launch.py
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

# Test MoveIt planning
ros2 run moveit_commander moveit_commander_cmdline.py

# Monitor joint states
ros2 topic echo /joint_states --once

# Test trajectory execution
ros2 action send_goal /stretch_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory
```

## Architecture

### Current Working System Structure
- Main directory (`/home/kantar/Desktop/hello-robot/`) - 4 working scripts + archived experimental files
- `simple_gazebo_ui.sh` - Optimized Gazebo UI launcher with VM graphics fixes
- `choose_gazebo_mode.sh` - Interactive mode selection menu
- `robot_car_control.py` - Basic robot driving with GUI controls  
- `robot_pick_place_control.py` - Advanced pick & place system (34k+ lines)
- `launch/` - Custom launch configurations with fixed mesh paths
- `worlds/` - Gazebo world files including multi_world.world with 5 obstacles
- `archived_files/` - 95 experimental/debug files safely stored

### ROS2 Workspace Structure
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

### Working System Files (Main Directory)
- `simple_gazebo_ui.sh` - Primary Gazebo UI launcher with graphics optimizations
- `choose_gazebo_mode.sh` - Interactive simulation mode selector
- `robot_car_control.py` - Basic robot driving control with GUI sliders
- `robot_pick_place_control.py` - Complete pick & place system with predefined poses
- `launch/ui_multi_world.launch.py` - Custom launch file with fixed mesh paths
- `worlds/multi_world.world` - Environment with 5 obstacles, table, and glass
- `README_WORKING_SYSTEM.md` - Documentation of current working system

### Configuration Files (ROS2 Workspace)
- `stretch_ws/src/stretch_moveit_config/config/stretch.srdf` - Robot semantic description
- `stretch_ws/src/stretch_moveit_config/config/joint_limits.yaml` - Motion limits
- `stretch_ws/src/stretch_moveit_config/config/kinematics.yaml` - IK solvers
- `stretch_ws/src/stretch_moveit_config/config/ompl_planning.yaml` - Motion planners
- `stretch_ws/src/stretch_moveit_config/config/moveit_controllers.yaml` - Controller interface

### Launch Files (ROS2 Workspace)
- `stretch_ws/src/stretch_moveit_config/launch/stretch_gazebo_moveit.launch.py` - Main simulation launch
- `stretch_ws/src/stretch_moveit_config/launch/stretch_gazebo.launch.py` - Gazebo only
- `stretch_ws/src/stretch_moveit_config/launch/stretch_moveit.launch.py` - MoveIt only

### Robot Description
- `stretch_ws/src/stretch_ros2/stretch_description/urdf/stretch_gazebo.urdf.xacro` - Gazebo URDF
- `stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_*.urdf` - Robot variants
- Key URDF: `stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf` (used in working system)

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

### Common Issues & Solutions
- **Robot Not Visible in Gazebo**: Mesh paths need to be absolute `file://` paths, not `package://` paths
  - Fixed in `launch/ui_multi_world.launch.py` with mesh path replacement
  - Robot spawns at (-3.0, 2.0, 0.5) to ensure visibility above ground
- **Gazebo UI Crashes (VM Environment)**: Use graphics optimizations
  - Set `LIBGL_ALWAYS_SOFTWARE=1`, `QT_QPA_PLATFORM=xcb`
  - Use `simple_gazebo_ui.sh` for automatic graphics optimization
- **Unwanted Robot Head Movement**: Disable autonomous behaviors in control scripts
  - Use `robot_car_control.py` or `robot_pick_place_control.py` (clean implementations)
- **Memory Requirements**: 16GB+ RAM for smooth Gazebo operation (32GB recommended)
- **MoveIt Planning Failures**: May fail with unreachable goals - try smaller motions
- **Controller Loading**: Ensure proper Gazebo ros2_control plugin loading
- **Missing Dependencies**: Check that all ROS2 environment variables are sourced
- **Joint Limits**: Enforced limits defined in joint_limits.yaml

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
- `/tf` and `/tf_static` - Transform trees
- `/robot_description` - Robot URDF parameter

## File Organization

### Package Structure (ROS2 Standard)
Each package follows standard ROS2 layout:
- `package.xml` - Package manifest with dependencies
- `CMakeLists.txt` - Build configuration (C++ packages)
- `setup.py` - Build configuration (Python packages)
- `src/` - Source code
- `launch/` - Launch files
- `config/` - Configuration files
- `urdf/` - Robot description files
- `meshes/` - 3D model files

### Configuration File Types
- `.yaml` - Parameter files and configuration
- `.srdf` - MoveIt semantic robot description
- `.xacro` - Parameterized URDF files
- `.launch.py` - ROS2 launch scripts
- `.rviz` - RViz visualization configurations

### Build System
- `colcon` - ROS2 workspace build tool
- `ament_cmake` - CMake-based build system
- `setuptools` - Python package building
- `rosdep` - Dependency resolution

## Critical Technical Notes

### Mesh Path Resolution
The key breakthrough for robot visibility was fixing mesh paths in URDF files:
```python
# In launch/ui_multi_world.launch.py (lines 73-78)
meshes_path = os.path.join(pkg_stretch_description, 'meshes')
robot_description_content = robot_description_content.replace(
    'package://stretch_description/meshes/', 
    f'file://{meshes_path}/'
)
```

### VM Graphics Optimization
For virtual machine environments, these environment variables are essential:
```bash
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11
export DISPLAY=:0
```

### Robot Spawning Position
Robot spawns at position (-3.0, 2.0, 0.5) to ensure:
- Visibility above ground plane (Z=0.5)
- Clear distance from obstacles
- Proper orientation toward manipulation targets

### Pick & Place System
The `robot_pick_place_control.py` includes:
- Predefined poses: home, approach_table, grasp_glass, lift_glass, transport, place_position
- Automated sequences for complete pick & place operations
- Manual joint control for fine-tuning
- GUI interface for real-time robot control

### Working Environment
- **Multi-world**: 5 distinct obstacles (boxes, cylinders, L-shaped)
- **Table with glass**: Central manipulation target at (0, 0, 0.75)
- **Room boundaries**: Contained environment for safe navigation
- **Proper lighting**: Optimized for robot visibility and operation
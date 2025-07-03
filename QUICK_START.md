# Hello Robot Stretch 3 - Gazebo & MoveIt Simulation

This repository contains a complete simulation setup for the Hello Robot Stretch 3 using Gazebo and MoveIt in ROS2 Humble.

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install ROS2 Humble (if not already installed)
sudo apt update
sudo apt install ros-humble-desktop ros-humble-gazebo-ros-pkgs ros-humble-moveit

# Install additional dependencies
sudo apt install python3-colcon-common-extensions
```

### 2. Build the Workspace

```bash
cd ~/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### 3. Launch the Complete Simulation

```bash
# Launch Gazebo + MoveIt + RViz
ros2 launch stretch_moveit_config stretch_gazebo_moveit.launch.py
```

This will start:
- 🏗️ Gazebo simulation with Stretch 3 robot
- 🎯 MoveIt motion planning framework
- 👁️ RViz with motion planning interface
- 🎮 Joint trajectory controllers

## 🎯 What You Can Do

### Motion Planning with RViz
1. **Set Planning Group**: Select "manipulator" in RViz MoveIt plugin
2. **Set Goal**: Drag the interactive markers to desired positions
3. **Plan**: Click "Plan" to generate a trajectory
4. **Execute**: Click "Execute" to run the motion

### Available Planning Groups
- **manipulator**: Main arm (lift + telescoping arm + wrist)
- **arm**: Telescoping arm segments only  
- **wrist**: Wrist joints (yaw, pitch, roll)
- **gripper**: Gripper fingers
- **head**: Head pan and tilt
- **mobile_base**: Differential drive wheels

### Predefined Poses
- **home**: All joints at zero
- **stow**: Robot in compact stowed position
- **gripper open/closed**: Gripper states

## 🔧 Alternative Launch Options

### Gazebo Only
```bash
ros2 launch stretch_moveit_config stretch_gazebo.launch.py
```

### MoveIt Only (no simulation)  
```bash
ros2 launch stretch_moveit_config stretch_moveit.launch.py
```

## 🐍 Python API Example

```python
import rclpy
from moveit_commander import MoveGroupCommander, RobotCommander

rclpy.init()
robot = RobotCommander()
group = MoveGroupCommander("manipulator")

# Move to named pose
group.set_named_target("home")
group.go(wait=True)

# Move to joint positions
joint_goal = group.get_current_joint_values()
joint_goal[0] = 0.5  # lift up
joint_goal[1] = 0.1  # extend arm
group.set_joint_value_target(joint_goal)
group.go(wait=True)
```

## 📁 Package Structure

```
stretch_ws/
├── src/
│   ├── stretch_ros2/           # Official Stretch ROS2 packages
│   │   ├── stretch_description/ # URDF and robot description
│   │   ├── stretch_simulation/  # MuJoCo simulation (alternative)
│   │   └── stretch_core/        # Robot drivers and controllers
│   └── stretch_moveit_config/   # Our MoveIt configuration
│       ├── config/              # MoveIt configuration files
│       ├── launch/              # Launch files
│       └── README.md            # Detailed documentation
```

## 🛠️ Customization

- **Joint Limits**: Edit `config/joint_limits.yaml`
- **Planning**: Modify `config/ompl_planning.yaml`
- **Robot Groups**: Update `config/stretch.srdf`
- **Controllers**: Adjust `config/moveit_controllers.yaml`

## ✅ Validation

Run the setup test:
```bash
cd stretch_ws/src/stretch_moveit_config
python3 test_setup.py
```

## 🆘 Troubleshooting

- **"colcon: command not found"**: Install colcon with `sudo apt install python3-colcon-common-extensions`
- **Robot not spawning**: Check that all URDF files are present
- **MoveIt not planning**: Verify joint limits and collision settings
- **Controllers failing**: Ensure Gazebo ros2_control plugins are loaded

## 🤝 Contributing

This simulation integrates:
- Hello Robot's official Stretch packages
- Custom Gazebo integration with sensors and controllers
- Complete MoveIt2 configuration with planning groups
- RViz visualization and interactive planning

Perfect for research, education, and development with the Stretch 3 robot!
# Hello Robot Stretch 3 - Gazebo & MoveIt Simulation

[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Classic-orange)](http://gazebosim.org/)
[![MoveIt](https://img.shields.io/badge/MoveIt2-Enabled-green)](https://moveit.ros.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A complete simulation environment for the **Hello Robot Stretch 3** mobile manipulator using **Gazebo** physics simulation and **MoveIt2** motion planning in **ROS2 Humble**.

![Stretch Robot](https://hello-robot.com/assets/images/stretch_re2_family.jpg)

## 🌟 Features

- 🤖 **Complete Stretch 3 Robot Model** with accurate kinematics and dynamics
- 🏗️ **Gazebo Integration** with physics simulation, sensors, and environmental interaction
- 🎯 **MoveIt2 Motion Planning** with OMPL planners and collision detection
- 👁️ **RViz Visualization** with interactive motion planning interface
- 🎮 **Multiple Planning Groups** for different robot subsystems
- 📡 **Sensor Simulation** including Lidar, cameras, and IMU
- 🚀 **Easy Launch System** with single-command startup
- 🐍 **Python API** support for programmatic control

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Package Structure](#-package-structure)
- [Robot Configuration](#-robot-configuration)
- [Programming Interface](#-programming-interface)
- [Advanced Topics](#-advanced-topics)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🛠️ Installation

### Prerequisites

- **Ubuntu 22.04 LTS**
- **ROS2 Humble** (Desktop installation recommended)
- **Python 3.10+**
- **16GB RAM** (minimum), **32GB RAM** (recommended)
- **NVIDIA GPU** (recommended for Gazebo performance)

### Step 1: Install ROS2 Humble

```bash
# Add ROS2 repository
sudo apt update && sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS2 Humble Desktop
sudo apt update
sudo apt install ros-humble-desktop ros-dev-tools
```

### Step 2: Install Dependencies

```bash
# Install MoveIt2 and Gazebo packages
sudo apt install \
    ros-humble-moveit \
    ros-humble-moveit-planners \
    ros-humble-moveit-simple-controller-manager \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-joint-state-publisher-gui \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool
```

### Step 3: Clone and Build

```bash
# Clone the repository
cd ~/Desktop
git clone <this-repository-url> hello-robot
cd hello-robot/stretch_ws

# Initialize rosdep (if not done before)
sudo rosdep init
rosdep update

# Install workspace dependencies
rosdep install --from-paths src --ignore-src -r -y

# Source ROS2 and build
source /opt/ros/humble/setup.bash
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

### Step 4: Verify Installation

```bash
cd src/stretch_moveit_config
python3 test_setup.py
```

You should see: `🎉 ALL TESTS PASSED!`

## 🚀 Quick Start

### Launch Complete Simulation

```bash
# Terminal 1: Launch the complete simulation
cd ~/Desktop/hello-robot/stretch_ws
source install/setup.bash
ros2 launch stretch_moveit_config stretch_gazebo_moveit.launch.py
```

This single command launches:
- **Gazebo** with Stretch 3 robot
- **MoveIt2** motion planning framework  
- **RViz** with motion planning interface
- **Joint controllers** for robot actuation

### First Motion Planning

1. **Wait for startup** (30-60 seconds for all components to initialize)
2. **In RViz**:
   - Select planning group: "**manipulator**"
   - Drag orange interactive markers to set goal pose
   - Click "**Plan**" button
   - Click "**Execute**" to run the motion
3. **Watch the robot move** in both Gazebo and RViz!

## 📚 Usage Guide

### Planning Groups

The robot is organized into several planning groups:

| Group | Description | Joints |
|-------|-------------|---------|
| `manipulator` | Complete arm system | lift + arm + wrist |
| `arm` | Telescoping arm only | joint_arm_l0 to l3 |
| `wrist` | 3-DOF wrist | yaw, pitch, roll |
| `gripper` | Finger control | left/right fingers |
| `head` | Camera positioning | pan, tilt |
| `mobile_base` | Wheel drive | left/right wheels |

### Predefined Poses

Access these poses in RViz or via API:

- **`home`**: All joints at zero position
- **`stow`**: Compact storage configuration
- **`gripper_open`**: Gripper fully opened
- **`gripper_closed`**: Gripper closed

### Alternative Launch Options

```bash
# Gazebo simulation only
ros2 launch stretch_moveit_config stretch_gazebo.launch.py

# MoveIt only (no simulation)
ros2 launch stretch_moveit_config stretch_moveit.launch.py

# With custom world file
ros2 launch stretch_moveit_config stretch_gazebo_moveit.launch.py world_name:=my_world.world
```

## 📁 Package Structure

```
hello-robot/
├── README.md                          # This file
├── QUICK_START.md                     # Quick reference guide
└── stretch_ws/                        # ROS2 workspace
    └── src/
        ├── stretch_ros2/               # Official Stretch packages
        │   ├── stretch_description/    # Robot URDF and meshes
        │   ├── stretch_core/           # Hardware drivers
        │   ├── stretch_simulation/     # MuJoCo simulation
        │   └── stretch_nav2/           # Navigation stack
        └── stretch_moveit_config/      # Our MoveIt configuration
            ├── config/                 # Configuration files
            │   ├── stretch.srdf        # Robot semantic description
            │   ├── kinematics.yaml     # Inverse kinematics solvers
            │   ├── joint_limits.yaml   # Motion limits
            │   ├── moveit_controllers.yaml # Controller interface
            │   ├── ompl_planning.yaml  # Motion planners
            │   └── moveit.rviz         # RViz configuration
            ├── launch/                 # Launch files
            │   ├── stretch_gazebo.launch.py
            │   ├── stretch_moveit.launch.py
            │   └── stretch_gazebo_moveit.launch.py
            ├── test_setup.py           # Validation script
            └── README.md               # Package documentation
```

## 🤖 Robot Configuration

### Joint Specifications

| Joint | Type | Range | Max Velocity | Description |
|-------|------|-------|--------------|-------------|
| `joint_lift` | Prismatic | 0.0 → 1.1m | 0.2 m/s | Vertical lift |
| `joint_arm_l0-l3` | Prismatic | 0.0 → 0.13m each | 0.4 m/s | Telescoping arm |
| `joint_wrist_yaw` | Revolute | -90° → 270° | 4.0 rad/s | Wrist rotation |
| `joint_wrist_pitch` | Revolute | -90° → 32° | 4.0 rad/s | Wrist pitch |
| `joint_wrist_roll` | Revolute | -90° → 90° | 4.0 rad/s | Wrist roll |
| `joint_gripper_*` | Revolute | ±0.166 rad | 0.5 rad/s | Gripper fingers |
| `joint_head_pan` | Revolute | ±90° | 2.0 rad/s | Head pan |
| `joint_head_tilt` | Revolute | -75° → 13° | 2.0 rad/s | Head tilt |

### Sensors

- **RPLidar A1**: 360° laser scanner (4m range)
- **Intel RealSense D435i**: RGB-D camera with IMU
- **Intel RealSense D405**: Wrist-mounted depth camera
- **Base IMU**: Orientation and acceleration sensing

## 🐍 Programming Interface

### Python MoveIt API

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from moveit_commander import MoveGroupCommander, RobotCommander, PlanningSceneInterface
from geometry_msgs.msg import Pose, Point, Quaternion

class StretchController(Node):
    def __init__(self):
        super().__init__('stretch_controller')
        
        # Initialize MoveIt commanders
        self.robot = RobotCommander()
        self.scene = PlanningSceneInterface()
        
        # Planning groups
        self.manipulator = MoveGroupCommander("manipulator")
        self.gripper = MoveGroupCommander("gripper")
        self.head = MoveGroupCommander("head")
        
        self.get_logger().info("Stretch controller initialized")
    
    def go_to_home(self):
        """Move to home position"""
        self.manipulator.set_named_target("home")
        return self.manipulator.go(wait=True)
    
    def extend_arm(self, lift_height=0.5, arm_extension=0.3):
        """Extend the arm to specified position"""
        joint_goal = self.manipulator.get_current_joint_values()
        joint_goal[0] = lift_height     # lift
        joint_goal[1] = arm_extension   # arm extension
        
        self.manipulator.set_joint_value_target(joint_goal)
        return self.manipulator.go(wait=True)
    
    def move_to_pose(self, x, y, z, roll=0, pitch=0, yaw=0):
        """Move end effector to Cartesian pose"""
        pose_goal = Pose()
        pose_goal.position = Point(x=x, y=y, z=z)
        
        # Convert RPY to quaternion (simplified)
        pose_goal.orientation = Quaternion(x=0, y=0, z=0, w=1)
        
        self.manipulator.set_pose_target(pose_goal)
        return self.manipulator.go(wait=True)
    
    def control_gripper(self, open_gripper=True):
        """Open or close gripper"""
        if open_gripper:
            self.gripper.set_named_target("open")
        else:
            self.gripper.set_named_target("closed")
        return self.gripper.go(wait=True)
    
    def look_at_position(self, pan=0.0, tilt=0.0):
        """Point head to specified angles"""
        joint_goal = self.head.get_current_joint_values()
        joint_goal[0] = pan   # head_pan
        joint_goal[1] = tilt  # head_tilt
        
        self.head.set_joint_value_target(joint_goal)
        return self.head.go(wait=True)

def main():
    rclpy.init()
    
    controller = StretchController()
    
    try:
        # Example sequence
        controller.get_logger().info("Going to home position...")
        controller.go_to_home()
        
        controller.get_logger().info("Opening gripper...")
        controller.control_gripper(open_gripper=True)
        
        controller.get_logger().info("Extending arm...")
        controller.extend_arm(lift_height=0.8, arm_extension=0.2)
        
        controller.get_logger().info("Looking around...")
        controller.look_at_position(pan=0.5, tilt=-0.3)
        
        controller.get_logger().info("Sequence complete!")
        
    except KeyboardInterrupt:
        controller.get_logger().info("Interrupted by user")
    
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Running the Example

```bash
# Save the code as stretch_example.py
python3 stretch_example.py
```

### ROS2 Command Line Interface

```bash
# Get current joint states
ros2 topic echo /joint_states

# Send trajectory commands
ros2 action send_goal /stretch_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "trajectory: {joint_names: ['joint_lift'], points: [{positions: [0.5], time_from_start: {sec: 2}}]}"

# Control gripper
ros2 action send_goal /gripper_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "trajectory: {joint_names: ['joint_gripper_finger_left', 'joint_gripper_finger_right'], points: [{positions: [0.166, -0.166], time_from_start: {sec: 1}}]}"
```

## 🔧 Advanced Topics

### Custom Planning Constraints

```python
# Add path constraints
from moveit_msgs.msg import Constraints, OrientationConstraint

constraints = Constraints()
ocm = OrientationConstraint()
ocm.link_name = "link_gripper"
ocm.header.frame_id = "base_link"
ocm.orientation.w = 1.0
ocm.absolute_x_axis_tolerance = 0.1
ocm.absolute_y_axis_tolerance = 0.1
ocm.absolute_z_axis_tolerance = 0.1
ocm.weight = 1.0

constraints.orientation_constraints.append(ocm)
manipulator.set_path_constraints(constraints)
```

### Adding Collision Objects

```python
# Add table to planning scene
from geometry_msgs.msg import PoseStamped
from shape_msgs.msg import SolidPrimitive

table_pose = PoseStamped()
table_pose.header.frame_id = "base_link"
table_pose.pose.position.x = 0.5
table_pose.pose.position.z = 0.4
table_pose.pose.orientation.w = 1.0

scene.add_box("table", table_pose, size=(0.8, 1.2, 0.02))
```

### Custom Motion Planners

Edit `config/ompl_planning.yaml` to modify planner settings:

```yaml
manipulator:
  planner_configs:
    - RRTConnectkConfigDefault
    - RRTstarkConfigDefault
  projection_evaluator: joints(joint_lift,joint_arm_l0)
  longest_valid_segment_fraction: 0.01  # Higher precision
```

## 🛠️ Troubleshooting

### Common Issues

**Issue**: `colcon: command not found`
```bash
sudo apt install python3-colcon-common-extensions
```

**Issue**: Robot not appearing in Gazebo
```bash
# Check if URDF files are present
ls ~/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/
```

**Issue**: MoveIt planning fails
```bash
# Check joint limits and collision detection
ros2 param list /move_group
```

**Issue**: Controllers not responding
```bash
# List available controllers
ros2 control list_controllers

# Check controller status
ros2 control list_hardware_interfaces
```

**Issue**: Performance problems
- Ensure you have sufficient RAM (16GB+)
- Close unnecessary applications
- Consider using GPU acceleration for Gazebo

### Debug Commands

```bash
# Check ROS2 nodes
ros2 node list

# Monitor topics
ros2 topic list
ros2 topic echo /joint_states

# Check transforms
ros2 run tf2_tools view_frames

# MoveIt debugging
ros2 param get /move_group robot_description
```

### Performance Optimization

```bash
# Set Gazebo to use GPU (if available)
export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models
export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11
export GAZEBO_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/gazebo-11/plugins
export GAZEBO_MODEL_DATABASE_URI=""
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Test thoroughly** with the validation script
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines

- Follow ROS2 coding standards
- Add documentation for new features
- Include unit tests where applicable
- Test with both simulation and (if available) real hardware

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hello Robot Inc.** for the amazing Stretch robot and official ROS2 packages
- **Open Source Robotics Foundation** for ROS2, Gazebo, and MoveIt2
- **PickNik Robotics** for MoveIt2 development and support
- The open-source robotics community for tools and inspiration

## 📞 Support

- **Documentation**: [Hello Robot Docs](https://docs.hello-robot.com/)
- **Community Forum**: [Hello Robot Forum](https://forum.hello-robot.com/)
- **ROS2 Support**: [ROS Discourse](https://discourse.ros.org/)
- **Issues**: Use the GitHub Issues tab for bug reports and feature requests

---

**Happy Robot Programming! 🤖✨**

Made with ❤️ for the robotics community
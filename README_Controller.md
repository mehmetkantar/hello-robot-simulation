# 🤖 Stretch Robot Advanced Controller

A modern, aesthetic GUI controller for the Hello Robot Stretch with simultaneous RViz and MuJoCo visualization.

## ✨ Features

### 🎮 Modern GUI Interface
- **Virtual Joystick**: Intuitive base movement control
- **Modern Sliders**: Smooth arm joint control (lift, extension, wrist, gripper)
- **Real-time Camera Feeds**: Live display from all robot cameras
- **Robot Status Monitoring**: Joint positions and system status
- **Emergency Stop**: Immediate halt of all robot movement
- **Quick Actions**: Home and stow position buttons

### 🔄 Simultaneous Visualization
- **MuJoCo Physics**: Realistic physics simulation with collision detection
- **RViz2**: Real-time robot state visualization and mapping
- **SLAM Integration**: Build maps while controlling the robot
- **Camera Integration**: See what the robot sees in real-time

## 🚀 Quick Start

### Launch Everything at Once
```bash
# Start the complete system (GUI + RViz + MuJoCo + SLAM)
./launch_robot_controller.sh

# Options:
./launch_robot_controller.sh --complex-world    # Complex demo environment (default)
./launch_robot_controller.sh --kitchen-world    # Kitchen environment
./launch_robot_controller.sh --simple-world     # Simple office environment
./launch_robot_controller.sh --headless         # Run MuJoCo without display
./launch_robot_controller.sh --no-gui          # Skip GUI controller
```

### Manual Launch (Step by Step)
```bash
# 1. Start MuJoCo simulation
python3 stretch_slam_bridge_improved.py --environment=demo_complex

# 2. Start SLAM
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=$(pwd)/config/slam_params.yaml

# 3. Start RViz
rviz2 -d $(pwd)/rviz/stretch_slam.rviz

# 4. Start controller bridge
python3 stretch_controller_bridge.py

# 5. Start GUI controller
python3 stretch_robot_controller.py
```

## 🎯 How to Use

### Base Movement
1. **Virtual Joystick**: Click and drag the blue knob to move the robot
   - Forward/Backward: Move knob up/down
   - Left/Right Turn: Move knob left/right
   - Release to stop
2. **Speed Control**: Adjust max linear and angular speeds with sliders
3. **Emergency Stop**: Red button immediately halts all movement

### Arm Control
1. **Lift Height**: Control vertical position of the arm
2. **Arm Extension**: Extend/retract the telescopic arm
3. **Wrist Orientation**: 
   - Yaw: Left/right rotation
   - Pitch: Up/down tilt
   - Roll: Twist rotation
4. **Gripper**: Open/close the gripper fingers

### Quick Actions
- **🏠 Home**: Move to standard home position
- **📦 Stow**: Compact storage position for navigation

### Monitoring
- **Camera Feeds**: Live video from D405, D435i, and Navigation cameras
- **Joint Status**: Real-time joint positions and robot state
- **System Messages**: Status updates and error messages

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  GUI Controller │───▶│ Controller Bridge │───▶│ MuJoCo Simulator│
│                 │    │                  │    │                 │
│ • Virtual       │    │ • Command        │    │ • Physics       │
│   Joystick      │    │   Translation    │    │ • Visualization │
│ • Arm Sliders   │    │ • Safety Limits  │    │ • Collision     │
│ • Camera Views  │    │ • ROS2 Bridge    │    │   Detection     │
│ • Status Info   │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────▶│     RViz2       │◀─────────────┘
                        │                 │
                        │ • Robot Model   │
                        │ • SLAM Map      │
                        │ • Camera Feeds  │
                        │ • Sensor Data   │
                        └─────────────────┘
```

## 🛠️ Technical Details

### GUI Components
- **Framework**: PyQt5 with modern styling
- **Real-time Updates**: 20Hz control loop
- **Camera Display**: OpenCV integration with ROS2
- **Safety Features**: Joint limits and emergency stop

### ROS2 Integration
- **Publishers**: `/cmd_vel`, joint commands
- **Subscribers**: `/joint_states`, camera topics
- **Bridge Node**: Translates GUI commands to simulation

### Environments
- **Demo Complex**: Multi-room building with offices and labs
- **Kitchen Scene**: Residential kitchen with appliances
- **Simple Office**: Basic office environment for testing

## 🎨 GUI Features

### Modern Design
- **Gradient Backgrounds**: Professional appearance
- **Hover Effects**: Interactive button responses  
- **Color Coding**: Intuitive status indicators
- **Responsive Layout**: Adapts to different screen sizes

### User Experience
- **Intuitive Controls**: Natural joystick and slider interaction
- **Visual Feedback**: Real-time status updates
- **Error Handling**: Graceful failure recovery
- **Performance**: Smooth 20Hz updates

## 🔧 Troubleshooting

### GUI Won't Start
```bash
# Check PyQt5 installation
python3 -c "import PyQt5; print('PyQt5 OK')"

# Install if missing
sudo apt install python3-pyqt5

# Check display
echo $DISPLAY
```

### No Camera Images
- Check if simulation is publishing images
- Verify ROS2 topic connections: `ros2 topic list`
- Check camera topic data: `ros2 topic echo /camera/d405_camera/color/image_raw`

### Robot Not Moving
- Verify controller bridge is running
- Check ROS2 connections: `ros2 node list`
- Test direct commands: `ros2 topic pub /cmd_vel geometry_msgs/Twist ...`

### Performance Issues
- Reduce camera resolution in simulation
- Lower GUI update frequency
- Use headless mode: `--headless`

## 📋 Requirements

### System Requirements
- **OS**: Ubuntu 20.04+ or ROS2-compatible system
- **ROS2**: Humble Hawksbill
- **Python**: 3.8+
- **Display**: X11 (for GUI)

### Dependencies
```bash
# ROS2 packages
sudo apt install ros-humble-slam-toolbox ros-humble-joint-state-publisher

# Python packages
pip3 install PyQt5 opencv-python numpy

# MuJoCo (included in stretch_mujoco)
```

## 🎬 Demo Scenarios

### Scenario 1: Exploration
1. Launch with complex environment
2. Use joystick to navigate between rooms
3. Watch SLAM build the map in RViz
4. See physics simulation in MuJoCo

### Scenario 2: Manipulation
1. Navigate to object location
2. Use arm sliders to position end-effector
3. Control gripper to pick up objects
4. Monitor with camera feeds

### Scenario 3: Multi-Room Mapping
1. Start in central corridor
2. Systematically explore each room
3. Build complete building map
4. Save map for future use

## 📝 Notes

- All joint movements respect safety limits
- Emergency stop immediately halts all motion
- Camera feeds update at 30 FPS when available
- System supports multiple simultaneous camera views
- SLAM map persists between sessions

## 🔗 Integration

The controller integrates seamlessly with:
- **Navigation2**: Path planning and autonomous navigation
- **MoveIt2**: Advanced manipulation planning
- **Custom Behaviors**: Your own robot behaviors and algorithms
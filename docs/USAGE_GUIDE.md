# Detailed Usage Guide

## Getting Started

### Prerequisites

Before running the simulation, ensure you have:

1. **stretch_mujoco installed** and properly configured
2. **Python 3.8+** with required packages
3. **Graphics drivers** for MuJoCo rendering

### First Time Setup

1. **Clone this repository**:
   ```bash
   git clone https://github.com/mehmetkantar/hello-robot-simulation.git
   cd hello-robot-simulation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify stretch_mujoco installation**:
   ```bash
   python -c "from stretch_mujoco import StretchMujocoSimulator; print('stretch_mujoco is working!')"
   ```

## Interface Overview

The GUI consists of three main tabs:

### 1. Robot Control Tab

**Left Panel - Movement Controls:**
- **Base Movement**: WASD keys or buttons
- **Arm Control**: IJKL keys for lift and extension
- **Head Control**: TFGH keys for pan/tilt
- **Wrist Control**: OPCVER keys for yaw/pitch/roll
- **Gripper Control**: NM keys for open/close

**Right Panel - Live Camera Feeds:**
- **D405 RGB**: Primary head camera
- **D435i RGB**: Secondary head camera  
- **Navigation**: Wide-angle navigation camera

**Preset Commands:**
- **Home Position**: Move robot to home pose
- **Stow Position**: Move robot to stow pose
- **Print Status**: Display detailed robot status

### 2. Status & Monitor Tab

**Detailed Status Display:**
- Real-time simulation metrics
- Base position and velocity
- Joint positions and velocities
- Simulation FPS and timing

**Log Output:**
- System messages and debugging info
- Camera connection status
- Performance metrics

### 3. Instructions Tab

Complete reference for keyboard shortcuts and usage tips.

## Performance Optimization

### Understanding Simulation Speed

The simulation displays "sim is running Xx as fast as realtime":
- **1.0x**: Real-time speed (ideal)
- **0.5x**: Half real-time speed (acceptable)
- **0.1x**: Very slow (needs optimization)
- **< 0.05x**: Too slow for practical use

### Optimization Options

#### Option 1: Fast Mode (Recommended for Speed)
- **Enable**: Check "Fast Mode (Disable cameras)"
- **Effect**: Disables all cameras for maximum speed
- **Expected**: 0.5x - 1.0x real-time speed
- **Use case**: When you don't need camera feedback

#### Option 2: Reduce Camera FPS
- **Setting**: Camera FPS spinbox (1-30)
- **Recommended**: 2-5 FPS for balanced performance
- **Effect**: Less frequent camera updates
- **Expected**: 0.2x - 0.5x real-time speed

#### Option 3: Disable MuJoCo Viewer
- **Setting**: Uncheck "Enable Mujoco 3D Viewer"
- **Effect**: No 3D visualization window
- **Benefit**: Slight performance improvement
- **Trade-off**: No visual feedback of robot in 3D space

## Advanced Features

### Velocity Scaling

Base movement buttons support intelligent velocity scaling:

1. **Single Click**: Normal speed (1x multiplier)
2. **Quick Double Click**: Increased speed (2x multiplier)
3. **Triple Click**: Maximum speed (3x multiplier)
4. **Auto Reset**: Returns to 1x after 1 second of no clicks

**To use:**
- Click movement buttons rapidly for increased speed
- Click "Stop" button to reset scaling
- Scaling applies to WASD keyboard control as well

### Camera Features

**Camera Types:**
- **D405 RGB**: 270x480 resolution, head-mounted
- **D435i RGB**: 240x424 resolution, alternative head camera
- **Navigation RGB**: Wide-angle view for navigation

**Camera Controls:**
- Cameras automatically follow robot head movement
- Real-time updates at configurable FPS
- Automatic rotation correction for proper viewing

## Keyboard Shortcuts Reference

### Movement Controls
```
Base Movement:
  W - Forward
  S - Backward  
  A - Rotate Left
  D - Rotate Right

Head Control:
  T - Tilt Up
  G - Tilt Down
  F - Pan Left
  H - Pan Right

Arm Control:
  I - Lift Up
  K - Lift Down
  J - Arm Retract
  L - Arm Extend

Wrist Control:
  O - Yaw Left
  P - Yaw Right
  C - Pitch Up
  V - Pitch Down
  E - Roll Counter-clockwise
  R - Roll Clockwise

Gripper:
  N - Open
  M - Close

System:
  Z - Print detailed status
  Q - Stop simulation
```

### Pro Tips

1. **Focus Management**: Click on the main window to ensure keyboard shortcuts work
2. **Smooth Movement**: Use keyboard for continuous movement, buttons for precise control
3. **Status Monitoring**: Use 'Z' key to print detailed status to log
4. **Emergency Stop**: Use 'Q' key or "Stop Simulation" button

## Common Workflows

### 1. Basic Navigation
```
1. Start simulation with cameras enabled
2. Use WASD to drive the base around
3. Use TFGH to look around with head cameras
4. Monitor navigation camera for obstacle avoidance
```

### 2. Object Manipulation
```
1. Position robot near object using base movement
2. Use head cameras to locate object precisely
3. Extend arm with 'L' key
4. Adjust wrist orientation with OPCVER keys
5. Open gripper with 'N', position, close with 'M'
```

### 3. High-Speed Testing
```
1. Enable "Fast Mode" for maximum simulation speed
2. Use keyboard controls for rapid testing
3. Monitor status tab for performance metrics
4. Use preset commands for quick positioning
```

## Integration with ROS2

While this GUI uses stretch_mujoco directly, it can be extended to work with ROS2:

- Joint states can be published to ROS2 topics
- Camera feeds can be published as sensor_msgs/Image
- Movement commands can subscribe to geometry_msgs/Twist

See the examples directory for ROS2 integration examples.
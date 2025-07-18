# Hello Robot Stretch Dual GUI Simulation

Advanced GUI control interface for Hello Robot Stretch with integrated MuJoCo simulation and live camera feeds.

## Features

- **Dual Interface**: Advanced GUI controls + MuJoCo 3D viewer
- **Live Camera Feeds**: Real-time camera views from D405, D435i, and Navigation cameras
- **Performance Optimization**: Fast mode and configurable camera FPS for optimal simulation speed
- **Comprehensive Control**: 
  - Base movement with velocity scaling (WASD)
  - Arm control (IJKL)
  - Head control (TFGH)
  - Wrist control (OPCVER)
  - Gripper control (NM)
- **Real-time Monitoring**: Joint status, robot pose, and simulation metrics
- **Keyboard Shortcuts**: Full keyboard control support

## Requirements

- Python 3.8+
- stretch_mujoco
- tkinter
- PIL (Pillow)
- OpenCV (cv2)
- NumPy

## Installation

1. **Install stretch_mujoco**:
   ```bash
   # Follow the installation guide for stretch_mujoco
   # Ensure it's properly installed and configured
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the simulation**:
   ```bash
   python stretch_dual_gui.py
   ```

## Usage

### Starting the Simulation

1. **Configure options**:
   - Enable/disable MuJoCo 3D Viewer
   - Enable/disable cameras
   - Enable Fast Mode for maximum performance
   - Adjust Camera FPS (1-30)

2. **Click "Start Dual GUI Mode"**

3. **Control the robot**:
   - Use GUI buttons or keyboard shortcuts
   - Monitor real-time camera feeds
   - Check status in the Status & Monitor tab

### Performance Optimization

The simulation performance can be optimized based on your needs:

- **Fast Mode**: Disables cameras for maximum simulation speed (~1.0x real-time)
- **Low Camera FPS**: Reduce camera FPS to 1-5 for better performance
- **No Cameras**: Disable cameras while keeping MuJoCo viewer

### Keyboard Controls

| Key | Action |
|-----|--------|
| W/S | Forward/Backward |
| A/D | Rotate Left/Right |
| T/G | Head Tilt Up/Down |
| F/H | Head Pan Left/Right |
| I/K | Lift Up/Down |
| J/L | Arm Retract/Extend |
| O/P | Wrist Yaw Left/Right |
| C/V | Wrist Pitch Up/Down |
| E/R | Wrist Roll CCW/CW |
| N/M | Gripper Open/Close |
| Z | Print Status |
| Q | Stop Simulation |

### Velocity Scaling

Base movement supports velocity scaling:
- **Single click**: Normal speed (1x)
- **Multiple clicks**: Increased speed (up to 3x)
- **Stop button**: Resets velocity scaling

## Camera Views

The simulation provides three live camera feeds:

1. **D405 RGB Camera**: Head-mounted camera for navigation
2. **D435i RGB Camera**: Alternative head camera
3. **Navigation RGB Camera**: Wide-angle navigation view

Cameras are displayed in a grid layout in the main control panel.

## Project Structure

```
hello-robot-simulation/
├── stretch_dual_gui.py     # Main simulation application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── docs/                  # Documentation
│   ├── USAGE_GUIDE.md     # Detailed usage instructions
│   └── TROUBLESHOOTING.md # Common issues and solutions
└── examples/              # Example scripts and configurations
```

## Troubleshooting

### Common Issues

1. **Simulation runs slowly (< 0.1x real-time)**:
   - Enable "Fast Mode" to disable cameras
   - Reduce Camera FPS to 1-5
   - Ensure stretch_mujoco is properly installed

2. **Camera feeds show "Camera Not Connected"**:
   - Ensure cameras are enabled in the main GUI
   - Check that stretch_mujoco supports camera rendering
   - Restart simulation with cameras enabled

3. **MuJoCo viewer doesn't appear**:
   - Check "Enable MuJoCo 3D Viewer" option
   - Ensure graphics drivers are properly installed

4. **Keyboard shortcuts don't work**:
   - Click on the main GUI window to focus it
   - Ensure simulation is running

### Performance Tips

- **For maximum speed**: Enable Fast Mode (disables cameras)
- **For balanced performance**: Set Camera FPS to 2-5
- **For full features**: Use default settings (may be slower)

## Contributing

This project is part of the Hello Robot ecosystem. Please follow the standard contribution guidelines.

## License

This project follows the same license as the Hello Robot stretch_mujoco package.

## Support

For issues related to:
- **stretch_mujoco**: Check the official stretch_mujoco documentation
- **This GUI**: Create an issue in this repository
- **Hello Robot hardware**: Contact Hello Robot support

---

**Generated with Claude Code** 🤖
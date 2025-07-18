# Troubleshooting Guide

## Common Issues and Solutions

### Performance Issues

#### Issue: Simulation runs very slowly (< 0.1x real-time)

**Symptoms:**
- Status shows "sim is running 0.043x as fast as realtime"
- Robot movement is jerky or delayed
- GUI becomes unresponsive

**Solutions:**
1. **Enable Fast Mode** (most effective):
   ```
   ✓ Check "Fast Mode (Disable cameras)" before starting
   Expected result: 0.5x - 1.0x real-time speed
   ```

2. **Reduce Camera FPS**:
   ```
   Set Camera FPS to 1-3 instead of default 10
   Expected result: 0.2x - 0.5x real-time speed
   ```

3. **Disable Cameras**:
   ```
   ✗ Uncheck "Enable Cameras"
   Keep MuJoCo viewer for visual feedback
   ```

4. **System optimization**:
   ```bash
   # Close other applications
   # Ensure adequate RAM (4GB+ recommended)
   # Use dedicated graphics card if available
   ```

#### Issue: Camera rendering causes crashes

**Symptoms:**
- Simulation crashes when cameras are enabled
- Error messages about OpenGL or rendering
- "Camera Not Connected" despite enabled cameras

**Solutions:**
1. **Update graphics drivers**:
   ```bash
   # For NVIDIA:
   sudo apt update && sudo apt install nvidia-driver-XXX
   
   # For Intel/AMD:
   sudo apt update && sudo apt install mesa-drivers
   ```

2. **Reduce camera resolution** (modify stretch_dual_gui.py):
   ```python
   # In update_camera_display method, change:
   img_pil = img_pil.resize((150, 100), Image.Resampling.LANCZOS)
   ```

3. **Use software rendering**:
   ```bash
   export MUJOCO_GL=osmesa
   python stretch_dual_gui.py
   ```

### Installation Issues

#### Issue: "No module named 'stretch_mujoco'"

**Symptoms:**
```
ImportError: No module named 'stretch_mujoco'
STRETCH_MUJOCO_AVAILABLE = False
```

**Solutions:**
1. **Install stretch_mujoco**:
   ```bash
   # Follow official Hello Robot installation guide
   # Ensure all dependencies are installed
   ```

2. **Check Python path**:
   ```bash
   python -c "import sys; print(sys.path)"
   # Ensure stretch_mujoco is in the path
   ```

3. **Virtual environment issues**:
   ```bash
   # If using conda/venv, ensure stretch_mujoco is installed in same environment
   which python
   pip list | grep stretch
   ```

#### Issue: "No module named 'PIL'" or PIL import errors

**Solutions:**
```bash
# Uninstall PIL and install Pillow
pip uninstall PIL
pip install Pillow>=9.0.0

# If still issues:
pip install --upgrade Pillow
```

#### Issue: tkinter not available

**Symptoms:**
```
ImportError: No module named 'tkinter'
```

**Solutions:**
```bash
# Ubuntu/Debian:
sudo apt install python3-tk

# CentOS/RHEL:
sudo yum install tkinter

# macOS (if using Homebrew Python):
brew install python-tk
```

### Runtime Issues

#### Issue: Keyboard shortcuts don't work

**Symptoms:**
- Pressing WASD or other keys has no effect
- Only GUI buttons work

**Solutions:**
1. **Focus the window**:
   ```
   Click anywhere on the main GUI window
   Ensure it has keyboard focus (title bar highlighted)
   ```

2. **Check simulation state**:
   ```
   Ensure simulation is running (status shows "Dual GUI Running")
   If stopped, start simulation first
   ```

3. **Key binding conflicts**:
   ```
   Close other applications that might capture global hotkeys
   Check if accessibility software is interfering
   ```

#### Issue: MuJoCo viewer window doesn't appear

**Symptoms:**
- "Enable Mujoco 3D Viewer" is checked
- Only GUI window appears, no 3D visualization

**Solutions:**
1. **Check display settings**:
   ```bash
   echo $DISPLAY  # Should show :0 or similar
   xhost +local:  # Allow local connections
   ```

2. **Window manager issues**:
   ```
   Check if window is minimized or on another desktop
   Try Alt+Tab to find MuJoCo window
   ```

3. **Graphics compatibility**:
   ```bash
   # Test MuJoCo directly
   python -c "import mujoco; print('MuJoCo working')"
   ```

#### Issue: Camera feeds show "Camera Not Connected"

**Symptoms:**
- Camera areas show red "CAMERA NOT CONNECTED" message
- Cameras are enabled in GUI

**Solutions:**
1. **Check debug output**:
   ```
   Look at Status & Monitor tab for camera debugging info
   Should show "Available cameras in data: ['cam_d405_rgb', ...]"
   ```

2. **Restart with cameras**:
   ```
   Stop simulation
   Ensure "Enable Cameras" is checked
   Start simulation again
   ```

3. **Verify stretch_mujoco camera support**:
   ```python
   from stretch_mujoco import StretchMujocoSimulator
   from stretch_mujoco.enums.stretch_cameras import StretchCameras
   
   sim = StretchMujocoSimulator(cameras_to_use=StretchCameras.rgb())
   sim.start()
   # Check if this works without errors
   ```

### Performance Optimization

#### Issue: High CPU usage

**Solutions:**
1. **Reduce update rates**:
   ```
   Set Camera FPS to 1-2
   The status update thread runs at 10Hz (cannot be changed easily)
   ```

2. **Use headless mode**:
   ```
   ✗ Uncheck "Enable Mujoco 3D Viewer"
   This reduces rendering overhead
   ```

#### Issue: High memory usage

**Solutions:**
1. **Monitor memory**:
   ```bash
   top -p $(pgrep -f stretch_dual_gui)
   # Should use < 1GB typically
   ```

2. **Camera memory leaks**:
   ```
   If memory keeps increasing, there may be a camera buffer leak
   Restart simulation periodically for long runs
   ```

### Development and Debugging

#### Issue: Need to modify simulation parameters

**File locations:**
```
Main GUI: stretch_dual_gui.py
Camera settings: Lines 860+ (update_camera_display method)
Performance settings: Lines 60+ (GUI options)
```

#### Issue: Adding custom features

**Extension points:**
```python
# Add new controls in setup_control_tab method
# Add new status displays in setup_status_tab method  
# Modify camera handling in get_camera_image method
```

## Getting Help

### Debug Information to Collect

When reporting issues, include:

1. **System info**:
   ```bash
   python --version
   pip list | grep -E "(stretch|mujoco|opencv|PIL)"
   uname -a
   ```

2. **Error messages**:
   ```
   Full error tracebacks
   Messages from Status & Monitor tab
   Console output when running python stretch_dual_gui.py
   ```

3. **Performance metrics**:
   ```
   Simulation speed (e.g., "0.043x real-time")
   System resource usage (CPU, RAM, GPU)
   Camera settings used
   ```

### Support Channels

- **stretch_mujoco issues**: Hello Robot official support
- **GUI-specific issues**: This repository's issue tracker
- **Installation problems**: Hello Robot community forums

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Slow simulation | Enable "Fast Mode" |
| No keyboard control | Click GUI window to focus |
| No MuJoCo viewer | Check graphics drivers |
| Camera not working | Restart with cameras enabled |
| High CPU usage | Reduce Camera FPS to 1-2 |
| Import errors | Check stretch_mujoco installation |

---

If none of these solutions work, consider using Fast Mode for maximum compatibility and performance.
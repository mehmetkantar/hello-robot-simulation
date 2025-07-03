# 🚀 How to Run Hello Robot Stretch 3 Simulation

## **Option 1: One-Click Launch (Recommended)**

```bash
cd ~/Desktop/hello-robot
./start_stretch_simulation.sh
```

This single command will:
1. ✅ Check prerequisites
2. 📦 Install all dependencies  
3. 🔨 Build the workspace
4. 🚀 Launch the simulation

## **Option 2: Step-by-Step**

### 1. Check System
```bash
cd ~/Desktop/hello-robot
./check_system.sh
```

### 2. Install Dependencies
```bash
./install_dependencies.sh
```

### 3. Build Workspace
```bash
./build_workspace.sh
```

### 4. Run Simulation
```bash
./run_simulation.sh
```

## **What Will Happen**

When you run the simulation, three windows will open:

### 🏗️ **Gazebo Window**
- Physics simulation environment
- 3D robot model that moves realistically
- You'll see the Stretch 3 robot in an empty world

### 👁️ **RViz Window** 
- Visualization and control interface
- **Motion Planning panel** on the left
- Interactive markers to drag and set goals

### 💻 **Terminal**
- Status messages and logs
- Keep this open (don't close it)

## **How to Control the Robot**

### **In RViz Motion Planning Panel:**

1. **Select Planning Group**:
   - Click dropdown, choose "**manipulator**"

2. **Set Goal Position**:
   - Drag the **orange interactive markers** 
   - Position them where you want the robot to go

3. **Plan Motion**:
   - Click "**Plan**" button
   - You'll see a preview of the trajectory

4. **Execute Motion**:
   - Click "**Execute**" button  
   - Watch the robot move in Gazebo!

### **Available Planning Groups**:
- `manipulator` - Complete arm (most useful)
- `arm` - Telescoping arm only
- `wrist` - Wrist joints only
- `gripper` - Gripper fingers
- `head` - Camera head
- `mobile_base` - Wheels

## **Example Motions to Try**

1. **Lift the Robot**:
   - Group: `manipulator`
   - Drag markers upward
   - Plan & Execute

2. **Extend the Arm**:
   - Group: `arm` 
   - Drag markers forward
   - Plan & Execute

3. **Move the Head**:
   - Group: `head`
   - Drag head markers to look around
   - Plan & Execute

## **Troubleshooting**

### ❌ **"colcon: command not found"**
```bash
sudo apt install python3-colcon-common-extensions
```

### ❌ **Build errors**
```bash
# Clean and rebuild
rm -rf stretch_ws/build stretch_ws/install
./build_workspace.sh
```

### ❌ **Robot not appearing in Gazebo**
```bash
# Check if everything is installed
./check_system.sh
```

### ❌ **RViz crashes or slow performance**
- Close other applications
- Your system has 10.5GB RAM (minimum is 8GB)
- Consider closing browser tabs

### ❌ **Motion planning fails**
- Try smaller motions
- Check that goal position is reachable
- Make sure no red collision indicators

## **Stopping the Simulation**

- **Press `Ctrl+C`** in the terminal
- Or close the Gazebo/RViz windows

## **Next Steps**

Once the simulation is working:

1. **Try the Python API**:
   ```bash
   # In a new terminal
   cd ~/Desktop/hello-robot/stretch_ws
   source install/setup.bash
   python3 src/stretch_moveit_config/examples/stretch_example.py
   ```

2. **Explore the packages**:
   - Look at `stretch_ws/src/stretch_moveit_config/`
   - Modify configurations in `config/` folder

3. **Read the full documentation**:
   - Open `README.md` for complete details

## **System Requirements Met ✅**

- ✅ Ubuntu 22.04
- ✅ ROS2 Humble  
- ✅ Python 3.10
- ✅ 10.5GB RAM (sufficient for basic use)
- ✅ All packages present

**You're ready to go! 🤖✨**
# 🤖 Hello Robot Stretch 3 - Joint Movement Guide

## 📋 Correct Joint Behaviors

### ✅ **Lift System** (Vertical Movement)
- **joint_lift**: Moves the entire arm assembly UP/DOWN along the mast
- Range: 0 to 1.1 meters
- This is the main vertical positioning

### ✅ **Telescoping Arm** (Horizontal Extension)
- **joint_arm_l0**: First telescoping segment (closest to mast)
- **joint_arm_l1**: Second telescoping segment  
- **joint_arm_l2**: Third telescoping segment
- **joint_arm_l3**: Fourth telescoping segment (furthest from mast)
- These extend the arm **horizontally** away from the robot

### ✅ **Wrist System** (End-effector Orientation)
- **joint_wrist_yaw**: Rotates wrist left/right
- **joint_wrist_pitch**: Tilts wrist up/down  
- **joint_wrist_roll**: Rolls wrist clockwise/counterclockwise

### ✅ **Gripper** (Grasping)
- **joint_gripper_finger_left**: Left finger open/close
- **joint_gripper_finger_right**: Right finger open/close

### ✅ **Head System** (Camera Positioning)
- **joint_head_pan**: Turn head left/right
- **joint_head_tilt**: Tilt head up/down

### ✅ **Wheels** (Mobility - Visual Only in RViz)
- **joint_left_wheel**: Left wheel rotation
- **joint_right_wheel**: Right wheel rotation
- **Note**: In RViz, wheels spin in place. For actual robot movement, you need navigation commands.

## 🎯 How Stretch Robot Actually Works

### **The telescoping arm extends HORIZONTALLY, not vertically!**

1. **joint_lift** = Move the whole arm up/down the mast
2. **joint_arm_l0-l3** = Extend the arm forward (away from the robot)
3. **joint_wrist_*** = Orient the end-effector
4. **joint_gripper_*** = Open/close gripper

### **Expected Movement Pattern:**
```
🏠 Base (stationary)
🔺 Mast (vertical post)
🔵 Lift (slides up/down mast) ← joint_lift
➡️ Arm segments (telescope horizontally) ← joint_arm_l0-l3  
🎯 Wrist (3DOF orientation) ← joint_wrist_***
✋ Gripper (open/close) ← joint_gripper_***
```

## 🐛 If You're Seeing Issues:

### **Issue**: "Arm rotating around mast instead of extending"
**Solution**: This might be a coordinate frame issue. The arm should extend horizontally when you increase joint_arm_l0-l3 values.

### **Issue**: "Wheels don't move the robot"  
**Solution**: This is NORMAL in RViz! RViz shows the robot model, not physics simulation. Wheels spin in place.

### **Issue**: "Robot looks wrong"
**Solution**: Try these joint values for a typical pose:
- joint_lift: 0.5 (middle height)
- joint_arm_l0: 0.1 (extend first segment)
- joint_arm_l1: 0.05 (extend second segment)
- joint_wrist_yaw: 0.0 (straight)

## 🔧 Testing Correct Movement:

1. **Start with all joints at 0**
2. **Increase joint_lift** → Should move arm assembly up the mast
3. **Increase joint_arm_l0** → Should extend first arm segment horizontally
4. **Increase joint_arm_l1-l3** → Should extend more arm segments
5. **Move wrist joints** → Should change end-effector orientation

If the arm is extending vertically instead of horizontally, there may be a coordinate frame issue in the URDF.
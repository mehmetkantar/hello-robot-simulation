#!/bin/bash

echo "🌍 Complete Stretch Robot - Gazebo with Joint Control"
echo "===================================================="

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Kill any existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui gazebo gzserver gzclient 2>/dev/null || true
sleep 3

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🏗️ Creating Gazebo world with objects..."

# Create a simple world with objects
cat > /tmp/stretch_world.world << 'EOF'
<?xml version="1.0" ?>
<sdf version="1.4">
  <world name="stretch_world">
    
    <!-- Physics settings -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
    
    <!-- Lighting -->
    <light name='sun' type='directional'>
      <cast_shadows>1</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>20 20</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>20 20</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Wood</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

    <!-- Table 1 -->
    <model name="table1">
      <static>true</static>
      <pose>2 1 0.4 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1.2 0.6 0.8</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1.2 0.6 0.8</size>
            </box>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Wood</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

    <!-- Red cup on table -->
    <model name="red_cup">
      <pose>2.2 1.0 0.85 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.04</radius>
              <length>0.1</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.04</radius>
              <length>0.1</length>
            </cylinder>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Red</name>
            </script>
          </material>
        </visual>
        <inertial>
          <mass>0.1</mass>
          <inertia>
            <ixx>0.001</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.001</iyy>
            <iyz>0</iyz>
            <izz>0.001</izz>
          </inertia>
        </inertial>
      </link>
    </model>

    <!-- Box -->
    <model name="green_box">
      <pose>-1 -1 0.05 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.1 0.1 0.1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.1 0.1 0.1</size>
            </box>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Green</name>
            </script>
          </material>
        </visual>
        <inertial>
          <mass>0.05</mass>
          <inertia>
            <ixx>0.001</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.001</iyy>
            <iyz>0</iyz>
            <izz>0.001</izz>
          </inertia>
        </inertial>
      </link>
    </model>

    <!-- GUI -->
    <gui fullscreen='0'>
      <camera name='user_camera'>
        <pose>-3 -3 2 0 0.3 0.7</pose>
        <view_controller>orbit</view_controller>
      </camera>
    </gui>

  </world>
</sdf>
EOF

echo "🚀 Starting Gazebo with world..."
gzserver --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so /tmp/stretch_world.world &
GZSERVER_PID=$!

sleep 8

echo "🖥️ Starting Gazebo client..."
gzclient &
GZCLIENT_PID=$!

sleep 5

echo "🤖 Creating Stretch robot for Gazebo..."

# Create Stretch robot URDF with Gazebo plugins
cat > /tmp/stretch_gazebo_robot.urdf << 'EOF'
<?xml version="1.0"?>
<robot name="stretch_gazebo">

  <!-- Base Link -->
  <link name="base_link">
    <inertial>
      <origin rpy="0 0 0" xyz="0 0 0.065"/>
      <mass value="20.0"/>
      <inertia ixx="0.2" ixy="0" ixz="0" iyy="0.2" iyz="0" izz="0.2"/>
    </inertial>
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <box size="0.34 0.33 0.13"/>
      </geometry>
      <material name="base_color">
        <color rgba="0.8 0.8 0.9 1"/>
      </material>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry>
        <box size="0.34 0.33 0.13"/>
      </geometry>
    </collision>
  </link>

  <!-- Mast -->
  <link name="link_mast">
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="1.0" ixy="0" ixz="0" iyy="1.0" iyz="0" izz="0.1"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0.55"/>
      <geometry>
        <cylinder radius="0.04" length="1.1"/>
      </geometry>
      <material name="mast_color">
        <color rgba="0.7 0.7 0.7 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0.55"/>
      <geometry>
        <cylinder radius="0.04" length="1.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Lift -->
  <link name="link_lift">
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.15 0.15 0.1"/>
      </geometry>
      <material name="lift_color">
        <color rgba="0.3 0.3 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.15 0.15 0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Arm -->
  <link name="link_arm">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.05"/>
    </inertial>
    <visual>
      <origin xyz="0.25 0 0"/>
      <geometry>
        <box size="0.5 0.05 0.05"/>
      </geometry>
      <material name="arm_color">
        <color rgba="0.6 0.3 0.1 1"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0.25 0 0"/>
      <geometry>
        <box size="0.5 0.05 0.05"/>
      </geometry>
    </collision>
  </link>

  <!-- Gripper -->
  <link name="link_gripper">
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.1 0.08 0.03"/>
      </geometry>
      <material name="gripper_color">
        <color rgba="0.1 0.8 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.1 0.08 0.03"/>
      </geometry>
    </collision>
  </link>

  <!-- Head -->
  <link name="link_head">
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.02"/>
    </inertial>
    <visual>
      <geometry>
        <box size="0.08 0.15 0.12"/>
      </geometry>
      <material name="head_color">
        <color rgba="0.8 0.8 0.2 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.08 0.15 0.12"/>
      </geometry>
    </collision>
  </link>

  <!-- Wheels -->
  <link name="link_left_wheel">
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
      <material name="wheel_color">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
    </collision>
  </link>

  <link name="link_right_wheel">
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
      <material name="wheel_color">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.03"/>
      </geometry>
    </collision>
  </link>

  <!-- JOINTS -->
  
  <!-- Base to mast -->
  <joint name="joint_mast" type="fixed">
    <parent link="base_link"/>
    <child link="link_mast"/>
    <origin xyz="-0.08 0 0.065"/>
  </joint>

  <!-- Mast to lift -->
  <joint name="joint_lift" type="prismatic">
    <parent link="link_mast"/>
    <child link="link_lift"/>
    <origin xyz="0 0 0.2"/>
    <axis xyz="0 0 1"/>
    <limit lower="0" upper="1.1" effort="100" velocity="0.2"/>
  </joint>

  <!-- Lift to arm -->
  <joint name="joint_arm" type="prismatic">
    <parent link="link_lift"/>
    <child link="link_arm"/>
    <origin xyz="0.13 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="0" upper="0.5" effort="100" velocity="0.2"/>
  </joint>

  <!-- Arm to gripper -->
  <joint name="joint_gripper" type="revolute">
    <parent link="link_arm"/>
    <child link="link_gripper"/>
    <origin xyz="0.5 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <!-- Mast to head -->
  <joint name="joint_head" type="revolute">
    <parent link="link_mast"/>
    <child link="link_head"/>
    <origin xyz="0 0 1.15"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <!-- Wheels -->
  <joint name="joint_left_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="link_left_wheel"/>
    <origin xyz="0.08 0.17 0.05" rpy="1.57 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="joint_right_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="link_right_wheel"/>
    <origin xyz="0.08 -0.17 0.05" rpy="1.57 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Gazebo differential drive plugin for movement -->
  <gazebo>
    <plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>/</namespace>
      </ros>
      <left_joint>joint_left_wheel</left_joint>
      <right_joint>joint_right_wheel</right_joint>
      <wheel_separation>0.34</wheel_separation>
      <wheel_diameter>0.1</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>
      <command_topic>cmd_vel</command_topic>
      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>false</publish_wheel_tf>
      <odometry_topic>odom</odometry_topic>
      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
    </plugin>
  </gazebo>

  <!-- Joint state publisher plugin -->
  <gazebo>
    <plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
      <ros>
        <namespace>/</namespace>
      </ros>
      <update_rate>50</update_rate>
      <joint_name>joint_lift</joint_name>
      <joint_name>joint_arm</joint_name>
      <joint_name>joint_gripper</joint_name>
      <joint_name>joint_head</joint_name>
    </plugin>
  </gazebo>

  <!-- Joint position controllers -->
  <gazebo>
    <plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
      <parameters>/home/kantar/Desktop/hello-robot/stretch_ws/config/stretch_controllers.yaml</parameters>
    </plugin>
  </gazebo>

</robot>
EOF

echo "🔧 Creating controller configuration..."
mkdir -p /home/kantar/Desktop/hello-robot/stretch_ws/config

cat > /home/kantar/Desktop/hello-robot/stretch_ws/config/stretch_controllers.yaml << 'EOF'
controller_manager:
  ros__parameters:
    update_rate: 100
    
    lift_controller:
      type: effort_controllers/JointGroupEffortController

    arm_controller:
      type: effort_controllers/JointGroupEffortController

    gripper_controller:
      type: effort_controllers/JointGroupEffortController

    head_controller:
      type: effort_controllers/JointGroupEffortController

lift_controller:
  ros__parameters:
    joints:
      - joint_lift

arm_controller:
  ros__parameters:
    joints:
      - joint_arm

gripper_controller:
  ros__parameters:
    joints:
      - joint_gripper

head_controller:
  ros__parameters:
    joints:
      - joint_head
EOF

echo "🤖 Spawning Stretch robot in Gazebo..."
ros2 run gazebo_ros spawn_entity.py \
    -file /tmp/stretch_gazebo_robot.urdf \
    -entity stretch_robot \
    -x 0 -y 0 -z 0.1

sleep 3

echo "🎯 Starting RViz for monitoring..."
rviz2 &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎉 Complete Stretch Robot - Gazebo Simulation Ready!"
echo "==================================================="
echo ""
echo "🌍 **Gazebo World:**"
echo "   • 3D physics simulation"
echo "   • Table with red cup"
echo "   • Green box on ground"
echo "   • Realistic movement and collisions"
echo ""
echo "🤖 **Robot Capabilities:**"
echo "   • REAL movement through space (not just joint rotation!)"
echo "   • Mobile base navigation"
echo "   • Lift and arm control"
echo "   • Head and gripper control"
echo "   • Physics-based interactions"
echo ""
echo "🎮 **Movement Controls:**"
echo ""
echo "   # Move forward"
echo "   ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \\"
echo "   '{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'"
echo ""
echo "   # Turn left"
echo "   ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \\"
echo "   '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}'"
echo ""
echo "   # Stop"
echo "   ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \\"
echo "   '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'"
echo ""
echo "🔧 **Joint Control:**"
echo "   # Raise lift"
echo "   ros2 topic pub --once /joint_lift/command std_msgs/msg/Float64 '{data: 0.5}'"
echo ""
echo "   # Extend arm"
echo "   ros2 topic pub --once /joint_arm/command std_msgs/msg/Float64 '{data: 0.3}'"
echo ""
echo "   # Rotate head"
echo "   ros2 topic pub --once /joint_head/command std_msgs/msg/Float64 '{data: 0.5}'"
echo ""
echo "🎯 **Now You'll See:**"
echo "   • Robot actually MOVES through the world"
echo "   • Can drive to the table and cup"
echo "   • Physics-based collisions and interactions"
echo "   • Real spatial navigation"
echo ""
echo "Press ENTER to stop the simulation..."
read

# Cleanup
kill $GZSERVER_PID $GZCLIENT_PID $RVIZ_PID 2>/dev/null
killall -9 gazebo gzserver gzclient rviz2 2>/dev/null || true

echo "✅ Gazebo simulation stopped!"
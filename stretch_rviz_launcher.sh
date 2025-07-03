#!/bin/bash

echo "🤖 Hello Robot Stretch 3 - RViz Launcher"
echo "========================================"
echo "Interactive launcher with world selection"

# Apply VM fixes
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

# Clean up any existing processes
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui gazebo gzserver gzclient 2>/dev/null || true
sleep 2

# Functions to create world-specific RViz configs
create_office_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.3
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Name: Office_Floor
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Office_Furniture
      Topic:
        Value: /office_markers
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Desks_and_Chairs
      Topic:
        Value: /furniture_markers
      Value: true
  Global Options:
    Background Color: 245; 245; 245
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3
      Focal Point:
        X: 1
        Y: 0
        Z: 0.5
      Name: Office_View
      Pitch: 0.7
      Target Frame: <Fixed Frame>
      Yaw: 0.785
    Saved: ~
EOF
}

create_warehouse_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.5
      Cell Size: 2
      Class: rviz_default_plugins/Grid
      Color: 100; 100; 120
      Enabled: true
      Name: Warehouse_Floor
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Shelving_Units
      Topic:
        Value: /warehouse_markers
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Pallets_and_Boxes
      Topic:
        Value: /cargo_markers
      Value: true
  Global Options:
    Background Color: 60; 60; 80
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 5
      Focal Point:
        X: 2
        Y: 0
        Z: 1
      Name: Warehouse_View
      Pitch: 0.5
      Target Frame: <Fixed Frame>
      Yaw: 0
    Saved: ~
EOF
}

create_kitchen_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.4
      Cell Size: 0.5
      Class: rviz_default_plugins/Grid
      Color: 200; 180; 160
      Enabled: true
      Name: Kitchen_Floor
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Kitchen_Cabinets
      Topic:
        Value: /kitchen_markers
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Appliances
      Topic:
        Value: /appliance_markers
      Value: true
  Global Options:
    Background Color: 250; 240; 230
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 2.5
      Focal Point:
        X: 0.5
        Y: 0
        Z: 0.8
      Name: Kitchen_View
      Pitch: 0.6
      Target Frame: <Fixed Frame>
      Yaw: 1.57
    Saved: ~
EOF
}

create_lab_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.6
      Cell Size: 0.25
      Class: rviz_default_plugins/Grid
      Color: 180; 180; 200
      Enabled: true
      Name: Lab_Floor
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Lab_Equipment
      Topic:
        Value: /lab_markers
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Sample_Stations
      Topic:
        Value: /station_markers
      Value: true
  Global Options:
    Background Color: 240; 240; 250
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 2
      Focal Point:
        X: 0
        Y: 0
        Z: 0.5
      Name: Lab_View
      Pitch: 0.8
      Target Frame: <Fixed Frame>
      Yaw: 0
    Saved: ~
EOF
}

create_garden_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.3
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 120; 160; 100
      Enabled: true
      Name: Garden_Ground
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Plants_and_Trees
      Topic:
        Value: /garden_markers
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Garden_Features
      Topic:
        Value: /feature_markers
      Value: true
  Global Options:
    Background Color: 135; 206; 235
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 4
      Focal Point:
        X: 1
        Y: 1
        Z: 0
      Name: Garden_View
      Pitch: 0.4
      Target Frame: <Fixed Frame>
      Yaw: 2.35
    Saved: ~
EOF
}

create_grid_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.8
      Cell Size: 0.5
      Class: rviz_default_plugins/Grid
      Color: 0; 0; 255
      Enabled: true
      Name: Navigation_Grid
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Grid_Obstacles
      Topic:
        Value: /grid_markers
      Value: true
  Global Options:
    Background Color: 248; 248; 255
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3
      Focal Point:
        X: 0
        Y: 0
        Z: 0
      Name: Grid_View
      Pitch: 1.57
      Target Frame: <Fixed Frame>
      Yaw: 0
    Saved: ~
EOF
}

create_target_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.4
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 255; 200; 0
      Enabled: true
      Name: Range_Floor
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Target_Objects
      Topic:
        Value: /target_markers
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Practice_Items
      Topic:
        Value: /practice_markers
      Value: true
  Global Options:
    Background Color: 255; 248; 220
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3
      Focal Point:
        X: 2
        Y: 0
        Z: 0.5
      Name: Range_View
      Pitch: 0.3
      Target Frame: <Fixed Frame>
      Yaw: 0
    Saved: ~
EOF
}

create_garage_world() {
    cat > "$WORLD_FILE" << 'EOF'
Panels:
  - Class: rviz_common/Displays
    Name: Displays
Visualization Manager:
  Displays:
    - Alpha: 0.5
      Cell Size: 1
      Class: rviz_default_plugins/Grid
      Color: 128; 128; 128
      Enabled: true
      Name: Garage_Floor
      Plane: XY
      Reference Frame: <Fixed Frame>
      Value: true
    - Alpha: 1
      Class: rviz_default_plugins/RobotModel
      Description Source: Topic
      Description Topic:
        Value: /robot_description
      Enabled: true
      Name: Stretch_Robot
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Tools_and_Equipment
      Topic:
        Value: /garage_markers
      Value: true
    - Class: rviz_default_plugins/MarkerArray
      Enabled: true
      Name: Workbenches
      Topic:
        Value: /workbench_markers
      Value: true
  Global Options:
    Background Color: 64; 64; 64
    Fixed Frame: base_link
    Frame Rate: 30
  Name: root
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 4
      Focal Point:
        X: 1
        Y: 0
        Z: 1
      Name: Garage_View
      Pitch: 0.5
      Target Frame: <Fixed Frame>
      Yaw: 0.5
    Saved: ~
EOF
}

# World selection menu
echo ""
echo "🌍 Select Environment:"
echo "======================"
echo "1. 🏠 Indoor Office Environment"
echo "2. 🏭 Warehouse/Factory Floor" 
echo "3. 🏡 Home Kitchen Environment"
echo "4. 🧪 Laboratory Setup"
echo "5. 🌳 Outdoor Garden/Patio"
echo "6. 📦 Simple Grid World"
echo "7. 🎯 Target Practice Range"
echo "8. 🚗 Garage/Workshop"
echo ""
read -p "Choose environment (1-8): " WORLD_CHOICE

# Create world-specific RViz configurations
case $WORLD_CHOICE in
    1)
        WORLD_NAME="Office Environment"
        WORLD_FILE="/tmp/office_world.rviz"
        create_office_world
        ;;
    2)
        WORLD_NAME="Warehouse"
        WORLD_FILE="/tmp/warehouse_world.rviz"
        create_warehouse_world
        ;;
    3)
        WORLD_NAME="Kitchen"
        WORLD_FILE="/tmp/kitchen_world.rviz"
        create_kitchen_world
        ;;
    4)
        WORLD_NAME="Laboratory"
        WORLD_FILE="/tmp/lab_world.rviz"
        create_lab_world
        ;;
    5)
        WORLD_NAME="Garden"
        WORLD_FILE="/tmp/garden_world.rviz"
        create_garden_world
        ;;
    6)
        WORLD_NAME="Grid World"
        WORLD_FILE="/tmp/grid_world.rviz"
        create_grid_world
        ;;
    7)
        WORLD_NAME="Target Range"
        WORLD_FILE="/tmp/target_world.rviz"
        create_target_world
        ;;
    8)
        WORLD_NAME="Garage"
        WORLD_FILE="/tmp/garage_world.rviz"
        create_garage_world
        ;;
    *)
        echo "Invalid choice, using default office environment"
        WORLD_NAME="Office Environment"
        WORLD_FILE="/tmp/office_world.rviz"
        create_office_world
        ;;
esac

echo ""
echo "🚀 Launching Stretch Robot in $WORLD_NAME..."
echo "============================================="

# Navigate to workspace
cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

# Create launch file for robot
cat > /tmp/stretch_robot.launch.py << 'EOF'
#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Get the URDF file
    pkg_stretch_description = get_package_share_directory('stretch_description')
    urdf_file = os.path.join(pkg_stretch_description, 'stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf')
    
    # Read the URDF content
    with open(urdf_file, 'r') as infp:
        robot_description_content = infp.read()
    
    robot_description = {'robot_description': robot_description_content}

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Joint state publisher GUI
    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node
    ])
EOF

# Launch robot description
echo "🤖 Starting robot state publisher..."
ros2 launch /tmp/stretch_robot.launch.py &
ROBOT_PID=$!

sleep 3

# Create world markers based on selection
echo "🌍 Creating $WORLD_NAME environment markers..."
python3 -c "
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import MarkerArray, Marker
from geometry_msgs.msg import Point
import time

class WorldMarkerPublisher(Node):
    def __init__(self):
        super().__init__('world_marker_publisher')
        
        # Publishers for different marker topics
        self.office_pub = self.create_publisher(MarkerArray, '/office_markers', 10)
        self.furniture_pub = self.create_publisher(MarkerArray, '/furniture_markers', 10)
        self.warehouse_pub = self.create_publisher(MarkerArray, '/warehouse_markers', 10)
        self.cargo_pub = self.create_publisher(MarkerArray, '/cargo_markers', 10)
        self.kitchen_pub = self.create_publisher(MarkerArray, '/kitchen_markers', 10)
        self.appliance_pub = self.create_publisher(MarkerArray, '/appliance_markers', 10)
        self.lab_pub = self.create_publisher(MarkerArray, '/lab_markers', 10)
        self.station_pub = self.create_publisher(MarkerArray, '/station_markers', 10)
        self.garden_pub = self.create_publisher(MarkerArray, '/garden_markers', 10)
        self.feature_pub = self.create_publisher(MarkerArray, '/feature_markers', 10)
        self.grid_pub = self.create_publisher(MarkerArray, '/grid_markers', 10)
        self.target_pub = self.create_publisher(MarkerArray, '/target_markers', 10)
        self.practice_pub = self.create_publisher(MarkerArray, '/practice_markers', 10)
        self.garage_pub = self.create_publisher(MarkerArray, '/garage_markers', 10)
        self.workbench_pub = self.create_publisher(MarkerArray, '/workbench_markers', 10)
        
        self.timer = self.create_timer(1.0, self.publish_markers)
        self.world_choice = $WORLD_CHOICE

    def create_marker(self, id, x, y, z, sx, sy, sz, r, g, b, a=1.0, marker_type=Marker.CUBE):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'world_objects'
        marker.id = id
        marker.type = marker_type
        marker.action = Marker.ADD
        
        marker.pose.position.x = float(x)
        marker.pose.position.y = float(y)
        marker.pose.position.z = float(z)
        marker.pose.orientation.w = 1.0
        
        marker.scale.x = float(sx)
        marker.scale.y = float(sy)
        marker.scale.z = float(sz)
        
        marker.color.r = float(r)
        marker.color.g = float(g)
        marker.color.b = float(b)
        marker.color.a = float(a)
        
        return marker

    def publish_markers(self):
        if self.world_choice == 1:  # Office
            # Office furniture
            office_markers = MarkerArray()
            office_markers.markers.append(self.create_marker(0, 2.0, 1.0, 0.4, 1.5, 0.8, 0.8, 0.6, 0.3, 0.1))  # Desk
            office_markers.markers.append(self.create_marker(1, 2.0, -1.0, 0.4, 1.5, 0.8, 0.8, 0.6, 0.3, 0.1))  # Desk
            office_markers.markers.append(self.create_marker(2, -1.0, 1.5, 0.9, 0.4, 2.0, 1.8, 0.4, 0.2, 0.1))  # Bookshelf
            self.office_pub.publish(office_markers)
            
            # Chairs
            furniture_markers = MarkerArray()
            furniture_markers.markers.append(self.create_marker(0, 1.5, 1.0, 0.2, 0.5, 0.5, 0.4, 0.2, 0.2, 0.8))  # Chair
            furniture_markers.markers.append(self.create_marker(1, 1.5, -1.0, 0.2, 0.5, 0.5, 0.4, 0.2, 0.2, 0.8))  # Chair
            self.furniture_pub.publish(furniture_markers)
            
        elif self.world_choice == 2:  # Warehouse
            # Shelving units
            warehouse_markers = MarkerArray()
            for i in range(4):
                warehouse_markers.markers.append(self.create_marker(i, 3.0 + i*2, 2.0, 1.0, 1.0, 0.3, 2.0, 0.7, 0.4, 0.1))
                warehouse_markers.markers.append(self.create_marker(i+4, 3.0 + i*2, -2.0, 1.0, 1.0, 0.3, 2.0, 0.7, 0.4, 0.1))
            self.warehouse_pub.publish(warehouse_markers)
            
            # Pallets and boxes
            cargo_markers = MarkerArray()
            for i in range(6):
                cargo_markers.markers.append(self.create_marker(i, 1.0 + i*0.5, 0.0, 0.15, 0.4, 0.4, 0.3, 0.8, 0.6, 0.2))
            self.cargo_pub.publish(cargo_markers)
            
        elif self.world_choice == 3:  # Kitchen
            # Kitchen cabinets
            kitchen_markers = MarkerArray()
            kitchen_markers.markers.append(self.create_marker(0, 1.5, 1.5, 0.45, 2.0, 0.6, 0.9, 0.8, 0.6, 0.4))  # Counter
            kitchen_markers.markers.append(self.create_marker(1, 1.5, 1.5, 1.2, 2.0, 0.4, 0.6, 0.6, 0.4, 0.2))  # Upper cabinets
            kitchen_markers.markers.append(self.create_marker(2, -0.5, 1.5, 0.45, 1.0, 0.6, 0.9, 0.8, 0.6, 0.4))  # Island
            self.kitchen_pub.publish(kitchen_markers)
            
            # Appliances
            appliance_markers = MarkerArray()
            appliance_markers.markers.append(self.create_marker(0, 0.5, 1.2, 0.5, 0.6, 0.6, 1.0, 0.9, 0.9, 0.9))  # Refrigerator
            appliance_markers.markers.append(self.create_marker(1, 1.8, 1.2, 0.2, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3))  # Microwave
            self.appliance_pub.publish(appliance_markers)
            
        elif self.world_choice == 4:  # Laboratory
            # Lab equipment
            lab_markers = MarkerArray()
            lab_markers.markers.append(self.create_marker(0, 1.0, 1.0, 0.4, 1.5, 0.8, 0.8, 0.9, 0.9, 0.9))  # Lab bench
            lab_markers.markers.append(self.create_marker(1, 1.0, -1.0, 0.4, 1.5, 0.8, 0.8, 0.9, 0.9, 0.9))  # Lab bench
            lab_markers.markers.append(self.create_marker(2, -0.5, 0.0, 0.8, 0.6, 0.6, 1.6, 0.8, 0.8, 0.8))  # Equipment rack
            self.lab_pub.publish(lab_markers)
            
            # Sample stations
            station_markers = MarkerArray()
            for i in range(3):
                station_markers.markers.append(self.create_marker(i, 1.0 + i*0.3, 0.8, 0.05, 0.2, 0.2, 0.1, 0.1, 0.8, 0.1))
            self.station_pub.publish(station_markers)
            
        elif self.world_choice == 5:  # Garden
            # Plants and trees
            garden_markers = MarkerArray()
            garden_markers.markers.append(self.create_marker(0, 2.0, 2.0, 1.0, 0.5, 0.5, 2.0, 0.4, 0.8, 0.2, 1.0, Marker.CYLINDER))  # Tree
            garden_markers.markers.append(self.create_marker(1, -1.0, 1.5, 0.3, 0.8, 0.8, 0.6, 0.2, 0.6, 0.1))  # Bush
            garden_markers.markers.append(self.create_marker(2, 1.5, -1.0, 0.2, 1.0, 0.5, 0.4, 0.8, 0.4, 0.2))  # Flower bed
            self.garden_pub.publish(garden_markers)
            
            # Garden features
            feature_markers = MarkerArray()
            feature_markers.markers.append(self.create_marker(0, 0.0, 2.0, 0.2, 0.8, 0.8, 0.4, 0.6, 0.6, 0.6))  # Garden table
            self.feature_pub.publish(feature_markers)
            
        elif self.world_choice == 6:  # Grid world
            # Grid obstacles
            grid_markers = MarkerArray()
            obstacles = [(1,1), (2,0), (0,2), (3,1), (1,3), (2,2)]
            for i, (x, y) in enumerate(obstacles):
                grid_markers.markers.append(self.create_marker(i, x*0.5, y*0.5, 0.25, 0.4, 0.4, 0.5, 0.8, 0.2, 0.2))
            self.grid_pub.publish(grid_markers)
            
        elif self.world_choice == 7:  # Target range
            # Target objects
            target_markers = MarkerArray()
            target_markers.markers.append(self.create_marker(0, 2.0, 0.0, 0.5, 0.3, 0.05, 1.0, 1.0, 0.0, 0.0, 1.0, Marker.CYLINDER))  # Target
            target_markers.markers.append(self.create_marker(1, 2.5, 1.0, 0.3, 0.2, 0.2, 0.6, 0.0, 1.0, 0.0))  # Practice object
            target_markers.markers.append(self.create_marker(2, 2.5, -1.0, 0.3, 0.2, 0.2, 0.6, 0.0, 0.0, 1.0))  # Practice object
            self.target_pub.publish(target_markers)
            
            # Practice items
            practice_markers = MarkerArray()
            for i in range(5):
                practice_markers.markers.append(self.create_marker(i, 1.0 + i*0.3, 0.5, 0.1, 0.1, 0.1, 0.2, 1.0, 1.0, 0.0))
            self.practice_pub.publish(practice_markers)
            
        elif self.world_choice == 8:  # Garage
            # Tools and equipment
            garage_markers = MarkerArray()
            garage_markers.markers.append(self.create_marker(0, 2.0, 1.5, 0.4, 1.0, 0.5, 0.8, 0.6, 0.6, 0.6))  # Workbench
            garage_markers.markers.append(self.create_marker(1, -1.0, 1.0, 0.8, 0.3, 0.3, 1.6, 0.4, 0.4, 0.4))  # Tool cabinet
            garage_markers.markers.append(self.create_marker(2, 1.0, -1.5, 0.3, 1.5, 0.8, 0.6, 0.3, 0.3, 0.8))  # Car (partial)
            self.garage_pub.publish(garage_markers)
            
            # Workbenches
            workbench_markers = MarkerArray()
            for i in range(3):
                workbench_markers.markers.append(self.create_marker(i, 1.8 + i*0.2, 1.3, 0.05, 0.15, 0.1, 0.1, 0.8, 0.8, 0.2))
            self.workbench_pub.publish(workbench_markers)

def main():
    rclpy.init()
    node = WorldMarkerPublisher()
    try:
        rclpy.spin_once(node, timeout_sec=2.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
" &
MARKER_PID=$!

sleep 2

# Launch RViz with the selected world
echo "🎯 Starting RViz with $WORLD_NAME environment..."
rviz2 -d "$WORLD_FILE" &
RVIZ_PID=$!

sleep 3

echo ""
echo "🎉 Hello Robot Stretch 3 - $WORLD_NAME Environment"
echo "=================================================="
echo ""
echo "🎮 Controls Available:"
echo "   • Joint State Publisher GUI - Move robot joints with sliders"
echo "   • RViz - Visualize robot and environment"
echo "   • Mouse controls in RViz:"
echo "     - Left click + drag: Rotate view"
echo "     - Middle click + drag: Pan view"
echo "     - Scroll wheel: Zoom in/out"
echo ""
echo "🌍 Environment Features:"
case $WORLD_CHOICE in
    1) echo "   • Office desks and chairs"
       echo "   • Bookshelf for navigation practice"
       echo "   • Realistic office lighting" ;;
    2) echo "   • Warehouse shelving units"
       echo "   • Pallets and cargo boxes"
       echo "   • Industrial environment" ;;
    3) echo "   • Kitchen counters and cabinets"
       echo "   • Appliances (fridge, microwave)"
       echo "   • Home environment simulation" ;;
    4) echo "   • Laboratory benches and equipment"
       echo "   • Sample stations for manipulation"
       echo "   • Scientific environment" ;;
    5) echo "   • Garden plants and trees"
       echo "   • Outdoor furniture"
       echo "   • Natural environment" ;;
    6) echo "   • Grid-based obstacles"
       echo "   • Navigation planning practice"
       echo "   • Algorithm testing environment" ;;
    7) echo "   • Target objects for manipulation"
       echo "   • Practice items for grasping"
       echo "   • Skill development setup" ;;
    8) echo "   • Workshop tools and equipment"
       echo "   • Workbenches and storage"
       echo "   • Garage/shop environment" ;;
esac
echo ""
echo "🤖 Robot Capabilities in this Environment:"
echo "   • Full 7-DOF arm manipulation"
echo "   • Mobile base navigation"
echo "   • Head camera positioning"
echo "   • Gripper control"
echo "   • Sensor visualization"
echo ""
echo "Press ENTER to stop the simulation..."
read

# Cleanup
echo "🛑 Shutting down simulation..."
kill $ROBOT_PID $MARKER_PID $RVIZ_PID 2>/dev/null
killall -9 rviz2 robot_state_publisher joint_state_publisher_gui python3 2>/dev/null || true

echo "✅ Simulation stopped. Thank you for using Hello Robot Stretch 3!"
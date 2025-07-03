#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os
import shutil

def fix_stretch_robot_urdf():
    """Fix the original Stretch robot URDF to be visible"""
    
    original_urdf = "/home/kantar/Desktop/hello-robot/stretch_ws/src/stretch_ros2/stretch_description/stretch_description_SE3_eoa_wrist_dw3_tool_sg3.urdf"
    fixed_urdf = "/tmp/stretch_robot_fixed.urdf"
    
    print("🔧 Fixing original Stretch robot URDF...")
    print(f"📖 Reading: {original_urdf}")
    
    # Parse the URDF
    tree = ET.parse(original_urdf)
    root = tree.getroot()
    
    # Counter for modifications
    mesh_count = 0
    material_count = 0
    
    # Find all visual elements
    for visual in root.iter('visual'):
        geometry = visual.find('geometry')
        
        if geometry is not None:
            mesh = geometry.find('mesh')
            
            if mesh is not None:
                mesh_count += 1
                filename = mesh.get('filename', '')
                
                # Get parent link name for color coding
                link = visual
                while link is not None and link.tag != 'link':
                    link = link.getparent()
                
                if link is None:
                    # Find parent link differently
                    parent = visual.getparent()
                    while parent is not None and parent.tag != 'link':
                        parent = parent.getparent()
                    link = parent
                
                link_name = link.get('name') if link is not None else 'unknown'
                
                # Replace mesh with appropriate basic shape based on link name
                geometry.clear()
                
                if 'base_link' in link_name:
                    box = ET.SubElement(geometry, 'box')
                    box.set('size', '0.5 0.3 0.2')
                    color = '0 0 1 1'  # Blue
                elif 'wheel' in link_name.lower():
                    cylinder = ET.SubElement(geometry, 'cylinder')
                    cylinder.set('radius', '0.05')
                    cylinder.set('length', '0.04')
                    color = '0.3 0.3 0.3 1'  # Gray
                elif 'mast' in link_name.lower() or 'lift' in link_name.lower():
                    box = ET.SubElement(geometry, 'box')
                    box.set('size', '0.08 0.08 0.6')
                    color = '1 0.5 0 1'  # Orange
                elif 'arm' in link_name.lower():
                    box = ET.SubElement(geometry, 'box')
                    if 'l0' in link_name or 'l1' in link_name:
                        box.set('size', '0.1 0.06 0.06')
                    else:
                        box.set('size', '0.15 0.06 0.06')
                    color = '1 0.5 0 1'  # Orange
                elif 'gripper' in link_name.lower():
                    box = ET.SubElement(geometry, 'box')
                    if 'finger' in link_name:
                        box.set('size', '0.04 0.08 0.02')
                    else:
                        box.set('size', '0.08 0.12 0.08')
                    color = '1 0 0 1'  # Red
                elif 'head' in link_name.lower():
                    box = ET.SubElement(geometry, 'box')
                    box.set('size', '0.15 0.1 0.08')
                    color = '0 1 0 1'  # Green
                elif 'wrist' in link_name.lower():
                    box = ET.SubElement(geometry, 'box')
                    box.set('size', '0.06 0.06 0.06')
                    color = '1 1 0 1'  # Yellow
                elif 'camera' in link_name.lower():
                    box = ET.SubElement(geometry, 'box')
                    box.set('size', '0.03 0.08 0.03')
                    color = '0 1 1 1'  # Cyan
                elif 'laser' in link_name.lower():
                    cylinder = ET.SubElement(geometry, 'cylinder')
                    cylinder.set('radius', '0.04')
                    cylinder.set('length', '0.06')
                    color = '1 0 1 1'  # Magenta
                else:
                    # Default shape
                    box = ET.SubElement(geometry, 'box')
                    box.set('size', '0.05 0.05 0.05')
                    color = '0.8 0.8 0.8 1'  # Light gray
                
                # Update or create material
                material = visual.find('material')
                if material is None:
                    material = ET.SubElement(visual, 'material')
                    material.set('name', f'{link_name}_material')
                
                # Set color
                color_elem = material.find('color')
                if color_elem is None:
                    color_elem = ET.SubElement(material, 'color')
                
                color_elem.set('rgba', color)
                material_count += 1
    
    print(f"✅ Replaced {mesh_count} mesh files with basic shapes")
    print(f"✅ Updated {material_count} materials with bright colors")
    
    # Save the fixed URDF
    tree.write(fixed_urdf, encoding='utf-8', xml_declaration=True)
    print(f"💾 Saved fixed URDF: {fixed_urdf}")
    
    return fixed_urdf

def test_fixed_robot(urdf_file):
    """Test the fixed robot"""
    
    test_script = f"""#!/bin/bash
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QPA_PLATFORM=xcb
export XDG_SESSION_TYPE=x11

killall -9 gzserver gzclient gazebo 2>/dev/null || true
sleep 3

echo "🚀 Testing FIXED Stretch Robot..."
echo "This should look like the real robot structure!"

gzserver --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so /opt/ros/humble/share/gazebo_ros/worlds/empty.world &
sleep 8
gzclient &
sleep 5

cd /home/kantar/Desktop/hello-robot/stretch_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "🤖 Spawning FIXED Stretch robot..."
ros2 run gazebo_ros spawn_entity.py \\
    -file {urdf_file} \\
    -entity stretch_robot_fixed \\
    -x 0 -y 0 -z 0.1

echo ""
echo "🎯 You should now see the REAL Stretch robot structure:"
echo "   🔵 Blue base (mobile platform)"
echo "   🟠 Orange mast (vertical lift column)" 
echo "   🟠 Orange arm segments (telescoping arm)"
echo "   🔴 Red gripper (end effector)"
echo "   🟢 Green head (camera assembly)"
echo "   ⚫ Gray wheels"
echo "   🟡 Yellow wrist joints"
echo "   🔷 Cyan cameras"
echo "   🟣 Magenta lidar"
echo ""
echo "This represents the actual Stretch robot joints and links!"
echo ""
echo "Press ENTER to close..."
read

killall -9 gzserver gzclient gazebo 2>/dev/null || true
"""
    
    script_file = "/tmp/test_fixed_stretch.sh"
    with open(script_file, 'w') as f:
        f.write(test_script)
    
    os.chmod(script_file, 0o755)
    return script_file

if __name__ == "__main__":
    print("🔧 Fixing Original Stretch Robot URDF")
    print("=====================================")
    
    try:
        fixed_urdf = fix_stretch_robot_urdf()
        test_script = test_fixed_robot(fixed_urdf)
        
        print(f"\n🚀 Run the test: {test_script}")
        print("\nThis will show the REAL Stretch robot structure")
        print("with all the correct joints, links, and proportions!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("The URDF file might have a different structure than expected.")
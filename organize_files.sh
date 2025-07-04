#!/bin/bash

echo "📁 Organizing Robot Project Files"
echo "================================="
echo ""

# Create archive directory
ARCHIVE_DIR="/home/kantar/Desktop/hello-robot/archived_files"
mkdir -p "$ARCHIVE_DIR"

echo "📦 Created archive directory: $ARCHIVE_DIR"
echo ""

# Define WORKING files that should stay (these are confirmed working)
WORKING_FILES=(
    "simple_gazebo_ui.sh"
    "choose_gazebo_mode.sh" 
    "robot_car_control.py"
    "robot_pick_place_control.py"
)

echo "✅ KEEPING working files:"
for file in "${WORKING_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ⚠️  $file (not found)"
    fi
done

echo ""

# Define files to archive (unused/experimental/debug files)
ARCHIVE_FILES=(
    # Debug and test scripts
    "debug_gazebo.sh"
    "debug_robot_spawn.sh" 
    "debug_robot_visibility.sh"
    "debug_simulation.sh"
    "test_complete_solution.sh"
    "test_final_gazebo.sh"
    "test_gazebo_only.sh"
    "test_gazebo_with_robot.sh"
    "test_minimal_gazebo.sh"
    "test_robot_only.sh"
    "test_robot_spawn.sh"
    "test_ros2_gazebo.sh"
    "test_simple_gazebo.sh"
    "test_stable_gazebo.sh"
    "test_pick_place_setup.sh"
    "test_rviz_objects.sh"
    "test_simple_rviz.sh"
    "verify_robot.sh"
    
    # Alternative/experimental controllers
    "complete_robot_control.py"
    "enhanced_stretch_controller.py"
    "gazebo_robot_controller.py"
    "minimal_robot_control.py"
    "simple_robot_controller.py"
    "simple_robot_control.py"
    "stable_robot_control.py"
    "working_robot.py"
    "custom_joint_control.py"
    "keyboard_drive.py"
    "multi_world_control.py"
    "simple_world_drive.py"
    "stable_world_control.py"
    "world_environments.py"
    "world_visualizer.py"
    "robot_car_control_stable.py"
    
    # Alternative launchers
    "launch_gazebo_ui.sh"
    "launch_gazebo_ui_safe.sh"
    "force_gazebo_ui.sh"
    "persistent_gazebo_ui.sh"
    "minimal_gazebo_ui.sh"
    "quick_ui.sh"
    "restart_gazebo_ui.sh"
    "launch_multi_world.sh"
    "launch_multi_world_rviz.sh"
    "launch_obstacle_world.sh"
    "launch_pick_place_world.sh"
    "launch_robot_guaranteed.sh"
    "launch_robot_system.sh"
    "launch_stable_simulation.sh"
    "launch_stable_simulation_fixed.sh"
    "launch_working_robot.sh"
    "manual_robot_launch.sh"
    "complete_stretch_gazebo.sh"
    "stretch_gazebo_complete.sh"
    "stretch_gazebo_world.sh"
    "working_robot_simulation.sh"
    "working_stretch_control.sh"
    
    # Setup and fix scripts
    "build_workspace.sh"
    "check_system.sh"
    "install_dependencies.sh"
    "run_simulation.sh"
    "start_stretch_simulation.sh"
    "setup_urdf_meshes.sh"
    "official_urdf_setup.sh"
    "execute_official_urdf.sh"
    
    # Control system scripts
    "car_control_system.sh"
    "clean_robot_control.sh"
    "enhanced_stretch_control.sh"
    "start_complete_control.sh"
    "start_robot_control.sh"
    "stop_robot_movement.sh"
    "standalone_custom_control.sh"
    "working_robot_control.sh"
    
    # Fix and visibility scripts
    "fix_gazebo_vm.sh"
    "fix_robot_display_proper.sh"
    "fix_rviz_robot.sh"
    "fix_world_visibility.sh"
    "simple_visibility_test.sh"
    
    # RViz scripts
    "exact_stretch_rviz.sh"
    "simplified_stretch_rviz.sh"
    "stretch_rviz_launcher.sh"
    "stretch_rviz_world.sh"
    
    # Python utilities
    "convert_and_test.py"
    "create_real_stretch.py"
    "create_visible_robot.py"
    "fix_robot_display.py"
    "fix_stretch_urdf.py"
    "test_gazebo_model.py"
    
    # Other test scripts
    "final_working_test.sh"
    "minimal_gazebo_test.sh"
    "simple_gazebo_test.sh"
    "simple_robot_test.sh"
    "test_fixed_robot.sh"
    "test_headless_gazebo.sh"
    "test_robot_empty_world.sh"
    "world_switcher.sh"
)

echo "📦 ARCHIVING unused/experimental files:"
archived_count=0
for file in "${ARCHIVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/"
        echo "   📦 $file → archived"
        ((archived_count++))
    fi
done

echo ""
echo "📊 ORGANIZATION SUMMARY:"
echo "   ✅ Working files kept: ${#WORKING_FILES[@]}"
echo "   📦 Files archived: $archived_count"
echo ""

echo "📁 MAIN DIRECTORY NOW CONTAINS:"
echo "================================"
ls -la *.py *.sh 2>/dev/null | grep -E "\.(py|sh)$" || echo "No .py or .sh files in main directory"

echo ""
echo "📦 ARCHIVED FILES LOCATION:"
echo "   $ARCHIVE_DIR"
echo ""

echo "🎯 CURRENT WORKING SETUP:"
echo "   1. Gazebo UI: ./simple_gazebo_ui.sh"
echo "   2. Mode selection: ./choose_gazebo_mode.sh"
echo "   3. Car control: python3 robot_car_control.py"
echo "   4. Pick & place: python3 robot_pick_place_control.py"
echo ""

echo "✅ Organization complete!"
echo "   All working files preserved"
echo "   Experimental files safely archived"
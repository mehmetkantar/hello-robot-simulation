#!/bin/bash

echo "🎮 Choose Your Gazebo Experience"
echo "================================"
echo ""
echo "All options include the FIXED robot with full 3D meshes!"
echo ""
echo "1. 🎯 Full UI Mode - Multi-world with obstacles and table"
echo "   ./launch_gazebo_ui.sh"
echo "   • Complete pick & place environment"
echo "   • 5 obstacles + table + glass"
echo "   • May crash on some VMs (graphics intensive)"
echo ""
echo "2. 🛡️  Safe UI Mode - Same world, conservative graphics"
echo "   ./launch_gazebo_ui_safe.sh"
echo "   • Same multi-world but safer graphics settings"
echo "   • Better compatibility with VMs"
echo "   • Timeout protection"
echo ""
echo "3. 🧪 Empty World UI - Minimal, most stable"
echo "   ./test_fixed_robot.sh"
echo "   • Robot in empty world (no obstacles)"
echo "   • Most stable, least likely to crash"
echo "   • Good for testing robot visibility"
echo ""
echo "4. 🤖 Headless Mode - Always works, no GUI"
echo "   ./test_headless_gazebo.sh"
echo "   • Robot runs perfectly, no graphics crashes"
echo "   • Use Joint State Publisher GUI for control"
echo "   • 100% reliable"
echo ""
echo "💡 Recommendation:"
echo "   • Try option 1 first (full experience)"
echo "   • If crashes → try option 2 (safe mode)"
echo "   • If still crashes → option 3 (empty world)"
echo "   • Always working → option 4 (headless)"
echo ""

read -p "Which option would you like to try? (1-4): " choice

case $choice in
    1)
        echo "🚀 Launching Full UI Mode..."
        ./launch_gazebo_ui.sh
        ;;
    2)
        echo "🛡️  Launching Safe UI Mode..."
        ./launch_gazebo_ui_safe.sh
        ;;
    3)
        echo "🧪 Launching Empty World UI..."
        ./test_fixed_robot.sh
        ;;
    4)
        echo "🤖 Launching Headless Mode..."
        ./test_headless_gazebo.sh
        ;;
    *)
        echo "Invalid choice. Please run the script again and choose 1-4."
        ;;
esac
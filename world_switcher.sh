#!/bin/bash

echo "🌍 World Environment Switcher"
echo "============================="

# Check if world environment is running
if ! pgrep -f "world_environments.py" > /dev/null; then
    echo "Starting world environment node..."
    python3 /home/kantar/Desktop/hello-robot/world_environments.py &
    sleep 2
fi

echo ""
echo "Available worlds:"
echo "1. empty - Clean space"
echo "2. office - Office with desks"
echo "3. warehouse - Storage racks"
echo "4. home - Living room"
echo "5. maze - Wall maze"
echo "6. garden - Trees and flowers"
echo "7. factory - Industrial machines"
echo ""

while true; do
    echo -n "Select world (1-7) or 'q' to quit: "
    read choice
    
    case $choice in
        1) world="empty" ;;
        2) world="office" ;;
        3) world="warehouse" ;;
        4) world="home" ;;
        5) world="maze" ;;
        6) world="garden" ;;
        7) world="factory" ;;
        q) echo "Goodbye!"; exit 0 ;;
        *) echo "Invalid choice. Try again."; continue ;;
    esac
    
    echo "🌍 Switching to $world world..."
    
    # Send world command
    source /opt/ros/humble/setup.bash
    ros2 topic pub --once /world_command std_msgs/String "data: '$world'" 2>/dev/null
    
    echo "✅ Switched to $world world"
    echo "   Check RViz to see the environment!"
    echo ""
done
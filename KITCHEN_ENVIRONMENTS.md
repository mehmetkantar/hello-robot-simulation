# Kitchen Environments for SLAM

Your SLAM system now supports realistic RoboCasa kitchen environments! 🏠

## Quick Start with Kitchen Environments

### Default Kitchen (L-shaped Scandinavian)
```bash
./launch_slam.sh
```

### Different Kitchen Layouts
```bash
# U-shaped kitchen
./launch_slam.sh --layout 5

# One wall kitchen with island
./launch_slam.sh --layout 1

# Galley kitchen
./launch_slam.sh --layout 4
```

### Different Kitchen Styles
```bash
# Modern kitchen
./launch_slam.sh --style 3

# Farmhouse kitchen
./launch_slam.sh --style 7

# Industrial kitchen
./launch_slam.sh --style 0
```

### Combined Options
```bash
# U-shaped Farmhouse kitchen
./launch_slam.sh --layout 5 --style 7

# One wall Industrial kitchen without RViz
./launch_slam.sh --layout 0 --style 0 --no-rviz
```

## Available Kitchen Layouts

| Layout | Description |
|--------|-------------|
| 0 | One wall |
| 1 | One wall w/ island |
| 2 | L-shaped (default) |
| 3 | L-shaped w/ island |
| 4 | Galley |
| 5 | U-shaped |
| 6 | U-shaped w/ island |
| 7 | G-shaped |
| 8 | G-shaped (large) |
| 9 | Wraparound |

## Available Kitchen Styles

| Style | Description |
|-------|-------------|
| 0 | Industrial |
| 1 | Scandinavian (default) |
| 2 | Coastal |
| 3 | Modern_1 |
| 4 | Modern_2 |
| 5 | Traditional_1 |
| 6 | Traditional_2 |
| 7 | Farmhouse |

## Fallback Options

If RoboCasa kitchen generation fails:
- The system automatically falls back to a simple environment
- Or use `--simple` flag to use simple environment directly

## Robot Control in Kitchen

Once the kitchen environment is loaded:

1. **View in RViz**: See the robot and kitchen environment
2. **Control robot**: In a new terminal:
   ```bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard
   ```
3. **Build map**: Drive around the kitchen to create a map
4. **Save map**: 
   ```bash
   ros2 run nav2_map_server map_saver_cli -f kitchen_map
   ```

## Environment Features

- **Realistic kitchen furniture**: Cabinets, counters, appliances
- **Varied layouts**: Different kitchen configurations
- **Multiple styles**: Different visual themes
- **Object clutter**: Realistic kitchen objects for SLAM challenges
- **Proper lighting**: Realistic lighting conditions
- **Camera feeds**: Multiple camera angles for visual SLAM

## Tips for Better SLAM

1. **Drive slowly**: Kitchen environments have complex geometry
2. **Explore thoroughly**: Cover all areas including around islands
3. **Use different approaches**: Try different paths to the same area
4. **Check loop closure**: SLAM works best with overlapping paths
5. **Save maps regularly**: Save good maps as you explore

## Troubleshooting

If kitchen environment fails to load:
- Check the console output for specific errors
- Try a different layout/style combination
- Use `--simple` flag as fallback
- Restart the system if needed

Ready to explore realistic kitchen environments with SLAM! 🤖🏠
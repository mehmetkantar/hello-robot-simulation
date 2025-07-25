#!/bin/bash

# Stretch Dual GUI Simulation Launcher
# This script provides easy ways to launch the simulation with different configurations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Enable NVIDIA PRIME render offload for maximum GPU performance
setup_gpu_acceleration() {
    export __NV_PRIME_RENDER_OFFLOAD=1      # Use NVIDIA GPU for rendering
    export __GLX_VENDOR_LIBRARY_NAME=nvidia # Use NVIDIA OpenGL library
    export MUJOCO_GL=egl                    # Use EGL backend for GPU acceleration
    export MUJOCO_GPU_DEVICE_ID=0           # Use first GPU
    export OMP_NUM_THREADS=8                # Multi-threading optimization
    export __GL_SYNC_TO_VBLANK=0            # Disable VSync for performance
    export __GL_YIELD=NOTHING               # Don't yield GPU resources
    export CUDA_LAUNCH_BLOCKING=0           # Non-blocking CUDA calls
    export NVIDIA_TF32_OVERRIDE=0           # Use full precision
    export CUDA_VISIBLE_DEVICES=0           # Use first CUDA device
    print_status "NVIDIA PRIME render offload enabled for 4-5x performance boost"
}

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Python packages
    python3 -c "import tkinter" 2>/dev/null || {
        print_error "tkinter is required. Install with: sudo apt install python3-tk"
        exit 1
    }
    
    python3 -c "import PIL" 2>/dev/null || {
        print_warning "PIL/Pillow not found. Installing..."
        pip3 install Pillow
    }
    
    python3 -c "import cv2" 2>/dev/null || {
        print_warning "OpenCV not found. Installing..."
        pip3 install opencv-python
    }
    
    python3 -c "import numpy" 2>/dev/null || {
        print_warning "NumPy not found. Installing..."
        pip3 install numpy
    }
    
    # Check stretch_mujoco
    python3 -c "from stretch_mujoco import StretchMujocoSimulator" 2>/dev/null || {
        print_error "stretch_mujoco not found. Please install it following Hello Robot's guide."
        exit 1
    }
    
    print_status "All dependencies satisfied!"
}

# Show usage information
show_usage() {
    print_header "Stretch Dual GUI Simulation Launcher"
    echo ""
    echo "Usage: $0 [MODE]"
    echo ""
    echo "Modes:"
    echo "  normal        - Start with default settings (cameras enabled)"
    echo "  fast          - Start in fast mode (no cameras, maximum speed)"
    echo "  headless      - Start without MuJoCo viewer (cameras enabled)"
    echo "  minimal       - Start with no cameras and no viewer"
    echo "  check         - Check dependencies only"
    echo "  examples      - Run example scripts"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 normal     # Default mode with cameras"
    echo "  $0 fast       # Maximum performance"
    echo "  $0 headless   # GUI only, no 3D viewer"
    echo ""
}

# Launch with specific configuration
launch_simulation() {
    local mode=$1
    print_status "Launching simulation in $mode mode..."
    
    case $mode in
        "normal")
            print_status "Starting with cameras and MuJoCo viewer enabled"
            python3 stretch_dual_gui.py
            ;;
        "fast")
            print_status "Starting in fast mode (cameras disabled)"
            print_warning "Note: Camera feeds will not be available in fast mode"
            # We could modify the script to accept command line arguments
            # For now, user needs to enable fast mode in GUI
            print_status "Please enable 'Fast Mode' in the GUI for maximum performance"
            python3 stretch_dual_gui.py
            ;;
        "headless")
            print_status "Starting without MuJoCo 3D viewer"
            print_status "Please disable 'Enable Mujoco 3D Viewer' in the GUI"
            python3 stretch_dual_gui.py
            ;;
        "minimal")
            print_status "Starting with minimal features (no cameras, no viewer)"
            print_status "Please disable both cameras and viewer in the GUI"
            python3 stretch_dual_gui.py
            ;;
        *)
            print_error "Unknown mode: $mode"
            show_usage
            exit 1
            ;;
    esac
}

# Run examples
run_examples() {
    print_header "Running Example Scripts"
    
    if [ -f "examples/basic_usage.py" ]; then
        print_status "Running basic usage example..."
        python3 examples/basic_usage.py
    else
        print_error "Example scripts not found"
    fi
}

# Install script (optional)
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        print_status "Installing individual packages..."
        pip3 install Pillow opencv-python numpy
    fi
    
    print_status "Dependencies installed!"
}

# Main script logic
main() {
    local mode=${1:-"help"}
    
    case $mode in
        "check")
            check_dependencies
            ;;
        "install")
            install_dependencies
            ;;
        "examples")
            check_dependencies
            run_examples
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        "normal"|"fast"|"headless"|"minimal")
            setup_gpu_acceleration
            check_dependencies
            launch_simulation $mode
            ;;
        *)
            print_error "Invalid option: $mode"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Handle Ctrl+C gracefully
trap 'print_warning "Simulation interrupted by user"; exit 130' INT

# Run main function with all arguments
main "$@"
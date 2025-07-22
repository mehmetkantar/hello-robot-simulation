#!/usr/bin/env python3
"""
Simple Web-based Robot Controller
Alternative to GUI when Qt/OpenCV conflicts occur
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class SimpleWebController(Node):
    def __init__(self):
        super().__init__('simple_web_controller')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Publishers for arm/lift control - matching SLAM bridge topic names
        self.lift_pub = self.create_publisher(Float64, '/stretch_controller/lift_joint/command', 10)
        self.arm_pub = self.create_publisher(Float64, '/stretch_controller/arm_joint/command', 10)
        self.head_pan_pub = self.create_publisher(Float64, '/stretch_controller/head_pan_joint/command', 10)
        self.head_tilt_pub = self.create_publisher(Float64, '/stretch_controller/head_tilt_joint/command', 10)
        
        self.current_twist = Twist()
        self.current_lift = 0.0  # meters
        self.current_arm = 0.0   # meters 
        self.current_head_pan = 0.0
        self.current_head_tilt = 0.0
        
    def move_robot(self, linear_x, linear_y, angular_z):
        """Send movement command to robot"""
        twist = Twist()
        twist.linear.x = float(linear_x)
        twist.linear.y = float(linear_y) 
        twist.angular.z = float(angular_z)
        
        self.cmd_vel_pub.publish(twist)
        self.current_twist = twist
        self.get_logger().info(f'Moving robot: linear=({linear_x:.2f}, {linear_y:.2f}), angular={angular_z:.2f}')

    def control_lift(self, position):
        """Send lift command to robot"""
        position = max(0.0, min(1.1, float(position)))  # Clamp to safe limits
        msg = Float64()
        msg.data = position
        self.lift_pub.publish(msg)
        self.current_lift = position
        self.get_logger().info(f'Lift command: {position:.2f}m')
        
    def control_arm(self, extension):
        """Send arm extension command to robot"""
        extension = max(0.0, min(0.52, float(extension)))  # Clamp to safe limits  
        msg = Float64()
        msg.data = extension
        self.arm_pub.publish(msg)
        self.current_arm = extension
        self.get_logger().info(f'Arm command: {extension:.2f}m')
        
    def control_head_pan(self, angle):
        """Send head pan command to robot"""
        angle = max(-1.57, min(1.57, float(angle)))  # Clamp to safe limits
        msg = Float64()
        msg.data = angle
        self.head_pan_pub.publish(msg)
        self.current_head_pan = angle
        self.get_logger().info(f'Head pan command: {angle:.2f}rad')
        
    def control_head_tilt(self, angle):
        """Send head tilt command to robot"""
        angle = max(-0.52, min(0.52, float(angle)))  # Clamp to safe limits
        msg = Float64()
        msg.data = angle
        self.head_tilt_pub.publish(msg)
        self.current_head_tilt = angle
        self.get_logger().info(f'Head tilt command: {angle:.2f}rad')

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Stretch Robot Controller</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; background: #f0f0f0; }
                    .container { max-width: 600px; margin: 20px auto; padding: 20px; background: white; border-radius: 10px; }
                    .control-panel { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }
                    .btn { padding: 20px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
                    .btn:hover { opacity: 0.8; }
                    .forward { background: #4CAF50; color: white; }
                    .backward { background: #f44336; color: white; }
                    .left { background: #2196F3; color: white; }
                    .right { background: #FF9800; color: white; }
                    .stop { background: #9E9E9E; color: white; }
                    .rotate-left { background: #9C27B0; color: white; }
                    .rotate-right { background: #E91E63; color: white; }
                    .speed-control { margin: 20px 0; }
                    .arm-controls { margin: 20px 0; }
                    .control-row { margin: 10px 0; display: flex; align-items: center; gap: 10px; }
                    .control-row label { min-width: 120px; }
                    .control-row input { flex: 1; max-width: 200px; }
                    .control-row span { min-width: 60px; }
                    .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Stretch Robot Controller</h1>
                    <div class="status">
                        <p><strong>Status:</strong> Connected to SLAM System</p>
                        <p><strong>Control:</strong> Click buttons to move robot base and manipulator</p>
                    </div>
                    
                    <div class="speed-control">
                        <label>Base Speed: </label>
                        <input type="range" id="speed" min="0.1" max="1.0" step="0.1" value="0.3">
                        <span id="speedValue">0.3</span> m/s
                    </div>
                    
                    <h3>🚗 Base Movement</h3>
                    <div class="control-panel">
                        <div></div>
                        <button class="btn forward" onclick="moveRobot(0.3, 0, 0)">↑ Forward</button>
                        <div></div>
                        
                        <button class="btn rotate-left" onclick="moveRobot(0, 0, 0.5)">↺ Rotate L</button>
                        <button class="btn stop" onclick="stopRobot()">⏹ STOP</button>
                        <button class="btn rotate-right" onclick="moveRobot(0, 0, -0.5)">↻ Rotate R</button>
                        
                        <div></div>
                        <button class="btn backward" onclick="moveRobot(-0.3, 0, 0)">↓ Backward</button>
                        <div></div>
                        
                        <button class="btn left" onclick="moveRobot(0, 0.3, 0)">← Left</button>
                        <div></div>
                        <button class="btn right" onclick="moveRobot(0, -0.3, 0)">→ Right</button>
                    </div>
                    
                    <h3>🦾 Arm & Lift Control</h3>
                    <div class="arm-controls">
                        <div class="control-row">
                            <label>Lift Height: </label>
                            <input type="range" id="liftHeight" min="0.0" max="1.1" step="0.05" value="0.5">
                            <span id="liftValue">0.5</span> m
                            <button class="btn" onclick="setLift()">Set Lift</button>
                        </div>
                        
                        <div class="control-row">
                            <label>Arm Extension: </label>
                            <input type="range" id="armExtension" min="0.0" max="0.52" step="0.02" value="0.1">
                            <span id="armValue">0.1</span> m
                            <button class="btn" onclick="setArm()">Set Arm</button>
                        </div>
                        
                        <div class="control-row">
                            <label>Head Pan: </label>
                            <input type="range" id="headPan" min="-1.57" max="1.57" step="0.1" value="0.0">
                            <span id="headPanValue">0.0</span> rad
                            <button class="btn" onclick="setHeadPan()">Set Pan</button>
                        </div>
                        
                        <div class="control-row">
                            <label>Head Tilt: </label>
                            <input type="range" id="headTilt" min="-0.52" max="0.52" step="0.05" value="0.0">
                            <span id="headTiltValue">0.0</span> rad
                            <button class="btn" onclick="setHeadTilt()">Set Tilt</button>
                        </div>
                    </div>
                    
                    <div class="status">
                        <p><strong>Instructions:</strong></p>
                        <p>• Use buttons to control robot base movement</p>
                        <p>• Use sliders to control arm, lift, and head</p>
                        <p>• Watch robot move in MuJoCo and RViz windows</p>
                        <p>• SLAM will build map as you explore</p>
                        <p>• Adjust base speed with speed slider</p>
                    </div>
                </div>
                
                <script>
                    // UI Element references
                    const speedSlider = document.getElementById('speed');
                    const speedValue = document.getElementById('speedValue');
                    const liftSlider = document.getElementById('liftHeight');
                    const liftValue = document.getElementById('liftValue');
                    const armSlider = document.getElementById('armExtension');
                    const armValue = document.getElementById('armValue');
                    const headPanSlider = document.getElementById('headPan');
                    const headPanValue = document.getElementById('headPanValue');
                    const headTiltSlider = document.getElementById('headTilt');
                    const headTiltValue = document.getElementById('headTiltValue');
                    
                    // Update display values when sliders change
                    speedSlider.addEventListener('input', function() {
                        speedValue.textContent = this.value;
                    });
                    
                    liftSlider.addEventListener('input', function() {
                        liftValue.textContent = this.value;
                    });
                    
                    armSlider.addEventListener('input', function() {
                        armValue.textContent = this.value;
                    });
                    
                    headPanSlider.addEventListener('input', function() {
                        headPanValue.textContent = this.value;
                    });
                    
                    headTiltSlider.addEventListener('input', function() {
                        headTiltValue.textContent = this.value;
                    });
                    
                    // Base movement functions
                    function moveRobot(linear_x, linear_y, angular_z) {
                        const speed = parseFloat(speedSlider.value);
                        linear_x *= speed;
                        linear_y *= speed;
                        angular_z *= speed;
                        
                        fetch('/move', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                linear_x: linear_x,
                                linear_y: linear_y,
                                angular_z: angular_z
                            })
                        });
                    }
                    
                    function stopRobot() {
                        fetch('/move', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                linear_x: 0,
                                linear_y: 0,
                                angular_z: 0
                            })
                        });
                    }
                    
                    // Arm and manipulator control functions
                    function setLift() {
                        const position = parseFloat(liftSlider.value);
                        fetch('/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                type: 'lift',
                                value: position
                            })
                        });
                    }
                    
                    function setArm() {
                        const extension = parseFloat(armSlider.value);
                        fetch('/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                type: 'arm',
                                value: extension
                            })
                        });
                    }
                    
                    function setHeadPan() {
                        const angle = parseFloat(headPanSlider.value);
                        fetch('/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                type: 'head_pan',
                                value: angle
                            })
                        });
                    }
                    
                    function setHeadTilt() {
                        const angle = parseFloat(headTiltSlider.value);
                        fetch('/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                type: 'head_tilt',
                                value: angle
                            })
                        });
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/move':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                linear_x = data.get('linear_x', 0.0)
                linear_y = data.get('linear_y', 0.0) 
                angular_z = data.get('angular_z', 0.0)
                
                # Send command to robot
                if hasattr(self.server, 'controller'):
                    self.server.controller.move_robot(linear_x, linear_y, angular_z)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"Error processing move command: {e}")
                
        elif self.path == '/control':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                control_type = data.get('type')
                value = data.get('value', 0.0)
                
                # Send command to robot based on type
                if hasattr(self.server, 'controller'):
                    controller = self.server.controller
                    
                    if control_type == 'lift':
                        controller.control_lift(value)
                    elif control_type == 'arm':
                        controller.control_arm(value)
                    elif control_type == 'head_pan':
                        controller.control_head_pan(value)
                    elif control_type == 'head_tilt':
                        controller.control_head_tilt(value)
                    else:
                        raise ValueError(f"Unknown control type: {control_type}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'type': control_type, 'value': value}).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"Error processing control command: {e}")
        else:
            self.send_response(404)
            self.end_headers()

def main():
    rclpy.init()
    
    # Create ROS2 node
    controller = SimpleWebController()
    
    # Start ROS2 spinning in separate thread
    def spin_ros():
        rclpy.spin(controller)
    
    ros_thread = threading.Thread(target=spin_ros, daemon=True)
    ros_thread.start()
    
    # Start web server
    server = HTTPServer(('localhost', 8081), WebHandler)
    server.controller = controller
    
    print("🌐 Starting Simple Web Controller...")
    print("📱 Open your web browser and go to: http://localhost:8081")
    print("🎮 Use the web interface to control your robot!")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web controller...")
        server.shutdown()
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
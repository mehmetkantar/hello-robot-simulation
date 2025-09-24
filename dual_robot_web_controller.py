#!/usr/bin/env python3
"""
Dual Robot Web Controller
Controls both Stretch robot and Humanoid robot via web interface
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64, Bool
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class DualRobotWebController(Node):
    def __init__(self):
        super().__init__('dual_robot_web_controller')

        # ========== STRETCH ROBOT PUBLISHERS ==========
        self.stretch_cmd_vel_pub = self.create_publisher(Twist, '/stretch/cmd_vel', 10)
        self.stretch_lift_pub = self.create_publisher(Float64, '/stretch/controller/lift_joint/command', 10)
        self.stretch_arm_pub = self.create_publisher(Float64, '/stretch/controller/arm_joint/command', 10)
        self.stretch_head_pan_pub = self.create_publisher(Float64, '/stretch/controller/head_pan_joint/command', 10)
        self.stretch_head_tilt_pub = self.create_publisher(Float64, '/stretch/controller/head_tilt_joint/command', 10)

        # ========== HUMANOID ROBOT PUBLISHERS ==========
        self.humanoid_cmd_vel_pub = self.create_publisher(Twist, '/humanoid/cmd_vel', 10)
        self.humanoid_walk_pub = self.create_publisher(Twist, '/humanoid/walk_cmd', 10)

        # ========== GENERAL PUBLISHERS ==========
        self.camera_toggle_pub = self.create_publisher(Bool, '/controller/toggle_cameras', 10)

        # Robot states
        self.stretch_state = {
            'twist': Twist(),
            'lift': 0.0,
            'arm': 0.0,
            'head_pan': 0.0,
            'head_tilt': 0.0
        }

        self.humanoid_state = {
            'twist': Twist(),
            'walking': False
        }

        self.get_logger().info("Dual Robot Web Controller initialized")

    def move_stretch_robot(self, linear_x, linear_y, angular_z):
        """Send movement command to Stretch robot"""
        twist = Twist()
        twist.linear.x = float(linear_x)
        twist.linear.y = float(linear_y)
        twist.angular.z = float(angular_z)

        self.stretch_cmd_vel_pub.publish(twist)
        self.stretch_state['twist'] = twist
        self.get_logger().info(f'🤖 Stretch move: v=({linear_x:.2f}, {linear_y:.2f}), w={angular_z:.2f}')

    def move_humanoid_robot(self, linear_x, angular_z):
        """Send movement command to Humanoid robot"""
        twist = Twist()
        twist.linear.x = float(linear_x)
        twist.linear.y = 0.0  # Humanoid doesn't strafe
        twist.angular.z = float(angular_z)

        self.humanoid_cmd_vel_pub.publish(twist)
        self.humanoid_walk_pub.publish(twist)  # Send to both topics
        self.humanoid_state['twist'] = twist
        self.humanoid_state['walking'] = abs(linear_x) > 0.01 or abs(angular_z) > 0.01
        self.get_logger().info(f'🚶 Humanoid move: v={linear_x:.2f}, w={angular_z:.2f}')

    def control_stretch_lift(self, position):
        """Send lift command to Stretch robot"""
        position = max(0.0, min(1.1, float(position)))
        msg = Float64()
        msg.data = position
        self.stretch_lift_pub.publish(msg)
        self.stretch_state['lift'] = position
        self.get_logger().info(f'🏗️ Stretch lift: {position:.2f}m')

    def control_stretch_arm(self, extension):
        """Send arm extension command to Stretch robot"""
        extension = max(0.0, min(0.52, float(extension)))
        msg = Float64()
        msg.data = extension
        self.stretch_arm_pub.publish(msg)
        self.stretch_state['arm'] = extension
        self.get_logger().info(f'🦾 Stretch arm: {extension:.2f}m')

    def control_stretch_head_pan(self, angle):
        """Send head pan command to Stretch robot"""
        angle = max(-1.57, min(1.57, float(angle)))
        msg = Float64()
        msg.data = angle
        self.stretch_head_pan_pub.publish(msg)
        self.stretch_state['head_pan'] = angle
        self.get_logger().info(f'🔄 Stretch head pan: {angle:.2f}rad')

    def control_stretch_head_tilt(self, angle):
        """Send head tilt command to Stretch robot"""
        angle = max(-0.52, min(0.52, float(angle)))
        msg = Float64()
        msg.data = angle
        self.stretch_head_tilt_pub.publish(msg)
        self.stretch_state['head_tilt'] = angle
        self.get_logger().info(f'🔄 Stretch head tilt: {angle:.2f}rad')

    def toggle_cameras(self, enabled):
        """Send camera toggle command"""
        msg = Bool()
        msg.data = bool(enabled)
        self.camera_toggle_pub.publish(msg)
        self.get_logger().info(f'📷 Cameras {enabled}')

class DualRobotWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dual Robot Controller - Stretch + Humanoid</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; background: #f0f0f0; }
                    .container { max-width: 1000px; margin: 20px auto; padding: 20px; background: white; border-radius: 10px; }
                    .robot-section { display: flex; gap: 20px; margin: 20px 0; }
                    .robot-panel { flex: 1; border: 2px solid #ddd; border-radius: 10px; padding: 20px; }
                    .stretch-panel { border-color: #4CAF50; }
                    .humanoid-panel { border-color: #2196F3; }
                    .control-panel { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }
                    .btn { padding: 15px; font-size: 14px; border: none; border-radius: 5px; cursor: pointer; }
                    .btn:hover { opacity: 0.8; }
                    .forward { background: #4CAF50; color: white; }
                    .backward { background: #f44336; color: white; }
                    .left { background: #2196F3; color: white; }
                    .right { background: #FF9800; color: white; }
                    .stop { background: #9E9E9E; color: white; }
                    .rotate-left { background: #9C27B0; color: white; }
                    .rotate-right { background: #E91E63; color: white; }
                    .walk { background: #00BCD4; color: white; }
                    .speed-control { margin: 15px 0; }
                    .arm-controls { margin: 15px 0; }
                    .control-row { margin: 8px 0; display: flex; align-items: center; gap: 10px; }
                    .control-row label { min-width: 100px; font-size: 12px; }
                    .control-row input { flex: 1; max-width: 150px; }
                    .control-row span { min-width: 50px; font-size: 12px; }
                    .status { background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 12px; }
                    .robot-title { color: #333; margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Dual Robot Controller</h1>
                    <div class="status">
                        <p><strong>Status:</strong> Connected to Dual Robot SLAM System</p>
                        <p><strong>Control:</strong> Stretch robot (left) + Humanoid robot (right) in same environment</p>
                    </div>

                    <div class="robot-section">
                        <!-- ========== STRETCH ROBOT PANEL ========== -->
                        <div class="robot-panel stretch-panel">
                            <h2 class="robot-title">🤖 STRETCH ROBOT</h2>

                            <div class="speed-control">
                                <label>Base Speed: </label>
                                <input type="range" id="stretchSpeed" min="0.5" max="15.0" step="0.5" value="3.0">
                                <span id="stretchSpeedValue">3.0</span> m/s
                            </div>

                            <h4>🚗 Base Movement</h4>
                            <div class="control-panel">
                                <div></div>
                                <button class="btn forward" onclick="moveStretch(3.0, 0, 0)">↑ Forward</button>
                                <div></div>

                                <button class="btn rotate-left" onclick="moveStretch(0, 0, 2.0)">↺ Left</button>
                                <button class="btn stop" onclick="stopStretch()">⏹ STOP</button>
                                <button class="btn rotate-right" onclick="moveStretch(0, 0, -2.0)">↻ Right</button>

                                <button class="btn left" onclick="moveStretch(0, 3.0, 0)">← Strafe L</button>
                                <button class="btn backward" onclick="moveStretch(-3.0, 0, 0)">↓ Back</button>
                                <button class="btn right" onclick="moveStretch(0, -3.0, 0)">→ Strafe R</button>
                            </div>

                            <h4>🦾 Arm & Manipulator</h4>
                            <div class="arm-controls">
                                <div class="control-row">
                                    <label>Lift Height:</label>
                                    <input type="range" id="stretchLift" min="0.0" max="1.1" step="0.05" value="0.5">
                                    <span id="stretchLiftValue">0.5</span> m
                                    <button class="btn" onclick="setStretchLift()">Set</button>
                                </div>

                                <div class="control-row">
                                    <label>Arm Extension:</label>
                                    <input type="range" id="stretchArm" min="0.0" max="0.52" step="0.02" value="0.1">
                                    <span id="stretchArmValue">0.1</span> m
                                    <button class="btn" onclick="setStretchArm()">Set</button>
                                </div>

                                <div class="control-row">
                                    <label>Head Pan:</label>
                                    <input type="range" id="stretchHeadPan" min="-1.57" max="1.57" step="0.1" value="0.0">
                                    <span id="stretchHeadPanValue">0.0</span> rad
                                    <button class="btn" onclick="setStretchHeadPan()">Set</button>
                                </div>

                                <div class="control-row">
                                    <label>Head Tilt:</label>
                                    <input type="range" id="stretchHeadTilt" min="-0.52" max="0.52" step="0.05" value="0.0">
                                    <span id="stretchHeadTiltValue">0.0</span> rad
                                    <button class="btn" onclick="setStretchHeadTilt()">Set</button>
                                </div>
                            </div>
                        </div>

                        <!-- ========== HUMANOID ROBOT PANEL ========== -->
                        <div class="robot-panel humanoid-panel">
                            <h2 class="robot-title">🚶 HUMANOID ROBOT</h2>

                            <div class="speed-control">
                                <label>Walk Speed: </label>
                                <input type="range" id="humanoidSpeed" min="0.1" max="2.0" step="0.1" value="0.5">
                                <span id="humanoidSpeedValue">0.5</span> m/s
                            </div>

                            <h4>🚶 Bipedal Walking</h4>
                            <div class="control-panel">
                                <div></div>
                                <button class="btn walk" onclick="moveHumanoid(0.5, 0)">↑ Walk Forward</button>
                                <div></div>

                                <button class="btn rotate-left" onclick="moveHumanoid(0, 1.0)">↺ Turn Left</button>
                                <button class="btn stop" onclick="stopHumanoid()">⏹ STOP</button>
                                <button class="btn rotate-right" onclick="moveHumanoid(0, -1.0)">↻ Turn Right</button>

                                <div></div>
                                <button class="btn backward" onclick="moveHumanoid(-0.3, 0)">↓ Walk Back</button>
                                <div></div>
                            </div>

                            <h4>🎯 Walking Patterns</h4>
                            <div class="arm-controls">
                                <div class="control-row">
                                    <button class="btn walk" onclick="humanoidWalkPattern('forward')">🏃 Forward Walk</button>
                                    <button class="btn walk" onclick="humanoidWalkPattern('circle')">🔄 Circle Walk</button>
                                </div>

                                <div class="control-row">
                                    <button class="btn walk" onclick="humanoidWalkPattern('zigzag')">⚡ Zigzag Walk</button>
                                    <button class="btn stop" onclick="humanoidWalkPattern('stop')">🛑 Stop All</button>
                                </div>
                            </div>

                            <div class="status" style="background: #e3f2fd;">
                                <p><strong>Humanoid Features:</strong></p>
                                <p>• Bipedal locomotion with gait generation</p>
                                <p>• Walking patterns: forward, backward, turning</p>
                                <p>• Dynamic balance simulation</p>
                                <p>• Real-time joint control</p>
                            </div>
                        </div>
                    </div>

                    <!-- ========== GLOBAL CONTROLS ========== -->
                    <div style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px;">
                        <h3>🌐 Global Controls</h3>
                        <div class="control-row">
                            <label for="camera_toggle">Camera Publishing:</label>
                            <input type="checkbox" id="camera_toggle" checked onchange="toggleCameras(this.checked)">
                            <button class="btn" onclick="emergencyStopAll()" style="background: #f44336; color: white; margin-left: 20px;">🚨 EMERGENCY STOP ALL</button>
                        </div>
                    </div>

                    <div class="status">
                        <p><strong>Instructions:</strong></p>
                        <p>• <strong>Stretch Robot:</strong> Full manipulator control + navigation + SLAM mapping</p>
                        <p>• <strong>Humanoid Robot:</strong> Bipedal walking + exploration in same environment</p>
                        <p>• Both robots operate in the same complex office scene</p>
                        <p>• Watch both robots in MuJoCo viewer and RViz</p>
                        <p>• Use different speeds: Stretch for precision, Humanoid for exploration</p>
                    </div>
                </div>

                <script>
                    // ========== UI UPDATE FUNCTIONS ==========
                    const stretchSpeedSlider = document.getElementById('stretchSpeed');
                    const stretchSpeedValue = document.getElementById('stretchSpeedValue');
                    const humanoidSpeedSlider = document.getElementById('humanoidSpeed');
                    const humanoidSpeedValue = document.getElementById('humanoidSpeedValue');

                    const stretchLiftSlider = document.getElementById('stretchLift');
                    const stretchLiftValue = document.getElementById('stretchLiftValue');
                    const stretchArmSlider = document.getElementById('stretchArm');
                    const stretchArmValue = document.getElementById('stretchArmValue');
                    const stretchHeadPanSlider = document.getElementById('stretchHeadPan');
                    const stretchHeadPanValue = document.getElementById('stretchHeadPanValue');
                    const stretchHeadTiltSlider = document.getElementById('stretchHeadTilt');
                    const stretchHeadTiltValue = document.getElementById('stretchHeadTiltValue');

                    // Update display values
                    stretchSpeedSlider.addEventListener('input', function() { stretchSpeedValue.textContent = this.value; });
                    humanoidSpeedSlider.addEventListener('input', function() { humanoidSpeedValue.textContent = this.value; });
                    stretchLiftSlider.addEventListener('input', function() { stretchLiftValue.textContent = this.value; });
                    stretchArmSlider.addEventListener('input', function() { stretchArmValue.textContent = this.value; });
                    stretchHeadPanSlider.addEventListener('input', function() { stretchHeadPanValue.textContent = this.value; });
                    stretchHeadTiltSlider.addEventListener('input', function() { stretchHeadTiltValue.textContent = this.value; });

                    // ========== STRETCH ROBOT CONTROLS ==========
                    function moveStretch(linear_x, linear_y, angular_z) {
                        const speed = parseFloat(stretchSpeedSlider.value);
                        linear_x *= speed;
                        linear_y *= speed;
                        if (speed > 5.0) {
                            angular_z *= (speed * 0.4);
                        } else {
                            angular_z *= (speed * 0.7);
                        }

                        fetch('/stretch/move', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                linear_x: linear_x,
                                linear_y: linear_y,
                                angular_z: angular_z
                            })
                        });
                    }

                    function stopStretch() {
                        fetch('/stretch/move', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ linear_x: 0, linear_y: 0, angular_z: 0 })
                        });
                    }

                    function setStretchLift() {
                        const position = parseFloat(stretchLiftSlider.value);
                        fetch('/stretch/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ type: 'lift', value: position })
                        });
                    }

                    function setStretchArm() {
                        const extension = parseFloat(stretchArmSlider.value);
                        fetch('/stretch/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ type: 'arm', value: extension })
                        });
                    }

                    function setStretchHeadPan() {
                        const angle = parseFloat(stretchHeadPanSlider.value);
                        fetch('/stretch/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ type: 'head_pan', value: angle })
                        });
                    }

                    function setStretchHeadTilt() {
                        const angle = parseFloat(stretchHeadTiltSlider.value);
                        fetch('/stretch/control', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ type: 'head_tilt', value: angle })
                        });
                    }

                    // ========== HUMANOID ROBOT CONTROLS ==========
                    function moveHumanoid(linear_x, angular_z) {
                        const speed = parseFloat(humanoidSpeedSlider.value);
                        linear_x *= speed;
                        angular_z *= speed * 0.8; // Slower turning for humanoid stability

                        fetch('/humanoid/move', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                linear_x: linear_x,
                                angular_z: angular_z
                            })
                        });
                    }

                    function stopHumanoid() {
                        fetch('/humanoid/move', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ linear_x: 0, angular_z: 0 })
                        });
                    }

                    function humanoidWalkPattern(pattern) {
                        fetch('/humanoid/pattern', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ pattern: pattern })
                        });
                    }

                    // ========== GLOBAL CONTROLS ==========
                    function toggleCameras(enabled) {
                        fetch('/global/cameras', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ enabled: enabled })
                        });
                    }

                    function emergencyStopAll() {
                        stopStretch();
                        stopHumanoid();
                        console.log('🚨 EMERGENCY STOP - All robots stopped');
                    }

                    // ========== WALKING PATTERN IMPLEMENTATIONS ==========
                    let walkingInterval = null;

                    function executeWalkingPattern(pattern) {
                        if (walkingInterval) {
                            clearInterval(walkingInterval);
                            walkingInterval = null;
                        }

                        if (pattern === 'stop') {
                            stopHumanoid();
                            return;
                        }

                        const speed = parseFloat(humanoidSpeedSlider.value);
                        let step = 0;

                        if (pattern === 'forward') {
                            moveHumanoid(1.0, 0);
                        } else if (pattern === 'circle') {
                            walkingInterval = setInterval(() => {
                                moveHumanoid(0.5, 0.5);
                            }, 100);
                        } else if (pattern === 'zigzag') {
                            walkingInterval = setInterval(() => {
                                const turn = (step % 60 < 30) ? 0.3 : -0.3;
                                moveHumanoid(0.7, turn);
                                step++;
                            }, 100);
                        }
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
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))

            # ========== STRETCH ROBOT ENDPOINTS ==========
            if self.path == '/stretch/move':
                linear_x = data.get('linear_x', 0.0)
                linear_y = data.get('linear_y', 0.0)
                angular_z = data.get('angular_z', 0.0)

                if hasattr(self.server, 'controller'):
                    self.server.controller.move_stretch_robot(linear_x, linear_y, angular_z)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'robot': 'stretch'}).encode('utf-8'))

            elif self.path == '/stretch/control':
                control_type = data.get('type')
                value = data.get('value', 0.0)

                if hasattr(self.server, 'controller'):
                    controller = self.server.controller

                    if control_type == 'lift':
                        controller.control_stretch_lift(value)
                    elif control_type == 'arm':
                        controller.control_stretch_arm(value)
                    elif control_type == 'head_pan':
                        controller.control_stretch_head_pan(value)
                    elif control_type == 'head_tilt':
                        controller.control_stretch_head_tilt(value)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'robot': 'stretch', 'type': control_type}).encode('utf-8'))

            # ========== HUMANOID ROBOT ENDPOINTS ==========
            elif self.path == '/humanoid/move':
                linear_x = data.get('linear_x', 0.0)
                angular_z = data.get('angular_z', 0.0)

                if hasattr(self.server, 'controller'):
                    self.server.controller.move_humanoid_robot(linear_x, angular_z)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'robot': 'humanoid'}).encode('utf-8'))

            elif self.path == '/humanoid/pattern':
                pattern = data.get('pattern', 'stop')

                # Pattern execution would be handled on the client side
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'pattern': pattern}).encode('utf-8'))

            # ========== GLOBAL ENDPOINTS ==========
            elif self.path == '/global/cameras':
                enabled = data.get('enabled', True)

                if hasattr(self.server, 'controller'):
                    self.server.controller.toggle_cameras(enabled)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'cameras': enabled}).encode('utf-8'))

            else:
                self.send_response(404)
                self.end_headers()

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            print(f"Error processing command: {e}")

def main():
    rclpy.init()

    # Create ROS2 node
    controller = DualRobotWebController()

    # Start ROS2 spinning in separate thread
    def spin_ros():
        rclpy.spin(controller)

    ros_thread = threading.Thread(target=spin_ros, daemon=True)
    ros_thread.start()

    # Start web server
    server = HTTPServer(('localhost', 8082), DualRobotWebHandler)
    server.controller = controller

    print("🌐 Starting Dual Robot Web Controller...")
    print("📱 Open your web browser and go to: http://localhost:8082")
    print("🤖 Control Stretch robot (left panel)")
    print("🚶 Control Humanoid robot (right panel)")
    print("🛑 Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dual robot web controller...")
        server.shutdown()
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
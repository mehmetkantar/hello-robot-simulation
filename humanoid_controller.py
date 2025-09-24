#!/usr/bin/env python3
"""
Gymnasium Humanoid Controller for MuJoCo Integration
Provides realistic walking humanoid that can be integrated with Stretch robot simulation.
"""

import gymnasium as gym
import numpy as np
import time
import threading
import math

class HumanoidController:
    def __init__(self, render_mode="human"):
        """Initialize Gymnasium Humanoid controller"""
        self.env = gym.make('Humanoid-v4', render_mode=render_mode)
        self.observation, self.info = self.env.reset()

        # Walking parameters
        self.walking_speed = 0.3
        self.turn_speed = 0.2
        self.walking_pattern = "random"  # "random", "circle", "straight", "stop"

        # Control state
        self.is_running = False
        self.last_action = None
        self.position = [0.0, 0.0]  # x, y position tracking
        self.orientation = 0.0  # heading angle

        # Walking patterns
        self.pattern_time = 0.0
        self.pattern_duration = 10.0  # seconds per pattern

        print("✓ Humanoid Controller initialized")
        print(f"  Action space: {self.env.action_space.shape}")
        print(f"  Observation space: {self.env.observation_space.shape}")

    def get_walking_action(self):
        """Generate action based on current walking pattern"""
        action = np.zeros(self.env.action_space.shape[0])

        if self.walking_pattern == "stop":
            return action

        elif self.walking_pattern == "straight":
            # Walk straight forward
            action[0] = self.walking_speed  # hip_1 (right hip pitch)
            action[3] = self.walking_speed  # hip_2 (left hip pitch)
            action[1] = -self.walking_speed * 0.5  # hip_1 (right hip roll)
            action[4] = self.walking_speed * 0.5   # hip_2 (left hip roll)

        elif self.walking_pattern == "circle":
            # Walk in a circle
            circle_time = self.pattern_time * 0.5
            action[0] = self.walking_speed * math.cos(circle_time)
            action[3] = self.walking_speed * math.cos(circle_time)
            action[2] = self.turn_speed * math.sin(circle_time)  # turning

        elif self.walking_pattern == "random":
            # Random walking with some structure
            if self.pattern_time % 3.0 < 1.5:  # Walk forward for 1.5s
                action[0] = self.walking_speed * (0.8 + 0.4 * np.random.random())
                action[3] = self.walking_speed * (0.8 + 0.4 * np.random.random())
            else:  # Turn for 1.5s
                action[2] = self.turn_speed * (np.random.random() - 0.5) * 2

        # Add some arm movement for natural walking
        action[8] = math.sin(self.pattern_time * 2) * 0.3   # right arm
        action[11] = -math.sin(self.pattern_time * 2) * 0.3  # left arm

        # Add noise for more realistic movement
        action += np.random.normal(0, 0.02, action.shape)

        return action

    def step(self):
        """Execute one step of humanoid simulation"""
        if not self.is_running:
            return False

        try:
            # Get action based on current pattern
            action = self.get_walking_action()

            # Execute action in environment
            observation, reward, terminated, truncated, info = self.env.step(action)

            # Update tracking
            self.last_action = action
            self.observation = observation
            self.pattern_time += 0.02  # Assuming 50Hz control

            # Change pattern periodically
            if self.pattern_time > self.pattern_duration:
                self.change_walking_pattern()
                self.pattern_time = 0.0

            # Reset if terminated
            if terminated or truncated:
                print("🔄 Humanoid fell, resetting...")
                self.observation, self.info = self.env.reset()

            return True

        except Exception as e:
            print(f"❌ Error in humanoid step: {e}")
            return False

    def change_walking_pattern(self):
        """Randomly change walking pattern"""
        patterns = ["straight", "circle", "random", "stop"]
        # Remove current pattern to ensure change
        available_patterns = [p for p in patterns if p != self.walking_pattern]
        self.walking_pattern = np.random.choice(available_patterns)
        print(f"🚶 Humanoid changing to: {self.walking_pattern}")

    def set_walking_pattern(self, pattern):
        """Manually set walking pattern"""
        valid_patterns = ["random", "circle", "straight", "stop"]
        if pattern in valid_patterns:
            self.walking_pattern = pattern
            self.pattern_time = 0.0
            print(f"🎯 Humanoid pattern set to: {pattern}")
        else:
            print(f"❌ Invalid pattern: {pattern}. Valid: {valid_patterns}")

    def start(self):
        """Start humanoid movement"""
        self.is_running = True
        print("▶️ Humanoid started walking")

    def stop(self):
        """Stop humanoid movement"""
        self.is_running = False
        self.walking_pattern = "stop"
        print("⏹️ Humanoid stopped")

    def render(self):
        """Render humanoid (handled by Gymnasium)"""
        if hasattr(self.env, 'render'):
            return self.env.render()

    def close(self):
        """Clean up humanoid environment"""
        if hasattr(self, 'env'):
            self.env.close()
        print("🔌 Humanoid controller closed")

def main():
    """Test humanoid controller standalone"""
    print("🧪 Testing Humanoid Controller")

    controller = HumanoidController()
    controller.start()

    try:
        for i in range(1000):  # Run for ~20 seconds at 50Hz
            success = controller.step()
            if not success:
                break

            # Change pattern every 5 seconds for demo
            if i % 250 == 0 and i > 0:
                controller.change_walking_pattern()

            time.sleep(0.02)  # 50Hz

    except KeyboardInterrupt:
        print("\n🛑 Stopping humanoid test...")
    finally:
        controller.stop()
        controller.close()

if __name__ == "__main__":
    main()
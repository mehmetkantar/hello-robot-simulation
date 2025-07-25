#!/usr/bin/env python3
"""
Test just the joystick component to see if it generates commands
"""

import sys
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np

class TestJoystick(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.center_x = 150
        self.center_y = 150
        self.knob_x = 150
        self.knob_y = 150
        self.max_distance = 120
        self.dragging = False
        
        self.setWindowTitle("🕹️ Joystick Test")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw outer circle
        painter.setBrush(QBrush(QColor(52, 73, 94)))
        painter.setPen(QPen(QColor(149, 165, 166), 3))
        painter.drawEllipse(30, 30, 240, 240)
        
        # Draw center cross
        painter.setPen(QPen(QColor(189, 195, 199), 2))
        painter.drawLine(150, 40, 150, 260)
        painter.drawLine(40, 150, 260, 150)
        
        # Draw knob
        painter.setBrush(QBrush(QColor(52, 152, 219)))
        painter.setPen(QPen(QColor(41, 128, 185), 2))
        painter.drawEllipse(self.knob_x - 20, self.knob_y - 20, 40, 40)
        
        painter.end()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            distance = ((event.x() - self.center_x) ** 2 + (event.y() - self.center_y) ** 2) ** 0.5
            if distance <= self.max_distance:
                self.dragging = True
                self.knob_x = event.x()
                self.knob_y = event.y()
                self._emit_position()
                self.update()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            dx = event.x() - self.center_x
            dy = event.y() - self.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance <= self.max_distance:
                self.knob_x = event.x()
                self.knob_y = event.y()
            else:
                # Constrain to circle
                angle = np.arctan2(dy, dx)
                self.knob_x = self.center_x + self.max_distance * np.cos(angle)
                self.knob_y = self.center_y + self.max_distance * np.sin(angle)
            
            self._emit_position()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.knob_x = self.center_x
            self.knob_y = self.center_y
            self._emit_position()
            self.update()
    
    def _emit_position(self):
        # Convert to -1 to 1 range
        x = (self.knob_x - self.center_x) / self.max_distance
        y = -(self.knob_y - self.center_y) / self.max_distance  # Invert Y
        
        print(f"🕹️ Joystick: x={x:.3f}, y={y:.3f}")
        
        # Convert to robot commands
        linear = y * 0.5   # Max 0.5 m/s
        angular = -x * 1.0  # Max 1.0 rad/s
        
        if abs(linear) > 0.01 or abs(angular) > 0.01:
            print(f"🤖 Robot cmd: linear={linear:.3f}, angular={angular:.3f}")


def main():
    app = QApplication(sys.argv)
    
    widget = QWidget()
    layout = QVBoxLayout()
    
    title = QLabel("🕹️ Joystick Test")
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
    
    instructions = QLabel("Drag the blue knob around.\nWatch the terminal for output.")
    instructions.setAlignment(Qt.AlignCenter)
    instructions.setStyleSheet("padding: 10px;")
    
    joystick = TestJoystick()
    
    layout.addWidget(title)
    layout.addWidget(instructions)
    layout.addWidget(joystick)
    
    widget.setLayout(layout)
    widget.setWindowTitle("Joystick Test")
    widget.show()
    
    print("🕹️ Joystick test started")
    print("📱 Move the joystick and watch for output")
    print("🛑 Close window to exit")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
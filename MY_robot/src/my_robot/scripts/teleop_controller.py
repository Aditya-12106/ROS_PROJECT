#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

import sys
import select
import termios
import tty
import time

msg = """
ULTRA LOW LATENCY TELEOP (PID CONTROL)
-------------------------------------
Arrow Keys → Move
W/S → Linear speed
A/D → Angular speed
SPACE → Instant brake
CTRL-C → Quit
"""

# ================= PID =================
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0

    def compute(self, target, current, dt):
        error = target - current
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return output


# ================= NODE =================
class TeleopPID(Node):
    def __init__(self):
        super().__init__('teleop_pid_ultra')

        # 🔥 FIXED QoS (RELIABLE + LOW LATENCY)
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.pub = self.create_publisher(Twist, '/cmd_vel', qos)

        # Max speeds
        self.max_linear = 0.6
        self.max_angular = 1.5

        # Targets
        self.target_linear = 0.0
        self.target_angular = 0.0

        # Current values (PID output)
        self.current_linear = 0.0
        self.current_angular = 0.0

        # PID tuning (fast response)
        self.linear_pid = PIDController(6.0, 0.0, 0.05)
        self.angular_pid = PIDController(8.0, 0.0, 0.05)

        # 🔥 200 Hz loop
        self.dt = 0.005

        self.settings = termios.tcgetattr(sys.stdin)
        self.last_key_time = time.time()

        print(msg)

    # ================= FIXED KEY INPUT =================
    def get_key(self, timeout=0.01):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)

        if rlist:
            key = sys.stdin.read(1)
            if key == '\x1b':   # arrow key prefix
                key += sys.stdin.read(2)  # read full sequence
        else:
            key = ''

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    # ================= CONTROL =================
    def update(self):
        lin_acc = self.linear_pid.compute(self.target_linear, self.current_linear, self.dt)
        ang_acc = self.angular_pid.compute(self.target_angular, self.current_angular, self.dt)

        self.current_linear += lin_acc * self.dt
        self.current_angular += ang_acc * self.dt

        # clamp small noise
        if abs(self.current_linear) < 1e-3 and self.target_linear == 0:
            self.current_linear = 0.0
        if abs(self.current_angular) < 1e-3 and self.target_angular == 0:
            self.current_angular = 0.0

        twist = Twist()
        twist.linear.x = self.current_linear
        twist.angular.z = self.current_angular
        self.pub.publish(twist)


# ================= MAIN =================
def main():
    rclpy.init()
    node = TeleopPID()

    try:
        while True:
            start = time.time()

            rclpy.spin_once(node, timeout_sec=0.0)

            key = node.get_key()

            if key:
                node.last_key_time = time.time()
                # DEBUG (optional)
                # print(f"Key: {repr(key)}")

            # ===== MOVEMENT =====
            if key == '\x1b[A':   # UP
                node.target_linear = node.max_linear
                node.target_angular = 0.0

            elif key == '\x1b[B': # DOWN
                node.target_linear = -node.max_linear
                node.target_angular = 0.0

            elif key == '\x1b[C': # RIGHT
                node.target_linear = 0.0
                node.target_angular = -node.max_angular

            elif key == '\x1b[D': # LEFT
                node.target_linear = 0.0
                node.target_angular = node.max_angular

            # ===== SPEED CONTROL =====
            elif key in ['w', 'W']:
                node.max_linear = min(node.max_linear + 0.1, 3.0)
                print(f"\rLinear: {node.max_linear:.2f}", end='')

            elif key in ['s', 'S']:
                node.max_linear = max(node.max_linear - 0.1, 0.1)
                print(f"\rLinear: {node.max_linear:.2f}", end='')

            elif key in ['a', 'A']:
                node.max_angular = min(node.max_angular + 0.2, 5.0)
                print(f"\rAngular: {node.max_angular:.2f}", end='')

            elif key in ['d', 'D']:
                node.max_angular = max(node.max_angular - 0.2, 0.2)
                print(f"\rAngular: {node.max_angular:.2f}", end='')

            # ===== BRAKE =====
            elif key == ' ':
                node.target_linear = 0.0
                node.target_angular = 0.0

                node.linear_pid.integral = 0.0
                node.angular_pid.integral = 0.0
                node.linear_pid.prev_error = 0.0
                node.angular_pid.prev_error = 0.0

                node.current_linear = 0.0
                node.current_angular = 0.0

            elif key == '\x03':
                break

            # ===== AUTO STOP =====
            if (time.time() - node.last_key_time) > 0.1:
                node.target_linear = 0.0
                node.target_angular = 0.0

            # ===== UPDATE =====
            node.update()

            # maintain 200 Hz
            elapsed = time.time() - start
            if elapsed < node.dt:
                time.sleep(node.dt - elapsed)

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        twist = Twist()
        node.pub.publish(twist)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        rclpy.shutdown()


if __name__ == '__main__':
    main()
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0

    def compute(self, setpoint, current_value, dt):
        error = setpoint - current_value
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return output

def euler_from_quaternion(x, y, z, w):
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)
    
    return roll_x, pitch_y, yaw_z

class PIDNode(Node):
    def __init__(self):
        super().__init__('pid_controller')
        
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        
        self.linear_pid = PIDController(kp=0.5, ki=0.0, kd=0.1)
        self.angular_pid = PIDController(kp=1.5, ki=0.0, kd=0.1)
        
        self.target_x = 2.0
        self.target_y = 2.0
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        
        self.last_time = self.get_clock().now()
        
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info(f"PID Controller Node Started. Navigating to ({self.target_x}, {self.target_y})")

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        
        q = msg.pose.pose.orientation
        _, _, self.current_yaw = euler_from_quaternion(q.x, q.y, q.z, q.w)

    def control_loop(self):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        if dt <= 0:
            return
            
        self.last_time = now

        distance_error = math.sqrt((self.target_x - self.current_x)**2 + (self.target_y - self.current_y)**2)
        target_angle = math.atan2(self.target_y - self.current_y, self.target_x - self.current_x)
        
        angle_error = target_angle - self.current_yaw
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi

        cmd = Twist()
        
        if distance_error < 0.1:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.get_logger().info("Target Reached!", once=True)
        else:
            cmd.angular.z = self.angular_pid.compute(angle_error, 0.0, dt)
            
           
            if abs(angle_error) > 0.2:
                cmd.linear.x = 0.0
            else:
              
                cmd.linear.x = self.linear_pid.compute(distance_error, 0.0, dt)
                
            cmd.linear.x = max(min(cmd.linear.x, 0.5), -0.5)
            cmd.angular.z = max(min(cmd.angular.z, 1.0), -1.0)

        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = PIDNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

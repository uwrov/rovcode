import threading
import time

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image


class CamNode(Node):
    def __init__(self):
        super().__init__('camera')
        self.declare_parameter('source', 'udp://0.0.0.0:5000')
        self.declare_parameter('fps', 30.0)
        self.declare_parameter('frame_id', 'cam_front_optical_frame')
        self.declare_parameter('best_effort', False)

        src = self.get_parameter('source').value
        if str(src).isdigit():
            src = int(src)
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            self.get_logger().error(f'Could not open {src}')
        else:
            self.get_logger().info(f'Opened {src}')

        reliability = (ReliabilityPolicy.BEST_EFFORT
                       if self.get_parameter('best_effort').value
                       else ReliabilityPolicy.RELIABLE)
        qos = QoSProfile(depth=5, reliability=reliability)
        self.pub = self.create_publisher(Image, 'image_raw', qos)
        self.bridge = CvBridge()

        self.lock = threading.Lock()
        self.frame = None
        self.new_frame = False
        self.read_ok = 0
        self.read_fail = 0
        self.published = 0
        self.running = True
        self.thread = threading.Thread(target=self.reader, daemon=True)
        self.thread.start()

        self.create_timer(1.0 / self.get_parameter('fps').value, self.publish_latest)
        self.create_timer(5.0, self.report)

    def reader(self):
        while self.running:
            ok, frame = self.cap.read()
            if ok:
                with self.lock:
                    self.frame = frame
                    self.new_frame = True
                    self.read_ok += 1
            else:
                self.read_fail += 1
                time.sleep(0.01)

    def publish_latest(self):
        with self.lock:
            if not self.new_frame:
                return
            frame = self.frame
            self.new_frame = False
        msg = self.bridge.cv2_to_imgmsg(frame, 'bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('frame_id').value
        self.pub.publish(msg)
        self.published += 1

    def report(self):
        self.get_logger().info(
            f'frames read={self.read_ok} read failures={self.read_fail} published={self.published}')


def main():
    rclpy.init()
    node = CamNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.running = False
        node.destroy_node()


if __name__ == '__main__':
    main()

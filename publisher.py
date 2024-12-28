import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image 
from cv_bridge import CvBridge
import cv2
  
class ImagePublisher(Node):
  def __init__(self):
    super().__init__('image_publisher')
    self.publisher_ = self.create_publisher(Image, 'video_frames', 10)
    timer_period = 0.1 
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.capture = cv2.VideoCapture(0)
    self.bridge = CvBridge()
    
  def timer_callback(self):
    ret, frame = self.capture.read()
    if ret == True:
        resize = cv2.resize(frame, (frame.shape[1], frame.shape[0]))

        gray = cv2.cvtColor(resize, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)

        contours, frame = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        min_contour_area = 5000
        large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
        frame_out = frame.copy()
        for cnt in large_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            frame_out = cv2.rectangle(resize, (x, y), (x + w, y + h), (255, 255, 0), 3)

        self.publisher_.publish(self.bridge.cv2_to_imgmsg(frame_out))
        self.get_logger().info('Publishing video frame')
   
def main(args=None):
    rclpy.init(args=args)
    image_publisher = ImagePublisher()
    rclpy.spin(image_publisher)
    image_publisher.destroy_node()
    rclpy.shutdown()
   
if __name__ == '__main__':
    main()
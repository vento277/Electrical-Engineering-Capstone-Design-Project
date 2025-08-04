#!/usr/bin/env python3

import rospy
import cv2
import os
from datetime import datetime
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import subprocess

class VideoRecorderNode:
    def __init__(self):
        rospy.init_node('video_recorder_node')
        
        # Parameters
        self.video_dir = rospy.get_param('~video_dir', 
            os.path.expanduser('~/Documents/ELEC491_TL101/icon_drone/videos'))
        self.fps = rospy.get_param('~fps', 30.0)
        self.codec = rospy.get_param('~codec', 'MJPG')
        self.topic = rospy.get_param('~image_topic', '/usb_cam/image_raw')
        self.client_ip = rospy.get_param('~client_ip', '192.168.0.100')
        
        # Create video directory
        os.makedirs(self.video_dir, exist_ok=True)
        
        # Initialize recording state
        self.video_writer = None
        self.bridge = CvBridge()
        self.recording = False
        self.frame_count = 0
        self.client_connected = False
        
        # Monitor for client connection
        self.client_check_timer = rospy.Timer(rospy.Duration(2.0), self.check_client_status)
        
        # Subscribe to image topic
        self.image_sub = rospy.Subscriber(self.topic, Image, self.image_callback, queue_size=10)
        
        rospy.loginfo(f"Video Recorder Node started")
        rospy.loginfo(f"Waiting for client connection from {self.client_ip}")
        rospy.loginfo(f"Videos will be saved to: {self.video_dir}")
        
    def check_client_status(self, event):
        """Check if client is connected"""
        client_active = False
        
        try:
            # Check network connection to client
            ping_result = subprocess.run(['ping', '-c', '1', '-W', '1', self.client_ip], 
                                      capture_output=True, text=True, timeout=3)
            network_reachable = ping_result.returncode == 0
            
            # Check if there are subscribers to the compressed image topic
            try:
                # Simple check - if we have image data and network is reachable, client is likely active
                client_active = network_reachable
            except:
                client_active = False
            
            # Handle connection state changes
            if client_active and not self.client_connected:
                self.on_client_connected()
            elif not client_active and self.client_connected:
                self.on_client_disconnected()
                
        except Exception as e:
            rospy.logwarn(f"Error checking client status: {e}")
    
    def on_client_connected(self):
        """Called when client connects"""
        self.client_connected = True
        rospy.loginfo("Client connected! Preparing to start recording...")
        
        # Generate new filename for this session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_filename = os.path.join(self.video_dir, f"flight_recording_{timestamp}.avi")
        
    def on_client_disconnected(self):
        """Called when client disconnects"""
        if self.client_connected:
            rospy.loginfo("Client disconnected! Stopping recording...")
            self.stop_recording()
            self.client_connected = False
    
    def image_callback(self, msg):
        """Process incoming images and record if client is connected"""
        if not self.client_connected:
            return
            
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Initialize video writer on first frame after client connection
            if self.video_writer is None and self.client_connected:
                height, width, _ = cv_image.shape
                fourcc = cv2.VideoWriter_fourcc(*self.codec)
                self.video_writer = cv2.VideoWriter(
                    self.video_filename, 
                    fourcc, 
                    self.fps, 
                    (width, height)
                )
                if self.video_writer.isOpened():
                    self.recording = True
                    self.frame_count = 0
                    rospy.loginfo(f"Started recording: {os.path.basename(self.video_filename)}")
                    rospy.loginfo(f"Resolution: {width}x{height}, FPS: {self.fps}")
                else:
                    rospy.logerr("Failed to initialize video writer")
                    return
            
            # Write frame to video
            if self.recording and self.video_writer is not None:
                self.video_writer.write(cv_image)
                self.frame_count += 1
                
                # Log progress every 300 frames (10 seconds at 30fps)
                if self.frame_count % 300 == 0:
                    duration = self.frame_count / self.fps
                    rospy.loginfo(f"Recording: {self.frame_count} frames ({duration:.1f}s)")
                    
        except Exception as e:
            rospy.logerr(f"Error in image callback: {e}")
    
    def stop_recording(self):
        """Stop current recording session"""
        if self.video_writer is not None:
            self.recording = False
            self.video_writer.release()
            self.video_writer = None
            
            duration = self.frame_count / self.fps if self.fps > 0 else 0
            rospy.loginfo(f"Recording stopped: {self.frame_count} frames ({duration:.1f}s)")
            
            # Log file size
            if os.path.exists(self.video_filename):
                file_size = os.path.getsize(self.video_filename) / (1024 * 1024)  # MB
                rospy.loginfo(f"Video saved: {os.path.basename(self.video_filename)} ({file_size:.2f} MB)")

if __name__ == '__main__':
    try:
        recorder = VideoRecorderNode()
        
        # Handle shutdown gracefully
        def shutdown_hook():
            rospy.loginfo("Shutting down video recorder...")
            recorder.stop_recording()
        
        rospy.on_shutdown(shutdown_hook)
        rospy.spin()
        
    except rospy.ROSInterruptException:
        pass
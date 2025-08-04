#!/usr/bin/env python3

import rospy
import cv2
import os
from datetime import datetime
from sensor_msgs.msg import Image
from std_srvs.srv import Empty, EmptyResponse
from cv_bridge import CvBridge

class VideoRecorderNode:
    def __init__(self):
        rospy.init_node('video_recorder_node')
        
        # Parameters
        self.video_dir = rospy.get_param('~video_dir', 
            os.path.expanduser('~/Documents/ELEC491_TL101/icon_drone/videos'))
        self.fps = rospy.get_param('~fps', 30.0)
        self.codec = rospy.get_param('~codec', 'MJPG')
        self.topic = rospy.get_param('~image_topic', '/usb_cam/image_raw')
        
        # Create video directory
        os.makedirs(self.video_dir, exist_ok=True)
        
        # Initialize recording state
        self.video_writer = None
        self.bridge = CvBridge()
        self.recording_enabled = False
        self.recording_active = False
        self.frame_count = 0
        self.video_filename = None
        
        # ROS Services for remote control
        self.start_service = rospy.Service('/video_recorder/start_recording', Empty, self.start_recording_callback)
        self.stop_service = rospy.Service('/video_recorder/stop_recording', Empty, self.stop_recording_callback)
        
        # Subscribe to image topic
        self.image_sub = rospy.Subscriber(self.topic, Image, self.image_callback, queue_size=10)
        
        rospy.loginfo("Video Recorder Node Ready")
        rospy.loginfo("Services available:")
        rospy.loginfo("  - /video_recorder/start_recording")
        rospy.loginfo("  - /video_recorder/stop_recording")
        rospy.loginfo("Waiting for start command...")
        
    def start_recording_callback(self, req):
        """Service callback to start recording"""
        if not self.recording_enabled:
            self.recording_enabled = True
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.video_filename = os.path.join(self.video_dir, f"flight_recording_{timestamp}.avi")
            
            rospy.loginfo("Recording ENABLED")
            rospy.loginfo(f"Video file: {os.path.basename(self.video_filename)}")
            rospy.loginfo("Will start with next frame...")
        else:
            rospy.logwarn("Recording already enabled")
        
        return EmptyResponse()
    
    def stop_recording_callback(self, req):
        """Service callback to stop recording"""
        if self.recording_enabled:
            self.recording_enabled = False
            self.stop_recording()
            rospy.loginfo("Recording STOPPED via service")
        else:
            rospy.logwarn("Recording was not active")
        
        return EmptyResponse()
        
    def image_callback(self, msg):
        """Process incoming images and record if enabled"""
        if not self.recording_enabled:
            return
            
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Initialize video writer on first frame after enable
            if self.video_writer is None and self.recording_enabled:
                height, width, _ = cv_image.shape
                fourcc = cv2.VideoWriter_fourcc(*self.codec)
                self.video_writer = cv2.VideoWriter(
                    self.video_filename, 
                    fourcc, 
                    self.fps, 
                    (width, height)
                )
                
                if self.video_writer.isOpened():
                    self.recording_active = True
                    self.frame_count = 0
                    rospy.loginfo("RECORDING STARTED")
                    rospy.loginfo(f"Resolution: {width}x{height}")
                    rospy.loginfo(f"FPS: {self.fps}")
                    rospy.loginfo(f"Codec: {self.codec}")
                else:
                    rospy.logerr("Failed to initialize video writer")
                    return
            
            # Write frame to video
            if self.recording_active and self.video_writer is not None:
                self.video_writer.write(cv_image)
                self.frame_count += 1
                
                # Log progress every 10 seconds (300 frames at 30fps)
                if self.frame_count % 300 == 0:
                    duration = self.frame_count / self.fps
                    rospy.loginfo(f"Recording: {duration:.1f}s ({self.frame_count} frames)")
                    
        except Exception as e:
            rospy.logerr(f"Error in image callback: {e}")
    
    def stop_recording(self):
        """Stop recording session"""
        if self.video_writer is not None:
            self.recording_active = False
            self.video_writer.release()
            self.video_writer = None
            
            duration = self.frame_count / self.fps if self.fps > 0 else 0
            
            # Log file info
            if self.video_filename and os.path.exists(self.video_filename):
                file_size = os.path.getsize(self.video_filename) / (1024 * 1024)  # MB
                rospy.loginfo("RECORDING SAVED:")
                rospy.loginfo(f"  File: {os.path.basename(self.video_filename)}")
                rospy.loginfo(f"  Duration: {duration:.1f}s ({self.frame_count} frames)")
                rospy.loginfo(f"  Size: {file_size:.2f} MB")

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
        rospy.loginfo("Video recorder interrupted")
    except Exception as e:
        rospy.logerr(f"Video recorder error: {e}")
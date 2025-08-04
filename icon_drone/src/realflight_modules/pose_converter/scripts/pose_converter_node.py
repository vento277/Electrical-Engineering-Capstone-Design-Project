#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry

class PoseConverterNode:
    def __init__(self):
        rospy.init_node('pose_converter_node')
        
        # Publisher for converted odometry
        self.odom_pub = rospy.Publisher('/orb_slam3/imu_pose', Odometry, queue_size=10)
        
        # Subscriber to ORB-SLAM3 pose
        self.pose_sub = rospy.Subscriber('/orb_slam3_ros/camera_pose', PoseStamped, self.pose_callback)
        
        rospy.loginfo("Pose Converter Node started")
        rospy.loginfo("Converting /orb_slam3_ros/camera_pose (PoseStamped) -> /orb_slam3/imu_pose (Odometry)")
        
    def pose_callback(self, pose_msg):
        """Convert PoseStamped to Odometry"""
        try:
            # Create Odometry message
            odom_msg = Odometry()
            
            # Copy header
            odom_msg.header = pose_msg.header
            odom_msg.child_frame_id = "base_link"  # or appropriate frame
            
            # Copy pose
            odom_msg.pose.pose = pose_msg.pose
            
            # Set covariance (if known, otherwise use default)
            # For now, set diagonal elements to indicate uncertainty
            odom_msg.pose.covariance[0] = 0.1   # x
            odom_msg.pose.covariance[7] = 0.1   # y
            odom_msg.pose.covariance[14] = 0.1  # z
            odom_msg.pose.covariance[21] = 0.1  # roll
            odom_msg.pose.covariance[28] = 0.1  # pitch
            odom_msg.pose.covariance[35] = 0.1  # yaw
            
            # Twist is typically zero for SLAM poses (no velocity info)
            # Twist covariance - set high uncertainty since we don't have velocity
            for i in range(6):
                odom_msg.twist.covariance[i*7] = 1000.0
            
            # Publish converted message
            self.odom_pub.publish(odom_msg)
            
        except Exception as e:
            rospy.logerr(f"Error converting pose: {e}")

if __name__ == '__main__':
    try:
        converter = PoseConverterNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Pose converter shutting down")
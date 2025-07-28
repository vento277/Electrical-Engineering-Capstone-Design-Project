#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import torch
import yaml
import os
import numpy as np
from image_transport import ImageTransport
from comp import load_model, infer_image

class DepthAnythingNode:
    def __init__(self):
        rospy.init_node('depth_anything_node')
        self.bridge = CvBridge()

        # Parameters
        self.encoder = rospy.get_param("~encoder", "vits")
        self.max_depth = rospy.get_param("~max_depth", 20.0)
        self.model_path = rospy.get_param(
            "~model_path",
            f"{os.environ['HOME']}/checkpoints/depth_anything_v2_metric_hypersim_{self.encoder}.pth"
        )
        self.intrinsics_path = rospy.get_param(
            "~intrinsics_path",
            f"{os.environ['HOME']}/Documents/ELEC491_TL101/icon_drone/src/depth_anything/camera_intrinsics.yml"
        )

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = load_model(self.model_path, self.device, self.max_depth, self.encoder)

        # Load camera intrinsics
        with open(self.intrinsics_path, 'r') as f:
            calib = yaml.safe_load(f)
        self.fx = calib['fx']
        self.fy = calib['fy']

        # Subscribe via image_transport
        self.pub = rospy.Publisher("/depth_anything/image", Image, queue_size=1)
        self.it = ImageTransport(rospy)
        self.sub = self.it.subscribe("/camera/image", "compressed", self.image_callback, queue_size=1)

        rospy.loginfo("depth_anything node started.")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            rospy.logerr(f"cv_bridge error: {e}")
            return

        try:
            depth_map = infer_image(self.model, cv_image, self.fx, self.fy)
            depth_msg = self.bridge.cv2_to_imgmsg(depth_map.astype(np.float32), encoding="32FC1")
            depth_msg.header = msg.header
            self.pub.publish(depth_msg)
        except Exception as e:
            rospy.logerr(f"Inference error: {e}")

if __name__ == "__main__":
    try:
        DepthAnythingNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass


#!/bin/bash

# Setup ROS environment	
source /opt/ros/noetic/setup.bash
source ~/ELEC491_TL101/icon_drone/devel/setup.bash

export ROS_PACKAGE_PATH=${ROS_PACKAGE_PATH}:PATH/ORB_SLAM3/Examples/ROS

# Set display (for RViz if needed)
export DISPLAY=:0

# Reset any existing ROS nodes
pkill -f ros & sleep 3

# Start ROS core in background
roscore & sleep 3

# Set ROS networking (this machine is the ROS master)
export ROS_MASTER_URI=http://192.168.0.179:11311
export ROS_HOSTNAME=192.168.0.179

# Launch IMU (AHRS)
roslaunch fdilink_ahrs ahrs_data.launch & sleep 2

# Launch MAVROS for PX4 connection
roslaunch mavros px4.launch & sleep 2

# Launch USB webcam (raw output)
rosrun usb_cam usb_cam_node \
  _video_device:=/dev/video0 \
  _image_width:=640 \
  _image_height:=480 \
  _pixel_format:=yuyv \
  _camera_frame_id:=usb_cam \
  & sleep 2

# Republish webcam image as compressed for Depth-Anything
rosrun image_transport republish raw in:=/usb_cam/image_raw compressed out:=/camera/image/compressed &


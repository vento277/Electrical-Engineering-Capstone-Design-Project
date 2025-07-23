#!/bin/bash

# Setup ROS environment
source /opt/ros/noetic/setup.bash
source ~/ELEC491_TL101/icon_drone/devel/setup.bash

# Set display (for RViz if needed)
export DISPLAY=:0

# Sync system clock
sudo systemctl restart chrony

# Reset any existing ROS nodes
pkill -f ros & sleep 3

# Start ROS core in background
roscore & sleep 3

# Set ROS networking
export ROS_MASTER_URI=http://192.168.0.179:11311
export ROS_HOSTNAME=192.168.0.179

# Launch necessary modules in background
roslaunch fdilink_ahrs ahrs_data.launch & sleep 2
roslaunch mavros px4.launch & sleep 2

# Launch USB webcam using usb_cam node
rosrun usb_cam usb_cam_node \
  _video_device:=/dev/video0 \
  _image_width:=640 \
  _image_height:=480 \
  _pixel_format:=yuyv \
  _camera_frame_id:=usb_cam \
  & sleep 2

# Republish USB camera image as compressed (for use with Depth-Anything or SLAM)
rosrun image_transport republish raw in:=/usb_cam/image_raw compressed out:=/camera/color/image_raw/compressed &


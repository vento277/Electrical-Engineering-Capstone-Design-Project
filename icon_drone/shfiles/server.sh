#!/bin/bash

source /opt/ros/noetic/setup.bash
source ~/ELEC491_TL101/icon_drone/devel/setup.bash

export DISPLAY=:0

sudo systemctl restart chrony

pkill -f ros & sleep 2

roscore & sleep 2
export ROS_MASTER_URI=http://192.168.0.179:11311
export ROS_HOSTNAME=192.168.0.179

roslaunch fdilink_ahrs ahrs_data.launch & sleep 2
roslaunch mavros px4.launch & sleep 2
roslaunch realsense2_camera rs_camera.launch & sleep 2

rosrun image_transport republish raw in:=/camera/infra1/image_rect_raw compressed out:=/camera/infra1/image_rect_raw/compressed
rosrun image_transport republish raw in:=/camera/infra2/image_rect_raw compressed out:=/camera/infra2/image_rect_raw/compressed


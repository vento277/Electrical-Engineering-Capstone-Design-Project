#!/bin/bash

source /opt/ros/noetic/setup.bash
source ~/Documents/ELEC491_TL101/icon_drone/devel/setup.bash

sudo systemctl restart chrony

pkill -f ros & sleep 3

export ROS_MASTER_URI=http://192.168.0.179:11311
export ROS_HOSTNAME=192.168.0.100

rosrun image_transport republish compressed in:=/image1 raw out:=/vins/image1 &
rosrun image_transport republish compressed in:=/image2 raw out:=/vins/image2 &

sleep 2

roslaunch vins fast_drone_250.launch

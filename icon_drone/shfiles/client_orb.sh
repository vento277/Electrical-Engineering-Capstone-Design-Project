#!/bin/bash

# Setup ROS environment
source /opt/ros/noetic/setup.bash
source ~/Documents/ELEC491_TL101/icon_drone/devel/setup.bash

# Sync system clock
sudo systemctl restart chrony

# Reset any existing ROS nodes
pkill -f ros & sleep 3

# Set ROS networking
export ROS_MASTER_URI=http://192.168.0.179:11311
export ROS_HOSTNAME=192.168.0.100

# Republish compressed webcam image to raw (ORB-SLAM3 expects raw)
rosrun image_transport republish compressed in:=/camera/image/compressed raw out:=/camera/image_raw & sleep 2

# Start Depth-Anything node to infer depth
rosrun depth_anything depth_anything_node.py & sleep 2

# Launch ORB-SLAM3 in RGB-D-Inertial mode
rosrun ORB_SLAM3 ros_rgbd_inertial \
  ~/ORB_SLAM3/Vocabulary/ORBvoc.txt \
  ~/ORB_SLAM3/Examples/RGB-D-Inertial/RealSense_D435i.yaml \
  true &  # Visualization enabled
sleep 2

# Optional: Exploration logic
roslaunch exploration_manager exploration.launch rviz:=false & sleep 2

# Launch controller (ensure it does not conflict with MAVROS)
roslaunch px4ctrl run_ctrl.launch & sleep 2


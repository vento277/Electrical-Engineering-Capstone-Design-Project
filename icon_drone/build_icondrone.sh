#!/bin/bash

set -e
set -x

sudo apt update
sudo apt install -y \
  ros-noetic-serial \
  libvtk7-dev \
  libdw-dev  \
  ros-noetic-realsense2-camera  \
  ros-noetic-nodelet

catkin_make
source devel/setup.bash

#!/bin/bash

set -e
set -x

sudo apt update
sudo apt install -y \
  ros-noetic-serial \
  libvtk7-dev \
  libdw-dev

catkin_make
source devel/setup.bash

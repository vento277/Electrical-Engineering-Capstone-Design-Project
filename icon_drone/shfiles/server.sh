#!/bin/bash

export FFMPEG_LOG_LEVEL=quiet
export AV_LOG_FORCE_NOCOLOR=1

# Setup ROS environment	
source /opt/ros/noetic/setup.bash
source ~/Documents/ELEC491_TL101/icon_drone/devel/setup.bash

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

# Launch MAVROS for PX4 connection (without IMU publishing)
roslaunch mavros px4.launch \
  publish_imu:=false & sleep 2

# Launch USB webcam (raw output) - Updated resolution
rosrun usb_cam usb_cam_node \
  _video_device:=/dev/video6 \
  _image_width:=1280 \
  _image_height:=720 \
  _pixel_format:=mjpeg \
  _framerate:=30 \
  _camera_frame_id:=usb_cam \
  _auto_focus:=false \
  _focus:=0 \
  _suppress_info_output:=true \
  & sleep 2

# Republish webcam image as compressed for Depth-Anything
rosrun image_transport republish raw in:=/usb_cam/image_raw compressed out:=/camera/image &

# Start video recording node (ready to receive commands)
roslaunch video_recorder video_recorder.launch &

echo "Server setup complete. Video recorder ready for remote commands."
echo "To start recording: rosservice call /video_recorder/start_recording"
echo "To stop recording:  rosservice call /video_recorder/stop_recording"

# Keep script running and handle cleanup
trap 'echo "Stopping all processes..."; pkill -f ros; exit' INT TERM

# Wait indefinitely (until Ctrl+C)
while true; do
    sleep 1
done
#!/bin/bash

# Setup ROS environment
source /opt/ros/noetic/setup.bash
source ~/Documents/ELEC491_TL101/icon_drone/devel/setup.bash

# Reset any existing ROS nodes
pkill -f ros & sleep 3

# Set ROS networking
export ROS_MASTER_URI=http://192.168.0.179:11311
export ROS_HOSTNAME=192.168.0.100

# Start video recording on Pi via ROS service
echo "Starting video recording on Raspberry Pi..."
rosservice call /video_recorder/start_recording
sleep 2

# Republish compressed webcam image to raw (ORB-SLAM3 expects raw)
rosrun image_transport republish compressed in:=/camera/image raw out:=/camera/image_raw & sleep 2

# Start Depth-Anything node to infer depth
rosrun depth_anything depth_anything_node.py & sleep 2

# Launch ORB-SLAM3 in Mono-Inertial mode
rosrun orb_slam3_ros ros_mono_inertial_node \
  /home/raeditio/Documents/ELEC491_TL101/icon_drone/src/realflight_modules/ORB_SLAM3/Vocabulary/ORBvoc.txt \
  /home/raeditio/Documents/ELEC491_TL101/icon_drone/src/realflight_modules/ORB_SLAM3/default_camera.yaml &
sleep 2

# Start pose converter (PoseStamped -> Odometry)
rosrun pose_converter pose_converter_node.py & sleep 1

# Optional: Exploration logic
roslaunch exploration_manager exploration.launch rviz:=false & sleep 2

# Launch controller
roslaunch px4ctrl run_ctrl.launch & sleep 2

echo "Client processes started. Video recording active on Pi."
echo "Press Ctrl+C to stop all processes and video recording."

# Handle graceful shutdown
trap 'echo "Stopping video recording on Pi..."; rosservice call /video_recorder/stop_recording; pkill -f ros; exit' INT TERM

# Wait indefinitely
while true; do
    sleep 1
done
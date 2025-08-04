cmake_minimum_required(VERSION 3.0.2)
project(pose_converter)

find_package(catkin REQUIRED COMPONENTS
  rospy
  geometry_msgs
  nav_msgs
)

catkin_package()

# Install scripts
catkin_install_python(PROGRAMS
  scripts/pose_converter_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
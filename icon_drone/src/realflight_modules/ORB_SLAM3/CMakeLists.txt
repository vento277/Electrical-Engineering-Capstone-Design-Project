cmake_minimum_required(VERSION 3.0.2)
project(orb_slam3_ros)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_BUILD_TYPE Release)

# --- Catkin and ROS dependencies ---
find_package(catkin REQUIRED COMPONENTS
  roscpp
  std_msgs
  sensor_msgs
  cv_bridge
  image_transport
)

# --- Other external dependencies ---
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Pangolin REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(Boost REQUIRED COMPONENTS serialization)

# --- Paths ---
set(ORB_SLAM3_ROOT ${PROJECT_SOURCE_DIR})
set(THIRDPARTY_DIR ${ORB_SLAM3_ROOT}/Thirdparty)

# --- Include Directories ---
include_directories(
  ${catkin_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIRS}
  ${Pangolin_INCLUDE_DIRS}
  ${Boost_INCLUDE_DIRS}
  ${ORB_SLAM3_ROOT}
  ${ORB_SLAM3_ROOT}/include
  ${ORB_SLAM3_ROOT}/include/CameraModels
  ${ORB_SLAM3_ROOT}/include/GeometricTools
  ${ORB_SLAM3_ROOT}/include/IMU
  ${THIRDPARTY_DIR}/DBoW2
  ${THIRDPARTY_DIR}/DBoW2/DUtils
  ${THIRDPARTY_DIR}/g2o
  ${THIRDPARTY_DIR}/Sophus
)

# --- Source Files ---
file(GLOB ORB_SRC
  ${ORB_SLAM3_ROOT}/src/*.cc
  ${ORB_SLAM3_ROOT}/src/*.cpp
  ${ORB_SLAM3_ROOT}/src/CameraModels/*.cpp
  ${ORB_SLAM3_ROOT}/src/GeometricTools/*.cc
  ${ORB_SLAM3_ROOT}/src/IMU/*.cc
)

# Remove standalone main.cc if present
list(REMOVE_ITEM ORB_SRC "${ORB_SLAM3_ROOT}/src/main.cc")

# Thirdparty Sources
file(GLOB THIRD_PARTY_DBOW2
  ${THIRDPARTY_DIR}/DBoW2/DBoW2/*.cpp
)
file(GLOB THIRD_PARTY_DUTILS
  ${THIRDPARTY_DIR}/DBoW2/DUtils/*.cpp
)

# ROS wrapper source
set(ROS_WRAPPER_SRC
  ${ORB_SLAM3_ROOT}/src/ros_mono_inertial.cc
)

# --- Catkin Package ---
catkin_package(
  INCLUDE_DIRS include
  LIBRARIES ros_mono_inertial_node
  CATKIN_DEPENDS roscpp std_msgs sensor_msgs cv_bridge image_transport
  DEPENDS OpenCV Eigen3 Boost Pangolin OpenSSL
)

# --- Executable ---
add_executable(ros_mono_inertial_node
  ${ROS_WRAPPER_SRC}
  ${ORB_SRC}
  ${THIRD_PARTY_DBOW2}
  ${THIRD_PARTY_DUTILS}
)

# --- Link libraries ---
target_link_libraries(ros_mono_inertial_node
  ${catkin_LIBRARIES}
  ${OpenCV_LIBRARIES}
  ${Pangolin_LIBRARIES}
  ${Boost_LIBRARIES}
  OpenSSL::Crypto
  ${THIRDPARTY_DIR}/g2o/lib/libg2o.so
)

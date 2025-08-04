cmake_minimum_required(VERSION 3.0.2)
project(ORB_SLAM3)

add_compile_options(-std=c++11)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  tf
  sensor_msgs
  image_transport
  cv_bridge
)

find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIR}
  ../../../
  ../../../include
  ../../../include/CameraModels
)

link_directories(
  ../../../Thirdparty/DBoW2/lib
  ../../../Thirdparty/g2o/lib
  ../../../lib
)

add_executable(rgbd_inertial src/ros_mono_inertial.cc)

target_link_libraries(rgbd_inertial
  ${catkin_LIBRARIES}
  ${OpenCV_LIBS}
  -lboost_system
  ${PROJECT_SOURCE_DIR}/../../../Thirdparty/DBoW2/lib/libDBoW2.so
  ${PROJECT_SOURCE_DIR}/../../../Thirdparty/g2o/lib/libg2o.so
  ${PROJECT_SOURCE_DIR}/../../../lib/libORB_SLAM3.so
)


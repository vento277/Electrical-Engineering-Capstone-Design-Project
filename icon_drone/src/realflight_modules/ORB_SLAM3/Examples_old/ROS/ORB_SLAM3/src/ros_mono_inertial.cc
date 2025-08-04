#include<iostream>
#include<queue>
#include<mutex>
#include<thread>

#include<ros/ros.h>
#include<sensor_msgs/Image.h>
#include<sensor_msgs/Imu.h>
#include<geometry_msgs/PoseStamped.h>
#include<cv_bridge/cv_bridge.h>
#include<opencv2/core/core.hpp>
#include<Eigen/Dense>

#include"System.h"
#include"../include/ImuTypes.h"

using namespace std;
using namespace sensor_msgs;

class ImuGrabber {
public:
    ImuGrabber() = default;
    void GrabImu(const ImuConstPtr &imu_msg) {
        unique_lock<mutex> lock(mBufMutex);
        imuBuf.push(imu_msg);
    }

    queue<ImuConstPtr> imuBuf;
    mutex mBufMutex;
};

class RGBDGrabber {
public:
    RGBDGrabber(ORB_SLAM3::System* pSLAM, ImuGrabber* pImu) : mpSLAM(pSLAM), mpImu(pImu) {}

    void GrabRGB(const ImageConstPtr& msg) {
        unique_lock<mutex> lock(mBufMutex);
        rgbBuf.push(msg);
    }

    void GrabDepth(const ImageConstPtr& msg) {
        unique_lock<mutex> lock(mBufMutex);
        depthBuf.push(msg);
    }

    void SyncAndTrack() {
        ros::NodeHandle nh;
        ros::Publisher pubPose = nh.advertise<geometry_msgs::PoseStamped>("/orb_slam3/imu_pose", 10);

        while(ros::ok()) {
            cv::Mat rgb, depth;
            double t = 0;

            {
                unique_lock<mutex> lock(mBufMutex);
                if (rgbBuf.empty() || depthBuf.empty())
                    continue;
                if (rgbBuf.front()->header.stamp != depthBuf.front()->header.stamp) {
                    if (rgbBuf.front()->header.stamp.toSec() < depthBuf.front()->header.stamp.toSec())
                        rgbBuf.pop();
                    else
                        depthBuf.pop();
                    continue;
                }

                t = rgbBuf.front()->header.stamp.toSec();
                rgb = cv_bridge::toCvShare(rgbBuf.front())->image.clone();
                depth = cv_bridge::toCvShare(depthBuf.front())->image.clone();
                rgbBuf.pop();
                depthBuf.pop();
            }

            vector<ORB_SLAM3::IMU::Point> vImuMeas;
            {
                unique_lock<mutex> lock(mpImu->mBufMutex);
                while (!mpImu->imuBuf.empty() && mpImu->imuBuf.front()->header.stamp.toSec() <= t) {
                    auto imu = mpImu->imuBuf.front();
                    double ti = imu->header.stamp.toSec();
                    cv::Point3f acc(imu->linear_acceleration.x, imu->linear_acceleration.y, imu->linear_acceleration.z);
                    cv::Point3f gyr(imu->angular_velocity.x, imu->angular_velocity.y, imu->angular_velocity.z);
                    vImuMeas.emplace_back(acc, gyr, ti);
                    mpImu->imuBuf.pop();
                }
            }

            Sophus::SE3f Tcw = mpSLAM->TrackRGBD(rgb, depth, t, vImuMeas);

            // Publish pose
            if (!Tcw.translation().isZero()) {
                Eigen::Matrix3f Rcw = Tcw.rotationMatrix();
                Eigen::Vector3f tcw = Tcw.translation();
                Eigen::Matrix3f Rwc = Rcw.transpose();
                Eigen::Vector3f twc = -Rwc * tcw;

                Eigen::Quaternionf q(Rwc);

                geometry_msgs::PoseStamped pose;
                pose.header.stamp = ros::Time::now();
                pose.header.frame_id = "world";
                pose.pose.position.x = twc[0];
                pose.pose.position.y = twc[1];
                pose.pose.position.z = twc[2];
                pose.pose.orientation.x = q.x();
                pose.pose.orientation.y = q.y();
                pose.pose.orientation.z = q.z();
                pose.pose.orientation.w = q.w();

                pubPose.publish(pose);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }

    ORB_SLAM3::System* mpSLAM;
    ImuGrabber* mpImu;

    queue<ImageConstPtr> rgbBuf, depthBuf;
    mutex mBufMutex;
};

int main(int argc, char **argv) {
    ros::init(argc, argv, "rgbd_inertial");
    ros::NodeHandle nh("~");

    if(argc != 3) {
        cerr << "Usage: rosrun ORB_SLAM3 rgbd_inertial path_to_vocabulary path_to_settings" << endl;
        return -1;
    }

    ORB_SLAM3::System SLAM(argv[1], argv[2], ORB_SLAM3::System::IMU_RGBD, true);

    ImuGrabber imugb;
    RGBDGrabber grabber(&SLAM, &imugb);

    ros::Subscriber sub_rgb = nh.subscribe("/camera/color/image_raw", 100, &RGBDGrabber::GrabRGB, &grabber);
    ros::Subscriber sub_depth = nh.subscribe("/depth_anything/image", 100, &RGBDGrabber::GrabDepth, &grabber);
    ros::Subscriber sub_imu = nh.subscribe("/imu", 1000, &ImuGrabber::GrabImu, &imugb);

    std::thread sync_thread(&RGBDGrabber::SyncAndTrack, &grabber);

    ros::spin();

    SLAM.Shutdown();
    return 0;
}


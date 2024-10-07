#include <opencv2/opencv.hpp>
#include <string>
#include <iostream>
#include <stdio.h>
#include <OpenNI.h>
using namespace openni;
using namespace std;
int main() {
    Status rc = OpenNI::initialize();
    if (rc != STATUS_OK){
        printf("Initialize failed%s", OpenNI::getExtendedError());
        return 1;
    }
    char oniPathFile[256] = "./dataset/sculpture.oni";

    Device device;
    rc = device.open(oniPathFile);
    if (rc != STATUS_OK){
        printf("Couldn't open device%s", OpenNI::getExtendedError());
        return 2;
    }

    VideoStream depthStream;
    rc = depthStream.create(device, SENSOR_DEPTH);
    if (rc != STATUS_OK){
        printf("Couldn't create depth stream%s", OpenNI::getExtendedError());
        return 3;
    }

    int width = depthStream.getVideoMode().getResolutionX();
    int height = depthStream.getVideoMode().getResolutionY();
    int fps = depthStream.getVideoMode().getFps();

    std::cout << "Width: " << width << ", Height: " << height << ", FPS: " << fps << std::endl;
    VideoStream colorStream;
    rc = colorStream.create(device, SENSOR_COLOR);
    if (rc != STATUS_OK){
        printf("Couldn't create color stream%s", OpenNI::getExtendedError());
        return 4;
    }

    rc = depthStream.start();
    if (rc != STATUS_OK){
        printf("Couldn't start the depth stream%s", OpenNI::getExtendedError());
        return 5;
    }

    rc = colorStream.start();
    if (rc != STATUS_OK){
        printf("Couldn't start the color stream%s", OpenNI::getExtendedError());
        return 6;
    }

    PlaybackControl* pc = device.getPlaybackControl();
    int total = pc->getNumberOfFrames(depthStream);
    while(1){
        VideoFrameRef depthFrame;
        VideoFrameRef colorFrame;
        depthStream.readFrame(&depthFrame);
        cv::Mat depthImage(cv::Size(depthFrame.getWidth(), depthFrame.getHeight()), CV_16UC1, (void*)depthFrame.getData());
        colorStream.readFrame(&colorFrame);
	    cv::Mat colorImage(cv::Size(colorFrame.getWidth(), colorFrame.getHeight()), CV_8UC3, (void*)colorFrame.getData());
        cv::cvtColor(colorImage, colorImage, CV_BGR2RGB);
        std::cout << "The current frame number being read is: " << colorFrame.getFrameIndex() << std::endl;
        std::cout << "The current loop iteration is: " << total << std::endl;
    }
    depthStream.stop();
    depthStream.destroy();
    colorStream.stop();
    colorStream.destroy();
    device.close();
    OpenNI::shutdown();
    return 0;
}


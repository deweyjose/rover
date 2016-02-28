/* 
 * File:   facefinder.cpp
 * Author: dewey
 *
 * Created on January 27, 2016, 9:53 PM
 */

#include <iostream>
#include <stdio.h>
#include <chrono>

#include "opencv2/objdetect.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"

using namespace std;
using namespace cv;
using namespace std::chrono;

void detectAndDisplay(Mat frame);

String face_cascade_name = "/home/pi/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_alt.xml";

CascadeClassifier face_cascade;

String window_name = "Capture - Face detection";

/* @function main */
int main(int argc, char * argv[]) {

    int width = atoi(argv[1]);
    int height = atoi(argv[2]);
    int fps = atoi(argv[3]);

    VideoCapture capture;
    Mat frame;

    //-- 1. Load the cascades
    if (!face_cascade.load(face_cascade_name)) {
        printf("--(!)Error loading face cascade\n");
        return -1;
    };
    
    //-- 2. Read the video stream
    capture.open(-1);
    capture.set(CV_CAP_PROP_FRAME_HEIGHT, height);
    capture.set(CV_CAP_PROP_FRAME_WIDTH, width);
    capture.set(CV_CAP_PROP_FPS, fps);
    if (!capture.isOpened()) {
        printf("--(!)Error opening video capture\n");
        return -1;
    }
    while (capture.read(frame)) {
        if (frame.empty()) {
            printf(" --(!) No captured frame -- Break!");
            break;
        }
        //-- 3. Apply the classifier to the frame
        detectAndDisplay(frame);
        int c = waitKey(10);
        if ((char) c == 27) {
            break;
        } // escape
    }
    return 0;
}

milliseconds milliseconds_since_epoch() {
    milliseconds ms = duration_cast< milliseconds >(
            system_clock::now().time_since_epoch()
            );
    return ms;
}

void detectAndDisplay(Mat frame) {
    std::vector<Rect> faces;
    Mat frame_gray;
    cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
    equalizeHist(frame_gray, frame_gray);
    //-- Detect faces
    milliseconds before = milliseconds_since_epoch();
    face_cascade.detectMultiScale(frame_gray, faces, 1.1, 2, 0 | CASCADE_SCALE_IMAGE, Size(30, 30));
    milliseconds after = milliseconds_since_epoch();
    cout << after.count() - before.count() << "ms\n";
    for (size_t i = 0; i < faces.size(); i++) {
        cout << faces[i].x << "," << faces[i].y << "\n";
        Point center(faces[i].x + faces[i].width / 2, faces[i].y + faces[i].height / 2);
        ellipse(frame, center, Size(faces[i].width / 2, faces[i].height / 2), 0, 0, 360, Scalar(255, 0, 255), 4, 8, 0);        
    }
    //-- Show what you got
    imshow(window_name, frame);
}

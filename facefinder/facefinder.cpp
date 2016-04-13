/* 
 * File:   facefinder.cpp
 * Author: dewey
 *
 * Created on January 27, 2016, 9:53 PM
 */

#include <iostream>
#include <fstream>
#include <stdio.h>
#include <chrono>

#include "opencv2/objdetect.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/face.hpp"

using namespace std;
using namespace std::chrono;
using namespace cv;
using namespace cv::face;

#define NO_INPUT    -1
#define LEARN_KEY   'l'
#define QUIT_KEY    'q'
#define MAIN_WINDOW "main window"
#define FACE_WINDOW "training faces"

// =========================================================

void detect(Ptr<VideoCapture> capture, Ptr<CascadeClassifier> classifier, Ptr<FaceRecognizer> model);

void learn(Ptr<VideoCapture> capture, Ptr<CascadeClassifier> classifier, Ptr<FaceRecognizer> model, const string& model_path);

std::vector<Mat>& extract_faces(Ptr<VideoCapture> capture, Ptr<CascadeClassifier> classifier, std::vector<Mat>& faces);

Ptr<FaceRecognizer> init_model(const string& path);

Ptr<CascadeClassifier> init_classifier(const string& path);

Ptr<VideoCapture> init_capture(const int width, const int height, const int fps);

milliseconds milliseconds_since_epoch();

bool DISPLAY_MODE_ENABLED = false;
int  FRAME_SAMPLE_SIZE    = 2;

void init_windows();

void show_main(const Mat& frame);

void show_face(const Mat& face);

// =========================================================

int main(int argc, char * argv[]) {    
    String classifier_path  = argv[1];
    int width               = atoi(argv[2]);
    int height              = atoi(argv[3]);
    int fps                 = atoi(argv[4]);    
    string model_path       = string(argv[5]);  
    string mode             = string(argv[6]);
    string display_mode     = string(argv[7]);
    
    FRAME_SAMPLE_SIZE    = atoi(argv[8]);
    DISPLAY_MODE_ENABLED = display_mode.compare("on") == 0;
   
    cout << "Loading face recognizer model " << model_path << "\n";
    Ptr<FaceRecognizer> model = init_model(model_path);
    
    cout << "Loading cascade classifier " << classifier_path << "\n";
    Ptr<CascadeClassifier> classifier = init_classifier(classifier_path);   
    
    cout << "Starting video capture\n";
    Ptr<VideoCapture> capture = init_capture(width, height, fps);
    
    init_windows();
    
    if (mode.compare("learn") == 0) {        
        learn(capture, classifier, model, model_path);         
    } else if (mode.compare("detect") == 0) {
        detect(capture, classifier, model);     
    } else if (mode.compare("")) {
        
    }
    
    return 0;
}

void detect(Ptr<VideoCapture> capture, Ptr<CascadeClassifier> classifier, Ptr<FaceRecognizer> model) {
    for (;;) {
        std::vector<Mat> faces;
        extract_faces(capture, classifier, faces);

        if (!faces.empty()) {
            for (size_t i = 0; i < faces.size(); i++) {                       
                int label = -1;
                double confidence = -1;
                model->predict(faces[i], label, confidence);
                cout << "Predicted label " << label << " confidence " << confidence << "\n";
            }    
        }
    }
}

void init_windows() {
    if (DISPLAY_MODE_ENABLED) {
        try {
            namedWindow(MAIN_WINDOW);
            namedWindow(FACE_WINDOW);
        } catch (...) {

        }
    }
}

void show_face(const Mat& face) {
    if (DISPLAY_MODE_ENABLED) {
        try {
            imshow(FACE_WINDOW, face);   
            waitKey(100);
        } catch (...) {

        }
    }
}

void show_main(const Mat& main) {
    if (DISPLAY_MODE_ENABLED) {
        try {
            imshow(MAIN_WINDOW, main);        
            waitKey(100);
        } catch (...) {

        }
    }
}

int input_number(const char* prompt) {
    while (true) {
        cout << prompt;
        string input;
        getline(cin, input);

        stringstream stream(input);
        int label = 0;
        if (stream >> label) {
            return label;
        } else {
            cout << "invalid input: " << input << "\n";
        }
    }
}

void filter_faces(Ptr<VideoCapture> capture, Ptr<CascadeClassifier> classifier, std::vector<Mat> &faces) {
    std::vector<Mat> potentialFaces;
    extract_faces(capture, classifier, potentialFaces);

    for (int x = 0; x < potentialFaces.size(); ++x) {
        Mat face = potentialFaces.at(x);
        show_face(face);
        if (input_number("accept face? (1==yes, 0==no): ") == 1) {
            faces.push_back(face);
        }
    }
}

void learn(Ptr<VideoCapture> capture, Ptr<CascadeClassifier> classifier, Ptr<FaceRecognizer> model, const string& model_path) {
    int label = input_number("enter a number label: ");
    
    for (int i = 0; i < 20;) {
        std::vector<Mat> faces;
        filter_faces(capture, classifier, faces);
        
        if (!faces.empty()) {            
            std::vector<int> labels;
            for(int x = 0; x < faces.size(); ++x) {                
                labels.push_back(label);
            }
            
            model->update(faces, labels);
            i += faces.size();
        }
    }
    
    model->save(model_path);
}

std::vector<Mat>& extract_faces(Ptr<VideoCapture> capture, Ptr<CascadeClassifier> classifier, std::vector<Mat>& faces) {
    if (FRAME_SAMPLE_SIZE < rand() % 100) {
        return faces;
    }
    
    Mat frame;
    capture->read(frame);
    
    show_main(frame);
    
    std::vector<Rect> face_rects;
    Mat frame_gray;
    cvtColor(frame, frame_gray, COLOR_BGR2GRAY);
    equalizeHist(frame_gray, frame_gray);
        
    classifier->detectMultiScale(frame_gray, face_rects, 1.1, 2, 0 | CASCADE_SCALE_IMAGE, Size(50, 50));
    
    for (size_t i = 0; i < face_rects.size(); i++) {                        
        Mat face(frame_gray, face_rects[i]);     
        show_face(face);
        faces.push_back(face);                
    }        
    
    return faces;
}

Ptr<FaceRecognizer> init_model(const string& model_path) {
    Ptr<FaceRecognizer> model = createLBPHFaceRecognizer();   
    
    std::ifstream infile(model_path);
    if (infile.good()) {
        model->load(model_path.c_str());
    }
    
    return model;
}

Ptr<CascadeClassifier> init_classifier(const string& path) {
    Ptr<CascadeClassifier> classifier = new CascadeClassifier();
    if (!classifier->load(path)) {
        throw "--(!)Error loading face cascade";
    };
    
    return classifier;
}

Ptr<VideoCapture> init_capture(const int width, const int height, const int fps) {
    Ptr<VideoCapture> capture = new VideoCapture();
    capture->open(-1);
    capture->set(CV_CAP_PROP_FRAME_HEIGHT, height);
    capture->set(CV_CAP_PROP_FRAME_WIDTH, width);
    capture->set(CV_CAP_PROP_FPS, fps);
    
    if (!capture->isOpened()) {
        throw "--(!)Error opening video capture";       
    }
    
    return capture;
}

milliseconds milliseconds_since_epoch() {
    return duration_cast< milliseconds >(system_clock::now().time_since_epoch());    
}

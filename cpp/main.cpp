/* This file is not permanent only for testing moving info from cpp to python */

#include <iostream>
#include <cstdio>
#include <string>
#include <array>
#include <memory>
#include <unistd.h>
using namespace std;

//getting user specific directory to execute other files
string get_current_directory() {
    char buffer[FILENAME_MAX];
    if (getcwd(buffer, sizeof(buffer))) {
        return string(buffer);
    } else {
        perror("Error obtaining current directory");
        return "";
    }
}

string get_result_from_model(const char* cmd) {
    
    //open pipe to execute command & read its output
    unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    
    if (!pipe) printf("pipe failed to open");
    
    //read output from python code
    string result;
    array<char, 128> buffer;
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    
    return result;
}

int main() {

    string prompt = "mozart piano";
    string action = "Generate";
    string randomness = "70";
    string filePath = "/Users/willsaliba/Documents/piano.wav";
    printf("Request Generated\n\n");

    //command to execute python code with args
    string currentDir = get_current_directory();
    string cmd = "python3 " + currentDir + "/plugin_requests.py \"" + prompt + "\" \"" + action + "\" " + randomness + " \"" + filePath + "\"";

    //perform command & store result
    string newTrackPath = get_result_from_model(cmd.c_str());

    //print response
    cout << "Response: " << newTrackPath << endl;

    return 0;
}
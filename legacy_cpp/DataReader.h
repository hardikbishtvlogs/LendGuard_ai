#ifndef DATAREADER_H
#define DATAREADER_H

#include <string>
#include <vector>
#include <map>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <random>
#include <cmath>
#include <iostream>

using namespace std;

class DataReader {
public:
    DataReader();
    bool loadCSV(const string& path);
    vector<vector<double>> getTrainFeatures() const;
    vector<int> getTrainLabels() const;
    vector<vector<double>> getValidateFeatures() const;
    vector<int> getValidateLabels() const;
    vector<vector<double>> getTestFeatures() const;
    vector<int> getTestLabels() const;
    vector<double> preprocessUserInput(const map<string,double>& numInput,const map<string,string>& catInput) const;
    vector<string> featureNames() const;
private:
    vector<vector<double>> allFeatures;
    vector<int> allLabels;
    vector<vector<double>> trainF, valF, testF;
    vector<int> trainL, valL, testL;
    map<string,vector<string>> categories;
    vector<string> numericOrder;
    map<string,double> meanMap;
    map<string,double> stdMap;
    vector<string> finalFeatureNames;
    void buildFeatureNames();
};

#endif

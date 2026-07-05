#include "DataReader.h"

using namespace std;

DataReader::DataReader(){}

bool DataReader::loadCSV(const string& path){
    ifstream fin(path);
    if(!fin.is_open()) return false;
    string line;
    vector<string> header;
    if(!getline(fin,line)) return false;
    {
        stringstream ss(line);
        string cell;
        while(getline(ss,cell,',')) header.push_back(cell);
    }
    map<string,int> idx;
    for(size_t i=0;i<header.size();++i) idx[header[i]] = (int)i;
    vector<string> numerics = {"person_age","person_income","cb_person_cred_hist_length","person_emp_length","loan_int_rate","loan_percent_income","loan_amnt"};
    vector<string> categoricals = {"person_home_ownership","loan_intent","loan_grade","cb_person_default_on_file"};
    numericOrder = numerics;
    vector<vector<string>> rawRows;
    while(getline(fin,line)){
        stringstream ss(line);
        string cell;
        vector<string> row;
        while(getline(ss,cell,',')) row.push_back(cell);
        if(row.size() != header.size()) continue;
        rawRows.push_back(row);
    }
    map<string,vector<double>> numericValues;
    for(const string& n : numerics) numericValues[n] = vector<double>();
    for(const auto& row : rawRows){
        bool skip = false;
        for(const string& n : numerics){
            int i = idx[n];
            string v = row[i];
            if(v.empty() || v=="NA") continue;
            try{
                double d = stod(v);
                numericValues[n].push_back(d);
            } catch(...){
                continue;
            }
        }
        for(const string& c : categoricals){
            int i = idx[c];
            string v = row[i];
            if(find(categories[c].begin(),categories[c].end(),v) == categories[c].end()) categories[c].push_back(v);
        }
    }
    for(const string& n : numerics){
        double sum = 0.0;
        for(double v : numericValues[n]) sum += v;
        double m = numericValues[n].empty() ? 0.0 : sum / (double)numericValues[n].size();
        double var = 0.0;
        for(double v : numericValues[n]) var += (v - m) * (v - m);
        double sd = numericValues[n].empty() ? 1.0 : sqrt(var / (double)numericValues[n].size());
        if(sd == 0.0) sd = 1.0;
        meanMap[n] = m;
        stdMap[n] = sd;
    }
    for(const auto& row : rawRows){
        vector<double> feature;
        for(const string& n : numerics){
            int i = idx[n];
            string v = row[i];
            double d = 0.0;
            if(v.empty() || v=="NA"){
                d = meanMap[n];
            } else {
                try{ d = stod(v); } catch(...){ d = meanMap[n]; }
            }
            double z = (d - meanMap[n]) / stdMap[n];
            feature.push_back(z);
        }
        for(const string& c : categoricals){
            int i = idx[c];
            string v = row[i];
            for(const string& cat : categories[c]){
                feature.push_back(v == cat ? 1.0 : 0.0);
            }
        }
        allFeatures.push_back(feature);
        if(idx.find("loan_status") != idx.end()){
            string lab = row[idx["loan_status"]];
            int li = 0;
            try{ li = stoi(lab); } catch(...){ li = lab == "Default" ? 1 : 0; }
            allLabels.push_back(li);
        } else {
            allLabels.push_back(0);
        }
    }
    vector<int> order(allFeatures.size());
    for(size_t i=0;i<order.size();++i) order[i] = (int)i;
    mt19937 rng(42);
    shuffle(order.begin(),order.end(),rng);
    vector<vector<double>> shuffledF;
    vector<int> shuffledL;
    for(int i : order){
        shuffledF.push_back(allFeatures[i]);
        shuffledL.push_back(allLabels[i]);
    }
    size_t N = shuffledF.size();
    size_t ntrain = (size_t)floor(0.7 * (double)N);
    size_t nval = (size_t)floor(0.1 * (double)N);
    for(size_t i=0;i<ntrain;++i){ trainF.push_back(shuffledF[i]); trainL.push_back(shuffledL[i]); }
    for(size_t i=ntrain;i<ntrain+nval;++i){ valF.push_back(shuffledF[i]); valL.push_back(shuffledL[i]); }
    for(size_t i=ntrain+nval;i<N;++i){ testF.push_back(shuffledF[i]); testL.push_back(shuffledL[i]); }
    buildFeatureNames();
    return true;
}

void DataReader::buildFeatureNames(){
    finalFeatureNames.clear();
    for(const string& n : numericOrder) finalFeatureNames.push_back(n);
    for(const auto& kv : categories){
        for(const string& c : kv.second) finalFeatureNames.push_back(kv.first + "_" + c);
    }
}

vector<vector<double>> DataReader::getTrainFeatures() const{ return trainF; }
vector<int> DataReader::getTrainLabels() const{ return trainL; }
vector<vector<double>> DataReader::getValidateFeatures() const{ return valF; }
vector<int> DataReader::getValidateLabels() const{ return valL; }
vector<vector<double>> DataReader::getTestFeatures() const{ return testF; }
vector<int> DataReader::getTestLabels() const{ return testL; }
vector<string> DataReader::featureNames() const{ return finalFeatureNames; }

vector<double> DataReader::preprocessUserInput(const map<string,double>& numInput,const map<string,string>& catInput) const{
    vector<double> out;
    for(const string& n : numericOrder){
        double v = 0.0;
        auto it = numInput.find(n);
        if(it != numInput.end()) v = it->second;
        double z = (v - meanMap.at(n)) / stdMap.at(n);
        out.push_back(z);
    }
    for(const auto& kv : categories){
        const string& key = kv.first;
        const vector<string>& cats = kv.second;
        string val = "";
        auto it = catInput.find(key);
        if(it != catInput.end()) val = it->second;
        for(const string& c : cats) out.push_back(val == c ? 1.0 : 0.0);
    }
    cout << "Preprocessed size: " << out.size() << " first dims: ";
    for(size_t i=0;i<min<size_t>(out.size(),30);++i) cout << out[i] << " ";
    cout << endl;
    return out;
}

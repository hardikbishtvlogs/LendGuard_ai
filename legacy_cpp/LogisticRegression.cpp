#include "LogisticRegression.h"

using namespace std;

LogisticRegression::LogisticRegression(double lr_,int ep_,double regLambda):bias(0.0),lr(lr_),ep(ep_),lambda(regLambda){}

void LogisticRegression::setHyper(double lr_,int ep_,double regLambda){
    lr = lr_;
    ep = ep_;
    lambda = regLambda;
}

double LogisticRegression::sigmoid(double z){
    if(z < -709) return 0.0;
    if(z > 709) return 1.0;
    return 1.0/(1.0+exp(-z));
}

void LogisticRegression::train(const vector<vector<double>>& X,const vector<int>& y){
    if(X.empty()) return;
    int n_samples = (int)X.size();
    int n_features = (int)X[0].size();
    weights.assign(n_features,0.0);
    bias = 0.0;
    for(int epoch=0; epoch<ep; ++epoch){
        vector<double> grad_w(n_features,0.0);
        double grad_b = 0.0;
        double epoch_loss = 0.0;
        for(int i=0;i<n_samples;++i){
            double z = bias;
            for(int j=0;j<n_features;++j) z += weights[j]*X[i][j];
            double y_pred = sigmoid(z);
            double error = y_pred - y[i];
            for(int j=0;j<n_features;++j) grad_w[j] += error * X[i][j];
            grad_b += error;
            double p = y_pred;
            if(p < 1e-12) p = 1e-12;
            if(p > 1-1e-12) p = 1-1e-12;
            epoch_loss += - ( y[i] * log(p) + (1 - y[i]) * log(1 - p) );
        }
        for(int j=0;j<n_features;++j) grad_w[j] = grad_w[j]/(double)n_samples + lambda*weights[j];
        grad_b = grad_b/(double)n_samples;
        for(int j=0;j<n_features;++j) weights[j] -= lr * grad_w[j];
        bias -= lr * grad_b;
        if(epoch % 100 == 0){
            cout << "Epoch " << epoch << " loss: " << epoch_loss / (double)n_samples << " bias: " << bias << " w0: " << weights[0] << endl;
        }
    }
    cout << "Training finished bias: " << bias << " w0: " << weights[0] << endl;
}

double LogisticRegression::predict(const vector<double>& x) const{
    if(x.size() != weights.size()) return 0.5;
    double z = bias;
    for(size_t i=0;i<weights.size();++i) z += weights[i] * x[i];
    return sigmoid(z);
}

const vector<double>& LogisticRegression::getWeights() const{
    return weights;
}

double LogisticRegression::getBias() const{
    return bias;
}

int LogisticRegression::getEpochs() const{
    return ep;
}

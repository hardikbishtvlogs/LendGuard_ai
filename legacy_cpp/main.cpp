#include <QApplication>
#include <QWidget>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QComboBox>
#include <QMessageBox>
#include <QDebug>
#include <QGridLayout>
#include <QIntValidator>
#include <QDoubleValidator>
#include "DataReader.h"
#include "LogisticRegression.h"
#include <iostream>

using namespace std;

double calculateAccuracy(LogisticRegression& model,const vector<vector<double>>& X,const vector<int>& y){
    if(X.empty()) return 0.0;
    int correct = 0;
    for(size_t i=0;i<X.size();++i){
        double p = model.predict(X[i]);
        int pred = p >= 0.5 ? 1 : 0;
        if(pred == y[i]) ++correct;
    }
    return (double)correct/(double)X.size();
}

int main(int argc,char *argv[]){
    QApplication app(argc,argv);
    DataReader dr;
    bool ok = dr.loadCSV("credit_risk_dataset.csv");
    if(!ok){
        QMessageBox::critical(nullptr,"Error","Failed to load dataset");
        return 1;
    }
    vector<vector<double>> Xtrain = dr.getTrainFeatures();
    vector<int> ytrain = dr.getTrainLabels();
    LogisticRegression model(0.01,2000,0.001);
    model.train(Xtrain,ytrain);
    vector<vector<double>> Xval = dr.getValidateFeatures();
    vector<int> yval = dr.getValidateLabels();
    vector<vector<double>> Xtest = dr.getTestFeatures();
    vector<int> ytest = dr.getTestLabels();
    cout << "Validation accuracy: " << calculateAccuracy(model,Xval,yval) << endl;
    cout << "Test accuracy: " << calculateAccuracy(model,Xtest,ytest) << endl;
    QWidget window;
    window.setWindowTitle("Loan Default Predictor (C++/Qt)");
    QVBoxLayout *mainLayout = new QVBoxLayout(&window);
    QLabel *title = new QLabel("Enter Loan Applicant Details");
    title->setAlignment(Qt::AlignCenter);
    mainLayout->addWidget(title);
    QGridLayout *grid = new QGridLayout();
    QLineEdit *ageEdit = new QLineEdit();
    QLineEdit *incomeEdit = new QLineEdit();
    QLineEdit *credEdit = new QLineEdit();
    QLineEdit *empEdit = new QLineEdit();
    QLineEdit *intRateEdit = new QLineEdit();
    QLineEdit *loanPctEdit = new QLineEdit();
    QLineEdit *loanAmtEdit = new QLineEdit();
    QComboBox *homeBox = new QComboBox();
    QComboBox *intentBox = new QComboBox();
    QComboBox *gradeBox = new QComboBox();
    QComboBox *defaultBox = new QComboBox();
    ageEdit->setPlaceholderText("Enter Age (years)");
    incomeEdit->setPlaceholderText("Enter Annual Income ($)");
    credEdit->setPlaceholderText("Enter Credit History Length (years)");
    empEdit->setPlaceholderText("Enter Employment Length (years)");
    intRateEdit->setPlaceholderText("Enter Interest Rate (%)");
    loanPctEdit->setPlaceholderText("Enter Loan % of Income");
    loanAmtEdit->setPlaceholderText("Enter Loan Amount ($)");
    QIntValidator *intVal = new QIntValidator(0,10000);
    ageEdit->setValidator(intVal);
    credEdit->setValidator(intVal);
    empEdit->setValidator(intVal);
    loanAmtEdit->setValidator(new QIntValidator(0,100000000));
    QDoubleValidator *dblVal = new QDoubleValidator(0,100000000,6);
    incomeEdit->setValidator(dblVal);
    intRateEdit->setValidator(new QDoubleValidator(0,100,6));
    loanPctEdit->setValidator(new QDoubleValidator(0,100,6));
    map<string,vector<string>> cats;
    vector<string> c1 = {"RENT","OWN","MORTGAGE","OTHER"};
    vector<string> c2 = {"EDUCATION","MEDICAL","PERSONAL","HOMEIMPROVEMENT","DEBTCONSOLIDATION"};
    vector<string> c3 = {"A","B","C","D","E","F","G"};
    vector<string> c4 = {"Y","N"};
    for(const string& s : c1) homeBox->addItem(QString::fromStdString(s));
    for(const string& s : c2) intentBox->addItem(QString::fromStdString(s));
    for(const string& s : c3) gradeBox->addItem(QString::fromStdString(s));
    for(const string& s : c4) defaultBox->addItem(QString::fromStdString(s));
    grid->addWidget(new QLabel("Age (years):"),0,0);
    grid->addWidget(ageEdit,0,1);
    grid->addWidget(new QLabel("Annual Income ($):"),1,0);
    grid->addWidget(incomeEdit,1,1);
    grid->addWidget(new QLabel("Credit History Length (years):"),2,0);
    grid->addWidget(credEdit,2,1);
    grid->addWidget(new QLabel("Employment Length (years):"),3,0);
    grid->addWidget(empEdit,3,1);
    grid->addWidget(new QLabel("Interest Rate (%):"),4,0);
    grid->addWidget(intRateEdit,4,1);
    grid->addWidget(new QLabel("Loan % of Income:"),5,0);
    grid->addWidget(loanPctEdit,5,1);
    grid->addWidget(new QLabel("Loan Amount ($):"),6,0);
    grid->addWidget(loanAmtEdit,6,1);
    grid->addWidget(new QLabel("Home Ownership:"),7,0);
    grid->addWidget(homeBox,7,1);
    grid->addWidget(new QLabel("Loan Intent:"),8,0);
    grid->addWidget(intentBox,8,1);
    grid->addWidget(new QLabel("Loan Grade:"),9,0);
    grid->addWidget(gradeBox,9,1);
    grid->addWidget(new QLabel("Default On File:"),10,0);
    grid->addWidget(defaultBox,10,1);
    mainLayout->addLayout(grid);
    QPushButton *predictBtn = new QPushButton("Predict Default Risk");
    QLabel *resultLabel = new QLabel("Awaiting Prediction...");
    resultLabel->setAlignment(Qt::AlignCenter);
    mainLayout->addWidget(predictBtn);
    mainLayout->addWidget(resultLabel);
    QObject::connect(predictBtn,&QPushButton::clicked,[=,&dr,&model,&resultLabel]() mutable {
        QString a = ageEdit->text();
        QString inc = incomeEdit->text();
        QString cred = credEdit->text();
        QString emp = empEdit->text();
        QString ir = intRateEdit->text();
        QString lp = loanPctEdit->text();
        QString amt = loanAmtEdit->text();
        QString home = homeBox->currentText();
        QString intent = intentBox->currentText();
        QString grade = gradeBox->currentText();
        QString def = defaultBox->currentText();
        cout << "raw age text: " << a.toStdString() << " income: " << inc.toStdString() << endl;
        bool ok1,ok2,ok3,ok4,ok5,ok6,ok7;
        double age = a.toDouble(&ok1);
        double income = inc.toDouble(&ok2);
        double credv = cred.toDouble(&ok3);
        double empv = emp.toDouble(&ok4);
        double intr = ir.toDouble(&ok5);
        double loanpct = lp.toDouble(&ok6);
        double loanamt = amt.toDouble(&ok7);
        if(!ok1 || !ok2 || !ok3 || !ok4 || !ok5 || !ok6 || !ok7){
            QMessageBox::warning(nullptr,"Invalid Input","Please enter valid numeric values");
            return;
        }
        map<string,double> numIn;
        numIn["person_age"] = age;
        numIn["person_income"] = income;
        numIn["cb_person_cred_hist_length"] = credv;
        numIn["person_emp_length"] = empv;
        numIn["loan_int_rate"] = intr;
        numIn["loan_percent_income"] = loanpct;
        numIn["loan_amnt"] = loanamt;
        map<string,string> catIn;
        catIn["person_home_ownership"] = home.toStdString();
        catIn["loan_intent"] = intent.toStdString();
        catIn["loan_grade"] = grade.toStdString();
        catIn["cb_person_default_on_file"] = def.toStdString();
        vector<double> x = dr.preprocessUserInput(numIn,catIn);
        cout << "MODEL BIAS: " << model.getBias() << " WEIGHTS[0]: " << model.getWeights().size() << endl;
        double p = model.predict(x);
        cout << "Predicted prob: " << p << endl;
        QString out;
        if(p >= 0.5) out = QString("HIGH RISK Probability: %1").arg(p);
        else out = QString("LOW RISK Probability: %1").arg(p);
        resultLabel->setText(out);
    });
    window.show();
    return app.exec();
}

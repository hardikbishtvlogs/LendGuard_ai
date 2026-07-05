QT += widgets
# Use C++11 standard for modern language features
CONFIG += c++11

# The name of the application executable
TARGET = LoanPredictor

# Input files
HEADERS += datareader.h \
           LogisticRegression.h

SOURCES += DataReader.cpp \
           LogisticRegression.cpp \
           main.cpp

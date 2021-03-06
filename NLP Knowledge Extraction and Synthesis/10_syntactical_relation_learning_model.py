import sklearn
import os
from typing import List, Any
import re
import pandas as pd
import numpy as np
from numpy import mean
from numpy import std
from itertools import chain
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn import svm
from matplotlib import pyplot


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# csv = os.path.join(os.getcwd(), ("possible_evidence_instances_training_data_2000.csv"))
csv = os.path.join(os.getcwd(), ("possible_evidence_instances_training_data_4000.csv"))
traindata = pd.read_csv(csv)

print(traindata.iloc[:,9:].head())

# define dataset
# X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=5, random_state=1)
y = traindata['Evidence_Truth']
X = traindata.iloc[:,9:]
target_names = [0,1]
X_train, X_test, y_train, y_test = train_test_split(X, y,
        test_size=0.2,
        random_state=23,
        stratify=y)


# print("Gradient Boosting")
# print("===============")
# # evaluate the model
# model = GradientBoostingClassifier()
# cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# n_scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
# print('Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
# n_scores = cross_val_score(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=-1, error_score='raise')
# print('F1 Score: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
# n_scores = cross_val_score(model, X, y, scoring='f1', cv=cv, n_jobs=-1, error_score='raise')
# print('F1 Score: %.3f (%.3f)' % ( mean(n_scores), std(n_scores)))
#
# # fit the model on the whole dataset
# model = GradientBoostingClassifier()
# model.fit(X_train, y_train)
# prediction = model.predict(X_test)
# report = classification_report(y_test, prediction)
# print(report)


print("Random Forest")
print("===============")
# evaluate the model
model = RandomForestClassifier()
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
n_scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
print('Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
n_scores = cross_val_score(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=-1, error_score='raise')
print('F1 Score: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
n_scores = cross_val_score(model, X, y, scoring='f1', cv=cv, n_jobs=-1, error_score='raise')
print('F1 Score: %.3f (%.3f)' % ( mean(n_scores), std(n_scores)))

# fit the model on the whole dataset
model = RandomForestClassifier()
model.fit(X_train.values, y_train.values)
prediction = model.predict(X_test.values)
report = classification_report(y_test.values, prediction)
print(report)
#
# print("Multi-layer Perceptron")
# print("===============")
# # evaluate the model
# model = MLPClassifier(solver='lbfgs',  max_iter= 1000, hidden_layer_sizes=(5, 2))
# cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# n_scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
# print('Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
# n_scores = cross_val_score(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=-1, error_score='raise')
# print('F1 Score: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
# n_scores = cross_val_score(model, X, y, scoring='f1', cv=cv, n_jobs=-1, error_score='raise')
# print('F1 Score: %.3f (%.3f)' % ( mean(n_scores), std(n_scores)))
#
# # fit the model on the whole dataset
# model = MLPClassifier(solver='lbfgs',  max_iter= 1000, hidden_layer_sizes=(5, 2), random_state=1)
# model.fit(X_train, y_train)
# prediction = model.predict(X_test)
# report = classification_report(y_test, prediction)
# print(report)
#
#
#
# print("Support vector machines")
# print("===============")
# # evaluate the model
# model = svm.SVC()
# cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# n_scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
# print('Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
# n_scores = cross_val_score(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=-1, error_score='raise')
# print('F1 Score: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
# n_scores = cross_val_score(model, X, y, scoring='f1', cv=cv, n_jobs=-1, error_score='raise')
# print('F1 Score: %.3f (%.3f)' % ( mean(n_scores), std(n_scores)))
#
# # fit the model on the whole dataset
# model = svm.SVC()
# model.fit(X_train, y_train)
# prediction = model.predict(X_test)
# report = classification_report(y_test, prediction)
# print(report)


# #
# # # # make predictions on rest of evidence instances
csv = os.path.join(os.getcwd(), ("possible_evidence_instances4.csv"))
preddata = pd.read_csv(csv)
preddata.replace({'NaN': -100}, regex=True, inplace=True)
print(preddata.iloc[:500,9:].head())


predictions =[]
for i in range(0, len(preddata)):
    predictions.extend(model.predict([preddata.iloc[i,9:]]))
    if i % 1000 == 0:
        print("Completed instance: ", i)

preddata["Evidence_Truth"] = predictions
print(predictions[0:1000])

preddata.to_csv("predicted_evidence_instances_all.csv", index=False)

trueevidenceintances = preddata.iloc[list(np.where(preddata["Evidence_Truth"] == 1)[0])]
print("Nr of true relation predictions:", len(trueevidenceintances))
trueevidenceintances.drop_duplicates()
print("Nr of true relation predictions (unique):",len(trueevidenceintances))
trueevidenceintances.to_csv("predicted_evidence_instances_true.csv", index=False)



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
from sklearn.metrics import f1_score
from matplotlib import pyplot

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("possible_evidence_instances_training_data600.csv"))
traindata = pd.read_csv(csv)
# replace Nan by -100
traindata.replace({'NaN': -100}, regex=True, inplace=True)

print(traindata.iloc[:500,9:].head())

# define dataset
# X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=5, random_state=1)
y = traindata['Evidence_Truth'].iloc[:500]
X = traindata.iloc[:500,9:]

# evaluate the model
model = GradientBoostingClassifier()
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
n_scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
print('Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))
n_scores = cross_val_score(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=-1, error_score='raise')
print('F1 Score: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))

# fit the model on the whole dataset
model = GradientBoostingClassifier()
model.fit(X, y)



# # make predictions on rest of evidence instances
csv = os.path.join(os.getcwd(), ("possible_evidence_instances.csv"))
preddata = pd.read_csv(csv)
preddata.replace({'NaN': -100}, regex=True, inplace=True)
print(preddata.iloc[:500,9:].head())

predictions =[]
for i in range(0, len(preddata)):
    predictions.extend(model.predict([preddata.iloc[i,9:]]))
preddata["Evidence_Truth"] = predictions
print(predictions[0:1000])

preddata.to_csv("predicted_evidence_instances_all.csv", index=False)

trueevidenceintances = preddata.iloc[list(np.where(preddata["Evidence_Truth"] == 1)[0])]
trueevidenceintances.to_csv("predicted_evidence_instances_true.csv", index=False)









# random forest, support vector model, neural network
# Supervised classification model

# X, y = make_classification(n_samples=1000, n_features=4,
#                            n_informative=2, n_redundant=0,
#                            random_state=0, shuffle=False)
# clf = RandomForestClassifier(max_depth=2, random_state=0)
# clf.fit(X, y)
# RandomForestClassifier(...)
# print(clf.predict([[0, 0, 0, 0]]))
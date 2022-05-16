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
csv = os.path.join(os.getcwd(), ("possible_evidence_instances_training_data.csv"))
data = pd.read_csv(csv)
# replace Nan by -100
data.replace({'NaN': -100}, regex=True, inplace=True)

print(data.iloc[:500,9:].head())

# define dataset
# X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, n_redundant=5, random_state=1)
y = data['Evidence_Truth'].iloc[:500]
X = data.iloc[:500,9:]

# evaluate the model
model = GradientBoostingClassifier()
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
n_scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
print('Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))


# fit the model on the whole dataset
model = GradientBoostingClassifier()
model.fit(X, y)

# f1_scores_perclass = f1_score(y_true=valid_tags, y_pred=pred_tags, average=None, labels=unique_labels)
# f1_weighted_mean = f1_score(y_true=valid_tags, y_pred=pred_tags, average='weighted', labels=unique_labels)

# # make a single prediction
# row = [[2.56999479, -0.13019997, 3.16075093, -4.35936352, -1.61271951, -1.39352057, -2.48924933, -1.93094078, 3.26130366, 2.05692145]]
# yhat = model.predict(row)
# print('Prediction: %d' % yhat[0])

# random forest, support vector model, neural network
# Supervised classification model

# X, y = make_classification(n_samples=1000, n_features=4,
#                            n_informative=2, n_redundant=0,
#                            random_state=0, shuffle=False)
# clf = RandomForestClassifier(max_depth=2, random_state=0)
# clf.fit(X, y)
# RandomForestClassifier(...)
# print(clf.predict([[0, 0, 0, 0]]))
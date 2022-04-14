import os
from typing import List, Any
import re
import pandas as pd
import numpy as np
from itertools import chain

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("disaggregated_evidence_instances.csv"))
pred_Evidence_instances_df = pd.read_csv(csv)
csv = os.path.join(os.getcwd(), ("manually_extracted_evidence_instances.csv"))
manual_Evidence_instances_df = pd.read_csv(csv)
manual_Evidence_instances_df = manual_Evidence_instances_df.iloc[list(np.where(manual_Evidence_instances_df['DOI']!= "10.1080_01441647.2017.1365101.csv")[0])]

articles = set(manual_Evidence_instances_df['DOI'])
pred_evidence_articles = pred_Evidence_instances_df.iloc[[x for x,y in enumerate(pred_Evidence_instances_df['DOI']) if y in articles]]
pred_evidence_articles['BehaviorDeterminant'] = [word.replace("['", "").replace("']","") for word in pred_evidence_articles['BehaviorDeterminant']]


print(articles)
print()
print(pred_evidence_articles)
print()
print(manual_Evidence_instances_df)

unique_BDs_manu = list(dict.fromkeys(manual_Evidence_instances_df['BehaviorDeterminant']))
unique_BDs_pred = list(dict.fromkeys(pred_evidence_articles['BehaviorDeterminant']))
unique_BDs_pred = list(dict.fromkeys(list(chain.from_iterable([word.split(" ; ") for word in unique_BDs_pred]))))
print(sorted(unique_BDs_manu))
print()
print(sorted(unique_BDs_pred))

shared_BDs = [word for word in unique_BDs_manu if word in unique_BDs_pred]
missing_BDs = [word for word in unique_BDs_manu if word not in unique_BDs_pred]

remaining_pred_BDs = [word for word in unique_BDs_pred if word not in shared_BDs]
print(shared_BDs)
print()
print(len(shared_BDs)/len(unique_BDs_manu))

print(sorted(missing_BDs))
print()
print(sorted(remaining_pred_BDs))

print(len([word for word in manual_Evidence_instances_df['BehaviorDeterminant'] if word in shared_BDs])/len(manual_Evidence_instances_df['BehaviorDeterminant']))
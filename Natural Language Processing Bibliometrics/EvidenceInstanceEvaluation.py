import os
from typing import List, Any
import re
import pandas as pd
import numpy as np
from itertools import chain

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("disaggregated_evidence_instances.csv"))
pred_Evidence_instances_df = pd.read_csv(csv)
csv = os.path.join(os.getcwd(), ("Evidence_instances_df.csv"))
pred_Evidence_instances_norelation_df = pd.read_csv(csv)
csv = os.path.join(os.getcwd(), ("manually_extracted_evidence_instances.csv"))
manual_Evidence_instances_df = pd.read_csv(csv)
manual_Evidence_instances_df = manual_Evidence_instances_df.iloc[list(np.where(manual_Evidence_instances_df['DOI']!= "10.1080_01441647.2017.1365101.csv")[0])]

articles = set(manual_Evidence_instances_df['DOI'])
pred_evidence_articles = pred_Evidence_instances_df.iloc[[x for x,y in enumerate(pred_Evidence_instances_df['DOI']) if y in articles]]
pred_evidence_articles['BehaviorDeterminant'] = [word.replace("['", "").replace("']","") for word in pred_evidence_articles['BehaviorDeterminant']]
pred_evidence_articles_norelation = pred_Evidence_instances_norelation_df['BehaviorDeterminant'].iloc[[x for x,y in enumerate(pred_Evidence_instances_norelation_df['DOI']) if y in articles]]
#pred_evidence_articles_norelation = pred_evidence_articles_norelation[np.where(pred_evidence_articles_norelation != "Nan")[0]]
pred_evidence_articles_norelation = list(chain.from_iterable([word.split(" ; ") for word in pred_evidence_articles_norelation if pd.isnull(word) == False]))
print(pred_evidence_articles_norelation)

print(articles)
print()
print(pred_evidence_articles)
print()
print(manual_Evidence_instances_df)

unique_BDs_manu = list(dict.fromkeys(manual_Evidence_instances_df['BehaviorDeterminant']))
unique_BDs_manu = list(dict.fromkeys([word.strip().lower() for word in unique_BDs_manu]))
unique_BDs_pred = list(dict.fromkeys(pred_evidence_articles['BehaviorDeterminant']))
unique_BDs_pred = list(dict.fromkeys(list(chain.from_iterable([word.split(" ; ") for word in unique_BDs_pred]))))
unique_BDs_pred = list(dict.fromkeys([word.strip().lower() for word in unique_BDs_pred]))
pred_evidence_articles_norelation = list(dict.fromkeys([word.strip().lower() for word in pred_evidence_articles_norelation]))

print("unique true BDs: ", sorted(unique_BDs_manu))
print()
print("unique predicted BDs: ",sorted(unique_BDs_pred))
print()
print("unique tot predicted BDs: ", sorted(pred_evidence_articles_norelation))
print()

shared_BDs = [word for word in unique_BDs_manu if word in unique_BDs_pred]
missing_BDs = [word for word in unique_BDs_manu if word not in unique_BDs_pred]
shared_BDs_tot = [word for word in unique_BDs_manu if word in pred_evidence_articles_norelation]

remaining_pred_BDs = [word for word in unique_BDs_pred if word not in shared_BDs]
print("shared BDs: ", len(shared_BDs), sorted(shared_BDs))
print()
print("percentage predicted of unique: ", len(shared_BDs)/len(unique_BDs_manu))
print()
print("Missing BDs: ", len(missing_BDs), sorted(missing_BDs))
print()
print("Falsely predicted: ", sorted(remaining_pred_BDs))
print()
print("percentage overall predicted: ", len([word for word in manual_Evidence_instances_df['BehaviorDeterminant'] if word.strip().lower() in shared_BDs])/len(manual_Evidence_instances_df['BehaviorDeterminant']))
print()

print("shared BDs: ", len(shared_BDs_tot), sorted(shared_BDs_tot))
print()
print("percentage predicted of unique tot: ", len(shared_BDs_tot)/len(unique_BDs_manu))
print()
print("percentage overall predicted tot: ", len([word for word in manual_Evidence_instances_df['BehaviorDeterminant'] if word.strip().lower() in shared_BDs_tot])/len(manual_Evidence_instances_df['BehaviorDeterminant']))



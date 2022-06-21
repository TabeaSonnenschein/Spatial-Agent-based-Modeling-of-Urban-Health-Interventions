import os
import re
import pandas as pd
import numpy as np

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")

csv = os.path.join(os.getcwd(), ("predicted_evidence_instances_true.csv"))
evidence_instances = pd.read_csv(csv)
evidence_instances = evidence_instances[['DOI', 'Sentence', 'Fullsentence', 'BehaviorOption', 'BehaviorDeterminant', 'AssociationType', 'Studygroup', 'Moderator']]

categories = ["consistent", "inconsistent", "significant", "insignificant", "positive", "negative", "correlated", "not correlated"]

evidence_instances["stat_significance"] = ""
evidence_instances["stat_consistency"] = ""
evidence_instances["stat_direction"] = ""
evidence_instances["stat_correl"] = ""

for count, value in enumerate(evidence_instances['AssociationType']):
    statrelat = None
    statconsist = None
    statdirect = None
    statcorrel = None
    if ("inconsistent" in value.lower()) or ("not" in value.lower() and "consistent" in value.lower()):
        statconsist = "inconsistent"
    elif "consistent" in value.lower():
        statconsist = "consistent"
    if "insignificant" in value.lower() or "non-significant" in value.lower() or "non - significant" in value.lower() or ("not" in value.lower() and "significant" in value.lower()):
        statrelat = "insignificant"
    elif ("not" in value.lower() and ("associated" in value.lower() or "related" in value.lower())) or \
            ("no" in value.lower() and ("association" in value.lower() or "relation" in value.lower() or "effect" in value.lower())):
        statrelat = "insignificant"
    elif ("significant" in value.lower()) or ("not" not in value.lower() and ("associated" in value.lower() or "association" in value.lower()
                                                                              or "positive" in value.lower() or "negative" in value.lower()
                                                                              or "relation" in value.lower() or "evidence" in value.lower())):
        statrelat = "significant"
    if "positive" in value.lower():
        statdirect = "positive"
    elif "negative" in value.lower():
        statdirect = "negative"
    if statconsist == "inconsistent":
        statrelat, statdirect = None, None
    if ("not" not in value.lower() and ("correlat" in value.lower() or "relate" in value.lower())):
        statcorrel = "correlated"
    evidence_instances["stat_significance"].iloc[count] = statrelat
    evidence_instances["stat_consistency"].iloc[count] = statconsist
    evidence_instances["stat_direction"].iloc[count] = statdirect
    evidence_instances["stat_correl"].iloc[count] = statcorrel
    print("Result:", statrelat, statconsist, statdirect, statcorrel, value )

evidence_instances.to_csv("classified_evidence_instances.csv", index=False)

print("Number of evidence instances", len(evidence_instances))
evidence_instances.drop_duplicates(inplace=True)
print("Number of unique evidence instances", len(evidence_instances))
evidence_instances["complete"] = 1
for i in range(1, len(evidence_instances)):
    if all([True if x == None else False for x in list(evidence_instances.iloc[i, -5:-1])]):
        evidence_instances["complete"].iloc[i] = 0
    ### here I could add a filter that removes
    ### all evidence instances that are within a question or contain whether

evidence_instances = evidence_instances[evidence_instances["complete"] == 1].iloc[:,:-1]
evidence_instances.drop("AssociationType", axis = 1, inplace = True)
evidence_instances.drop_duplicates(inplace=True)

print("Number of contributing articles", len(set(evidence_instances['DOI'])))
print("Number of unique and complete evidence instances", len(evidence_instances))

evidence_instances.to_csv("unique_evidence_instances.csv", index=False)


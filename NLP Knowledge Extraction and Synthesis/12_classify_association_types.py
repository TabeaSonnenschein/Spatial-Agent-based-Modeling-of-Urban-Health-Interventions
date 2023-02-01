import os
import re
import pandas as pd
import numpy as np

################################################################
## This script classifies association types into categories.
## categories = ["consistent", "inconsistent", "significant", "insignificant", "positive", "negative", "correlated", "not correlated"]
## Careful results might need manual check to be sure!
###############################################################

## Functions
def ClassifyIntoCategories(string):
    """Classify the string capturing the association type into the categories (below) based on keywords.
       consistent, inconsistent, significant, insignificant, positive, negative, correlated, not correlated"""
    statrelat, statconsist, statdirect, statcorrel = None, None, None, None
    if ("inconsistent" in string) or ("not" in string and "consistent" in string):
        statconsist = "inconsistent"
    elif "consistent" in string:
        statconsist = "consistent"
    if "insignificant" in string or "non-significant" in string or "non - significant" in string or (
            "not" in string and "significant" in string):
        statrelat = "insignificant"
    elif ("not" in string and ("associated" in string or "related" in string)) or ("no" in string and (
                    "association" in string or "relation" in string or "effect" in value.lower())):
        statrelat = "insignificant"
    elif ("significant" in string) or ("not" not in string and ("associated" in string or "association" in string
                                            or "positive" in string or "negative" in string
                                            or "relation" in string or "evidence" in string)):
        statrelat = "significant"
    if "positive" in string:
        statdirect = "positive"
    elif "negative" in string:
        statdirect = "negative"
    if statconsist == "inconsistent":
        statrelat, statdirect = None, None
    if ("not" not in string and ("correlat" in string or "relate" in string)):
        statcorrel = "correlated"
    return statrelat, statconsist, statdirect, statcorrel


## Execution
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("predicted_evidence_instances_true.csv"))
evidence_instances = pd.read_csv(csv)
evidence_instances = evidence_instances[['DOI', 'Sentence', 'Fullsentence', 'BehaviorOption', 'BehaviorDeterminant', 'AssociationType', 'Studygroup', 'Moderator']]

# categories = ["consistent", "inconsistent", "significant", "insignificant", "positive", "negative", "correlated", "not correlated"]

evidence_instances["stat_significance"] = ""
evidence_instances["stat_consistency"] = ""
evidence_instances["stat_direction"] = ""
evidence_instances["stat_correl"] = ""

for count, value in enumerate(evidence_instances['AssociationType']):
    statrelat, statconsist, statdirect, statcorrel = ClassifyIntoCategories(value.lower())
    evidence_instances["stat_significance"].iloc[count] = statrelat
    evidence_instances["stat_consistency"].iloc[count] = statconsist
    evidence_instances["stat_direction"].iloc[count] = statdirect
    evidence_instances["stat_correl"].iloc[count] = statcorrel
    print("Result:", statrelat, statconsist, statdirect, statcorrel, value )

# evidence_instances.to_csv("classified_evidence_instances.csv", index=False)

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

#evidence_instances.to_csv("unique_evidence_instances.csv", index=False)


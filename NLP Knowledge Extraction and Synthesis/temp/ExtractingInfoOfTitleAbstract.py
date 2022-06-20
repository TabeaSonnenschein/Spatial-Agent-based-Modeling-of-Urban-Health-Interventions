import os
import pandas as pd
import numpy as np
from itertools import chain

pd.options.display.max_colwidth = 100000

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper\modalchoice literature search")
article_data = pd.read_csv("metareview_details.csv")
# print(article_data.columns)
article_data['filename'] = [( doi.replace("/", "_")) for doi in article_data['doi']]

# print(article_data['filename'] )


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances = pd.read_csv("Evidence_instances_df.csv")
evidence_instances['filename'] = [doi.replace(".csv", "").replace("doi_", "") for doi in evidence_instances['DOI']]
labeled_papers = list(dict.fromkeys(evidence_instances['filename']))


evidence_instances[['Title', 'BehavOptionsInTitle', 'BehavOptionsInAbstract', 'StudyGroupInTitle', 'StudyGroupInAbstract']] = ""
for file in labeled_papers:
    article_data_idx = list(np.where(article_data['filename'] == file)[0])
    evidence_data_idxs = list(np.where(evidence_instances['filename'] == file)[0])
    title = article_data['title'].iloc[article_data_idx].to_string()
    evidence_instances['Title'].iloc[evidence_data_idxs] = title
    title = title.lower()
    BehavOptions = evidence_instances['BehaviorOption'].iloc[evidence_data_idxs]
    BehavOptions = [elm.lower().split(" ; ") for elm in BehavOptions if isinstance(elm, str)]
    BehavOptions = list(dict.fromkeys(list(chain.from_iterable(BehavOptions))))
    BO_inTitle = [elm for elm in BehavOptions if title.find(elm) != -1]
    if len(BO_inTitle) > 1:
        longest_BO = max(BO_inTitle, key=len)
        if all(True for elm in BO_inTitle if elm in longest_BO):
            BO_inTitle = [longest_BO]
    evidence_instances['BehavOptionsInTitle'].iloc[evidence_data_idxs] = " ; ".join(BO_inTitle)
    abstract = article_data['abstract'].iloc[article_data_idx].to_string().lower()
    print(title)
    print(abstract)
    print(BO_inTitle)
    if BO_inTitle == []:
        BO_inAbstract = [elm for elm in BehavOptions if abstract.find(elm) != -1]
        if len(BO_inAbstract) > 1:
            longest_BO = max(BO_inAbstract, key=len)
            if all(True for elm in BO_inAbstract if elm in longest_BO):
                BO_inAbstract = [longest_BO]
        evidence_instances['BehavOptionsInAbstract'].iloc[evidence_data_idxs] = " ; ".join(BO_inAbstract)
        print(BO_inAbstract)
    StudyGroup = evidence_instances['Studygroup'].iloc[evidence_data_idxs]
    StudyGroup = [elm.lower().split(" ; ") for elm in StudyGroup if isinstance(elm, str)]
    StudyGroup = list(dict.fromkeys(list(chain.from_iterable(StudyGroup))))
    SG_inTitle = [elm for elm in StudyGroup if title.find(elm) != -1]
    if len(SG_inTitle) > 1:
        longest_SG = max(SG_inTitle, key=len)
        if all(True for elm in SG_inTitle if elm in longest_SG):
            SG_inTitle = [longest_SG]
    evidence_instances['StudyGroupInTitle'].iloc[evidence_data_idxs] = " ; ".join(SG_inTitle)
    print(SG_inTitle)
    if SG_inTitle == []:
        SG_inAbstract = [elm for elm in StudyGroup if abstract.find(elm) != -1]
        if len(SG_inAbstract) > 1:
            longest_SG = max(SG_inAbstract, key=len)
            if all(True for elm in SG_inAbstract if elm in longest_BO):
                SG_inAbstract = [longest_SG]
        evidence_instances['StudyGroupInAbstract'].iloc[evidence_data_idxs] = " ; ".join(SG_inAbstract)
        print(SG_inAbstract)

evidence_instances['Title'] = [title.replace("Series([], )", "") for title in evidence_instances['Title']]

csv = os.path.join(os.getcwd(), ("Evidence_instances_df.csv"))
evidence_instances.to_csv(csv, index=False)


complete_evidence_Instances = evidence_instances.iloc[list(np.where((evidence_instances['BehaviorDeterminant'].notnull()) & (evidence_instances['AssociationType'].notnull()))[0])]
csv = os.path.join(os.getcwd(), ("Complete_evidence_Instances.csv"))
complete_evidence_Instances.to_csv(csv, index=False)
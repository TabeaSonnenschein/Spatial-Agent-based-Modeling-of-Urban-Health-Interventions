import os
import pandas as pd
import numpy as np
from itertools import chain

pd.options.display.max_colwidth = 100000

######################################################################
## This script can be used to extract Information on Behavior Options
## and Studygroups of Analysis from the Title and Abstract of a Scientific artile
#################################################################################

#Functions
def extendInfofromTitleAbstract(articlesdata, fulllabeledtext, evidenceinstance_df):
    labeled_papers = list(dict.fromkeys(evidenceinstance_df['DOI']))
    evidenceinstance_df[['Title', 'Abstract', 'NrBO_inArticle', 'NrTitleBOappears', 'NrSG_inArticle', 'BehavOptionsInTitle', 'BehavOptionsInAbstract', 'StudyGroupInTitle', 'StudyGroupInAbstract']] = ""
    for file in labeled_papers:
        article_data_idx = list(np.where(articlesdata['filename'] == file)[0])
        evidence_data_idx = list(np.where(evidenceinstance_df['DOI'] == file)[0])
        labeled_words_idx = list(np.where(fulllabeledtext['filename'] == file)[0])
        title = articlesdata['title'].iloc[article_data_idx].to_string()
        evidenceinstance_df['Title'].iloc[evidence_data_idx] = title
        title = title.lower()
        BehavOptions = fulllabeledtext['BehaviorOption'].iloc[labeled_words_idx]
        BehavOptions = [elm.lower().split(" ; ") for elm in BehavOptions if isinstance(elm, str)]
        BehavOptions = list(dict.fromkeys(list(chain.from_iterable(BehavOptions))))
        evidenceinstance_df['NrBO_inArticle'].iloc[evidence_data_idx] = len(BehavOptions)
        BO_inTitle = [elm for elm in BehavOptions if title.find(elm) != -1]
        if len(BO_inTitle) > 1:
            longest_BO = max(BO_inTitle, key=len)
            if all(True for elm in BO_inTitle if elm in longest_BO):
                BO_inTitle = [longest_BO]
        if len(BO_inTitle) > 0:
            evidenceinstance_df['NrTitleBOappears'].iloc[evidence_data_idx] = len([i for i in fulllabeledtext['BehaviorOption'].iloc[labeled_words_idx] if BO_inTitle[0] in str(i)])
        evidenceinstance_df['BehavOptionsInTitle'].iloc[evidence_data_idx] = " ; ".join(BO_inTitle)
        abstract = article_data['abstract'].iloc[article_data_idx].to_string().lower()
        evidenceinstance_df['Abstract'].iloc[evidence_data_idx] = abstract
        print(title)
        print(abstract)
        print(BO_inTitle)
        if BO_inTitle == []:
            BO_inAbstract = [elm for elm in BehavOptions if abstract.find(elm) != -1]
            if len(BO_inAbstract) > 1:
                longest_BO = max(BO_inAbstract, key=len)
                if all(True for elm in BO_inAbstract if elm in longest_BO):
                    BO_inAbstract = [longest_BO]
            evidenceinstance_df['BehavOptionsInAbstract'].iloc[evidence_data_idx] = " ; ".join(BO_inAbstract)
            print(BO_inAbstract)
        StudyGroup = fulllabeledtext['Studygroup'].iloc[labeled_words_idx]
        StudyGroup = [elm.lower().split(" ; ") for elm in StudyGroup if isinstance(elm, str)]
        StudyGroup = list(dict.fromkeys(list(chain.from_iterable(StudyGroup))))
        StudyGroup = [i for i in StudyGroup if i not in ["in", "of", "to"]]
        evidenceinstance_df['NrSG_inArticle'].iloc[evidence_data_idx] = len(StudyGroup)
        SG_inTitle = [elm for elm in StudyGroup if title.find(elm) != -1]
        if len(SG_inTitle) > 1:
            longest_SG = max(SG_inTitle, key=len)
            if all(True for elm in SG_inTitle if elm in longest_SG):
                SG_inTitle = [longest_SG]
        evidenceinstance_df['StudyGroupInTitle'].iloc[evidence_data_idx] = " ; ".join(SG_inTitle)
        print(SG_inTitle)
        if SG_inTitle == []:
            SG_inAbstract = [elm for elm in StudyGroup if abstract.find(elm) != -1]
            if len(SG_inAbstract) > 1:
                longest_SG = max(SG_inAbstract, key=len)
                if all(True for elm in SG_inAbstract if elm in longest_SG):
                    SG_inAbstract = [longest_SG]
            evidenceinstance_df['StudyGroupInAbstract'].iloc[evidence_data_idx] = " ; ".join(SG_inAbstract)
            print(SG_inAbstract)

    evidenceinstance_df['Title'] = [title.replace("Series([], )", "") for title in evidence_instances['Title']]
    return evidenceinstance_df


def find_lastBO_for_missing_BO_info(fulllabeledtext, evidenceinstance_df):
    evidenceinstance_df[['last_BO', 'sent_last_BO', 'sent_distance_lastBO']] = " "
    for count, value in enumerate(evidenceinstance_df['Sentence']):
        if str(evidenceinstance_df['BehaviorOption'].iloc[count]) == "-100":
            labeled_words_idx = list(np.where(fulllabeledtext['filename'] == evidenceinstance_df['DOI'].iloc[count])[0])
            current_idx = list(np.where((fulllabeledtext['filename'] == evidenceinstance_df['DOI'].iloc[count]) & (fulllabeledtext['Sentence'] == evidenceinstance_df['Sentence'].iloc[count]))[0])
            potentialBO = [i for i in fulllabeledtext['BehaviorOption'].iloc[min(labeled_words_idx): min(current_idx)] if str(i) != "nan"]
            sentenceID_BO = [val for cnt, val in enumerate(fulllabeledtext['Sentence'].iloc[min(labeled_words_idx):min(current_idx)]) if str(fulllabeledtext['BehaviorOption'].iloc[labeled_words_idx[cnt-1]]) != "nan"]
            if len(potentialBO) > 0:
                evidenceinstance_df['last_BO'].iloc[count] = potentialBO[-1]
                evidenceinstance_df['sent_last_BO'].iloc[count] = sentenceID_BO[-1]
                evidenceinstance_df['sent_distance_lastBO'].iloc[count] = int(evidenceinstance_df['Sentence'].iloc[count].replace("Sentence: ", "")) - int(evidenceinstance_df['sent_last_BO'].iloc[count].replace("Sentence: ", ""))
                print(potentialBO[-1])
    return evidenceinstance_df

def select_correct_imputation(evidenceinstance_df):
    evidenceinstance_df[["BOimputed", "SGimputed"]] = ""
    for count, value in enumerate(evidenceinstance_df['BehaviorOption']):
        if value == "-100":
            if len(evidenceinstance_df['BehavOptionsInTitle'].iloc[count]) > 0:
                if ((evidenceinstance_df['BehavOptionsInTitle'].iloc[count] == evidenceinstance_df['last_BO'].iloc[count]) |
                    (evidenceinstance_df['BehavOptionsInTitle'].iloc[count] in evidenceinstance_df['Fullsentence'].iloc[count])):
                    evidenceinstance_df['BehaviorOption'].iloc[count] = evidenceinstance_df['BehavOptionsInTitle'].iloc[count]
                    evidenceinstance_df["BOimputed"].iloc[count] = 1
                elif ((evidenceinstance_df['BehavOptionsInTitle'].iloc[count] in evidenceinstance_df['last_BO'].iloc[count]) & (evidenceinstance_df['sent_distance_lastBO'].iloc[count] <3)):
                    if ";" in evidenceinstance_df['last_BO'].iloc[count]:
                        BOset = evidenceinstance_df['last_BO'].iloc[count].split(" ; ")
                        BOset = list(dict.fromkeys([i for i in BOset if evidenceinstance_df['BehavOptionsInTitle'].iloc[count] in i]))
                        if len(BOset) == 1:
                            evidenceinstance_df['BehaviorOption'].iloc[count] = BOset[0]
                    else:
                        evidenceinstance_df['BehaviorOption'].iloc[count] = evidenceinstance_df['last_BO'].iloc[count]
                        evidenceinstance_df["BOimputed"].iloc[count] = 1
                elif ((evidenceinstance_df['last_BO'].iloc[count] in evidenceinstance_df['BehavOptionsInTitle'].iloc[count]) & (evidenceinstance_df['NrTitleBOappears'].iloc[count] > 20)):
                    evidenceinstance_df['BehaviorOption'].iloc[count] = evidenceinstance_df['BehavOptionsInTitle'].iloc[count]
                    evidenceinstance_df["BOimputed"].iloc[count] = 1
                elif ((evidenceinstance_df['NrTitleBOappears'].iloc[count]  > evidenceinstance_df['NrBO_inArticle'].iloc[count] )| (evidenceinstance_df['NrTitleBOappears'].iloc[count] > 25)):
                    evidenceinstance_df['BehaviorOption'].iloc[count] = evidenceinstance_df['BehavOptionsInTitle'].iloc[count]
                    evidenceinstance_df["BOimputed"].iloc[count] = 1
                elif evidenceinstance_df['sent_distance_lastBO'].iloc[count] <3:
                    if ";" in evidenceinstance_df['last_BO'].iloc[count]:
                        BOset = evidenceinstance_df['last_BO'].iloc[count].split(" ; ")
                        print(BOset)
                        one = list(dict.fromkeys([i for i in BOset if (i in evidenceinstance_df['BehaviorOption'].iloc[count-1]) or (i in evidenceinstance_df['BehaviorOption'].iloc[count+1]) or (str(evidenceinstance_df['BehaviorOption'].iloc[count-1]) in i) or (str(evidenceinstance_df['BehaviorOption'].iloc[count+1]) in i)]))
                        print(one)
                        if len(one) == 1:
                            evidenceinstance_df['BehaviorOption'].iloc[count] = one[0]
                        elif len(one) > 1:
                            evidenceinstance_df['BehaviorOption'].iloc[count] = min(one, key=len)
                        else:
                            one = [i for i in one if any(True for x in one if x in i)]
                            if len(one) == 1:
                                evidenceinstance_df['BehaviorOption'].iloc[count] = one[0]
                            one = list(dict.fromkeys([i for i in BOset if i in evidenceinstance_df['BehaviorOption'].iloc[count-5:count+5]]))
                            if len(one) == 1:
                                evidenceinstance_df['BehaviorOption'].iloc[count] = one[0]
                    else:
                        evidenceinstance_df['BehaviorOption'].iloc[count] = evidenceinstance_df['last_BO'].iloc[count]
                        evidenceinstance_df["BOimputed"].iloc[count] = 1
            else:
                if isinstance(evidenceinstance_df['sent_distance_lastBO'].iloc[count], int):
                    if evidenceinstance_df['sent_distance_lastBO'].iloc[count] < 3:
                        evidenceinstance_df['BehaviorOption'].iloc[count] = evidenceinstance_df['last_BO'].iloc[count]
                        evidenceinstance_df["BOimputed"].iloc[count] = 1

    for count, value in enumerate(evidenceinstance_df['Studygroup']):
        if ((value == "-100") & (evidenceinstance_df['StudyGroupInTitle'].iloc[count] != "")):
            evidenceinstance_df['Studygroup'].iloc[count] = evidenceinstance_df['StudyGroupInTitle'].iloc[count]
            evidenceinstance_df["SGimputed"].iloc[count] = 1

    return evidenceinstance_df


# Execution
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper\modalchoice literature search")
article_data = pd.read_csv("metareview_details.csv")
article_data['filename'] = [( doi.replace("/", "_")) for doi in article_data['doi']]

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
labeled_words = pd.read_csv("Evidence_instances_df.csv")
labeled_words['filename'] = [doi.replace(".csv", "").replace("doi_", "") for doi in labeled_words['DOI']]
evidence_instances = pd.read_csv("unique_evidence_instances.csv")
evidence_instances['DOI'] = [doi.replace(".csv", "").replace("doi_", "") for doi in evidence_instances['DOI']]


evidence_instances = extendInfofromTitleAbstract(articlesdata = article_data, fulllabeledtext = labeled_words, evidenceinstance_df= evidence_instances)
evidence_instances = find_lastBO_for_missing_BO_info(fulllabeledtext = labeled_words, evidenceinstance_df= evidence_instances)
evidence_instances = select_correct_imputation(evidenceinstance_df = evidence_instances)

csv = os.path.join(os.getcwd(), ("unique_evidence_instances_interpolatingMissinginfo.csv"))
evidence_instances.to_csv(csv, index=False)

csv = os.path.join(os.getcwd(), ("unique_evidence_instances_clean.csv"))
evidence_instances.iloc[:, :11].to_csv(csv, index=False)
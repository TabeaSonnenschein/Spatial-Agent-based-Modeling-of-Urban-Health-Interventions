import os
from typing import List, Any
import pandas as pd
import numpy as np
import nltk
import utils.TokentoRelatUtils

############ Abbreviation list
## ST = study, BD = Behavior Determinant, BO = Behavior Choice Option, AT = Association Type, SG = Study Group, MO = Moderator

# Settings
# mode = "IOB"
mode = "IO"
TagToWordExtension = False
manual_label = False

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
if manual_label == True:
    listOfFiles = ["labeled_articles_joined_IO - Copy.csv"]
else:
    listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "predict_labeled"))

instance_ST, instance_BD, instance_BO, instance_AT, instance_SG, instance_MO, sentenceid, fullsentence, AT_POS, BO_POS, BD_POS, sentence_POS = [], [], [], [], [], [], [], [], [], [], [], []
len_instance_before = 0
for file in listOfFiles:
    print("Processing file: ", file)
    if manual_label == True:
        labeled_data = pd.read_csv(os.path.join(os.getcwd(), ("manually_labeled/" + file)), encoding="latin1")
    else:
        labeled_data = pd.read_csv(os.path.join(os.getcwd(), ("predict_labeled/" + file)), encoding="latin1")
    # labeled_data = labeled_data.iloc[list(np.where((labeled_data['Word'] != "[SEP]") & (labeled_data['Word'] != "[CLS]"))[0])]
    labeled_data['Tag'].iloc[list(np.where((labeled_data['Word'] == "[SEP]") | (labeled_data['Word'] == "[CLS]") | (labeled_data['Word'] == ".") | (labeled_data['Word'] == "s")| (labeled_data['Word'] == "'"))[0])] = 'O'
    labeled_data = addPOS(labeled_data)
    AT_words = list(np.where((labeled_data['Word'] == 'significant') | (
            labeled_data['Word'] == 'insignificant') | (
            labeled_data['Word'] == 'consistent') | (
            labeled_data['Word'] == 'Consistent') | (
            labeled_data['Word'] == 'associated') | (
            labeled_data['Word'] == 'inconsistent') | (
            labeled_data['Word'] == 'Associations') | (
            labeled_data['Word'] == 'associations') | (
            labeled_data['Word'] == 'Association') | (
            labeled_data['Word'] == 'association') | (
            labeled_data['Word'] == 'significantly') | (
            labeled_data['Word'] == 'insignificantly') | (
            # labeled_data['Word'] == 'relationships') | (
            # labeled_data['Word'] == 'relationship') | (
            # labeled_data['Word'] == 'mixed') | (
            # labeled_data['Word'] == 'positive') | (
            # labeled_data['Word'] == 'Positive') | (
            # labeled_data['Word'] == 'negative') | (
            # labeled_data['Word'] == 'Negative') | (
            labeled_data['Word'] == 'influence'))[0])
    labeled_data['Tag'].iloc[AT_words] = 'I-assocType'
    # AT_words = list(np.where((labeled_data['Word'] == 'related') & (labeled_data['POS'] == "VBN")))
    # labeled_data['Tag'].iloc[AT_words] = 'I-assocType'
    AT_words = list(np.where(labeled_data['Tag'] == 'I-assocType')[0])
    x = []
    x.extend(idx - 1 for idx in AT_words if labeled_data['Word'].iloc[idx - 1] in ["non", "not", "Non", "Not", "no", "No", "nil"])
    x.extend(idx - 2 for idx in AT_words if labeled_data['Word'].iloc[idx - 2] in ["non", "not", "Non", "Not", "no", "No", "Lack", "lack", "nil"])
    labeled_data['Tag'].iloc[x] = 'I-assocType'
    AT_words = list(np.where(labeled_data['Tag'] == 'I-assocType')[0])
    x = [x+1 for x in AT_words if (x+2 in AT_words) and (labeled_data['Word'].iloc[x+1] in ["of", ",", "and", "for", "to", "a", "the"])]
    x.extend((x+2 for x in AT_words if (x+3 in AT_words) and (labeled_data['Word'].iloc[x+1] in ["of", ",", "and", "for", "to", "a", "the"]) and (labeled_data['Word'].iloc[x+2] in ["of", ",", "and", "for", "to", "a", "the"])))
    labeled_data['Tag'].iloc[x] = 'I-assocType'
    dataframe = extendVariableNamesToNeighboringAdjectNouns(labeled_data, ["I-behavDeterm", "I-behavOption", "I-moderator"])
    dataframe = extendAssociationTypesToNeighboringAdjectNegatives(labeled_data)
    if TagToWordExtension:
        labeled_data = extendTagsToAllEqualWordSeq(labeled_data)
    labeled_data = extendSpecificTagsToAllEqualWordSeq(labeled_data, "I-behavOption")
    sentences = list(dict.fromkeys(labeled_data['Sentence']))
    for sentence in sentences:
        sentence_idx_range = np.where(labeled_data['Sentence'] == sentence)[0]
        sent_POS = labeled_data['POS'].iloc[sentence_idx_range]
        if any(labeled_data['Tag'].iloc[sentence_idx_range] != 'O'):
            if mode == "IOB":
                # if IOB has sufficient quality to distinguish ingroup classification
                AT_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-assocType")[0])
                AT_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range]== "I-assocType")[0])
                BO_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-behavOption")[0])
                BO_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavOption")[0])
                BD_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-behavDeterm")[0])
                BD_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavDeterm")[0])
                SG_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-studygroup")[0])
                SG_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-studygroup")[0])
                MO_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-moderator")[0])
                MO_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-moderator")[0])
                instance_AT.append(" ; ".join(IOB_sequence_tracing(B_indx_list=AT_indx_B, I_index_list=AT_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BO.append(" ; ".join(IOB_sequence_tracing(B_indx_list=BO_indx_B, I_index_list=BO_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BD.append(" ; ".join(IOB_sequence_tracing(B_indx_list=BD_indx_B, I_index_list=BD_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_SG.append(" ; ".join(IOB_sequence_tracing(B_indx_list=SG_indx_B, I_index_list=SG_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_MO.append(" ; ".join(IOB_sequence_tracing(B_indx_list=MO_indx_B, I_index_list=MO_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))

            if mode == "IO":
                # if IOB has not sufficient quality to distinguish ingroup classification, or IO labeling was used
                AT_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-assocType")[0])
                BO_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavOption")[0])
                BD_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavDeterm")[0])
                SG_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-studygroup")[0])
                MO_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-moderator")[0])
                instance_AT.append(" ; ".join(IO_sequence_tracing(indx_list= AT_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BO.append(" ; ".join(IO_sequence_tracing(indx_list=BO_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BD.append(" ; ".join(IO_sequence_tracing(indx_list=BD_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_SG.append(" ; ".join(IO_sequence_tracing(indx_list=SG_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_MO.append(" ; ".join(IO_sequence_tracing(indx_list=MO_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                AT_POS.append(" ; ".join(sent_POS.iloc[AT_indx]))
                BO_POS.append(" ; ".join(sent_POS.iloc[BO_indx]))
                BD_POS.append(" ; ".join(sent_POS.iloc[BD_indx]))
            sentenceid.append(sentence)
            sentence_POS.append(" ; ".join(sent_POS[1:-1]))
            sentence_txt = " ".join(str(e) for e in labeled_data['Word'].iloc[sentence_idx_range])
            fullsentence.append(sentence_txt.replace("[CLS]", "").replace("[SEP]", ""))

    instance_ST.extend([file] * (len(instance_AT)-len_instance_before))
    len_instance_before = len(instance_AT)


if TagToWordExtension:
    file_name_suffix = "_enhanced"
else:
    file_name_suffix = ""


if manual_label:
    file_name_suffix2 = "_ManualLabel"
else:
    file_name_suffix2 = ""

Evidence_instances_df = pd.DataFrame({'DOI': instance_ST, 'Sentence': sentenceid, 'BehaviorOption': instance_BO, 'BehaviorDeterminant': instance_BD, 'AssociationType': instance_AT, 'Studygroup': instance_SG, 'Moderator': instance_MO ,  'Fullsentence': fullsentence, 'BO_POS': BO_POS, 'BD_POS': BD_POS, 'AT_POS': AT_POS, 'sentence_POS': sentence_POS })
print(Evidence_instances_df.head())


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("Evidence_instances_df"+ file_name_suffix2 +file_name_suffix + ".csv"))
Evidence_instances_df.to_csv(csv, index=False)

complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'] != "") & (Evidence_instances_df['AssociationType'] != ""))[0])]
print(complete_evidence_Instances.head())
csv = os.path.join(os.getcwd(), ("Complete_evidence_Instances"+ file_name_suffix2 +file_name_suffix + ".csv"))
complete_evidence_Instances.to_csv(csv, index=False)


if manual_label == False:
    BDs, freq_BD = [], []
    for BD_instance in complete_evidence_Instances['BehaviorDeterminant']:
        BDs.extend(BD_instance.split(" ; "))
    unique_BD = list(dict.fromkeys(BDs))
    for BD in unique_BD:
        freq_BD.append(BDs.count(BD))
    csv = os.path.join(os.getcwd(), ("unique_BehaviorDeterminants.csv"))
    pd.DataFrame({'BehaviorDeterm': unique_BD, 'Freq': freq_BD}).to_csv(csv, index=False)

    BOs, freq_BO = [], []
    for BO_instance in complete_evidence_Instances['BehaviorOption']:
        BOs.extend(BO_instance.split(" ; "))
    unique_BO = list(dict.fromkeys(BOs))
    for BO in unique_BO:
        freq_BO.append(BOs.count(BO))
    csv = os.path.join(os.getcwd(), ("unique_BehaviorOptions.csv"))
    pd.DataFrame({'BehaviorOption': unique_BO, 'Freq': freq_BO} ).to_csv(csv, index=False)

    unique_AT = []
    for AT_instance in complete_evidence_Instances['AssociationType']:
        unique_AT.extend(AT_instance.split(" ; "))
    unique_AT = list(dict.fromkeys(unique_AT))
    csv = os.path.join(os.getcwd(), ("unique_AssociationTypes.csv"))
    pd.DataFrame(unique_AT).to_csv(csv, index=False)


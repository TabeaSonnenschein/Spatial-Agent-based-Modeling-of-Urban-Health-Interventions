import os
from typing import List, Any

import pandas as pd
import numpy as np

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "predict_labeled"))

############ Abbreviation list
## ST = study, BD = Behavior Determinant, BO = Behavior Choice Option, AT = Association Type, SG = Study Group, MO = Moderator

# Settings
# mode = "IOB"
mode = "IO"
TagToWordExtension = False


def IOB_sequence_tracing(B_indx_list, I_index_list, Words_data):
    tags = []
    for indx in B_indx_list:
        tag_string = str(Words_data.iloc[indx])
        if indx + 1 in I_index_list:
            tag_string = tag_string + " " + str(Words_data.iloc[indx + 1])
            nr_concatenated_words = 1
            for x in range(2, len(I_index_list)+1):
                if all(elem in I_index_list  for elem in range(indx + 1, indx + x+1)):
                    tag_string = tag_string + " " + str(Words_data.iloc[indx + x])
                    nr_concatenated_words = x
            I_index_list = [I_index_list.remove(indx + w) for w in range(1,nr_concatenated_words)]
        tags.append(tag_string)
    I_index_list = [i for i in I_index_list if i]
    if bool(I_index_list):
        for I_indx in I_index_list:
            tags.append(Words_data.iloc[I_indx])
    return tags

def IO_sequence_tracing(indx_list, Words_data):
    tags = []
    if len(indx_list) > 1:
        already_included = 0
        for indx in indx_list:
            if indx > already_included:
                tag_string = str(Words_data.iloc[indx])
                if indx + 1 in indx_list:
                    tag_string = tag_string + " " + str(Words_data.iloc[indx + 1])
                    already_included = indx + 1
                    for x in range(2, len(indx_list)+1):
                        if all(elem in indx_list  for elem in range(indx + 1, indx + x+1)):
                            tag_string = tag_string + " " + str(Words_data.iloc[indx + x])
                            already_included = indx + x
                tags.append(tag_string)
    else:
        if bool(indx_list):
            tags.append(Words_data.iloc[indx_list[0]])
    return tags

def extendTagsToAllEqualWordSeq(dataframe):
    labels = list(dict.fromkeys(dataframe['Tag']))
    labels.remove('O')
    for label in labels:
        label_indices = list(np.where(dataframe['Tag'] == label)[0])
        unique_labeled_words = list(dict.fromkeys(IO_sequence_tracing(indx_list=label_indices, Words_data=dataframe['Word'])))
        unique_labeled_words = unique_labeled_words.replace("[SEP]", "").replace("[CLS]", "")
        for word in unique_labeled_words:
            words = word.split()
            if len(words) == 1:
                dataframe['Tag'].iloc[list(np.where((dataframe['Word'] == word) & (dataframe['Tag'] == 'O'))[0])] = label
            else:
                first_word_index = list(np.where((dataframe['Word'] == words[0]) & (dataframe['Tag'] == 'O'))[0])
                for indx in first_word_index:
                    if list(dataframe['Word'].iloc[indx:(indx+len(words))]) == words:
                        dataframe['Tag'].iloc[indx:(indx+len(words))] = label
    return dataframe

def extendSpecificTagsToAllEqualWordSeq(dataframe, Tagname):
    label_indices = list(np.where(dataframe['Tag'] == Tagname)[0])
    unique_labeled_words = list(dict.fromkeys(IO_sequence_tracing(indx_list=label_indices, Words_data=dataframe['Word'])))
    for word in unique_labeled_words:
        words = word.split()
        if len(words) == 1:
            dataframe['Tag'].iloc[list(np.where((dataframe['Word'] == word) & (dataframe['Tag'] == 'O'))[0])] = Tagname
        else:
            first_word_index = list(np.where((dataframe['Word'] == words[0]) & (dataframe['Tag'] == 'O'))[0])
            for indx in first_word_index:
                if list(dataframe['Word'].iloc[indx:(indx+len(words))]) == words:
                    dataframe['Tag'].iloc[indx:(indx+len(words))] = Tagname
    return dataframe


instance_ST, instance_BD, instance_BO, instance_AT, instance_SG, instance_MO, sentenceid, fullsentence = [], [], [], [], [], [], [], []
len_instance_before = 0
for file in listOfFiles:
    print("Processing file: ", file)
    labeled_data = pd.read_csv(os.path.join(os.getcwd(), ("predict_labeled/" + file)), encoding="latin1")
    labeled_data['Tag'].iloc[list(np.where((labeled_data['Word'] == "[SEP]") | (
                labeled_data['Word'] == "[CLS]")| (labeled_data['Word'] == "."))[0])] = 'O'
    if TagToWordExtension:
        labeled_data = extendTagsToAllEqualWordSeq(labeled_data)
    labeled_data = extendSpecificTagsToAllEqualWordSeq(labeled_data, "I-behavOption")
    AT_words = list(np.where((labeled_data['Word'] == 'significant') | (labeled_data['Word'] == 'insignificant') | (labeled_data['Word'] == 'consistent') | (labeled_data['Word'] == 'associated'))[0])
    AT_words.extend(idx-1 for idx in AT_words if labeled_data['Word'].iloc[idx-1] in ["non", "not", "Non", "Not", "no", "No"])
    AT_words.extend(idx-2 for idx in AT_words if labeled_data['Word'].iloc[idx-2] in ["non", "not", "Non", "Not", "no", "No"])
    labeled_data['Tag'].iloc[AT_words] = 'I-assocType'
    sentences = list(dict.fromkeys(labeled_data['Sentence']))
    for sentence in sentences:
        sentence_idx_range = np.where(labeled_data['Sentence'] == sentence)[0]
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
                AT_indx = list(np.where((labeled_data['Tag'].iloc[sentence_idx_range] == "B-assocType") | (labeled_data['Tag'].iloc[sentence_idx_range]== "I-assocType"))[0])
                BO_indx = list(np.where((labeled_data['Tag'].iloc[sentence_idx_range] == "B-behavOption") | (labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavOption"))[0])
                BD_indx = list(np.where((labeled_data['Tag'].iloc[sentence_idx_range] == "B-behavDeterm") | (labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavDeterm"))[0])
                SG_indx = list(np.where((labeled_data['Tag'].iloc[sentence_idx_range] == "B-studygroup") | (labeled_data['Tag'].iloc[sentence_idx_range] == "I-studygroup"))[0])
                MO_indx = list(np.where((labeled_data['Tag'].iloc[sentence_idx_range] == "B-moderator") | (labeled_data['Tag'].iloc[sentence_idx_range] == "I-moderator"))[0])
                instance_AT.append(" ; ".join(IO_sequence_tracing(indx_list= AT_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BO.append(" ; ".join(IO_sequence_tracing(indx_list=BO_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BD.append(" ; ".join(IO_sequence_tracing(indx_list=BD_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_SG.append(" ; ".join(IO_sequence_tracing(indx_list=SG_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_MO.append(" ; ".join(IO_sequence_tracing(indx_list=MO_indx, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
            sentenceid.append(sentence)
            sentence_txt = " ".join(str(e) for e in labeled_data['Word'].iloc[sentence_idx_range])
            fullsentence.append(sentence_txt.replace("[CLS]", "").replace("[SEP]", ""))

    instance_ST.extend([file] * (len(instance_AT)-len_instance_before))
    len_instance_before = len(instance_AT)



if TagToWordExtension:
    file_name_suffix = "_enhanced"
else:
    file_name_suffix = ""

Evidence_instances_df = pd.DataFrame({'DOI': instance_ST, 'Sentence': sentenceid, 'BehaviorOption': instance_BO, 'BehaviorDeterminant': instance_BD, 'AssociationType': instance_AT, 'Studygroup': instance_SG, 'Moderator': instance_MO ,  'Fullsentence': fullsentence })
print(Evidence_instances_df.head())
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("Evidence_instances_df"+ file_name_suffix + ".csv"))
Evidence_instances_df.to_csv(csv, index=False)

complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'] != "") & (Evidence_instances_df['AssociationType'] != ""))[0])]
print(complete_evidence_Instances.head())
csv = os.path.join(os.getcwd(), ("Complete_evidence_Instances"+ file_name_suffix + ".csv"))
complete_evidence_Instances.to_csv(csv, index=False)

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

# complete_evidence_Instances
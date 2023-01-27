import os
from typing import List, Any
import re
import pandas as pd
import numpy as np
from itertools import chain

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# csv = os.path.join(os.getcwd(), ("Evidence_instances_df_ManualLabel.csv"))
csv = os.path.join(os.getcwd(), ("Evidence_instances_df.csv"))

Evidence_instances_df = pd.read_csv(csv, encoding="latin1")

def classif_assoc_syntact_encoding(sent_wordlist, sent_POSlist, AT_word_idx):
    AT_POS = [sent_POSlist[i] for i in AT_word_idx]
    syntact_class, nr_class, class_AT_idx = [],[], []
    if ("VBN" in AT_POS):
        AT_VBN = [AT_word_idx[x] for x in [i for i, x in enumerate(AT_POS) if x == "VBN"]]
        subAT, subAT2, indx = [], [], 0
        for vbn in AT_VBN:
            if (any([True for i in ["VB", "VBZ", "VBP", "VBD"] if i in POS_sentence[indx:vbn]])) :
                subAT.append(vbn)
                indx = vbn
            else:
                subAT2.append(vbn)
                indx = vbn
        if bool(subAT):
            syntact_class.append("past_participle")
            nr_class.append(len(subAT))
            class_AT_idx.append(subAT)
        if bool(subAT2):
            syntact_class.append("other_verb")
            nr_class.append(len(subAT))
            class_AT_idx.append(subAT)
    if ("NNS" in AT_POS) or ("NN" in AT_POS):
        AT_NN = [AT_word_idx[x] for x in [i for i, x in enumerate(AT_POS) if x in ["NN", "NNS"]]]
        if ("(" in sent_wordlist) and (")" in sent_wordlist):
            opening = sent_wordlist.index("(")
            closing = sent_wordlist.index(")")
            within_brackets = [i for i in AT_NN if opening < i < closing]
            if bool(within_brackets):
                syntact_class.append("noun_in_brackets")
                nr_class.append(len(within_brackets))
                class_AT_idx.append(within_brackets)
            if len(within_brackets)!= len(AT_NN):
                syntact_class.append("noun")
                [AT_NN.remove(i) for i in within_brackets]
                nr_class.append(len(AT_NN))
                class_AT_idx.append(AT_NN)
        else:
            syntact_class.append("noun")
            nr_class.append(len(AT_NN))
            class_AT_idx.append(AT_NN)
    return syntact_class, nr_class, class_AT_idx


def test_BO_joined_evidence_instance(BO_words, full_sentence, BO_indices):
    if len(BO_indices)>1:
        between_words = full_sentence[min(BO_indices):max(BO_indices)]
        for entity in BO_words:
            between_words = between_words.replace(entity, "")
        between_words = between_words.split()
        if all([True if word in ["and", ",", "the", "as", "well"] else False for word in between_words]):
            return True
        else:
            return False
    else:
        return True


## disaggregating evidence of within sentence colocation
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'].notnull()) & (Evidence_instances_df['AssociationType'].notnull()))[0])]
complete_evidence_Instances = complete_evidence_Instances.fillna(" ")
complete_evidence_Instances['AssociationType'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['AssociationType']]
complete_evidence_Instances['BehaviorDeterminant'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['BehaviorDeterminant']]

BD_disagg, AT_disagg, SENT_disagg, DOI_disagg, sent_ID_disagg, BO_disagg, SG_disagg, MO_disagg  = [], [], [], [], [], [], [], []
for count, value in enumerate(complete_evidence_Instances['Fullsentence']):
    print(value)
    AT_entities = complete_evidence_Instances['AssociationType'].iloc[count].split(" ; ")
    BD_entities = complete_evidence_Instances['BehaviorDeterminant'].iloc[count].split(" ; ")
    BO_entities = complete_evidence_Instances['BehaviorOption'].iloc[count].split(" ; ")
    POS_sentence = complete_evidence_Instances['sentence_POS'].iloc[count].split(" ; ")
    AT_words = list(chain.from_iterable([x.split() for x in AT_entities]))
    words = value.split()
    AT_word_idx = [words.index(i) for i in AT_words]
    split_prepos = [m.start() for x in ["whereas", "while", "unlike", "although", "though"] for m in re.finditer((x), value)]
    AT_indices, BD_indices, BO_indices = [], [], []
    indx = -1
    for entity in AT_entities:
        candidates = [(m.start()+1) for m in re.finditer((" " + entity + " "), value) if (m.start()+1) > indx][0]
        AT_indices.extend([candidates])
        indx = max(AT_indices)
    indx = -1
    for entity in BD_entities:
        candidates = [(m.start()+1) for m in re.finditer((" " + entity + " "), value) if (m.start()+1) > indx][0]
        BD_indices.extend([candidates])
        indx = max(BD_indices)
    indx = -1
    if len(BO_entities) >1:
        for entity in BO_entities:
            candidates = [(m.start()+1) for m in re.finditer((" " + entity + " "), value) if (m.start()+1) > indx][0]
            BO_indices.extend([candidates])
            indx = max(BO_indices)
    # print(AT_entities, AT_indices, BD_entities, BD_indices, BO_entities, BO_indices)
    BO_entities = list(dict.fromkeys(BO_entities))
    BO_joined = False
    if test_BO_joined_evidence_instance(BO_words = BO_entities, full_sentence= value, BO_indices= BO_indices):
        BO_joined = True
    syntact_class, nr_class, class_AT_idx = classif_assoc_syntact_encoding(sent_wordlist= words, sent_POSlist= POS_sentence, AT_word_idx= AT_word_idx)
    print(syntact_class, nr_class, AT_entities)
    Nr_added_Instances= 0
    BO_added = 0

    if len(AT_entities) == 1:
        if (len(BO_entities) > 1) and (BO_joined == False):
            if ("VBN" in complete_evidence_Instances['AT_POS'].iloc[count]) and (POS_sentence[AT_word_idx[0]-1] in ["VB", "VBZ", "VBP"]):
                if AT_indices[0] < min(BD_indices):
                    subBOs_idx = [i for i in BO_indices if i < AT_indices[0]]
                    if len(subBOs_idx) <2:
                        subBOs = [BO_entities[0]]
                    else:
                        if test_BO_joined_evidence_instance(BO_words= BO_entities[0:(len(subBOs_idx))], full_sentence = value, BO_indices= BO_indices[0:len(subBOs_idx)]):
                            subBOs = BO_entities[0:len(subBOs_idx)]
                    print("SMALLER", subBOs_idx, subBOs)
                elif AT_indices[0] > max(BD_indices):
                    subBOs_idx = [i for i in BO_indices if i > AT_indices[0]]
                    if len(subBOs_idx) < 2:
                        subBOs = [BO_entities[-1]]
                    else:
                        if test_BO_joined_evidence_instance(BO_words= BO_entities[-(len(subBOs_idx)):], full_sentence = value, BO_indices= BO_indices[-(len(subBOs_idx)):]):
                            subBOs = BO_entities[-(len(subBOs_idx)):]
                    print("BIGGER", subBOs_idx, subBOs)
        else:
            subBOs = BO_entities
        AT_disagg.extend((AT_entities)* len(BD_entities)*len(subBOs))
        BD_disagg.extend((BD_entities)*len(subBOs))
        for BO in subBOs:
            BO_disagg.extend([BO]*len(BD_entities))
        Nr_added_Instances = (len(BD_entities)*len(subBOs))
        BO_added = 1
    elif len(BD_entities) == 1:
        if BO_joined == True:
            subBOs = BO_entities
            BD_disagg.extend([BD_entities] * len(subBOs))
            AT_disagg.extend([", ".join(AT_entities)] * len(subBOs))
            Nr_added_Instances = (len(BD_entities) * len(subBOs))
            for BO in subBOs:
                BO_disagg.extend([BO] * len(BD_entities))
            BO_added = 1
        else:
            BD_disagg.extend(BD_entities)
            AT_disagg.extend([", ".join(AT_entities)])
            Nr_added_Instances = len(BD_entities)
    elif (max(AT_indices) < min(BD_indices)) | (min(AT_indices) > max(BD_indices)):
        BD_disagg.extend(BD_entities)
        AT_disagg.extend([", ".join(AT_entities)] * len(BD_entities))
        Nr_added_Instances = len(BD_entities)
    else:
        if (bool(split_prepos)) and (min(BD_indices)< min(split_prepos)> min(AT_indices)):
            indx =-1
            for prepos in split_prepos:
                subBDs_idx = [i for i, v in enumerate(BD_indices) if prepos > v > indx]
                subATs_idx = [i for i, v in enumerate(AT_indices)  if prepos > v > indx]
                # print("SUBAT", subATs_idx)
                BD_disagg.extend((BD_entities[i] for i in subBDs_idx))
                subATs = " ".join([AT_entities[i] for i in subATs_idx])
                AT_disagg.extend([subATs] * len(subBDs_idx))
                indx = prepos
            subBDs_idx = [i for i, v in enumerate(BD_indices) if indx < v]
            subATs_idx = [i for i, v in enumerate(AT_indices) if indx < v]
            BD_disagg.extend((BD_entities[i] for i in subBDs_idx))
            subATs = ", ".join([AT_entities[i] for i in subATs_idx])
            AT_disagg.extend([subATs] * len(subBDs_idx))
            Nr_added_Instances = len(BD_entities)
        elif AT_indices[0] < BD_indices[0] and max(AT_indices) < max(BD_indices):
            AT_indices.append(10000)
            Covered_ATs, Covered_BDs = -1, -1
            while Covered_ATs < (len(AT_indices)-2):
                subATs_idx = [i for i, v in enumerate(AT_indices) if i > Covered_ATs if v < BD_indices[Covered_BDs + 1]]
                subBDs_idx = [i for i, v in enumerate(BD_indices) if i > Covered_BDs if v < AT_indices[max(subATs_idx)+1]]
                BD_disagg.extend((BD_entities[i] for i in subBDs_idx))
                subATs = " ".join([AT_entities[i] for i in subATs_idx])
                AT_disagg.extend([subATs]*len(subBDs_idx))
                Covered_ATs, Covered_BDs = max(subATs_idx), max(subBDs_idx)
            Nr_added_Instances = len(BD_entities)
        elif AT_indices[0] > BD_indices[0] and max(AT_indices) > max(BD_indices):
            BD_indices.append(10000)
            Covered_ATs, Covered_BDs = -1, -1
            while Covered_ATs < (len(AT_indices)-1):
                subBDs_idx = [i for i, v in enumerate(BD_indices) if i > Covered_BDs if v < AT_indices[Covered_ATs+1]]
                subATs_idx = [i for i, v in enumerate(AT_indices) if i > Covered_ATs if v < BD_indices[max(subBDs_idx)+1]]
                BD_disagg.extend((BD_entities[i] for i in subBDs_idx))
                subATs = ", ".join([AT_entities[i] for i in subATs_idx])
                AT_disagg.extend([subATs]*len(subBDs_idx))
                Covered_ATs, Covered_BDs = max(subATs_idx), max(subBDs_idx)
            Nr_added_Instances = len(BD_entities)
        else:
            AT_disagg.extend([complete_evidence_Instances['AssociationType'].iloc[count]])
            BD_disagg.extend([complete_evidence_Instances['BehaviorDeterminant'].iloc[count]])
            Nr_added_Instances = 1
    SENT_disagg.extend([value]*Nr_added_Instances)
    DOI_disagg.extend([complete_evidence_Instances['DOI'].iloc[count]]*Nr_added_Instances)
    sent_ID_disagg.extend([complete_evidence_Instances['Sentence'].iloc[count]]*Nr_added_Instances)
    if BO_added == 0:
        BO_disagg.extend([" ; ".join(BO_entities)]*Nr_added_Instances)
    SG_disagg.extend([complete_evidence_Instances['Studygroup'].iloc[count]]*Nr_added_Instances)
    MO_disagg.extend([complete_evidence_Instances['Moderator'].iloc[count]]*Nr_added_Instances)
    # print(BD_entities,len(BD_disagg), len(AT_disagg), len(SENT_disagg))


## disaggregating evidence of association type in sentence before
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'].isnull()) | (Evidence_instances_df['AssociationType'].isnull()))[0])]
complete_evidence_Instances = complete_evidence_Instances.iloc[list(np.where((complete_evidence_Instances['BehaviorDeterminant'].notnull()) | (complete_evidence_Instances['AssociationType'].notnull()))[0])]


sentences = [int(ids.replace("Sentence: ", "")) for ids in complete_evidence_Instances['Sentence']]
x = len(sentences)-1
conseq = [[i,i+1] for i,v in enumerate(sentences) if i != x if v+1 == sentences[i+1]]

# keywords = ["These", "these", "this", "This"]
keywords = ["These"]
for count, value in enumerate(conseq):
    if pd.notnull(complete_evidence_Instances['AssociationType'].iloc[value[0]]):
        if pd.notnull(complete_evidence_Instances['BehaviorDeterminant'].iloc[value[1]]) :
            if any(keyword in complete_evidence_Instances['Fullsentence'].iloc[value[1]] for keyword in keywords):
                # print(complete_evidence_Instances['AssociationType'].iloc[value[0]], complete_evidence_Instances['Fullsentence'].iloc[value[0]])
                # print(complete_evidence_Instances['BehaviorDeterminant'].iloc[value[1]], complete_evidence_Instances['Fullsentence'].iloc[value[1]])
                # print()
                BD_entities = complete_evidence_Instances['BehaviorDeterminant'].iloc[value[1]].split(" ; ")
                AT_entities = complete_evidence_Instances['AssociationType'].iloc[value[0]].split(" ; ")
                BD_disagg.extend(BD_entities)
                AT_disagg.extend([" ".join(AT_entities)] * len(BD_entities))
                Nr_added_Instances = len(BD_entities)
                SENT_disagg.extend([" ".join(complete_evidence_Instances['Fullsentence'].iloc[value])]*Nr_added_Instances)
                DOI_disagg.extend([complete_evidence_Instances['DOI'].iloc[value[0]]]*Nr_added_Instances)
                sent_ID_disagg.extend([" ; ".join(complete_evidence_Instances['Sentence'].iloc[value])]*Nr_added_Instances)
                if pd.notnull(complete_evidence_Instances['BehaviorOption'].iloc[value[0]]):
                    BO_disagg.extend([complete_evidence_Instances['BehaviorOption'].iloc[value[0]]]*Nr_added_Instances)
                elif pd.notnull(complete_evidence_Instances['BehaviorOption'].iloc[value[1]]):
                    BO_disagg.extend([complete_evidence_Instances['BehaviorOption'].iloc[value[1]]]*Nr_added_Instances)
                else:
                    BO_disagg.extend([" "]*Nr_added_Instances)
                SG_disagg.extend([complete_evidence_Instances['Studygroup'].iloc[value[0]]]*Nr_added_Instances)
                MO_disagg.extend([complete_evidence_Instances['Moderator'].iloc[value[0]]]*Nr_added_Instances)
#
print(len(SENT_disagg), len(BD_disagg), len(AT_disagg), len(BO_disagg))
disaggregated_evidence_instances = pd.DataFrame({'DOI': DOI_disagg, 'Sentence': sent_ID_disagg, 'BehaviorOption': BO_disagg, 'BehaviorDeterminant': BD_disagg, 'AssociationType': AT_disagg, 'Studygroup': SG_disagg, 'Moderator': MO_disagg ,  'Fullsentence': SENT_disagg })
disaggregated_evidence_instances.to_csv("disaggregated_evidence_instances.csv", index=False)
# #
print("Nr of unique articles contributing evidence: ",len(set(disaggregated_evidence_instances['DOI'])))
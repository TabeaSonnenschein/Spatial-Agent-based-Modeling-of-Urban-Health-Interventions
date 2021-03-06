import os
from typing import List, Any
import re
import pandas as pd
import numpy as np
from itertools import chain
import spacy
import deplacy
from spacy.lang.en.examples import sentences
en = spacy.load('en_core_web_sm')
from spacy import displacy

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
Evidence_instances_df = pd.read_csv(os.path.join(os.getcwd(), ("Evidence_instances_df.csv")))

# checks if multiple behavior options are mentioned in one evidence instance
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


# the entity list has to be ordered sequentially;
# finds the indices of the words in the sentence
def find_indices_words_in_sentence(entity_list, fullsentence):
    indx = -1
    entity_indices = []
    for entity in entity_list:
        candidates = [(m.start()+1) for m in re.finditer((" " + entity + " "), (" " + fullsentence + " ")) if (m.start()+1) > indx][0]
        entity_indices.extend([candidates])
        indx = max(entity_indices)
    return entity_indices

def repeat_each_item_n_times_in_list (list, times):
    rep_list = []
    for el in list:
        rep_list.extend([el] * times)
    return rep_list

def check_if_in_wordlist_and_append(list_of_lists, wordlist):
    output_list = []
    for list in list_of_lists:
        output_list.extend([el for el in list if el in wordlist])
    return output_list


# creates sublist of list that is in same subtree list as evidence elements
def entities_in_same_subtree_list_as_evidence_instance(entity_list, subtree_list, list_evidence_el):
    sublist = []
    for list in subtree_list:
        if all([True if x in list else False for x in list_evidence_el]):
            sublist.extend([el for el in entity_list if el in list])
    return sublist

def divide_words_by_split_proposition(split_prepos, word_indices):
    nested_list = []
    indx = -1
    for prepos in split_prepos:
        nested_list.append([i for i, v in enumerate(word_indices) if prepos > v > indx])
        indx = prepos
    nested_list.append([i for i, v in enumerate(word_indices) if indx < v])
    return nested_list

def evidence_instance_appending(ATs, BDs, BOs, SGs, MOs):
    AT_extension, BD_extension, BO_extension, SG_extension, MO_extension = [],[],[],[],[]
    AT_extension.extend([ATs] * len(BDs) * len(BOs) * len(SGs) * len(MOs))
    BD_extension.extend((BDs) * len(BOs) * len(SGs) * len(MOs))
    BO_extension.extend((repeat_each_item_n_times_in_list(BOs, len(BDs))) * len(SGs) * len(MOs))
    SG_extension.extend((repeat_each_item_n_times_in_list(SGs, (len(BDs)*len(BOs)))) * len(MOs))
    MO_extension.extend((repeat_each_item_n_times_in_list(MOs, (len(BDs)*len(BOs)*len(SGs)))))
    return AT_extension, BD_extension, BO_extension, SG_extension, MO_extension

## disaggregating evidence of within sentence colocation
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'].notnull()) & (Evidence_instances_df['AssociationType'].notnull()))[0])]
complete_evidence_Instances = complete_evidence_Instances.fillna(" ")
complete_evidence_Instances['AssociationType'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['AssociationType']]
complete_evidence_Instances['BehaviorDeterminant'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['BehaviorDeterminant']]

## subselecting complete sentences
gramm_complete_sentences = [x for i in ['VB','VBG','VBD', 'VBN', 'VBP', 'VBZ'] for x,y in enumerate(complete_evidence_Instances['sentence_POS']) if i in y]
complete_evidence_Instances = complete_evidence_Instances.iloc[gramm_complete_sentences]
complete_evidence_Instances['Fullsentence'] = [x.replace("?",",") for x in complete_evidence_Instances['Fullsentence']]

## Target List Creation
BD_disagg, AT_disagg, SENT_disagg, DOI_disagg, sent_ID_disagg, BO_disagg, SG_disagg, MO_disagg  = [], [], [], [], [], [], [], []

## Filling Target Lists with identified Evidence Instances
for count, value in enumerate(complete_evidence_Instances['Fullsentence']):
    value = value.strip()
    value = re.sub(r'(\d+)( \. )(\d+)', r'\1.\3', value)
    Nr_added_Instances = 0

    ## creating entity and indice lists
    AT_entities = complete_evidence_Instances['AssociationType'].iloc[count].split(" ; ")
    BD_entities = complete_evidence_Instances['BehaviorDeterminant'].iloc[count].split(" ; ")
    BO_entities = complete_evidence_Instances['BehaviorOption'].iloc[count].split(" ; ")
    SG_entities = complete_evidence_Instances['Studygroup'].iloc[count].split(" ; ")
    MO_entities = complete_evidence_Instances['Moderator'].iloc[count].split(" ; ")
    POS_sentence = complete_evidence_Instances['sentence_POS'].iloc[count].split(" ; ")
    AT_indices = find_indices_words_in_sentence(AT_entities, value)
    BD_indices = find_indices_words_in_sentence(BD_entities, value)
    if BO_entities != [" "]:
        BO_indices = find_indices_words_in_sentence(BO_entities, value)
    else:
        BO_indices = []
    if SG_entities != [" "]:
        SG_indices = find_indices_words_in_sentence(SG_entities, value)
    else:
        SG_indices = []
    if MO_entities != [" "]:
        MO_indices = find_indices_words_in_sentence(MO_entities, value)
    else:
        MO_indices = []


    ## String based identification
    split_prepos = [m.start() for x in ["whereas", "while", "unlike", "although", "though"] for m in re.finditer((x), value)]
    BO_joined = test_BO_joined_evidence_instance(BO_words=BO_entities, full_sentence=value, BO_indices=BO_indices)
    print(BO_joined)

    ## printing data
    print("-" * 70)
    print("assoc:", AT_entities)
    print("behavDet:", BD_entities)
    print("behavOpt:", BO_entities)
    print("studyGroup:", SG_entities)
    print("moderators:", MO_entities)
    print(value)

    #######################
    ## Dependency Parser ##
    #######################
    doc = en(value)
    root = [word for word in doc if (word.dep_ in ['ROOT', 'advcl']) or ((word.head.dep_ == 'ROOT') and (word.dep_ == 'conj'))]
    rootpos = [token.pos_ for token in root]
    print("ROOT", root, rootpos)

    ## for each root identify important subtree components and compile a wordlist of these
    ## then check which BOs, BDs, ATs, SGs and MOs are part of the sublist
    items_in_subtree_groups = []
    for token in root:
        clausal_complement = [word for word in token.children if word.dep_ in ['ccomp', 'xcomp']]
        clausal_complement_children = [child for cl in clausal_complement for child in cl.subtree]
        subject = [child for child in token.children if child.dep_ in ['nsubjpass', 'nsubj']]
        subject_children = [child for sub in subject for child in sub.subtree]
        preposition = [child for child in token.children if child.dep_ == 'prep']
        preposition_children = [child for prep in preposition for child in prep.subtree]
        object = [child for child in token.children if child.dep_ == 'dobj']
        object_children = [child for obj in object for child in obj.subtree]
        wordlist = list(chain.from_iterable([[str(token)], clausal_complement, clausal_complement_children,
                                             subject, subject_children, preposition, preposition_children, object,
                                             object_children]))
        wordlist = (" ").join([str(word) for word in wordlist])
        items_in_subtree_groups.append(check_if_in_wordlist_and_append([AT_entities,BD_entities,BO_entities,SG_entities, MO_entities], wordlist))
    print(items_in_subtree_groups)

    ##################################
    ## inferring evidence relations ##
    ##################################

    # if there is only one association type or only one behavior determinant
    if (len(AT_entities) == 1) | (len(BD_entities) == 1):
        if BO_joined == True:
            subBOs = BO_entities
        else:
            subBOs = entities_in_same_subtree_list_as_evidence_instance(BO_entities, items_in_subtree_groups, list(chain.from_iterable([AT_entities,BD_entities])))
        AT_disagg.extend([", ".join(AT_entities)] * len(BD_entities)*len(subBOs))
        BD_disagg.extend((BD_entities)*len(subBOs))
        BO_disagg.extend(repeat_each_item_n_times_in_list(subBOs, len(BD_entities)))
        Nr_added_Instances = (len(BD_entities)*len(subBOs))
        print("evidence instance:", subBOs, AT_entities, BD_entities)

    # if all association types are before all behavior determinant or vice versa
    elif (max(AT_indices) < min(BD_indices)) | (min(AT_indices) > max(BD_indices)):
        print("all association types are before all behavior determinant or vice versa")


    else:
        # if there is a split proposition that is breaking up evidence instances
        if (bool(split_prepos)) and (min(BD_indices) < min(split_prepos) > min(AT_indices)):
            print("there is a split proposition that is breaking up evidence instances")
            subBDs_idx = divide_words_by_split_proposition(split_prepos=split_prepos, word_indices=BD_indices)
            subATs_idx = divide_words_by_split_proposition(split_prepos=split_prepos, word_indices=AT_indices)
            subBOs_idx = divide_words_by_split_proposition(split_prepos=split_prepos, word_indices=BO_indices)
            subSGs_idx = divide_words_by_split_proposition(split_prepos=split_prepos, word_indices=SG_indices)
            subMOs_idx = divide_words_by_split_proposition(split_prepos=split_prepos, word_indices=MO_indices)
            for x in range(0, len(subBOs_idx)):
                subBDs = [BD_entities[i] for i in subBDs_idx[x]]
                subATs = " ".join([AT_entities[i] for i in subATs_idx[x]])
                subBOs = [BO_entities[i] for i in subBOs_idx[x]]
                subSGs = [SG_entities[i] for i in subSGs_idx[x]]
                subMOs = [MO_entities[i] for i in subMOs_idx[x]]
                subBDs = (" " if len(subBDs) == 0 else subBDs)
                subATs = (" " if len(subATs) == 0 else subATs)
                subBOs = (" " if len(subBOs) == 0 else subBOs)
                subSGs = (" " if len(subSGs) == 0 else subSGs)
                subMOs = (" " if len(subMOs) == 0 else subMOs)
                AT_extension, BD_extension, BO_extension, SG_extension, MO_extension = evidence_instance_appending(subATs, subBDs, subBOs, subSGs, subMOs)
                print(AT_extension, BD_extension, BO_extension, SG_extension, MO_extension)
                AT_disagg.extend(AT_extension)
                BD_disagg.extend(BD_extension)
                BO_disagg.extend(BO_extension)
                SG_disagg.extend(SG_extension)
                MO_disagg.extend(MO_extension)
                print("evidence instance:",  subATs, subBDs, subBOs, subSGs, subMOs)
                Nr_added_Instances += (len(subBDs)*len(subBOs)*len(subSGs)*len(subMOs))
                print(Nr_added_Instances, len(AT_disagg), len(BD_disagg))


        elif AT_indices[0] < BD_indices[0] and max(AT_indices) < max(BD_indices):
            print("AT_indices[0] < BD_indices[0] and max(AT_indices) < max(BD_indices)")

        elif AT_indices[0] > BD_indices[0] and max(AT_indices) > max(BD_indices):
            print("AT_indices[0] > BD_indices[0] and max(AT_indices) > max(BD_indices)")

        else:
            AT_disagg.extend([complete_evidence_Instances['AssociationType'].iloc[count]])
            BD_disagg.extend([complete_evidence_Instances['BehaviorDeterminant'].iloc[count]])
            Nr_added_Instances = 1

    ##############################################################
    ## Adding the doc and sentence details to evidence instance ##
    ##############################################################
    SENT_disagg.extend([value] * Nr_added_Instances)
    DOI_disagg.extend([complete_evidence_Instances['DOI'].iloc[count]] * Nr_added_Instances)
    sent_ID_disagg.extend([complete_evidence_Instances['Sentence'].iloc[count]] * Nr_added_Instances)
    SG_disagg.extend([complete_evidence_Instances['Studygroup'].iloc[count]] * Nr_added_Instances)
    MO_disagg.extend([complete_evidence_Instances['Moderator'].iloc[count]] * Nr_added_Instances)
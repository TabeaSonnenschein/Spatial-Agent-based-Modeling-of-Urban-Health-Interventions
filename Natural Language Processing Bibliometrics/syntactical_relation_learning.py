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
from utils_Syntact_Learn import *


#########################################
### READING AND PREPARING DATA ##########
#########################################

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# csv = os.path.join(os.getcwd(), ("Evidence_instances_df_ManualLabel.csv"))
csv = os.path.join(os.getcwd(), ("Evidence_instances_df.csv"))
Evidence_instances_df = pd.read_csv(csv)
# columnnames: 'DOI','Sentence','BehaviorOption','BehaviorDeterminant','AssociationType',
#              'Studygroup','Moderator',Fullsentence','BO_POS','BD_POS',AT_POS','sentence_POS'

## disaggregating evidence of within sentence colocation
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'].notnull()) & (Evidence_instances_df['AssociationType'].notnull()))[0])]
complete_evidence_Instances = complete_evidence_Instances.fillna(" ")
complete_evidence_Instances['AssociationType'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['AssociationType']]
complete_evidence_Instances['BehaviorDeterminant'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['BehaviorDeterminant']]

## subselecting complete sentences
gramm_complete_sentences = [x for i in ['VB','VBG','VBD', 'VBN', 'VBP', 'VBZ'] for x,y in enumerate(complete_evidence_Instances['sentence_POS']) if i in y]
complete_evidence_Instances = complete_evidence_Instances.iloc[gramm_complete_sentences]
complete_evidence_Instances['Fullsentence'] = [x.replace("?",",") for x in complete_evidence_Instances['Fullsentence']]

#########################################################################################
### create df with all possible within sentence evidence relation combinations ##########
#########################################################################################
# the entity list has to be ordered sequentially;
# finds the indices of the words in the sentence

## Target List Creation
BD_disagg, AT_disagg, SENT_disagg, DOI_disagg, sent_ID_disagg, BO_disagg, SG_disagg, MO_disagg  = [], [], [], [], [], [], [], []

## Syntactical Properties
# Indices
BD_indice_disagg, AT_indice_disagg, BO_indice_disagg, MO_indice_disagg, SG_indice_disagg, split_prepos_indice_disagg = [], [], [], [], [], []

# combinatory variable properties
same_dependTree = []

## filling target lists and syntactical properties
for count, value in enumerate(complete_evidence_Instances['Fullsentence']):
    ## creating entity and indice lists
    AT_entities = complete_evidence_Instances['AssociationType'].iloc[count].split(" ; ")
    BD_entities = complete_evidence_Instances['BehaviorDeterminant'].iloc[count].split(" ; ")
    BO_entities = replace_spacestr_NA(complete_evidence_Instances['BehaviorOption'].iloc[count].split(" ; "))
    SG_entities = replace_spacestr_NA(complete_evidence_Instances['Studygroup'].iloc[count].split(" ; "))
    MO_entities = replace_spacestr_NA(complete_evidence_Instances['Moderator'].iloc[count].split(" ; "))
    AT_indices = find_indices_words_in_sentence(AT_entities, value)
    BD_indices = find_indices_words_in_sentence(BD_entities, value)
    BO_indices = find_indices_words_in_sentence(BO_entities, value)
    SG_indices = find_indices_words_in_sentence(SG_entities, value)
    MO_indices = find_indices_words_in_sentence(MO_entities, value)

    NR_poss_relat = 1*len(BD_entities)*(len(BO_entities)+1)*(len(SG_entities)+1)*(len(MO_entities)+1)
    #print(NR_poss_relat)

    ## String based identification
    split_prepos = [m.start() for x in ["whereas", "while", "unlike", "although"] for m in re.finditer((x), value)]
    split_prepos.extend(["NaN"])
    BO_joined = test_BO_joined_evidence_instance(BO_words=BO_entities, full_sentence=value, BO_indices=BO_indices)

    #######################
    ## Dependency Parser ##
    #######################
    doc = en(value)
    root = [word for word in doc if (word.dep_ in ['ROOT', 'advcl']) or ((word.head.dep_ == 'ROOT') and (word.dep_ == 'conj'))]
    rootpos = [token.pos_ for token in root]
    #print("ROOT", root, rootpos)

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
    #print(items_in_subtree_groups)


    ### filling target list
    # variable names
    BO_entities.extend("NaN")
    MO_entities.extend("NaN")
    SG_entities.extend("NaN")
    AT_extension_name, BD_extension_name, BO_extension_name, SG_extension_name, MO_extension_name = evidence_instance_appending(AT_entities, BD_entities, BO_entities, SG_entities, MO_entities)
    AT_disagg.extend(AT_extension_name)
    BD_disagg.extend(BD_extension_name)
    BO_disagg.extend(BO_extension_name)
    SG_disagg.extend(SG_extension_name)
    MO_disagg.extend(MO_extension_name)

    # indices
    BO_indices.extend(" ")
    MO_indices.extend(" ")
    SG_indices.extend(" ")
    AT_extension_indx, BD_extension_indx, BO_extension_indx, SG_extension_indx, MO_extension_indx = evidence_instance_appending(AT_indices, BD_indices, BO_indices, SG_indices, MO_indices)
    BD_indice_disagg.extend(BD_extension_indx)
    AT_indice_disagg.extend(AT_extension_indx)
    BO_indice_disagg.extend(BO_extension_indx)
    MO_indice_disagg.extend(SG_extension_indx)
    SG_indice_disagg.extend(MO_extension_indx)

    # combinatory syntactical properties



    for i in range(0, len(AT_extension_name)):
        same_tree = check_if_varcombi_same_dependency_subtree(AT_extension_name[i], BD_extension_name[i],
                                                  BO_extension_name[i], SG_extension_name[i],
                                                  MO_extension_name[i], items_in_subtree_groups)
        same_dependTree.extend(same_tree)
        print(same_tree)

    # sentence level variables
    split_prepos_indice_disagg.extend([split_prepos[0]] * NR_poss_relat)
    SENT_disagg.extend([value] * NR_poss_relat)
    DOI_disagg.extend([complete_evidence_Instances['DOI'].iloc[count]] * NR_poss_relat)
    sent_ID_disagg.extend([complete_evidence_Instances['Sentence'].iloc[count]] * NR_poss_relat)

    # check if all lists same length
    print(len(BD_disagg), len(AT_disagg), len(SENT_disagg), len(DOI_disagg), len(sent_ID_disagg),
          len(BO_disagg), len(SG_disagg), len(MO_disagg))
    print(len(BD_indice_disagg), len(AT_indice_disagg), len(BO_indice_disagg), len(MO_indice_disagg),
          len(SG_indice_disagg), len(split_prepos_indice_disagg))
    print(len(same_dependTree))




possible_evidence_instances = pd.DataFrame({'DOI': DOI_disagg, 'Sentence': sent_ID_disagg, 'Fullsentence': SENT_disagg,
                                                 'BehaviorOption': BO_disagg, 'BehaviorDeterminant': BD_disagg,
                                                 'AssociationType': AT_disagg, 'Studygroup': SG_disagg, 'Moderator': MO_disagg ,
                                                 'BD_indice': BD_indice_disagg, 'AT_indice': AT_indice_disagg,
                                                 'BO_indice': BO_indice_disagg, 'SG_indice': SG_indice_disagg,
                                                 'MO_indice': MO_indice_disagg, 'Split_Propos_indice': split_prepos_indice_disagg,
                                                 'same_dependTree': same_dependTree})
possible_evidence_instances.to_csv("possible_evidence_instances.csv", index=False)
# #
print("Nr of unique articles contributing evidence: ",len(set(possible_evidence_instances['DOI'])))
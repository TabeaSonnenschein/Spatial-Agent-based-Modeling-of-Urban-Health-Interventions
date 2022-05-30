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
import networkx as nx


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
Evidence_Truth = []
BD_disagg, AT_disagg, BO_disagg, SG_disagg, MO_disagg  = [], [], [], [], []
SENT_disagg, DOI_disagg, sent_ID_disagg = [], [], []

## Syntactical Properties
# Indices
BD_idx_disagg, AT_idx_disagg, BO_idx_disagg, MO_idx_disagg, SG_idx_disagg, split_prepos_idx_disagg = [], [], [], [], [], []
all_before_or_after_split_propos, index_dist_ATmin_BD, index_dist_ATmax_BD, index_dist_ATmin_BO, index_dist_ATmax_BO = [], [], [], [], []
index_dist_ATmin_MO, index_dist_ATmax_MO, index_dist_ATmin_SG,  index_dist_ATmax_SG = [], [], [], []
semicolon_idx, all_before_or_after_semicolon = [], []

max_sent_ATidx, min_sent_ATidx, max_sent_BDidx, min_sent_BDidx, max_sent_BOidx, min_sent_BOidx = [], [], [], [], [], []
max_sent_MOidx, min_sent_MOidx, max_sent_SGidx, min_sent_SGidx= [], [], [], []

# Nr entities
Nr_AT, Nr_BO, Nr_BD, Nr_MO, Nr_SG = [], [], [], [], []

# POS properties (part of speech)
Nr_verbs, earliestverb_indx, latestverb_indx = [], [], []

# Association Type properties
Verb_in_AT_inst, Noun_in_AT_inst, Adj_Adv_in_AT_inst, Comp_Adj_Adv_in_AT_inst, Verb_outside_AT_inst, Noun_outside_AT_inst, Adj_Adv_outside_AT_inst = [], [], [], [], [], [], []
Nr_ATs_in_instance, Multi_AT_Indice_gap, minimum_AT_idx, maximum_AT_idx = [], [], [], []
some_AT_in_brackets, all_AT_in_brackets= [], []
multiAT_shortestPathLen_min, multiAT_shortestPathLen_max = [], []

# combinatory variable properties
same_dependTree = []
AT_BD_minshortpath, AT_BD_maxshortpath, AT_BD_sumshortpath, AT_BO_minshortpath, AT_BO_maxshortpath, AT_BO_sumshortpath = [], [], [], [], [], []
AT_SG_minshortpath, AT_SG_maxshortpath, AT_SG_sumshortpath, AT_MO_minshortpath, AT_MO_maxshortpath, AT_MO_sumshortpath =  [], [], [], [], [], []
verb_between_ATmin_BD, verb_between_ATmax_BD, verb_between_ATmin_BO, verb_between_ATmax_BO = [], [], [], []
verb_between_ATmin_MO, verb_between_ATmax_MO, verb_between_ATmin_SG, verb_between_ATmax_SG = [], [], [], []

#others
joined_BO_instances = []

## filling target lists and syntactical properties
for count, value in enumerate(complete_evidence_Instances['Fullsentence']):
    ## creating entity and idx lists
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


    ## String based identification
    split_prepos = [m.start() for x in ["whereas", "while", "unlike", "although"] for m in re.finditer((x), value)]
    split_prepos.extend(["NaN"])
    BO_joined = test_BO_joined_evidence_instance(BO_words=BO_entities, full_sentence=value, BO_indices=BO_indices)
    # commas = [m.start() for m in re.finditer(",", value)]
    # brackets = [m.start() for x in ["(", ")"] for m in re.finditer((x), value)]
    semicolon = [m.start() for m in re.finditer(";", value)]
    semicolon.extend(["NaN"])

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
    graph = Dependencytree_to_Graph(doc)


    ### filling target list
    # variable names
    BO_entities.extend(["NaN"])
    MO_entities.extend(["NaN"])
    SG_entities.extend(["NaN"])
    AT_extension_name, BD_extension_name, BO_extension_name, SG_extension_name, MO_extension_name, NR_poss_relat = evidence_instance_appending(AT_entities, BD_entities, BO_entities, SG_entities, MO_entities)
    AT_disagg.extend(AT_extension_name)
    BD_disagg.extend(BD_extension_name)
    BO_disagg.extend(BO_extension_name)
    SG_disagg.extend(SG_extension_name)
    MO_disagg.extend(MO_extension_name)

    # indices
    BO_indices.extend(["NaN"])
    MO_indices.extend(["NaN"])
    SG_indices.extend(["NaN"])
    AT_extension_indx, BD_extension_indx, BO_extension_indx, SG_extension_indx, MO_extension_indx, NR_poss_relat  = evidence_instance_appending(AT_indices, BD_indices, BO_indices, SG_indices, MO_indices)
    BD_idx_disagg.extend(BD_extension_indx)
    AT_idx_disagg.extend(AT_extension_indx)
    BO_idx_disagg.extend(BO_extension_indx)
    MO_idx_disagg.extend(SG_extension_indx)
    SG_idx_disagg.extend(MO_extension_indx)

    AT_repetition = len(BD_entities) * len(BO_entities) * len(SG_entities) * len(MO_entities)
    ATindicelist = combinations_alllists(AT_indices)
    Nr_ATs_in_instance.extend([len(x) for x in ATindicelist] * AT_repetition)
    minimum_AT_idx.extend([min(x) for x in ATindicelist] * AT_repetition)
    maximum_AT_idx.extend([max(x) for x in ATindicelist] * AT_repetition)
    Multi_AT_Indice_gap.extend([max(x)-min(x) for x in ATindicelist] * AT_repetition)

    # combinatory syntactical properties
    # part of same subtree + shortest path between all options
    for i in range(0, len(AT_extension_name)):
        same_tree = check_if_varcombi_same_dependency_subtree(AT_extension_name[i], BD_extension_name[i],
                                                  BO_extension_name[i], SG_extension_name[i],
                                                  MO_extension_name[i], items_in_subtree_groups)
        same_dependTree.extend(same_tree)
        minSP, maxSP, sumSP = getShortestPathbetweenPhrases(AT_extension_name[i], BD_extension_name[i], graph)
        AT_BD_minshortpath.extend(minSP)
        AT_BD_maxshortpath.extend(maxSP)
        AT_BD_sumshortpath.extend(sumSP)
        if BO_extension_name[i]!= "NaN":
            minSP, maxSP, sumSP = getShortestPathbetweenPhrases(AT_extension_name[i], BO_extension_name[i], graph)
            AT_BO_minshortpath.extend(minSP)
            AT_BO_maxshortpath.extend(maxSP)
            AT_BO_sumshortpath.extend(sumSP)
        else:
            AT_BO_minshortpath.extend(["NaN"])
            AT_BO_maxshortpath.extend(["NaN"])
            AT_BO_sumshortpath.extend(["NaN"])
        if SG_extension_name[i]!= "NaN":
            minSP, maxSP, sumSP = getShortestPathbetweenPhrases(AT_extension_name[i], SG_extension_name[i], graph)
            AT_SG_minshortpath.extend(minSP)
            AT_SG_maxshortpath.extend(maxSP)
            AT_SG_sumshortpath.extend(sumSP)
        else:
            AT_SG_minshortpath.extend(["NaN"])
            AT_SG_maxshortpath.extend(["NaN"])
            AT_SG_sumshortpath.extend(["NaN"])
        if MO_extension_name[i]!= "NaN":
            minSP, maxSP, sumSP = getShortestPathbetweenPhrases(AT_extension_name[i], MO_extension_name[i], graph)
            AT_MO_minshortpath.extend(minSP)
            AT_MO_maxshortpath.extend(maxSP)
            AT_MO_sumshortpath.extend(sumSP)
        else:
            AT_MO_minshortpath.extend(["NaN"])
            AT_MO_maxshortpath.extend(["NaN"])
            AT_MO_sumshortpath.extend(["NaN"])

    # POS properties
    sentencePOS = complete_evidence_Instances['sentence_POS'].iloc[count].split(" ; ")
    words_in_sentence = value.split(" ")
    verbs = [words_in_sentence[x+1] for x,v in enumerate(sentencePOS) if v in ["VBN", "VB", "VBZ", "VBP", "VBD"]]
    # verbsPOS = [v for v in sentencePOS if v in ["VBN", "VB", "VBZ", "VBP", "VBD"]]
    verb_indx = find_indices_words_in_sentence(verbs, value)
    Nr_verbs.extend([len(verbs)]*NR_poss_relat)
    if len(verbs) > 0:
        earliestverb_indx.extend([min(verb_indx)]*NR_poss_relat)
        latestverb_indx.extend([max(verb_indx)]*NR_poss_relat)
    else:
        earliestverb_indx.extend(["NaN"]*NR_poss_relat)
        latestverb_indx.extend(["NaN"]*NR_poss_relat)


    #split propos index
    AT_extension_indx_alllists = ATindicelist*AT_repetition
    for i in range(0, len(AT_extension_name)):
        indices = list(chain.from_iterable([AT_extension_indx_alllists[i], [BD_extension_indx[i]],
                                            [BO_extension_indx[i]], [SG_extension_indx[i]], [MO_extension_indx[i]]]))
        if split_prepos[0] != 'NaN':
            if all(True if x == 'NaN' or x > split_prepos[0] else False for x in indices) or all(True if x == 'NaN'  or x < split_prepos[0] else False for x in indices ):
                all_before_or_after_split_propos.extend(["1"])
            else:
                all_before_or_after_split_propos.extend(["0"])
        else:
            all_before_or_after_split_propos.extend(["NaN"])
        if semicolon[0] != 'NaN':
            if all(True if x == 'NaN' or x > semicolon[0] else False for x in indices) or all(True if x == 'NaN' or x < semicolon[0] else False for x in indices ):
                all_before_or_after_semicolon.extend(["1"])
            else:
                all_before_or_after_semicolon.extend(["0"])
        else:
            all_before_or_after_semicolon.extend(["NaN"])

        index_dist_ATmin_BD.extend([min(AT_extension_indx_alllists[i]) - BD_extension_indx[i]])
        index_dist_ATmax_BD.extend([max(AT_extension_indx_alllists[i]) - BD_extension_indx[i]])
        verb_between_ATmin_BD.extend(["1" if any(True for x in verb_indx if min(AT_extension_indx_alllists[i])> x <BD_extension_indx[i]
                                                 or min(AT_extension_indx_alllists[i])< x >BD_extension_indx[i]) else "0"])
        verb_between_ATmax_BD.extend(["1" if any(True for x in verb_indx if min(AT_extension_indx_alllists[i])> x <BD_extension_indx[i]
                                                 or max(AT_extension_indx_alllists[i])< x >BD_extension_indx[i]) else "0"])
        if BO_extension_indx[i] != "NaN":
            index_dist_ATmin_BO.extend([min(AT_extension_indx_alllists[i]) - BO_extension_indx[i]])
            index_dist_ATmax_BO.extend([max(AT_extension_indx_alllists[i]) - BO_extension_indx[i]])
            verb_between_ATmin_BO.extend(["1" if any(True for x in verb_indx if
                                                     min(AT_extension_indx_alllists[i]) > x < BO_extension_indx[
                                                         i] or min(AT_extension_indx_alllists[i]) < x >
                                                     BO_extension_indx[i]) else "0"])
            verb_between_ATmax_BO.extend(["1" if any(True for x in verb_indx if
                                                     min(AT_extension_indx_alllists[i]) > x < BO_extension_indx[
                                                         i] or max(AT_extension_indx_alllists[i]) < x >
                                                     BO_extension_indx[i]) else "0"])
        else:
            index_dist_ATmin_BO.extend(["NaN"])
            index_dist_ATmax_BO.extend(["NaN"])
            verb_between_ATmin_BO.extend(["NaN"])
            verb_between_ATmax_BO.extend(["NaN"])
        if MO_extension_indx[i] != "NaN":
            index_dist_ATmin_MO.extend([min(AT_extension_indx_alllists[i]) - MO_extension_indx[i]])
            index_dist_ATmax_MO.extend([max(AT_extension_indx_alllists[i]) - MO_extension_indx[i]])
            verb_between_ATmin_MO.extend(["1" if any(True for x in verb_indx if
                                                     min(AT_extension_indx_alllists[i]) > x < MO_extension_indx[
                                                         i] or min(AT_extension_indx_alllists[i]) < x >
                                                     MO_extension_indx[i]) else "0"])
            verb_between_ATmax_MO.extend(["1" if any(True for x in verb_indx if
                                                     min(AT_extension_indx_alllists[i]) > x < MO_extension_indx[
                                                         i] or max(AT_extension_indx_alllists[i]) < x >
                                                     MO_extension_indx[i]) else "0"])
        else:
            index_dist_ATmin_MO.extend(["NaN"])
            index_dist_ATmax_MO.extend(["NaN"])
            verb_between_ATmin_MO.extend(["NaN"])
            verb_between_ATmax_MO.extend(["NaN"])
        if SG_extension_indx[i] != "NaN":
            index_dist_ATmin_SG.extend([min(AT_extension_indx_alllists[i]) - SG_extension_indx[i]])
            index_dist_ATmax_SG.extend([max(AT_extension_indx_alllists[i]) - SG_extension_indx[i]])
            verb_between_ATmin_SG.extend(["1" if any(True for x in verb_indx if
                                                     min(AT_extension_indx_alllists[i]) > x < SG_extension_indx[
                                                         i] or min(AT_extension_indx_alllists[i]) < x >
                                                     SG_extension_indx[i]) else "0"])
            verb_between_ATmax_SG.extend(["1" if any(True for x in verb_indx if
                                                     min(AT_extension_indx_alllists[i]) > x < SG_extension_indx[
                                                         i] or max(AT_extension_indx_alllists[i]) < x >
                                                     SG_extension_indx[i]) else "0"])
        else:
            index_dist_ATmin_SG.extend(["NaN"])
            index_dist_ATmax_SG.extend(["NaN"])
            verb_between_ATmin_SG.extend(["NaN"])
            verb_between_ATmax_SG.extend(["NaN"])


    # Association types properties
    # direct link between association types
    ATentitylist = combinations_alllists(AT_entities)
    # Get the length and path
    multiAT_shortestPath_min = []
    multiAT_shortestPath_max = []

    for i in range(0, len(ATentitylist)):
        if len(ATentitylist[i]) == 1:
            multiAT_shortestPath_min.extend([0])
            multiAT_shortestPath_max.extend([0])
        else:
            multiAT_shortestPath = []
            words_inlist = list(chain.from_iterable([phrase.split(" ") for phrase in ATentitylist[i]]))
            for f in range(0, len(words_inlist)):
                for x in range((f + 1), (len(words_inlist))):
                    multiAT_shortestPath.extend([nx.shortest_path_length(graph, source=words_inlist[f].lower(),
                                                                   target=words_inlist[x].lower())])

            multiAT_shortestPath_min.extend([min(multiAT_shortestPath)])
            multiAT_shortestPath_max.extend([max(multiAT_shortestPath)])
    multiAT_shortestPathLen_min.extend(multiAT_shortestPath_min * AT_repetition)
    multiAT_shortestPathLen_max.extend(multiAT_shortestPath_max * AT_repetition)

    # checking ATs part of speech (gramma function)
    fullsentence_ATPOS = complete_evidence_Instances['AT_POS'].iloc[count].split(" ; ")
    wordlengths = [len(word.split(" ")) for word in AT_entities]
    ATPOS_perword = [fullsentence_ATPOS[:wordlengths[0]]]
    for x in range(1,len(wordlengths)):
        idx = (sum(wordlengths[:x]))
        ATPOS_perword.extend([fullsentence_ATPOS[idx:idx+wordlengths[x]]])
    AT_POS_combi = combinations_alllists(ATPOS_perword)
    verb_inside = ["1" if any([True for i in ["VBN", "VB", "VBZ", "VBP", "VBD"] if i in list(chain.from_iterable(ATPOS))]) else "0" for ATPOS in AT_POS_combi]
    noun_inside = ["1" if any([True for i in ["NNS","NN"] if i in list(chain.from_iterable(ATPOS))]) else "0" for ATPOS in AT_POS_combi]
    adj_adv_inside = ["1" if any([True for i in ["JJ","RB", "JJS", "RBS"] if i in list(chain.from_iterable(ATPOS))]) else "0" for ATPOS in AT_POS_combi]
    comp_adj_adv_inside = ["1" if any([True for i in ["JJR","RBR"] if i in list(chain.from_iterable(ATPOS))]) else "0" for ATPOS in AT_POS_combi]
    Verb_in_AT_inst.extend((verb_inside) * AT_repetition)
    Noun_in_AT_inst.extend((noun_inside)* AT_repetition)
    Adj_Adv_in_AT_inst.extend((adj_adv_inside)*AT_repetition)
    Comp_Adj_Adv_in_AT_inst.extend((comp_adj_adv_inside)* AT_repetition)
    # Adj_Adv_outside_AT_inst
    # Verb_outside_AT_inst
    # Noun_outside_AT_inst
    # if it is before or after

    # some_AT_in_brackets
    # all_AT_in_brackets


    # sentence level variables
    split_prepos_idx_disagg.extend([split_prepos[0]] * NR_poss_relat)
    semicolon_idx.extend([semicolon[0]]*NR_poss_relat)
    SENT_disagg.extend([value] * NR_poss_relat)
    DOI_disagg.extend([complete_evidence_Instances['DOI'].iloc[count]] * NR_poss_relat)
    sent_ID_disagg.extend([complete_evidence_Instances['Sentence'].iloc[count]] * NR_poss_relat)
    Nr_AT.extend([len(AT_entities)]* NR_poss_relat)
    Nr_BO.extend([len(BO_entities)-1]* NR_poss_relat)
    Nr_BD.extend([len(BD_entities)]* NR_poss_relat)
    Nr_MO.extend([len(MO_entities)-1]* NR_poss_relat)
    Nr_SG.extend([len(SG_entities)-1]* NR_poss_relat)
    joined_BO_instances.extend([BO_joined]* NR_poss_relat)
    Evidence_Truth.extend(["0"]*NR_poss_relat)
    max_sent_ATidx.extend([max(AT_indices)] * NR_poss_relat)
    min_sent_ATidx.extend([min(AT_indices)] * NR_poss_relat)
    max_sent_BDidx.extend([max(BD_indices)] * NR_poss_relat)
    min_sent_BDidx.extend([min(BD_indices)] * NR_poss_relat)
    if BO_indices != ["NaN"]:
        BO_indices.remove("NaN")
        max_sent_BOidx.extend([max(BO_indices)] * NR_poss_relat)
        min_sent_BOidx.extend([min(BO_indices)] * NR_poss_relat)
    else:
        max_sent_BOidx.extend(["NaN"]*NR_poss_relat)
        min_sent_BOidx.extend(["NaN"]*NR_poss_relat)
    if MO_indices != ["NaN"]:
        MO_indices.remove("NaN")
        max_sent_MOidx.extend([max(MO_indices)] * NR_poss_relat)
        min_sent_MOidx.extend([min(MO_indices)] * NR_poss_relat)
    else:
        max_sent_MOidx.extend(["NaN"]*NR_poss_relat)
        min_sent_MOidx.extend(["NaN"]*NR_poss_relat)
    if SG_indices != ["NaN"]:
        SG_indices.remove("NaN")
        max_sent_SGidx.extend([max(SG_indices)] * NR_poss_relat)
        min_sent_SGidx.extend([min(SG_indices)] * NR_poss_relat)
    else:
        max_sent_SGidx.extend(["NaN"]*NR_poss_relat)
        min_sent_SGidx.extend(["NaN"]*NR_poss_relat)

    # check if all lists same length
    print_summary_of_length_ofLists([BD_disagg, AT_disagg, BO_disagg, SG_disagg, MO_disagg, SENT_disagg, DOI_disagg, sent_ID_disagg,
                                     BD_idx_disagg, AT_idx_disagg, BO_idx_disagg, MO_idx_disagg, SG_idx_disagg,
                                     split_prepos_idx_disagg,Nr_AT, Nr_BO, Nr_BD, Nr_MO, Nr_SG, Nr_verbs, earliestverb_indx,
                                     latestverb_indx, Verb_in_AT_inst, Noun_in_AT_inst, Adj_Adv_in_AT_inst, Comp_Adj_Adv_in_AT_inst,
                                     Nr_ATs_in_instance, Multi_AT_Indice_gap, minimum_AT_idx, maximum_AT_idx, multiAT_shortestPathLen_min,
                                     multiAT_shortestPathLen_max, same_dependTree, joined_BO_instances, AT_BD_minshortpath, AT_BD_maxshortpath,
                                     AT_BD_sumshortpath, AT_BO_minshortpath, AT_BO_maxshortpath, AT_BO_sumshortpath, AT_SG_minshortpath,
                                     AT_SG_maxshortpath, AT_SG_sumshortpath, AT_MO_minshortpath, AT_MO_maxshortpath, AT_MO_sumshortpath,
                                     all_before_or_after_split_propos, index_dist_ATmin_BD, index_dist_ATmax_BD, index_dist_ATmin_BO,
                                     index_dist_ATmax_BO, index_dist_ATmin_MO, index_dist_ATmax_MO, index_dist_ATmin_SG,  index_dist_ATmax_SG,
                                     verb_between_ATmin_BD, verb_between_ATmax_BD, verb_between_ATmin_BO, verb_between_ATmax_BO, verb_between_ATmin_MO,
                                     verb_between_ATmax_MO, verb_between_ATmin_SG, verb_between_ATmax_SG, max_sent_ATidx, min_sent_ATidx,
                                     max_sent_BDidx, min_sent_BDidx, max_sent_BOidx, min_sent_BOidx, max_sent_MOidx, min_sent_MOidx,
                                     max_sent_SGidx, min_sent_SGidx, semicolon_idx, all_before_or_after_semicolon])



possible_evidence_instances = pd.DataFrame({'DOI': DOI_disagg, 'Sentence': sent_ID_disagg, 'Evidence_Truth': Evidence_Truth, 'Fullsentence': SENT_disagg,
                                                 'BehaviorOption': BO_disagg, 'BehaviorDeterminant': BD_disagg,
                                                 'AssociationType': AT_disagg, 'Studygroup': SG_disagg, 'Moderator': MO_disagg,
                                                 'BD_idx': BD_idx_disagg, 'BO_idx': BO_idx_disagg, 'SG_idx': SG_idx_disagg,
                                                 'MO_idx': MO_idx_disagg, 'Split_Propos_idx': split_prepos_idx_disagg,
                                                 'all_before_or_after_split_propos': all_before_or_after_split_propos,
                                                 'semicolon_idx': semicolon_idx, 'all_before_or_after_semicolon': all_before_or_after_semicolon,
                                                 'index_dist_ATmin_BD': index_dist_ATmin_BD, 'index_dist_ATmax_BD': index_dist_ATmax_BD,
                                                 'index_dist_ATmin_BO': index_dist_ATmin_BO, 'index_dist_ATmax_BO': index_dist_ATmax_BO,
                                                 'index_dist_ATmin_MO': index_dist_ATmin_MO, 'index_dist_ATmax_MO': index_dist_ATmax_MO,
                                                 'index_dist_ATmin_SG': index_dist_ATmin_SG,  'index_dist_ATmax_SG': index_dist_ATmax_SG,
                                                 'same_dependTree': same_dependTree, 'joined_BO_instances': joined_BO_instances,
                                                 'Nr_AT': Nr_AT, 'Nr_BO': Nr_BO, 'Nr_BD': Nr_BD, 'Nr_MO': Nr_MO, 'Nr_SG': Nr_SG,
                                                 'Verb_in_AT_inst': Verb_in_AT_inst, 'Noun_in_AT_inst': Noun_in_AT_inst,
                                                 'Adj_Adv_in_AT_inst': Adj_Adv_in_AT_inst, 'Comp_Adj_Adv_in_AT_inst': Comp_Adj_Adv_in_AT_inst,
                                                 'Nr_ATs_in_instance': Nr_ATs_in_instance, 'Multi_AT_Indice_gap': Multi_AT_Indice_gap,
                                                 'minimum_AT_idx': minimum_AT_idx, 'maximum_AT_idx': maximum_AT_idx,
                                                 'Nr_verbs': Nr_verbs, 'earliestverb_indx': earliestverb_indx, 'latestverb_indx': latestverb_indx,
                                                 'multiAT_shortestPathLen_min': multiAT_shortestPathLen_min,'multiAT_shortestPathLen_max': multiAT_shortestPathLen_max,
                                                 'AT_BD_minshortpath': AT_BD_minshortpath, 'AT_BD_maxshortpath': AT_BD_maxshortpath, 'AT_BD_sumshortpath': AT_BD_sumshortpath,
                                                 'AT_BO_minshortpath': AT_BO_minshortpath, 'AT_BO_maxshortpath': AT_BO_maxshortpath, 'AT_BO_sumshortpath': AT_BO_sumshortpath,
                                                 'AT_SG_minshortpath': AT_SG_minshortpath, 'AT_SG_maxshortpath': AT_SG_maxshortpath, 'AT_SG_sumshortpath': AT_SG_sumshortpath,
                                                 'AT_MO_minshortpath': AT_MO_minshortpath, 'AT_MO_maxshortpath': AT_MO_maxshortpath, 'AT_MO_sumshortpath': AT_MO_sumshortpath,
                                                 'verb_between_ATmin_BD': verb_between_ATmin_BD, 'verb_between_ATmax_BD': verb_between_ATmax_BD,
                                                 'verb_between_ATmin_BO': verb_between_ATmin_BO, 'verb_between_ATmax_BO': verb_between_ATmax_BO,
                                                 'verb_between_ATmin_MO': verb_between_ATmin_MO, 'verb_between_ATmax_MO': verb_between_ATmax_MO,
                                                 'verb_between_ATmin_SG': verb_between_ATmin_SG, 'verb_between_ATmax_SG': verb_between_ATmax_SG,
                                                 'max_sent_ATidx': max_sent_ATidx, 'min_sent_ATidx': min_sent_ATidx,
                                                 'max_sent_BDidx': max_sent_BDidx, 'min_sent_BDidx': min_sent_BDidx,
                                                 'max_sent_BOidx': max_sent_BOidx, 'min_sent_BOidx': min_sent_BOidx,
                                                 'max_sent_MOidx': max_sent_MOidx, 'min_sent_MOidx': min_sent_MOidx,
                                                 'max_sent_SGidx': max_sent_SGidx, 'min_sent_SGidx': min_sent_SGidx})

possible_evidence_instances.to_csv("possible_evidence_instances.csv", index=False)
# #
print("Nr of unique articles contributing evidence: ",len(set(possible_evidence_instances['DOI'])))
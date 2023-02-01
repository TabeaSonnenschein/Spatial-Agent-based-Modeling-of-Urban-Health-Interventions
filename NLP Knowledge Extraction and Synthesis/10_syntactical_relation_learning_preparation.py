import os
import spacy
en = spacy.load('en_core_web_sm')
from spacy import displacy
import networkx as nx
from itertools import chain
import statistics
import re
import pandas as pd
import numpy as np

################################################################################################
## This script creates 71 syntactical properties of the labeled sentences to infer which phrase
## relates to which other to create an evidence instance. The property enriched dataframe can
## then be used to train a feature based machine learning model.
################################################################################################

# Functions
def SelectGrammCompleteSent(df):
    """tests which sentences contain at least a verb as a minimum grammatical requirement for a complete
       sentence and then subselects only these sentences."""
    gramm_complete_sentences = [x for i in ['VB', 'VBG', 'VBD', 'VBN', 'VBP', 'VBZ'] for x, y in
                                enumerate(df['sentence_POS']) if i in y]
    df = df.iloc[gramm_complete_sentences]
    return df

def FixBracketsInVariableNames(df):
    """Remove brackets from phrase names of association types and behavior determinants"""
    df['AssociationType'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ","").replace(
            " )", "").replace("(", "").replace(")", "").replace("  ", " ") for x in df['AssociationType']]
    df['BehaviorDeterminant'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ","").replace(
            " )", "").replace("(", "").replace(")", "").replace("  ", " ").replace(" +", "") for x in df['BehaviorDeterminant']]
    return df

def replace_spacestr_NA (list):
    """Replace a list with only an empty space with an empty list."""
    if list == [" "]:
        newlist = []
    else:
        newlist = list
    return newlist

def createEntityList(df):
    """Split the listed phrases per sentences into entities per Label"""
    AT_entities = df['AssociationType'].iloc[count].split(" ; ")
    BD_entities = df['BehaviorDeterminant'].iloc[count].split(" ; ")
    BO_entities = replace_spacestr_NA(df['BehaviorOption'].iloc[count].split(" ; "))
    SG_entities = replace_spacestr_NA(df['Studygroup'].iloc[count].split(" ; "))
    MO_entities = replace_spacestr_NA(df['Moderator'].iloc[count].split(" ; "))
    return AT_entities, BD_entities, BO_entities, SG_entities, MO_entities

def find_indices_words_in_sentence(entity_list, fullsentence):
    """Find the index of the phrases in the sentence."""
    indx = -1
    entity_indices = []
    for entity in entity_list:
        candidates = [(m.start()+1) for m in re.finditer(re.escape(" " + entity + " "), (" " + fullsentence + " ")) if m.start()>= indx][0]
        entity_indices.extend([candidates])
        indx = max(entity_indices)
    return entity_indices


def repeat_each_item_n_times_in_list (list, times):
    """Repeat each item n times in a list"""
    rep_list = []
    for el in list:
        rep_list.extend([el] * times)
    return rep_list


def check_if_in_wordlist_and_append(list_of_lists, wordlist):
    """Checks if any element of a list in the list of lists is in the wordlist
       and then appends it to the output list."""
    output_list = []
    for list in list_of_lists:
        output_list.extend([el for el in list if el in wordlist])
    return output_list


def combinations(items):
    """Creates a list with all combinations of the elements in the items list. """
    comblist = []
    for i in range(0,len(items)):
        comblist.append(items[i])
        for x in range((i+2), (len(items)+1)):
            comblist.append(items[i:x])
            if (i+1) < x < len(items):
                comblist.append([items[i], items[x]])
                if x < (len(items)-1):
                    comblist.append(([items[i]] + items[x:]))
    return comblist

def combinations_NANlists(items):
    """Creates a list with all combinations of the elements in the items list,
       dealing with the issue of NaNs. """
    if items != ["NaN"]:
        items.remove("NaN")
        comblist = combinations(items)
        comblist.extend(["NaN"])
        items.extend(["NaN"])
    else:
        comblist = items
    return comblist

def combinations_alllists(items):
    """Creates a nested list of lists of all combinations of
       the elements of the items list. """
    comblist = []
    for i in range(0,len(items)):
        comblist.append([items[i]])
        for x in range((i+2), (len(items)+1)):
            comblist.append(items[i:x])
            if (i+1) < x < len(items):
                comblist.append([items[i], items[x]])
                if x < (len(items)-1):
                    comblist.append(([items[i]] + items[x:]))
    return comblist


def evidence_instance_appending(ATs, BDs, BOs, SGs, MOs):
    """Creates lists for each label with the correct number of repeats of each phrase,
       so that when placed in a dataframe together it covers all combinations in the correct order."""
    AT_extension, BD_extension, BO_extension, SG_extension, MO_extension = [],[],[],[],[]
    AT_combinations = combinations(ATs)
    SG_combinations = combinations_NANlists(SGs)
    AT_extension.extend((AT_combinations) * len(BDs) * len(BOs) * len(SG_combinations) * len(MOs))
    BD_extension.extend((repeat_each_item_n_times_in_list(BDs, len(AT_combinations))) * len(BOs) * len(SG_combinations) * len(MOs))
    BO_extension.extend((repeat_each_item_n_times_in_list(BOs, (len(BDs)*len(AT_combinations)))) * len(SG_combinations) * len(MOs))
    SG_extension.extend((repeat_each_item_n_times_in_list((SG_combinations), (len(BDs)*len(BOs)*len(AT_combinations)))) * len(MOs))
    MO_extension.extend((repeat_each_item_n_times_in_list(MOs, (len(BDs)*len(BOs)*len(SG_combinations)*len(AT_combinations)))))
    Nr_added = len(AT_combinations) * len(BDs) * len(BOs) * len(SG_combinations) * len(MOs)
    return AT_extension, BD_extension, BO_extension, SG_extension, MO_extension, Nr_added


def test_BO_joined_evidence_instance(BO_words, full_sentence, BO_indices):
    """ Checks if multiple behavior options are mentioned in one evidence instance."""
    if len(BO_indices)>1:
        between_words = full_sentence[min(BO_indices):max(BO_indices)]
        for entity in BO_words:
            between_words = between_words.replace(entity, "")
        between_words = between_words.split()
        if all([True if word in ["and", ",", "the", "as", "well"] else False for word in between_words]):
            return 1
        else:
            return 0
    else:
        return 1


def check_if_varcombi_same_dependency_subtree(varlist_varcombi, totalsentence_varlist, subtrees):
    """ Checks whether the variable combination is part of the same dependency subtree."""
    joined_instance = 0
    missing_var = "NaN"
    remaining_var = [i for i in totalsentence_varlist if (i not in varlist_varcombi) and (i != "NaN")]
    variables = [x for x in varlist_varcombi if x != "NaN"]
    for a in range(0, len(subtrees)):
        if all([True if x in subtrees[a] else False for x in variables]):
            joined_instance += 1
            if any([True if x in subtrees[a] else False for x in remaining_var]):
                missing_var = "1"
            else:
                missing_var = "0"
    if joined_instance > 0:
        return "1", missing_var
    else:
        return "0", missing_var


def Dependencytree_to_Graph(doc):
    """ Load spacy's dependency tree into a networkx graph."""
    edges = []
    for token in doc:
        for child in token.children:
            edges.append(('{0}'.format(token.lower_),
                          '{0}'.format(child.lower_)))
    graph = nx.Graph(edges)
    return graph

def getShortestPathbetweenPhrases(listA, listB, graph):
    """Find the minimum, maximum and sum of shortest path between two phrases
       (multiple words continuesly labeled with the same tag)."""
    shortestPath = []
    if not isinstance(listA, str):
        words_inlistA = list(chain.from_iterable([phrase.split(" ") for phrase in listA]))
    else:
        words_inlistA = listA.split(" ")
    if not isinstance(listB, str):
        words_inlistB = list(chain.from_iterable([phrase.split(" ") for phrase in listB]))
    else:
        words_inlistB = listB.split(" ")
    for f in range(0, len(words_inlistA)):
        for x in range(0, len(words_inlistB)):
            try:
                shortestPath.extend([nx.shortest_path_length(graph, source=words_inlistA[f].lower(),
                                                             target=words_inlistB[x].lower())])
            except nx.exception.NodeNotFound:
                print("Node not found", words_inlistA[f], words_inlistB[x])
            except nx.exception.NetworkXNoPath:
                print("No Path between", words_inlistA[f], "and", words_inlistB[x])
                shortestPath.extend([100])
            else:
                pass
    return [min(shortestPath)], [max(shortestPath)], [sum(shortestPath)]

def print_summary_of_length_ofLists(list_oflists):
    """ Prints the length of all lists and names the outlier lists.
        Helps figuring out errors in case a target list was erroneous."""
    x = [len(element) for element in list_oflists]
    median = int(statistics.median(x))
    print("Median value: ", median, "appears", x.count(median), "times")
    outliers = [count for count, value in enumerate(x) if value != median]
    print("outliers are", outliers)

def ifnotlist_makelist(object):
    """ Makes a list out of non-lists."""
    if not isinstance(object, list):
        return [object]
    else:
        return object

def testVerbInBetween(verb_indx, idx1, idx2 ):
    """ Tests whether there is a verb in between idx1 and idx2. """
    result = ["1" if any(True for x in verb_indx if idx1 > x < idx2
                or idx1 < x > idx2) else "0"]
    return result

def testIfAllPhrasesBeforeIdx(idx, PhraseIndices):
    """ Tests whether all phrases in the variable combination are before a specific index
       or all are after. The important thing is whether they are together (either before or after)
       and not split. An example application is to test whether they are before or after
       split propositions or semicolons."""
    if idx != 'NaN':
        if all(True if x == 'NaN' or x > idx else False for x in PhraseIndices) or all(
                True if x == 'NaN' or x < idx else False for x in PhraseIndices):
            return ["1"]
        else:
            return ["0"]
    else:
        return ["NaN"]

# Execution

#########################################
### READING AND PREPARING DATA ##########
#########################################

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# csv = os.path.join(os.getcwd(), ("Evidence_instances_df_ManualLabel.csv"))
csv = os.path.join(os.getcwd(), ("Evidence_instances_df.csv"))
# csv = os.path.join(os.getcwd(), ("Evidence_instances_df_training_data.csv"))
Evidence_instances_df = pd.read_csv(csv)
# columnnames: 'DOI','Sentence','BehaviorOption','BehaviorDeterminant','AssociationType',
#              'Studygroup','Moderator',Fullsentence','BO_POS','BD_POS',AT_POS','sentence_POS'

## disaggregating evidence of within sentence colocation
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'].notnull()) & (Evidence_instances_df['AssociationType'].notnull()))[0])]
complete_evidence_Instances = complete_evidence_Instances.fillna(" ")

# Fix punctuation
complete_evidence_Instances = FixBracketsInVariableNames(complete_evidence_Instances)
complete_evidence_Instances['Fullsentence'] = [x.replace("?",",") for x in complete_evidence_Instances['Fullsentence']]

## subselecting complete sentences
complete_evidence_Instances = SelectGrammCompleteSent(complete_evidence_Instances)


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
# Variable Combination Indices
BD_idx_disagg, AT_idx_disagg, BO_idx_disagg, MO_idx_disagg, SG_idx_disagg, split_prepos_idx_disagg = [], [], [], [], [], []
all_before_or_after_split_propos, index_dist_ATmin_BD, index_dist_ATmax_BD, index_dist_ATmin_BO, index_dist_ATmax_BO = [], [], [], [], []
index_dist_ATmin_MO, index_dist_ATmax_MO, index_dist_ATmin_SGmin, index_dist_ATmin_SGmax, index_dist_ATmax_SGmin, index_dist_ATmax_SGmax = [], [], [], [], [], []
semicolon_idx, all_before_or_after_semicolon = [], []
min_negator_idx, max_negator_idx = [], []

minimum_AT_idx, maximum_AT_idx, minimum_SG_idx, maximum_SG_idx = [],[], [],[]

# sentence level indices
max_sent_ATidx, min_sent_ATidx, max_sent_BDidx, min_sent_BDidx, max_sent_BOidx, min_sent_BOidx = [], [], [], [], [], []
max_sent_MOidx, min_sent_MOidx, max_sent_SGidx, min_sent_SGidx= [], [], [], []

# Nr entities
Nr_AT, Nr_BO, Nr_BD, Nr_MO, Nr_SG = [], [], [], [], []

# POS properties (part of speech)
Nr_verbs, earliestverb_indx, latestverb_indx = [], [], []

# Association Type properties
Verb_in_AT_inst, Noun_in_AT_inst, Adj_Adv_in_AT_inst, Comp_Adj_Adv_in_AT_inst, Verb_outside_AT_inst, Noun_outside_AT_inst, Adj_Adv_outside_AT_inst = [], [], [], [], [], [], []
Nr_ATs_in_instance, Multi_AT_Indice_gap = [], []
some_AT_in_brackets, all_AT_in_brackets= [], []
multiAT_shortestPathLen_min, multiAT_shortestPathLen_max = [], []
ATinst_has_not, ATsent_has_not = [], []

# combinatory variable properties
same_dependTree, missing_var_in_same_dependTree = [], []
AT_BD_minshortpath, AT_BD_maxshortpath, AT_BD_sumshortpath, AT_BO_minshortpath, AT_BO_maxshortpath, AT_BO_sumshortpath = [], [], [], [], [], []
AT_SG_minshortpath, AT_SG_maxshortpath, AT_SG_sumshortpath, AT_MO_minshortpath, AT_MO_maxshortpath, AT_MO_sumshortpath =  [], [], [], [], [], []
verb_between_ATmin_BD, verb_between_ATmax_BD, verb_between_ATmin_BO, verb_between_ATmax_BO = [], [], [], []
verb_between_ATmin_MO, verb_between_ATmax_MO, verb_between_ATmin_SGmin, verb_between_ATmax_SGmin, verb_between_ATmin_SGmax, verb_between_ATmax_SGmax = [], [], [], [], [], []

#others
joined_BO_instances = []

## filling target lists and syntactical properties
for count, value in enumerate(complete_evidence_Instances['Fullsentence']):
    ## creating entity and idx lists
    AT_entities, BD_entities, BO_entities, SG_entities, MO_entities = createEntityList(complete_evidence_Instances)

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
    negators = [m.start() for x in ["not", "except", "Not"] for m in re.finditer((x), value)]

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
    MO_idx_disagg.extend(MO_extension_indx )
    SG_idx_disagg.extend(SG_extension_indx)

    ATindicelist = combinations_alllists(AT_indices)
    AT_repetition = int(NR_poss_relat/len(ATindicelist))
    Nr_ATs_in_instance.extend([len(x) for x in ATindicelist] * AT_repetition)
    minimum_AT_idx.extend([min(x) for x in ATindicelist] * AT_repetition)
    maximum_AT_idx.extend([max(x) for x in ATindicelist] * AT_repetition)
    Multi_AT_Indice_gap.extend([max(x)-min(x) for x in ATindicelist] * AT_repetition)

    # combinatory syntactical properties
    # part of same subtree + shortest path between all options
    for i in range(0, len(AT_extension_name)):
        same_tree, missing_var_sametree = check_if_varcombi_same_dependency_subtree(list(chain.from_iterable([ifnotlist_makelist(AT_extension_name[i]), ifnotlist_makelist(BD_extension_name[i]),
                                                  ifnotlist_makelist(BO_extension_name[i]), ifnotlist_makelist(SG_extension_name[i]),
                                                  ifnotlist_makelist(MO_extension_name[i])])), list(chain.from_iterable([BO_entities, SG_entities,
                                                  MO_entities])), items_in_subtree_groups)
        same_dependTree.extend(same_tree)
        missing_var_in_same_dependTree.extend([missing_var_sametree])
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
        indices = list(chain.from_iterable([AT_extension_indx_alllists[i], [BD_extension_indx[i]],[BO_extension_indx[i]], ifnotlist_makelist(SG_extension_indx[i]), [MO_extension_indx[i]]]))

        all_before_or_after_split_propos.extend(testIfAllPhrasesBeforeIdx(idx=split_prepos[0], PhraseIndices=indices))
        all_before_or_after_semicolon.extend(testIfAllPhrasesBeforeIdx(idx=semicolon[0], PhraseIndices=indices))

        index_dist_ATmin_BD.extend([min(AT_extension_indx_alllists[i]) - BD_extension_indx[i]])
        index_dist_ATmax_BD.extend([max(AT_extension_indx_alllists[i]) - BD_extension_indx[i]])

        verb_between_ATmin_BD.extend(testVerbInBetween(verb_indx, min(AT_extension_indx_alllists[i]), BD_extension_indx[i]))
        verb_between_ATmax_BD.extend(testVerbInBetween(verb_indx, max(AT_extension_indx_alllists[i]), BD_extension_indx[i]))
        if BO_extension_indx[i] != "NaN":
            index_dist_ATmin_BO.extend([min(AT_extension_indx_alllists[i]) - BO_extension_indx[i]])
            index_dist_ATmax_BO.extend([max(AT_extension_indx_alllists[i]) - BO_extension_indx[i]])

            verb_between_ATmin_BO.extend(testVerbInBetween(verb_indx, min(AT_extension_indx_alllists[i]), BO_extension_indx[i]))
            verb_between_ATmax_BO.extend(testVerbInBetween(verb_indx, max(AT_extension_indx_alllists[i]), BO_extension_indx[i]))
        else:
            index_dist_ATmin_BO.extend(["NaN"])
            index_dist_ATmax_BO.extend(["NaN"])
            verb_between_ATmin_BO.extend(["NaN"])
            verb_between_ATmax_BO.extend(["NaN"])
        if MO_extension_indx[i] != "NaN":
            index_dist_ATmin_MO.extend([min(AT_extension_indx_alllists[i]) - MO_extension_indx[i]])
            index_dist_ATmax_MO.extend([max(AT_extension_indx_alllists[i]) - MO_extension_indx[i]])

            verb_between_ATmin_MO.extend(testVerbInBetween(verb_indx, min(AT_extension_indx_alllists[i]), MO_extension_indx[i]))
            verb_between_ATmax_MO.extend(testVerbInBetween(verb_indx, max(AT_extension_indx_alllists[i]), MO_extension_indx[i]))
        else:
            index_dist_ATmin_MO.extend(["NaN"])
            index_dist_ATmax_MO.extend(["NaN"])
            verb_between_ATmin_MO.extend(["NaN"])
            verb_between_ATmax_MO.extend(["NaN"])
        if SG_extension_indx[i] != "NaN":
            index_dist_ATmin_SGmin.extend([min(AT_extension_indx_alllists[i]) - min(ifnotlist_makelist(SG_extension_indx[i]))])
            index_dist_ATmax_SGmin.extend([max(AT_extension_indx_alllists[i]) - min(ifnotlist_makelist(SG_extension_indx[i]))])
            index_dist_ATmin_SGmax.extend([min(AT_extension_indx_alllists[i]) - max(ifnotlist_makelist(SG_extension_indx[i]))])
            index_dist_ATmax_SGmax.extend([max(AT_extension_indx_alllists[i]) - max(ifnotlist_makelist(SG_extension_indx[i]))])

            verb_between_ATmin_SGmin.extend(testVerbInBetween(verb_indx, min(AT_extension_indx_alllists[i]), min(ifnotlist_makelist(SG_extension_indx[i]))))
            verb_between_ATmax_SGmin.extend(testVerbInBetween(verb_indx, max(AT_extension_indx_alllists[i]), min(ifnotlist_makelist(SG_extension_indx[i]))))
            verb_between_ATmin_SGmax.extend(testVerbInBetween(verb_indx, min(AT_extension_indx_alllists[i]), max(ifnotlist_makelist(SG_extension_indx[i]))))
            verb_between_ATmax_SGmax.extend(testVerbInBetween(verb_indx, max(AT_extension_indx_alllists[i]), max(ifnotlist_makelist(SG_extension_indx[i]))))

            minimum_SG_idx.extend([min(ifnotlist_makelist(SG_extension_indx[i]))])
            maximum_SG_idx.extend([max(ifnotlist_makelist(SG_extension_indx[i]))])
        else:
            index_dist_ATmin_SGmin.extend(["NaN"])
            index_dist_ATmax_SGmin.extend(["NaN"])
            index_dist_ATmin_SGmax.extend(["NaN"])
            index_dist_ATmax_SGmax.extend(["NaN"])
            verb_between_ATmin_SGmin.extend(["NaN"])
            verb_between_ATmax_SGmin.extend(["NaN"])
            verb_between_ATmin_SGmax.extend(["NaN"])
            verb_between_ATmax_SGmax.extend(["NaN"])
            minimum_SG_idx.extend(["NaN"])
            maximum_SG_idx.extend(["NaN"])

    # Association types properties
    # if it contains a negator (not)
    ATsent_has_not.extend([1 if any(True if "not" in phrase else False for phrase in AT_entities) else 0] * NR_poss_relat)

    # direct link between association types
    ATentitylist = combinations_alllists(AT_entities)
    # Get the length and path
    multiAT_shortestPath_min, multiAT_shortestPath_max = [], []
    has_not = []
    for i in range(0, len(ATentitylist)):
        if len(ATentitylist[i]) == 1:
            multiAT_shortestPath_min.extend([0])
            multiAT_shortestPath_max.extend([0])
            has_not.extend([1 if "not" in ATentitylist[i] else 0])
        else:
            multiAT_shortestPath = []
            words_inlist = list(chain.from_iterable([phrase.split(" ") for phrase in ATentitylist[i]]))
            ## checking if any "not" in wordlist
            has_not.extend([1 if "not" in words_inlist else 0])
            for f in range(0, len(words_inlist)):
                for x in range((f + 1), (len(words_inlist))):
                    multiAT_shortestPath.extend([nx.shortest_path_length(graph, source=words_inlist[f].lower(),
                                                                   target=words_inlist[x].lower())])

            multiAT_shortestPath_min.extend([min(multiAT_shortestPath)])
            multiAT_shortestPath_max.extend([max(multiAT_shortestPath)])
    multiAT_shortestPathLen_min.extend(multiAT_shortestPath_min * AT_repetition)
    multiAT_shortestPathLen_max.extend(multiAT_shortestPath_max * AT_repetition)
    ATinst_has_not.extend(has_not * AT_repetition)

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
    if negators:
        min_negator_idx.extend([min(negators)]*NR_poss_relat)
        max_negator_idx.extend([max(negators)]*NR_poss_relat)
    else:
        min_negator_idx.extend(["NaN"] * NR_poss_relat)
        max_negator_idx.extend(["NaN"] * NR_poss_relat)
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
                                     multiAT_shortestPathLen_max, same_dependTree, missing_var_in_same_dependTree, joined_BO_instances,
                                     ATinst_has_not, ATsent_has_not, AT_BD_minshortpath, AT_BD_maxshortpath,
                                     AT_BD_sumshortpath, AT_BO_minshortpath, AT_BO_maxshortpath, AT_BO_sumshortpath, AT_SG_minshortpath,
                                     AT_SG_maxshortpath, AT_SG_sumshortpath, AT_MO_minshortpath, AT_MO_maxshortpath, AT_MO_sumshortpath,
                                     all_before_or_after_split_propos, index_dist_ATmin_BD, index_dist_ATmax_BD, index_dist_ATmin_BO,
                                     index_dist_ATmax_BO, index_dist_ATmin_MO, index_dist_ATmax_MO, index_dist_ATmin_SGmin, index_dist_ATmin_SGmax,
                                     index_dist_ATmax_SGmin, index_dist_ATmax_SGmax,
                                     verb_between_ATmin_BD, verb_between_ATmax_BD, verb_between_ATmin_BO, verb_between_ATmax_BO, verb_between_ATmin_MO,
                                     verb_between_ATmax_MO, verb_between_ATmin_SGmin, verb_between_ATmax_SGmin, verb_between_ATmin_SGmax, verb_between_ATmax_SGmax,
                                     max_sent_ATidx, min_sent_ATidx, max_sent_SGidx, min_sent_SGidx,
                                     max_sent_BDidx, min_sent_BDidx, max_sent_BOidx, min_sent_BOidx, max_sent_MOidx, min_sent_MOidx,
                                     max_sent_SGidx, min_sent_SGidx, semicolon_idx, all_before_or_after_semicolon, max_negator_idx, min_negator_idx])



possible_evidence_instances = pd.DataFrame({'DOI': DOI_disagg, 'Sentence': sent_ID_disagg, 'Evidence_Truth': Evidence_Truth, 'Fullsentence': SENT_disagg,
                                                 'BehaviorOption': BO_disagg, 'BehaviorDeterminant': BD_disagg,
                                                 'AssociationType': AT_disagg, 'Studygroup': SG_disagg, 'Moderator': MO_disagg,
                                                 'BD_idx': BD_idx_disagg, 'BO_idx': BO_idx_disagg,
                                                 'MO_idx': MO_idx_disagg, 'Split_Propos_idx': split_prepos_idx_disagg,
                                                 'all_before_or_after_split_propos': all_before_or_after_split_propos,
                                                 'semicolon_idx': semicolon_idx, 'all_before_or_after_semicolon': all_before_or_after_semicolon,
                                                 'max_negator_idx': max_negator_idx, 'min_negator_idx': min_negator_idx,
                                                 'index_dist_ATmin_BD': index_dist_ATmin_BD, 'index_dist_ATmax_BD': index_dist_ATmax_BD,
                                                 'index_dist_ATmin_BO': index_dist_ATmin_BO, 'index_dist_ATmax_BO': index_dist_ATmax_BO,
                                                 'index_dist_ATmin_MO': index_dist_ATmin_MO, 'index_dist_ATmax_MO': index_dist_ATmax_MO,
                                                 'index_dist_ATmin_SGmin': index_dist_ATmin_SGmin,  'index_dist_ATmax_SGmin': index_dist_ATmax_SGmin,
                                                 'index_dist_ATmin_SGmax': index_dist_ATmin_SGmax, 'index_dist_ATmax_SGmax': index_dist_ATmax_SGmax,
                                                 'same_dependTree': same_dependTree, 'missing_var_in_same_dependTree' : missing_var_in_same_dependTree,  'joined_BO_instances': joined_BO_instances,
                                                 'Nr_AT': Nr_AT, 'Nr_BO': Nr_BO, 'Nr_BD': Nr_BD, 'Nr_MO': Nr_MO, 'Nr_SG': Nr_SG,
                                                 'Verb_in_AT_inst': Verb_in_AT_inst, 'Noun_in_AT_inst': Noun_in_AT_inst,
                                                 'Adj_Adv_in_AT_inst': Adj_Adv_in_AT_inst, 'Comp_Adj_Adv_in_AT_inst': Comp_Adj_Adv_in_AT_inst,
                                                 'Nr_ATs_in_instance': Nr_ATs_in_instance, 'Multi_AT_Indice_gap': Multi_AT_Indice_gap,
                                                 'minimum_AT_idx': minimum_AT_idx, 'maximum_AT_idx': maximum_AT_idx,
                                                 'minimum_SG_idx': minimum_SG_idx, 'maximum_SG_idx': maximum_SG_idx,
                                                 'ATinst_has_not': ATinst_has_not, 'ATsent_has_not': ATsent_has_not,
                                                 'Nr_verbs': Nr_verbs, 'earliestverb_indx': earliestverb_indx, 'latestverb_indx': latestverb_indx,
                                                 'multiAT_shortestPathLen_min': multiAT_shortestPathLen_min,'multiAT_shortestPathLen_max': multiAT_shortestPathLen_max,
                                                 'AT_BD_minshortpath': AT_BD_minshortpath, 'AT_BD_maxshortpath': AT_BD_maxshortpath, 'AT_BD_sumshortpath': AT_BD_sumshortpath,
                                                 'AT_BO_minshortpath': AT_BO_minshortpath, 'AT_BO_maxshortpath': AT_BO_maxshortpath, 'AT_BO_sumshortpath': AT_BO_sumshortpath,
                                                 'AT_SG_minshortpath': AT_SG_minshortpath, 'AT_SG_maxshortpath': AT_SG_maxshortpath, 'AT_SG_sumshortpath': AT_SG_sumshortpath,
                                                 'AT_MO_minshortpath': AT_MO_minshortpath, 'AT_MO_maxshortpath': AT_MO_maxshortpath, 'AT_MO_sumshortpath': AT_MO_sumshortpath,
                                                 'verb_between_ATmin_BD': verb_between_ATmin_BD, 'verb_between_ATmax_BD': verb_between_ATmax_BD,
                                                 'verb_between_ATmin_BO': verb_between_ATmin_BO, 'verb_between_ATmax_BO': verb_between_ATmax_BO,
                                                 'verb_between_ATmin_MO': verb_between_ATmin_MO, 'verb_between_ATmax_MO': verb_between_ATmax_MO,
                                                 'verb_between_ATmin_SGmin': verb_between_ATmin_SGmin, 'verb_between_ATmax_SGmin': verb_between_ATmax_SGmin,
                                                 'verb_between_ATmin_SGmax': verb_between_ATmin_SGmax, 'verb_between_ATmax_SGmax': verb_between_ATmax_SGmax,
                                                 'max_sent_ATidx': max_sent_ATidx, 'min_sent_ATidx': min_sent_ATidx,
                                                 'max_sent_BDidx': max_sent_BDidx, 'min_sent_BDidx': min_sent_BDidx,
                                                 'max_sent_BOidx': max_sent_BOidx, 'min_sent_BOidx': min_sent_BOidx,
                                                 'max_sent_MOidx': max_sent_MOidx, 'min_sent_MOidx': min_sent_MOidx,
                                                 'max_sent_SGidx': max_sent_SGidx, 'min_sent_SGidx': min_sent_SGidx})

possible_evidence_instances.replace({'NaN': -100}, regex=False, inplace=True)


possible_evidence_instances.to_csv("possible_evidence_instances4.csv", index=False)
# #
print("Nr of unique articles contributing evidence: ",len(set(possible_evidence_instances['DOI'])))
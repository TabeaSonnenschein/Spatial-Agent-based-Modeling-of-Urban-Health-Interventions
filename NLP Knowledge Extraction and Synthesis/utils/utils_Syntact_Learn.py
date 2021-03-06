import re
import pandas as pd
import numpy as np
from itertools import chain
import networkx as nx
import statistics

def find_indices_words_in_sentence(entity_list, fullsentence):
    indx = -1
    entity_indices = []
    for entity in entity_list:
        # print(fullsentence)
        # print(entity_list, entity, indx)
        candidates = [(m.start()+1) for m in re.finditer(re.escape(" " + entity + " "), (" " + fullsentence + " ")) if m.start()>= indx][0]
        entity_indices.extend([candidates])
        indx = max(entity_indices)
    return entity_indices

def repeat_each_item_n_times_in_list (list, times):
    rep_list = []
    for el in list:
        rep_list.extend([el] * times)
    return rep_list

def replace_spacestr_NA (list):
    if list == [" "]:
        newlist = []
    else:
        newlist = list
    return newlist

def check_if_in_wordlist_and_append(list_of_lists, wordlist):
    output_list = []
    for list in list_of_lists:
        output_list.extend([el for el in list if el in wordlist])
    return output_list


def combinations(items):
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
    if items != ["NaN"]:
        items.remove("NaN")
        comblist = combinations(items)
        comblist.extend(["NaN"])
        items.extend(["NaN"])
    else:
        comblist = items
    return comblist

def combinations_alllists(items):
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


def evidence_instance_appending_singleAT(ATs, BDs, BOs, SGs, MOs):
    AT_extension, BD_extension, BO_extension, SG_extension, MO_extension = [],[],[],[],[]
    AT_extension.extend([ATs] * len(BDs) * len(BOs) * len(SGs) * len(MOs))
    BD_extension.extend((BDs) * len(BOs) * len(SGs) * len(MOs))
    BO_extension.extend((repeat_each_item_n_times_in_list(BOs, len(BDs))) * len(SGs) * len(MOs))
    SG_extension.extend((repeat_each_item_n_times_in_list(SGs, (len(BDs)*len(BOs)))) * len(MOs))
    MO_extension.extend((repeat_each_item_n_times_in_list(MOs, (len(BDs)*len(BOs)*len(SGs)))))
    return AT_extension, BD_extension, BO_extension, SG_extension, MO_extension

def evidence_instance_appending_singleSG(ATs, BDs, BOs, SGs, MOs):
    AT_extension, BD_extension, BO_extension, SG_extension, MO_extension = [],[],[],[],[]
    AT_combinations = combinations(ATs)
    AT_extension.extend((AT_combinations) * len(BDs) * len(BOs) * len(SGs) * len(MOs))
    BD_extension.extend((repeat_each_item_n_times_in_list(BDs, len(AT_combinations))) * len(BOs) * len(SGs) * len(MOs))
    BO_extension.extend((repeat_each_item_n_times_in_list(BOs, (len(BDs)*len(AT_combinations)))) * len(SGs) * len(MOs))
    SG_extension.extend((repeat_each_item_n_times_in_list(SGs, (len(BDs)*len(BOs)*len(AT_combinations)))) * len(MOs))
    MO_extension.extend((repeat_each_item_n_times_in_list(MOs, (len(BDs)*len(BOs)*len(SGs)*len(AT_combinations)))))
    Nr_added = len(AT_combinations) * len(BDs) * len(BOs) * len(SGs) * len(MOs)
    return AT_extension, BD_extension, BO_extension, SG_extension, MO_extension, Nr_added

def evidence_instance_appending(ATs, BDs, BOs, SGs, MOs):
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

# checks if multiple behavior options are mentioned in one evidence instance
def test_BO_joined_evidence_instance(BO_words, full_sentence, BO_indices):
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


# Load spacy's dependency tree into a networkx graph
def Dependencytree_to_Graph(doc):
    edges = []
    for token in doc:
        for child in token.children:
            edges.append(('{0}'.format(token.lower_),
                          '{0}'.format(child.lower_)))
    graph = nx.Graph(edges)
    return graph

def getShortestPathbetweenPhrases(listA, listB, graph):
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
    x = [len(element) for element in list_oflists]
    median = int(statistics.median(x))
    print("Median value: ", median, "appears", x.count(median), "times")
    outliers = [count for count, value in enumerate(x) if value != median]
    print("outliers are", outliers)

def ifnotlist_makelist(object):
    if not isinstance(object, list):
        return [object]
    else:
        return object
import re
import pandas as pd
import numpy as np
from itertools import chain

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

def evidence_instance_appending(ATs, BDs, BOs, SGs, MOs):
    AT_extension, BD_extension, BO_extension, SG_extension, MO_extension = [],[],[],[],[]
    AT_extension.extend([ATs] * len(BDs) * len(BOs) * len(SGs) * len(MOs))
    BD_extension.extend((BDs) * len(BOs) * len(SGs) * len(MOs))
    BO_extension.extend((repeat_each_item_n_times_in_list(BOs, len(BDs))) * len(SGs) * len(MOs))
    SG_extension.extend((repeat_each_item_n_times_in_list(SGs, (len(BDs)*len(BOs)))) * len(MOs))
    MO_extension.extend((repeat_each_item_n_times_in_list(MOs, (len(BDs)*len(BOs)*len(SGs)))))
    return AT_extension, BD_extension, BO_extension, SG_extension, MO_extension

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


def check_if_varcombi_same_dependency_subtree(AT, BD, BO, SG, MO, subtrees):
    joined_instance = 0
    for a in range(0, len(subtrees)):
        print(list(chain.from_iterable([AT, [BD], [BO], [SG], [MO]])))
        print(subtrees[a])
        if all([True if x in subtrees[a] else False for x in list(chain.from_iterable([AT, [BD], [BO], [SG], [MO]]))]):
            joined_instance += 1
    if joined_instance > 0:
        return "1"
    else:
        return "0"
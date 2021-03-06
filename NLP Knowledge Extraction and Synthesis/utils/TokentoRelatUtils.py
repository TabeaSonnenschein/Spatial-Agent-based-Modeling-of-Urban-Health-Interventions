import os
from typing import List, Any
import pandas as pd
import numpy as np
import nltk


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
    [tags.remove(el) for el in ["-", "the", "a", "s"] if el in tags]
    return tags

def IO_sequence_tracing(indx_list, Words_data):
    tags = []
    if len(indx_list) > 1:
        already_included = -1
        for indx in indx_list:
            if indx > already_included:
                tag_string = str(Words_data.iloc[indx])
                if indx + 1 in indx_list:
                    tag_string = tag_string + " " + str(Words_data.iloc[indx + 1])
                    already_included = indx + 1
                    for x in range(2, len(indx_list)+1):
                        if all(elem in indx_list for elem in range(indx + 1, indx + x+1)):
                            tag_string = tag_string + " " + str(Words_data.iloc[indx + x])
                            already_included = indx + x
                tags.append(tag_string)
    else:
        if bool(indx_list):
            tags.append(Words_data.iloc[indx_list[0]])
    [tags.remove(el) for el in ["-", "the", "a", "s"] if el in tags]
    return tags


def IO_sequence_tracingopt(indx_list, Words_data):
    tags = []
    if len(indx_list) > 1:
        nested_worldlength = [indx_list]
        n_long_words = [i for i in indx_list if i + 1 in indx_list]
        nested_worldlength.append(n_long_words)
        for n in range(2,15):
            n_long_words = [i for i in n_long_words if i+n in indx_list]
            if bool(n_long_words):
                nested_worldlength.append(n_long_words)
        for n in range(len(nested_worldlength)-1, 0, -1):
            for indx in nested_worldlength[n]:
                tags.append(" ".join(Words_data[indx:(indx+n+1)]))
            for x in range(0,n):
                nested_worldlength[x] = [e for e in nested_worldlength[x] if e not in nested_worldlength[n]]
                for g in range(1, int(n-x+1)):
                    nested_worldlength[x] = [e for e in nested_worldlength[x] if e not in list(np.asarray(nested_worldlength[n]) + g)]
        if len(nested_worldlength[0])>0:
            tags.extend(list(Words_data[nested_worldlength[0]]))
    else:
        if bool(indx_list):
            tags.append(Words_data.iloc[indx_list[0]])
    # print(tags)
    [tags.remove(el) for el in ["-", "the", "a", "s"] if el in tags]
    return tags


def extendTagsToAllEqualWordSeq(dataframe):
    labels = list(dict.fromkeys(dataframe['Tag']))
    labels.remove('O')
    for label in labels:
        label_indices = list(np.where(dataframe['Tag'] == label)[0])
        unique_labeled_words = list(dict.fromkeys(IO_sequence_tracingopt(indx_list=label_indices, Words_data=dataframe['Word'])))
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
    unique_labeled_words = list(dict.fromkeys(IO_sequence_tracingopt(indx_list=label_indices, Words_data=dataframe['Word'])))
    [unique_labeled_words.remove(el) for el in ["-", "the", "a"] if el in unique_labeled_words]
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


def addPOS(dataframe):
    POS = list(nltk.pos_tag([str(word) for word in dataframe['Word']]))
    POS = pd.DataFrame(data=POS, columns=["Word", "POS_tag"])
    dataframe['POS'] = POS["POS_tag"]
    dataframe['POS'].iloc[list(np.where((dataframe['Word'] == "[SEP]") | (dataframe['Word'] == "[CLS]"))[0])] = 'PAD'
    dataframe['POS'].iloc[list(np.where((dataframe['Word'] == "[") | (dataframe['Word'] == "]")| (dataframe['Word'] == "(") | (dataframe['Word'] == ")"))[0])] = '.'
    dataframe['POS'].iloc[list(np.where((dataframe['Word'] == "whereas") | (dataframe['Word'] == "while")| (dataframe['Word'] == "unlike") | (dataframe['Word'] == "although")|(dataframe['Word'] == "though")| (dataframe['Word'] == "such"))[0])] = 'IN'
    return dataframe

def extendVariableNamesToNeighboringAdjectNouns(dataframe, Tagnames):
    for Tagname in Tagnames:
        for turn in [1,2,3,4]:
            label_indices = list(np.where(dataframe['Tag'] == Tagname)[0])
            label_indices_post = [i+1 for i in label_indices]
            label_indices_pre = [i-1 for i in label_indices]
            x = list(np.where(dataframe['Tag'].iloc[label_indices_post] == 'O')[0])
            f = list(np.where(dataframe['Tag'].iloc[label_indices_pre] == 'O')[0])
            if Tagname == "I-behavDeterm":
                y = [i for i in label_indices_post if (dataframe['POS'].iloc[i] in ["NN", "NNS", "JJ", "JJS"]) or (dataframe['Word'].iloc[i] in ["of", "over", "/", "the"])]
                g = [i for i in label_indices_pre if ((dataframe['POS'].iloc[i] in ["NN", "NNS", "JJ", "JJS", "VBN", "JJR", "VBD"]) or (dataframe['Word'].iloc[i] in ["of", "over", "/", "the", "-"])) and (dataframe['Word'].iloc[i] != "s")]
            else:
                y = [label_indices_post[i] for i in x if (dataframe['POS'].iloc[label_indices_post[i]] in ["NN", "NNS", "JJ", "JJS"])]
                g = [label_indices_pre[i] for i in f if (dataframe['POS'].iloc[label_indices_pre[i]] in ["NN", "NNS", "JJ", "JJS"]) and (dataframe['Word'].iloc[label_indices_pre[i]] != "s")]
            dataframe['Tag'].iloc[y] = Tagname
            dataframe['Tag'].iloc[g] = Tagname
            label_indices = list(np.where(dataframe['Tag'] == Tagname)[0])
            open_hyphens = [i-1 for i in label_indices if (dataframe['Word'].iloc[i] == '-') and (i-1 not in label_indices)]
            dataframe['Tag'].iloc[open_hyphens] = Tagname
            open_hyphens = [i+1 for i in label_indices if (dataframe['Word'].iloc[i] == '-') and (i+1 not in label_indices)]
            dataframe['Tag'].iloc[open_hyphens] = Tagname
            open_slash = [i-1 for i in label_indices if (dataframe['Word'].iloc[i] == '/') and (i-1 not in label_indices)]
            dataframe['Tag'].iloc[open_slash] = Tagname
            open_slash = [i+1 for i in label_indices if (dataframe['Word'].iloc[i] == '/') and (i+1 not in label_indices)]
            dataframe['Tag'].iloc[open_slash] = Tagname
            y = [i for i in label_indices_post if ((dataframe['POS'].iloc[i-1] in ["JJ", "JJS"]) or (
                        "," in dataframe['Word'].iloc[i-4:i])) and (dataframe['Word'].iloc[i] in ["and", "or"]) and (dataframe['Tag'].iloc[i+1] == Tagname)]
            dataframe['Tag'].iloc[y] = Tagname
            y = [i for i in label_indices_post if (dataframe['POS'].iloc[i - 1] in ["NN", "NNS"]) and (dataframe['Word'].iloc[i] in ["and", "or"]) and (
                             dataframe['Tag'].iloc[i + 1] == Tagname) and (((
                             dataframe['Tag'].iloc[i + 2] == Tagname) and (dataframe['Tag'].iloc[i-2] != Tagname)) or ((
                             dataframe['Tag'].iloc[i - 2] == Tagname) and (dataframe['Tag'].iloc[i+2] != Tagname)))]
            dataframe['Tag'].iloc[y] = Tagname
            y = [i for i in label_indices_post if (
                        "," in dataframe['Word'].iloc[i-3:i]) and ((
                        "," in dataframe['Word'].iloc[i+1:i+4]) or (
                        "." in dataframe['Word'].iloc[i+1:i+4])) and (dataframe['Word'].iloc[i] in ["and", "or"]) and (
                             dataframe['Tag'].iloc[i + 1] == Tagname) and ((
                             dataframe['Tag'].iloc[i + 2] == Tagname) or (
                             dataframe['Tag'].iloc[i - 2] == Tagname))]
            dataframe['Tag'].iloc[y] = Tagname
    return dataframe

def extendAssociationTypesToNeighboringAdjectNegatives(dataframe):
    for turn in [1,2,3]:
        label_indices = list(np.where(dataframe['Tag'] == 'I-assocType')[0])
        label_indices_post = [i+1 for i in label_indices]
        label_indices_pre = [i-1 for i in label_indices]
        x = list(np.where(dataframe['Tag'].iloc[label_indices_post] == 'O')[0])
        f = list(np.where(dataframe['Tag'].iloc[label_indices_pre] == 'O')[0])
        g = [label_indices_pre[i] for i in f if (dataframe['Word'].iloc[label_indices_pre[i]] in ["non", "not", "Non", "Not", "no", "No", "nil", "relationship", "relationships", "effect", "impact"]) or (dataframe['POS'].iloc[label_indices_pre[i]] in ["JJ", "JJS", "JJR"])]
        y = [label_indices_post[i] for i in x if (dataframe['Word'].iloc[label_indices_post[i]] in ["no", "not", "No", "Not", "nil", "relationship", "relationships", "effect", "impact"]) or (dataframe['POS'].iloc[label_indices_post[i]] in ["JJ", "JJS", "JJR"])]
        dataframe['Tag'].iloc[y] = 'I-assocType'
        dataframe['Tag'].iloc[g] = 'I-assocType'
        label_indices_post = [i + 2 for i in label_indices]
        label_indices_pre = [i - 2 for i in label_indices]
        x = list(np.where(dataframe['Tag'].iloc[label_indices_post] == 'O')[0])
        f = list(np.where(dataframe['Tag'].iloc[label_indices_pre] == 'O')[0])
        g = [label_indices_pre[i] for i in f if (dataframe['Word'].iloc[label_indices_pre[i]] in ["non", "not", "Non", "Not", "no", "No", "Lack", "lack", "nil", "relationship", "relationships", "effect", "impact"]) or (
                dataframe['POS'].iloc[label_indices_pre[i]] in ["JJ", "JJS", "JJR"])]
        y = [label_indices_post[i] for i in x if (dataframe['Word'].iloc[label_indices_post[i]] in ["no", "not", "No", "Not", "nil", "relationship", "relationships", "effect", "impact"])]
        dataframe['Tag'].iloc[y] = 'I-assocType'
        dataframe['Tag'].iloc[g] = 'I-assocType'
        label_indices = list(np.where(dataframe['Tag'] == 'I-assocType')[0])
        assoc_sent = [count for count, value in enumerate(dataframe['Sentence']) if (value in list(set(dataframe['Sentence'].iloc[label_indices]))) and dataframe['Tag'].iloc[count] == "O"]
        y = [i for i in assoc_sent if str(dataframe['Word'].iloc[i]).lower() in ["evidence", "not", "no", "nil", "relationship", "relationships", "effect", "influence", "impact", "positive", "negative", "mixed", "high"]]
        dataframe['Tag'].iloc[y] = 'I-assocType'
    return dataframe

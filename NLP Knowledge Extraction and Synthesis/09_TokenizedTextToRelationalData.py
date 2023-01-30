import os
import pandas as pd
import numpy as np
import nltk

# Functions
def IOB_sequence_tracing(B_indx_list, I_index_list, Words_data):
    """Identify phrases based on continues labeling of word sequences with the same tag
       for IOB labeling."""
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
    """Identify phrases based on continues labeling of word sequences with the same tag
       for IO labeling."""
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
    """Identify phrases based on continues labeling of word sequences with the same tag
       for IO labeling. This function is designed to be used dynamically in other functions."""
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
    """Extend labels of all phrases to equivalent phrases in the rest of the document."""
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
    """Extend all phrases of a specific Label to equivalent phrases in the rest of the document."""
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
    """ Add a part of speech tag to a list of words in sentences. """
    POS = list(nltk.pos_tag([str(word) for word in dataframe['Word']]))
    POS = pd.DataFrame(data=POS, columns=["Word", "POS_tag"])
    dataframe['POS'] = POS["POS_tag"]
    dataframe['POS'].iloc[list(np.where((dataframe['Word'] == "[SEP]") | (dataframe['Word'] == "[CLS]"))[0])] = 'PAD'
    dataframe['POS'].iloc[list(np.where((dataframe['Word'] == "[") | (dataframe['Word'] == "]")| (dataframe['Word'] == "(") | (dataframe['Word'] == ")"))[0])] = '.'
    dataframe['POS'].iloc[list(np.where((dataframe['Word'] == "whereas") | (dataframe['Word'] == "while")| (dataframe['Word'] == "unlike") | (dataframe['Word'] == "although")|(dataframe['Word'] == "though")| (dataframe['Word'] == "such"))[0])] = 'IN'
    return dataframe

def extendVariableNamesToNeighboringAdjectNouns(dataframe, Tagnames):
    """Extend Labeled Phrases to neighboring adjectives or nouns to be sure to capture the whole variable name."""
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
    """Extend Association Type phrases to neighboring adjectives and negatives."""
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

def LabelAssocTypeWords(labeled_data):
    """Label words that are obviously describing statistical associations based on keywords."""
    x = list(np.where((labeled_data['Word'] == 'significant') | (
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
                            labeled_data['Word'] == 'influence'))[0])
    labeled_data['Tag'].iloc[x] = 'I-assocType'
    return labeled_data

def ExtendATwordsToNegation(labeled_data):
    """Identify linked negation words and label them to make sure the correct association type is identified."""
    AT_words = list(np.where(labeled_data['Tag'] == 'I-assocType')[0])
    x = []
    x.extend(idx - 1 for idx in AT_words if
             labeled_data['Word'].iloc[idx - 1] in ["non", "not", "Non", "Not", "no", "No", "nil"])
    x.extend(idx - 2 for idx in AT_words if
             labeled_data['Word'].iloc[idx - 2] in ["non", "not", "Non", "Not", "no", "No", "Lack", "lack", "nil"])
    labeled_data['Tag'].iloc[x] = 'I-assocType'
    return labeled_data

def FillLinkingATs(labeled_data):
    """Identify linking words between 2 AT phrases and label them to unify the phrase."""
    AT_words = list(np.where(labeled_data['Tag'] == 'I-assocType')[0])
    x = [x+1 for x in AT_words if (x+2 in AT_words) and (labeled_data['Word'].iloc[x+1] in ["of", ",", "and", "for", "to", "a", "the"])]
    x.extend((x+2 for x in AT_words if (x+3 in AT_words) and (labeled_data['Word'].iloc[x+1] in ["of", ",", "and", "for", "to", "a", "the"]) and (labeled_data['Word'].iloc[x+2] in ["of", ",", "and", "for", "to", "a", "the"])))
    labeled_data['Tag'].iloc[x] = 'I-assocType'
    return labeled_data


def UniqueLabelsFreq(phraselist):
    """Find unique Labels and count their frequency"""
    Labels, freq_Labels = [], []
    for instance in phraselist:
        Labels.extend(instance.split(" ; "))
    unique_Labels = list(dict.fromkeys(Labels))
    for Label in unique_Labels:
        freq_Labels.append(Labels.count(Label))
    return unique_Labels, freq_Labels


def FindIndexesPerLabel_IO(labeled_data, sentence_idx_range):
    """ Composes lists of indices per label for IO labeling. """
    AT_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-assocType")[0])
    BO_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavOption")[0])
    BD_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavDeterm")[0])
    SG_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-studygroup")[0])
    MO_indx = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-moderator")[0])
    return AT_indx, BO_indx, BD_indx, SG_indx, MO_indx


def FindIndexesPerLabel_IOB(labeled_data, sentence_idx_range):
    """ Composes lists of indices per label for IOB labeling. """
    AT_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-assocType")[0])
    AT_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-assocType")[0])
    BO_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-behavOption")[0])
    BO_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavOption")[0])
    BD_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-behavDeterm")[0])
    BD_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-behavDeterm")[0])
    SG_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-studygroup")[0])
    SG_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-studygroup")[0])
    MO_indx_B = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "B-moderator")[0])
    MO_indx_I = list(np.where(labeled_data['Tag'].iloc[sentence_idx_range] == "I-moderator")[0])
    return AT_indx_B, AT_indx_I, BO_indx_B, BO_indx_I, BD_indx_B, BD_indx_I, SG_indx_B, SG_indx_I, MO_indx_B, MO_indx_I

# Execution

############ Abbreviation list
## ST = study, BD = Behavior Determinant, BO = Behavior Choice Option, AT = Association Type, SG = Study Group, MO = Moderator

# Settings
# mode = "IOB"
mode = "IO"
TagToWordExtension = False     # Do you want that labeled phrases are extended to all equivalent words in the rest of the document?
manual_label = False           # Do you want to summarize the manually labeled data

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

    # Sometimes [SEP] and [CLS] are wrongly assigned a label.
    labeled_data['Tag'].iloc[list(np.where((labeled_data['Word'] == "[SEP]") | (labeled_data['Word'] == "[CLS]") | (labeled_data['Word'] == ".") | (labeled_data['Word'] == "s")| (labeled_data['Word'] == "'"))[0])] = 'O'

    # we extend our data with part of speech tags
    labeled_data = addPOS(labeled_data)

    # we extend the association types to relevant neighbors and keywords
    labeled_data = LabelAssocTypeWords(labeled_data)
    labeled_data = ExtendATwordsToNegation(labeled_data)
    labeled_data = FillLinkingATs(labeled_data)

    # we extent the other labels to full variable name phrases
    dataframe = extendVariableNamesToNeighboringAdjectNouns(labeled_data, ["I-behavDeterm", "I-behavOption", "I-moderator"])
    dataframe = extendAssociationTypesToNeighboringAdjectNegatives(labeled_data)
    if TagToWordExtension:
        labeled_data = extendTagsToAllEqualWordSeq(labeled_data)
    labeled_data = extendSpecificTagsToAllEqualWordSeq(labeled_data, "I-behavOption")

    ## Composing relational dataset of phrases per label per sentence
    sentences = list(dict.fromkeys(labeled_data['Sentence']))
    for sentence in sentences:
        sentence_idx_range = np.where(labeled_data['Sentence'] == sentence)[0]
        sent_POS = labeled_data['POS'].iloc[sentence_idx_range]
        if any(labeled_data['Tag'].iloc[sentence_idx_range] != 'O'):
            if mode == "IOB":
                # if IOB has sufficient quality to distinguish ingroup classification
                AT_indx_B, AT_indx_I, BO_indx_B, BO_indx_I, BD_indx_B, BD_indx_I, SG_indx_B, SG_indx_I, MO_indx_B, MO_indx_I = FindIndexesPerLabel_IOB(labeled_data,sentence_idx_range)
                instance_AT.append(" ; ".join(IOB_sequence_tracing(B_indx_list=AT_indx_B, I_index_list=AT_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BO.append(" ; ".join(IOB_sequence_tracing(B_indx_list=BO_indx_B, I_index_list=BO_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_BD.append(" ; ".join(IOB_sequence_tracing(B_indx_list=BD_indx_B, I_index_list=BD_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_SG.append(" ; ".join(IOB_sequence_tracing(B_indx_list=SG_indx_B, I_index_list=SG_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))
                instance_MO.append(" ; ".join(IOB_sequence_tracing(B_indx_list=MO_indx_B, I_index_list=MO_indx_I, Words_data=labeled_data['Word'].iloc[sentence_idx_range])))

            if mode == "IO":
                # if IOB has not sufficient quality to distinguish ingroup classification, or IO labeling was used
                AT_indx, BO_indx, BD_indx, SG_indx, MO_indx = FindIndexesPerLabel_IO(labeled_data, sentence_idx_range)
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


# make dataframe
Evidence_instances_df = pd.DataFrame({'DOI': instance_ST, 'Sentence': sentenceid, 'BehaviorOption': instance_BO, 'BehaviorDeterminant': instance_BD, 'AssociationType': instance_AT, 'Studygroup': instance_SG, 'Moderator': instance_MO ,  'Fullsentence': fullsentence, 'BO_POS': BO_POS, 'BD_POS': BD_POS, 'AT_POS': AT_POS, 'sentence_POS': sentence_POS })
print(Evidence_instances_df.head())

# write dataframe
if TagToWordExtension:
    file_name_suffix = "_enhanced"
else:
    file_name_suffix = ""

if manual_label:
    file_name_suffix2 = "_ManualLabel"
else:
    file_name_suffix2 = ""

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
csv = os.path.join(os.getcwd(), ("Evidence_instances_df"+ file_name_suffix2 +file_name_suffix + ".csv"))
Evidence_instances_df.to_csv(csv, index=False)

# subselect evidence instances with at least a behavior determinant and an association type
# This is the minimum requirement for a complete evidence instance
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'] != "") & (Evidence_instances_df['AssociationType'] != ""))[0])]
print(complete_evidence_Instances.head())
csv = os.path.join(os.getcwd(), ("Complete_evidence_Instances"+ file_name_suffix2 +file_name_suffix + ".csv"))
complete_evidence_Instances.to_csv(csv, index=False)

# write the unique labels and their frequency
if manual_label == False:
    unique_BD, freq_BD = UniqueLabelsFreq(complete_evidence_Instances['BehaviorDeterminant'])
    pd.DataFrame({'BehaviorDeterm': unique_BD, 'Freq': freq_BD}).to_csv(os.path.join(os.getcwd(), ("unique_BehaviorDeterminants.csv")), index=False)

    unique_BO, freq_BO = UniqueLabelsFreq(complete_evidence_Instances['BehaviorOption'])
    pd.DataFrame({'BehaviorOption': unique_BO, 'Freq': freq_BO}).to_csv(os.path.join(os.getcwd(), ("unique_BehaviorOptions.csv")), index=False)

    unique_AT, freq_AT = UniqueLabelsFreq(complete_evidence_Instances['AssociationType'])
    pd.DataFrame(unique_AT).to_csv(os.path.join(os.getcwd(), ("unique_AssociationTypes.csv")), index=False)


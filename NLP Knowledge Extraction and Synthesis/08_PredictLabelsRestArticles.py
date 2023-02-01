import pandas as pd
import numpy as np
import torch
import os
from itertools import chain
import pickle

####################################################################################################
## This script can be used to apply the trained BERT model to other articles to predict their labels.
####################################################################################################

# Functions
def flatten(listOfLists):
    """Flatten one level of nesting"""
    return list(chain.from_iterable(listOfLists))

def predict_labels(doc):
    """Predict the labels for all sentences of a document."""
    labels, tags, sentenceid = [], [], []
    for count, value in enumerate(dict.fromkeys(doc["Sentence #"])):
        subset = doc.iloc[doc.index[doc["Sentence #"] == value]]
        test_sentence = " ".join(str(item) for item in subset['Word'])
        tokenized_sentence = tokenizer.encode(test_sentence)
        input_ids = torch.tensor([tokenized_sentence]).cuda()
        with torch.no_grad():
            output = model(input_ids)
        label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)

        # join bpe split tokens
        tokens = tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
        new_tokens, new_labels = [], []
        for token, label_idx in zip(tokens, label_indices[0]):
            if token.startswith("##"):
                new_tokens[-1] = new_tokens[-1] + token[2:]
            else:
                new_labels.append(tag_values[label_idx])
                new_tokens.append(token)
        # for token, label in zip(new_tokens, new_labels):
            # print("{}\t{}".format(label, token))
        labels.append(new_labels)
        tags.append(new_tokens)
        # sentenceid.append(value.extend([value] * len(new_tokens)))
        sentenceid.append([value] * len(new_tokens))
    return pd.DataFrame({'Sentence': flatten(sentenceid), 'Tag': flatten(labels),'Word': flatten(tags)})

# Execution

# Load the model
os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
modelname = "BERT_NER_epoch7_wF1_0_88.pickle"
output_model = ('D:/PhD EXPANSE/Written Paper/02- Behavioural Model paper/' + modelname)
model = pickle.load(open(output_model, 'rb'))
tokenizer = model.tokenizer
tag_values = model.tag_values


# Load the files and apply the named entity recognition model
# We start with XML documents due to the superior text cleanliness
listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "xml_csvs"))
for file in listOfFiles:
    doc_txt = pd.read_csv(os.path.join(os.getcwd(), ("xml_csvs/" + file)), encoding="latin1")
    d = predict_labels(doc_txt)
    print(file)
    # print(d)
    d.to_csv(os.path.join(os.getcwd(), ("predict_labeled_NEW/" + file)), index=False)

# Then we test for the pdf documents whether an xml version has been already labeled.
# If not, then the pdf text will be labeled.
listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "pdftxt_csvs"))
xml_doclist = os.listdir(path=os.path.join(os.getcwd(), "xml_csvs"))
for file in listOfFiles:
    if file in xml_doclist:
        print("file already labeled")
    else:
        doc_txt = pd.read_csv(os.path.join(os.getcwd(), ("pdftxt_csvs/" + file)), encoding="latin1")
        d = predict_labels(doc_txt)
        print(file)
        # print(d)
        d.to_csv(os.path.join(os.getcwd(), ("predict_labeled_NEW/" + file)), index=False)
import pandas
import pandas as pd
import numpy as np
from tqdm import tqdm, trange
import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertConfig
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import transformers
from transformers import BertForTokenClassification, AdamW
from transformers import get_linear_schedule_with_warmup
from seqeval.metrics import f1_score, accuracy_score, classification_report
import matplotlib.pyplot as plt
#%matplotlib inline
import seaborn as sns
import os
from itertools import chain
import pickle

torch.__version__
transformers.__version__

## settings (hardware usage and model parameters)
print(torch.cuda.is_available())
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
n_gpu = torch.cuda.device_count()
torch.cuda.get_device_name(0)
print(torch.cuda.get_device_name(0))
MAX_LEN = 75
bs = 32

## loading and preparing data
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
epochs = 3
tokenizer = BertTokenizer.from_pretrained('bert-base-cased', do_lower_case=False)
open_file = open("tag_values.pkl", "rb")
tag_values = pickle.load(open_file)
open_file.close()
print(tag_values)

# load model
model = BertForTokenClassification.from_pretrained(
    "bert-base-cased",
    num_labels=len(tag_values),
    output_attentions = False,
    output_hidden_states = False
)
output_model = ('C:/Users/Tabea/Documents/PhD EXPANSE/Written Paper/02- Behavioural Model paper/model_' + str(epochs) + '.bin')
model.load_state_dict(torch.load(output_model))
model.to(device)

def flatten(listOfLists):
    "Flatten one level of nesting"
    return list(chain.from_iterable(listOfLists))

def predict_labels(doc):
    labels = []
    tags = []
    sentenceid = []
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
        for token, label in zip(new_tokens, new_labels):
            print("{}\t{}".format(label, token))
        labels.append(new_labels)
        tags.append(new_tokens)
        # sentenceid.append(value.extend([value] * len(new_tokens)))
        sentenceid.append([value] * len(new_tokens))
    return pd.DataFrame({'Sentence': flatten(sentenceid), 'Word': flatten(labels),'Tag': flatten(tags)})


listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "xml_csvs"))
for file in listOfFiles:
    doc_txt = pd.read_csv(os.path.join(os.getcwd(), ("xml_csvs/" + file)), encoding="latin1")
    d = predict_labels(doc_txt)
    # print(d)
    d.to_csv(os.path.join(os.getcwd(), ("predict_labeled/" + file)), index=False)

listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "pdftxt_csvs"))
for file in listOfFiles:
    doc_txt = pd.read_csv(os.path.join(os.getcwd(), ("pdftxt_csvs/" + file)), encoding="latin1")
    d = predict_labels(doc_txt)
    print(d)
    d.to_csv(os.path.join(os.getcwd(), ("predict_labeled/" + file)), index=False)
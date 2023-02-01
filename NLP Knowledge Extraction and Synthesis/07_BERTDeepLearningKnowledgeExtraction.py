import pandas as pd
import numpy as np
from tqdm import trange
import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
import transformers
from transformers import BertForTokenClassification, AdamW, BertTokenizer, BertConfig, get_linear_schedule_with_warmup, AutoTokenizer, AutoModelForTokenClassification, logging
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from seqeval.metrics import f1_score, accuracy_score, classification_report
from sklearn.metrics import f1_score as f1sc
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle

logging.set_verbosity_warning()
torch.__version__
transformers.__version__

###################################################################################################
## This script trains a BERT Named Entity Recognition Model and saves the one with the best F1 score
## Moreover it generates a figure with the model performance (Learning curve)
####################################################################################################

## Functions
class SentenceGetter(object):
    """New class of a sentence Getter"""
    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func = lambda s: [(w, p, t) for w, p, t in zip(s["Word"].values.tolist(),
                                                           s["POS"].values.tolist(),
                                                           s["Tag"].values.tolist())]
        self.grouped = self.data.groupby("Sentence #").apply(agg_func)
        self.sentences = [s for s in self.grouped]
    def get_next(self):
        try:
            s = self.grouped["Sentence: {}".format(self.n_sent)]
            self.n_sent += 1
            return s
        except:
            return None

def GetSentencesLables(data):
    """ Applies Sentence Getter to data and generates sentences and labels lists."""
    getter = SentenceGetter(data)
    sentences = [[word[0] for word in sentence] for sentence in getter.sentences]
    print("Example sentence:", sentences[1])
    labels = [[s[2] for s in sentence] for sentence in getter.sentences]
    print("Example labels:", labels[1])
    print()
    return sentences, labels

def PrepareDumpTagValues(data):
    """Gets the Tag values and saves them as a pickle file.
       Also generates the tag to index map (tag2idx)."""
    tag_values = list(set(data["Tag"].values))
    tag_values.append("PAD")
    open_file = open("tag_values.pkl", "wb")
    pickle.dump(tag_values, open_file)
    open_file.close()
    tag2idx = {t: i for i, t in enumerate(tag_values)}
    print("List of tag values:", tag_values)
    return tag_values, tag2idx

def GetUniqueLabes(data):
    """Gets the unique tag labels."""
    unique_labels = list(set(data["Tag"].values))
    unique_labels.remove("O")
    print("uniq Tags:", unique_labels)
    return unique_labels

def tokenize_and_preserve_labels(sentence, text_labels):
    tokenized_sentence = []
    labels = []
    for word, label in zip(sentence, text_labels):
        # Tokenize the word and count # of subwords the word is broken into
        tokenized_word = tokenizer.tokenize(word)
        n_subwords = len(tokenized_word)
        # Add the tokenized word to the final tokenized word list
        tokenized_sentence.extend(tokenized_word)
        # Add the same label to the new list of labels `n_subwords` times
        labels.extend([label] * n_subwords)
    return tokenized_sentence, labels

def PlotLearningCurve(unique_labels, F1_per_class,F1_score_values, loss_values, validation_loss_values, accuracy_values):
    """ Takes the BERT output and plots it into a single figure with performance over epochs differentiated by labels. """
    # Use plot styling from seaborn.
    sns.set(style='darkgrid')
    # Increase the plot size and font size.
    sns.set(font_scale=1.5)
    plt.rcParams["figure.figsize"] = (12, 6)
    colorset = ["#663300", "#004C99", "#FF8000", "#009999", "#FF33FF"]
    for count, value in enumerate(unique_labels):
        plt.plot([x[count] for x in F1_per_class], "--o", color=colorset[count],
                 label=("F1-" + value.replace("I-", "")))
    plt.plot(F1_score_values, "--^", color="#009900", linewidth=3, markersize=13, label="F1-score weighted total")
    plt.plot(loss_values, color="#0000FF", linewidth=2.5, label="training loss")
    plt.plot(validation_loss_values, color="#CC0000", linewidth=2.5, label="validation loss")
    plt.plot(accuracy_values, color="#6600CC", linewidth=2.5, label="validation accuracy")
    plt.title("Learning curve")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend(bbox_to_anchor=(1.02, 1), borderaxespad=0)  # legend in upper right corner outside plot
    plt.tight_layout()
    return plt


## Setting Params

## hardware settings
print(torch.cuda.is_available())
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
n_gpu = torch.cuda.device_count()
torch.cuda.get_device_name(0)
print(torch.cuda.get_device_name(0))

## model parameters
MAX_LEN = 75
bs = 35     # batch size, the larger batch size the more chance of finding global optimum, but also chance of overfitting to labeled dataset
test_percentage = 0.1
epochs = 10
learning_rate = 4e-5
epsilon = 1e-8      #Adam’s epsilon for numerical stability.
weight_decay = 0 # form of regularization to lower the chance of overfitting, default is 0
nr_articles_labeled = 5

pretrained_model = "bert-base-cased"
# pretrained_model = "bert-base-uncased"


## Execution

## loading and preparing data
os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
data = pd.read_csv("manually_labeled/labeled_articles_joined_IO.csv", encoding="latin1").fillna("O")
print(data.head(10))

sentences, labels = GetSentencesLables(data)
tag_values, tag2idx = PrepareDumpTagValues(data)
unique_labels = GetUniqueLabes(data)


## applying BERT
# Prepare the sentences and labels
tokenizer = BertTokenizer.from_pretrained(pretrained_model, do_lower_case=False)

tokenized_texts_and_labels = [
    tokenize_and_preserve_labels(sent, labs)
    for sent, labs in zip(sentences, labels)
]

tokenized_texts = [token_label_pair[0] for token_label_pair in tokenized_texts_and_labels]
labels = [token_label_pair[1] for token_label_pair in tokenized_texts_and_labels]

input_ids = pad_sequences([tokenizer.convert_tokens_to_ids(txt) for txt in tokenized_texts],
                          maxlen=MAX_LEN, dtype="long", value=0.0,
                          truncating="post", padding="post")

tags = pad_sequences([[tag2idx.get(l) for l in lab] for lab in labels],
                     maxlen=MAX_LEN, value=tag2idx["PAD"], padding="post",
                     dtype="long", truncating="post")

attention_masks = [[float(i != 0.0) for i in ii] for ii in input_ids]

tr_inputs, val_inputs, tr_tags, val_tags = train_test_split(input_ids, tags,
                                                            random_state=2018, test_size=test_percentage)
tr_masks, val_masks, _, _ = train_test_split(attention_masks, input_ids,
                                             random_state=2018, test_size=test_percentage)

tr_inputs = torch.tensor(tr_inputs)
val_inputs = torch.tensor(val_inputs)
tr_tags = torch.tensor(tr_tags)
val_tags = torch.tensor(val_tags)
tr_masks = torch.tensor(tr_masks)
val_masks = torch.tensor(val_masks)


train_data = TensorDataset(tr_inputs, tr_masks, tr_tags)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=bs)

valid_data = TensorDataset(val_inputs, val_masks, val_tags)
valid_sampler = SequentialSampler(valid_data)
valid_dataloader = DataLoader(valid_data, sampler=valid_sampler, batch_size=bs)


# Setup the Bert model for finetuning
model = BertForTokenClassification.from_pretrained(
    pretrained_model,
    num_labels=len(tag2idx),
    output_attentions = False,
    output_hidden_states = False
)

model.cuda();

FULL_FINETUNING = True
if FULL_FINETUNING:
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'gamma', 'beta']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
         'weight_decay_rate': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
         'weight_decay_rate': 0.0}
    ]
else:
    param_optimizer = list(model.classifier.named_parameters())
    optimizer_grouped_parameters = [{"params": [p for n, p in param_optimizer]}]

optimizer = AdamW(
    optimizer_grouped_parameters,
    lr=learning_rate,
    eps=epsilon,
    weight_decay=weight_decay
)

max_grad_norm = 1.0

# Total number of training steps is number of batches * number of epochs.
total_steps = len(train_dataloader) * epochs

# Create the learning rate scheduler.
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps
)

# Fit BERT for named entity recognition
## Store the average loss after each epoch so we can plot them.
loss_values, validation_loss_values, F1_score_values, accuracy_values, F1_per_class = [], [], [], [], []
best_F1sc, best_epoch = 0, 0
for _ in trange(epochs, desc="Epoch"):
    # ========================================
    #               Training
    # ========================================
    # Perform one full pass over the training set.

    # Put the model into training mode.
    model.train()
    # Reset the total loss for this epoch.
    total_loss = 0

    # Training loop
    for step, batch in enumerate(train_dataloader):
        # add batch to gpu
        batch = tuple(t.to(device) for t in batch)
        b_input_ids, b_input_mask, b_labels = batch
        b_labels = b_labels.to(torch.int64)
        # Always clear any previously calculated gradients before performing a backward pass.
        model.zero_grad()
        # forward pass
        # This will return the loss (rather than the model output)
        # because we have provided the `labels`.
        outputs = model(b_input_ids, token_type_ids=None,
                        attention_mask=b_input_mask, labels=b_labels)
        # get the loss
        loss = outputs[0]
        # Perform a backward pass to calculate the gradients.
        loss.backward()
        # track train loss
        total_loss += loss.item()
        # Clip the norm of the gradient
        # This is to help prevent the "exploding gradients" problem.
        torch.nn.utils.clip_grad_norm_(parameters=model.parameters(), max_norm=max_grad_norm)
        # update parameters
        optimizer.step()
        # Update the learning rate.
        scheduler.step()

    # Calculate the average loss over the training data.
    avg_train_loss = total_loss / len(train_dataloader)
    print("Average train loss: {}".format(avg_train_loss))

    # Store the loss value for plotting the learning curve.
    loss_values.append(avg_train_loss)


    # ========================================
    #               Validation
    # ========================================
    # After the completion of each training epoch, measure our performance on
    # our validation set.

    # Put the model into evaluation mode
    model.eval()
    # Reset the validation loss for this epoch.
    eval_loss, eval_accuracy = 0, 0
    nb_eval_steps, nb_eval_examples = 0, 0
    predictions , true_labels = [], []
    for batch in valid_dataloader:
        batch = tuple(t.to(device) for t in batch)
        b_input_ids, b_input_mask, b_labels = batch
        b_labels = b_labels.to(torch.int64)

        # Telling the model not to compute or store gradients,
        # saving memory and speeding up validation
        with torch.no_grad():
            # Forward pass, calculate logit predictions.
            # This will return the logits rather than the loss because we have not provided labels.
            outputs = model(b_input_ids, token_type_ids=None,
                            attention_mask=b_input_mask, labels=b_labels)
        # Move logits and labels to CPU
        logits = outputs[1].detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()

        # Calculate the accuracy for this batch of test sentences.
        eval_loss += outputs[0].mean().item()
        predictions.extend([list(p) for p in np.argmax(logits, axis=2)])
        true_labels.extend(label_ids)

    eval_loss = eval_loss / len(valid_dataloader)
    validation_loss_values.append(eval_loss)
    print("Validation loss: {}".format(eval_loss))
    pred_tags = [tag_values[p_i] for p, l in zip(predictions, true_labels)
                                 for p_i, l_i in zip(p, l) if tag_values[l_i] != "PAD"]
    valid_tags = [tag_values[l_i] for l in true_labels
                                  for l_i in l if tag_values[l_i] != "PAD"]
    print("Validation Accuracy: {}".format(accuracy_score(pred_tags, valid_tags)))
    # print("Validation F1-Score: {}".format(f1_score([pred_tags], [valid_tags])))
    # F1_score_values.append(f1_score([pred_tags], [valid_tags]))
    f1_scores_perclass = f1sc(y_true=valid_tags,y_pred=pred_tags, average=None, labels=unique_labels)
    f1_weighted_mean = f1sc(y_true=valid_tags,y_pred=pred_tags, average='weighted', labels=unique_labels)
    F1_per_class.append(f1_scores_perclass)
    F1_score_values.append(f1_weighted_mean)
    print("Validation F1-Score: {}".format(f1_weighted_mean))
    f1_scores_with_labels = {label: score for label, score in zip(unique_labels, f1_scores_perclass)}
    print(f1_scores_with_labels)
    accuracy_values.append(accuracy_score(pred_tags, valid_tags))
    print()

    # save model if better than former versions
    if f1_weighted_mean > best_F1sc:
        best_model = model
        best_epoch = _
        best_F1sc = f1_weighted_mean


# Save the best model and tokenizer as well as tag values with it
best_model.tokenizer = tokenizer
best_model.tag_values = tag_values
best_F1sc = str(round(best_F1sc,2)).replace(".","_")

output_model = ('D:/PhD EXPANSE/Written Paper/02- Behavioural Model paper/BERT_NER_epoch' + str(best_epoch) +'_wF1_' + best_F1sc + '.pickle')
pickle.dump(best_model, open(output_model, 'wb'))


# Visualize the training loss
plt = PlotLearningCurve(unique_labels, F1_per_class,F1_score_values, loss_values, validation_loss_values, accuracy_values)
plt.savefig("D:/PhD EXPANSE/Written Paper/02- Behavioural Model paper/ModelLearningCurve_finalNEW_bs" + str(
        bs) + "_ep" + str(epochs) + "_lr" + str(learning_rate) + "_art" + str(nr_articles_labeled) + ".png",dpi=350)
plt.show()

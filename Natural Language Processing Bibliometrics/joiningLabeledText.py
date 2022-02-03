import os
import pandas as pd
import numpy as np
import re

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
data = pd.read_csv("manually_labeled/labeled_articles_joined_IOB.csv", encoding="latin1").fillna("O")

sentence_endings = data[data['Word']=='.'].index.values
print(sentence_endings)

last_ending=-1
for count, value in enumerate(sentence_endings):
    data['Sentence #'].iloc[last_ending+1:value+1] = ("Sentence: " + str(count))
    last_ending = value

data['word_id'] = list(data.index)
print(data)
csv = os.path.join(os.getcwd(), ("manually_labeled/labeled_articles_joined_IOB.csv"))
data.to_csv(csv, index=False)
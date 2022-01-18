import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import re
import nltk
nltk.download('averaged_perceptron_tagger')


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "xml_extractedtxt"))

print(listOfFiles)

for file in listOfFiles:
    txt_file = open(os.path.join(os.getcwd(), ("xml_extractedtxt/" + file)), 'r').read()
    txt_file = txt_file.replace(", ", " , ")
    messy_words = txt_file.split(" ")
    sentences = txt_file.split(". ")
    word_id = list(range(1, (len(messy_words) + len(sentences))))
    text_df = pd.DataFrame(data=word_id, columns=["word_id"])
    text_df['Sentence #'] = ""
    text_df['Word'] = ""
    print(text_df)
    index = -1

    ## hierarchical sentence, word restructuring
    for count, value in enumerate(sentences):
        print(count)
        words = value.strip().split(" ")
        print(len(words))
        text_df['Sentence #'].iloc[(index + 1):(index + len(words) + 2)] = ("Sentence: " + str(count))
        text_df['Word'].iloc[(index + 1):(index + 1 + len(words))] = words
        text_df['Word'].iloc[(index + len(words) + 1)] = "."
        print(text_df[['Sentence #', 'word']].iloc[(index + 1):(index + 3 + len(words))])
        index = index + len(words) + 1
    text_df = text_df.iloc[0:index]

    ## part-of-speech (POS) tagging
    ## Part - of - speech(POS) tagging is a natural language processing task which consists in labelling words in context
    ## with their grammatical category, such as noun, verb, preposition
    # text_df["POS"] = nltk.pos_tag( text_df['Word'])
    POS = list(nltk.pos_tag(text_df['Word']))
    POS = pd.DataFrame(data= POS, columns= ["Word", "POS_tag"])
    print(POS.iloc[0:30])
    text_df['POS'] = POS["POS_tag"]
    text_df['Tag'] = "O"

    csv = os.path.join(os.getcwd(), (file.replace(".txt", "") + ".csv"))
    text_df.to_csv(csv, index=False)

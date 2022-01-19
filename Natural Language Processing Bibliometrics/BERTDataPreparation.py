import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import re
import nltk
nltk.download('averaged_perceptron_tagger')


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
# listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "xml_extractedtxt"))
listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "txt"))

print(listOfFiles)

for file in listOfFiles:
    print(file)
    # txt_file = open(os.path.join(os.getcwd(), ("xml_extractedtxt/" + file)), 'r').read()
    txt_file = open(os.path.join(os.getcwd(), ("txt/" + file)), 'r').read()
    txt_file = txt_file.replace(", ", " , ")
    messy_words = txt_file.split(" ")
    sentences = txt_file.split(". ")
    def condition(x): return len(x.split(" ")) > 490
    toolongsentence = [idx for idx, element in enumerate(sentences) if condition(element)]
    print(toolongsentence)
    print("nr sentences before: ",  len(sentences))
    added_indxs = 0
    for longsentence in toolongsentence:
        wordsinsentence = sentences[longsentence].split(" ")
        i = 490
        sentences[longsentence + added_indxs]= " ".join(wordsinsentence[0:490])
        while i + 490 < len(wordsinsentence):
            sentences.insert(longsentence+1+added_indxs, " ".join(wordsinsentence[i+1:i+490]))
            i += 490
            added_indxs += 1
        sentences.insert(longsentence+1+added_indxs, " ".join(wordsinsentence[i+1:i+len(wordsinsentence)-1]))
        added_indxs += 1
    print("nr sentences after: " , len(sentences))
    word_id = list(range(1, (len(messy_words) + (len(sentences)*2))))
    text_df = pd.DataFrame(data=word_id, columns=["word_id"])
    text_df['Sentence #'] = ""
    text_df['Word'] = ""
    # print(text_df)
    index = -1

    ## hierarchical sentence, word restructuring
    for count, value in enumerate(sentences):
        # print(count)
        words = value.strip().split(" ")
        words = list(filter(None, words))
        # print(len(words))
        text_df['Sentence #'].iloc[(index + 1):(index + len(words) + 2)] = ("Sentence: " + str(count))
        text_df['Word'].iloc[(index + 1):(index + 1 + len(words))] = words
        text_df['Word'].iloc[(index + len(words) + 1)] = "."
        # print(text_df[['Sentence #', 'Word']].iloc[(index + 1):(index + 3 + len(words))])
        index = index + len(words) + 1
    text_df = text_df.iloc[0:index]

    ## part-of-speech (POS) tagging
    ## Part - of - speech(POS) tagging is a natural language processing task which consists in labelling words in context
    ## with their grammatical category, such as noun, verb, preposition
    # text_df["POS"] = nltk.pos_tag( text_df['Word'])
    POS = list(nltk.pos_tag(text_df['Word']))
    POS = pd.DataFrame(data= POS, columns= ["Word", "POS_tag"])
    # print(POS.iloc[0:30])
    text_df['POS'] = POS["POS_tag"]
    text_df['Tag'] = "O"

    # csv = os.path.join(os.getcwd(),  ("xml_csvs/" + (file.replace(".txt", "") + ".csv")))
    csv = os.path.join(os.getcwd(), ("pdftxt_csvs/" + (file.replace(".txt", "") + ".csv")))
    text_df.to_csv(csv, index=False)

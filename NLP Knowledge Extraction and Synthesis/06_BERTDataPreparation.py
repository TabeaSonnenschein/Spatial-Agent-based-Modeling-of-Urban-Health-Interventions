import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import re
import nltk
# nltk.download('averaged_perceptron_tagger')


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")

# folder_orig, folder_dest = "txtclean", "pdftxt_csvs"
folder_orig, folder_dest = "xml_extractedtxt", "xml_csvs"
max_words_in_sentence = 100

listOfFiles = os.listdir(path=os.path.join(os.getcwd(), folder_orig))
print(listOfFiles)

for file in listOfFiles:
    print(file)
    txt_file = open(os.path.join(os.getcwd(), (folder_orig + "/" + file)), 'r').read().encode('ascii', 'ignore').decode()
    txt_file = txt_file.replace(", ", " , ")
    messy_words = txt_file.split(" ")
    sentences = txt_file.split(". ")
    def condition(x): return len(x.split(" ")) > max_words_in_sentence
    toolongsentence = [idx for idx, element in enumerate(sentences) if condition(element)]
    print(toolongsentence)
    print("nr sentences before: ",  len(sentences))
    added_indxs = 0
    for longsentence in toolongsentence:
        wordsinsentence = sentences[longsentence].split(" ")
        i = max_words_in_sentence
        sentences[longsentence + added_indxs]= " ".join(wordsinsentence[0:max_words_in_sentence])
        while i + max_words_in_sentence < len(wordsinsentence):
            sentences.insert(longsentence+1+added_indxs, " ".join(wordsinsentence[i+1:i+max_words_in_sentence]))
            i += max_words_in_sentence
            added_indxs += 1
        sentences.insert(longsentence+1+added_indxs, " ".join(wordsinsentence[i+1:i+len(wordsinsentence)-1]))
        added_indxs += 1
    print("nr sentences after: " , len(sentences))
    word_id = list(range(1, (len(messy_words) + (len(sentences)*2))))
    text_df = pd.DataFrame(data=word_id, columns=["word_id"])
    text_df['Sentence #'] = ""
    text_df['Word'] = ""
    index = -1

    ## hierarchical sentence, word restructuring
    for count, value in enumerate(sentences):
        words = value.strip().split(" ")
        words = list(filter(None, words))
        text_df['Sentence #'].iloc[(index + 1):(index + len(words) + 2)] = ("Sentence: " + str(count))
        text_df['Word'].iloc[(index + 1):(index + 1 + len(words))] = words
        text_df['Word'].iloc[(index + len(words) + 1)] = "."
        index = index + len(words) + 1
    text_df = text_df.iloc[0:index]

    ## part-of-speech (POS) tagging: labelling words in context with their grammatical category
    POS = list(nltk.pos_tag(text_df['Word']))
    POS = pd.DataFrame(data= POS, columns= ["Word", "POS_tag"])
    text_df['POS'] = POS["POS_tag"]
    text_df['Tag'] = "O"

    csv = os.path.join(os.getcwd(), (folder_dest + "/" + (file.replace(".txt", "") + ".csv")))
    text_df.to_csv(csv, index=False)

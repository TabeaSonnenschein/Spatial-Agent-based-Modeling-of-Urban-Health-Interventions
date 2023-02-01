import os
import pandas as pd
import nltk
pd.options.mode.chained_assignment = None  # default='warn'
## when not having downloaded this POS tagger yet, then uncomment
# nltk.download('averaged_perceptron_tagger')

## This script transforms the fluent text data into a hierarchical dataframe of sentences and words.
## It moreover applies a Part of speech tagger and ensures sentences do not contain more than a max number of words.
## The output table will be directly readable by the BERT model.

## Functions
def addPOSTag(df):
    """ This function adds POS Tags to a dataframe of words using the nltk library.
       Part-of-speech (POS) tagging = labelling words in context with their grammatical category."""
    POS = list(nltk.pos_tag(df['Word']))
    POS = pd.DataFrame(data= POS, columns= ["Word", "POS_tag"])
    df['POS'] = POS["POS_tag"]
    return df

def structureWordsSentencesIntoDf(wordlist, sentencelist):
    """Hierarchical sentence, word restructuring"""
    word_id = list(range(1, (len(wordlist) + (len(sentencelist) * 2))))
    df = pd.DataFrame(data=word_id, columns=["word_id"])
    df['Sentence #'] = ""
    df['Word'] = ""
    index = -1
    for count, value in enumerate(sentencelist):
        words = value.strip().split(" ")
        words = list(filter(None, words))
        df['Sentence #'].iloc[(index + 1):(index + len(words) + 2)] = ("Sentence: " + str(count))
        df['Word'].iloc[(index + 1):(index + 1 + len(words))] = words
        df['Word'].iloc[(index + len(words) + 1)] = "."
        index = index + len(words) + 1
    df = df.iloc[0:index]
    return df


def LengthCondition(x, max_words_in_sentence):
    """Checks whether sentence has words more than the max words parameter."""
    return len(x.split(" ")) > max_words_in_sentence

def SplitTooLongSentence(sentences):
    """Splits sentences when they are too long."""
    toolongsentence = [idx for idx, element in enumerate(sentences) if LengthCondition(element, max_words_in_sentence)]
    print(toolongsentence)
    print("nr sentences before: ", len(sentences))
    added_indxs = 0
    for longsentence in toolongsentence:
        wordsinsentence = sentences[longsentence].split(" ")
        i = max_words_in_sentence
        sentences[longsentence + added_indxs] = " ".join(wordsinsentence[0:max_words_in_sentence])
        while i + max_words_in_sentence < len(wordsinsentence):
            sentences.insert(longsentence + 1 + added_indxs, " ".join(wordsinsentence[i + 1:i + max_words_in_sentence]))
            i += max_words_in_sentence
            added_indxs += 1
        sentences.insert(longsentence + 1 + added_indxs, " ".join(wordsinsentence[i + 1:i + len(wordsinsentence) - 1]))
        added_indxs += 1
    print("nr sentences after: ", len(sentences))
    return sentences


## Execution
# Read list of files
os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
folder_orig, folder_dest = "txtclean", "pdftxt_csvs"
# folder_orig, folder_dest = "xml_extractedtxt", "xml_csvs"
listOfFiles = os.listdir(path=os.path.join(os.getcwd(), folder_orig))

# set parameter for maximum number of words in sentence
# BERT can only deal with a maximum number of words
max_words_in_sentence=100

# Apply algorithms
for file in listOfFiles:
    print(file)
    txt_file = open(os.path.join(os.getcwd(), (folder_orig + "/" + file)), 'r').read().encode('ascii', 'ignore').decode()
    txt_file = txt_file.replace(", ", " , ")
    messy_words = txt_file.split(" ")
    sentences = txt_file.split(". ")

    sentences = SplitTooLongSentence(sentences)
    text_df = structureWordsSentencesIntoDf(wordlist = messy_words, sentencelist = sentences)
    text_df = addPOSTag(text_df)
    text_df['Tag'] = "O"

    # write data
    csv = os.path.join(os.getcwd(), (folder_dest + "/" + (file.replace(".txt", "") + ".csv")))
    text_df.to_csv(csv, index=False)

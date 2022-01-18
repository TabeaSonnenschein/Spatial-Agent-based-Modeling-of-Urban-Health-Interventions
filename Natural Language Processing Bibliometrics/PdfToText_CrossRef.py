import string

import PyPDF2
import os
import pandas as pd
import numpy as np
import pikepdf
import wordninja
import re
from transformers import BertTokenizer
from math import log

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/pdf')
print(listOfFiles)

# words = open("words.txt").read().split()
#
# listOfWordFiles = os.listdir(path=os.path.join(os.getcwd(), "xml_csvs"))
# for file in listOfWordFiles:
#     word_data = pd.read_csv(os.path.join(os.getcwd(), ("xml_csvs/" + file)), encoding="latin1")
#     words.extend(word_data["Word"].replace("(", ""). replace(")", ""))
# words = list(filter(None, words))
#
# words_clean = []
# for ele in words:
#     try:
#         float(ele)
#     except ValueError:
#         words_clean.append(ele)
#
# wordcost = dict((k, log(i+1)*log(len(words_clean))) for i,k in enumerate(words_clean))
# maxword = max(len(x) for x in words_clean)
# print(wordcost)
#
#
# def infer_spaces(s):
#     def best_match(i):
#         candidates = enumerate(reversed(cost[max(0,i-maxword):i]))
#         return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)
#     cost = [0]
#     for i in range(1, len(s)+1):
#         c,k = best_match(i)
#         cost.append(c)
#     out=[]
#     i = len(s)
#     while i>0:
#         c,k = best_match(i)
#         assert c == cost[i]
#         out.append(s[i-k:i])
#         i -= k
#
#     return " ".join(reversed(out))



for file in listOfFiles:
    try:
        pdfreader = PyPDF2.PdfFileReader(open(os.path.join(os.getcwd(), ("pdf/" + file)), "rb"))
    except PyPDF2.utils.PdfReadError:
        print("invalid PDF file")
    else:
        pass
        x = pdfreader.numPages
        print(str(x) + " Number of pages")
        for i in range(0, x, 1):
            print('page ' + str(i))
            pageobj = pdfreader.getPage(i)
            text = pageobj.extractText()
            text = text.encode("ascii", "replace").decode()
            replacements = [("igni?can", "ignifican"), ("n?uen", "nfluen"), ("denti?e", "dentifie"), ("?rst", "first"),
                            ("ci?cation", "cification"), ("raf?c", "raffic"), ("f?cien", "fficien"), ("peci?c", "pecific"),
                            ("i?e", "ifie"), ("?nanc", "financ"), ("?nish", "finish"), ("?ve", "five"), ("bene?t", "benefit"),
                            ("?nd", "find"), ("de?n", "defin"), ("of?c", "offic"), ("?n", "fin"), ("re?ect", "reflect"), ("on?den", "onfiden"),
                            ("?ts", "fits"), ("?tted", "fitted"), ("goodnessof?t","goodnessoffit"), ("?x", "fix"), ("con?rm", "confirm"),
                            ("di?cat", "dificat"), ("if?cult", "ifficult"), ("?ed", "fied"), (" ?t ", " fit "), ("model?t", "modelfit"), ("?tness", "fitness"),
                            ("?es", "fies"), ("n?ict", "nflict"), ("e?cie", "eficien"), ("f?y", "fly"), ("?gur", "figur"), ("?ow", "flow"), ("good?t", "goodfit"),
                            ("better?t", "betterfit"), ("sacri?c", "sacrific")]
            for a, b in replacements:
                text = text.replace(a, b)
            if len(text.strip()) != 0:
                if len(max(text.split(), key=len)) > 5 and len(re.sub("[^0-9]", "", text)) < len(re.sub("[^a-zA-Z]", "", text)) and len(text.replace(' ',''))/len(text.split()) > 4 and (len(text) - len(re.sub("[^0-9]", "", text)) - len(re.sub("[^a-zA-Z]", "", text))) < len(re.sub("[^a-zA-Z]", "", text)):
                    sentences = text.split(".")
                    filename = str(file).replace(".pdf", "")
                    file1 = open(
                        r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\txt\doi_' + filename + '.txt',
                        "a", errors="replace")
                    for sentence in sentences:
                        if len(sentence.strip()) != 0:
                            # print(infer_spaces(sentence))
                            wordlist = wordninja.split(sentence)
                            stringlength = 0
                            wordidx = 0
                            for count, value in enumerate(sentence.strip().replace("\n", "")):
                                if value in str("!#$%&'()*+, -./:;<=>?@[\]^_`{|}~"):
                                    # print("count: " + str(count) + " , value: " + value)
                                    while stringlength < (count) and wordidx <= len(wordlist):
                                        stringlength = len("".join(wordlist[0:wordidx+1]))
                                        # print(wordlist[0:wordidx+1])
                                        print(count, value, stringlength, wordidx)
                                        wordidx += 1
                                    if stringlength == count:
                                        wordlist.insert(wordidx, value)
                                    elif stringlength > (count):
                                        wordlist.insert(wordidx-1, value)
                                    if value == "?":
                                        print(sentence)
                            # print((" ".join(wordlist)) + ". ")
                            file1.writelines((" ".join(wordlist)) + ". ")
                else:
                    print(str(file) + " has only words shorter than 5")
                    print(text)
            else:
                print(str(file) + " is an empty file")


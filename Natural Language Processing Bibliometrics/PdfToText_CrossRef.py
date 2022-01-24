import string

import PyPDF2
import os
import pandas as pd
import numpy as np
import pikepdf
import wordninja
import re
from math import log

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/pdf')
print(listOfFiles)

full_abbr = []
full_fullnames =[]
full_doitracking = []

for file in listOfFiles:
    try:
        pdfreader = PyPDF2.PdfFileReader(open(os.path.join(os.getcwd(), ("pdf/" + file)), "rb"))
    except PyPDF2.utils.PdfReadError:
        print("invalid PDF file")
    else:
        pass
        x = pdfreader.numPages
        print(str(x) + " Number of pages")
        abbreviations = []
        fullnames = []
        doi_tracking = []
        for i in range(0, x, 1):
            # print('page ' + str(i))
            pageobj = pdfreader.getPage(i)
            text = pageobj.extractText()
            text = text.encode("ascii", "replace").decode()
            replacements = [("igni?can", "ignifican"), ("n?uen", "nfluen"), ("denti?e", "dentifie"), ("?rst", "first"),
                            ("ci?cation", "cification"), ("raf?c", "raffic"), ("f?cien", "fficien"), ("peci?c", "pecific"),
                            ("i?e", "ifie"), ("?nanc", "financ"), ("?nish", "finish"), ("?ve", "five"), ("bene?t", "benefit"), ("e?ect", "effect"),
                            ("?nd", "find"), ("de?n", "defin"), ("of?c", "offic"), ("?n", "fin"), ("re?ect", "reflect"), ("on?den", "onfiden"),
                            ("?ts", "fits"), ("?tted", "fitted"), ("goodnessof?t","goodnessoffit"), ("?x", "fix"), ("con?rm", "confirm"),
                            ("di?cat", "dificat"), ("if?cult", "ifficult"), ("?ed", "fied"), (" ?t ", " fit "), ("model?t", "modelfit"), ("?tness", "fitness"),
                            ("?es", "fies"), ("n?ict", "nflict"), ("e?cie", "eficien"), ("f?y", "fly"), ("?gur", "figur"), ("?ow", "flow"), ("good?t", "goodfit"),
                            ("better?t", "betterfit"), ("sacri?c", "sacrific"), ("-", ""), ("pro?le", "profile"), ("\n", ""), ("ful?l", "fulfill"), ("?eld", "field")]
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
                            if("(" and ")" in sentence):
                                # print(sentence)
                                openbrackets = sentence.find("(")
                                closebrackets = sentence.find(")")
                                if sentence[openbrackets+1:closebrackets].isupper() and sentence[openbrackets+1:closebrackets].isalpha() and (len(sentence[openbrackets+1:closebrackets])>1):
                                    abbr = sentence[openbrackets+1:closebrackets]
                                    abbreviationlen = len(abbr)
                                    wordsbefore = wordninja.split(sentence[:openbrackets])
                                    wordsbefore = wordsbefore[len(wordsbefore)-abbreviationlen-3:]
                                    possible_fullnames = []
                                    if len(abbr) < 2:
                                        for count, value in enumerate(wordsbefore[:len(wordsbefore) - 2]):
                                            if value[0].upper() == abbr[0] and (
                                                    wordsbefore[count + 1][0].upper() == abbr[1] or
                                                    wordsbefore[count + 2][0].upper() == abbr[1]):
                                                fullname = " ".join(wordsbefore[count:])
                                                possible_fullnames.append(fullname)
                                    else:
                                        for count, value in enumerate(wordsbefore[:len(wordsbefore) - 1]):
                                            if value[0].upper() == abbr[0] and wordsbefore[count + 1][0].upper() == \
                                                    abbr[1]:
                                                fullname = " ".join(wordsbefore[count:])
                                                possible_fullnames.append(fullname)
                                    if(possible_fullnames):
                                        fullnames.append(min(possible_fullnames, key=len))
                                        abbreviations.append(abbr)
                                        doi_tracking.append(file)
                                        print(abbreviations[-1])
                                        print(fullnames[-1])
                                        sentence = "".join([sentence[:openbrackets], sentence[closebrackets+1:]])
                                        print()

                            if bool(abbreviations):
                                order = list(pd.Series(abbreviations).str.len().sort_values().index.values)
                                print(abbreviations, order)
                                for index in range(len(abbreviations) - 1, -1, -1):
                                    sentence = sentence.replace(abbreviations[order.index(index)],
                                                                        fullnames[order.index(index)])

                            wordlist = wordninja.split(sentence)

                            stringlength = 0
                            wordidx = 0
                            for count, value in enumerate(sentence.strip().replace("\n", "")):
                                if value in str("!#$%&'()*+, -./:;<=>?@[\]^_`{|}~"):
                                    # print("count: " + str(count) + " , value: " + value)
                                    while stringlength < (count) and wordidx <= len(wordlist):
                                        stringlength = len("".join(wordlist[0:wordidx+1]))
                                        # print(wordlist[0:wordidx+1])
                                        # print(count, value, stringlength, wordidx)
                                        wordidx += 1
                                    if stringlength == count:
                                        wordlist.insert(wordidx, value)
                                    elif stringlength > (count):
                                        wordlist.insert(wordidx-1, value)
                                    # if value == "?":
                                    #     print(sentence)

                            clean_sentence = (" ".join(wordlist)) + ". "
                            finalsliff = [("en v iron mental", "environmental"), ("car poole r", "carpooler"), ("sign i cant ly", "significantly"),
                                          ("in u en ce", "influence"), ("modi fic a t ion", "modification"), ("di e ren", "differen"), ("die ren", "differen"),
                                          ("di cult", "difficult"), (" n ding", " finding"), ("e ect size", "effect size"), ("eec t size", "effect size"), ("coe cie nt", "coefficient"),
                                          ("tra c", "traffic"),("Tra c", "Traffic"),("in s uci ent", "insufficient"), ("elastic i ties", "elasticities"), ("sign i ? cant ly", "significantly"),
                                          ("i den tied", "identified"), (" lter", " filter"), (" ? s ", "'s "), ("lastic i ties", "lasticities"),  (" ? t ","'t ")]
                            for a, b in finalsliff:
                                clean_sentence = clean_sentence.replace(a, b).strip()
                                fullnames = [name.replace(a, b) for name in fullnames]
                            # print(clean_sentence)
                            file1.writelines(clean_sentence + " ")
                else:
                    print(str(file) + " has only words shorter than 5")
                    # print(text)

            else:
                print(str(file) + " is an empty file")
        full_abbr.extend(abbreviations)
        full_fullnames.extend(fullnames)
        full_doitracking.extend(doi_tracking)



abbreviation_def_df = pd.DataFrame(
    {'doi': full_doitracking,
     'abbrev': full_abbr,
     'fullname': full_fullnames
    })

abbreviation_def_df.to_csv("C:/Users/Tabea/Documents/PhD EXPANSE/Written Paper/02- Behavioural Model paper/abbreviation_replacements_pdftxt.csv", index=False)
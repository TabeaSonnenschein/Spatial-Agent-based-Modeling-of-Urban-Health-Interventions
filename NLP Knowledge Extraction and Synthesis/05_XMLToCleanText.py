import os
import pandas as pd
import re

## This script extracts the text from XML documents and identifies as well as substitutes abbreviations
## with their full names. The result will be fluent text that can be used for Natural Language Processing.

## Functions
def extractMaiTextbody(file):
    """This funcion extracts the text from xml documents that are in between the "<body" and </body> params."""
    file = file[int([m.start() for m in re.finditer('<body', file)][0]):int([m.start() for m in re.finditer('</body>', file)][0])]
    return file

def substituteXMLparams(file):
    """This function takes a text including XML params and
       transforms the params (e.g. <ce:label>) into fluent natural language text."""
    file = file.replace("</ce:section-title>", ". ")
    labelnr_starts = [m.start() for m in re.finditer('<ce:label>', file)]
    for times in range(0, len(labelnr_starts)):
        labelnr_starts = [m.start() for m in re.finditer('<ce:label>', file)]
        labelnr_ends = [m.start() for m in re.finditer('</ce:label>', file)]
        file = file[:labelnr_starts[0]] + file[(labelnr_ends[0] + 11):]

    label_starts = [m.start() for m in re.finditer('<', xml_file)]
    label_ends = [m.start() for m in re.finditer('>', xml_file)]
    label_starts.append(label_ends[-1])
    fulltext = ""
    for count, value in enumerate(label_ends):
        fulltext += xml_file[(value+1):label_starts[count+1]].replace("\n", "").strip() + " "
    return fulltext

def FindAbbrev(sentence):
    """Identifies Abbreviation based on Syntax."""
    if len(sentence.strip()) != 0:
        if ("(" and ")" in sentence):
            open_brackets = [m.start() for m in re.finditer("[(]", sentence)]
            close_brackets = [m.start() for m in re.finditer("[)]", sentence)]
            min_length = min(len(open_brackets), len(close_brackets))
            if min_length > 0:
                for abbr_indx in range(0, min_length):
                    if sentence[open_brackets[abbr_indx] + 1:close_brackets[abbr_indx]].replace(" ", "").isupper() or (
                            sentence[open_brackets[abbr_indx] + 1:(close_brackets[abbr_indx] - 1)].replace(" ", "").isupper() and
                            sentence[(close_brackets[abbr_indx] - 1):close_brackets[abbr_indx]] == "s"):
                        if sentence[open_brackets[abbr_indx] + 1:close_brackets[abbr_indx]].replace(" ", "").isalpha() and (
                                len(sentence[open_brackets[abbr_indx] + 1:close_brackets[abbr_indx]]) > 1):
                            abbr = sentence[open_brackets[abbr_indx]+1:close_brackets[abbr_indx]].replace(" ","")
                            if sentence[(close_brackets[abbr_indx] - 1):close_brackets[abbr_indx]] == "s":
                                abbreviation_len = len(abbr) -1
                            else:
                                abbreviation_len = len(abbr)
                            words_before = re.split(' |-|\n|\+', sentence[:open_brackets[abbr_indx]].strip())
                            words_before = list(filter(None, words_before))
                            words_before = words_before[len(words_before) - abbreviation_len - 3:]
                            possible_fullnames = []
                            if len(abbr) < 2:
                                for count, value in enumerate(words_before[:len(words_before) - 2]):
                                    if value[0].upper() == abbr[0] and (
                                            words_before[count + 1][0].upper() == abbr[1] or words_before[count + 2][0].upper() ==
                                            abbr[1]):
                                        fullname = " ".join(words_before[count:])
                                        possible_fullnames.append(fullname)
                            else:
                                for count, value in enumerate(words_before[:len(words_before) - 1]):
                                    if value[0].upper() == abbr[0] and words_before[count + 1][0].upper() == abbr[1]:
                                        fullname = " ".join(words_before[count:])
                                        possible_fullnames.append(fullname)
                            if bool(possible_fullnames):
                                final_fullname = min(possible_fullnames, key=len)
                                new_sentence = "".join([sentence[:open_brackets[abbr_indx]], sentence[close_brackets[abbr_indx] + 1:]])
                                return new_sentence, abbr, final_fullname
                            else:
                                return sentence, "", ""
                        else:
                            return sentence, "", ""
                    else:
                        return sentence, "", ""
            else:
                return sentence, "", ""
        else:
            return sentence, "", ""
    else:
        return sentence, "", ""


def FindNReplaceAbbr(textdoc):
    """Replaces the appreviations with the full text counterparts."""
    sentences = textdoc.split(".")
    abbreviations, fullnames = [], []
    new_fulltext = ""
    for sentence in sentences:
        new_sentence, abbr, final_fullname = FindAbbrev(sentence)
        if abbr != "":
            abbreviations.append(abbr)
            fullnames.append(final_fullname)
            sentence = new_sentence
            print(abbr, final_fullname)
        new_fulltext += sentence + ". "
    if bool(abbreviations):
        sorted_abbr = sorted(abbreviations, reverse=True, key=len)
        order = [sorted_abbr.index(x) for x in abbreviations]
        print("order: ", order, "abbrev: ", abbreviations)
        for index in range(0, len(abbreviations)):
            if index in order:
                new_fulltext = new_fulltext.replace(abbreviations[order.index(index)], fullnames[order.index(index)])
    return new_fulltext, abbreviations, fullnames


def fixPunctuation(text):
    """Replaces common abbreviations that are not usually officially introduced in scientific articles
       with full text counterparts. This allows use punctuation to identify sentences (where it starts and ends)."""
    text = text.replace(" %", "%").replace("i. e.", "id est").replace("e. g.", "for example").replace("al. ", "al").replace("AL. ", "al").replace("i.e.", "id est").replace("e.g.", "for example")
    text = text.replace("Fig. ", "Figure ").replace("Tab. ", "Table ").replace("p. ", "p").replace(" vs. ", " versus ").replace("pp.", "pp").replace("Vol.", "Vol").replace("No.", "No").replace("U.S.", "US")
    return text


## Execution
# Reading list of files
os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\xml")
listOfFiles = os.listdir(path='D:/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/xml')
print(listOfFiles)

# Applying algorithms
full_abbr, full_fullnames, full_doitracking = [], [], []
for file in listOfFiles:
    xml_file = open(os.path.join(os.getcwd(),file),'r', encoding="utf-8").read()
    xml_file = extractMaiTextbody(xml_file)
    fulltext = substituteXMLparams(xml_file)
    cleantext, abbreviations, fullnames = FindNReplaceAbbr(fulltext)
    cleantext = fixPunctuation(cleantext)

    # writing text file
    file1 = open(r'D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\xml_extractedtxt\\' + file, "a", errors="replace")
    file1.writelines(cleantext.strip())

    # saving abbreviation data for reproducability
    full_abbr.extend(abbreviations)
    full_fullnames.extend(fullnames)
    full_doitracking.extend([file] * len(abbreviations))


# saving abbreviation data to file
abbreviation_def_df = pd.DataFrame(
    {'doi': full_doitracking,
    'abbrev': full_abbr,
    'fullname': full_fullnames
    })
abbreviation_def_df.to_csv("D:/PhD EXPANSE/Written Paper/02- Behavioural Model paper/abbreviation_replacements_xmltxt.csv", index=False)
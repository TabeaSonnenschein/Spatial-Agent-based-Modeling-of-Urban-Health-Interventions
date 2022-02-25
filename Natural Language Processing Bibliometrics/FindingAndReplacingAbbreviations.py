import os
import pandas as pd
import numpy as np
import re


def FindAbbrev(sentence):
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
    sentences = textdoc.split(".")
    abbreviations = []
    fullnames = []
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



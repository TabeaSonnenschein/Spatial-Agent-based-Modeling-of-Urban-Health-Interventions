import PyPDF2
import os
import pandas as pd
import wordninja
import re

############################################################################################
## This script extracts and prepares the text from PDF documents. The focus are scientific articles.
############################################################################################

## Functions

def tryPdfReader(file):
    """Tried reading the PDF"""
    try:
        pdfreader = PyPDF2.PdfFileReader(open(os.path.join(os.getcwd(), ("pdf/" + file)), "rb"))
    except PyPDF2.utils.PdfReadError:
        print("invalid PDF file")
        pdfreader = []
    else:
        pass
    return pdfreader

def extractEncodeText(pdfreader):
    """Extracts the text from the PDF and encodes it in ASCII."""
    pageobj = pdfreader.getPage(i)
    text = pageobj.extractText()
    text = text.encode("ascii", "replace").decode()
    return text

def addressCommonTextExtractBugs(text):
    """Most relevant cases where it misreads "fi" as "?".
       This function replaces those cases with the correct ones."""
    replacements = [("igni?can", "ignifican"), ("n?uen", "nfluen"), ("denti?e", "dentifie"), ("?rst", "first"),
                    ("ci?cation", "cification"), ("raf?c", "raffic"), ("f?cien", "fficien"), ("peci?c", "pecific"),
                    ("i?e", "ifie"), ("?nanc", "financ"), ("?nish", "finish"), ("?ve", "five"), ("bene?t", "benefit"),
                    ("e?ect", "effect"),("?nd", "find"), ("de?n", "defin"), ("of?c", "offic"), ("?n", "fin"), ("re?ect", "reflect"),
                    ("on?den", "onfiden"),("?ts", "fits"), ("?tted", "fitted"), ("goodnessof?t", "goodnessoffit"), ("?x", "fix"),
                    ("con?rm", "confirm"),("di?cat", "dificat"), ("if?cult", "ifficult"), ("?ed", "fied"), ("aren?t", "aren't"),
                    ("aren ?t", "aren't"), (" ?t ", " fit "), ("model?t", "modelfit"), ("?tness", "fitness"),
                    ("?es", "fies"), ("n?ict", "nflict"), ("e?cie", "eficien"), ("f?y", "fly"), ("?gur", "figur"),
                    ("?ow", "flow"), ("good?t", "goodfit"),("better?t", "betterfit"), ("sacri?c", "sacrific"), ("-", ""), ("pro?le", "profile"), ("\n", ""),
                    ("ful?l", "fulfill"),("?eld", "field"), ("arti?cial", "artificial")]
    for a, b in replacements:
        text = text.replace(a, b)
    return text


def IdentifyAbbreviations(sentence):
    """Identifies Abbreviation based on Syntax."""
    if (("(" in sentence) and ( ")" in sentence)):
        openbrackets = [m.start() for m in re.finditer("[(]", sentence)]
        closebrackets = [m.start() for m in re.finditer("[)]", sentence)]
        min_length = min(len(openbrackets), len(closebrackets))
        for abbr_indx in range(0, min_length):
            if sentence[openbrackets[abbr_indx] + 1:closebrackets[abbr_indx]].replace(" ", "").isupper() or (
                    sentence[openbrackets[abbr_indx] + 1:(closebrackets[abbr_indx] - 1)].replace(" ","").isupper() and sentence[(closebrackets[abbr_indx] - 1):closebrackets[abbr_indx]] == "s"):
                if sentence[openbrackets[abbr_indx] + 1:closebrackets[abbr_indx]].replace(" ", "").isalpha() and (
                        len(sentence[openbrackets[abbr_indx] + 1:closebrackets[abbr_indx]]) > 1):
                    abbr = sentence[openbrackets[abbr_indx] + 1:closebrackets[abbr_indx]].replace(" ", "")
                    if sentence[(closebrackets[abbr_indx] - 1):closebrackets[abbr_indx]] == "s":
                        abbreviationlen = len(abbr) - 1
                    else:
                        abbreviationlen = len(abbr)
                    wordsbefore = wordninja.split(sentence[:openbrackets[abbr_indx]])
                    wordsbefore = wordsbefore[len(wordsbefore) - abbreviationlen - 3:]
                    possible_fullnames = []
                    if len(abbr) > 2:
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
                    if len(possible_fullnames) > 0:
                        fullname =  min(possible_fullnames, key=len)
                    else:
                        fullname = 0
                        # sentence = "".join([sentence[:openbrackets[abbr_indx]], sentence[closebrackets[abbr_indx] + 1:]])
                        print()
                    return fullname, abbr

                else:
                    return 0, 0
            else:
                return 0, 0
    else:
        return 0, 0



def ReplaceAbbrevWithFullName(abbreviations, fullnames, sentence):
    """Replaces any abbreviation with the previously identified fullnames of the document."""
    sorted_abbr = sorted(abbreviations, reverse=True, key=len)
    order = [sorted_abbr.index(x) for x in abbreviations]
    print("order: ", order, "abbrev: ", abbreviations)
    for index in range(0, len(abbreviations)):
        if index in order:
            sentence = sentence.replace(abbreviations[order.index(index)], fullnames[order.index(index)])
    return sentence

def SplittingSentenceStringIntoWords(sentence):
    """Splits Sentences into Words using wordninja."""
    wordlist = wordninja.split(sentence)
    stringlength, wordidx = 0, 0
    for count, value in enumerate(sentence.strip().replace("\n", "")):
        if value in str("!#$%&()*+, -./:;<=>?@[\]^_`{|}~"):
            while stringlength < (count) and wordidx <= len(wordlist):
                stringlength = len("".join(wordlist[0:wordidx + 1]))
                wordidx += 1
            if stringlength == count:
                wordlist.insert(wordidx, value)
            elif stringlength > (count):
                wordlist.insert(wordidx - 1, value)
    return wordlist

finalsliff = [("en v iron mental", "environmental"), ("car poole r", "carpooler"),("sign i cant ly", "significantly"),
                  ("in u en ce", "influence"), ("modi fic a t ion", "modification"), ("di e ren", "differen"),
                  ("die ren", "differen"),("di cult", "difficult"), (" n ding", " finding"), ("e ect size", "effect size"),
                  ("eec t size", "effect size"), ("coe cie nt", "coefficient"),
                  ("tra c", "traffic"), ("Tra c", "Traffic"), ("in s uci ent", "insufficient"),
                  ("elastic i ties", "elasticities"), ("sign i ? cant ly", "significantly"),
                  ("i den tied", "identified"), (" lter", " filter"), (" ? s ", "'s "),
                  ("lastic i ties", "lasticities"), (" ? t ", "'t "), ("in ue nti al", "influential"),
                  ("in u enc e", "influence "), ("ign i can", "ignifican"), ("dent i cation", "dentification"),
                  ("xternal i ties", "xternalities"), ("coe ci ent", "coefficient"), ("ec i cation", "ecification"), ("class i ed", "classifed"),
                  ("a ttt i tude", "attitude"), (" o or ", "floor "), ("gnifican ce", "gnificance"), ("rider ship", "ridership"), (" xter nal", "external"),
                  (" in signific", "  insignific"), ("re ect s", " reflects "), ("re ect ", " reflect"),
                  ("r eec t", "reflect"), ("eec t", "effect"), ("multi no mi al", "multinominal "), (" no mi al", " nominal "), ("spec ic", "specific"),
                  (" un weight", " unweight"), (" rst ", " first "), (" oe rsa ", " offers a "),
                  (" dieren ces ", " differences "), ("Dieren ces", "Differences"), ("rig our", "rigour"),
                  (" nds ", " finds "), ("Eec t", "Effect"), ("re pli c ability", " replicability"),
                  ("de ned", "defined"),(" de ne", " define"), ("uct u at ion", " fluctuation"), ("con rm", "confirm"),
                  (" d is aggregate", " disaggregate"), (" el d ", " field "), (" our is he d ", " flourished "),
                  ("effecti ve", "effective"), (" nite ", " finite "), ("general is able", "generalisable"),
                  ("oe ring", "offering"), ("different ly", "differently"), ("indifferent", "in different"),
                  ("at t it udin al", "attitudinal"), ("systemic al", "systemical"), (" ve ", " five "),
                  ("die ring", "differing"), ("nul lies", "nullifies"), ("operational is ation", "operationalisation"),
                  ("con found", "confound"), ("At t it udin al", "Attitudinal"), ("xe de ect s", "fixed effects"),
                  ("xe de ect", "fixed effect"), (" die r ", " differ "), (" gu re", " Figure"),
                  ("walk ability", "walkability"), ("n dings ", " findings "), ("are nf it", "aren't"),
                  ("non - significant", "insignificant"), ("Non - significant", "Insignificant"),
                  ("quant if i cation", "quantification"), ("streets cape", "streetscape"), ("Walk ability", "Walkability"),
                  ("operational is ed", "operationalised"), ("co variate s ", "covariates "), (" noor ", " no or "),
                  ("s ? ", "s' "),("fac il it at or s ", "facilitators "), ("fac il it at or", "facilitator"),
                  ("hypothesis ed ", "hypothesised "), ("walk able", "walkable"), ("con ? den ce", "confidence"),
                  (" be nets", " benefits"),("Th ending", "The finding"), ("th ending", "the finding"), ("The sending s", "These findings"),
                  ("the sending s", "these findings"), ("specie d ", "specified"), ("conde n ce", "confidence"),
                  (" nal ", " final "),("aside n tied", "as identified"), ("ide n tied", "identified"), ("in ten t", "intent "),
                  ("lassic ation", "lassification"), ("afixed", "a fixed"), ("aggregate deffect", "aggregated effect"),
                  ("ident ies", "identifies"), ("specific ally", "specifically"), (" a ect ", " affect "),
                  (" gur es ", " Figures "), ("s u er", " suffer"), ("con r med", "confirmed"), ("aec ted", "affected"),
                  ("conic ting", "conflicting"), ("rearm", "reaffirm"), ("chau eu ring", "chauffeuring"),
                  (" con text", " context"), ("in ue nti a l", "influential "), ("classic ation", "classification"),
                  ("? ex i bil it y", "flexibility"), ("ident i ? cation", "identification"),
                  ("car pool er", "carpooler"), ("just i ? abl", "justifiabl"), ("class i ? cat", "classificat"),
                  ("M ov ability", "Movability"), ("random is ed", "randomised")]

def AddressCommonWordsplitBugs( clean_sentence, wordreplace_map = finalsliff):
    """Also with the wordsplit function "wordninja", there are some common bugs.
       Here I tried addressing the most common ones across the extracted articles."""
    for a, b in wordreplace_map:
        clean_sentence = clean_sentence.replace(a, b).strip()
    return clean_sentence

def AddressCommonWordsplitBugs_list( fullnames, wordreplace_map = finalsliff):
    """Also with the wordsplit function "wordninja", there are some common bugs.
       Here I tried addressing the most common ones across the extracted articles."""
    for a, b in wordreplace_map:
        fullnames = [name.replace(a, b) for name in fullnames]
    return fullnames


## Execution

# Identify the pdf documents that should be extracting by giving direction of folder in which they are contained
os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path='D:/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/pdf')
print(listOfFiles)
textDocFolder = "D:/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/newCrossRef/text/"

# applying extraction and preparation algorithms
full_abbr,full_fullnames, full_doitracking = [], [], []
for file in listOfFiles:
    pdfreader = tryPdfReader(file)
    if pdfreader != []:
        x = pdfreader.numPages
        print(str(x) + " Number of pages")
        abbreviations, fullnames, doi_tracking = [], [], []
        for i in range(0, x, 1):
            text = extractEncodeText(pdfreader)
            text = addressCommonTextExtractBugs(text)
            if len(text.strip()) != 0:
                if len(max(text.split(), key=len)) > 5 and len(re.sub("[^0-9]", "", text)) < len(re.sub("[^a-zA-Z]", "", text)) and \
                        len(text.replace(' ',''))/len(text.split()) > 4 and (len(text) - len(re.sub("[^0-9]", "", text)) - len(re.sub("[^a-zA-Z]", "", text))) < len(re.sub("[^a-zA-Z]", "", text)):
                    sentences = text.split(".")
                    filename = str(file).replace(".pdf", "").replace("doi_", "")
                    file1 = open(os.path.join(textDocFolder +'doi_' + filename + '.txt'), "a", errors="replace")
                    for sentence in sentences:
                        if len(sentence.strip()) != 0:
                            fullname, abbr = IdentifyAbbreviations(str(sentence))
                            if fullname != 0:
                                fullnames.append(fullname)
                                abbreviations.append(abbr)
                                doi_tracking.append(file)
                                print(fullnames)
                            if bool(abbreviations):
                                sentence = ReplaceAbbrevWithFullName(abbreviations, fullnames, str(sentence))
                            wordlist = SplittingSentenceStringIntoWords(str(sentence))
                            clean_sentence = (" ".join(wordlist)) + ". "
                            clean_sentence = AddressCommonWordsplitBugs(clean_sentence)
                            fullnames = AddressCommonWordsplitBugs_list(fullnames)
                            print("cleansentence: ", clean_sentence)
                            file1.writelines(clean_sentence + " ")
                else:
                    print(str(file) + " has only words shorter than 5")
            else:
                print(str(file) + " is an empty file")
        full_abbr.extend(abbreviations)
        full_fullnames.extend(fullnames)
        full_doitracking.extend(doi_tracking)


## writing abbreviation data
abbreviation_def_df = pd.DataFrame(
    {'doi': full_doitracking,
     'abbrev': full_abbr,
     'fullname': full_fullnames
    })

folder= "D:/PhD EXPANSE/Written Paper/02- Behavioural Model paper/"
abbreviation_def_df.to_csv(os.path.join(folder+"abbreviation_replacements_pdftxt.csv"), index=False)
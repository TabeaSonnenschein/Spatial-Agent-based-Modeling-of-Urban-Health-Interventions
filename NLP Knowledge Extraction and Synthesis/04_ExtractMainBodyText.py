# Importing modules
import os
import re

###################################################################################
## This script helps extracting the main body of the scientific articles
## and formats the punctuation and spacing so that it can be used for NLP
###################################################################################

# Functions
def cleanPunctuation(file):
    """This function fixed all punctuation and spacing issues caused by Citation formats, and common abbreviations."""
    file = re.sub(r'(\d+)(\.\s)(\d+)', r'\1.\3', file.strip().replace("  ", " ").replace("  ", " "))
    file = re.sub(r'(\d+)(\. )(\d+)', r'\1.\3', file)
    file = file.replace(" %", "%").replace("i. e.", "id est").replace("e. g.", "for example").replace(" ? s ","'s ").replace(
        "al. ", "al").replace("AL. ", "al").replace("(", " ( ").replace(")", " ) ")
    file = file.replace("Fig. ", "Figure ").replace("Tab. ", "Table ").replace("p. ", "p").replace(" vs. "," versus ").replace(
        "pp.", "pp").replace("Vol.", "Vol").replace("No.", "No").replace("U.S.", "US").replace("U. S.", "US")
    file = re.sub(r'([A-Z]\w*)([\s*])([a-z]+)([\s*])(e[\s*]t[\s*]al)', r'\1\3 et al ', file)
    file = re.sub(r'([1-9]+)(\s\?\s)([1-9]+)', r'\1-\3', file)
    file = re.sub(r'([a-z+]s)(\s\?\s)([a-z+])', r'\1\' \3', file)
    file = re.sub(r'(\?\s)([a-zA-Z\s]+)(\s\?)', r'" \2 "', file)
    file = re.sub(r'([A-Z][a-z]+)([\s]*)([a-z]+)(\sand\s)([A-Z][a-z]+)([\s]*)([a-z]+)([\s,\(]*[0-9][0-9][0-9][0-9])',r'\1\3\4\5\7\8', file)
    file = re.sub(r'([A-Z]\w*)(\s)([a-z]+)(\s)([a-z]+)(\s*)(et al)', r'\1\3\5 et al ', file)
    file = re.sub(r'([A-Z]\w*)(\s)([a-z]+)(\s*)(et al)', r'\1\3 et al ', file)
    file = re.sub(r'([A-Z]\w*)(\s)([a-z]+)([\s,\(]*[0-9][0-9][0-9][0-9])', r'\1\3 \4', file)
    file = re.sub(r'([A-Z]\w*)(\s)([a-z]+)(\s)([a-z]+)([\s,\(]*[0-9][0-9][0-9][0-9])', r'\1\3\5 \6', file)
    file = re.sub(r'([A-Z]\w*)(\s)([a-z]+)(\s)([a-z]+)(\s)([a-z]+)([\s,\(]*[0-9][0-9][0-9][0-9])', r'\1\3\5\7 \8',file)
    file = re.sub(r'([A-Z][a-z]+)(etal)([\s,\(]*[0-9][0-9][0-9][0-9])', r'\1 et al\3', file)
    file = re.sub(r'([A-Z]\w*)(\s)([a-z]+)(e tal)', r'\1\3 et al ', file)
    file = re.sub(r'(et al)([0-9][0-9][0-9][0-9])', r'\1 \2', file)
    file = file.replace("  ", " ")
    return file

def StartFromIntro(file):
    """This function checks whether there is an Introduction section
     and cuts out the content from before, which is usually noise text."""
    intro_start = [m.start() for m in re.finditer('Introduction', file)]
    if bool(intro_start):
        print(intro_start)
        if intro_start[0] < 3000:
            print(file[intro_start[0]:(intro_start[0] + 30)])
            file = file[intro_start[0]: len(file)]
    return file

def CutTextFromReferencesAcknowledgem(file):
    """This function tries to find the beginning of the References or Acknowledgements section
       and then cuts out the text from thereon, since there is no evidence to be expected in these sections."""
    reference_start = [m.start() for m in re.finditer('References', file)]
    acknowledge_start = [m.start() for m in re.finditer('Acknowledgement', file)]
    if bool(reference_start):
        length_ref = len(reference_start)
        print(reference_start)
        print(file[reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
        if reference_start[length_ref - 1] > (len(file) / 2):
            print("passed the check")
            file = file[0: reference_start[length_ref - 1]]
        else:
            if bool(acknowledge_start):
                if reference_start[length_ref - 1] > acknowledge_start[-1]:
                    print("passed the check")
                    file = file[0: reference_start[length_ref - 1]]
    else:
        reference_start = [m.start() for m in re.finditer('Bibliography', file)]
        if bool(reference_start):
            length_ref = len(reference_start)
            print(file[reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
            file = file[0:reference_start[length_ref - 2]]
        else:
            reference_start = [m.start() for m in re.finditer('Acknowledgement', file)]
            if bool(reference_start):
                length_ref = len(reference_start)
                print(file[reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
                file = file[0:reference_start[length_ref - 2]]
    return file

# Execution

# Setting directory and List of files
os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\newCrossRef")
# os.chdir(r"D:\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path=os.path.join(os.getcwd(),"txt"))

# Extracting Main Textbody
for file in listOfFiles:
    print(file)
    file1 = open(os.path.join(os.getcwd(), ("txt/" + file)),'r').read()
    file1 = StartFromIntro(file1)
    file1 = CutTextFromReferencesAcknowledgem(file1)
    file1 = cleanPunctuation(file1)

    # write data
    if len(file1) > 10000:
        file2 = open(os.path.join(os.getcwd(), ('txtclean/' + file.replace("doi_","") + '.txt')),
            "a", errors="replace")
        file2.writelines(file1)


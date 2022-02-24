import os
import pandas as pd
import numpy as np
import re
from FindingAndReplacingAbbreviations import FindNReplaceAbbr, FindAbbrev

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\xml")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/xml')
print(listOfFiles)

full_abbr = []
full_fullnames =[]
full_doitracking = []
for file in listOfFiles:
    xml_file = open(os.path.join(os.getcwd(),file),'r', encoding="utf-8").read()
    # print(xml_file[int([m.start() for m in re.finditer('<body', xml_file)][0]):int([m.start() for m in re.finditer('</body>', xml_file)][0])])
    xml_file = xml_file[int([m.start() for m in re.finditer('<body', xml_file)][0]):int([m.start() for m in re.finditer('</body>', xml_file)][0])]
    xml_file = xml_file.replace("</ce:section-title>", ". ")

    labelnr_starts = [m.start() for m in re.finditer('<ce:label>', xml_file)]
    for times in range(0,len(labelnr_starts)):
        labelnr_starts = [m.start() for m in re.finditer('<ce:label>', xml_file)]
        labelnr_ends = [m.start() for m in re.finditer('</ce:label>', xml_file)]
        xml_file = xml_file[:labelnr_starts[0]] + xml_file[(labelnr_ends[0]+11):]

    label_starts = [m.start() for m in re.finditer('<', xml_file)]
    label_ends = [m.start() for m in re.finditer('>', xml_file)]
    label_starts.append(label_ends[-1])

    file1 = open(
        r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\xml_extractedtxt\\' + file,
        "a", errors="replace")
    fulltext = ""
    for count, value in enumerate(label_ends):
        fulltext += xml_file[(value+1):label_starts[count+1]].replace("\n", "").strip() + " "
    cleantext, abbreviations, fullnames = FindNReplaceAbbr(fulltext)
    cleantext = cleantext.replace(" %", "%").replace("i. e.", "id est").replace("e. g.", "for example").replace("al. ", "al").replace("AL. ", "al").replace("i.e.", "id est").replace("e.g.", "for example")
    cleantext = cleantext.replace("Fig. ", "Figure ").replace("Tab. ", "Table ").replace("p. ", "p").replace(" vs. ", " versus ").replace("pp.", "pp").replace("Vol.", "Vol").replace("No.", "No")
    file1.writelines(cleantext.strip())
    full_abbr.extend(abbreviations)
    full_fullnames.extend(fullnames)
    full_doitracking.extend([file] * len(abbreviations))

abbreviation_def_df = pd.DataFrame(
    {'doi': full_doitracking,
    'abbrev': full_abbr,
    'fullname': full_fullnames
    })

abbreviation_def_df.to_csv(
    "C:/Users/Tabea/Documents/PhD EXPANSE/Written Paper/02- Behavioural Model paper/abbreviation_replacements_xmltxt.csv",
    index=False)
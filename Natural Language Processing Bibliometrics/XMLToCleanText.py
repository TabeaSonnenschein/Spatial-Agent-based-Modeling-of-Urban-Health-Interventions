import os
import pandas as pd
import numpy as np
import re

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\xml")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/xml')
print(listOfFiles)

for file in listOfFiles:
    xml_file = open(os.path.join(os.getcwd(),file),'r', encoding="utf-8").read()
    # print(xml_file[int([m.start() for m in re.finditer('<body', xml_file)][0]):int([m.start() for m in re.finditer('</body>', xml_file)][0])])
    xml_file = xml_file[int([m.start() for m in re.finditer('<body', xml_file)][0]):int([m.start() for m in re.finditer('</body>', xml_file)][0])]
    xml_file = xml_file.replace("</ce:section-title>", ". ")

    labelnr_starts = [m.start() for m in re.finditer('<ce:label>', xml_file)]
    for times in range(0,len(labelnr_starts)):
        labelnr_starts = [m.start() for m in re.finditer('<ce:label>', xml_file)]
        labelnr_ends = [m.start() for m in re.finditer('</ce:label>', xml_file)]
        print(xml_file[labelnr_starts[0]:(labelnr_ends[0]+11)])
        xml_file = xml_file[:labelnr_starts[0]] + xml_file[(labelnr_ends[0]+11):]

    label_starts = [m.start() for m in re.finditer('<', xml_file)]
    label_ends = [m.start() for m in re.finditer('>', xml_file)]
    label_starts.append(label_ends[-1])

    file1 = open(
        r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\xml_extractedtxt\\' + file,
        "a", errors="replace")

    for count, value in enumerate(label_ends):
        file1.writelines(xml_file[(value+1):label_starts[count+1]].replace("\n", "").strip() + " ")



import PyPDF2
import os
import pandas as pd
import numpy as np
import pikepdf
import wordninja
import re
import codecs
import pdfplumber
import pdfminer

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\pdf")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/pdf')
print(listOfFiles)

for file in listOfFiles:
    try:
        pdf = pdfplumber.open(file)
    except pdfminer.pdfparser.PDFSyntaxError:
        print("failed to read")
    else:
        pass
        x = len(pdf.pages)
        print(str(x) + " Number of pages")
        for i in range(0, x, 1):
            print('page ' + str(i))
            pageobj = pdf.pages[i]
            text = pageobj.extract_text()
            if len(text.strip()) != 0:
                if len(max(text.split(), key=len)) > 5 and len(re.sub("[^0-9]", "", text)) < len(re.sub("[^a-zA-Z]", "", text)) and len(text.replace(' ',''))/len(text.split()) > 4 and (len(text) - len(re.sub("[^0-9]", "", text)) - len(re.sub("[^a-zA-Z]", "", text))) < len(re.sub("[^a-zA-Z]", "", text)):
                    sentences = text.split(".")
                    filename = str(file).replace(".pdf", "")
                    file1 = open(
                        r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\txt2\doi_' + filename + '.txt',
                        "a", errors="replace")
                    for sentence in sentences:
                        if len(sentence.strip()) != 0:
                            print((" ".join(wordninja.split(sentence))) + ". ")
                            file1.writelines((" ".join(wordninja.split(sentence))) + ". ")
                else:
                    print(str(file) + " has only words shorter than 5")
                    # print(text)
            else:
                print(str(file) + " is an empty file")

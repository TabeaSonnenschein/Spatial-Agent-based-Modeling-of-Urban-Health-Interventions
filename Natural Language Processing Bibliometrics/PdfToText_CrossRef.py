import PyPDF2
import os
import pandas as pd
import numpy as np
import pikepdf
import wordninja

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
paper_ids = pd.read_csv("ref_ids.csv")
print(paper_ids)

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\pdf")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/pdf')
print(listOfFiles)

for file in listOfFiles:
    try:
        pdfreader = PyPDF2.PdfFileReader(open(file, "rb"))
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
            sentences = text.split(".")
            filename = str(file).replace(".pdf", "")
            file1 = open(
                r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\doi_' + filename + '.txt',
                "a", errors="replace")
            for sentence in sentences:
                print((" ".join(wordninja.split(sentence))) + ". ")
                file1.writelines((" ".join(wordninja.split(sentence))) + ". ")


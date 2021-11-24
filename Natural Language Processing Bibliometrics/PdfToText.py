import PyPDF2
import os
import pandas as pd
import numpy as np
import pikepdf


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
paper_ids = pd.read_csv("ref_ids.csv")
print(paper_ids)

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\search3")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/search3')
print(listOfFiles)

for file in listOfFiles:
    id_index = int(np.where(paper_ids.filter(items=['file_name']) == file)[0])
    id = paper_ids.loc[id_index, "article_id"]
    print(id)
    if str(id) != "nan":
        # text = extract_text(file)
        # print(text)
        try:
            pdfreader = PyPDF2.PdfFileReader(open(file, "rb"))
        except PyPDF2.utils.PdfReadError:
            print("invalid PDF file")
        else:
            pass
        # pdffileobj = pikepdf.Pdf.open(file)
        # pdfreader = PyPDF2.PdfFileReader(pdffileobj)
        x = pdfreader.numPages
        print(str(x) + " Number of pages")
        for i in range(0, x, 1):
            print('page ' + str(i))
            pageobj = pdfreader.getPage(i)
            text = pageobj.extractText()
            file1 = open(r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\search3txt\a_' + id + '.txt', "a", errors="replace")
            file1.writelines(text)

# encoding error
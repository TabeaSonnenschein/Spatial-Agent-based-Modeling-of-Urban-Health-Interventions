import PyPDF2
import os
import pandas as pd
import numpy as np
import pikepdf
import wordninja
import re
import pdfplumber
import pdfminer

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
paper_ids = pd.read_csv("ref_ids.csv")
print(paper_ids)

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\search3")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/search3')
print(listOfFiles)

# invalid_txt = []
# for file in listOfFiles:
#     print(file)
#     id_index = int(np.where(paper_ids.filter(items=['file_name']) == file)[0])
#     id = str(paper_ids.loc[id_index, "doi"]).replace("/", "_")
#     if id == "NA" or id is None or id == "nan":
#         id = str("articleID_" + str(paper_ids.loc[id_index, "article_id"]))
#     try:
#         pdfreader = PyPDF2.PdfFileReader(open(file, "rb"))
#     except PyPDF2.utils.PdfReadError:
#         print("invalid PDF file")
#     else:
#         pass
#         x = pdfreader.numPages
#         print(str(x) + " Number of pages")
#
#         for i in range(0, x, 1):
#             # print('page ' + str(i))
#             pageobj = pdfreader.getPage(i)
#             text = pageobj.extractText()
#             # print("Txt length without spaces: " + str(len(text.replace(' ', ''))))
#             # print("Txt length with spaces: " + str(len(text.split())))
#             if len(text.strip()) != 0:
#                 if len(max(text.split(), key=len)) > 5 and len(re.sub("[^0-9]", "", text)) < len(re.sub("[^a-zA-Z]", "", text)) and len(text.replace(' ',''))/len(text.split()) > 4 and (len(text) - len(re.sub("[^0-9]", "", text)) - len(re.sub("[^a-zA-Z]", "", text))) < len(re.sub("[^a-zA-Z]", "", text)):
#                     sentences = text.split(".")
#                     filename = str(file).replace(".pdf", "")
#                     file1 = open(
#                         r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\search3txt\doi_' + id + '.txt',
#                         "a", errors="replace")
#                     for sentence in sentences:
#                         if len(sentence.strip()) != 0:
#                             # print((" ".join(wordninja.split(sentence))) + ". ")
#                             file1.writelines((" ".join(wordninja.split(sentence))) + ". ")
#                 else:
#                     print(str(file) + " has only words shorter than 5")
#                     print(text)
#             else:
#                 print(str(file) + " is an empty file")
#     # char.isdigit() for char in inputString

for file in listOfFiles:
    print(file)
    id_index = int(np.where(paper_ids.filter(items=['file_name']) == file)[0])
    id = str(paper_ids.loc[id_index, "doi"]).replace("/", "_")
    if id == "NA" or id is None or id == "nan":
        id = str("articleID_" + str(paper_ids.loc[id_index, "article_id"]))
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
            if text:
                if len(text.strip()) != 0:
                    if len(max(text.split(), key=len)) > 5 and len(re.sub("[^0-9]", "", text)) < len(re.sub("[^a-zA-Z]", "", text)) and len(text.replace(' ',''))/len(text.split()) > 4 and (len(text) - len(re.sub("[^0-9]", "", text)) - len(re.sub("[^a-zA-Z]", "", text))) < len(re.sub("[^a-zA-Z]", "", text)):
                        sentences = text.split(".")
                        filename = str(file).replace(".pdf", "")
                        file1 = open(
                            r'C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\search3txt2\doi_' + id + '.txt',
                            "a", errors="replace")
                        for sentence in sentences:
                            if len(sentence.strip()) != 0:
                                print((" ".join(wordninja.split(sentence.strip()))) + ". ")
                                file1.writelines((" ".join(wordninja.split(sentence.strip()))) + ". ")
                    else:
                         print(str(file) + " has only words shorter than 5")
                         # print(text)
                else:
                     print(str(file) + " is an empty file")


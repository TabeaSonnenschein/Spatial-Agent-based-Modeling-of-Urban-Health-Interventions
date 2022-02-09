import nltk
import pandas as pd
import os
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults\manually_labeled")


doc_txt = pd.read_csv(os.path.join(os.getcwd(), ("doi_10.1016_j.jtrangeo.2017.04.004.csv")), encoding="latin1")
POS = list(nltk.pos_tag([str(word) for word in doc_txt['Word']]))
POS = pd.DataFrame(data=POS, columns=["Word", "POS_tag"])
doc_txt['POS'] = POS["POS_tag"]

print(doc_txt.head())
csv = os.path.join(os.getcwd(), ("doi_10.1016_j.jtrangeo.2017.04.004_withPOS.csv"))
doc_txt.to_csv(csv)
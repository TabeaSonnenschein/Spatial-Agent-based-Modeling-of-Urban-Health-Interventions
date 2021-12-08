# Importing modules
import pandas as pd
import os
# Load the regular expression library
import re
import numpy as np

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
text_df = pd.read_csv("ref_data_clean.csv")
print(text_df)

core_folder = r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref"
os.chdir(os.path.join(core_folder, "CrossrefResults"))
# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref")
# os.chdir(r"C:\Dokumente\PhD EXPANSE\Literature\WOSref\CrossrefResults\txt")

listOfFiles = os.listdir(path=os.path.join(os.getcwd(),"txt"))
# listOfFiles = os.listdir(path=os.path.join(os.getcwd(),"search3txt"))
print(listOfFiles)

text_df['DOI_filename'] = 'doi_' + text_df['doi']
text_df['DOI_filename'] = [str(doi).replace("/", "_") for doi in text_df['DOI_filename']]
text_df['fulltext'] = ''
text_df['complete'] = 'empty'
print(text_df.head())

for textdoc in listOfFiles:
    doi_filename = str(textdoc.replace(".txt", ""))
    print(doi_filename)
    index = text_df.index[text_df['DOI_filename'] == doi_filename].tolist()
    print("index: " + str(index))
    text_df['fulltext'].iloc[index] = str(open(os.path.join(os.getcwd(),("txt/" + textdoc)), 'r').read()).replace(",", "")
    text_df['complete'].iloc[index] = 'complete'


os.chdir(core_folder)
listOfFiles = os.listdir(path=os.path.join(os.getcwd(),"search3txt"))

for textdoc in listOfFiles:
    doi_filename = str(textdoc.replace(".txt", ""))
    print(doi_filename)
    if bool(text_df.index[text_df['DOI_filename'] == doi_filename].tolist()):
        index = text_df.index[text_df['DOI_filename'] == doi_filename].tolist()[0]
        print("index: " + str(index))
        if bool(text_df['complete'].iloc[index] == 'empty'):
            print('is empty')
            text_df['fulltext'].iloc[index] = str(open(os.path.join(os.getcwd(),("search3txt/" + textdoc)), 'r').read()).replace(",", "")
            # print(text_df['fulltext'].iloc[index])
            text_df['complete'].iloc[index] = 'complete'
    else:
        print("no index")

complete_index = text_df.index[text_df['complete'] == 'complete'].tolist()
text_df['text_clean'] = text_df['fulltext']
os.chdir(os.path.join(core_folder, "cleantxt_all"))

for index in complete_index:
    intro_start = [m.start() for m in re.finditer('Introduction', text_df['text_clean'].iloc[index])]
    if bool(intro_start):
        print(intro_start)
        if intro_start[0] < 3000:
            print(text_df['text_clean'].iloc[index][intro_start[0]:(intro_start[0] + 30)])
            text_df['text_clean'].iloc[index] = text_df['text_clean'].iloc[index][intro_start[0]: len(text_df['text_clean'].iloc[index])]
    reference_start = [m.start() for m in re.finditer('References', text_df['text_clean'].iloc[index])]
    if bool(reference_start):
        length_ref = len(reference_start)
        print(reference_start)
        print(text_df['text_clean'].iloc[index][reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
        if reference_start[length_ref-1] > (len(text_df['text_clean'].iloc[index])/1.5):
            # print(text_df['text_clean'].iloc[index][reference_start[length_ref-1]:(reference_start[length_ref-1]+80)])
            print("passed the check")
    else:
        reference_start = [m.start() for m in re.finditer('Bibliography', text_df['text_clean'].iloc[index])]
        if bool(reference_start):
            length_ref = len(reference_start)
            print(reference_start)
            print(text_df['text_clean'].iloc[index][reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
            text_df['text_clean'].iloc[index] = text_df['text_clean'].iloc[index][0:reference_start[length_ref - 2]]
    # file1 = open(os.path.join(os.getcwd() , (text_df['DOI_filename'].iloc[index] + '.txt')),
    #     "a", errors="replace")
    # file1.writelines(text_df['text_clean'].iloc[index])

print(text_df[['fulltext', 'text_clean']].iloc[complete_index].head())
csv = os.path.join(os.getcwd(),"textcsv.csv")
pd.DataFrame(text_df).to_csv(csv)

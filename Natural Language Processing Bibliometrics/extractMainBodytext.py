# Importing modules
import pandas as pd
import os
import re
import numpy as np

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path=os.path.join(os.getcwd(),"txt"))

for file in listOfFiles:
    print(file)
    file1 = open(os.path.join(os.getcwd(), ("txt/" + file)),'r').read()
    intro_start = [m.start() for m in re.finditer('Introduction', file1)]
    if bool(intro_start):
        print(intro_start)
        if intro_start[0] < 3000:
            print(file1[intro_start[0]:(intro_start[0] + 30)])
            file1 = file1[intro_start[0]: len(file1)]
    reference_start = [m.start() for m in re.finditer('References', file1)]
    acknowledge_start = [m.start() for m in re.finditer('Acknowledgement', file1)]
    if bool(reference_start):
        length_ref = len(reference_start)
        print(reference_start)
        print(file1[reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
        if reference_start[length_ref-1] > (len(file1)/2):
            # print(file1[reference_start[length_ref-1]:(reference_start[length_ref-1]+80)])
            print("passed the check")
            file1 = file1[0: reference_start[length_ref-1]]
        else:
            if bool(acknowledge_start):
                if reference_start[length_ref-1] > acknowledge_start[-1]:
                    print("passed the check")
                    file1 = file1[0: reference_start[length_ref - 1]]
    else:
        reference_start = [m.start() for m in re.finditer('Bibliography', file1)]
        if bool(reference_start):
            length_ref = len(reference_start)
            print(reference_start)
            print(file1[reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
            file1 = file1[0:reference_start[length_ref - 2]]
        else:
            reference_start = [m.start() for m in re.finditer('Acknowledgement', file1)]
            if bool(reference_start):
                length_ref = len(reference_start)
                print(reference_start)
                print(file1[reference_start[length_ref - 1]:(reference_start[length_ref - 1] + 80)])
                file1 = file1[0:reference_start[length_ref - 2]]
    file2 = open(os.path.join(os.getcwd(), ('txtclean/' + file + '.txt')),
        "a", errors="replace")
    file2.writelines(file1)


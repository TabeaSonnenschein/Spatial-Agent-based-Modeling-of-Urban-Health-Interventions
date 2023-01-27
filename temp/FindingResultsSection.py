import os
import pandas as pd
import numpy as np
from itertools import chain

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
listOfFiles = os.listdir(path=os.path.join(os.getcwd(), "predict_labeled"))

for file in listOfFiles:
    labeled_data = pd.read_csv(os.path.join(os.getcwd(), ("predict_labeled/" + file)), encoding="latin1")
    print(file)
    Intro_start = -1
    for i in x:
        if Intro_start < 0:
            if (labeled_data['Word'].iloc[(i + 1)][0].isupper()) or (labeled_data['Word'].iloc[(i + 1)] == "."):
                print(i, " ".join(labeled_data['Word'].iloc[(i - 1):(i + 10)]))
                Intro_start = i
    x = np.where(labeled_data['Word'] == "Results")[0]
    for i in x:
        # if (labeled_data['Word'].iloc[(i - 1)] == "[CLS]") and (labeled_data['Word'].iloc[(i + 1)][0].isupper()):
        if (labeled_data['Word'].iloc[(i + 1)][0].isupper()) or (labeled_data['Word'].iloc[(i + 1)] == "."):
            print(i, " ".join(labeled_data['Word'].iloc[(i - 3):(i + 10)]))
            Results_start = i
    x = np.where(labeled_data['Word'] == "Introduction")[0]


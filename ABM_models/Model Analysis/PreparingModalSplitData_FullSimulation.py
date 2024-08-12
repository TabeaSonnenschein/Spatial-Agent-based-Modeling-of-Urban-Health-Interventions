import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
import datetime
import numpy as np
####################################################

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"

# scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
# scenario = "15mCity"
scenario = "15mCityWithDestination"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
# modelruns = [12365, 364241, 441245, 510849, 976383, 992330]
# modelruns = [modelrun for modelrun in modelruns if not(modelrun in [708658,481658])]

os.chdir(os.path.join(path_data,scenario, f"{nb_agents}Agents/ModalSplit"))

for modelrun in modelruns:
    print("Modelrun:", modelrun)
    # read the txt file, which consists of a list of dictionaries and transform to a dataframe
    with open(f"ModalSplitLog{nb_agents}_{scenario}_{modelrun}.txt") as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    content = [x.split(", ") for x in content]
    content = content[1:]

    hours = [x[0] for x in content]
    print(hours)
    dict = [", ".join(x[1:]).replace("Counter(", "").replace(")", "") for x in content]
    dict = [ast.literal_eval(x) if x != "" else ast.literal_eval("{'bike': 0, 'walk': 0, 'transit': 0, 'drive': 0}") for x in dict ]

    # transform the list of dictionaries to a dataframe
    modalsplit_df = pd.DataFrame.from_dict(dict)
    modalsplit_df["datesuffix"] = hours
    modalsplit_df["month"] = [x[1:] for x in modalsplit_df["datesuffix"].str.split("_").str[0]]
    modalsplit_df["day"] = [x[1:] for x in modalsplit_df["datesuffix"].str.split("_").str[1]]
    modalsplit_df["hour"] = [x[1:] for x in modalsplit_df["datesuffix"].str.split("_").str[2]]
    
    print(modalsplit_df.head())
    modalsplit_df["hour"] = modalsplit_df["hour"].astype(int)
    modalsplit_df["day"] = modalsplit_df["day"].astype(int)
    modalsplit_df["month"] = modalsplit_df["month"].astype(int)
    modalsplit_df["date"] = [f"2019-{modalsplit_df['month'].iloc[x]}-{modalsplit_df['day'].iloc[x]}" for x in range(len(modalsplit_df))]
    try:
        modalsplit_df['date'] = pd.to_datetime(modalsplit_df['date'], format='%Y-%m-%d', errors='coerce')
    except Exception as e:
        print("Error converting dates:", e)
    modalsplit_df["weekday"] = modalsplit_df['date'].dt.day_name()
    modalsplit_df[["bike", "drive", "transit", "walk"]] = modalsplit_df[["bike", "drive", "transit", "walk"]].fillna(0)
    print(modalsplit_df.head())

    modalsplit_df.to_csv(f"ModalSplitLog{nb_agents}_{scenario}_{modelrun}.csv", index=False)

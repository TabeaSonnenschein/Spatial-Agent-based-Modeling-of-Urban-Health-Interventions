import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
import datetime
import numpy as np
####################################################
# Preparing mean modal split for all runs

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"

# scenario = "StatusQuo"
scenario = "PrkPriceInterv"
# scenario = "15mCity"
# scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"

enriched = False

os.chdir(os.path.join(path_data,scenario, f"{nb_agents}Agents/ModalSplit"))

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
# modelruns = [ 108922, 194070,671831, 922980, 855029, 415419, 782789]

modes = ["bike","drive", "transit","walk"]
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
timerefs = ["month", "weekday",  "hour"]

if enriched:
    modalsplit_df =  pd.read_csv(f"ModalSplitEnriched_{scenario}_{modelruns[0]}.csv")
    modalsplit_df["date"] = [f"2019-{modalsplit_df['Month'].iloc[x]}-{modalsplit_df['Day'].iloc[x]}" for x in range(len(modalsplit_df))]
    try:
        modalsplit_df['date'] = pd.to_datetime(modalsplit_df['date'], format='%Y-%m-%d', errors='coerce')
    except Exception as e:
        print("Error converting dates:", e)
    modalsplit_df["weekday"] = modalsplit_df['date'].dt.day_name()
    modes = modes + ["duration"]
    # rename the columns
    modalsplit_df = modalsplit_df.rename(columns={"Month": "month", "Hour": "hour"})
    print(modalsplit_df.head())
else:
    modalsplit_df =  pd.read_csv(f"ModalSplitLog{nb_agents}_{scenario}_{modelruns[0]}.csv")

modalsplit_df = modalsplit_df[timerefs+modes]

for count, modelrun in enumerate(modelruns[1:]):
    if enriched:
        modalsplit_df2 =  pd.read_csv(f"ModalSplitEnriched_{scenario}_{modelruns[0]}.csv")
        modalsplit_df2["date"] = [f"2019-{modalsplit_df2['Month'].iloc[x]}-{modalsplit_df2['Day'].iloc[x]}" for x in range(len(modalsplit_df2))]
        try:
            modalsplit_df2['date'] = pd.to_datetime(modalsplit_df2['date'], format='%Y-%m-%d', errors='coerce')
        except Exception as e:
            print("Error converting dates:", e)
        modalsplit_df2["weekday"] = modalsplit_df2['date'].dt.day_name()
        modalsplit_df2 = modalsplit_df2.rename(columns={"Month": "month", "Hour": "hour"})
    else:
        modalsplit_df2 =  pd.read_csv(f"ModalSplitLog{nb_agents}_{scenario}_{modelrun}.csv")
    modalsplit_df2 = modalsplit_df2[timerefs+modes]
    modalsplit_df = modalsplit_df.merge(modalsplit_df2, on=timerefs, how="outer",suffixes=("",f"_{count+1}"))

modalsplit_df = modalsplit_df.rename(columns={mode: f"{mode}_0" for mode in modes})
for mode in modes:
    modalsplit_df[mode] = modalsplit_df[[f"{mode}_{count}" for count in range(len(modelruns))]].mean(axis=1)
    

modalsplit_df['weekday'] = pd.Categorical(modalsplit_df['weekday'], categories=days_order, ordered=True)
modalsplit_df = modalsplit_df[timerefs+modes].sort_values(by=timerefs)
print(modalsplit_df.head())
modalsplit_df.to_csv(f"ModalSplitLog{nb_agents}_{scenario}_MeanAcrossRuns.csv", index=False)
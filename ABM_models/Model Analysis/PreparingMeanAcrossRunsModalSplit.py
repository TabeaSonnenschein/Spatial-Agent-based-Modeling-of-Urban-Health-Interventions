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

# scenario = "SpeedInterv"
scenario = "StatusQuo"
# scenario = "PedStrWidth"
# scenario = "RetaiDnsDiv"
# scenario = "LenBikRout"
# scenario = "PedStrWidthOutskirt"
# scenario = "PedStrWidthCenter"
# scenario = "AmenityDnsExistingAmenityPlaces"
# scenario = "AmenityDnsDivExistingAmenityPlaces"
# scenario = "PedStrLen"
# scenario = "PedStrWidthOutskirt"
# scenario = "PedStrWidthCenter"
# scenario = "PedStrLenCenter"
# scenario = "PedStrLenOutskirt"
# scenario = "PrkPriceInterv"

os.chdir(os.path.join(path_data,scenario, f"{nb_agents}Agents/ModalSplit"))

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
modelruns = [modelrun for modelrun in modelruns if not(modelrun in [481658])]
modes = ["bike","drive", "transit","walk"]
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
timerefs = ["month", "weekday",  "hour"]
modalsplit_df =  pd.read_csv(f"ModalSplitLog{nb_agents}_{scenario}_{modelruns[0]}.csv")
modalsplit_df = modalsplit_df[timerefs+modes]

for count, modelrun in enumerate(modelruns[1:]):
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
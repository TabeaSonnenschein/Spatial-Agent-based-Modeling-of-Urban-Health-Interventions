import pandas as pd
import os
from matplotlib import pyplot as plt

path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/TrafficRemainder/TraffRemainder/new/"
scenario = "StatusQuo"
nb_humans = 43500
# read in the data
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_humans}Agents"), "Model Run"].values
subsetnr = [experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Model Run"]== modelrun), "Population Sample"].values[0] for modelrun in modelruns]
print(modelruns, subsetnr)
# modelruns = [400301,885127, 82445,411905, 360111, 601529, 276407, 872156, 678167, 869497]
# subsetnr = [0,2,3,4,5,6,7,1,9, 8]

newcols = [f"TraffVrest{hour}" for hour in range(24)]
for count,modelrun in enumerate(modelruns):
    # read in the text data
    TraffRemainder = pd.read_csv(f'{path_data}/AirPollGrid_HourlyTraffRemainder_{nb_humans}_pop{subsetnr[count]}_{modelrun}.csv')
    # print(TraffRemainder.columns)
    TraffVrestcols = [col for col in TraffRemainder.columns if "TraffVrest" in col]
    TraffVrestcols = [col for col in TraffVrestcols if not(col.endswith("_1"))]
    colhours = [int(col.replace("TraffVrest", "").split("_")[0]) for col in TraffVrestcols]
    for hour in range(24):
        print("hour", hour)
        # indices of the hour in colhours
        hourindices = [count for count, colhour in enumerate(colhours) if colhour == hour]
        hourcols = [TraffVrestcols[hourindex] for hourindex in hourindices]
        print(hourcols)
        TraffRemainder[f"TraffVrest{hour}"] = TraffRemainder[hourcols].mean(axis=1)
        
    TraffRemainder[["int_id"]+newcols].to_csv(f"{path_data}/MeanTraffRemainder_{nb_humans}_pop{subsetnr[count]}_{modelrun}.csv", index=False)
    if count == 0:
        TotTraffRemainder = TraffRemainder[["int_id"]+newcols]
        
    else:
        TotTraffRemainder[newcols] = TotTraffRemainder[newcols] + TraffRemainder[newcols]
        
TotTraffRemainder[newcols] = TotTraffRemainder[newcols]/len(modelruns)
TotTraffRemainder.to_csv(f"{path_data}/MeanTraffRemainder_{nb_humans}_popTot.csv", index=False)


import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
####################################################
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
# scenario  = "AmenityDnsDivExistingAmenityPlaces"
# scenario = "StatusQuoAllVars"
# scenario = "PedStrLen"
# scenario ="PedStrWidthOutskirt"
# scenario ="PedStrWidthCenter"
# scenario = "PedStrLenCenter"
# scenario = "PedStrLenOutskirt"
# scenario = "PrkPriceInterv"

cellsize = 50

experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
modelruns = [481658] 
bestStatusQuo = 481658

os.chdir(path_data)

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

viztype = [
        "singleIntervention", 
        # "statusquocomparison", 
        # "multipleRunComparison"
        ]

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz")

destination = path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"
AirPollGrid = gpd.read_feather(f"C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/FeatherDataABM/AirPollgrid{cellsize}m.feather")
NO2vars = [f"prNO2_m{month}_h{hour}" for hour in range(24)]

for modelrun in modelruns:
    for month in [1, 4,7,10]:
        for day in range(1,8):
            NO2dat = pd.read_csv(f"/{scenario}/{nb_agents}Agents/NO2/{modelrun}/AirPollGrid_NO2_{modelrun}_M{month}_D{day}_{scenario}_{modelrun}.csv")
            NO2dat["int_id"] = NO2dat["int_id"].astype(int)
            AirPollGrid_x = AirPollGrid.merge(NO2dat, on="int_id", how="left")

NO2dat_interv = pd.read_csv(f"NO2/{modelrun}/AirPollGrid_NO2_pred{nb_agents}_{modelrun}.csv")
NO2dat_statquo = pd.read_csv(f"NO2/StatusQuo/AirPollGrid_NO2_pred{nb_agents}_StatusQuo.csv")

# calculate hourly difference
NO2diff =  NO2dat_interv[NO2vars]- NO2dat_statquo[NO2vars]
NO2diff_cols = [var + "_diff" for var in NO2vars]
NO2diff.columns = NO2diff_cols

NO2diff["mean_NO2_diff"] = NO2diff.mean(axis=1)
meansperhour = list(NO2diff.mean(axis=0))
print("means per hour", meansperhour)
NO2diff["int_id"] = NO2dat_interv["int_id"]
NO2diff.to_csv(f"NO2/AirPollGrid_NO2_diff{nb_agents}_{modelrun}.csv", index=False)
print(NO2diff.describe())

AirPollGrid = AirPollGrid.merge(NO2diff, on="int_id", how="left")

AirPollGrid.plot("mean_NO2_diff", antialiased=False, legend = True)
plt.title(f"Mean NO2 Difference between {modelrun} and Status Quo")
plt.savefig(f'NO2/AirPollGrid_NO2_MeanDiff{nb_agents}_{modelrun}.png')
plt.close()

AirPollGrid.plot(NO2diff_cols[meansperhour.index(min(meansperhour))], antialiased=False, legend = True)
plt.title(f"Max NO2 Difference between {modelrun} and Status Quo: Hour {meansperhour.index(min(meansperhour))}")
plt.savefig(f'NO2/AirPollGrid_NO2_MaxDiff{nb_agents}_{modelrun}.png')
plt.close()

AirPollGrid.plot(NO2diff_cols[meansperhour.index(max(meansperhour))], antialiased=False, legend = True)
plt.title(f"Max NO2 Difference between {modelrun} and Status Quo: Hour {meansperhour.index(min(meansperhour))}")
plt.savefig(f'NO2/AirPollGrid_NO2_MinDiff{nb_agents}_{modelrun}.png')
plt.close()

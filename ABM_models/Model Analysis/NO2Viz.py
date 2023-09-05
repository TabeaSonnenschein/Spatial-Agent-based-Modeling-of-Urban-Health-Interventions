import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
####################################################
nb_agents = 43500
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/ModelRuns/"
# path_data = "/Users/tsonnens/Documents/dasefwg/"


# modelrun = "SpeedInterv"
# modelrun = "StatusQuo"
modelrun = "PedStrWidth"
# modelrun = "RetaiDnsDiv"
# modelrun = "LenBikRout"
cellsize = 50

os.chdir(path_data)

NO2dat_interv = pd.read_csv(f"NO2/{modelrun}/AirPollGrid_NO2_pred{nb_agents}_{modelrun}.csv")
NO2dat_statquo = pd.read_csv(f"NO2/StatusQuo/AirPollGrid_NO2_pred{nb_agents}_StatusQuo.csv")

month = 1
# calculate hourly difference
NO2vars = [f"prNO2_m{month}_h{hour}" for hour in range(24)]

NO2diff =  NO2dat_interv[NO2vars]- NO2dat_statquo[NO2vars]
NO2diff_cols = [var + "_diff" for var in NO2vars]
NO2diff.columns = NO2diff_cols

NO2diff["mean_NO2_diff"] = NO2diff.mean(axis=1)
meansperhour = list(NO2diff.mean(axis=0))
print("means per hour", meansperhour)
NO2diff["int_id"] = NO2dat_interv["int_id"]
NO2diff.to_csv(f"NO2/AirPollGrid_NO2_diff{nb_agents}_{modelrun}.csv", index=False)
print(NO2diff.describe())

AirPollGrid = gpd.read_feather(f"C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/FeatherDataABM/AirPollgrid{cellsize}m.feather")
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

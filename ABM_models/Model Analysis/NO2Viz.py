import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
####################################################
nb_agents = 43500
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"


# modelrun = "SpeedInterv"
# modelrun = "StatusQuo"
# modelrun = "PedStrWidth"
modelrun = "RetaiDnsDiv"
# modelrun = "LenBikRout"
cellsize = 50

os.chdir(path_data)

NO2dat_interv = pd.read_csv(f"ModelRuns/NO2/AirPollGrid_NO2_pred{nb_agents}_{modelrun}.csv")
NO2dat_statquo = pd.read_csv(f"ModelRuns/NO2/AirPollGrid_NO2_pred{nb_agents}_StatusQuo.csv")

month = 1
# calculate hourly difference
NO2vars = [f"prNO2_m{month}_h{hour}" for hour in range(24)]

NO2diff = NO2dat_statquo[NO2vars] - NO2dat_interv[NO2vars]
NO2diff_cols = [var + "_diff" for var in NO2vars]
NO2diff.columns = NO2diff_cols

NO2diff["mean_NO2_diff"] = NO2diff.mean(axis=1)
NO2diff["int_id"] = NO2dat_interv["int_id"]
NO2diff.to_csv(f"ModelRuns/NO2/AirPollGrid_NO2_diff{nb_agents}_{modelrun}.csv", index=False)
print(NO2diff.describe())

AirPollGrid = gpd.read_feather(f"FeatherDataABM/AirPollgrid{cellsize}m.feather")
AirPollGrid = AirPollGrid.merge(NO2diff, on="int_id", how="left")

AirPollGrid.plot("mean_NO2_diff", antialiased=False, legend = True)
plt.title(f"NO2 Difference between {modelrun} and Status Quo")
plt.savefig(f'ModelRuns/NO2/AirPollGrid_NO2_MeanDiff{nb_agents}_{modelrun}.png')
plt.close()
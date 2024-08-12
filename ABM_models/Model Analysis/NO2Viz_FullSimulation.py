import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from CellAutDisp import PrintSaveSummaryStats, MapSpatialDataFixedColorMapSetofVariables, ParallelMapSpatialDataFixedColorMap, ParallelMapSpatialData_StreetsFixedColorMap, ViolinOverTimeColContinous, SplitYAxis2plusLineGraph, meltPredictions, plotComputationTime,ViolinOverTimeColContinous_WithMaxSubgroups
from shapely import Point

####################################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"

# scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
# scenario = "15mCityWithDestination"
# scenario = "15mCity"
scenario = "NoEmissionZone2025"

cellsize = 50
os.chdir(path_data)

viztype = [
        "singleIntervention", 
        # "statusquocomparison", 
        # "multipleRunComparison"
        ]

experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
# modelruns = [modelrun for modelrun in modelruns if not(modelrun in [481658,708658])]
# modelruns = [715113]

os.chdir(path_data)

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
monthsnames = ["January",  "February",  "March",  "April",  "May",  "June",  
               "July",  "August",  "September",  "October",  "November",  "December"]


if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz")

destination = path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"
AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid{cellsize}m.feather")

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
datecolumns = [f"{day}-{month}-2019" for day in range(1,8) for month in [1,4,7,10]]
datedf = pd.DataFrame(datecolumns, columns=["date"])
datedf['date'] = pd.to_datetime(datedf['date'], format='%d-%m-%Y', errors='coerce')
datedf["weekday"] = datedf['date'].dt.day_name()
datedf['weekday'] = pd.Categorical(datedf['weekday'], categories=days_order, ordered=True)
datedf["day"] = datedf["date"].dt.day
datedf["month"] = datedf["date"].dt.month
datedf = datedf.sort_values("weekday")
datedf.to_csv(destination+"/datedf.csv", index=False)

for modelrun in modelruns:
    totNO2dat = pd.DataFrame()
    totNO2cols = []
    totNO2Ccols = []
    listoffiles = os.listdir(path_data+f"/{scenario}/{nb_agents}Agents/NO2/{modelrun}")
    for month in [1, 4,7,10, 12]:
        for day in range(1,8):
            if f"AirPollGrid_NO2_{modelrun}_M{month}_D{day}_{scenario}_{modelrun}.csv" in listoffiles:
                NO2dat = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/NO2/{modelrun}/AirPollGrid_NO2_{modelrun}_M{month}_D{day}_{scenario}_{modelrun}.csv")
                NO2dat["int_id"] = NO2dat["int_id"].astype(int)
                NO2vars = [col for col in NO2dat.columns if "prNO2" in col]
                totNO2cols = totNO2cols + NO2vars
    
                if totNO2dat.shape[0] == 0:
                    totNO2dat = NO2dat
                else:
                    totNO2dat = pd.concat([totNO2dat, NO2dat[NO2vars]], axis=1)
                print(totNO2dat.shape)
    print("final shape",totNO2dat.shape)
    print("finalcols", totNO2dat.columns)
    AirPollGrid_x = AirPollGrid.merge(totNO2dat, on="int_id", how="left")


    crs = "epsg:28992"
    points = gpd.GeoSeries(
            [Point(485000, 120000), Point(485001, 120000)], crs=crs
        )  # Geographic WGS 84 - degrees
    points = points.to_crs(32619)  # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])
    print(distance_meters)

    if "singleIntervention" in viztype:
        print("singleIntervention")
            
        AirPollGrid_x["mean_prNO2"] = AirPollGrid_x[totNO2cols].mean(axis=1)
        for month in [1, 4,7,10]:
            monthlycols = [col for col in AirPollGrid_x.columns if f"prNO2_M{month}" in col]
            AirPollGrid_x[f"mean_prNO2_M{month}"] = AirPollGrid_x[monthlycols].mean(axis=1)

        for hour in range(24):
            #hourly cols if column name ends with f"H{hour}"
            hourlycols = [col for col in AirPollGrid_x.columns if col.endswith(f"H{hour}")]
            AirPollGrid_x[f"mean_prNO2_H{hour}"] = AirPollGrid_x[hourlycols].mean(axis=1)
        
        for weekday in days_order: 
            weekdaycolentries = [f"prNO2_M{date[0]}_D{date[1]}" for date in datedf.loc[datedf["weekday"] == weekday, ["month", "day"]].values]
            weekdaycols = [col for entry in weekdaycolentries for col in AirPollGrid_x.columns  if entry in col]
            AirPollGrid_x[f"mean_prNO2_{weekday}"] = AirPollGrid_x[weekdaycols].mean(axis=1)

        # AirPollGrid_x.rename(columns={"mean_prTraff_Tuesday": "mean_prTraff_Monday",
        #                               "mean_prTraff_Wednesday": "mean_prTraff_Tuesday",
        #                               "mean_prTraff_Thursday": "mean_prTraff_Wednesday",
        #                               "mean_prTraff_Friday": "mean_prTraff_Thursday",
        #                               "mean_prTraff_Saturday": "mean_prTraff_Friday",
        #                               "mean_prTraff_Sunday": "mean_prTraff_Saturday",
        #                               "mean_prTraff_Monday": "mean_prTraff_Sunday"
        #                             }, inplace=True)

        colnames = ["mean_prNO2"]+[f"mean_prNO2_M{month}" for month in [1,4,7,10]] + [f"mean_prNO2_H{hour}" for hour in range(24)] + [f"mean_prNO2_{weekday}" for weekday in days_order] 
        labels = ["Mean annual NO2"] + [f"Mean NO2 in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean NO2 at Hour {hour}" for hour in range(24)] + [f"Mean NO2 on {weekday}s" for weekday in days_order] 
        os.chdir(destination)
        AirPollGrid_x[["int_id"]+colnames].to_csv(destination+f"/NO2Means_{scenario}_{modelrun}.csv", index=False)


# destination = path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"
# AirPollGrid = gpd.read_feather(f"C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/FeatherDataABM/AirPollgrid{cellsize}m.feather")
# 

# for modelrun in modelruns:
#     for month in [1, 4,7,10]:
#         for day in range(1,8):
#             NO2dat = pd.read_csv(f"/{scenario}/{nb_agents}Agents/NO2/{modelrun}/AirPollGrid_NO2_{modelrun}_M{month}_D{day}_{scenario}_{modelrun}.csv")
#             NO2dat["int_id"] = NO2dat["int_id"].astype(int)
#             AirPollGrid_x = AirPollGrid.merge(NO2dat, on="int_id", how="left")
            
        

# NO2dat_interv = pd.read_csv(f"NO2/{modelrun}/AirPollGrid_NO2_pred{nb_agents}_{modelrun}.csv")
# NO2dat_statquo = pd.read_csv(f"NO2/StatusQuo/AirPollGrid_NO2_pred{nb_agents}_StatusQuo.csv")

# # calculate hourly difference
# NO2diff =  NO2dat_interv[NO2vars]- NO2dat_statquo[NO2vars]
# NO2diff_cols = [var + "_diff" for var in NO2vars]
# NO2diff.columns = NO2diff_cols

# NO2diff["mean_NO2_diff"] = NO2diff.mean(axis=1)
# meansperhour = list(NO2diff.mean(axis=0))
# print("means per hour", meansperhour)
# NO2diff["int_id"] = NO2dat_interv["int_id"]
# NO2diff.to_csv(f"NO2/AirPollGrid_NO2_diff{nb_agents}_{modelrun}.csv", index=False)
# print(NO2diff.describe())

# AirPollGrid = AirPollGrid.merge(NO2diff, on="int_id", how="left")

# AirPollGrid.plot("mean_NO2_diff", antialiased=False, legend = True)
# plt.title(f"Mean NO2 Difference between {modelrun} and Status Quo")
# plt.savefig(f'NO2/AirPollGrid_NO2_MeanDiff{nb_agents}_{modelrun}.png')
# plt.close()

# AirPollGrid.plot(NO2diff_cols[meansperhour.index(min(meansperhour))], antialiased=False, legend = True)
# plt.title(f"Max NO2 Difference between {modelrun} and Status Quo: Hour {meansperhour.index(min(meansperhour))}")
# plt.savefig(f'NO2/AirPollGrid_NO2_MaxDiff{nb_agents}_{modelrun}.png')
# plt.close()

# AirPollGrid.plot(NO2diff_cols[meansperhour.index(max(meansperhour))], antialiased=False, legend = True)
# plt.title(f"Max NO2 Difference between {modelrun} and Status Quo: Hour {meansperhour.index(min(meansperhour))}")
# plt.savefig(f'NO2/AirPollGrid_NO2_MinDiff{nb_agents}_{modelrun}.png')
# plt.close()

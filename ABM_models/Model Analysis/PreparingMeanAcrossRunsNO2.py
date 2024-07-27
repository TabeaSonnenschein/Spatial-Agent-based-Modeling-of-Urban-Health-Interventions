
import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from CellAutDisp import PrintSaveSummaryStats, MapSpatialDataFixedColorMapSetofVariables, ParallelMapSpatialDataFixedColorMap, ParallelMapSpatialData_StreetsFixedColorMap, ViolinOverTimeColContinous, SplitYAxis2plusLineGraph, meltPredictions, plotComputationTime,ViolinOverTimeColContinous_WithMaxSubgroups
from shapely import Point

####################################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"

scenario = "StatusQuo"
# scenario = "PrkPriceInterv"

cellsize = 50

experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
modelruns = [modelrun for modelrun in modelruns if not(modelrun in [481658])]

os.chdir(path_data)

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
monthsnames = ["January",  "February",  "March",  "April",  "May",  "June",  
               "July",  "August",  "September",  "October",  "November",  "December"]


viztype = [
        # "singleIntervention", 
        # "statusquocomparison", 
        "multipleRunComparison"
        ]

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz")

destination = path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"
AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid{cellsize}m.feather")


days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

os.chdir(destination)

colnames = ["mean_prNO2"]+[f"mean_prNO2_M{month}" for month in [1,4,7,10]] + [f"mean_prNO2_H{hour}" for hour in range(24)] + [f"mean_prNO2_{weekday}" for weekday in days_order] 
NO2_df =  pd.read_csv(f"NO2Means_{scenario}_{modelruns[0]}.csv")
NO2_df = NO2_df[["int_id"]+colnames]

for count, modelrun in enumerate(modelruns[1:]):
    NO2_df2 =  pd.read_csv(f"NO2Means_{scenario}_{modelrun}.csv")
    NO2_df2 = NO2_df2[["int_id"]+colnames]
    NO2_df = NO2_df.merge(NO2_df2, on="int_id", how="outer",suffixes=("",f"_{count+1}"))
    
NO2_df = NO2_df.rename(columns={col: f"{col}_0" for col in colnames})
print(NO2_df.columns)
for col in colnames:
    NO2_df[col] = NO2_df[[f"{col}_{count}" for count in range(len(modelruns))]].mean(axis=1)
    
NO2_df = NO2_df[["int_id"]+colnames]
NO2_df.to_csv(destination+f"/NO2Means_{scenario}_MeanAcrossRuns.csv", index=False)

AirPollGrid_x = AirPollGrid.merge(NO2_df, on="int_id", how="left")


crs = "epsg:28992"
points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
points = points.to_crs(32619)  # Projected WGS 84 - meters
distance_meters = points[0].distance(points[1])
print(distance_meters)

labels = ["Mean annual NO2"] + [f"Mean NO2 in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean NO2 at Hour {hour}" for hour in range(24)] + [f"Mean NO2 on {weekday}s" for weekday in days_order] 
os.chdir(destination)
MapSpatialDataFixedColorMapSetofVariables(variables = colnames, rasterdf = AirPollGrid_x, jointlabel = "", 
                                                specificlabel = labels, vmin=0, vmax=40,distance_meters= distance_meters, 
                                                cmap="turbo", suffix=f"{scenario}_MeanAcrossRuns")
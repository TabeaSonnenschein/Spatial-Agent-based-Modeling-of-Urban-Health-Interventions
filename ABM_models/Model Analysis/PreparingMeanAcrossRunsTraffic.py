
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
modelruns = [modelrun for modelrun in modelruns if not(modelrun in [481658])]

os.chdir(path_data)

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
monthsnames = ["January",  "February",  "March",  "April",  "May",  "June",  
               "July",  "August",  "September",  "October",  "November",  "December"]


viztype = [
        "singleIntervention", 
        # "statusquocomparison", 
        # "multipleRunComparison"
        ]

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/Traffic/TraffViz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/Traffic/TraffViz")

destination = path_data+f"/{scenario}/{nb_agents}Agents/Traffic/TraffViz"
AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid{cellsize}m.feather")


days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

os.chdir(destination)

colnames = ["mean_prTraff", "mean_TrCount"]+[f"mean_prTraff_M{month}" for month in [1,4,7,10]] + [f"mean_prTraff_H{hour}" for hour in range(24)] + [f"mean_prTraff_{weekday}" for weekday in days_order]
Traffic_df =  pd.read_csv(f"TraffMeans_{scenario}_{modelruns[0]}.csv")
Traffic_df = Traffic_df[["int_id"]+colnames]

for count, modelrun in enumerate(modelruns[1:]):
    Traffic_df2 =  pd.read_csv(f"TraffMeans_{scenario}_{modelrun}.csv")
    Traffic_df2 = Traffic_df2[["int_id"]+colnames]
    Traffic_df = Traffic_df.merge(Traffic_df2, on="int_id", how="outer",suffixes=("",f"_{count+1}"))
    
Traffic_df = Traffic_df.rename(columns={col: f"{col}_0" for col in colnames})
print(Traffic_df.columns)
for col in colnames:
    Traffic_df[col] = Traffic_df[[f"{col}_{count}" for count in range(len(modelruns))]].mean(axis=1)
    
Traffic_df = Traffic_df[["int_id"]+colnames]
Traffic_df.to_csv(destination+f"/TraffMeans_{scenario}_MeanAcrossRuns.csv", index=False)

AirPollGrid_x = AirPollGrid.merge(Traffic_df, on="int_id", how="left")


crs = "epsg:28992"
points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
points = points.to_crs(32619)  # Projected WGS 84 - meters
distance_meters = points[0].distance(points[1])
print(distance_meters)

labels = ["Mean annual Traffic Volumn", "Mean annual Traffic Count"] + [f"Mean Traffic Volume in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean Traffic Volume at Hour {hour}" for hour in range(24)] + [f"Mean Traffic Volume on {weekday}s" for weekday in days_order]
os.chdir(destination)
MapSpatialDataFixedColorMapSetofVariables(variables = colnames, rasterdf = AirPollGrid_x, jointlabel = "", 
                                                specificlabel = labels, vmin=0, vmax=600,distance_meters= distance_meters, 
                                                cmap="turbo", suffix=f"{scenario}_MeanAcrossRuns")
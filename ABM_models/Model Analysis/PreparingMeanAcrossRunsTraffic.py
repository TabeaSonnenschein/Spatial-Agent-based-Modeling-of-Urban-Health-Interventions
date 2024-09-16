
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

# scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
scenario = "15mCity"
# scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"

cellsize = 50

viztype = [
        # "preparingData",
        # "mappingInterventionTraffic", 
        "statusquocomparison",
        ]

experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values

os.chdir(path_data)

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
monthsnames = ["January",  "February",  "March",  "April",  "May",  "June",  
               "July",  "August",  "September",  "October",  "November",  "December"]


if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/Traffic/TraffViz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/Traffic/TraffViz")

destination = path_data+f"/{scenario}/{nb_agents}Agents/Traffic/TraffViz"
AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid{cellsize}m.feather")
os.chdir(destination)

colnames = ["mean_prTraff", "mean_TrCount"]+[f"mean_prTraff_M{month}" for month in [1,4,7,10]] + [f"mean_prTraff_H{hour}" for hour in range(24)] + [f"mean_prTraff_{weekday}" for weekday in days_order]

crs = "epsg:28992"
points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
points = points.to_crs(32619)  # Projected WGS 84 - meters
distance_meters = points[0].distance(points[1])
print(distance_meters)


if "preparingData" in viztype:

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
else:
    Traffic_df =  pd.read_csv(destination+f"/TraffMeans_{scenario}_MeanAcrossRuns.csv")



if "mappingInterventionTraffic" in viztype:
    AirPollGrid_x = AirPollGrid.merge(Traffic_df, on="int_id", how="left")
    labels = ["Mean annual Traffic Volumn", "Mean annual Traffic Count"] + [f"Mean Traffic Volume in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean Traffic Volume at Hour {hour}" for hour in range(24)] + [f"Mean Traffic Volume on {weekday}s" for weekday in days_order]
    os.chdir(destination)
    MapSpatialDataFixedColorMapSetofVariables(variables = colnames, rasterdf = AirPollGrid_x, jointlabel = "", 
                                                    specificlabel = labels, vmin=0, vmax=600,distance_meters= distance_meters, 
                                                    cmap="turbo", suffix=f"{scenario}_MeanAcrossRuns")


if "statusquocomparison" in viztype:
    Traffic_status =  pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/Traffic/TraffViz/TraffMeans_StatusQuo_MeanAcrossRuns.csv")
    Traffic_diff = Traffic_df
    Traffic_diff[colnames] = Traffic_df[colnames].subtract(Traffic_status[colnames])
    Traffic_diff = Traffic_diff.rename(columns={col: f"{col}_diff" for col in colnames})
    Traffic_diff.to_csv(destination+f"/TraffMeans_{scenario}_MeanAcrossRuns_diff.csv", index=False)
    newcolnames = [f"{col}_diff" for col in colnames]  
    AirPollGrid_x = AirPollGrid.merge(Traffic_diff, on="int_id", how="left")
    # find global min and max
    vmin = AirPollGrid_x[newcolnames].min().min()
    vmax = AirPollGrid_x[newcolnames].max().max()
    print("vmin: ", vmin, "vmax: ", vmax)
    labels = ["Difference annual Traffic"] + [f"Difference Traffic in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Difference Traffic at Hour {hour}" for hour in range(24)] + [f"Difference Traffic on {weekday}s" for weekday in days_order] 
    MapSpatialDataFixedColorMapSetofVariables(variables = newcolnames, rasterdf = AirPollGrid_x, jointlabel = "", 
                                                    specificlabel = labels, vmin=vmin, vmax=30,distance_meters= distance_meters, 
                                                    cmap="turbo", suffix=f"{scenario}_DifferenceStatusQuo")
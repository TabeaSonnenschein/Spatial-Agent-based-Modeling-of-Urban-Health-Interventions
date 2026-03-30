
import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
# from CellAutDisp import PrintSaveSummaryStats, MapSpatialDataFixedColorMapSetofVariables, ParallelMapSpatialDataFixedColorMap, ParallelMapSpatialData_StreetsFixedColorMap, ViolinOverTimeColContinous, SplitYAxis2plusLineGraph, meltPredictions, plotComputationTime,ViolinOverTimeColContinous_WithMaxSubgroups
from shapely import Point
from matplotlib_scalebar.scalebar import ScaleBar

def MapSpatialDataFixedColorMapSetofVariables(variables, rasterdf, jointlabel, specificlabel, colormaplabelprefix, vmin, vmax, 
                                              distance_meters, cmap= "viridis" , suffix = ""):
    """This function maps the spatial distribution of a set of variables and saves them to files. 
    It uses a fixed color map.

    Args:
        variables (list(str)): A list of variables for which to create the maps.
        rasterdf (geodataframe): A geodataframe with the spatial data.
        jointlabel (str): A string label to use for the variables.
        specificlabel (list(str)): A list of string labels to use for the variables.
        vmin (float): The minimum value for the color map.
        vmax (float): The maximum value for the color map.
        distance_meters (int): The distance in meters for the scale bar.
        cmap (str, optional): The color map to use. Defaults to "viridis".
        suffix (str, optional): A string for the filesuffix. Defaults to "".
    """
    for variable in variables:
        print(rasterdf[variable].describe())
        ax= rasterdf.plot(variable, cmap= cmap, antialiased=False, linewidth = 0.00001, legend = True, legend_kwds= {"label": f"{colormaplabelprefix}{specificlabel[variables.index(variable)]} (µg/m3)", "location":"top", "shrink": 0.72,  "pad":0.03}, vmin = vmin, vmax=vmax)
        ax.set_xlim(rasterdf.total_bounds[0], rasterdf.total_bounds[2])
        ax.set_ylim(rasterdf.total_bounds[1], rasterdf.total_bounds[3])
        scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
        ax.add_artist(scalebar)
        # ax.axis('off')
        plt.xticks(fontsize=7.5)
        plt.yticks(fontsize=7.5)
        plt.xlabel("Latitude (EPSG:28992)", fontsize=7.5)
        plt.ylabel("Longitude (EPSG:28992)", fontsize=7.5)
        # plt.title(f"{jointlabel} Distribution: {specificlabel[variables.index(variable)]}")
        plt.savefig(f'{variable}_map_{suffix}.png', bbox_inches='tight',dpi=400)
        plt.close()



####################################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"

# scenario = "StatusQuo"
scenario = "PrkPriceInterv"
# scenario = "15mCityWithDestination"
# scenario = "15mCity"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"

cellsize = 50

experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
# modelruns = [modelrun for modelrun in modelruns if not(modelrun in [481658])]
print(modelruns)
os.chdir(path_data)


days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
monthsnames = ["January",  "February",  "March",  "April",  "May",  "June",  
               "July",  "August",  "September",  "October",  "November",  "December"]


viztype = [
        "preparingData",
        "mappingInterventionNO2", 
        "statusquocomparison",
        ]
allvars = False

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz")

destination = path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz"
AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid{cellsize}m.feather")



days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

os.chdir(destination)

colnames = ["mean_prNO2"]+[f"mean_prNO2_M{month}" for month in [1,4,7,10]] + [f"mean_prNO2_H{hour}" for hour in range(24)] + [f"mean_prNO2_{weekday}" for weekday in days_order] 

crs = "epsg:28992"
points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
points = points.to_crs(32619)  # Projected WGS 84 - meters
distance_meters = points[0].distance(points[1])
print(distance_meters)



if "preparingData" in viztype:
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
else:
    NO2_df =  pd.read_csv(f"NO2Means_{scenario}_MeanAcrossRuns.csv")

if "mappingInterventionNO2" in viztype:
    AirPollGrid_x = AirPollGrid.merge(NO2_df, on="int_id", how="left")
    os.chdir(destination)
    if allvars:
        mapvars = colnames
    else:
        mapvars = colnames[:1]
    labels = ["Mean annual NO2"] + [f"Mean NO2 in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean NO2 at Hour {hour}" for hour in range(24)] + [f"Mean NO2 on {weekday}s" for weekday in days_order] 
    MapSpatialDataFixedColorMapSetofVariables(variables = mapvars, rasterdf = AirPollGrid_x, jointlabel = "", 
                                                    specificlabel = labels, colormaplabelprefix="",
                                                    vmin=0, vmax=40,distance_meters= distance_meters, 
                                                    cmap="turbo", suffix=f"{scenario}_MeanAcrossRuns")

if "statusquocomparison" in viztype:
    NO2_status =  pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/NO2/NO2Viz/NO2Means_StatusQuo_MeanAcrossRuns.csv")
    NO2_diff = NO2_df
    NO2_diff[colnames] = NO2_df[colnames].subtract(NO2_status[colnames])
    NO2_diff = NO2_diff.rename(columns={col: f"{col}_diff" for col in colnames})
    NO2_diff.to_csv(destination+f"/NO2Means_{scenario}_MeanAcrossRuns_diff.csv", index=False)
    newcolnames = [f"{col}_diff" for col in colnames]  
    if allvars:
        mapvars = newcolnames
    else:
        mapvars = newcolnames[:1]
    AirPollGrid_x = AirPollGrid.merge(NO2_diff, on="int_id", how="left")
    # find global min and max
    vmin = AirPollGrid_x[newcolnames].min().min()
    vmax = AirPollGrid_x[newcolnames].max().max()
    # vmin = -0.3
    # vmax = 0.6
    print("vmin: ", vmin, "vmax: ", vmax)
    labels = ["Mean annual NO2"] + [f"Mean NO2 in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean NO2 at Hour {hour}" for hour in range(24)] + [f"Mean NO2 on {weekday}s" for weekday in days_order] 
    # labels = ["Difference annual NO2"] + [f"Difference NO2 in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Difference NO2 at Hour {hour}" for hour in range(24)] + [f"Difference NO2 on {weekday}s" for weekday in days_order] 
    MapSpatialDataFixedColorMapSetofVariables(variables = mapvars, rasterdf = AirPollGrid_x, jointlabel = "", 
                                                    specificlabel = labels, colormaplabelprefix="Δ ",
                                                    vmin=vmin, vmax=vmax,distance_meters= distance_meters, 
                                                    cmap="turbo", suffix=f"{scenario}_DifferenceStatusQuo")
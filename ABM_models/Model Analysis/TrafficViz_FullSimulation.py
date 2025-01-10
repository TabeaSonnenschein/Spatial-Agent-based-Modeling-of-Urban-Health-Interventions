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
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/samemodelrun/"
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/popsizes/"

# scenario = "StatusQuo"
scenario = "PrkPriceInterv"
# scenario = "15mCity"
# scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"

cellsize = 50

experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
# modelruns = [modelrun for modelrun in modelruns if not(modelrun in [481658, 708658])]
# modelruns = [715113]
modelruns = [750904,786142]
print(modelruns)

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
    print(scenario,"Modelrun: ", modelrun)
    totTraffdat = pd.DataFrame()
    totTraffcols = []
    totTraffCcols = []
    listoffiles = os.listdir(path_data+f"/{scenario}/{nb_agents}Agents/Traffic/{modelrun}")
    for month in [1, 4,7,10, 12]:
        for day in range(1,8):
            if f"AirPollGrid_Traff_{modelrun}_M{month}_D{day}_{scenario}_{modelrun}.csv" in listoffiles:
                Traffdat = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/Traffic/{modelrun}/AirPollGrid_Traff_{modelrun}_M{month}_D{day}_{scenario}_{modelrun}.csv")
                Traffdat["int_id"] = Traffdat["int_id"].astype(int)
                Traffvars = [col for col in Traffdat.columns if "prTraff" in col]
                totTraffcols = totTraffcols + Traffvars
                TraffCvars = [col for col in Traffdat.columns if "TrCount" in col]
                totTraffCcols = totTraffCcols + TraffCvars
                if totTraffdat.shape[0] == 0:
                    totTraffdat = Traffdat
                else:
                    totTraffdat = pd.concat([totTraffdat, Traffdat[Traffvars+TraffCvars]], axis=1)
                print(totTraffdat.shape)
    print("final shape",totTraffdat.shape)
    AirPollGrid_x = AirPollGrid.merge(totTraffdat, on="int_id", how="left")


    crs = "epsg:28992"
    points = gpd.GeoSeries(
            [Point(485000, 120000), Point(485001, 120000)], crs=crs
        )  # Geographic WGS 84 - degrees
    points = points.to_crs(32619)  # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])
    print(distance_meters)

    if "singleIntervention" in viztype:
        print("singleIntervention")
            
        AirPollGrid_x["mean_prTraff"] = AirPollGrid_x[totTraffcols].mean(axis=1)
        AirPollGrid_x["mean_TrCount"] = AirPollGrid_x[totTraffCcols].mean(axis=1)

        for month in [1, 4,7,10]:
            monthlycols = [col for col in AirPollGrid_x.columns if f"prTraff_M{month}_" in col]
            AirPollGrid_x[f"mean_prTraff_M{month}"] = AirPollGrid_x[monthlycols].mean(axis=1)

        for hour in range(24):
            hourlycols = [col for col in AirPollGrid_x.columns if ("prTraff" in col) & col.endswith(f"H{hour}")]
            AirPollGrid_x[f"mean_prTraff_H{hour}"] = AirPollGrid_x[hourlycols].mean(axis=1)
        
        for weekday in days_order: 
            weekdaycolentries = [f"prTraff_M{date[0]}_D{date[1]}" for date in datedf.loc[datedf["weekday"] == weekday, ["month", "day"]].values]
            weekdaycols = [col for entry in weekdaycolentries for col in AirPollGrid_x.columns  if entry in col]
            AirPollGrid_x[f"mean_prTraff_{weekday}"] = AirPollGrid_x[weekdaycols].mean(axis=1)
        
        # AirPollGrid_x.rename(columns={"mean_prTraff_Tuesday": "mean_prTraff_Monday",
        #                               "mean_prTraff_Wednesday": "mean_prTraff_Tuesday",
        #                               "mean_prTraff_Thursday": "mean_prTraff_Wednesday",
        #                               "mean_prTraff_Friday": "mean_prTraff_Thursday",
        #                               "mean_prTraff_Saturday": "mean_prTraff_Friday",
        #                               "mean_prTraff_Sunday": "mean_prTraff_Saturday",
        #                               "mean_prTraff_Monday": "mean_prTraff_Sunday"
        #                             }, inplace=True)
        
        colnames = ["mean_prTraff", "mean_TrCount"]+[f"mean_prTraff_M{month}" for month in [1,4,7,10]] + [f"mean_prTraff_H{hour}" for hour in range(24)] + [f"mean_prTraff_{weekday}" for weekday in days_order] + ["prTraff_M1_D1_H8", "TrCount_M1_D1_H8", "prTraff_M1_D2_H2", "TrCount_M1_D2_H2"]
        labels = ["Mean annual Traffic Volumn", "Mean annual Traffic Count"] + [f"Mean Traffic Volume in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean Traffic Volume at Hour {hour}" for hour in range(24)] + [f"Mean Traffic Volume on {weekday}s" for weekday in days_order] + ["Traffic Volume at: 01.01 at 8am", "Traffic Count at: 01.01 at 8am", "Traffic Volume at: 02.01 at 2am", "Traffic Count at: 02.01 at 2am"]
        os.chdir(destination)
        AirPollGrid_x[["int_id"]+colnames].to_csv(destination+f"/TraffMeans_{scenario}_{modelrun}.csv", index=False)
        # MapSpatialDataFixedColorMapSetofVariables(variables = colnames, rasterdf = AirPollGrid_x, jointlabel = "", 
        #                                             specificlabel = labels, vmin=0, vmax=400,distance_meters= distance_meters, 
        #                                             cmap="turbo", suffix=f"{scenario}_{modelrun}")
        # AirPollGrid_x.plot("TrCount_M1_D1_H8", antialiased=False, legend = True)
        # plt.title(f"Traffic Count at: 01.01 at 8am")
        # plt.savefig(f'AirPollGrid_TraffC_M1_D1_H8_{scenario}_{modelrun}.png')
        # plt.close()
        # AirPollGrid_x.plot("prTraff_M1_D1_H8", antialiased=False, legend = True)
        # plt.title(f"Traffic Volume at: 01.01 at 8am")
        # plt.savefig(f'AirPollGrid_Traff_M1_D1_H8_{scenario}_{modelrun}.png')
        # plt.close()
        # AirPollGrid_x.plot("TrCount_M1_D2_H2", antialiased=False, legend = True)
        # plt.title(f"Traffic Count at: 02.01 at 2am")
        # plt.savefig(f'AirPollGrid_TraffC_M1_D2_H2_{scenario}_{modelrun}.png')
        # plt.close()
        # AirPollGrid_x.plot("prTraff_M1_D2_H2", antialiased=False, legend = True)
        # plt.title(f"Traffic Volume at: 02.01 at 2am")
        # plt.savefig(f'AirPollGrid_Traff_M1_D2_H2_{scenario}_{modelrun}.png')
        # plt.close()
        
    if "statusquocomparison" in viztype:
        print("statusquocomparison")
        os.chdir(destination)

        Traffdat_interv = pd.read_csv(f"TraffMeans_{scenario}_{modelrun}.csv")
        Traffdat_statquo = pd.read_csv(f"/StatusQuo/{nb_agents}Agents/Traffic/TraffViz/TraffMeans_StatusQuo_{bestStatusQuo}.csv")

        # calculate hourly difference
        colnames = ["mean_prTraff", "mean_TrCount"]+[f"mean_prTraff_M{month}" for month in [1,4,7,10]] + [f"mean_prTraff_H{hour}" for hour in range(24)] + [f"mean_prTraff_{weekday}" for weekday in days_order] + ["prTraff_M1_D1_H8", "TrCount_M1_D1_H8", "prTraff_M1_D2_H2", "TrCount_M1_D2_H2"]

        Traffdiff =  Traffdat_interv[colnames]- Traffdat_statquo[colnames]
        Traffdiff_cols = [var + "_diff" for var in colnames]
        Traffdiff.columns = Traffdiff_cols

        Traffdiff["mean_NO2_diff"] = Traffdiff.mean(axis=1)
        meanspercol = list(Traffdiff.mean(axis=0))
        print("means per column", meanspercol)
        Traffdiff["int_id"] = Traffdat_interv["int_id"]
        Traffdiff.to_csv(f"TraffDiff_{scenario}_StatQuo_{modelrun}.csv", index=False)
        print(Traffdiff.describe())

        AirPollGrid_y = AirPollGrid.merge(Traffdiff, on="int_id", how="left")

        AirPollGrid_y.plot("mean_prTraff_diff", antialiased=False, legend = True)
        plt.title(f"Mean Traffic Volume Difference between {modelrun} and Status Quo")
        plt.savefig(f'Traff_MeanDiff{nb_agents}_{modelrun}.png')
        plt.close()

        labels = ["Mean annual Traffic Volumn", "Mean annual Traffic Count"] + [f"Mean Traffic Volume in {monthsnames[month-1]}" for month in [1, 4,7,10]] + [f"Mean Traffic Volume at Hour {hour}" for hour in range(24)] + [f"Mean Traffic Volume on {weekday}s" for weekday in days_order] + ["Traffic Volume at: 01.01 at 8am", "Traffic Count at: 01.01 at 8am", "Traffic Volume at: 02.01 at 2am", "Traffic Count at: 02.01 at 2am"]
        labelsdiff = [f"{label} Difference" for label in labels]

        MapSpatialDataFixedColorMapSetofVariables(variables = Traffdiff_cols, rasterdf = AirPollGrid_y, jointlabel = "", 
                                                    specificlabel = labels, vmin=0, vmax=100,distance_meters= distance_meters, 
                                                    cmap="turbo", suffix=f"{scenario}_{modelrun}")
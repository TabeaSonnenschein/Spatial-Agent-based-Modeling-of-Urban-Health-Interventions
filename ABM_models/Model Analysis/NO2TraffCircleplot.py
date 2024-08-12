import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import geopandas as gpd
from pycirclize import Circos
import numpy as np
from matplotlib.lines import Line2D
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry.point import Point
from itertools import chain
####################################################

def calc_min_max(df, column, timeunit_contains, round_val = 1, hardzero = True):
            origmin_val = np.min([df.loc[df["timeunit"].str.contains(timeunit_contains), column].min()])
            origmax_val = np.max([df.loc[df["timeunit"].str.contains(timeunit_contains), column].max()])
            print("original min", origmin_val, "original max", origmax_val)
            step = ((origmax_val - origmin_val)/7).round(round_val)
            min_val = (origmin_val - step).round(round_val)  
            if hardzero:
                if min_val < 0:
                    min_val = 0
            max_val = (origmax_val + step).round(round_val)
            step = ((max_val - min_val)/5).round(round_val)
            while step == 0:
                round_val += 1
                min_val = np.min([df.loc[df["timeunit"].str.contains(timeunit_contains), column].min()]).round(round_val)
                max_val = np.max([df.loc[df["timeunit"].str.contains(timeunit_contains),column].max()]).round(round_val)      
                step = ((max_val - min_val)/4).round(round_val)    
                min_val = (min_val - step).round(round_val)  
                if hardzero:
                    if min_val < 0:
                        min_val = 0
                max_val = (max_val + step).round(round_val)
                step = ((max_val - min_val)/4).round(round_val)
            if round_val == 0:
                min_val = int(min_val)
                max_val = int(max_val)
                step = int(step)
            print("Finalmin", min_val, "max", max_val, "step", step)
            return min_val, max_val, step

def create_NO2Traffmaxminparamdict(df, hardzero = True):
    NO2hourmin, NO2hourmax, NO2hourstep = calc_min_max(df, column= "NO2", timeunit_contains = "hour", round_val = 1, hardzero = hardzero)
    NO2monthmin, NO2monthmax, NO2monthstep = calc_min_max(df, column= "NO2", timeunit_contains = "month", round_val = 2, hardzero = hardzero)
    NO2weekdaymin, NO2weekdaymax, NO2weekdaystep = calc_min_max(df, column= "NO2", timeunit_contains = "weekday", round_val = 2, hardzero = hardzero)
    if NO2weekdaymin < NO2monthmin:
        NO2monthmin = NO2weekdaymin
    if NO2weekdaymax > NO2monthmax:
        NO2monthmax = NO2weekdaymax
    Traffhourmin, Traffhourmax, Traffhourstep = calc_min_max(df, column= "Traffic", timeunit_contains = "hour", round_val = 0, hardzero = hardzero)
    Traffmonthmin, Traffmonthmax, Traffmonthstep = calc_min_max(df, column= "Traffic", timeunit_contains = "weekday", round_val = 0, hardzero = hardzero)
    minmaxparams = {"NO2monthmin": NO2monthmin, "NO2monthmax": NO2monthmax, "NO2monthstep": NO2monthstep,
            "NO2hourmin": NO2hourmin, "NO2hourmax": NO2hourmax, "NO2hourstep": NO2hourstep,
            "Traffmonthmin": Traffmonthmin, "Traffmonthmax": Traffmonthmax, "Traffmonthstep": Traffmonthstep,
            "Traffhourmin": Traffhourmin, "Traffhourmax": Traffhourmax, "Traffhourstep": Traffhourstep}        
    return minmaxparams

def plotCircosNO2Traff_Timeunits(aggexposure, colourdict,
                                NO2monthmin = 19.9, NO2monthmax = 21, NO2monthstep = 0.2,
                                NO2hourmin=18, NO2hourmax = 24, NO2hourstep=1, 
                                Traffmonthmin = 265, Traffmonthmax = 286, Traffmonthstep = 2,
                                Traffhourmin = 20, Traffhourmax = 320 , Traffhourstep = 50,
                                suffix = None):
        outerringdict = {"Hours": 23, "Weekdays": 6, "Timeunits": 1,"Months": 3, 
                        "Total": 0.4
                        }
        outerringdict_xvalues = {
            "Hours": list(range(24)) ,
            "Weekdays": list(range(7)),  # Convert to numeric indices
            "Months": list(range(4)),     # Convert to numeric indices
            "Total": [0]
        }
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        outerringdict_labels = {
            "Hours": [f"{x}:00" for x in range(24)] + [""],
            "Weekdays":days_order + [""], 
            "Months": ["January", "April", "July", "October"] + [""],
            "Total": ["Mean"] + [""]
        }

        sectorrows = {"Hours": [f"hour {hour}" for hour in range(24)],
                        "Weekdays": [f"weekday {day}" for day in days_order],
                        "Months": [f"month {month}" for month in [1,4,7,10]],
                        "Total": ["total"]
                        }
                            
        axiscol = "dimgray"
        gridcol = "lightgrey"
        axiswidth = 1.3 
        # Create Circos plot
        circos = Circos(outerringdict, space=20)

        for sector in circos.sectors:
            print(sector.name)
            if sector.name == "Timeunits":
                # Plot sector name
                NO2_track = sector.add_track((65, 100), r_pad_ratio=0.1)
                NO2_track.axis(ec = "none")
                NO2_track.text("NO2(µg/m3)", x = NO2_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

                Traff_track = sector.add_track((20, 55), r_pad_ratio=0.1)
                Traff_track.axis(ec = "none")
                Traff_track.text("Traffic Volume", x = Traff_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

            else:
                # Plot sector name
                sector.text(f"{sector.name}", r=125, size=14)
                sectorrows_df = aggexposure.loc[aggexposure["timeunit"].isin(sectorrows[sector.name])]
                print(sectorrows_df)
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]
                print(sectorrows_df["NO2"].values)
                NO2 = sectorrows_df["NO2"].values
                Traff =  sectorrows_df["Traffic"].values
                
                # NO2 line
                NO2_track = sector.add_track((65, 100), r_pad_ratio=0.1)
                NO2_track.axis(ec = axiscol)
                if sector.name == "Hours":
                    NO2max = NO2hourmax
                    NO2min = NO2hourmin
                    rangeNO2 =list(np.arange(start=NO2min, stop = NO2max + NO2hourstep, step = NO2hourstep))
                else:
                    NO2max = NO2monthmax
                    NO2min = NO2monthmin
                    rangeNO2 =list(np.arange(start=NO2min, stop = NO2max + NO2monthstep, step = NO2monthstep))
                
                rangeNO2 = [round(val, 2) for val in rangeNO2]
                NO2max = rangeNO2[-1]    
                NO2_track.yticks(y=rangeNO2, labels=rangeNO2,vmin=NO2min, vmax=NO2max, side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for NO2val in rangeNO2:
                    NO2_track.line([NO2_track.start, NO2_track.end], [NO2val, NO2val], vmin=NO2min, vmax=NO2max, lw=1, ls="dotted", color = gridcol)
                
                if sector.name == "Total":
                    NO2_track.scatter(x, NO2, vmin=NO2min, vmax=NO2max,lw=2, color=colourdict["NO2"])
                else:
                    NO2_track.line(x, NO2, vmin=NO2min, vmax=NO2max, lw=2, color=colourdict["NO2"])

                NO2_track.xticks_by_interval(
                    1,
                    label_size=8,
                    label_orientation="vertical",
                    label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                )
                
                # Plot points
                Traff_track = sector.add_track((20, 55), r_pad_ratio=0.1)
                Traff_track.axis(ec = axiscol)
                if sector.name == "Hours":
                    Traffmax = Traffhourmax
                    Traffmin = Traffhourmin
                    rangeTraff =list(np.arange(start=Traffmin, stop = Traffmax +Traffhourstep, step = Traffhourstep))
                else:
                    Traffmax = Traffmonthmax
                    Traffmin = Traffmonthmin
                    rangeTraff =list(np.arange(start=Traffmin, stop = Traffmax + Traffmonthstep, step = Traffmonthstep))
        
                    Traffmax = rangeTraff[-1]    
                Traff_track.yticks(y=rangeTraff, labels=rangeTraff,vmin=Traffmin, vmax=Traffmax,  side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for Traffval in rangeTraff:
                    Traff_track.line([Traff_track.start, Traff_track.end], [Traffval, Traffval], vmin=Traffmin, vmax=Traffmax,  lw=1, ls="dotted", color = gridcol)
                
                if sector.name == "Total":
                    Traff_track.scatter(x, Traff, vmin=Traffmin, vmax=Traffmax, lw=2, color = colourdict["Traffic"])

                else:
                    Traff_track.line(x, Traff, vmin=Traffmin, vmax=Traffmax, lw=2, color = colourdict["Traffic"])


        # Create legend
        legend_elements = []
        legend_elements.append(Line2D([0], [0], color=colourdict["NO2"], lw=2, label="Mean NO2"))
        legend_elements.append(Line2D([0], [0], color=colourdict["Traffic"], lw=2, label="Mean Traffic Volume"))
        figure = circos.plotfig(dpi=600)
        figure.legend(handles=legend_elements, loc='lower right', ncol=1, title = "Legend")
        figure.savefig(f"CirclePlot_with_Legend{suffix}.png", dpi=600)

#########################


nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData"

# scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
# scenario = "15mCityWithDestination"
# scenario = "15mCity"
scenario = "NoEmissionZone2025"

cellsize = 50

needCompAggdf = True

viztype = [
        "singleIntervention",
        "statusquocomparison",
]

AmsterdamCityExtent = True
if AmsterdamCityExtent:
    suffix = "AmsterdamCityExtent"
else:
    suffix = "FullSpatialExtent"



if needCompAggdf:
    Traff_df = pd.read_csv(path_data + f"/ModelRuns/{scenario}/{nb_agents}Agents/Traffic/TraffViz/TraffMeans_{scenario}_MeanAcrossRuns.csv")
    NO2_df =  pd.read_csv(path_data +f"/ModelRuns/{scenario}/{nb_agents}Agents/NO2/NO2Viz/NO2Means_{scenario}_MeanAcrossRuns.csv")
    BackgroundNO2 = pd.read_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\AirPollutionModelData\Pred_50mTrV_TrI_noTrA.csv")
    BackgroundNO2 = BackgroundNO2[["int_id", "baseline_NO2"]]
    
    AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid{cellsize}m.feather")
    if AmsterdamCityExtent:
        spatial_extent = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/NoEmissionZone2030.feather")
    else:
        spatial_extent = gpd.read_feather(path_data+"/SpatialData/SpatialExtent.feather")

    Intids = gpd.sjoin(AirPollGrid,spatial_extent, how="inner", predicate='intersects')["int_id"].values

    print(Intids)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    NO2colnames = ["mean_prNO2"]+[f"mean_prNO2_M{month}" for month in [1,4,7,10]] + [f"mean_prNO2_H{hour}" for hour in range(24)] + [f"mean_prNO2_{weekday}" for weekday in days_order] 
    Traffcolnames = ["mean_prTraff"]+[f"mean_prTraff_M{month}" for month in [1,4,7,10]] + [f"mean_prTraff_H{hour}" for hour in range(24)] + [f"mean_prTraff_{weekday}" for weekday in days_order]

    NO2_df = NO2_df.loc[NO2_df["int_id"].isin(Intids), ["int_id"]+NO2colnames]
    print(NO2_df.head())

    Traff_df = Traff_df.loc[(Traff_df["int_id"].isin(Intids)) & (Traff_df["mean_prTraff"] != 0), ["int_id"]+Traffcolnames]
    print(Traff_df.head())

    BackgroundNO2 = BackgroundNO2.loc[BackgroundNO2["int_id"].isin(Intids),["int_id", "baseline_NO2"]]
    BackgroundNO2.loc[BackgroundNO2["int_id"].isin(Intids),"baseline_NO2"].mean()
    print(f"MeanBackgroundNO2 for {suffix}", BackgroundNO2["baseline_NO2"].mean())
    
    NO2_means = NO2_df[NO2colnames].mean(axis=0).values
    Traff_means = Traff_df[Traffcolnames].mean(axis=0).values

    TraffNO2 =  NO2_df.copy()   
    for col in NO2colnames:
        TraffNO2[col] = TraffNO2[col] - BackgroundNO2["baseline_NO2"].values
    TraffNO2_means = TraffNO2[NO2colnames].mean(axis=0).values
    
    print(NO2_means)
    print(Traff_means)

    outerringdict_xvalues = {
        "Hours": list(range(24)) ,
        "Weekdays": list(range(7)),  # Convert to numeric indices
        "Months": list(range(4)),     # Convert to numeric indices
        "Total": [0]
    }
    outerringdict_labels = {
        "Hours": [f"{x}:00" for x in range(24)] + [""],
        "Weekdays":days_order + [""], 
        "Months": ["January", "April", "July", "October"] + [""],
        "Total": ["Mean"] + [""]
    }

    sectorrows = {"Hours": [f"hour {hour}" for hour in range(24)],
                    "Weekdays": [f"weekday {day}" for day in days_order],
                    "Months": [f"month {month}" for month in [1,4,7,10]],
                    "Total": ["total"]
                    }

    timeunits = sectorrows["Total"] + sectorrows["Months"] + sectorrows["Hours"] + sectorrows["Weekdays"]

    timeNO2Traff_df = pd.DataFrame({"timeunit": timeunits, "NO2": NO2_means, "Traffic": Traff_means, "TraffNO2": TraffNO2_means})
    os.chdir(path_data +f"/ModelRuns/{scenario}/{nb_agents}Agents/NO2/NO2Viz/")

    timeNO2Traff_df.to_csv(f"NO2TraffMeansTime_{scenario}_MeanAcrossRuns_{suffix}.csv", index=False)
    
else:
    os.chdir(path_data +f"/ModelRuns/{scenario}/{nb_agents}Agents/NO2/NO2Viz/")
    timeNO2Traff_df = pd.read_csv(f"NO2TraffMeansTime_{scenario}_MeanAcrossRuns_{suffix}.csv")

colourdict = {"NO2": "red", "Traffic": "blue"}

if "singleIntervention" in viztype:
    minmaxparams = create_NO2Traffmaxminparamdict(timeNO2Traff_df)
    plotCircosNO2Traff_Timeunits(timeNO2Traff_df, colourdict, **minmaxparams, suffix = f"{scenario}_TraffNO2Timeunits_{suffix}")

if "statusquocomparison" in viztype:
    statustimeNO2Traff_df = pd.read_csv(path_data +f"/ModelRuns/StatusQuo/{nb_agents}Agents/NO2/NO2Viz/NO2TraffMeansTime_StatusQuo_MeanAcrossRuns.csv")
    timeNO2Traff_diff_df = timeNO2Traff_df.copy()
    timeNO2Traff_diff_df["NO2"] = timeNO2Traff_df["NO2"] - statustimeNO2Traff_df["NO2"]
    timeNO2Traff_diff_df["Traffic"] = timeNO2Traff_df["Traffic"] - statustimeNO2Traff_df["Traffic"]
    timeNO2Traff_diff_df.to_csv(f"NO2TraffMeansTime_{scenario}_DiffStatusQuo.csv", index=False)

    minmaxparams = create_NO2Traffmaxminparamdict(timeNO2Traff_diff_df, hardzero= False )
    plotCircosNO2Traff_Timeunits(timeNO2Traff_diff_df, colourdict, **minmaxparams,suffix = f"{scenario}_TraffNO2Timeunits _{suffix}")
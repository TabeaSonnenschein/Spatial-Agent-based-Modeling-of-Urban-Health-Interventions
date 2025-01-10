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
import matplotlib.cm as cm
import matplotlib.colors as colors

def plotCircosMeanStrat(stratexposure_df, subgroups, subgroupcolors, outcomevar, meanval, roundval, centertext, redlinelabel = "Mean Exposure", rangeval = None, suffix = None):
        outerringdict = {}
        outerringdict_xvalues = {}
        outerringdict["Mean"] = 0.3
        outerringdict_xvalues["Mean"] = [0]
        for subgroup in subgroups:
            outerringdict[subgroup] = len(subgroups[subgroup])-0.5
            outerringdict_xvalues[subgroup]= list(range(len(subgroups[subgroup])))
        
        outerringdict_labels = subgroups
        outerringdict_labels["Mean"] = ["", ""]
        if rangeval == None:
            if "NO2" in outcomevar:
                minval = -0.5
                maxval = 0.5
                rangeval = [-0.5, -0.25, 0, 0.25, 0.5]
            elif "MET" in outcomevar:
                minval = -0.05
                maxval = 0.05
                rangeval = [-0.05, -0.025, 0, 0.025, 0.05]
        else:
            minval = rangeval[0]
            maxval = rangeval[-1]
        if meanval != 0:
            meanval = meanval.round(roundval)
            absoluterange = [(meanval + val).round(roundval) for val in rangeval]
            absolutemin = absoluterange[0].round(roundval)
            absolutemax = absoluterange[-1].round(roundval)
        else:   
            absoluterange = [(meanval + val) for val in rangeval]
            absolutemin = absoluterange[0]
            absolutemax = absoluterange[-1]
   
        axiscol = "white"
        gridcol = "lightgrey"
        circos = Circos(outerringdict, space=25)

        for sector in circos.sectors:
                print(sector.name)
                # Plot sector name
                if sector.name == "Mean":
                    sector.text(f"{redlinelabel}\n(red line)", r=120, size=14, color="red", adjust_rotation=False, orientation="horizontal")
                else:
                    sector.text(f"{sector.name.capitalize().replace('_', ' ').replace('Hh', 'Household')}", r=140, size=14)
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]

                labeltrack = sector.add_track((98, 99), r_pad_ratio=0)
                labeltrack.axis(ec = "none")
                if sector.name != "Mean":
                    labeltrack.xticks_by_interval(
                        1,
                        label_size=8,
                        label_orientation="vertical",
                        label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                    )
                
                Track = sector.add_track((35, 98), r_pad_ratio=0)
                if sector.name == "Mean":
                    Track.axis(ec = axiscol, fc="none")
                    for yval in absoluterange:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=absolutemin, vmax=absolutemax, lw=1, ls="dotted", color = gridcol)
                    Track.line([Track.start,Track.end], [meanval,meanval], vmin=absolutemin, vmax=absolutemax, lw=2, color="red")
                    Track.yticks(y=absoluterange, labels=absoluterange,vmin=absolutemin, vmax=absolutemax, side="left", tick_length=1, 
                             label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                    
                else:
                    Track.axis(ec = axiscol)
                    for yval in rangeval:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=minval, vmax=maxval, lw=1, ls="dotted", color = gridcol)
                    Track.line([Track.start,Track.end], [0,0], vmin=minval, vmax=maxval, lw=2, color="red")
                    sectordata = list([stratexposure_df.loc[stratexposure_df["Label"] == val, outcomevar].values[0] for val in subgroups[sector.name]])
                    print(x, sectordata, subgroupcolors[sector.name])
                    Track.bar(x=x, height = sectordata, vmin=minval, vmax = maxval , align="edge", width=0.4, color=subgroupcolors[sector.name])
                    # Track.yticks(y=rangeval, labels=rangeval,vmin=minval, vmax=maxval, side="left", tick_length=1, 
                    #          label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                if sector.name == "Mean":
                    innerText = sector.add_track((0, 0), r_pad_ratio=0.1)
                    innerText.axis(ec = "none")
                    innerText.text(centertext, x = innerText.start, color="black", adjust_rotation=False, orientation="horizontal" ,size=14)

        figure = circos.plotfig(dpi=600)
        figure.savefig(f"CirclePlot_{outcomevar}_Subgroups_{suffix}.png", dpi=600)


def plotCircosMeanStratRelativ(stratexposure_df, subgroups, subgroupcolors, outcomevar, meanvalStatQ,meanvalScenario, roundval, centertext, redlinelabel = "Mean Exposure", rangeval = None, suffix = None):
        outerringdict = {}
        outerringdict_xvalues = {}
        outerringdict["Mean"] = 0.3
        outerringdict_xvalues["Mean"] = [0]
        for subgroup in subgroups:
            outerringdict[subgroup] = len(subgroups[subgroup])-0.5
            outerringdict_xvalues[subgroup]= list(range(len(subgroups[subgroup])))
        
        outerringdict_labels = subgroups
        outerringdict_labels["Mean"] = ["", ""]
        if rangeval == None:
            if "NO2" in outcomevar:
                minval = -0.5
                maxval = 0.5
                rangeval = [-0.5, -0.25, 0, 0.25, 0.5]
            elif "MET" in outcomevar:
                minval = -0.05
                maxval = 0.05
                rangeval = [-0.05, -0.025, 0, 0.025, 0.05]
        else:
            minval = rangeval[0]
            maxval = rangeval[-1]
        if meanvalStatQ != 0:
            meanvalStatQ = meanvalStatQ.round(roundval)
            absoluterange = [(meanvalStatQ + val).round(roundval) for val in rangeval]
            absolutemin = absoluterange[0].round(roundval)
            absolutemax = absoluterange[-1].round(roundval)
        else:   
            absoluterange = [(meanvalStatQ + val) for val in rangeval]
            absolutemin = absoluterange[0]
            absolutemax = absoluterange[-1]
   
        axiscol = "#FF000000"
        gridcol = "lightgrey"
        circos = Circos(outerringdict, space=24)

        for sector in circos.sectors:
                print(sector.name)
                # Plot sector name
                if sector.name == "Mean":
                    sector.text("Population\nMean", r=140, size=14, color="black", adjust_rotation=False, orientation="horizontal")
                else:
                    sector.text(f"{sector.name.capitalize().replace('_', ' ').replace('Hh', 'Household')}", r=140, size=14)
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]

                labeltrack = sector.add_track((98, 99), r_pad_ratio=0)
                labeltrack.axis(ec = "none")
                if sector.name != "Mean":
                    labeltrack.xticks_by_interval(
                        1,
                        label_size=8,
                        label_orientation="vertical",
                        label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                    )
                
                Track = sector.add_track((35, 98), r_pad_ratio=0)
                if sector.name == "Mean":
                    Track.axis(ec = axiscol, fc="none")
                    for yval in absoluterange:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=absolutemin, vmax=absolutemax, lw=1, ls="dotted", color = gridcol)
                    Track.scatter([Track.end], [meanvalStatQ], vmin=absolutemin, vmax=absolutemax, lw=2, color="red")
                    Track.scatter([Track.end], [meanvalScenario], vmin=absolutemin, vmax=absolutemax, lw=2, color="black")
                    # Track.line([Track.start,Track.end], [meanval,meanval], vmin=absolutemin, vmax=absolutemax, lw=2, color="red")
                    Track.yticks(y=absoluterange, labels=absoluterange,vmin=absolutemin, vmax=absolutemax, side="left", tick_length=1, 
                             label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                    
                else:
                    Track.axis(ec = axiscol)
                    for yval in rangeval:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=minval, vmax=maxval, lw=1, ls="dotted", color = gridcol)
                    # Track.line([Track.start,Track.end], [0,0], vmin=minval, vmax=maxval, lw=1.5, color="red")
                    sectordata_after = list([stratexposure_df.loc[stratexposure_df["Label"] == val, f"{outcomevar}_deviationStatQMean"].values[0] for val in subgroups[sector.name]])
                    sectordata_before = list([stratexposure_df.loc[stratexposure_df["Label"] == val, f"{outcomevar}_StatQdevStatQMean"].values[0] for val in subgroups[sector.name]])
                    bothbelow = [idx for idx in range(len(sectordata_after)) if ((sectordata_after[idx] < 0) and (sectordata_before[idx]<0))]
                    bothabove = [idx for idx in range(len(sectordata_after)) if ((sectordata_after[idx] > 0) and (sectordata_before[idx]>0))]
                    blank = [0 for x in range(len(sectordata_after))]
                    for idx in bothbelow:
                        if sectordata_after[idx] < sectordata_before[idx]:
                            blank[idx] = sectordata_before[idx]
                        else:
                            blank[idx] = sectordata_after[idx]
                    for idx in bothabove:
                        if sectordata_after[idx] < sectordata_before[idx]:
                            blank[idx] = sectordata_after[idx]
                        else:
                            blank[idx] = sectordata_before[idx]
                    print(x, sectordata_after, sectordata_before, subgroupcolors[sector.name])
                    Track.bar(x=x, height = sectordata_before, vmin=minval, vmax = maxval , align="center", width=0.4, color=subgroupcolors[sector.name], alpha=0.5)
                    Track.bar(x=x, height = sectordata_after, vmin=minval, vmax = maxval , align="center", width=0.4, color=subgroupcolors[sector.name], alpha=0.5)
                    Track.bar(x=x, height = blank, vmin=minval, vmax = maxval , align="center", width=0.5, color="white")
                    Track.scatter(x, sectordata_before, vmin=minval, vmax=maxval,lw=2, color="red")
                    Track.scatter(x, sectordata_after, vmin=minval, vmax=maxval,lw=2, color="black")
                    # Track.yticks(y=rangeval, labels=rangeval,vmin=minval, vmax=maxval, side="left", tick_length=1, 
                    #          label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                if sector.name == "Mean":
                    innerText = sector.add_track((0, 0), r_pad_ratio=0.1)
                    innerText.axis(ec = "none")
                    innerText.text(centertext, x = innerText.start, color="black", adjust_rotation=False, orientation="horizontal" ,size=14)

         # Create legend
        legend_elements = []
        legend_elements.append(Line2D([0], [0], color="red", marker='o', lw=0, label=f"Exposure Before Intervention"))
        legend_elements.append(Line2D([0], [0], color="black", marker='o', lw=0, label=f"Exposure After Intervention"))
        figure = circos.plotfig(dpi=600)
        figure.legend(handles=legend_elements, loc='lower right', ncol=1, title = "Legend")
        figure.savefig(f"CirclePlot_{outcomevar}_Subgroups_{suffix}.png", dpi=600)

def PlotPerNeighbOutcome(outcomvar, showplots, modelrun, spatialdata, distance_meters, vmax = None, vmin= None, outcomelabel = None):
    if outcomelabel is None:
        outcomelabel = outcomvar
    ax = spatialdata.plot(outcomvar, antialiased=False, legend = True, legend_kwds= {"label": outcomelabel, "location":"top", "shrink": 0.72,  "pad":0.03}, vmax = vmax, vmin = vmin)
    cx.add_basemap(ax, crs=spatialdata.crs, source=cx.providers.CartoDB.PositronNoLabels, attribution= False)
    ax.annotate("© OpenStreetMap contributors © CARTO", xy=(0.15, 0.1), xycoords="figure fraction", fontsize=6, color="dimgrey")
    scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
    ax.add_artist(scalebar)
    # plt.title(f"{outcomelabel} Per Neighborhood")
    plt.xticks(fontsize=7.5)
    plt.yticks(fontsize=7.5)
    plt.xlabel("Latitude (EPSG:28992)", fontsize=7.5)
    plt.ylabel("Longitude (EPSG:28992)", fontsize=7.5)
    plt.savefig(f'{modelrun}_neighbmap_{outcomvar}.png', dpi = 600, bbox_inches='tight', pad_inches=0.1)
    if showplots:
        plt.show()
    plt.close()

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/popsizes/"
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/samemodelrun/"

os.chdir(path_data)

# scenario = "StatusQuo"
scenario = "PrkPriceInterv"
# scenario = "15mCity"
# scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"


# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
# modelruns = [modelrun for modelrun in modelruns if not(modelrun in [786142])]
popsamples = [experimentoverview.loc[experimentoverview["Model Run"]== modelrun, "Population Sample"].values[0] for modelrun in modelruns]
# print(scenario, modelruns, popsamples)
# modelruns = [757283, 229107,107744, 943146,445545]
# popsamples = [0,0,0,0,0]
# print(scenario, modelruns, popsamples)
# modelruns = [ 786142]
# popsamples = [7]

viztype = [
        # "verticalExposureprep",
        # "methoursprep",
        "meanMEThoursstrat",
        "METneigh",
        "meanMEThoursstratdiff",
        "meanMETNeighdiff",
]


StatusQuomean = 21
Helbichmean = 14
RIVMLSMmean = 23

refactorization = 1  #  14/21


categoricalstratvars = ["sex", "migr_bck", "income_class", "age_group", "HH_size", "absolved_education", "HH_type", "student", "location"]
fullnamedict = {
    "income": "Income Decile: 1 low, 10 high",
    "sex": "sex",
    "migr_bck": "Migration Background",
    "income_class": "Income Group",
    "age_group": "Age Group",
    "HH_size": "Household Size",
    "absolved_education": "Education Level",
    "HH_type": "Household Type",
    "student": "Student Status",
    "location": "Location",
    "NO2": "NO2 (µg/m3)",
    "MET": "Metabolic Equivalent of Task (MET)",
    "NO2wFilter": "NO2 with O/I (µg/m3)",
    "indoortime": "Time spent indoors (min/h)",
    "NO2_diff": "NO2 Difference (µg/m3)",
    "MET_diff": "Metabolic Equivalent of Task (MET) Difference" }

subgroups_Meta = {"income": ["Low", "Medium", "High"],
            "sex": ["male", "female"], 
            "migration_background": ["Dutch", "Western", "Non-Western"],
            "age_group": ["Aged 0-29", "Aged 30-59", "Aged 60+"],
            "HH_size": ["HH size 1", "HH size 2", "HH size 3", "HH size 4", "HH size 5", "HH size 6", "HH size 7"],
            "absolved_education": ["low", "middle", "high"],
            "HH_type": ["Single Person", "Pair without children", "Pair with children", "Single Parent with children", "Other multiperson household"],
            "student": ["Student", "Not Student"],
            "location": ["inside ring", "outside ring"]
            }
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

innerring = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/SpatialData/NoEmissionZone2025.feather")
neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
innerringsneighborhoods = innerring.sjoin(neighborhoods, how="inner", predicate='intersects')
innerringsneighborhoods = list(innerringsneighborhoods["buurtcode"].values)

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


if "verticalExposureprep" in viztype:
    for modelrun in modelruns:
        # read exposure data
        os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}")
        listOfFiles = os.listdir(path=os.getcwd())
        if "ExposureViz" in listOfFiles:
            listOfFiles.remove("ExposureViz")
        print(listOfFiles)
        for count, file in enumerate(listOfFiles):
            exposure_df = pd.read_csv(file)
            filesplit = file.split("_")
            print(filesplit)
            if count == 0:
                exposure_df["day"] = filesplit[4][1:]
                exposure_df["month"] = filesplit[3][1:]
                exposure_df["hour"] = filesplit[5][1:]
                exposure_df_vertical = exposure_df
            else:
                exposure_df["day"] = filesplit[4][1:]
                exposure_df["month"] = filesplit[3][1:]
                exposure_df["hour"] = filesplit[5][1:]
                exposure_df_vertical = pd.concat([exposure_df_vertical, exposure_df], axis=0)
        exposure_df_vertical = exposure_df_vertical.rename(columns={"agent": "agent_ID"})
        if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz"):
            # Create the directory
            os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz")
        os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz")
        exposure_df_vertical.to_csv(f"MarginalMET_A{nb_agents}_{modelrun}_verticalAsRows.csv", index=False)


if "methoursprep" in viztype:
    for count, modelrun in enumerate(modelruns):
        print(f"Model run {modelrun}")
        os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz")
        print("Reading the data")
        exposure_df_vertical = pd.read_csv(f"MarginalMET_A{nb_agents}_{modelrun}_verticalAsRows.csv")
        
        exposure_df_vertical["date"] = [f"{daymonth[0]}-{daymonth[1]}-2019" for daymonth in exposure_df_vertical[["day", "month"]].values]
        exposure_df_vertical['date'] = pd.to_datetime(exposure_df_vertical['date'], format='%d-%m-%Y', errors='coerce')
        exposure_df_vertical["weekday"] = exposure_df_vertical['date'].dt.day_name()
        exposure_df_vertical['weekday'] = pd.Categorical(exposure_df_vertical['weekday'], categories=days_order, ordered=True)
        exposure_df_vertical["MET"] = exposure_df_vertical["METtot"]
        
        dailyMEThours = pd.DataFrame(exposure_df_vertical[["agent_ID","weekday", "month", "MET"]].groupby(["agent_ID","weekday", "month"], as_index=False).sum())
        weeklyMEThours = pd.DataFrame(dailyMEThours[["agent_ID","month", "MET"]].groupby(["agent_ID","month"], as_index=False).sum())
        print(dailyMEThours.head())
        print(weeklyMEThours.head())
        
        agent_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/Amsterdam_population_subset{nb_agents}_{modelrun}_{popsamples[count]}.csv")
        
        print("Merging the data DailyMEThours")
        exposure_df_vertical = pd.merge(agent_df, dailyMEThours, on="agent_ID", how="right")

        # Renaming some columns for elegance
        exposure_df_vertical = exposure_df_vertical.rename(columns={"incomeclass_int": "income", "migrationbackground": "migr_bck"})
        exposure_df_vertical["income"] = exposure_df_vertical["income"].astype(int)
        # restructuring data
        exposure_df_vertical["income_class"]=exposure_df_vertical["income"].apply(lambda x: "Low" if x in range(1,5) else ("Medium" if x in range(5,9) else "High"))
        # 1 low # 10 high
        # restructuring age into groups
        exposure_df_vertical["age_group"]=exposure_df_vertical["age"].apply(lambda x: "Aged 0-29" if x in range(0,30) else ("Aged 30-59" if x in range(30,60) else "Aged 60+"))    
        # renaming binary student variable
        exposure_df_vertical["student"] = exposure_df_vertical["student"].replace({1: "Student", 0: "Not Student"})

        
        # creating HH type from multiple hh variables
        exposure_df_vertical["HH_type"] = ""
        # exposure_df_vertical["Nrchildren"] = exposure_df_vertical["Nrchildren"].astype(int)
        exposure_df_vertical["Nr_adults"] = exposure_df_vertical["HH_size"] - exposure_df_vertical["Nrchildren"]
        exposure_df_vertical.loc[exposure_df_vertical["hh_single"]==1, "HH_type"] = "Single Person"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]==2) & (exposure_df_vertical["havechild"] == 0), "HH_type"] = "Pair without children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>2) & (exposure_df_vertical["havechild"] == 1), "HH_type"] = "Pair with children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>=2) & (exposure_df_vertical["havechild"] == 1) & (exposure_df_vertical["Nr_adults"]==1), "HH_type"] = "Single Parent with children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>=2) & (exposure_df_vertical["Nr_adults"]>2), "HH_type"] = "Other multiperson household"
                
        # make hh_size into a categorical variable
        exposure_df_vertical["HH_size"] = [f"HH size {hhsize}" for hhsize in exposure_df_vertical["HH_size"]]
        continuousstratvars = ["income"]
        
        exposure_df_vertical["location"] = "outside ring"
        exposure_df_vertical.loc[exposure_df_vertical["neighb_code"].isin(innerringsneighborhoods), "location"] = "inside ring"

        print("Creating an aggregate dataset")
        timeunits = ["weekday", "month"]
        outcomevars = ["MET"]
        aggexposure = exposure_df_vertical[outcomevars].mean().values
        aggexposure = pd.DataFrame([["total"]+list(aggexposure)], columns=["timeunit"]+outcomevars)
        print(aggexposure)
        for timeunit in timeunits:
            timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit]+outcomevars].groupby(timeunit, as_index=False).mean())
            timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
            print(timeunitexposure.head())
            aggexposure = pd.concat([aggexposure, timeunitexposure[["timeunit"]+outcomevars]], axis=0, ignore_index=True)
            print(aggexposure.head(30))   

        aggexposure.index = aggexposure["timeunit"]
        for strativar in categoricalstratvars:
            stratexposure = pd.DataFrame(exposure_df_vertical[[strativar]+outcomevars].groupby(strativar, as_index=False).mean())
            stratexposure["timeunit"] = "total"
            stratexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=stratexposure)
            stratcol = [f"{col[0]}_{col[1]}" for col in stratexposure.columns]
            stratexposure.columns = stratcol
            print(stratexposure.head())
            aggexposure[stratcol] = None
            aggexposure.loc[aggexposure["timeunit"] == "total", stratcol] = stratexposure[stratcol]
            for timeunit in timeunits:
                timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit, strativar]+outcomevars].groupby([timeunit, strativar], as_index=False).mean())
                timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
                timeunitexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=timeunitexposure)
                timeunitexposure.columns = stratcol
                print(timeunitexposure.head())
                aggexposure.loc[timeunitexposure.index, stratcol] = timeunitexposure[stratcol]
                print(aggexposure.head(30))
            
        aggexposure.to_csv(f"DailyMEThours_A{nb_agents}_{modelrun}_aggregate.csv", index=False)

        print("Merging the data WeeklyMEThours")
        exposure_df_vertical = pd.merge(agent_df, weeklyMEThours, on="agent_ID", how="right")

        # Renaming some columns for elegance
        exposure_df_vertical = exposure_df_vertical.rename(columns={"incomeclass_int": "income", "migrationbackground": "migr_bck"})
        exposure_df_vertical["income"] = exposure_df_vertical["income"].astype(int)
        # restructuring data
        exposure_df_vertical["income_class"]=exposure_df_vertical["income"].apply(lambda x: "Low" if x in range(1,5) else ("Medium" if x in range(5,9) else "High"))
        # 1 low # 10 high
        # restructuring age into groups
        exposure_df_vertical["age_group"]=exposure_df_vertical["age"].apply(lambda x: "Aged 0-29" if x in range(0,30) else ("Aged 30-59" if x in range(30,60) else "Aged 60+"))    
        # renaming binary student variable
        exposure_df_vertical["student"] = exposure_df_vertical["student"].replace({1: "Student", 0: "Not Student"})

        
        # creating HH type from multiple hh variables
        exposure_df_vertical["HH_type"] = ""
        # exposure_df_vertical["Nrchildren"] = exposure_df_vertical["Nrchildren"].astype(int)
        exposure_df_vertical["Nr_adults"] = exposure_df_vertical["HH_size"] - exposure_df_vertical["Nrchildren"]
        exposure_df_vertical.loc[exposure_df_vertical["hh_single"]==1, "HH_type"] = "Single Person"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]==2) & (exposure_df_vertical["havechild"] == 0), "HH_type"] = "Pair without children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>2) & (exposure_df_vertical["havechild"] == 1), "HH_type"] = "Pair with children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>=2) & (exposure_df_vertical["havechild"] == 1) & (exposure_df_vertical["Nr_adults"]==1), "HH_type"] = "Single Parent with children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>=2) & (exposure_df_vertical["Nr_adults"]>2), "HH_type"] = "Other multiperson household"
                
        # make hh_size into a categorical variable
        exposure_df_vertical["HH_size"] = [f"HH size {hhsize}" for hhsize in exposure_df_vertical["HH_size"]]
        continuousstratvars = ["income"]
        
        exposure_df_vertical["location"] = "outside ring"
        exposure_df_vertical.loc[exposure_df_vertical["neighb_code"].isin(innerringsneighborhoods), "location"] = "inside ring"

        print("Creating an aggregate dataset")
        timeunits = [ "month"]
        outcomevars = ["MET"]
        aggexposure = exposure_df_vertical[outcomevars].mean().values
        aggexposure = pd.DataFrame([["total"]+list(aggexposure)], columns=["timeunit"]+outcomevars)
        print(aggexposure)
        for timeunit in timeunits:
            timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit]+outcomevars].groupby(timeunit, as_index=False).mean())
            timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
            print(timeunitexposure.head())
            aggexposure = pd.concat([aggexposure, timeunitexposure[["timeunit"]+outcomevars]], axis=0, ignore_index=True)
            print(aggexposure.head(30))   

        aggexposure.index = aggexposure["timeunit"]
        for strativar in categoricalstratvars:
            stratexposure = pd.DataFrame(exposure_df_vertical[[strativar]+outcomevars].groupby(strativar, as_index=False).mean())
            stratexposure["timeunit"] = "total"
            stratexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=stratexposure)
            stratcol = [f"{col[0]}_{col[1]}" for col in stratexposure.columns]
            stratexposure.columns = stratcol
            print(stratexposure.head())
            aggexposure[stratcol] = None
            aggexposure.loc[aggexposure["timeunit"] == "total", stratcol] = stratexposure[stratcol]
            for timeunit in timeunits:
                timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit, strativar]+outcomevars].groupby([timeunit, strativar], as_index=False).mean())
                timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
                timeunitexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=timeunitexposure)
                timeunitexposure.columns = stratcol
                print(timeunitexposure.head())
                aggexposure.loc[timeunitexposure.index, stratcol] = timeunitexposure[stratcol]
                print(aggexposure.head(30))
            
        aggexposure.to_csv(f"WeeklyMEThours_A{nb_agents}_{modelrun}_aggregate.csv", index=False)
        
        exposure_neigh = exposure_df_vertical[["neighb_code", "MET"]].groupby(["neighb_code"],  as_index=False).mean()
        exposure_df_vertical["count"]=1
        exposure_neigh_count = exposure_df_vertical[["neighb_code", "agent_ID", "count"]].drop_duplicates()[["neighb_code", "count"]].groupby(["neighb_code"],  as_index=False).sum()
        exposure_neigh= pd.merge(exposure_neigh, exposure_neigh_count, on="neighb_code", how="left")
        exposure_neigh.to_csv(f"Exposure_A{nb_agents}_{modelrun}_neigh.csv", index=False)


if "meanMEThoursstrat" in viztype:
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    print("Creating an aggregate time stratification dataset")
    print(modelruns, popsamples)
    aggexposure = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelruns[0]}/ExposureViz/DailyMEThours_A{nb_agents}_{modelruns[0]}_aggregate.csv")
    cols = aggexposure.columns[1:]
    for count, modelrun in enumerate(modelruns[1:]):
        aggexposure2 = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz/DailyMEThours_A{nb_agents}_{modelrun}_aggregate.csv")
        aggexposure[cols] = aggexposure[cols] + aggexposure2[cols]
    aggexposure[cols] = aggexposure[cols]/len(modelruns)
    aggexposure[cols] = aggexposure[cols]* refactorization
    aggexposure.to_csv(f"DailyMEThours_A{nb_agents}_Mean_{scenario}_aggregate.csv", index=False)    

    aggexposure = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelruns[0]}/ExposureViz/WeeklyMEThours_A{nb_agents}_{modelruns[0]}_aggregate.csv")
    cols = aggexposure.columns[1:]
    for count, modelrun in enumerate(modelruns[1:]):
        aggexposure2 = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz/WeeklyMEThours_A{nb_agents}_{modelrun}_aggregate.csv")
        aggexposure[cols] = aggexposure[cols] + aggexposure2[cols]
    aggexposure[cols] = aggexposure[cols]/len(modelruns)
    aggexposure[cols] = aggexposure[cols]* refactorization
    aggexposure.to_csv(f"WeeklyMEThours_A{nb_agents}_Mean_{scenario}_aggregate.csv", index=False)    



    subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "olive","greenyellow",  "lightseagreen", "green", "aqua", "maroon", "blue"]
    subgroupcolors = {stratgroup: subgroupcolorpalette[count] for count, stratgroup in enumerate(subgroups_Meta)}

    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    aggexposure = pd.read_csv(f"WeeklyMEThours_A{nb_agents}_Mean_{scenario}_aggregate.csv")
    weeklymean = aggexposure.loc[aggexposure["timeunit"]=="total", "MET"].values[0]
    outcomevar = "MET"
    aggexposure_subs = aggexposure.loc[aggexposure["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]]
    stratexposure_df = pd.DataFrame({f"{outcomevar}": [aggexposure_subs[f"{outcomevar}_{val}"].values for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]})
    stratexposure_df["Label"] = [val for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df["Group"] = [subgroup for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df[outcomevar] = [x[0] for x in stratexposure_df[outcomevar]]
    stratexposure_df[f"{outcomevar}_deviation"] = stratexposure_df[f"{outcomevar}"] - aggexposure.loc[aggexposure["timeunit"]=="total", outcomevar].values[0]
    stratexposure_df.rename(columns={"MET": "weeklyMEThours", "MET_deviation": "weeklyMEThours_deviation"}, inplace=True)
    stratexposure_df2 = stratexposure_df.copy()

    aggexposure = pd.read_csv(f"DailyMEThours_A{nb_agents}_Mean_{scenario}_aggregate.csv")
    dailymean = aggexposure.loc[aggexposure["timeunit"]=="total", "MET"].values[0]
    outcomevar = "MET"
    aggexposure_subs = aggexposure.loc[aggexposure["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]]
    stratexposure_df = pd.DataFrame({f"{outcomevar}": [aggexposure_subs[f"{outcomevar}_{val}"].values for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]})
    stratexposure_df["Label"] = [val for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df["Group"] = [subgroup for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df[outcomevar] = [x[0] for x in stratexposure_df[outcomevar]]
    stratexposure_df[f"{outcomevar}_deviation"] = stratexposure_df[f"{outcomevar}"] - aggexposure.loc[aggexposure["timeunit"]=="total", outcomevar].values[0]
    stratexposure_df.rename(columns={"MET": "dailyMEThours", "MET_deviation": "dailyMEThours_deviation"}, inplace=True)

    stratexposure_df = stratexposure_df.merge(stratexposure_df2, on=["Label", "Group"], how="inner")

    print(stratexposure_df.head(20))
    stratexposure_df.to_csv(f"METhours_A{nb_agents}_{scenario}_aggregate_strat.csv", index=False)


    subgroups_Meta["HH_type"] = ["Single Person", "Pair without\nchildren","Pair with\nchild(ren)", "Single Parent\nwith child(ren)", "Other\nmultiperson HH"]
    stratexposure_df["Label"] = stratexposure_df["Label"].replace({"Pair without children": "Pair without\nchildren",
                                                                    "Pair with children": "Pair with\nchild(ren)", 
                                                                    "Single Parent with children": "Single Parent\nwith child(ren)",
                                                                    "Other multiperson household": "Other\nmultiperson HH"})

    # drop the HH size stratification
    subgroups_Meta.pop("HH_size")

    if scenario == "StatusQuo":
        labelprefix = "Status Quo"
    else:
        labelprefix = "Scenario"


    
    print(stratexposure_df["dailyMEThours_deviation"].describe())
    print(stratexposure_df["weeklyMEThours_deviation"].describe())
    
    
    # dailyMEThoursrange = [-0.4, -0.2, 0, 0.2, 0.4]
    # weeklyMEThoursrange = [-2, -1, 0, 1, 2]
    
    # dailyMEThoursrange= [-0.8, -0.4, 0, 0.4, 0.8]
    # weeklyMEThoursrange = [-5, -2.5, 0, 2.5, 5]
    
    dailyMEThoursrange= [-0.8, -0.4, 0, 0.4, 0.8]
    weeklyMEThoursrange = [-6, -3, 0, 3, 6]
    
    # dailyMEThoursrange= [-0.5, -0.25, 0, 0.25, 0.5]
    # weeklyMEThoursrange = [-4, -2, 0, 2, 4]
    

    plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel="Scenario Mean Exposure\nacross population",
                        subgroupcolors = subgroupcolors, meanval= dailymean, rangeval=dailyMEThoursrange,
                        outcomevar = "dailyMEThours_deviation", roundval = 2, centertext=f"Daily\nMarginal Transport\nMET-hours\nDeviation\nfrom Mean", suffix = "")

    plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel="Scenario Mean Exposure\nacross population",
                        subgroupcolors = subgroupcolors, meanval= weeklymean,rangeval=weeklyMEThoursrange,
                        outcomevar = "weeklyMEThours_deviation", roundval = 2, centertext=f"Weekly\nMarginal Transport\nMET-hours\nDeviation\nfrom Mean", suffix = "")


if "METneigh" in viztype:
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    exposure_neigh = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelruns[0]}/ExposureViz/Exposure_A{nb_agents}_{modelruns[0]}_neigh.csv")
    exposure_neigh.sort_values("neighb_code", inplace=True)
    # rename columns with modelrun suffix
    exposure_neigh.columns = [exposure_neigh.columns.values[0]]+[f"{col}_0" for col in exposure_neigh.columns.values[1:]]    
    for count, modelrun in enumerate(modelruns[1:]):
        print(f"Adding data from modelrun {modelrun}")
        exposure_neigh2 = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz/Exposure_A{nb_agents}_{modelrun}_neigh.csv")
        exposure_neigh2.sort_values("neighb_code", inplace=True)
        exposure_neigh2.columns = [exposure_neigh2.columns.values[0]]+[f"{col}_{count+1}" for col in exposure_neigh2.columns.values[1:]]   
        exposure_neigh = exposure_neigh.merge(exposure_neigh2, on="neighb_code", how="outer")


    exposure_neigh["MET"] = exposure_neigh[[f"MET_{count}" for count in range(len(modelruns))]].mean(axis=1) 
    exposure_neigh["METrefactored"] = exposure_neigh["MET"] * refactorization
    exposure_neigh["totcount"] = exposure_neigh[[f"count_{count}" for count in range(len(modelruns))]].sum(axis=1)
    for count in range(len(modelruns)):
        exposure_neigh[f"weightedMET_{count}"] = (exposure_neigh[f"MET_{count}"]*exposure_neigh[f"count_{count}"]/exposure_neigh["totcount"]) 
    exposure_neigh["weightedMET"] = exposure_neigh[[f"weightedMET_{count}" for count in range(len(modelruns))]].sum(axis=1)
    exposure_neigh["weightedMETrefactored"] = exposure_neigh["weightedMET"] * refactorization
    
    print(exposure_neigh.head(20))
    exposure_neigh.to_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_neigh.csv", index=False)    
    exposure_neigh.rename(columns={"neighb_code": "buurtcode"}, inplace=True)

    outcomecols = exposure_neigh.columns[1:]
    observations = exposure_neigh[outcomecols[0:10]]
    exposure_neigh["samplecount"] = observations.count(axis=1)
    print(exposure_neigh["samplecount"].value_counts())

    # deleting neighborhoods where below 5 observations are available
    exposure_neigh = exposure_neigh.loc[exposure_neigh["totcount"]>10]
    exposure_neigh["MET"] = exposure_neigh["weightedMETrefactored"]
    
    
    print("Plotting mean status quo scenario exposure per neighborhood")

    crs = 28992    
    points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
    points = points.to_crs(32619)  # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])
    print(distance_meters)
    neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
    print(neighborhoods.columns)
    neighborhoods = neighborhoods.merge(exposure_neigh, on="buurtcode", how="left")

    fullnamedict["MET"] = "Marginal Transport METh/week"
    showplots = False

    print(f"Plotting the exposure stratification for MET")
    PlotPerNeighbOutcome(outcomvar="MET", showplots=showplots, modelrun="MeanAcrossRuns", 
                        spatialdata=neighborhoods, outcomelabel=fullnamedict["MET"], 
                        distance_meters=distance_meters)

if "meanMEThoursstratdiff" in viztype:
    # read dictionary from textfile
    with open(f"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\IntervRunDict_{scenario}.txt", "r") as f:
        IntervRunDict = eval(f.read())

    # IntervRunDict.pop(0.0)    
    print(IntervRunDict)
    keys = list(IntervRunDict)
    print(keys)
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    
    
    
    aggexposureStatusQ = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/UpdatedExposure/{IntervRunDict[keys[0]]['StatusQuo']}/ExposureViz/DailyMEThours_A{nb_agents}_{IntervRunDict[keys[0]]['StatusQuo']}_aggregate.csv")
    cols = aggexposureStatusQ.columns[1:]
    
    dailydifference = []
    weeklydifference = []
    for popsample in keys:
        dailyaggexposureStatusQ = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/UpdatedExposure/{IntervRunDict[popsample]['StatusQuo']}/ExposureViz/DailyMEThours_A{nb_agents}_{IntervRunDict[popsample]['StatusQuo']}_aggregate.csv")
        dailyaggexposureInterv = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{IntervRunDict[popsample][scenario]}/ExposureViz/DailyMEThours_A{nb_agents}_{IntervRunDict[popsample][scenario]}_aggregate.csv")
        dailydifference.append(dailyaggexposureInterv.loc[0,cols].values-dailyaggexposureStatusQ.loc[0,cols].values)
        
        weeklyaggexposureStatusQ = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/UpdatedExposure/{IntervRunDict[popsample]['StatusQuo']}/ExposureViz/WeeklyMEThours_A{nb_agents}_{IntervRunDict[popsample]['StatusQuo']}_aggregate.csv")
        weeklyaggexposureInterv = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/{IntervRunDict[popsample][scenario]}/ExposureViz/WeeklyMEThours_A{nb_agents}_{IntervRunDict[popsample][scenario]}_aggregate.csv")
        weeklydifference.append(weeklyaggexposureInterv.loc[0,cols].values -weeklyaggexposureStatusQ.loc[0,cols].values)
     
    print(dailydifference)
    
    difference_df = pd.DataFrame(dailydifference, columns=["daily"+ col for col in cols])
    difference_df2 = pd.DataFrame(weeklydifference, columns=["weekly"+ col for col in cols])
    difference_df = pd.concat([difference_df, difference_df2], axis=1)
    difference_df["popsamples"] = keys
    columns = difference_df.columns.tolist()
    columns = columns[-1:] + columns[:-1]
    difference_df = difference_df[columns]


    difference_df.to_csv(f"DifferenceMEThours_A{nb_agents}_Mean_{scenario}_aggregate_strat.csv", index=False)    


    subgroups_Meta = {"income": ["Low", "Medium", "High"],
                "sex": ["male", "female"], 
                "migration_background": ["Dutch", "Western", "Non-Western"],
                "age_group": ["Aged 0-29", "Aged 30-59", "Aged 60+"],
                "HH_size": ["HH size 1", "HH size 2", "HH size 3", "HH size 4", "HH size 5", "HH size 6", "HH size 7"],
                "absolved_education": ["low", "middle", "high"],
                "HH_type": ["Single Person", "Pair without children", "Pair with children", "Single Parent with children", "Other multiperson household"],
                "student": ["Student", "Not Student"],
                "location": ["inside ring", "outside ring"]
                }

    aggexposureStatusQ = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/UpdatedExposure/MeanExposureViz/WeeklyMEThours_A{nb_agents}_Mean_StatusQuo_aggregate.csv")
    aggexposure = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz/WeeklyMEThours_A{nb_agents}_Mean_{scenario}_aggregate.csv")

    outcomevar = "MET"
    aggexposure_subs = aggexposure.loc[aggexposure["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]]
    stratexposure_df = pd.DataFrame({f"{outcomevar}": [aggexposure_subs[f"{outcomevar}_{val}"].values for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]})
    stratexposure_df["Label"] = [val for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df["Group"] = [subgroup for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    aggexposure_StatQsubs = aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]]
    stratexposure_df[outcomevar] = [x[0] for x in stratexposure_df[outcomevar]]
    stratexposure_df[f"{outcomevar}_deviationStatQMean"] = stratexposure_df[f"{outcomevar}"] - aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", outcomevar].values[0]
    stratexposure_df[f"{outcomevar}_StatQ"] =[aggexposure_StatQsubs[f"{outcomevar}_{val}"].values[0] for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df[f"{outcomevar}_diffStatQ"] = stratexposure_df[f"{outcomevar}"] - stratexposure_df[f"{outcomevar}_StatQ"]
    stratexposure_df[f"{outcomevar}_StatQdevStatQMean"] = stratexposure_df[f"{outcomevar}_StatQ"]- aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", outcomevar].values[0]
    print(stratexposure_df.head(20))
    stratexposure_df.to_csv(f"WeeklyExposure_A{nb_agents}_{scenario}_aggregate_diff_strat.csv", index=False)

    
    subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "olive","blue", "green", "aqua", "maroon", "blue"]
    subgroupcolors = {stratgroup: subgroupcolorpalette[count] for count, stratgroup in enumerate(subgroups_Meta)}

    
    subgroups_Meta["HH_type"] = ["Single Person", "Pair without\nchildren","Pair with\nchild(ren)", "Single Parent\nwith child(ren)", "Other\nmultiperson HH"]
    stratexposure_df["Label"] = stratexposure_df["Label"].replace({"Pair without children": "Pair without\nchildren",
                                                                   "Pair with children": "Pair with\nchild(ren)", 
                                                                   "Single Parent with children": "Single Parent\nwith child(ren)",
                                                                   "Other multiperson household": "Other\nmultiperson HH"})
    subgroups_Meta.pop("HH_size")
    
    
    outcomevars = [ "MET"]
    oucomecentertextdicDevStatQ = {"MET": "Transport\nmarginal METh/week\nDeviation to\nStatus Quo Mean"}
    
    oucomecentertextdicDiffStatQ = {"MET": "Transport\nmarginal METh/week\nDifference to\nGroup StatQ Mean"}
    
    oucomecentertextdicChangeStatQ = { "MET": "Transport\nmarginal METh/week\nChange from\nStatus Quo"  }

   
    maxval = np.max(stratexposure_df[f"{outcomevar}_deviationStatQMean"])
    minval = np.min(stratexposure_df[f"{outcomevar}_deviationStatQMean"])
    print(f"DeviationStatQMean {outcomevar}:  Min value {minval}, Max value {maxval}")
   
    maxval = np.max(stratexposure_df[f"{outcomevar}_diffStatQ"])
    minval = np.min(stratexposure_df[f"{outcomevar}_diffStatQ"])
    print(f"DiffStatQ {outcomevar}:  Min value {minval}, Max value {maxval}")
    
   
    # # 15min city destination
    # outcomedeviationrangeStatQMean = [-14, -7, 0, 7, 14]
    # outcomedeviationrangeDiffStatQ = [-14, -7, 0, 7, 14]
    # outcomedeviationrangeStatQRelative = [-15, -10, -5, 0,5]

    # # no emission zone 2030
    # outcomedeviationrangeStatQMean = [-4, 0, 4, 8, 12]
    # outcomedeviationrangeDiffStatQ =[-4, 0, 4, 8, 12]
    # outcomedeviationrangeStatQRelative = [-4, 0, 4, 8, 12]
    
    # parking price
    outcomedeviationrangeStatQMean = [-3, 0, 3, 6, 9]
    outcomedeviationrangeDiffStatQ =[-0.11, 0, 0.11, 0.22, 0.33]
    outcomedeviationrangeStatQRelative = [-3, 0, 3, 6, 9]
   
    plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel="Status Quo Mean\nacross popoulation", rangeval = outcomedeviationrangeStatQMean,
                            subgroupcolors = subgroupcolors, meanval= aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", outcomevar].values[0],
                            outcomevar = f"{outcomevar}_deviationStatQMean", roundval = 2, centertext=oucomecentertextdicDevStatQ[outcomevar], suffix = "diff_StatQMean")

    plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel="Status Quo Mean\nof respective subgroup", rangeval = outcomedeviationrangeDiffStatQ,
                            subgroupcolors = subgroupcolors, meanval= aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", outcomevar].values[0],
                            outcomevar = f"{outcomevar}_diffStatQ", roundval = 2, centertext=oucomecentertextdicDiffStatQ[outcomevar], suffix = "diff_StatQ")

    plotCircosMeanStratRelativ(stratexposure_df, subgroups= subgroups_Meta, rangeval = outcomedeviationrangeStatQRelative,
                    subgroupcolors = subgroupcolors, 
                    meanvalStatQ= aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", outcomevar].values[0], 
                    meanvalScenario= aggexposure.loc[aggexposure["timeunit"]=="total", outcomevar].values[0],
                    redlinelabel="Mean across \n popoulation",
                    outcomevar = outcomevar, roundval = 2, centertext=oucomecentertextdicChangeStatQ[outcomevar], suffix = "diff_beforeafterStatQ")



if "meanMETNeighdiff" in viztype:
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz")
   
    exposure_neigh = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz/Exposure_A{nb_agents}_Mean_{scenario}_neigh.csv")
    exposure_neigh.rename(columns={"neighb_code": "buurtcode"}, inplace=True)
    exposure_neigh["MET"] = exposure_neigh["weightedMETrefactored"]
    
    exposure_neighStatusQ = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/UpdatedExposure/MeanExposureViz/Exposure_A{nb_agents}_Mean_StatusQuo_neigh.csv")
    exposure_neighStatusQ.rename(columns={"neighb_code": "buurtcode"}, inplace=True)
    exposure_neighStatusQ["MET"] = exposure_neighStatusQ["weightedMETrefactored"]

    exposure_neighDiff = exposure_neigh.copy()
    outcomecols = exposure_neigh.columns[1:]
    exposure_neighDiff[f"MET_diff"] = exposure_neigh[f"MET"] - exposure_neighStatusQ[f"MET"]
    
    exposure_neighDiff.to_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_neigh_diff.csv", index=False)
    exposure_neighDiff.rename(columns={"neighb_code": "buurtcode"}, inplace=True)
    exposure_neighDiff = exposure_neighDiff.loc[exposure_neighDiff["totcount"]>20]  
    print("Plotting mean status quo scenario exposure per neighborhood")
    crs = 28992    
    points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
    points = points.to_crs(32619)  # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])
    print(distance_meters)
    neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
    print(neighborhoods.columns)
    neighborhoods = neighborhoods.merge(exposure_neighDiff, on="buurtcode", how="left")

    fullnamedict["MET"] = "Difference in Marginal Transport METh/week"
    showplots = False

    print(f"Plotting the exposure stratification for MET")
    PlotPerNeighbOutcome(outcomvar="MET_diff", showplots=showplots, modelrun="MeanAcrossRuns", 
                        spatialdata=neighborhoods, outcomelabel=fullnamedict["MET"],
                        distance_meters=distance_meters)
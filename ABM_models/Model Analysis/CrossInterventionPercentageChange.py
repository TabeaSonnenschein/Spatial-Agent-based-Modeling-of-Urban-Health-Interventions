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


nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
os.chdir(path_data)
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")

scenarios = list(experimentoverview['Experiment'].unique())
scenarios.remove("PrkPriceIntervWithoutRemainderAdjust")
scenarios = ["PrkPriceInterv", "StatusQuo"]


personalNO2, personalNO2Filter, personalMET, Indoortime, NO2, Traffic, TrafficNO2  = [], [], [], [], [], [], []
DrivingShare, BikingShare, WalkingShare, PTShare = [], [], [], []
DrivingCount, BikingCount, WalkingCount, PTCount = [], [], [], []
Traveltime, Nrtrips, Nrtravelers = [], [], []

for scenario in scenarios:
    print(scenario)
    aggexposure = pd.read_csv(f"{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz/Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv")
    personalNO2.append(aggexposure.loc[aggexposure["timeunit"]== "total",'NO2'].values[0])
    personalNO2Filter.append(aggexposure.loc[aggexposure["timeunit"]== "total",'NO2wFilter'].values[0])
    Indoortime.append(aggexposure.loc[aggexposure["timeunit"]== "total",'indoortime'].values[0])
    aggMETexposure = pd.read_csv(f"{scenario}/{nb_agents}Agents/UpdatedExposure/MeanExposureViz/WeeklyMEThours_A{nb_agents}_Mean_{scenario}_aggregate.csv")
    personalMET.append(aggMETexposure.loc[aggexposure["timeunit"]== "total",'MET'].values[0])
    traffNO2df = pd.read_csv(f"{scenario}/{nb_agents}Agents/NO2/NO2Viz/NO2TraffMeansTime_{scenario}_MeanAcrossRuns_AmsterdamCityExtent.csv")
    NO2.append(traffNO2df.loc[traffNO2df["timeunit"]== "total",'NO2'].values[0])
    Traffic.append(traffNO2df.loc[traffNO2df["timeunit"]== "total",'Traffic'].values[0])
    TrafficNO2.append(traffNO2df.loc[traffNO2df["timeunit"]== "total",'TraffNO2'].values[0])
    durationdf = pd.read_csv(f"{scenario}/{nb_agents}Agents/Tracks/TrackViz/ModalSplitEnrichedSummary_{scenario}.csv")
    DrivingCount.append(durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly drive trips"].values[0])
    BikingCount.append(durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly bike trips"].values[0])
    WalkingCount.append(durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly walk trips"].values[0])
    PTCount.append(durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly transit trips"].values[0])
    DrivingShare.append((durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly drive trips"].values[0])/durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly Nr trips"].values[0])
    BikingShare.append((durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly bike trips"].values[0])/durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly Nr trips"].values[0])
    WalkingShare.append((durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly walk trips"].values[0])/durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly Nr trips"].values[0])
    PTShare.append((durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly transit trips"].values[0])/durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly Nr trips"].values[0])
    Traveltime.append(durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly travel duration"].values[0])
    Nrtrips.append(durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly Nr trips"].values[0])
    Nrtravelers.append(durationdf.loc[durationdf["Modelrun"]== "Mean", "Mean hourly Nr travelers"].values[0])
    

ScenarioResults = pd.DataFrame({"Scenario": scenarios, 
              "Personal NO2": personalNO2, 
              "Personal NO2 w. I/O Filter": personalNO2Filter,
              "Personal MET": personalMET, 
              "Time spent indoors": Indoortime,
              "NO2": NO2, 
              "Emitting Traffic": Traffic, 
              "TrafficNO2": TrafficNO2, 
              "Driving Count": DrivingCount,
              "Biking Count": BikingCount,
              "Walking Count": WalkingCount,
              "Transit Count": PTCount,
              "Driving Share": DrivingShare, 
              "Biking Share": BikingShare, 
              "Walking Share":WalkingShare, 
              "Transit Share": PTShare,
              "Mean Travel Time": Traveltime,
              "Mean Nr Trips": Nrtrips,
              "Mean Nr Travelers": Nrtravelers})

statusquo = ScenarioResults.loc[ScenarioResults['Scenario'] == "StatusQuo"]
outcomecols = ScenarioResults.columns[1:]
for column in outcomecols:
    ScenarioResults[f"{column} Difference"] = ScenarioResults[column] - statusquo[column].values[0]
for column in outcomecols:
    ScenarioResults[f"% {column} Change"] = (ScenarioResults[column] - statusquo[column].values[0])/statusquo[column].values[0]
for column in outcomecols:
    if "Share" in column:
        ScenarioResults[f"{column} Diff (% Change)"] = "\makecell[l]{"+(ScenarioResults[f"{column} Difference"]*100).round(2).astype(str) + "\\%\\\\(" + (ScenarioResults[f"% {column} Change"]*100).round(2).astype(str) + "\\%)}"
    else:
        ScenarioResults[f"{column} Diff (% Change)"] = "\makecell[l]{"+ScenarioResults[f"{column} Difference"].round(2).astype(str) + "\\\\(" + (ScenarioResults[f"% {column} Change"]*100).round(2).astype(str) + "\\%)}"

print(ScenarioResults)


ScenarioResults.to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ScenarioResultsOverviewFinalPrkPriceupdate.csv", index=False)
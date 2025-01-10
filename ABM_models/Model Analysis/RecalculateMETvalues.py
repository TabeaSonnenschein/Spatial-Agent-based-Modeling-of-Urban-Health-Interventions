import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
from shapely import LineString, Point
import geopandas as gpd
from shapely.wkt import loads
from shapely.ops import transform


####################################################

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns/"
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/samemodelrun/"
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/popsizes/"

# trackpath = "F:/ModelRuns/"
trackpath=path_data

os.chdir(path_data)
crs = "epsg:28992"

# scenario = "StatusQuo"
scenario = "PrkPriceInterv"
# scenario = "15mCity"
# scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"

# # identify model run for scenario
# experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
# experimentoverview = experimentoverview.loc[experimentoverview["fullrun"] == True]
# modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
# popsamples = [experimentoverview.loc[experimentoverview["Model Run"]== modelrun, "Population Sample"].values[0] for modelrun in modelruns]
# print(modelruns, popsamples)

modelruns = [786142]
popsamples = [7]

METvalues = {"bike":"5.8", #6.8, marginal 5.8 
             "walk":"2.5",  #3.5, marginal 2.5
             "transit":"0.75", #2.5, marginal 1.5/2 (50% walking to transit)
             "drive":"0"} #0, marginal 0

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure"):
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure")

destination = path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure"

for count, modelrun in enumerate(modelruns):
    print("Modelrun: ", modelrun)
    if not os.path.exists(destination+f"/{modelrun}"):
      os.mkdir(destination+f"/{modelrun}")

    agent_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/Amsterdam_population_subset{nb_agents}_{modelrun}_{popsamples[count]}.csv")
    runagents = pd.DataFrame(agent_df["agent_ID"])
    runagents.columns = ["agent"]

    observations= os.listdir(path=f"{trackpath}{scenario}/{nb_agents}Agents/Tracks/{modelrun}/")
    for observation in observations:
        trackdf = pd.read_csv(os.path.join(f"{trackpath}{scenario}/{nb_agents}Agents/Tracks/{modelrun}/" , observation))
        trackdf["METact"] = trackdf["mode"].str.replace("bike", METvalues["bike"]).str.replace("walk", METvalues["walk"]).str.replace("transit", METvalues["transit"]).str.replace("drive", METvalues["drive"]).str.replace("[", "").str.replace("]", "").str.replace("'", "")   
        trackdf["duration"] = trackdf["duration"].str.replace("[", "").str.replace("]", "").str.replace("'", "")
        agentswithmultitrips = trackdf["mode"].str.contains(",", na=False)
        # get the index of agents with multiple trips
        
        trackdf["METtot"] = 0.0
        trackdf.loc[~agentswithmultitrips, "METtot"] = (trackdf["METact"].loc[~agentswithmultitrips].astype(float) * trackdf["duration"].loc[~agentswithmultitrips].astype(float))/60
        trackdf["splittedMETact"] = trackdf["METact"].str.split(",")
        trackdf["splittedduration"] = trackdf["duration"].str.split(",")
        agentswithmultitrips = trackdf.loc[agentswithmultitrips].index
        trackdf.loc[agentswithmultitrips,"METtot"] = [sum([float(trackdf["splittedMETact"].iloc[i][j]) * float(trackdf["splittedduration"].iloc[i][j]) for j in range(len(trackdf["splittedMETact"].iloc[i]))])/60 for i in agentswithmultitrips]
        trackdf = runagents.merge(trackdf[["agent", "METtot"]], on="agent", how="left")
        trackdf = trackdf.fillna(0.0)
        newname = observation.replace("AllTracks", "MarginalMET")
        trackdf.to_csv(destination+f"/{modelrun}/{newname}", index=False)
        
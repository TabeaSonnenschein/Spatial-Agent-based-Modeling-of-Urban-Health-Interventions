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
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"
os.chdir(path_data)
crs = "epsg:28992"

# scenario = "StatusQuo"
scenario = "PrkPriceInterv"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
experimentoverview = experimentoverview.loc[experimentoverview["fullrun"] == True]
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
modelruns = [805895]
METvalues = {"bike":6.8, 
             "walk":3.5, 
             "transit":1.9, 
             "drive":1.65}

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure"):
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure")

destination = path_data+f"/{scenario}/{nb_agents}Agents/UpdatedExposure"

def reverse_geom(geom):
    def _reverse(x, y, z=None):
        if z:
            return x[::-1], y[::-1], z[::-1]
        return x[::-1], y[::-1]
    return transform(_reverse, geom)


for modelrun in modelruns:
    print("Modelrun: ", modelrun)
    if not os.path.exists(destination+f"/{modelrun}"):
      os.mkdir(destination+f"/{modelrun}")

    observations = os.listdir(path=f"F:/ModelRuns/{scenario}/Tracks/{modelrun}/")
    # nrtimexceeds = []
    # for observation in observations:
    #     trackdf = pd.read_csv(os.path.join(f"F:/ModelRuns/{scenario}/Tracks/{modelrun}/" , observation))
    #     trackdf["mode"] = trackdf["mode"].apply(lambda x: ast.literal_eval(x))
    #     trackdf["duration"] = trackdf["duration"].apply(lambda x:  ast.literal_eval(x))
    #     trackdf["travelMET"] = [sum([(METvalues[mode]*trackdf["duration"].iloc[row][count]) for count, mode in enumerate(modes)])  for row, modes in enumerate(trackdf["mode"])]
    #     trackdf["totTraveltime"] = [sum(trackdf["duration"].iloc[row]) for row in range(len(trackdf))]
    #     trackdf["traveltimefraction"] = trackdf["totTraveltime"]/60
    #     trackdf.loc[trackdf["traveltimefraction"] > 1, "traveltimefraction"] = 1
    #     trackdf["meanhourlyMET"] = (trackdf["travelMET"]/trackdf["totTraveltime"])*trackdf["traveltimefraction"]
    #     nrtimexceeds.append(len(trackdf["totTraveltime"] > 60))
        
    #     exposurefile = observation.replace("AllTracks", "AgentExposure")
    #     exposuredf = pd.read_csv(os.path.join(f"{path_data}/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}" , exposurefile))
    #     exposuredf["MET"] = 0.0
    #     for Agent in trackdf["agent"]:
    #         exposuredf.loc[exposuredf["agent"] == Agent, "MET"] = trackdf.loc[trackdf["agent"] == Agent, "meanhourlyMET"].values[0]
        
    #     exposuredf.to_csv(os.path.join(destination+f"/{modelrun}" , exposurefile), index=False)
        
    # pd.DataFrame({"file":observations, "nrtimexceeds":nrtimexceeds}).to_csv(os.path.join(destination+f"/{modelrun}" , "nrtimexceeds.csv"), index=False)
    
    
    trackdf = pd.read_csv(os.path.join(f"F:/ModelRuns/{scenario}/Tracks/{modelrun}/" , observations[5]))
    trackdf["geometry"] = trackdf["geometry"].apply(lambda x: LineString(loads(x.split("; "))[0]))
    print(trackdf["geometry"].iloc[0])
    print(reverse_geom(trackdf["geometry"].iloc[0]))
    reversegeom = reverse_geom(trackdf["geometry"].iloc[0])
    
    if "reversegeom" in locals():
        print("reversegeom exists")
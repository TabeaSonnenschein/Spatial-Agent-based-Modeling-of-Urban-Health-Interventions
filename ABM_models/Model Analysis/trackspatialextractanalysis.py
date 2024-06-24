import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
from shapely import LineString, Point
import geopandas as gpd
from shapely.wkt import loads
from itertools import chain


nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"
os.chdir(path_data)
crs = "epsg:28992"

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

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
modelruns = [708658]
modelruns = [921087]
modelruns = [612742]
modelruns = [107935]
modelruns = [416590]

spatialjointype = "trackintersect"

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz")
      
destination = path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz"

extractname = "parkingprice_interventionextent"

for modelrun in modelruns:
    tracksubset = pd.read_csv(f"{destination}/AllTracks_{scenario}_{modelrun}_{extractname}_{spatialjointype}.csv")
    modal_split = tracksubset.groupby(["Month", "Day", "Hour"]).count()["id"]
    modal_split = pd.DataFrame(modal_split)
    modal_split = modal_split.rename(columns={"id": "nr_travelers"})
    modal_split.to_csv(f"{destination}/ModalSplit_{scenario}_{modelrun}_{extractname}_{spatialjointype}.csv")
    modal_split = pd.read_csv(f"{destination}/ModalSplit_{scenario}_{modelrun}_{extractname}_{spatialjointype}.csv")
    for month in [1, 4,7,10]:
        for day in range(1,8):
            for hour in range(24):
                trackindices = (tracksubset["Month"] == month) & (tracksubset["Day"] == day) & (tracksubset["Hour"] == hour)
                trips = list(tracksubset[trackindices]["mode"])
                trips = list(chain.from_iterable([el.split(", ") for el in trips]))
                index=(modal_split["Month"] == month) & (modal_split["Day"] == day) & (modal_split["Hour"] == hour)
                modal_split.loc[index, "nr_trips"] = len(trips)
                modal_split.loc[index, "bike"] = trips.count("'bike'")
                modal_split.loc[index, "drive"] = trips.count("'drive'")
                modal_split.loc[index, "transit"] = trips.count("'transit'")
                modal_split.loc[index, "walk"] = trips.count("'walk'")
                durations = list(tracksubset["duration"].loc[trackindices])
                durations = list(chain.from_iterable([el.split(", ") for el in durations]))
                durations = [float(x) for x in durations]
                if len(durations) == 0:
                    modal_split.loc[index, "mean_duration"] = None
                else:
                    modal_split.loc[index, "mean_duration"] = sum(durations)/len(durations)
    
    
    
    
    modal_split.to_csv(f"{destination}/ModalSplit_{scenario}_{modelrun}_{extractname}_{spatialjointype}.csv", index=False)
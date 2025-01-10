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
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"
path_data = "F:/ModelRuns"
os.chdir(path_data)
crs = "epsg:28992"

scenario = "StatusQuo"
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
popsamples = [experimentoverview.loc[experimentoverview["Model Run"]== modelrun, "Population Sample"].values[0] for modelrun in modelruns]

destination = path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz"

values = []
for count, modelrun in enumerate(modelruns):
    print("Modelrun: ", modelrun)
    observations = os.listdir(path=f"{path_data}/{scenario}/{nb_agents}Agents/Tracks/{modelrun}")
    agent_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/Amsterdam_population_subset{nb_agents}_{modelrun}_{popsamples[count]}.csv")
    nr_travelers, nr_trips, bike, drive, transit, walk, mean_durations = [], [], [], [], [], [], []
    for observation in observations:
        print("Observation: ", observation)
        df = pd.read_csv(os.path.join(f"{path_data}/{scenario}/{nb_agents}Agents/Tracks/{modelrun}" , observation))
        df = df.merge(agent_df,  left_on="agent", right_on="agent_ID", how="left")
        df = df.loc[df["age"] >17]
        trips = list(df["mode"].apply(lambda x: x.replace("[", "").replace("]", "")))
        trips = list(chain.from_iterable([el.split(", ") for el in trips]))
        durations = list(df["duration"].apply(lambda x: x.replace("[", "").replace("]", "")))
        nr_travelers.append(len(df["agent"].unique()))
        nr_trips.append(len(trips))
        durations = list(chain.from_iterable([el.split(", ") for el in durations]))
        durations = [float(x) for x in durations]
        if len(durations) == 0:
            mean_durations.append(None)
        else:
            mean_durations.append(sum(durations)/len(durations))
        bike.append(trips.count("'bike'"))
        drive.append(trips.count("'drive'"))
        transit.append(trips.count("'transit'"))
        walk.append(trips.count("'walk'"))
        trips.count("'drive'")
        

    ADULTmodalsplit = pd.DataFrame({"nr_trips": nr_trips, "nr_travelers": nr_travelers, "duration": mean_durations,"bike": bike, 
                    "drive": drive, "transit": transit, "walk": walk})
    # add a row with the mean values per column
    ADULTmodalsplit.loc[len(ADULTmodalsplit.index), :] = [ADULTmodalsplit[col].mean() for col in ADULTmodalsplit.columns]
    print(ADULTmodalsplit.loc[len(ADULTmodalsplit.index)-1, :])
    values.append(ADULTmodalsplit.loc[len(ADULTmodalsplit.index)-1, :].values)
    ADULTmodalsplit.to_csv(f"{destination}/ADULTModalSplit_{scenario}_{modelrun}.csv", index=False)
    
# create a summary of the enriched modal split across all modelruns
ADULTmodalsplittot = pd.DataFrame(values, columns=ADULTmodalsplit.columns)
ADULTmodalsplittot["Modelrun"] = modelruns
ADULTmodalsplittot.to_csv(f"{destination}/ADULTModalSplit_tot_{scenario}.csv", index=False)
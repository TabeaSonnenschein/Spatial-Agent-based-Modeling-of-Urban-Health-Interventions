import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
from shapely import LineString, Point
import geopandas as gpd
from shapely.wkt import loads
from itertools import chain

####################################################

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"
path_data = "F:/ModelRuns"
os.chdir(path_data)
crs = "epsg:28992"

# scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
# scenario = "15mCity"
scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
# modelruns = [413719]
# modelruns = [700698, 895973, 958354]
# modelruns = [ 912787, 493519, 989597]

print(modelruns)

# spatialjointype = "origdest"
spatialjointype = "trackintersect"

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz")
      
destination = path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz"

spatial_extract = False

if spatial_extract:
    spatial_extract = gpd.read_file("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/parking/parkingprices_prepostintervention.shp")
    extractname = "parkingprice_interventionextent"
    # map the spatial extract to the same crs as the model data
    spatial_extract = spatial_extract.to_crs(crs)
    #plot the spatial extract
    plot = spatial_extract.plot()
    plot.set_title(f"Spatial Extract: {extractname}")
    plt.savefig(f"{destination}/SpatialExtract_{extractname}.png")
    plt.close()

    #plot on top of total extent
    tot_spatial_extent = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/SpatialData/SpatialExtent.feather")
    tot_spatial_extent = tot_spatial_extent.to_crs(crs)

    #plot the tot_spatial_extent but only the boundary
    plot = tot_spatial_extent.boundary.plot( color="black", linewidth=0.5)
    spatial_extract.plot(ax=plot, color="red")
    plt.savefig(f"{destination}/SpatialExtract_ontopTotExtent_{extractname}.png")
    plt.close()

    for modelrun in modelruns:
        print("Modelrun: ", modelrun)
        observations = os.listdir(path=f"{path_data}/{scenario}/{nb_agents}Agents/Tracks/{modelrun}")
        final_gdf = gpd.GeoDataFrame()
        for observation in observations:
            df = pd.read_csv(os.path.join(f"{path_data}/{scenario}/{nb_agents}Agents/Tracks/{modelrun}" , observation))
            df["Month"] = observation.split("_")[3][1:]
            df["Day"] = observation.split("_")[4][1:]
            df["Hour"] = observation.split("_")[5][1:]
            df["geometry"] = df["geometry"].apply(lambda x: LineString(loads(x.split("; ")[0])))
            df["origin"] = df["geometry"].apply(lambda x: str(x.coords[0]))
            df["dest"] = df["geometry"].apply(lambda x: str(x.coords[-1]))
            df["mode"] = df["mode"].apply(lambda x: x.replace("[", "").replace("]", ""))
            df["duration"] = df["duration"].apply(lambda x: x.replace("[", "").replace("]", ""))
            gdf = gpd.GeoDataFrame(df, geometry="geometry")
            final_gdf = pd.concat([final_gdf, gdf], ignore_index=True)
            final_gdf.reset_index(drop=True, inplace=True)
            
        # find entries of final_gdf where either origin or destination is located in spatial extract
        final_gdf.crs = crs
        final_gdf["id"] = final_gdf.index
        spatial_extract = spatial_extract.to_crs(crs)
        #  make spatial_extract to single polygon
        spatial_extract = spatial_extract.dissolve()
        
        if spatialjointype == "trackintersect":
            final_subset = gpd.sjoin(final_gdf, spatial_extract, how="inner", predicate="intersects")
            pd.DataFrame(final_subset).to_csv(f"{destination}/AllTracks_{scenario}_{modelrun}_{extractname}_{spatialjointype}.csv", index=False)
        
        
        if spatialjointype == "origdest":
            final_gdf["origin"] = final_gdf["origin"].apply(lambda x: ast.literal_eval(x))
            final_gdf["dest"] = final_gdf["dest"].apply(lambda x: ast.literal_eval(x))
            # point in polygon
            origindf = final_gdf[["origin", "id"]].copy()
            destdf = final_gdf[["dest", "id"]].copy()
            origindf["origin"] = origindf["origin"].apply(lambda x: Point(x))
            destdf["dest"] = destdf["dest"].apply(lambda x: Point(x))
            origindf = gpd.GeoDataFrame(origindf[["origin", "id"]], geometry="origin")
            destdf = gpd.GeoDataFrame(destdf[["dest", "id"]], geometry="dest")
            origindf.crs = crs
            destdf.crs = crs
            originsubset = gpd.sjoin(origindf, spatial_extract, how="inner", predicate="intersects")
            destsubset = gpd.sjoin(destdf, spatial_extract, how="inner", predicate="intersects")
            final_subset = final_gdf[(final_gdf["id"].isin(originsubset["id"])) | (final_gdf["id"].isin(destsubset["id"]))]
            pd.DataFrame(final_subset).to_csv(f"{destination}/AllTracks_{scenario}_{modelrun}_{extractname}_{spatialjointype}.csv", index=False)


        # save to file
        # pd.DataFrame(final_gdf).to_csv(f"{destination}/AllTracks_{scenario}_{modelrun}.csv", index=False)
        # final_gdf.to_feather(f"{destination}/AllTracks_{scenario}_{modelrun}.feather")

else:
    for modelrun in modelruns:
        print("Modelrun: ", modelrun)
        observations = os.listdir(path=f"{path_data}/{scenario}/{nb_agents}Agents/Tracks/{modelrun}")
        month, day, hour, nr_trips, bike, drive, transit, walk, mean_durations, nr_travelers = [], [], [], [], [], [], [], [], [], []
        for observation in observations:
            print("Observation: ", observation)
            df = pd.read_csv(os.path.join(f"{path_data}/{scenario}/{nb_agents}Agents/Tracks/{modelrun}" , observation))
            month.append(observation.split("_")[3][1:])
            day.append(observation.split("_")[4][1:])
            hour.append(observation.split("_")[5][1:])
            nr_travelers.append(len(df["agent"].unique()))
            trips = list(df["mode"].apply(lambda x: x.replace("[", "").replace("]", "")))
            trips = list(chain.from_iterable([el.split(", ") for el in trips]))
            durations = list(df["duration"].apply(lambda x: x.replace("[", "").replace("]", "")))
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

        pd.DataFrame({"Month": month, "Day": day, "Hour": hour, "Nr travelers": nr_travelers,
                      "nr_trips": nr_trips,  "duration": mean_durations,"bike": bike, 
                      "drive": drive, "transit": transit, "walk": walk}).to_csv(f"{destination}/ModalSplitEnriched_{scenario}_{modelrun}.csv", index=False)
            

    ### create a summary of the enriched modal split across all modelruns
    nr_trips, bike, drive, transit, walk, mean_durations, nr_travelers = [], [], [], [], [], [], []
    for modelrun in modelruns:  
        modal_split = pd.read_csv(f"{destination}/ModalSplitEnriched_{scenario}_{modelrun}.csv")
        modal_split["totduration"] = modal_split["nr_trips"] * modal_split["duration"]
        mean_durations.append(modal_split["totduration"].sum()/modal_split["nr_trips"].sum())
        nr_trips.append(modal_split["nr_trips"].mean())
        nr_travelers.append(modal_split["Nr travelers"].mean())
        bike.append(modal_split["bike"].mean())
        drive.append(modal_split["drive"].mean())
        transit.append(modal_split["transit"].mean())
        walk.append(modal_split["walk"].mean())
    
    AverageModalSplit = pd.DataFrame({"Modelrun": modelruns, "Mean hourly Nr trips": nr_trips, 
                                      "Mean hourly Nr travelers": nr_travelers,
                                      "Mean hourly travel duration": mean_durations, 
                                      "Mean hourly bike trips": bike,
                                      "Mean hourly drive trips": drive, 
                                      "Mean hourly transit trips": transit, 
                                      "Mean hourly walk trips": walk})
    # add the mean across all modelruns
    AverageModalSplit["Modelrun"] =  AverageModalSplit["Modelrun"].astype(str)
    AverageModalSplit.loc[len(AverageModalSplit.index), :] =   ["Mean"] +  [AverageModalSplit[col].mean() for col in AverageModalSplit.columns[1:]]

    AverageModalSplit.to_csv(f"{destination}/ModalSplitEnrichedSummary_{scenario}.csv", index=False)
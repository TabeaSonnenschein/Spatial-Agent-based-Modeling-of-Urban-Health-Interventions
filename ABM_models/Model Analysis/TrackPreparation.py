import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
from shapely import LineString, Point
import geopandas as gpd
from shapely.wkt import loads

####################################################

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"
os.chdir(path_data)
crs = "epsg:28992"

# scenario = "StatusQuo"
scenario = "PrkPriceInterv"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
modelruns = [543595]

# spatialjointype = "origdest"
spatialjointype = "trackintersect"

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz")
      
destination = path_data+f"/{scenario}/{nb_agents}Agents/Tracks/TrackViz"


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
        

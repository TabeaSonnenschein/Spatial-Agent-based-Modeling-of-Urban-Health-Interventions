import pandas as pd
import numpy as np
import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, Polygon
from routingpy.routers import MapboxOSRM
import time
import matplotlib.pyplot as plt
import random
import json

path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"
crs = "epsg:28992"
walking_speed = 85  # meters per minute
walking_time = 15  # minutes
walking_distance = walking_speed * walking_time  # meters


################################################
### Calculate isochrones for each EnvBehavDeterm cell
################################################
# EnvBehavDeterms = gpd.read_feather(path_data+"SpatialData/EnvBehavDeterminants.feather")
# print(EnvBehavDeterms.columns)
# # calculate centroids

# Centroids = EnvBehavDeterms["geometry"].centroid
# Centroids = gpd.GeoDataFrame( EnvBehavDeterms["Intid"], geometry=Centroids, crs=crs)
# print(Centroids.head())

# keys = ["pk.eyJ1IjoidHNvbm5lbnMiLCJhIjoiY2x4b3dvcm00MDRxcDJqcXNqdWp6c3Q3MCJ9.qDaqQCtsIJuM29iOB8WXiA",
#          "pk.eyJ1IjoidHNvbm5lbnMiLCJhIjoiY2x4b3d1cjAyMGcwYzJwc2g5c3ltY2NlcCJ9.uFM2ONNvHZmgz2lmTgsLgA",
#          "pk.eyJ1IjoidHNvbm5lbnMiLCJhIjoiY2x4b3hpamRtMDlyeDJxcXlzZHB3OWRkaSJ9.RDm7EnZy1AkCOnSJb11c4w"]


# def mb_isochrone(gdf, timeintervals = [15], profile = "walking", keys = keys):

#     # Grab X and Y values in 4326
#     gdf['LON_VALUE'] = gdf.to_crs(4326).geometry.x
#     gdf['LAT_VALUE'] = gdf.to_crs(4326).geometry.y

#     coordinates = gdf[['LON_VALUE', 'LAT_VALUE']].values.tolist()

#     # Build a list of shapes
#     isochrone_shapes = []

#     if type(timeintervals) is not list:
#         timeintervals = [timeintervals]

#     # Use minutes as input, but the API requires seconds
#     time_seconds = [60 * x for x in timeintervals]

#     # Given the way that routingpy works, we need to iterate through the list of 
#     # coordinate pairs, then iterate through the object returned and extract the 
#     # isochrone geometries.  
#     mb = MapboxOSRM(api_key =keys[0])
#     x =0
#     for count,c in enumerate(coordinates):
#         iso_request = mb.isochrones(locations = c, profile = profile,
#                                     intervals = time_seconds, polygons = "true")

#         for i in iso_request:
#             iso_geom = Polygon(i.geometry[0])
#             isochrone_shapes.append(iso_geom)
#         if (count % 300 == 0) and (count != 0):
#             print(f"Processed {count} of {len(coordinates)} switching to next key")
#             x = x +1
#             if x == len(keys):
#                 x = 0
#             mb = MapboxOSRM(api_key =keys[x])

#             if (count % 900 == 0) and (count != 0):
#                 # wait for 60 seconds to avoid rate limiting
#                 print(f"Processed {count} of {len(coordinates)}, now waiting for 60 seconds to avoid rate limiting")
#                 time.sleep(60)

#     # Here, we re-build the dataset but with isochrone geometries

#     time_col = timeintervals * len(gdf)
#     # We'll need to repeat the dataframe to account for multiple time intervals
#     df_values_rep = pd.DataFrame(np.repeat(gdf["Intid"].values, len(time_seconds), axis = 0))
#     df_values_rep.columns = ["Intid"]

#     isochrone_gdf = gpd.GeoDataFrame(
#         data = df_values_rep,
#         geometry = isochrone_shapes,
#         crs = 4326
#     )

#     isochrone_gdf['time'] = time_col

#     # We are sorting the dataframe in descending order of time to improve visualization
#     # (the smallest isochrones should go on top, which means they are plotted last)
#     isochrone_gdf = isochrone_gdf.sort_values('time', ascending = False)

#     return(isochrone_gdf)

# isochronegdf = mb_isochrone(Centroids, timeintervals = [walking_time], profile = "walking")
# isochronegdf = isochronegdf.to_crs(crs)
# isochronegdf.to_feather(path_data+f"SpatialData/Isochrones{walking_time}m.feather")


#####################################################
### identify relevant isochrones for agent residences
#####################################################
# # read data
# isochronegdf = gpd.read_feather(path_data+f"SpatialData/Isochrones{walking_time}m.feather")
# Residences = gpd.read_feather(path_data+"SpatialData/Residences.feather")
# pop_df = pd.read_csv(path_data+"Population/Agent_pop_clean.csv")

# # identify residences with agent neighbourhoods
# agentneighborhoods = pop_df["neighb_code"].drop_duplicates().values
# print(agentneighborhoods)

# agent_residences = Residences[Residences["nghb_cd"].isin(agentneighborhoods)]
# agent_residences.to_file("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/PotentialAgentResidences.shp", driver="ESRI Shapefile")

# # join EnvBehavDeterms with agent residences to identify Intids
# agent_residences = gpd.read_file("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/PotentialAgentResidences.shp")
# EnvBehavDeterms = EnvBehavDeterms.to_crs(crs)
# agent_residences = agent_residences.to_crs(crs)
# EnvBehavDeterms = gpd.sjoin(EnvBehavDeterms, agent_residences, how="inner", predicate="intersects")
# agent_envIntids = EnvBehavDeterms["Intid"].drop_duplicates()
# print(agent_envIntids)

# # identify isochrones that have agent_evIntids
# agent_isochrones = isochronegdf[isochronegdf["Intid"].isin(agent_envIntids)]
# agent_isochrones.to_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")


########################################################
### join the agent_isochrones with the POIs of city functions to identify the 15min city gaps
########################################################
# read data
necessaryAmenities = pd.read_csv("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/necessaryAmenities_withoutnames.csv")

agent_isochrones = gpd.read_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")
agent_isochrones = agent_isochrones.to_crs(crs)
# functions of the city
greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")
Schools = gpd.read_feather(path_data+"SpatialData/Schools.feather")
Supermarkets = gpd.read_feather(path_data+"SpatialData/Supermarkets.feather")
Universities = gpd.read_feather(path_data+"SpatialData/Universities.feather")
Kindergardens = gpd.read_feather(path_data+"SpatialData/Kindergardens.feather")
Restaurants = gpd.read_feather(path_data+"SpatialData/Restaurants.feather")
Entertainment = gpd.read_feather(path_data+"SpatialData/Entertainment.feather")
ShopsnServ = gpd.read_feather(path_data+"SpatialData/ShopsnServ.feather")
Nightlife = gpd.read_feather(path_data+"SpatialData/Nightlife.feather")
Professional = gpd.read_feather(path_data+"SpatialData/Profess.feather")


# retrieve unique necessaryAmenity["class"] values
amenityclasses = necessaryAmenities[["class", "count", "Data", "Foursquare"]].drop_duplicates()
amenityclasses = {amenityclasses["class"].iloc[x]:{"count": amenityclasses["count"].iloc[x], "Data": amenityclasses["Data"].iloc[x], "Foursquare": amenityclasses["Foursquare"].iloc[x] } for x in range(len(amenityclasses))}
for amenityclass in amenityclasses.keys():
    venueids = necessaryAmenities.loc[necessaryAmenities["class"] == amenityclass, "venueid"].values
    amenityclasses[amenityclass]["venueids"] = list(venueids)
print(amenityclasses)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

#save dictionary
with open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/NecessaryAmenities.json", "w") as f:
    json.dump(amenityclasses, f, cls=NpEncoder)



Data = [greenspace, Schools, Supermarkets, Universities, Kindergardens, Restaurants, Entertainment, ShopsnServ, Nightlife, Professional]

for count, amenity in enumerate(amenityclasses.keys()):
    # find a datafile with the name amenityclases[poi]["Data"]
    POIs = [df for df in Data if df.name == amenityclasses[amenity]["Data"]][0]
    if amenityclasses[amenity]["Foursquare"] == 1:
        # find the venueids
        venueids = amenityclasses[amenity]["venueids"]
        # filter the POIs with the venueids
        POIs = POIs.loc[POIs["venueid"].isin(venueids)]
    
    poiisochrones = gpd.sjoin(agent_isochrones, POIs, how="left", predicate="intersects")
    poiisochrones = poiisochrones.rename(columns={"index_right":amenity})
    print( poiisochrones[["Intid", amenity]].head(50))
    poiisochrones[amenity] = poiisochrones[amenity].apply(lambda x: 0 if np.isnan(x) else 1)
    print(len(poiisochrones), poiisochrones[["Intid", amenity]].head(50))
    
    # count the number of POIs in each isochrone
    poiisochrones = poiisochrones[["Intid", amenity]].groupby("Intid").agg({amenity:"sum"}).reset_index()
    print(len(poiisochrones), poiisochrones.head())
    print(poiisochrones[amenity].value_counts())
    agent_isochrones = agent_isochrones.merge(poiisochrones, on="Intid", how="left")
    
isochronepoifrequencies = agent_isochrones.drop(columns=["geometry"]).drop_duplicates()
isochronepoifrequencies.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv", index=False)



# POIs = [Schools, Supermarkets, Universities, Kindergardens, Restaurants, Entertainment, ShopsnServ, Nightlife, Professional, greenspace]
# POIs = [poi.to_crs(crs) for poi in POIs]
# POInames = ["Schools", "Supermarkets", "Universities", "Kindergardens", "Restaurants", "Entertainment", "ShopsnServ", "Nightlife", "Professional", "GreenSpace"]

# for poi in POIs:
#     #plot the POIs    
#     poi.plot()
#     plt.show()

# # print the type of file the POIs
# for poi in POIs:
#     print(type(poi))


# for count, poi in enumerate(POIs):
#     poiname = POInames[count]
#     print(poiname)
#     poiisochrones = gpd.sjoin(agent_isochrones, poi, how="left", predicate="intersects")
#     poiisochrones = poiisochrones.rename(columns={"index_right":poiname})
#     print( poiisochrones[["Intid", poiname]].head(50))
#     poiisochrones[poiname] = poiisochrones[poiname].apply(lambda x: 0 if np.isnan(x) else 1)
#     print(len(poiisochrones), poiisochrones[["Intid", poiname]].head(50))
    
#     # count the number of POIs in each isochrone
#     poiisochrones = poiisochrones[["Intid", poiname]].groupby("Intid").agg({poiname:"sum"}).reset_index()
#     print(len(poiisochrones), poiisochrones.head())
#     print(poiisochrones[poiname].value_counts())
#     agent_isochrones = agent_isochrones.merge(poiisochrones, on="Intid", how="left")
    
# isochronepoifrequencies = agent_isochrones.drop(columns=["geometry"]).drop_duplicates()
# isochronepoifrequencies.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv", index=False)



# ### calculate stats for the isochronepoifrequencies
# isochronepoifrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv")

# maxpois, maxpoithresholds, nr_cells_nopois, nr_cell_abovethresholds =[], [], [], []
 

# for poi in POInames:
#     isochronepoifrequencies[f"no_{poi}"] = isochronepoifrequencies[poi].apply(lambda x: 1 if x == 0 else 0)
#     maxnrpoi = isochronepoifrequencies[poi].max()
#     maxpois.append(maxnrpoi)
#     maxpoithreshold = int((maxnrpoi/3)*2)
#     maxpoithresholds.append(maxpoithreshold)
#     nr_cells_nopois.append(len(isochronepoifrequencies[isochronepoifrequencies[poi] == 0]))
#     if maxpoithreshold == 0:
#         isochronepoifrequencies[f"aboveTH_{poi}"] = 0
#         nr_cell_abovethreshold = 0
#     else:
#         isochronepoifrequencies[f"aboveTH_{poi}"] = isochronepoifrequencies[poi].apply(lambda x: 1 if x > maxpoithreshold else 0)
#         nr_cell_abovethreshold = len(isochronepoifrequencies[isochronepoifrequencies[poi] > maxpoithreshold])
#     nr_cell_abovethresholds.append(nr_cell_abovethreshold)
#     print(f"POI: {poi}, MaxPOIs: {maxnrpoi}, MaxPOIThreshold: {maxpoithreshold}, NrCellsNoPOIs: {nr_cells_nopois[-1]}, NrCellsAboveThreshold: {nr_cell_abovethresholds[-1]}")

# isochronepoifrequencies.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv", index=False)

# pd.DataFrame({"POI":POInames, "MaxPOIs":maxpois, 
#               "MaxPOIThreshold":maxpoithresholds, 
#               "NrCellsNoPOIs":nr_cells_nopois, 
#               "NrCellsAboveThreshold":nr_cell_abovethresholds}).to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv", index=False)
    

######################################################
######## fill the 15min city gaps
######################################################
# read data
necessaryAmenities = pd.read_csv("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/necessaryAmenities_withoutnames.csv")
agent_isochrones = gpd.read_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")
agent_isochrones = agent_isochrones.to_crs(crs)
greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")
Schools = gpd.read_feather(path_data+"SpatialData/Schools.feather")
Supermarkets = gpd.read_feather(path_data+"SpatialData/Supermarkets.feather")
Universities = gpd.read_feather(path_data+"SpatialData/Universities.feather")
Kindergardens = gpd.read_feather(path_data+"SpatialData/Kindergardens.feather")
Restaurants = gpd.read_feather(path_data+"SpatialData/Restaurants.feather")
Entertainment = gpd.read_feather(path_data+"SpatialData/Entertainment.feather")
ShopsnServ = gpd.read_feather(path_data+"SpatialData/ShopsnServ.feather")
Nightlife = gpd.read_feather(path_data+"SpatialData/Nightlife.feather")
Professional = gpd.read_feather(path_data+"SpatialData/Profess.feather")



# isochronePoistats = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv")
# isochronepoifrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv")
# POInames = ["Schools", "Supermarkets", "Universities","Kindergardens", "Restaurants", "Entertainment", "ShopsnServ", "Nightlife", "Professional"]
# POIs = [Schools, Supermarkets, Universities, Kindergardens, Restaurants, Entertainment, ShopsnServ, Nightlife, Professional]
# minnrs = [1,2,1,1,3,1,3,1,3,1]
# isochronePoistats["MinNrFacilities"] = minnrs
# isochronePoistats["NrNewFacilities"] = None

# print(agent_isochrones.columns)
# print(agent_isochrones.head(30))
# ## make agent_isochrones["Intid"] to int
# agent_isochrones["Intid"] = agent_isochrones["Intid"].astype(int)

# uniqueIntids = agent_isochrones["Intid"].drop_duplicates().values
# for count,poi in enumerate(POInames):
#     minnr = minnrs[count]
#     print(poi, "minnr", minnr)
#     lackingcells = isochronepoifrequencies.loc[isochronepoifrequencies[poi]<minnr, "Intid"].values
    
#     # sort lackingcells and greedycells randomly
#     random.shuffle(lackingcells)
    
#     newPOIs = gpd.GeoDataFrame()
#     for lackingcell in lackingcells:
#         isochrone = agent_isochrones.loc[agent_isochrones["Intid"] == lackingcell]
#         isochronestats = isochronepoifrequencies.loc[isochronepoifrequencies["Intid"] == lackingcell]
#         nrlacking = minnr - isochronestats[poi].values[0]
#         # print(isochronestats)
#         if (len(newPOIs) >0 )and (len(gpd.sjoin(isochrone,newPOIs, how = "inner",predicate="intersects")) >= nrlacking):
#             pass
#         else:
#             # create a random point in that isochrone
#             random_point = gpd.GeoSeries(isochrone["geometry"]).sample_points(nrlacking, random_state=1)
#             # add the point to the poi gdf
#             random_point = gpd.GeoDataFrame(geometry=random_point, crs=crs)
#             # add the point to POIs[count]
#             if len(newPOIs) == 0:
#                 newPOIs = random_point
#             else:
#                 newPOIs = pd.concat([newPOIs,random_point])
#     newPOIs = newPOIs.explode(ignore_index=True)
#     newPOIs["POI"] = poi
#     print(len(newPOIs ))
#     newPOIs.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mMissing{poi}.shp", driver="ESRI Shapefile")
#     isochronePoistats.loc[isochronePoistats["POI"] == poi, "NrNewFacilities"] = len(newPOIs)
    
#     greedycells = isochronepoifrequencies.loc[isochronepoifrequencies[poi] > minnr, ["Intid", poi]].sort_values(poi, ascending=False)["Intid"].values
#     POIs[count]["id"] = range(len(POIs[count]))
#     if len(greedycells) > len(newPOIs):
#         greedycells = greedycells[:len(newPOIs)]
#         greedyisochrones = agent_isochrones.loc[agent_isochrones["Intid"].isin(greedycells)]
#         busypois = list(gpd.sjoin(greedyisochrones, POIs[count], how = "inner", predicate="intersects")["id"].values)
#         execcessivePois = random.sample( busypois, len(newPOIs))
#         execcessivePois = POIs[count].loc[POIs[count]["id"].isin(execcessivePois)]
#         execcessivePois.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mExeccessive{poi}.shp", driver="ESRI Shapefile")
    
#     # remove exessivePOIs from the POIs
#     updatedPOIs = POIs[count].loc[~POIs[count]["id"].isin(execcessivePois["id"].values)]
    
#     updatedPOIs = pd.concat([updatedPOIs, newPOIs])
#     updatedPOIs.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdated{poi}.shp", driver="ESRI Shapefile")
    
    
################################################################
#### calculate updated amenity density and diversity
################################################################

# def entropy(mat):
#     row_sums = np.sum(mat, axis=1, keepdims=True)
#     freqs = mat / row_sums
#     entropy_values = -np.sum(freqs * np.log2(freqs + 1e-9), axis=1)
#     return np.round(entropy_values, decimals=3)


# EnvBehavDeterms = gpd.read_feather(path_data+"SpatialData/EnvBehavDeterminants.feather")
# isochronepoifrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv")
# print(EnvBehavDeterms.columns)
# EnvBehavDeterms[f'retaiDns{walking_time}'] = EnvBehavDeterms["retaiDns"]
# relevantids = list(isochronepoifrequencies["Intid"].values.astype(int))
# EnvBehavDeterms["Intid"] = EnvBehavDeterms["Intid"].astype(int)


# Entertainment = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedEntertainment.shp")
# Restaurants =gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedRestaurants.shp")
# Nightlife = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedNightlife.shp")
# ShopsnServ = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedShopsnServ.shp")

# # Combine data
# Fsq_retail = pd.concat([Entertainment, Restaurants, Nightlife, ShopsnServ]).drop_duplicates()
# Fsq_retail = Fsq_retail.explode(ignore_index=True)

# # Convert to GeoDataFrame
# Fsq_retail.crs = crs
# Fsq_retail_gridjoin = gpd.sjoin(Fsq_retail, EnvBehavDeterms, how="inner", predicate="intersects")

# # Calculate density
# for id in relevantids:
#     count = len(Fsq_retail_gridjoin[Fsq_retail_gridjoin['Intid'] == id])
#     EnvBehavDeterms.loc[EnvBehavDeterms['Intid'] == id, f'retaiDns{walking_time}'] = count

# print(EnvBehavDeterms.loc[EnvBehavDeterms["Intid"].isin(relevantids), [f'retaiDns{walking_time}', "retaiDns"]].head(30))

# # Save the result
# EnvBehavDeterms.to_file(path_data+f"SpatialData/EnvBehavDeterminants_{walking_time}mCity.shp", driver="ESRI Shapefile")
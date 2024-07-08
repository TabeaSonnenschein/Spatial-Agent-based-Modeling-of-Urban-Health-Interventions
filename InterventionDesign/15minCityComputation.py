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
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.patches as mpatches
from shapely.affinity import translate
from math import cos, sin, atan2

path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"
crs = "epsg:28992"
walking_speed = 85  # meters per minute
walking_time = 15  # minutes
walking_distance = walking_speed * walking_time  # meters


# ###############################################
# ## Calculate isochrones for each EnvBehavDeterm cell
# ###############################################
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


# ####################################################
# ## identify relevant isochrones for agent residences
# ####################################################
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


# #######################################################
# ## prepare the necessary Amenity dictionary
# #######################################################
# necessaryAmenities = pd.read_csv("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/necessaryAmenities_withoutnames.csv")
# amenityclasses = necessaryAmenities[["class", "count", "Data", "Foursquare"]].drop_duplicates()
# amenityclasses = {amenityclasses["class"].iloc[x]:{"count": amenityclasses["count"].iloc[x], "Data": amenityclasses["Data"].iloc[x], "Foursquare": amenityclasses["Foursquare"].iloc[x] } for x in range(len(amenityclasses))}
# for amenityclass in amenityclasses.keys():
#     venueids = necessaryAmenities.loc[necessaryAmenities["class"] == amenityclass, "venueid"].values
#     amenityclasses[amenityclass]["venueids"] = list(venueids)
# print(amenityclasses)

# class NpEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.integer):
#             return int(obj)
#         if isinstance(obj, np.floating):
#             return float(obj)
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()
#         return super(NpEncoder, self).default(obj)

# #save dictionary
# with open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/NecessaryAmenities.json", "w") as f:
#     json.dump(amenityclasses, f, cls=NpEncoder)

# #######################################################
# ## join the agent_isochrones with the POIs of city functions to identify the 15min city gaps
# #######################################################
# # # # read data
# amenityclasses = json.load(open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/NecessaryAmenities.json"))
# agent_isochrones = gpd.read_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")
# agent_isochrones = agent_isochrones.to_crs(crs)
# greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")
# Schools = gpd.read_feather(path_data+"SpatialData/Schools.feather")
# Supermarkets = gpd.read_feather(path_data+"SpatialData/Supermarkets.feather")
# Universities = gpd.read_feather(path_data+"SpatialData/Universities.feather")
# Kindergardens = gpd.read_feather(path_data+"SpatialData/Kindergardens.feather")
# Restaurants = gpd.read_feather(path_data+"SpatialData/Restaurants.feather")
# Entertainment = gpd.read_feather(path_data+"SpatialData/Entertainment.feather")
# ShopsnServ = gpd.read_feather(path_data+"SpatialData/ShopsnServ.feather")
# Nightlife = gpd.read_feather(path_data+"SpatialData/Nightlife.feather")
# Professional = gpd.read_feather(path_data+"SpatialData/Profess.feather")

# Data = [greenspace, Schools, Supermarkets, Universities, Kindergardens, Restaurants, Entertainment, ShopsnServ, Nightlife, Professional]
# names = ["greenspace", "Schools", "Supermarkets", "Universities", "Kindergardens", "Restaurants", "Entertainment", "ShopsnServ", "Nightlife", "Professional"]


# for count, amenity in enumerate(amenityclasses.keys()):
#     print(amenity)
#     POIs = Data[names.index(amenityclasses[amenity]["Data"])]
#     print(POIs)
#     if amenityclasses[amenity]["Foursquare"] == 1:
#         # find the venueids
#         venueids = amenityclasses[amenity]["venueids"]
#         # filter the POIs with the venueids
#         POIs = POIs.loc[POIs["catgryd"].isin(venueids)]
    
#     poiisochrones = gpd.sjoin(agent_isochrones, POIs, how="left", predicate="intersects")
#     poiisochrones = poiisochrones.rename(columns={"index_right":amenity})
#     # print( poiisochrones[["Intid", amenity]].head(50))
#     poiisochrones[amenity] = poiisochrones[amenity].apply(lambda x: 0 if np.isnan(x) else 1)
#     print(len(poiisochrones), poiisochrones[["Intid", amenity]].head(50))
    
#     # count the number of POIs in each isochrone
#     poiisochrones = poiisochrones[["Intid", amenity]].groupby("Intid").agg({amenity:"sum"}).reset_index()
#     # print(len(poiisochrones), poiisochrones.head())
#     print(poiisochrones[amenity].value_counts())
#     agent_isochrones = agent_isochrones.merge(poiisochrones, on="Intid", how="left")
    
# isochronepoifrequencies = agent_isochrones.drop(columns=["geometry"]).drop_duplicates()
# isochronepoifrequencies.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv", index=False)


# ### calculate stats for the isochronepoifrequencies
# amenityclasses = json.load(open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/NecessaryAmenities.json"))
# isochronepoifrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv")

# maxpois, maxpoithresholds, nr_cells_nopois, nr_cell_abovethresholds, nr_cell_belowmin, minthres =[], [], [], [], [], []
 

# for poi in amenityclasses.keys():
#     isochronepoifrequencies[f"no_{poi}"] = isochronepoifrequencies[poi].apply(lambda x: 1 if x == 0 else 0)
#     isochronepoifrequencies[f"belowmin_{poi}"] = isochronepoifrequencies[poi].apply(lambda x: 1 if x < amenityclasses[poi]["count"] else 0)
#     minthres.append(amenityclasses[poi]["count"])
#     maxnrpoi = isochronepoifrequencies[poi].max()
#     maxpois.append(maxnrpoi)
#     maxpoithreshold = int((maxnrpoi/3)*2)
#     maxpoithresholds.append(maxpoithreshold)
#     nr_cells_nopois.append(len(isochronepoifrequencies[isochronepoifrequencies[poi] == 0]))
#     nr_cell_belowmin.append(len(isochronepoifrequencies.loc[isochronepoifrequencies[f"belowmin_{poi}"] == 1]))
#     if maxpoithreshold == 0:
#         isochronepoifrequencies[f"aboveTH_{poi}"] = 0
#         nr_cell_abovethreshold = 0
#     else:
#         isochronepoifrequencies[f"aboveTH_{poi}"] = isochronepoifrequencies[poi].apply(lambda x: 1 if x > maxpoithreshold else 0)
#         nr_cell_abovethreshold = len(isochronepoifrequencies.loc[isochronepoifrequencies[poi] > maxpoithreshold])
#     nr_cell_abovethresholds.append(nr_cell_abovethreshold)
#     print(f"POI: {poi}, MaxPOIs: {maxnrpoi}, MaxPOIThreshold: {maxpoithreshold}, NrCellsNoPOIs: {nr_cells_nopois[-1]}, NrCellsAboveThreshold: {nr_cell_abovethresholds[-1]}")

# isochronepoifrequencies.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv", index=False)

# pd.DataFrame({"POI":amenityclasses.keys(), "MaxPOIs":maxpois, 
#               "MaxPOIThreshold":maxpoithresholds, 
#               "NrCellsNoPOIs":nr_cells_nopois, 
#               "NrCellsBelowMin":nr_cell_belowmin,
#               "MinThreshold":minthres,
#               "NrCellsAboveThreshold":nr_cell_abovethresholds}).to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv", index=False)
    

# ######################################################
# ######## fill the 15min city gaps
# # # ######################################################
# # read data
# amenityclasses = json.load(open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/NecessaryAmenities.json"))
# agent_isochrones = gpd.read_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")
# agent_isochrones = agent_isochrones.to_crs(crs)
# greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")
# Schools = gpd.read_feather(path_data+"SpatialData/Schools.feather")
# Supermarkets = gpd.read_feather(path_data+"SpatialData/Supermarkets.feather")
# Universities = gpd.read_feather(path_data+"SpatialData/Universities.feather")
# Kindergardens = gpd.read_feather(path_data+"SpatialData/Kindergardens.feather")
# Restaurants = gpd.read_feather(path_data+"SpatialData/Restaurants.feather")
# Entertainment = gpd.read_feather(path_data+"SpatialData/Entertainment.feather")
# ShopsnServ = gpd.read_feather(path_data+"SpatialData/ShopsnServ.feather")
# Nightlife = gpd.read_feather(path_data+"SpatialData/Nightlife.feather")
# Professional = gpd.read_feather(path_data+"SpatialData/Profess.feather")


# isochronePoistats = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv")
# isochronepoifrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv")
# Data = [greenspace, Schools, Supermarkets, Universities, Kindergardens, Restaurants, Entertainment, ShopsnServ, Nightlife, Professional]
# names = ["greenspace", "Schools", "Supermarkets", "Universities", "Kindergardens", "Restaurants", "Entertainment", "ShopsnServ", "Nightlife", "Professional"]
# isochronePoistats["NrNewFacilities"] = None
# isochronePoistats["RemovedFacilities"] = None

# print(agent_isochrones.columns)
# print(agent_isochrones.head(30))
# ## make agent_isochrones["Intid"] to int
# agent_isochrones["Intid"] = agent_isochrones["Intid"].astype(int)

# uniqueIntids = agent_isochrones["Intid"].drop_duplicates().values


# for count,amenity in enumerate(amenityclasses.keys()):
#     minnr = amenityclasses[amenity]["count"]
#     print(amenity, "minnr", minnr)
#     lackingcells = isochronepoifrequencies.loc[isochronepoifrequencies[amenity]<minnr, "Intid"].values
    
#     # sort lackingcells and greedycells randomly
#     random.shuffle(lackingcells)
#     newPOIs = gpd.GeoDataFrame()
#     for lackingcell in lackingcells:
#         isochrone = agent_isochrones.loc[agent_isochrones["Intid"] == lackingcell]
#         isochronestats = isochronepoifrequencies.loc[isochronepoifrequencies["Intid"] == lackingcell]
#         nrlacking = minnr - isochronestats[amenity].values[0]
#         # print(isochronestats)
#         if (len(newPOIs) >0 )and (len(gpd.sjoin(isochrone,newPOIs, how = "inner",predicate="intersects")) >0):
#             if len(gpd.sjoin(isochrone,newPOIs, how = "inner",predicate="intersects")) >= nrlacking:
#                 pass
#             else:
#                 nrlacking = nrlacking - len(gpd.sjoin(isochrone,newPOIs, how = "inner",predicate="intersects"))
#                 # create a random point in that isochrone
#                 random_point = gpd.GeoSeries(isochrone["geometry"]).sample_points(nrlacking, random_state=1)
#                 randomcatid = random.choices(amenityclasses[amenity]["venueids"], k=nrlacking)
#                 random_point = gpd.GeoDataFrame(geometry=random_point, crs=crs)
#                 if nrlacking > 1:
#                     random_point = random_point.explode(ignore_index=True)
#                 random_point["catgryd"] = randomcatid
#                 if len(newPOIs) == 0:
#                     newPOIs = random_point
#                 else:
#                     newPOIs = pd.concat([newPOIs,random_point])
#         else:
#             # create a random point in that isochrone
#             random_point = gpd.GeoSeries(isochrone["geometry"]).sample_points(nrlacking, random_state=1)
#             randomcatid = random.choices(amenityclasses[amenity]["venueids"], k=nrlacking)
#             random_point = gpd.GeoDataFrame(geometry=random_point, crs=crs)
#             if nrlacking > 1:
#                 random_point = random_point.explode(ignore_index=True)
#             random_point["catgryd"] = randomcatid
#             if len(newPOIs) == 0:
#                 newPOIs = random_point
#             else:
#                 newPOIs = pd.concat([newPOIs,random_point])
#     newPOIs = newPOIs.explode(ignore_index=True)
#     newPOIs["POI"] = amenity
#     print("added", len(newPOIs ))
#     newPOIs.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mMissing{amenity}.shp", driver="ESRI Shapefile")
#     isochronePoistats.loc[isochronePoistats["POI"] == amenity, "NrNewFacilities"] = len(newPOIs)
    
#     greedycells = isochronepoifrequencies.loc[isochronepoifrequencies[amenity] > minnr, ["Intid", amenity]].sort_values(amenity, ascending=False)["Intid"].values
#     POIs = Data[names.index(amenityclasses[amenity]["Data"])]
#     if amenityclasses[amenity]["Foursquare"] == 1:
#         # find the venueids
#         venueids = amenityclasses[amenity]["venueids"]
#         # filter the POIs with the venueids
#         POIs = POIs.loc[POIs["catgryd"].isin(venueids)]
        
#     POIs["id"] = range(len(POIs))
#     if len(greedycells) > len(newPOIs):
#         busypois = gpd.sjoin(agent_isochrones, POIs, how = "inner", predicate="intersects")        
#         greedystats = isochronepoifrequencies.loc[:, ["Intid",amenity]]
#         greedystats["capacity"] = greedystats[amenity] - minnr
#         excesspois = []
#         for cell in greedycells:
#             cellpois = busypois.loc[busypois["Intid"]==cell]
#             cellpois = cellpois.sample(frac=1)                
#             for cellpoi in cellpois["id"].values[:6]:
#                 if len(excesspois) < len(newPOIs):
#                     affectedcells = list(busypois.loc[busypois["id"] == cellpoi, "Intid"].values)
#                     if np.min(greedystats.loc[greedystats["Intid"].isin(affectedcells),"capacity"]) > 0:
#                         excesspois.append(cellpoi)
#                         greedystats.loc[greedystats["Intid"].isin(affectedcells), "capacity"] = greedystats.loc[greedystats["Intid"].isin(affectedcells), "capacity"] - 1
                
        
#         execcessivePois = POIs.loc[POIs["id"].isin(excesspois)]
#         execcessivePois.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mExeccessive{amenity}.shp", driver="ESRI Shapefile")
    
#     isochronePoistats.loc[isochronePoistats["POI"] == amenity, "RemovedFacilities"] = len(execcessivePois)
#     POIs.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs{amenity}_before.shp", driver="ESRI Shapefile")

#     # remove exessivePOIs from the POIs
#     updatedPOIs = POIs.loc[~POIs["id"].isin(execcessivePois["id"].values)]
#     updatedPOIs = pd.concat([updatedPOIs, newPOIs])
#     updatedPOIs = updatedPOIs.explode(ignore_index=True)
#     updatedPOIs.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdated{amenity}.shp", driver="ESRI Shapefile")
    
#     isochronePoistats.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv", index=False)



# # ################################################################
# # #### regroup the amenities in foursquare supercategories
# # # ###############################################################

# amenityclasses = json.load(open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/NecessaryAmenities.json"))
# ShopsnServ = gpd.read_feather(path_data+"SpatialData/ShopsnServ.feather")
# Professional = gpd.read_feather(path_data+"SpatialData/Profess.feather")

# print("ShopsServ", len(ShopsnServ), "Proff", len(Professional))

# Proffkeys = ["library", "medicalservice", "school", "community center", "postoffice", "policestation"]
# ShopsnServkeys = ["supermarket", "bike shop", "childcare", "pharmacy", "laundry", "bookstore", "publicbathroom", "market", "cashmachine"]

# for key in Proffkeys:
#     updatedPOIs = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdated{key}.shp")
#     Professional = Professional.loc[~Professional["catgryd"].isin(amenityclasses[key]["venueids"])]
#     Professional = pd.concat([Professional, updatedPOIs])
# Professional = Professional.explode(ignore_index=True)
# Professional.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedProfessional.shp", driver="ESRI Shapefile")

# for key in ShopsnServkeys:
#     updatedPOIs = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdated{key}.shp")
#     ShopsnServ = ShopsnServ.loc[~ShopsnServ["catgryd"].isin(amenityclasses[key]["venueids"])]
#     ShopsnServ = pd.concat([ShopsnServ, updatedPOIs])

# ShopsnServ = ShopsnServ.explode(ignore_index=True)
# ShopsnServ.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedShopsnServ.shp", driver="ESRI Shapefile")
# print("ShopsServ", len(ShopsnServ), "Proff", len(Professional))



# ##########################################################
# ## plot the changed amenity distributions
# ##########################################################

# amenityclasses = json.load(open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/NecessaryAmenities.json"))
# SpatialExtent = gpd.read_feather(path_data+"SpatialData/SpatialExtent.feather")

# names = {"library": "Libraries",
#          "school": "Schools",
#          "supermarket": "Supermarkets",
#          "bike shop": "Bike Repair/Shops",
#          "community center": "Community Centers",
#          "restaurants": "Restaurants",
#          "entertainment": "Arts & Entertainment Venues",
#          "medicalservice": "Medical Service",
#          "childcare": "Childcare Centers",
#          "pharmacy": "Pharmacies",
#          "nightlife": "Nightlife Venues",
#          "postoffice": "Post Offices",
#          "policestation": "Police Stations",
#          "laundry": "Laundry Services",
#          "bookstore": "Bookstores",
#         "publicbathroom": "Public Bathrooms",
#         "market": "Markets",
#         "cashmachine": "Cash Machines"
            
#          }

# crs = 28992    
# points = gpd.GeoSeries(
#     [Point(485000, 120000), Point(485001, 120000)], crs=crs
# )  # Geographic WGS 84 - degrees
# points = points.to_crs(32619)  # Projected WGS 84 - meters
# distance_meters = points[0].distance(points[1])

# for amenity in amenityclasses.keys():
#     print(amenity)
#     before = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs{amenity}_before.shp")
#     try:
#         removed = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mExeccessive{amenity}.shp")
#     except:
#         removed = None
#     after = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdated{amenity}.shp")
#     added = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mMissing{amenity}.shp")
    
#     ax = SpatialExtent.plot( color = None , edgecolor="grey", alpha= 0)
#     before.plot(ax = ax, color="black", markersize=1)
#     if removed is not None:
#         removed.plot(ax=ax, color="red", markersize=1)
#     cx.add_basemap(ax, crs=before.crs, source=cx.providers.CartoDB.PositronNoLabels)
#     scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
#     ax.add_artist(scalebar)
#     plt.title(f"{names[amenity]} before {walking_time}m city scenario")
#     black_patch = mpatches.Patch(color='black', label='Existing Maintained Facilities')
#     red_patch = mpatches.Patch(color='red', label='Removed Facilities')
#     plt.legend(handles=[black_patch, red_patch], loc = "lower left", bbox_to_anchor=(0, 0.03))
#     plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/{amenity.replace(' ', '')}{walking_time}mCityBefore.png", bbox_inches="tight", dpi=600)
#     plt.close()
    
#     ax = SpatialExtent.plot( color = None , edgecolor="grey", alpha= 0)
#     after.plot(ax = ax, color="black", markersize=1)
#     added.plot(ax=ax, color="blue", markersize=1)
#     cx.add_basemap(ax, crs=before.crs, source=cx.providers.CartoDB.PositronNoLabels)
#     scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
#     ax.add_artist(scalebar)
#     plt.title(f"{names[amenity]} after {walking_time}m city scenario")
#     black_patch = mpatches.Patch(color='black', label='Existing Maintained Facilities')
#     blue_patch = mpatches.Patch(color='blue', label='Added Facilities')
#     plt.legend(handles=[black_patch, blue_patch], loc = "lower left", bbox_to_anchor=(0, 0.03))
#     plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/{amenity.replace(' ', '')}{walking_time}mCityAfter.png", bbox_inches="tight", dpi=600)
#     plt.close()
    


# #######################################################################
# #### plot an isochrone
# ########################################################################
# EnvBehavDeterms = gpd.read_feather(path_data+"SpatialData/EnvBehavDeterminants.feather")
# print(EnvBehavDeterms.columns)
# Centroids = EnvBehavDeterms["geometry"].centroid
# Centroids = gpd.GeoDataFrame( EnvBehavDeterms["Intid"], geometry=Centroids, crs=crs)
# agent_isochrones = gpd.read_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")
# agent_isochrones = agent_isochrones.to_crs(crs)
# streets = gpd.read_feather(path_data+"SpatialData/Streets.feather")

# for x in range(5):
#     randomisochrone = agent_isochrones.sample(1)
#     isocentroid = Centroids.loc[Centroids["Intid"] == randomisochrone["Intid"].values[0]]
#     print(randomisochrone)
#     # isostreets = gpd.sjoin(streets, randomisochrone, how="inner", predicate="intersects")
#     # clip the streets to the isochrone
#     isostreets = gpd.clip(streets, randomisochrone)

#     crs = 28992    
#     points = gpd.GeoSeries(
#         [Point(485000, 120000), Point(485001, 120000)], crs=crs
#     )  # Geographic WGS 84 - degrees
#     points = points.to_crs(32619)  # Projected WGS 84 - meters
#     distance_meters = points[0].distance(points[1])

#     ax = randomisochrone.plot( color = "green" , edgecolor="grey", alpha= 0.2)
#     isostreets.plot(ax=ax, color="black", alpha=0.2)
#     isocentroid.plot(ax = ax, color="red", markersize=1)

#     cx.add_basemap(ax, crs=randomisochrone.crs, source=cx.providers.CartoDB.PositronNoLabels)
#     scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
#     ax.add_artist(scalebar)
#     plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/ExampleIsochrone{x}.png", bbox_inches="tight", dpi=600)
#     plt.close()





# ###############################################################
# ### calculate updated amenity density and diversity
# ###############################################################

# EnvBehavDeterms = gpd.read_feather(path_data+"SpatialData/EnvBehavDeterminants.feather")
# print(EnvBehavDeterms.columns  )


# isochronepoifrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIs.csv")
# print(EnvBehavDeterms.columns)
# EnvBehavDeterms[f'retaiDns{walking_time}'] = EnvBehavDeterms["retaiDns"]
# EnvBehavDeterms["Intid"] = EnvBehavDeterms["Intid"].astype(int)
# # relevant_ids = isochronepoifrequencies["Intid"].drop_duplicates().values

# Restaurants = gpd.read_feather(path_data+"SpatialData/Restaurants.feather")
# Entertainment = gpd.read_feather(path_data+"SpatialData/Entertainment.feather")
# ShopsnServ = gpd.read_feather(path_data+"SpatialData/ShopsnServ.feather")
# Nightlife = gpd.read_feather(path_data+"SpatialData/Nightlife.feather")
# Fsq_retail_before = pd.concat([Entertainment, Restaurants, Nightlife, ShopsnServ]).drop_duplicates()
# Fsq_retail_before = Fsq_retail_before.explode(ignore_index=True)
# Fsq_retail_before.crs = crs
# Fsq_retail_before_gridjoin = gpd.sjoin(Fsq_retail_before, EnvBehavDeterms, how="inner", predicate="intersects")


# Entertainment = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedentertainment.shp")
# Restaurants =gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedrestaurants.shp")
# Nightlife = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatednightlife.shp")
# ShopsnServ = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedShopsnServ.shp")

# # Combine data
# Fsq_retail_after = pd.concat([Entertainment, Restaurants, Nightlife, ShopsnServ]).drop_duplicates()
# Fsq_retail_after = Fsq_retail_after.explode(ignore_index=True)
# Fsq_retail_after.crs = crs
# Fsq_retail_after_gridjoin = gpd.sjoin(Fsq_retail_after, EnvBehavDeterms, how="inner", predicate="intersects")

# # Calculate density
# for id in EnvBehavDeterms["Intid"].values:
#     count_after = len(Fsq_retail_after_gridjoin[Fsq_retail_after_gridjoin['Intid'] == id])
#     count_before = len(Fsq_retail_before_gridjoin[Fsq_retail_before_gridjoin['Intid'] == id])
#     EnvBehavDeterms.loc[EnvBehavDeterms['Intid'] == id, f'retaiDns{walking_time}'] = count_after
#     EnvBehavDeterms.loc[EnvBehavDeterms['Intid'] == id, 'retaiDns'] = count_before

# print(EnvBehavDeterms.loc[:, [f'retaiDns{walking_time}', "retaiDns"]].head(30))
# print(EnvBehavDeterms[f'retaiDns{walking_time}'].value_counts())
# print(EnvBehavDeterms["retaiDns"].value_counts())

# # Save the result
# EnvBehavDeterms.to_file(path_data+f"SpatialData/EnvBehavDeterminants_{walking_time}mCity.shp", driver="ESRI Shapefile")


# # calculate diversity
# def entropy(mat):
#     row_sums = np.sum(mat, axis=1, keepdims=True)
#     freqs = mat / row_sums
#     entropy_values = -np.sum(freqs * np.log2(freqs + 1e-9), axis=1)
#     return np.round(entropy_values, decimals=3)

# def calculateRetailDiversity(gridjoin_df, categoryidcol="catgryd", uniqueidcol="Intid" ):
#     venuecategories = gridjoin_df[categoryidcol].unique()
#     uniqids = gridjoin_df[uniqueidcol].unique()
#     venuecat_matrix = np.zeros((len(uniqids), len(venuecategories)))
#     category_to_index = {category: idx for idx, category in enumerate(venuecategories)}
#     for category in venuecategories:
#         subset = gridjoin_df[gridjoin_df[categoryidcol] == category]
#         counts = subset[uniqueidcol].value_counts()
#         for unique_id, count in counts.items():
#             row_index = np.where(uniqids == unique_id)[0][0]
#             col_index = category_to_index[category]
#             venuecat_matrix[row_index, col_index] = count
#     uniqids_df = pd.DataFrame({uniqueidcol: uniqids})
#     uniqids_df['amen_entropy'] = entropy(venuecat_matrix)
#     return uniqids_df

# retailentropy_before = calculateRetailDiversity(Fsq_retail_before_gridjoin)
# retailentropy_after = calculateRetailDiversity(Fsq_retail_after_gridjoin)

# print(retailentropy_after)

# EnvBehavDeterms[f"retDiv{walking_time}"] = 0.0
# EnvBehavDeterms[f"retDivbef"] = 0.0
# for idx, row in retailentropy_before.iterrows():
#     unique_id = row['Intid']
#     entropy_value = row['amen_entropy']
#     EnvBehavDeterms.loc[EnvBehavDeterms['Intid'] == unique_id, 'retDivbef'] = entropy_value
    
# for idx, row in retailentropy_after.iterrows():
#     unique_id = row['Intid']
#     entropy_value = row['amen_entropy']
#     EnvBehavDeterms.loc[EnvBehavDeterms['Intid'] == unique_id, f'retDiv{walking_time}'] = entropy_value

# EnvBehavDeterms[f"retDivbef"] = EnvBehavDeterms[f"retDivbef"].fillna(0)
# EnvBehavDeterms[f"retDiv{walking_time}"] = EnvBehavDeterms[f"retDiv{walking_time}"].fillna(0)
# EnvBehavDeterms.loc[EnvBehavDeterms[f"retDivbef"] <0, f"retDivbef"] = 0
# EnvBehavDeterms.loc[EnvBehavDeterms[f"retDiv{walking_time}"] <0, f"retDiv{walking_time}"] = 0

# EnvBehavDeterms.to_file(path_data+f"SpatialData/EnvBehavDeterminants_{walking_time}mCity.shp", driver="ESRI Shapefile")


# ##################################################################
# ## plot the updated retail density and diversity #################
# ##################################################################
# EnvBehavDeterms = gpd.read_file(path_data+f"SpatialData/EnvBehavDeterminants_{walking_time}mCity.shp")
# crs = 28992
# EnvBehavDeterms.plot(column=f'retaiDns{walking_time}', cmap='viridis', vmax = 3, legend=True)
# plt.title(f'Retail Density {walking_time}m City')
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/retaildensity{walking_time}mCity.png", bbox_inches="tight", dpi=600)
# plt.close()

# EnvBehavDeterms.plot(column="retaiDns", cmap='viridis', vmax = 3, legend=True)
# plt.title('Retail Density')
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/retaildensityBefore.png", bbox_inches="tight", dpi=600)
# plt.close()

# EnvBehavDeterms.plot(column="retailDiv", cmap='viridis', vmax = 3, legend=True)
# plt.title('Retail Diversity')
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/retaildivBefore_old.png", bbox_inches="tight", dpi=600)
# plt.close()

# EnvBehavDeterms.plot(column="retDivbef", cmap='viridis', vmax = 3, legend=True)
# plt.title('Retail Diversity')
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/retaildivBefore.png", bbox_inches="tight", dpi=600)
# plt.close()

# EnvBehavDeterms.plot(column=f'retDiv{walking_time}', cmap='viridis', vmax = 3, legend=True)
# plt.title('Retail Diversity')
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/retaildiv{walking_time}mCity.png", bbox_inches="tight", dpi=600)
# plt.close()

# # ##################################################################################
# # ####### Add green space
# # ##################################################################################
# agent_isochrones = gpd.read_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")
# agent_isochrones = agent_isochrones.to_crs(crs)
# greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")
# greenspace = greenspace.explode(ignore_index=True)


# print("Calculating Greenspace Gaps")
# greenisochrones = gpd.sjoin(agent_isochrones, greenspace, how="left", predicate="intersects")
# greenisochrones = greenisochrones.rename(columns={"index_right":"greenspace"})
# greenisochrones["greenspace"] = greenisochrones["greenspace"].apply(lambda x: 0 if np.isnan(x) else 1)
# print(len(greenisochrones), greenisochrones[["Intid", "greenspace"]].head(50))

# # count the number of greenspaces in each isochrone
# greenisochrones = greenisochrones[["Intid", "greenspace"]].groupby("Intid").agg({"greenspace":"sum"}).reset_index()
# print(greenisochrones["greenspace"].value_counts())
# agent_isochrones = agent_isochrones.merge(greenisochrones, on="Intid", how="left")
    
# isochronegreenspacefrequencies = agent_isochrones.drop(columns=["geometry"]).drop_duplicates()
# isochronegreenspacefrequencies.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mGreenspace.csv", index=False)


# ### calculate stats for the isochronepoifrequencies
# isochronegreenspacefrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mGreenspace.csv")

# maxpois, maxpoithresholds, nr_cells_nopois, nr_cell_abovethresholds, nr_cell_belowmin, minthres =[], [], [], [], [], []
 
# poi = "greenspace"
# isochronegreenspacefrequencies[f"no_{poi}"] = isochronegreenspacefrequencies[poi].apply(lambda x: 1 if x == 0 else 0)
# isochronegreenspacefrequencies[f"belowmin_{poi}"] = isochronegreenspacefrequencies[poi].apply(lambda x: 1 if x < 1 else 0)
# minthres.append(1)
# maxnrpoi = isochronegreenspacefrequencies[poi].max()
# maxpois.append(maxnrpoi)
# maxpoithreshold = int((maxnrpoi/3)*2)
# maxpoithresholds.append(maxpoithreshold)
# nr_cells_nopois.append(len(isochronegreenspacefrequencies[isochronegreenspacefrequencies[poi] == 0]))
# nr_cell_belowmin.append(len(isochronegreenspacefrequencies.loc[isochronegreenspacefrequencies[f"belowmin_{poi}"] == 1]))
# if maxpoithreshold == 0:
#     isochronegreenspacefrequencies[f"aboveTH_{poi}"] = 0
#     nr_cell_abovethreshold = 0
# else:
#     isochronegreenspacefrequencies[f"aboveTH_{poi}"] = isochronegreenspacefrequencies[poi].apply(lambda x: 1 if x > maxpoithreshold else 0)
#     nr_cell_abovethreshold = len(isochronegreenspacefrequencies.loc[isochronegreenspacefrequencies[poi] > maxpoithreshold])
# nr_cell_abovethresholds.append(nr_cell_abovethreshold)
# print(f"POI: {poi}, MaxPOIs: {maxnrpoi}, MaxPOIThreshold: {maxpoithreshold}, NrCellsNoPOIs: {nr_cells_nopois[-1]}, NrCellsAboveThreshold: {nr_cell_abovethresholds[-1]}")

# isochronegreenspacefrequencies.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mGreenspace.csv", index=False)

# Greenstats = pd.DataFrame({"POI":["greenspace"], "MaxPOIs":maxpois, 
#               "MaxPOIThreshold":maxpoithresholds, 
#               "NrCellsNoPOIs":nr_cells_nopois, 
#               "NrCellsBelowMin":nr_cell_belowmin,
#               "MinThreshold":minthres,
#               "NrCellsAboveThreshold":nr_cell_abovethresholds})

# POIstats = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mPOIsStats.csv")
# POIstats = pd.concat([POIstats, Greenstats])
# print(POIstats)    

# POIstats.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv", index=False)

# # ################################################
# # ### Create Missing Greenspace
# # ################################################
# agent_isochrones = gpd.read_feather(path_data+f"SpatialData/AgentResidenceIsochrones{walking_time}m.feather")
# agent_isochrones = agent_isochrones.to_crs(crs)
# agent_isochrones["Intid"] = agent_isochrones["Intid"].astype(int)

# # greenspace = gpd.read_file("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Green Spaces/Green_Spaces_OSM_Amsterdam_dissolved.shp")
# greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")
# isochronegreenspacefrequencies = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mGreenspace.csv")
# POIstats = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv")

# crs = "epsg:28992"
# points = gpd.GeoSeries(
#         [Point(485000, 120000), Point(485001, 120000)], crs=crs
#     )  # Geographic WGS 84 - degrees
# points = points.to_crs(32619)  # Projected WGS 84 - meters
# distance_meters = points[0].distance(points[1])

# def create_random_polygon_within(isochrone, num_vertices=5, radius=50):
#     # Get the bounds of the isochrone
#     bounds = isochrone.bounds
#     minx, miny, maxx, maxy = bounds

#     # Create a random center point within the isochrone bounds
#     center = gpd.GeoSeries(isochrone).sample_points(size = 1, random_state=1)
#     center_x = center.geometry.x.values[0]
#     center_y = center.geometry.y.values[0]

#     # Create a random polygon around the center point
#     angles = sorted([random.uniform(0, 360) for _ in range(num_vertices)])
#     points = [
#         (
#             center_x + radius * random.uniform(0.5, 1) * cos(angle),
#             center_y + radius * random.uniform(0.5, 1) * sin(angle),
#         )
#         for angle in angles
#     ]
#     # sort the points so they form a polygon
#     points = sorted(points, key=lambda x: atan2(x[1] - center_y, x[0] - center_x)) 
    
#     polygon = Polygon(points)

#     return polygon

# def redoIfInvalidGeometryElseReturnDf(isochrone, crs,  num_vertices=5, radius=50):
#     polygon = create_random_polygon_within(isochrone, num_vertices=num_vertices, radius=radius)
#     polygon_df = gpd.GeoDataFrame(geometry=[polygon], crs=crs)
#     if polygon_df.is_valid.values[0]:
#         return polygon_df
#     else:
#         while not polygon_df.is_valid.values[0]:
#             polygon = create_random_polygon_within(isochrone, num_vertices=num_vertices, radius=radius)
#             polygon_df = gpd.GeoDataFrame(geometry=[polygon], crs=crs)
#         return polygon_df

# minnr = 1
# lackingcells = isochronegreenspacefrequencies.loc[isochronegreenspacefrequencies["greenspace"]<minnr, "Intid"].values
# random.shuffle(lackingcells)
# newPOIs = gpd.GeoDataFrame()
# for lackingcell in lackingcells:
#     isochrone = agent_isochrones.loc[agent_isochrones["Intid"] == lackingcell]
#     isochronestats = isochronegreenspacefrequencies.loc[isochronegreenspacefrequencies["Intid"] == lackingcell]
#     if (len(newPOIs) >0 )and (len(gpd.sjoin(isochrone,newPOIs, how = "inner",predicate="intersects")) >0):
#         pass
#     else:
#         random_polygon = redoIfInvalidGeometryElseReturnDf(isochrone["geometry"], radius = distance_meters*200, crs = crs)
#         if len(newPOIs) == 0:
#             newPOIs = random_polygon
#         else:
#             newPOIs = pd.concat([newPOIs,random_polygon])
# newPOIs["POI"] = "greenspace"
# print("added", len(newPOIs))
# newPOIs.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mMissingParks.shp", driver="ESRI Shapefile")
# POIstats.loc[POIstats["POI"] == "greenspace", "NrNewFacilities"] = len(newPOIs)
# POIstats.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mPOIsStats.csv", index=False)
# updatedgreenspace = pd.concat([greenspace, newPOIs])
# updatedgreenspace = updatedgreenspace.dissolve()
# updatedgreenspace.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedParks.shp", driver="ESRI Shapefile")

# greenspace = gpd.read_file("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Green Spaces/Green_Spaces_OSM_Amsterdam_dissolved.shp")
# updatedgreenspace = pd.concat([greenspace, newPOIs])
# updatedgreenspace = updatedgreenspace.dissolve()
# updatedgreenspace.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedGreenSpace.shp", driver="ESRI Shapefile")


# # ############################################################
# # #### Plot the changed Park Maps
# # ######################################
# crs = "epsg:28992"
# points = gpd.GeoSeries(
#         [Point(485000, 120000), Point(485001, 120000)], crs=crs
#     )  # Geographic WGS 84 - degrees
# points = points.to_crs(32619)  # Projected WGS 84 - meters
# distance_meters = points[0].distance(points[1])

# print("Plotting Greenspace before and after")
# SpatialExtent = gpd.read_feather(path_data+"SpatialData/SpatialExtent.feather")
# afterParks = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedParks.shp")
# afterGreenSpace = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mUpdatedGreenSpace.shp")
# added = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/AgentResidenceIsochrones{walking_time}mMissingParks.shp")


# ax = SpatialExtent.plot( color = None , edgecolor="grey", alpha= 0)
# afterParks.plot(ax = ax, color="green")
# added.plot(ax=ax, color="blue")
# cx.add_basemap(ax, crs=afterParks.crs, source=cx.providers.CartoDB.PositronNoLabels)
# scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
# ax.add_artist(scalebar)
# plt.title(f"Parks after {walking_time}m city scenario")
# black_patch = mpatches.Patch(color='green', label='Existing Parks')
# blue_patch = mpatches.Patch(color='blue', label='Added Parks')
# plt.legend(handles=[black_patch, blue_patch], loc = "lower left", bbox_to_anchor=(0, 0.03))
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/Parks{walking_time}mCityAfter.png", bbox_inches="tight", dpi=600)
# plt.close()


# ax = SpatialExtent.plot( color = None , edgecolor="grey", alpha= 0)
# afterGreenSpace.plot(ax = ax, color="green")
# cx.add_basemap(ax, crs=afterGreenSpace.crs, source=cx.providers.CartoDB.PositronNoLabels)
# scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
# ax.add_artist(scalebar)
# plt.title(f"Green Space after {walking_time}m city scenario")
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/GreenSpace{walking_time}mCityAfter.png", bbox_inches="tight", dpi=600)
# plt.close()



# ############################################################
# #### Calculate Green Space Fraction
# # ############################################################

# EnvBehavDeterms = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/EnvBehavDeterminants_{walking_time}mCity.shp")
# print(EnvBehavDeterms.columns)

# afterGreenSpace = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedGreenSpace.shp")
# afterGreenSpace = afterGreenSpace.dissolve()
# greenspacegeometry = afterGreenSpace["geometry"].values[0]
# cellarea = EnvBehavDeterms["geometry"][0].area
# print(cellarea)
# ## calculating the fraction of greenspace coverage by cell EnvBehavDeterms
# greenCovr = []
# for idx, row in EnvBehavDeterms.iterrows():
#     cell = row["geometry"]
#     if cell.intersects(greenspacegeometry):
#         intersected = cell.intersection(greenspacegeometry)
#         intersectedarea = intersected.area
#         greenCovr.append(intersectedarea/cellarea)
#     else:
#         greenCovr.append(0)
    
# EnvBehavDeterms[f"grenCovr{walking_time}"] = greenCovr

# print(EnvBehavDeterms[f"grenCovr{walking_time}"].value_counts())
# EnvBehavDeterms.to_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/EnvBehavDeterminants_{walking_time}mCity.shp", driver="ESRI Shapefile")

# ###########################################################
# ### Plot Green Space Coverage 
# ############################################################
# EnvBehavDeterms = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/EnvBehavDeterminants_{walking_time}mCity.shp")

# crs = "epsg:28992"
# points = gpd.GeoSeries(
#         [Point(485000, 120000), Point(485001, 120000)], crs=crs
#     )  # Geographic WGS 84 - degrees
# points = points.to_crs(32619)  # Projected WGS 84 - meters
# distance_meters = points[0].distance(points[1])

# ax = EnvBehavDeterms.plot(column="greenCovr", cmap='viridis')
# scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
# ax.add_artist(scalebar)
# plt.title(f"Green Space Coverage before {walking_time}m city scenario")
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/GreenSpaceCoverage{walking_time}mCityBefore.png", bbox_inches="tight", dpi=600)
# plt.close()

# ax = EnvBehavDeterms.plot(column=f"grenCovr{walking_time}", cmap='viridis')
# scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
# ax.add_artist(scalebar)
# plt.title(f"Green Space Coverage after {walking_time}m city scenario")
# plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/15min city/GreenSpaceCoverage{walking_time}mCityAfter.png", bbox_inches="tight", dpi=600)
# plt.close()



# #############################################################
# #### Saving updated files as feather
# ############################################################

# EnvBehavDeterms = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/EnvBehavDeterminants_{walking_time}mCity.shp")
# print(EnvBehavDeterms.columns)
# EnvBehavDeterms.to_feather(path_data+f"SpatialData/EnvBehavDeterminants{walking_time}mCity.feather")

# Greenspace = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedParks.shp")
# Greenspace.to_feather(path_data+f"SpatialData/Greenspace{walking_time}mCity.feather")

# Entertainment = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedentertainment.shp")
# Entertainment.to_feather(path_data+f"SpatialData/Entertainment{walking_time}mCity.feather")

# Restaurants =gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedrestaurants.shp")
# Restaurants.to_feather(path_data+f"SpatialData/Restaurants{walking_time}mCity.feather")

# Nightlife = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatednightlife.shp")
# Nightlife.to_feather(path_data+f"SpatialData/Nightlife{walking_time}mCity.feather")

# ShopsnServ = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedShopsnServ.shp")
# ShopsnServ.to_feather(path_data+f"SpatialData/ShopsnServ{walking_time}mCity.feather")

# Profess = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedProfessional.shp")
# Profess.to_feather(path_data+f"SpatialData/Profess{walking_time}mCity.feather")

# Schools = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedschool.shp")
# Schools.to_feather(path_data+f"SpatialData/Schools{walking_time}mCity.feather")

# Supermarkets = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedsupermarket.shp")
# Supermarkets.to_feather(path_data+f"SpatialData/Supermarkets{walking_time}mCity.feather")

# Kindergardens = gpd.read_file(f"D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/15mcity/AgentResidenceIsochrones{walking_time}mUpdatedchildcare.shp")
# Kindergardens.to_feather(path_data+f"SpatialData/Kindergardens{walking_time}mCity.feather")


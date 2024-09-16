import geopandas as gpd
import pyarrow.feather as feather
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

# Load the spatial built environmen
shape_file_buildings = gpd.read_file(path_data+"Built Environment/Buildings/Buildings.shp")
shape_file_streets = gpd.read_file(path_data +"Built Environment/Transport Infrastructure/Amsterdam_roads_RDNew.shp")
shape_file_greenspace = gpd.read_file(path_data +"Built Environment/Green Spaces/Green Spaces_RDNew_window.shp")
shape_file_Residences = gpd.read_file(path_data + "Built Environment/Buildings/ResidencesAmsterdamNeighbCode.shp")
shape_file_Schools = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_schools_RDNew.shp")
shape_file_Supermarkets = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp")
shape_file_Universities = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_universities_RDNew.shp")
shape_file_Kindergardens = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp")
shape_file_Restaurants = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_Foursquarevenues_Food_RDNew.shp")
shape_file_Entertainment = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew.shp")
shape_file_ShopsnServ = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_Foursquarevenues_ShopsServ_RDNew.shp")
shape_file_Nightlife = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_Foursquarevenues_Nightlife_RDNew.shp")
shape_file_Profess = gpd.read_file(path_data +"Built Environment/Facilities/Amsterdam_Foursquarevenues_Profess_other_RDNew.shp")
spatial_extent = gpd.read_file(path_data+"SpatialExtent/Amsterdam Diemen Oude Amstel Extent.shp")
shape_EnvBehavDeterminants = gpd.read_file(path_data+"Built Environment/Transport Infrastructure/ModalChoice_determ_200.shp")
shape_AirPollPreds = gpd.read_file(path_data+"Air Pollution Determinants/AirPollDeterm_grid50m_intTraff.shp")
shape_file_carroads = gpd.read_file(path_data+"Built Environment/Transport Infrastructure/cars/Speedlimit_Amsterdam_RDnew.shp")


shape_file_buildings.to_feather(path_data+"FeatherDataABM/Buildings.feather")
shape_file_streets.to_feather(path_data+"FeatherDataABM/Streets.feather" )
shape_file_greenspace.to_feather(path_data+"FeatherDataABM/Greenspace.feather" )
shape_file_Residences.to_feather(path_data+"FeatherDataABM/Residences.feather" )
shape_file_Schools.to_feather(path_data+"FeatherDataABM/Schools.feather" )
shape_file_Supermarkets.to_feather(path_data+"FeatherDataABM/Supermarkets.feather" )
shape_file_Universities.to_feather(path_data+"FeatherDataABM/Universities.feather" )
shape_file_Kindergardens.to_feather(path_data+"FeatherDataABM/Kindergardens.feather" )
shape_file_Restaurants.to_feather(path_data+"FeatherDataABM/Restaurants.feather" )
shape_file_Entertainment.to_feather(path_data+"FeatherDataABM/Entertainment.feather" )
shape_file_ShopsnServ.to_feather(path_data+"FeatherDataABM/ShopsnServ.feather" )
shape_file_Nightlife.to_feather(path_data+"FeatherDataABM/Nightlife.feather")
shape_file_Profess.to_feather(path_data+"FeatherDataABM/Profess.feather" )
spatial_extent.to_feather(path_data+"FeatherDataABM/SpatialExtent.feather")
shape_EnvBehavDeterminants.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")
shape_AirPollPreds.to_feather(path_data+"FeatherDataABM/AirPollgrid50m.feather")
shape_file_carroads[["fid", "geometry"]].to_feather(path_data+"FeatherDataABM/carroads.feather")


shape_file_greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")
greenspace = shape_file_greenspace.explode(index_parts=True)
greenspace_centroids = greenspace.copy()
greenspace_centroids["geometry"] = greenspace_centroids["geometry"].centroid
greenspace_centroids = greenspace_centroids.drop_duplicates(subset="geometry").reset_index(drop=True)
greenspace_centroids.to_feather(path_data+"SpatialData/GreenspaceCentroids.feather")
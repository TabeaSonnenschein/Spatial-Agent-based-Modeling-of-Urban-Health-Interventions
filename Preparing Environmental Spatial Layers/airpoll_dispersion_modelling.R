
pkgs = c("geojsonsf", "maptools","raster", "rgdal","sp", "sf", "jpeg", "data.table", "purrr", "rgeos" , "leaflet", "RColorBrewer",
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", "dplyr",
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree", "exactextractr", "terra")
sapply(pkgs, require, character.only = T) #load
rm(pkgs)


 

dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"


setwd(paste(dataFolder, "/Air Pollution Determinants", sep = ""))
airpoll_grid = readOGR(dsn=getwd(),layer="AirPollDeterm_grid50_clean")
airpoll_grid_raster <- raster("AirPollDeterm_grid.tif")
airpoll_road_data = read.csv("AirPollDeterm_grid50_baselineNO2.csv")

airpoll_grid_centroids = gCentroid(airpoll_grid, byid= T, id= airpoll_grid$int_id)
airpoll_grid_centroids$int_id = airpoll_grid$int_id
onroad_centroids = airpoll_grid_centroids[which(airpoll_grid_centroids$int_id %in% airpoll_road_data$int_id),]
offroad_centroids = airpoll_grid_centroids[which(!(airpoll_grid_centroids$int_id %in% airpoll_road_data$int_id)),]

airpoll_grid_centroids_sf = st_as_sf(airpoll_grid_centroids)
offroad_centroids_sf = st_as_sf(offroad_centroids)
offroad_centroids_sf <- st_transform(offroad_centroids_sf, 5880) # transform to your desired proj (unit = m)
onroad_centroids_sf = st_as_sf(onroad_centroids)
onroad_centroids_sf <- st_transform(onroad_centroids_sf, 5880) # transform to your desired proj (unit = m)
dist_matrix   <- st_distance(offroad_centroids_sf, onroad_centroids_sf)           # creates a matrix of distances

OffRoadData <- geojson_sf("D:/PhD EXPANSE/Data/Amsterdam/Air Pollution Determinants/PalmesOffRoadMeasurements/ams_palmes_only_agg_sf.geojson")

airpoll_grid_df = as.data.frame(airpoll_grid)
OffRoadData_df = as.data.frame(OffRoadData)
joined = merge(airpoll_grid_df, OffRoadData_df, by = "int_id", all = T)
joined_complete = joined[!is.na(joined$Vierweekse_7),]
joined_complete_onroad = joined_complete[joined_complete$ON_ROAD.x == 0,]

colnames(joined_complete_onroad)

# Extract 3D Bag data
# https://docs.3dbag.nl/en/schema/concepts/#level-of-detail-lod
layername = "lod12_2d"
layername = "lod12_3d"
layername = "lod22_2d"
layername = "lod22_3d"
filelist = list.files(path = "D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG")
joinedfile = st_read(paste0("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG/", filelist[1]), layer = layername)
for(file in filelist){
  d = st_read(paste0("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG/", file), layer = layername)
  joinedfile <- rbind(d, joinedfile)
}
joinedfile = unique(joinedfile)
joinedfile_shp = as_Spatial(joinedfile)
writeOGR(joinedfile_shp, dsn="D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG 2D files" ,layer= paste0("BAG3D_", layername),driver="ESRI Shapefile")



# o	Distance calculation: centroid of an off-road gridcell distance to closest road identify cell to which it belong. Euclidean distance
# o	Average fraction of Open space between cell and road
# o	(Green space/Nr Trees in between cell and road)
# o	Mode/ Average building height / fraction of building over a specific threshold/ standard deviation
# o	Windspeed and winddirection
# ???	Precalculate that
# ???	Calculate how much direction of road to cell overlaps with winddirection
# ???	Calculate degree of road to cell and subtract

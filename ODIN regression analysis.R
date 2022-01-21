
pkgs = c("maptools","rgdal","sp", "sf", "jpeg", "data.table", "purrr", "rgeos" , "leaflet", "RColorBrewer",
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", 
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree", "exactextractr")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)


dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"
city = "Amsterdam"

setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure", sep = ""))
walkability_grid = readOGR(dsn=getwd(),layer="walkability_grid")

postcode_polys =  readOGR(dsn="C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Calibration/Amsterdam/Calibration/AMS-PC4_polygons",layer="AMS-PC4_polygons")

ODIN_df = read.csv("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Subset_ODiN_1000.csv", sep = ";")

env_grid_centroids = gCentroid(walkability_grid, byid= T, id= walkability_grid$unqId)
postcode_env_join = point.in.poly(env_grid_centroids, postcode_polys)
postcode_env_join = merge(as.data.frame(postcode_env_join@data), as.data.frame(walkability_grid@data), by.x="pt.ids" , by.y = "Intid")


postcode_polys@data[,c("popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "Intid")] = 0
for(x in postcode_polys$PC4){
  postcode_polys$popDns[which(postcode_polys$PC4 == x)] = mean(postcode_env_join[which(postcode_env_join$PC4 == x), c("popDns")])
  postcode_polys$retaiDns[which(postcode_polys$PC4 == x)] = mean(postcode_env_join[which(postcode_env_join$PC4 == x), c("retaiDns")])
  postcode_polys$greenCovr[which(postcode_polys$PC4 == x)] = mean(postcode_env_join[which(postcode_env_join$PC4 == x), c("greenCovr")])
  postcode_polys$pubTraDns[which(postcode_polys$PC4 == x)] = mean(postcode_env_join[which(postcode_env_join$PC4 == x), c("pubTraDns")])
  postcode_polys$RdIntrsDns[which(postcode_polys$PC4 == x)] = mean(postcode_env_join[which(postcode_env_join$PC4 == x), c("RdIntrsDns")])
}

summary(postcode_polys@data$popDns)
summary(postcode_polys@data$retaiDns)
summary(postcode_polys@data$greenCovr)
summary(postcode_polys@data$pubTraDns)
summary(postcode_polys@data$RdIntrsDns)



ODIN_df = merge(ODIN_df, postcode_polys@data, by.x = "put here the columnname for postcode of origin of trip", by.y = "PC4", all.x = T, all.y = F)


###
# trip distance you need geodesic euclidean distance of the origin postcode centroid to destination postcode centroid
postcode_centroids = gCentroid(postcode_polys, byid= T, id= postcode_polys$PC4)
postcode_centroids_WG84 = spTransform(postcode_centroids, CRSobj = "+proj=longlat +datum=WGS84")
postcode_centroids_WG84@coords[,0]
postcode_centroids_WG84$PC4 = postcode_centroids_WG84@coords[,0]
postcode_centroids_WG84@data$PC4 =  postcode_centroids_WG84@coords[,0]

## you need to change the column names of the origin and destination Postcodes of trips
ODIN_df[,"trip_distance"] = 0
for(trip in 0:len(ODIN_df)){
  ODIN_df[trip,"trip_distance"] = spDists(postcode_centroids_WG84[which(postcode_centroids_WG84$PC4 == ODIN_df[trip, "origin"])], 
                                          postcode_centroids_WG84[which(postcode_centroids_WG84$PC4 == ODIN_df[trip, "destination"])], 
                                          longlat = T)
}



###
#generate affordability based on trip distance and cost as in simulation


###
#generate tript time based on trip distance and mode speed as in simulation


###
## trip distance BMI and age interaction just create a interaction within the regression (multiply the variables...)


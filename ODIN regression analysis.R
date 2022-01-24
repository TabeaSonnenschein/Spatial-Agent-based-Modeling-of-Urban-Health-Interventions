pkgs = c("maptools","rgdal","sp", "sf", "jpeg", "data.table", "purrr", "rgeos" , "leaflet", "RColorBrewer",
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", 
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree", "exactextractr")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)


dataFolder= "C:/Users/Marco/Documents/ABM_thesis/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"
city = "Amsterdam"

# read cell grid file
setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure", sep = ""))
walkability_grid = readOGR(dsn=getwd(),layer="walkability_grid")

# read PC4 polygons file
postcode_polys =  readOGR(dsn="C:/Users/Marco/Documents/ABM_thesis/Data/Amsterdam/Calibration/AMS-PC4_polygons",layer="AMS-PC4_polygons")

# read ODiN file
ODIN_df = read.csv("C:/Users/Marco/Documents/ABM_thesis/Data/Amsterdam/Calibration/df_AMS.csv")

# calculate the centroid for each grid cell
env_grid_centroids = gCentroid(walkability_grid, byid= T, id= walkability_grid$unqId)

# merge each grid cell centroid which the PC4 polygon associated
postcode_env_join = point.in.poly(env_grid_centroids, postcode_polys)
# then, also merge each centroid with the grid cell information (densities...)
postcode_env_join = merge(as.data.frame(postcode_env_join@data), as.data.frame(walkability_grid@data), by.x="pt.ids" , by.y = "Intid")
# --> postcode_env_join: dataset where for each grid cell centroid, I have their densities and the PC4 label that contains it.

postcode_polys@data[,c("popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "Intid")] = 0

# for each PC4, calculate the mean of each grid cell density contained
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

# merge PC4 statistics with ODiN trips

# clean ODiN
ODIN_df <- ODIN_df[ODIN_df$dep_postcode!='outsideAMS',] # delete trips outside AMS
ODIN_df <- ODIN_df[ODIN_df$arr_postcode!='outsideAMS',] # delete trips outside AMS
# remove trip with un-implemented modal choices
ODIN_df <- ODIN_df[ODIN_df$modal_choice=='walk' | ODIN_df$modal_choice=='bike' | ODIN_df$modal_choice=='car',]
ODIN_df <- ODIN_df[!is.na(ODIN_df$modal_choice),]



ODIN_df <- ODIN_df[ODIN_df$dep_postcode!=1110,] # todo
ODIN_df <- ODIN_df[ODIN_df$arr_postcode!=1110,] # todo

ODIN_df <- ODIN_df[!is.na(ODIN_df$disp_id),] # delete no trip rows
ODIN_PC4stats = merge(ODIN_df, postcode_polys@data, by.x = "dep_postcode", by.y = "PC4", all.x = T, all.y = F)


###
# In practice: trip distance you need geodesic euclidean distance of the origin postcode centroid to destination postcode centroid

# calculate the centroid of each PC4
postcode_centroids = gCentroid(postcode_polys, byid= T, id= postcode_polys$PC4)
postcode_centroids_WG84 = spTransform(postcode_centroids, CRSobj = "+proj=longlat +datum=WGS84")
#postcode_centroids_WG84@coords[,0]
postcode_centroids_WG84$PC4 = postcode_centroids_WG84@coords[,0]
postcode_centroids_WG84@data$PC4 =  postcode_centroids_WG84@coords[,0]

coord_postcodes = as.data.frame(postcode_centroids_WG84@coords)
coord_postcodes <- cbind(PC4 = rownames(coord_postcodes), coord_postcodes)
rownames(coord_postcodes) <- 1:nrow(coord_postcodes)

## you need to change the column names of the origin and destination Postcodes of trips
ODIN_PC4stats$trip_distance <- NA
ODIN_PC4stats$dep_postcode <- as.character(ODIN_PC4stats$dep_postcode)
ODIN_PC4stats$arr_postcode <- as.character(ODIN_PC4stats$arr_postcode)

library('geosphere')
for(trip in 1:nrow(ODIN_PC4stats)){
  ODIN_PC4stats[trip,"trip_distance"] <- distm(c(coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "dep_postcode"],2], coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "dep_postcode"],3]),
                                              c(coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "arr_postcode"],2], coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "arr_postcode"],3]),
                                              fun = distHaversine)
  ODIN_PC4stats[trip,"dep_x"] <- (coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "dep_postcode"],2])
  ODIN_PC4stats[trip,"dep_y"] <- (coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "dep_postcode"],3])
  ODIN_PC4stats[trip,"arr_x"] <- (coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "arr_postcode"],2])
  ODIN_PC4stats[trip,"arr_y"] <- (coord_postcodes[coord_postcodes$PC4==ODIN_PC4stats[trip, "arr_postcode"],3])
}



###
#generate affordability based on trip distance and cost as in simulation
budget = runif(1, 800.0, 5000.0)
transport_costs = cbind(modal_choice=c('walk', 'bike', 'car'), modal_choice_cost=c(0, 0.01, 0.2))
transport_costs = as.data.frame(transport_costs)
transport_costs$modal_choice_cost <- as.numeric(transport_costs$modal_choice_cost)
ODIN_PC4stats = merge(ODIN_PC4stats, transport_costs, by='modal_choice')

ODIN_PC4stats$affordability = (ODIN_PC4stats$modal_choice_cost*(ODIN_PC4stats$trip_distance/1000))/((budget/31)-20) 

###
#generate trip time based on trip distance and mode speed as in simulation
transport_speeds = cbind(modal_choice=c('walk', 'bike', 'car'), modal_choice_speed=c(1.4, 3.33, 11.11))
transport_speeds = as.data.frame(transport_speeds)
transport_speeds$modal_choice_speed <- as.numeric(transport_speeds$modal_choice_speed)
ODIN_PC4stats = merge(ODIN_PC4stats, transport_speeds, by='modal_choice')

ODIN_PC4stats$trip_time = ODIN_PC4stats$trip_distance/ODIN_PC4stats$modal_choice_speed

###
## trip distance BMI and age interaction just create a interaction within the regression (multiply the variables...)



## find the grid cells that intersect the trip and average their environmental attributes

#pkgs <- c("osrm", "sf")
#sapply(pkgs, require, character.only = T) #load

#route <- osrmRoute(src = c(ODIN_PC4stats[1,'dep_x'],ODIN_PC4stats[1,'dep_y']), dst = c(ODIN_PC4stats[1,'arr_x'],ODIN_PC4stats[1,'arr_y']), overview = "full", returnclass = "sf", osrm.server = "http://127.0.0.1:5001/", osrm.profile = "bike")
#track = as.data.frame(cbind(unlist(route$geometry)[1:(length(unlist(route$geometry))/2)], unlist(route$geometry)[((length(unlist(route$geometry))/2)+1):length(unlist(route$geometry))]))
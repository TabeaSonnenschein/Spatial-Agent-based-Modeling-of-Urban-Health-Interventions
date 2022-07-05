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
df <- merge(ODIN_df, postcode_polys@data, by.x = "dep_postcode", by.y = "PC4", all.x = T, all.y = F)

df <- df %>%
  select(
    dep_postcode,
    arr_postcode,
    sex,
    age,
    income_household,
    has_driving_license,
    car_in_household,
    popDns,
    retaiDns,
    greenCovr,
    pubTraDns,
    RdIntrsDns
  )

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
df$trip_distance <- NA
df$dep_postcode <- as.character(df$dep_postcode)
df$arr_postcode <- as.character(df$arr_postcode)

library('geosphere')
for(trip in 1:nrow(df)){
  df[trip,"trip_distance"] <- distm(c(coord_postcodes[coord_postcodes$PC4==df[trip, "dep_postcode"],2], coord_postcodes[coord_postcodes$PC4==df[trip, "dep_postcode"],3]),
                                              c(coord_postcodes[coord_postcodes$PC4==df[trip, "arr_postcode"],2], coord_postcodes[coord_postcodes$PC4==df[trip, "arr_postcode"],3]),
                                              fun = distHaversine)
  df[trip,"dep_x"] <- (coord_postcodes[coord_postcodes$PC4==df[trip, "dep_postcode"],2])
  df[trip,"dep_y"] <- (coord_postcodes[coord_postcodes$PC4==df[trip, "dep_postcode"],3])
  df[trip,"arr_x"] <- (coord_postcodes[coord_postcodes$PC4==df[trip, "arr_postcode"],2])
  df[trip,"arr_y"] <- (coord_postcodes[coord_postcodes$PC4==df[trip, "arr_postcode"],3])
}



###
#generate affordability based on trip distance and cost as in simulation
budget = runif(1, 800.0, 5000.0)

df$transport_costs_walk <- 0
df$transport_costs_bike <- 0.01
df$transport_costs_car <- 0.2

df$affordability_walk = (df$transport_costs_walk*(df$trip_distance/1000))/((budget/31)-20)
df$affordability_bike = (df$transport_costs_bike*(df$trip_distance/1000))/((budget/31)-20) 
df$affordability_car = (df$transport_costs_car*(df$trip_distance/1000))/((budget/31)-20) 


###
#generate trip time based on trip distance and mode speed as in simulation
df$transport_speed_walk <- 1.4
df$transport_speed_bike <- 3.33
df$transport_speed_car <- 11.11

df$travel_time_walk = df$trip_distance/df$transport_speed_walk
df$travel_time_bike = df$trip_distance/df$transport_speed_bike
df$travel_time_car = df$trip_distance/df$transport_speed_car


###
## trip distance BMI and age interaction just create a interaction within the regression (multiply the variables...)


## find the grid cells that intersect the trip and average their environmental attributes

#pkgs <- c("osrm", "sf")
#sapply(pkgs, require, character.only = T) #load

#route <- osrmRoute(src = c(df[1,'dep_x'],df[1,'dep_y']), dst = c(df[1,'arr_x'],df[1,'arr_y']), overview = "full", returnclass = "sf", osrm.server = "http://127.0.0.1:5001/", osrm.profile = "bike")
#track = as.data.frame(cbind(unlist(route$geometry)[1:(length(unlist(route$geometry))/2)], unlist(route$geometry)[((length(unlist(route$geometry))/2)+1):length(unlist(route$geometry))]))


### calculate utilities
# fix NaN environmental variables
df[is.nan(df$popDns),]$popDns <- 0
df[is.nan(df$retaiDns),]$retaiDns <- 0
df[is.nan(df$greenCovr),]$greenCovr <- 0
df[is.nan(df$pubTraDns),]$pubTraDns <- 0
df[is.nan(df$RdIntrsDns),]$RdIntrsDns <- 0

# normalise factors
normalise <- function(a){
  return((a-min(a))/(max(a)-min(a)))
}

df$affordability_walk <- 1-tanh(df$affordability_walk)
df$affordability_bike <- 1-tanh(df$affordability_bike)
df$affordability_car <- 1-tanh(df$affordability_car)
df$travel_time_walk <- 1-tanh(df$travel_time_walk/1000)
df$travel_time_bike <- 1-tanh(df$travel_time_bike/1000)
df$travel_time_car <- 1-tanh(df$travel_time_car/1000)
df$trip_distance <- 1-tanh(df$trip_distance/1000)
df$popDns <- normalise(df$popDns)
df$retaiDns <- normalise(df$retaiDns)
df$greenCovr <- normalise(df$greenCovr)
df$pubTraDns <- normalise(df$pubTraDns)
df$RdIntrsDns <- normalise(df$RdIntrsDns)

df$utility_walk <-
  df$affordability_walk + # always zero anyway
  df$popDns +
  df$retaiDns +
  df$greenCovr +
  df$pubTraDns +
  df$RdIntrsDns +
  df$travel_time_walk +
  df$trip_distance
df$utility_walk <- df$utility_walk/8

df$utility_bike <-
  df$affordability_bike +
  df$popDns +
  df$retaiDns +
  df$greenCovr +
  df$pubTraDns +
  df$RdIntrsDns +
  df$travel_time_bike +
  df$trip_distance
df$utility_bike <- df$utility_bike/8

df$utility_car <-
  df$affordability_car +
  df$travel_time_car +
  df$trip_distance
df$utility_car <- df$utility_car/3

# select modal choice also based on age limitations
df$predicted_modal_choice <- NA

for(i in 1:nrow(df)){
  if (df[i,"age"]<=8){
    df[i, 'predicted_modal_choice'] <- 'walk'
  } else if (df[i,"age"]>=8 & df[i,"age"]<=17) {
    df[i, 'predicted_modal_choice'] <- ifelse(df[i, 'utility_walk'] > df[i, 'utility_bike'],
                                              "walk", df[i, 'predicted_modal_choice'])
    df[i, 'predicted_modal_choice'] <- ifelse(df[i, 'utility_bike'] > df[i, 'utility_walk'],
                                              "bike", df[i, 'predicted_modal_choice'])
  } else { # adult
    if (df[i,"has_car_license"]==1 && df[i,"car_in_household"]==1) {
      df[i, 'predicted_modal_choice'] <- ifelse(df[i, 'utility_walk'] > df[i, 'utility_bike'] &
                                                  df[i, 'utility_walk'] > df[i, 'utility_car'],
                                                "walk", df[i, 'predicted_modal_choice'])
      df[i, 'predicted_modal_choice'] <- ifelse(df[i, 'utility_bike'] > df[i, 'utility_walk'] &
                                                  df[i, 'utility_bike'] > df[i, 'utility_car'],
                                                "bike", df[i, 'predicted_modal_choice'])
      df[i, 'predicted_modal_choice'] <- ifelse(df[i, 'utility_car'] > df[i, 'utility_bike'] &
                                                  df[i, 'utility_car'] > df[i, 'utility_bike'],
                                                "car", df[i, 'predicted_modal_choice']) 
    } else {
      df[i, 'predicted_modal_choice'] <- ifelse(df[i, 'utility_walk'] > df[i, 'utility_bike'],
                                                "walk", df[i, 'predicted_modal_choice'])
      df[i, 'predicted_modal_choice'] <- ifelse(df[i, 'utility_bike'] > df[i, 'utility_walk'],
                                                "bike", df[i, 'predicted_modal_choice'])
    }
  }
}

df <- df %>%
  select(
    predicted_modal_choice,
    affordability_walk,
    affordability_bike,
    affordability_car,
    travel_time_walk,
    travel_time_bike,
    travel_time_car,
    trip_distance,
    popDns,
    retaiDns,
    greenCovr,
    pubTraDns,
    RdIntrsDns
  )

# subselect factors for regression
df$affordability = ifelse(df$predicted_modal_choice=='walk',
                          df$affordability_walk,
                          ifelse(df$predicted_modal_choice=='bike',
                                 df$affordability_bike,
                                 df$affordability_car))

df$travel_time = ifelse(df$predicted_modal_choice=='walk',
                          df$travel_time_walk,
                          ifelse(df$predicted_modal_choice=='bike',
                                 df$travel_time_bike,
                                 df$travel_time_car))

df <- df %>%
  select(
    predicted_modal_choice,
    affordability,
    travel_time,
    trip_distance,
    popDns,
    retaiDns,
    greenCovr,
    pubTraDns,
    RdIntrsDns
  )



##############################
##Walkability index###########
##############################
#criteria

#1 Population density
#2 Density of retail and service destinations (retail environment)
#3 Land-use mix (commercial, cultural) Shannon Entropy 
#4 Street connectivity (intersection density)
#5 Green space
#6 Side walk density
#7 Public Transport Density


#optional criteria

# Safety from crime
# Traffic safety
# Traffic volume and speed
# Pedestrian crossing availability
# Aesthetics
# Air quality
# Shade or sun in appropriate seasons
# Street furniture
# Wind conditions
# Specific walking destinations such as light rail stops and bus stops (Brown et al., 2009)
# Job density


pkgs = c("maptools","rgdal","sp", "sf", "jpeg", "data.table", "purrr", "rgeos" , "leaflet", "RColorBrewer",
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", "dplyr",
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree", "exactextractr", "terra")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)

dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"
extent = readOGR(dsn=paste(dataFolder, "/SpatialExtent", sep = "" ),layer="Amsterdam Diemen Oude Amstel Extent")
extent = spTransform(extent, CRSobj = crs)
city = "Amsterdam"
raster_size = 200
setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure", sep = ""))
walkability_grid = readOGR(dsn=getwd(),layer=paste("walkability_grid_",raster_size, sep=""))
colnames(walkability_grid@data) = c("layer", "unique_id",  "population_density", "retail_density" , "green_coverage_fraction", "public_trans_density"  , "street_intersection_density", "int_id", "Nr_Traffic_accidents", "Nr_Traffic_Pedestrian_Accidents", "Nr_Trees", "averageTrafficVolume", "sumTrafficVolume", "MetersMajorStreets", "Pedestrian_Street_Width",  "Pedestrian_Streets_Length", "len_intersec_bikeroute", "dist_CBD")  
csv = as.data.frame(walkability_grid)
write.csv(csv, "walkability_measures2.csv" )
library()
########################################
# Making a grid of size: 100mx100m
########################################
walkability_grid_raster = raster(xmn=extent(extent)[1], xmx=extent(extent)[2], ymn=extent(extent)[3], ymx=extent(extent)[4])
raster::res(walkability_grid_raster) <- raster_size
projection(walkability_grid_raster) = crs
ncells = ncell(walkability_grid_raster)
dim(walkability_grid_raster)
walkability_grid = rasterToPolygons(walkability_grid_raster)
walkability_grid@data[("unique_id")] = paste("id_", 1:ncells, sep = "")
plot(walkability_grid,border='black', lwd=1)
walkability_grid$int_id = gsub("id_", "", walkability_grid$unique_id)
as.numeric(walkability_grid$int_id)
values(walkability_grid_raster) = as.numeric(walkability_grid$int_id)

?raster
########################################
#1 Population density
########################################
setwd(paste(dataFolder, "/Population/Worldpop", sep = ""))
Population = raster("nld_ppp_2020_UNadj_constrained.tif") #Warsaw
Population = projectRaster(Population,
              crs = crs)
Population_extent = crop(Population, extent(extent))
Population_extent = rasterToPolygons(Population_extent)
pop_cells = length(Population_extent)
Population_extent@data[("unique_id_pop")] = paste("popgrid_", 1:pop_cells, sep = "")
summary(Population_extent)
Population_extent_centroids = gCentroid(Population_extent, byid= T, id= Population_extent$unique_id_pop)
Population_extent_centroids$pop = Population_extent$nld_ppp_2020_UNadj_constrained
population_gridjoin = point.in.poly(Population_extent_centroids, walkability_grid)

walkability_grid$population_density =0
for(x in walkability_grid$unique_id){
 walkability_grid$population_density[which(walkability_grid$unique_id == x)] = sum(population_gridjoin@data[which(population_gridjoin$unique_id == x), c("pop")])
}

#analysis
summary(walkability_grid$population_density)
plot(walkability_grid, col= walkability_grid$population_density)
plot(Population_extent, add=T)


########################################
#2 Retail density
########################################
setwd(paste(dataFolder, "/Built Environment/Facilities", sep = ""))

Fsq_Arts = read.csv(paste(city, "_Foursquarevenues_ArtsEntertainment.csv", sep = ""))
Fsq_Food = read.csv(paste(city, "_Foursquarevenues_Food.csv", sep = ""))
Fsq_Nightlife = read.csv(paste(city, "_Foursquarevenues_Nightlife.csv", sep = ""))
Fsq_Shops = read.csv(paste(city, "_Foursquarevenues_ShopsServ.csv", sep = ""))

Fsq_retail= rbind(Fsq_Arts, Fsq_Food, Fsq_Nightlife, Fsq_Shops)
Fsq_retail= unique(subset(Fsq_retail, select= -c(X)))
coordinates(Fsq_retail)= ~lon+lat
proj4string(Fsq_retail)=CRS("+proj=longlat +datum=WGS84") 
Fsq_retail = spTransform(Fsq_retail, CRSobj = crs)
Fsq_retail_extent = crop(Fsq_retail, extent(extent))
Fsq_retail_gridjoin = point.in.poly(Fsq_retail_extent, walkability_grid)


walkability_grid$retail_density =0
for(x in walkability_grid@data$unique_id){
  walkability_grid$retail_density[which(walkability_grid$unique_id == x)] = length(which(Fsq_retail_gridjoin$unique_id == x))
}

#Analysis
summary(walkability_grid$retail_density)
plot(walkability_grid, col= walkability_grid$retail_density)
plot(Fsq_retail_extent, add = T)


#######################################
#4 Street connectivity (intersection density)
#######################################
setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure", sep = ""))
Streets = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure", sep = "" ),layer="Amsterdam_roads_RDNew")
Streets = spTransform(Streets, CRSobj = crs)
plot(Streets, add = T)
Streets = st_as_sfc(Streets)
street_intersections = st_intersection(Streets)
street_intersections_df = as.data.frame(street_intersections)
street_intersections_df$nr_coordinates = nchar(street_intersections_df$geometry)/16
street_intersections_df = street_intersections_df[which(street_intersections_df$nr_coordinates < 3),]

intersection_points_data = as.data.frame(matrix(NA, nrow = length(intersection_points)))
intersection_points = as(street_intersections_df$geometry, "Spatial")
intersection_points= SpatialPointsDataFrame(intersection_points, data = intersection_points_data)
writeOGR(intersection_points, dsn=getwd() ,layer= "intersection_points",driver="ESRI Shapefile")

plot(Streets)
plot(intersection_points, col= "Red", add= T)

street_intersections_gridjoin = point.in.poly(intersection_points, walkability_grid)

walkability_grid$street_intersection_density =0
for(x in walkability_grid@data$unique_id){
  walkability_grid$street_intersection_density[which(walkability_grid$unique_id == x)] = length(which(street_intersections_gridjoin$unique_id == x))
}

plot(walkability_grid, col= walkability_grid$street_intersection_density)
summary(walkability_grid$street_intersection_density)


#######################################
#5 Green space
#######################################
#official parks
GreenSpaces = readOGR(dsn=paste(dataFolder, "/Built Environment/Green Spaces", sep = "" ),layer="Green Spaces")
#OSM green spaces
GreenSpaces = readOGR(dsn=paste(dataFolder, "/Built Environment/Green Spaces", sep = "" ),layer="Green_Spaces_OSM_Amsterdam_dissolved")

GreenSpaces = spTransform(GreenSpaces, CRSobj = crs)
GreenSpaces = aggregate(GreenSpaces, dissolve = T)
GreenSpaces_sfc = st_as_sfc(GreenSpaces)
plot(GreenSpaces,col="green", add = T)

green_space_raster = coverage_fraction(walkability_grid_raster, GreenSpaces_sfc)[[1]]
plot(green_space_raster)
green_space_raster= rasterToPolygons(green_space_raster)
walkability_grid@data$green_coverage_fraction = green_space_raster@data$layer
plot(walkability_grid, col= walkability_grid$green_coverage_fraction)
summary(walkability_grid$green_coverage_fraction)




#######################################
#7 Public Transport Density
#######################################
PT_stations = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/public transport", sep = "" ),layer="Tram_n_Metrostations")
PT_stations = spTransform(PT_stations, CRSobj = crs)
PT_stations_gridjoin = point.in.poly(PT_stations, walkability_grid)

walkability_grid$public_trans_density =0
for(x in walkability_grid@data$unique_id){
  walkability_grid$public_trans_density[which(walkability_grid$unique_id == x)] = length(which(PT_stations_gridjoin$unique_id == x))
}

plot(walkability_grid, col= walkability_grid$public_trans_density)
summary(walkability_grid$public_trans_density)




#######################################
#8 Traffic Accidents
#######################################
setwd(paste(dataFolder, "/Built Environment/Traffic Accidents", sep = ""))
Traffic_Accidents = readOGR(dsn=paste(dataFolder, "/Built Environment/Traffic Accidents", sep = ""),layer="TrafficAccidentsAmsterdamRegion")
Traffic_Accidents = spTransform(Traffic_Accidents, CRSobj = crs)
Traffic_Accidents = crop(Traffic_Accidents, extent(extent))
writeOGR(Traffic_Accidents, dsn=getwd() ,layer="TrafficAccidentsAmsterdam",driver="ESRI Shapefile")

Traffic_Accidents_gridjoin = point.in.poly(Traffic_Accidents, walkability_grid)

unique(Traffic_Accidents@data$AOL_ID)

walkability_grid$Nr_Traffic_accidents =0
walkability_grid$Nr_Traffic_Pedestrian_Accidents =0
for(x in walkability_grid@data$unique_id){
  walkability_grid$Nr_Traffic_accidents[which(walkability_grid$unique_id == x)] = length(which(Traffic_Accidents_gridjoin$unique_id == x))
  walkability_grid$Nr_Traffic_Pedestrian_Accidents[which(walkability_grid$unique_id == x)] = length(which(Traffic_Accidents_gridjoin$unique_id == x & Traffic_Accidents_gridjoin$AOL_ID == "Voetganger"))
}

plot(walkability_grid, col= walkability_grid$Nr_Traffic_accidents)
summary(walkability_grid$Nr_Traffic_accidents)

plot(walkability_grid, col= walkability_grid$Nr_Traffic_Pedestrian_Accidents)
summary(walkability_grid$Nr_Traffic_Pedestrian_Accidents)


#######################################
#9 Trees
#######################################
setwd(paste(dataFolder, "/Built Environment/Trees", sep = ""))
Trees = readOGR(dsn=paste(dataFolder, "/Built Environment/Trees", sep = "" ),layer="Amsterdam Trees")
Trees = spTransform(Trees, CRSobj = crs)
Trees_gridjoin = point.in.poly(Trees, walkability_grid)

walkability_grid$Nr_Trees =0
for(x in walkability_grid@data$unique_id){
  walkability_grid$Nr_Trees[which(walkability_grid$unique_id == x)] = length(which(Trees_gridjoin$unique_id == x))
}

plot(walkability_grid, col= walkability_grid$Nr_Trees)
summary(walkability_grid$Nr_Trees)


#######################################
#10 Traffic Volume
#######################################
CarStreets = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/cars", sep = ""),layer="Car Traffic_RDNew")
CarStreets = spTransform(CarStreets, CRSobj = crs)
plot(CarStreets)
CarStreet_gridjoin = intersect(CarStreets, walkability_grid)


walkability_grid$averageTrafficVolume =0
walkability_grid$sumTrafficVolume =0
for(x in walkability_grid@data$unique_id){
  walkability_ids = which(CarStreet_gridjoin$unique_id == x)
  if(length(walkability_ids)>0){
    walkability_grid$averageTrafficVolume[which(walkability_grid$unique_id == x)] = mean(as.integer(CarStreet_gridjoin$etmaal[walkability_ids]))
    walkability_grid$sumTrafficVolume[which(walkability_grid$unique_id == x)] = sum(as.integer(CarStreet_gridjoin$etmaal[walkability_ids]))
  }
}

plot(walkability_grid, col= walkability_grid$averageTrafficVolume)
summary(walkability_grid$averageTrafficVolume)

plot(walkability_grid, col= walkability_grid$sumTrafficVolume)
summary(walkability_grid$sumTrafficVolume)

#######################################
#11 Urban Highway Length
#######################################
CarStreets = CarStreets[which(CarStreets$etmaal != 0),]
CarStreets_sf= st_as_sf(CarStreets)
walkability_grid_sf = st_as_sf(walkability_grid)
intersection <- st_intersection(walkability_grid_sf, CarStreets_sf) %>% 
  mutate(lenght = st_length(.)) %>% 
  st_drop_geometry() # complicates things in joins later on


walkability_grid$MetersMajorStreets =0
for(x in walkability_grid$unique_id){
  walkability_grid$MetersMajorStreets[which(walkability_grid$unique_id == x)] = sum(intersection$lenght[which(intersection$unique_id == x)])
}

plot(walkability_grid, col= walkability_grid$MetersMajorStreets)
summary(walkability_grid$MetersMajorStreets)


#######################################
#12 Pedestrian Pathway Width
#######################################
setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure/pedestrian", sep = ""))
Pedestrian_streets = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/pedestrian", sep = "" ),layer="Pedestrian Network_Amsterdam")
Pedestrian_streets = spTransform(Pedestrian_streets, CRSobj = crs)

Pedestrian_streets_sf= st_as_sf(Pedestrian_streets)
inter <- st_intersects(Pedestrian_streets_sf,Pedestrian_streets_sf, sparse = TRUE)
Pedestrian_streets_sf <- Pedestrian_streets_sf[lengths(inter)>2,] #select lines intersecting with more than themselves
Pedestrian_streets_new = as_Spatial(Pedestrian_streets_sf)
writeOGR(Pedestrian_streets_new, dsn=getwd() ,layer="Pedestrian_Network_Amsterdam_clean",driver="ESRI Shapefile")

walkability_grid_sf = st_as_sf(walkability_grid)
Pedestrian_streets_gridjoin = st_intersection(Pedestrian_streets_sf, walkability_grid_sf)

walkability_grid$Pedestrian_Street_Width =0
for(x in walkability_grid@data$unique_id){
  walkability_grid$Pedestrian_Street_Width[which(walkability_grid$unique_id == x)] = mean(na.omit(Pedestrian_streets_gridjoin$gewogen_ge[which(Pedestrian_streets_gridjoin$unique_id == x)]))
  }


plot(walkability_grid, col= walkability_grid$Pedestrian_Street_Width)
summary(walkability_grid$Pedestrian_Street_Width)


#######################################
#13 Pedestrian Pathway length
#######################################

intersection <- st_intersection(walkability_grid_sf, Pedestrian_streets_sf) %>% 
  mutate(lenght = st_length(.)) %>% 
  st_drop_geometry() # complicates things in joins later on

walkability_grid$Pedestrian_Streets_Length = 0
for(x in walkability_grid$unique_id){
  walkability_grid$Pedestrian_Streets_Length[which(walkability_grid$unique_id == x)] = sum(intersection$lenght[which(intersection$unique_id == x)])
}

plot(walkability_grid, col= walkability_grid$Pedestrian_Streets_Length)
summary(walkability_grid$Pedestrian_Streets_Length)

#######################################
#14 Bikelane Length
#######################################
setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure/bike", sep = ""))
Bike_lanes = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/bike", sep = "" ),layer="Fietsknooppuntnetwerken_Amsterdam")
Bike_lanes = spTransform(Bike_lanes, CRSobj = crs)

Bike_lanes_sf= st_as_sf(Bike_lanes)
walkability_grid_sf = st_as_sf(walkability_grid)

intersection <- st_intersection(walkability_grid_sf, Bike_lanes_sf) %>% 
  mutate(lenght = st_length(.)) %>% 
  st_drop_geometry() # complicates things in joins later on

walkability_grid$len_intersec_bikeroute = 0
for(x in walkability_grid@data$unique_id){
  walkability_grid$len_intersec_bikeroute[which(walkability_grid$unique_id == x)] = sum(intersection$lenght[which(intersection$unique_id == x)])
}

plot(walkability_grid, col= walkability_grid$len_intersec_bikeroute)
summary(walkability_grid$len_intersec_bikeroute)


#######################################
#15 Distance to CBD
#######################################

walkability_grid_centroids = gCentroid(walkability_grid, byid= T, id= walkability_grid$unique_id)
walkability_grid_centroids = spTransform(walkability_grid_centroids, CRSobj = CRS("+proj=longlat +datum=WGS84") )
CBD = walkability_grid_centroids[which(walkability_grid$retail_density == max(walkability_grid$retail_density))]

plot(walkability_grid)
plot(CBD, add= T)
plot(postcode_polys, add = T)

walkability_grid$dist_CBD = 0
x = as.data.frame(spDists(walkability_grid_centroids, CBD, longlat = T))
walkability_grid$dist_CBD = x$V1

plot(walkability_grid, col= walkability_grid$dist_CBD)
summary(walkability_grid$dist_CBD)





#####################################
# Saving the grid data
#####################################

setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure", sep = ""))

colnames(walkability_grid@data)
c("layer", "unique_id",  "population_density", "retail_density" , "green_coverage_fraction", "public_trans_density"  , "street_intersection_density", "int_id", "Nr_Traffic_accidents", "Nr_Traffic_Pedestrian_Accidents", "Nr_Trees", "averageTrafficVolume", "sumTrafficVolume", "MetersMajorStreets", "Pedestrian_Street_Width",  "Pedestrian_Streets_Length", "len_intersec_bikeroute", "dist_CBD")   
colnames(walkability_grid@data) =c("layer", "unqId",  "popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "Intid", "TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV", "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD")   

walkability_grid@data = walkability_grid@data[c("unqId", "Intid", "popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV", "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD")]

writeOGR(walkability_grid, dsn=getwd() ,layer= paste("walkability_grid_",raster_size, sep=""),driver="ESRI Shapefile")
writeRaster(walkability_grid_raster, "walkability_grid.tif", format = "GTiff", overwrite = T)
walkability_measures = as.data.frame(walkability_grid)
walkability_measures= subset(walkability_measures, select= -c(layer))
write.csv(walkability_measures, "walkability_measures.csv", row.names = F, quote=FALSE)

walkability_grid = readOGR(dsn=getwd(),layer=paste("walkability_grid_",raster_size, sep=""))
colnames(walkability_grid@data) = c("unqId", "Intid", "popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV", "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD")
colnames(walkability_grid@data) = c("unique_id",  "int_id", "population_density", "retail_density" , "green_coverage_fraction", "public_trans_density"  , "street_intersection_density",  "Nr_Traffic_accidents", "Nr_Traffic_Pedestrian_Accidents", "Nr_Trees", "averageTrafficVolume", "sumTrafficVolume", "MetersMajorStreets", "Pedestrian_Street_Width",  "Pedestrian_Streets_Length", "len_intersec_bikeroute", "dist_CBD")  

summary(walkability_grid$popDns)
summary(walkability_grid$greenCovr)
summary(walkability_grid$retaiDns)
summary(walkability_grid$pubTraDns)
summary(walkability_grid$RdIntrsDns)



#####################################
# Mapping
#####################################

rlang::last_error()

# Define cut points for the colorbins
cuts <- c(0.0, 0.1, 0.2, 0.3, 0.40, 0.5, 0.60, 0.7, 0.8, 0.9, 1)

# Choose a color palette and assign it to the values
colorbins <- colorBin("YlOrRd", domain = walkability_grid$green_coverage_fraction, bins = cuts)

# Display data on elderly people on the map 
map <-  leaflet(walkability_grid) %>%
  #  addTiles() %>%
  #  addProviderTiles("Esri.WorldGrayCanvas") %>%
  addPolygons(stroke = TRUE, color = "white", weight="1", smoothFactor = 0.3, 
              fillOpacity = 0.7, fillColor = ~colorbins(walkability_grid$green_coverage_fraction))  

map

# Add a legend
map_with_legend <- map %>% addLegend(pal = colorbins, 
                                     values = neighborhoods_utrecht$p_65_inf,
                                     labFormat = labelFormat(suffix = " %", transform = function(p_65_inf) 100 * p_65_inf),
                                     opacity = 0.7, title = "Residents of age 65 and older", position = "topright")

map_with_legend
ggplot(walkability_grid, aes(long,lat,group=group, fill=green_coverage_fraction )) + geom_polygon() + geom_path(colour="white")+coord_fixed()


ggplot(walkability_grid, aes(x=long, y=lat, group=group))+
  geom_polygon(aes(fill=walkability_grid$green_coverage_fraction))+
  geom_path(colour="grey50")+
  scale_fill_gradientn("2012 Marriages",
                       colours=rev(brewer.pal(10,"Spectral")), 
                       trans="log", 
                       breaks=c(0.0, 0.1, 0.2, 0.3, 0.40, 0.5, 0.60, 0.7, 0.8, 0.9, 1))+
  theme(axis.text=element_blank(), 
        axis.ticks=element_blank(), 
        axis.title=element_blank())+
  coord_fixed()

walkability_grid
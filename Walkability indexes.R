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
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", 
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree", "exactextractr")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)

dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"
extent = readOGR(dsn=paste(dataFolder, "/SpatialExtent", sep = "" ),layer="Amsterdam Diemen Oude Amstel Extent")
extent = spTransform(extent, CRSobj = crs)
city = "Amsterdam"

library()
########################################
# Making a grid of size: 100mx100m
########################################
walkability_grid_raster = raster(xmn=extent(extent)[1], xmx=extent(extent)[2], ymn=extent(extent)[3], ymx=extent(extent)[4])
raster_size = 200
res(walkability_grid_raster) <- raster_size
projection(walkability_grid_raster) = crs
ncells = ncell(walkability_grid_raster)
dim(walkability_grid_raster)
walkability_grid = rasterToPolygons(walkability_grid_raster)
walkability_grid@data[("unique_id")] = paste("id_", 1:ncells, sep = "")
plot(walkability_grid,border='black', lwd=1)
walkability_grid$int_id = gsub("id_", "", walkability_grid$unique_id)
as.numeric(walkability_grid$int_id)
values(walkability_grid_raster) = as.numeric(walkability_grid$int_id)

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
setwd(paste(dataFolder, "/Built Environment/Green Spaces", sep = ""))
GreenSpaces = readOGR(dsn=paste(dataFolder, "/Built Environment/Green Spaces", sep = "" ),layer="Green Spaces")
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
setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure/public transport", sep = ""))
PT_stations = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/public transport", sep = "" ),layer="Tram_n_Metrostations")
PT_stations = spTransform(PT_stations, CRSobj = crs)
PT_stations_gridjoin = point.in.poly(PT_stations, walkability_grid)

walkability_grid$public_trans_density =0
for(x in walkability_grid@data$unique_id){
  walkability_grid$public_trans_density[which(walkability_grid$unique_id == x)] = length(which(PT_stations_gridjoin$unique_id == x))
}

plot(walkability_grid, col= walkability_grid$public_trans_density)
summary(walkability_grid$public_trans_density)





#####################################
# Saving the grid data
#####################################

setwd(paste(dataFolder, "/Built Environment/Transport Infrastructure", sep = ""))

colnames(walkability_grid@data)
c("layer", "unique_id",  "population_density", "retail_density" , "green_coverage_fraction", "public_trans_density"  , "street_intersection_density", "int_id")   
colnames(walkability_grid@data) = c("layer", "unqId",  "popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "Intid")   

writeOGR(walkability_grid, dsn=getwd() ,layer= "walkability_grid",driver="ESRI Shapefile")
writeRaster(walkability_grid_raster, "walkability_grid.tif", format = "GTiff", overwrite = T)
walkability_measures = as.data.frame(walkability_grid)
walkability_measures= subset(walkability_measures, select= -c(layer))
write.csv(walkability_measures, "walkability_measures.csv", row.names = F)


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
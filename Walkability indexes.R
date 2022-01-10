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

pkgs = c("maptools","rgdal","sp", "sf", "jpeg", "data.table", "purrr", "rgeos" , 
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", 
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)

dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
extent = readOGR(dsn=paste(dataFolder, "/SpatialExtent", sep = "" ),layer="Amsterdam Diemen Oude Amstel Extent")
extent = spTransform(extent, CRSobj = crs)
city = "Amsterdam"


########################################
# Making a grid of size: 100mx100m
########################################
walkability_grid = raster(xmn=extent(extent)[1], xmx=extent(extent)[2], ymn=extent(extent)[3], ymx=extent(extent)[4])
res(walkability_grid) <- 200
projection(walkability_grid) = crs
ncells = ncell(walkability_grid)
dim(walkability_grid)
walkability_grid = rasterToPolygons(walkability_grid)
walkability_grid@data[("unique_id")] = paste("id_", 1:ncells, sep = "")
plot(walkability_grid,add=TRUE, border='black', lwd=1)


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
plot(walkability_grid["population_density"])
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
plot(walkability_grid["retail_density"])
plot(Fsq_retail_extent, add = T)

#######################################
#5 Green space
#######################################
setwd(paste(dataFolder, "/Built Environment/Green Spaces", sep = ""))
GreenSpaces = readOGR(dsn=paste(dataFolder, "/Built Environment/Green Spaces", sep = "" ),layer="Green Spaces_RDNew")
GreenSpaces = spTransform(GreenSpaces, CRSobj = crs)
GreenSpaces_extent = crop(GreenSpaces, extent(extent))


#######################################
#7 Public Transport Density
#######################################





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

pkgs = c("maptools","rgdal","sp", "sf", "jpeg", "data.table", "purrr",   
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", 
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)

dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
extent = readOGR(dsn=paste(dataFolder, "/SpatialExtent", sep = "" ),layer="Amsterdam Diemen Oude Amstel Extent")
extent = spTransform(extent, CRSobj = crs)

########################################
#1 Population density
########################################
setwd(paste(dataFolder, "/Population/Worldpop", sep = ""))
Population = raster("nld_ppp_2020_UNadj_constrained.tif") #Warsaw
Population = projectRaster(Population,
              crs = crs)

Population_extent = crop(Population, extent(extent))
summary(Population_extent)
plot(Population_extent)

########################################
#2 Retail density
########################################
setwd(paste(dataFolder, "/Built Environment/Facilities", sep = ""))

Fsq = readOGR(dsn=paste(dataFolder, "/Built Environment/Facilities", sep = "") ,layer= paste(city, "_Fsq.csv", sep = ""))

"Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew"
"Amsterdam_Foursquarevenues_Food_RDNew"
"Amsterdam_Foursquarevenues_Nightlife_RDNew"
"Amsterdam_Foursquarevenues_ShopsServ_RDNew"






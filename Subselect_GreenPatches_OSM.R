
pkgs = c("maptools", "rgdal","sp", "sf",  "rgeos" , "ggplot2",  "raster",  "dplyr" )
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)

# download OSM data from Geofabric and set directory to folder where GIS files are extracted
dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"
crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"
extent = readOGR(dsn=paste(dataFolder, "/SpatialExtent", sep = "" ),layer="Amsterdam Diemen Oude Amstel Extent")
extent = spTransform(extent, CRSobj = crs)
city = "Amsterdam"

### keys for green spaces as proposed here: https://www.researchgate.net/publication/328786218_A_System_for_Generating_Customized_Pleasant_Pedestrian_Routes_Based_on_OpenStreetMap_Data
### Novack, Tessio & Wang, Zhiyong & Zipf, Alexander. (2018). A System for Generating Customized Pleasant Pedestrian Routes Based on OpenStreetMap Data. Sensors. 18. 3794. 10.3390/s18113794. 

# landuse 
LU_keys = c("grass", "forest", "farmland", "allotments", "cemetery", "greenfield", "meadow", "orchard", "recreation_ground", "village_green", "vineyard")

# natural
NAT_keys = c("wood", "scrub", "heath", "grassland", "wetland")

# POIs
POI_keys = c("garden", "golf_course", "nature_reserve", "park", "pitch","grave_yard", "camp_site", "playground")

# POIs containes the following keys
# amenity --> c("grave_yard")
# leisure --> c("garden", "golf_course", "nature_reserve", "park", "pitch")
# tourism --> c("camp_site")


# loading the relevant OSM datasets
setwd(paste(dataFolder, "/OSM", sep = ""))
landuse_OSM = readOGR(dsn=getwd(),layer="gis_osm_landuse_a_free_1")
Green_LU = landuse_OSM[which(landuse_OSM$fclass %in% LU_keys),]

natural_OSM = readOGR(dsn=getwd(),layer="gis_osm_natural_a_free_1")
Green_NAT = natural_OSM[which(natural_OSM$fclass %in% NAT_keys),]

pois_OSM = readOGR(dsn=getwd(),layer="gis_osm_pois_a_free_1")
Green_POI = pois_OSM[which(pois_OSM$fclass %in% POI_keys),]

Green_Spaces = bind(Green_LU, Green_POI)
Green_Spaces = bind(Green_Spaces, Green_NAT)

Green_Spaces = spTransform(Green_Spaces, CRSobj = crs)
writeOGR(Green_Spaces, dsn=getwd() ,layer= "Green_Spaces_OSM",driver="ESRI Shapefile")

Green_Spaces = crop(Green_Spaces, raster::extent(extent))
writeOGR(Green_Spaces, dsn=getwd() ,layer= paste("Green_Spaces_OSM_", city, sep = ""),driver="ESRI Shapefile")

#3 the below code doesn't work
Green_Spaces_dissolved = gUnaryUnion(Green_Spaces)
Green_Spaces_dissolved = sp::aggregate(Green_Spaces)


Green_Spaces_dissolved_polys = Green_Spaces_dissolved@polygons[[1]]
x = SpatialPolygons(list(Green_Spaces_dissolved_polys@Polygons),proj4string = CRS(crs) )

?SpatialPolygons
Green_Spaces_dissolved = sp::disaggregate(Green_Spaces_dissolved)
ids = paste("id_", 1:length(Green_Spaces_dissolved_polys@Polygons), sep = "")
Green_Spaces_dissolved = SpatialPolygonsDataFrame(Green_Spaces_dissolved_polys, data = ids)
Green_Spaces_dissolved@data$id = paste("id_", range(1, length(length(Green_Spaces_dissolved_polys@Polygons))))

?disaggregate


writeOGR(Green_Spaces_dissolved, dsn=getwd() ,layer= paste("Green_Spaces_OSM_dissolved_", city, sep = ""),driver="ESRI Shapefile")
plot(Green_Spaces_dissolved)







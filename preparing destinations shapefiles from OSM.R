pkgs <- c("sf", "sp", "rgdal", "spatialEco")

#sapply(pkgs, install.packages, character.only = T) #uncomment when installation needed
sapply(pkgs, require, character.only = T) #load packages
rm(pkgs)

setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/OSM")
dsn_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/OSM"
OSM_POIs <- readOGR(dsn=dsn_data ,layer="gis_osm_pois_free_1")

unique(OSM_POIs@data$fclass)
supermarkets = OSM_POIs[which(OSM_POIs@data$fclass == "supermarket"),]
hospitals = OSM_POIs[which(OSM_POIs@data$fclass == "hospital" ),]
universities = OSM_POIs[which(OSM_POIs@data$fclass == "university"),]
kindergardens = OSM_POIs[which(OSM_POIs@data$fclass == "kindergarten" ),]

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
supermarkets = spTransform(supermarkets, CRSobj = crs)
hospitals = spTransform(hospitals, CRSobj = crs)
universities = spTransform(universities, CRSobj = crs)
kindergardens = spTransform(kindergardens, CRSobj = crs)

city = "Amsterdam"

writeOGR(supermarkets, dsn=dsn_data ,layer= paste(city, "_","supermarkets", "_", crs_name, sep = ""),driver="ESRI Shapefile")
writeOGR(hospitals, dsn=dsn_data ,layer= paste(city, "_","hospitals", "_", crs_name, sep = ""),driver="ESRI Shapefile")
writeOGR(universities, dsn=dsn_data ,layer= paste(city, "_","universities", "_", crs_name, sep = ""),driver="ESRI Shapefile")
writeOGR(kindergardens, dsn=dsn_data ,layer= paste(city, "_","kindergardens", "_", crs_name, sep = ""),driver="ESRI Shapefile")


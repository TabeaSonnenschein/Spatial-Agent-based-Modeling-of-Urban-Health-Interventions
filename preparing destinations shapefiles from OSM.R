pkgs <- c("sf", "sp", "rgdal", "spatialEco", "maptools")

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
dsn_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"
extent <- readOGR(dsn=dsn_data ,layer="Amsterdam Diemen Oude Amstel Extent")

dsn_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities"

hospitals <- point.in.poly(hospitals, extent, sp = T)
hospitals <- hospitals[!is.na(hospitals@data$gemeenteco),]
plot(hospitals)
writeOGR(hospitals, dsn=dsn_data ,layer= paste(city, "_","hospitals", "_", crs_name, sep = ""),driver="ESRI Shapefile")

supermarkets <- point.in.poly(supermarkets, extent, sp = T)
supermarkets <- supermarkets[!is.na(supermarkets@data$gemeenteco),]
plot(supermarkets)
writeOGR(supermarkets, dsn=dsn_data ,layer= paste(city, "_","supermarkets", "_", crs_name, sep = ""),driver="ESRI Shapefile")


universities <- point.in.poly(universities, extent, sp = T)
universities <- universities[!is.na(universities@data$gemeenteco),]
plot(universities)
writeOGR(universities, dsn=dsn_data ,layer= paste(city, "_","universities", "_", crs_name, sep = ""),driver="ESRI Shapefile")


dsn_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/schools"
schools <- readOGR(dsn=dsn_data ,layer="schools_ED50")
schools = spTransform(schools, CRSobj = crs)

schools <- point.in.poly(schools, extent, sp = T)
schools <- schools[!is.na(schools@data$gemeenteco),]
plot(schools)
writeOGR(schools, dsn=dsn_data ,layer= paste(city, "_","schools", "_", crs_name, sep = ""),driver="ESRI Shapefile")



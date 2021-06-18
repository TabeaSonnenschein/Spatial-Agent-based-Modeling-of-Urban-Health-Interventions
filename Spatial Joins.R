
pkgs <- c("sf", "sp", "stplanr", "rgdal", "spatialEco")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)

crs <- "+init=EPSG:23095" #ED_1950_TM_5_NE
crs <- "+init=EPSG:28992" #Amersfoort / RD New


dsn_data = setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Administrative Units")
polygon = readOGR(dsn=dsn_data ,layer="Netherlands_Neighborhoods", driver="ESRI Shapefile")
colnames(polygon@data)
polygon@data = polygon@data[,c("buurtcode" , "buurtnaam")]
polygon = spTransform(polygon, CRSobj = crs)
proj4string(polygon)=CRS(crs) 

dsn_data = setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings")
point = readOGR(dsn=dsn_data ,layer="Residences", driver="ESRI Shapefile")
residences = spTransform(point, CRSobj = crs)
proj4string(point)=CRS(crs) 

## needs to be same coordinate reference system!
polygon@proj4string
point@proj4string

point <- point.in.poly(point, polygon, sp = T)
colnames(point@data) #check if the desired columns are present


plot(point)

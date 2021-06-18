
pkgs <- c("sf", "sp", "stplanr", "rgdal", "spatialEco")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)


dsn_data = setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Administrative Units")
polygon = readOGR(dsn=dsn_data ,layer="Netherlands_Neighborhoods")
colnames(polygon@data) # select only columns that should be joined to point dataset

dsn_data = setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings")
point = readOGR(dsn=dsn_data ,layer="Residences")



joinPolygonAttr_to_PointSPDF = function(polygon_SPDF, point_SPDF, Country_ISO, poly_col_list){
  if(Country_ISO == "NL"){
    crs = "+init=EPSG:28992" #Amersfoort / RD New
  }
  polygon_SPDF@data = polygon_SPDF@data[,poly_col_list] # select only columns that should be joined to point dataset
  polygon_SPDF = spTransform(polygon_SPDF, CRSobj = crs)
  proj4string(polygon_SPDF)=CRS(crs) 
  point_SPDF = spTransform(point_SPDF, CRSobj = crs)
  proj4string(point_SPDF)=CRS(crs) 
  if(as.character(polygon_SPDF@proj4string) == as.character(point_SPDF@proj4string)){ ## needs to be same coordinate reference system!
    newSdf <- point.in.poly(point_SPDF, polygon_SPDF, sp = T)
    print(paste("New columns of Spatial Point Dataframe:", paste(colnames(newSdf@data))))  #check if the desired columns are present
    return(newSdf) 
   }
  else{
    print("Not possible to transform spatial datasets into same CRS")
  }
}

point = joinPolygonAttr_to_PointSPDF(polygon_SPDF = polygon, point_SPDF = point, Country_ISO = "NL", poly_col_list= c("buurtcode" , "buurtnaam"))

dsn_data = setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings")
writeOGR(point, dsn=dsn_data ,layer="Residences_neighcode_RDNew",driver="ESRI Shapefile")
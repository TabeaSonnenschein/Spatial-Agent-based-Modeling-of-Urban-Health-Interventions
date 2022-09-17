pkgs <- c("sf", "sp", "rgdal", "spatialEco")
sapply(pkgs, require, character.only = T) #load
rm(pkgs)


setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Traffic/bike traffic")

files = list.files(path = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Traffic/bike traffic", pattern = "*.csv", all.files = FALSE,
           full.names = FALSE, recursive = FALSE,
           ignore.case = FALSE, include.dirs = FALSE, no.. = FALSE)

x = 0
for(file in files){
  if(x == 0){
    fulldata = read.csv(file)
  }
  else{
  data = read.csv(file)
  fulldata = rbind(fulldata, data)
  }
  x=1
}


# clean and prepare data
## remove missing data
fulldata= fulldata[which(!is.na(fulldata$intensiteit_oplopend)),]


Uniq_loc = unique(fulldata$locatiecode)
print(paste("Number of unique locations:" , as.character(length(Uniq_loc))))
loc_coords = unique(fulldata[,c( "lengtegraad", "breedtegraad")])
loc_coords = SpatialPoints(loc_coords)
crs = "+proj=longlat +datum=WGS84"
proj4string(loc_coords)=CRS(crs)
crs = "+init=EPSG:28992" #Amersfoort / RD New
loc_coords = spTransform(loc_coords, CRSobj = crs)

Amsterdam_Roads = readOGR(dsn="C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure" ,layer="Amsterdam_roads_RDNew")

plot(Amsterdam_Roads, col = "azure4")
plot(loc_coords, add=T, col = "red")

Uniq_timepoints = unique(fulldata$begintijd)
print(paste("Number of unique timepoints for measurement:" , as.character(length(Uniq_timepoints))))
print(Uniq_timepoints)




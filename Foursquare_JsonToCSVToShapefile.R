####################################################################
##########  Transform Foursquare Json File into Data frame #########
####################################################################
#install.packages("jsonlite") #uncomment when not yet installed
library(jsonlite)
  
setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare") ##seting the working directory to folder with json dataset
city = "Amsterdam"

### uncomment the venuetype from which you want to convert the json
venuetype = "Food"
#venuetype = "ArtsEntertainment"
#venuetype = "Nightlife"
#venuetype = "College_Uni"
venuetype = "Outdoors_Recreation"
#venuetype = "ShopsServ"
#venuetype = "Profess_other"


Json_File <- fromJSON(txt= paste(city,"_Foursquarevenues_",venuetype, ".json", sep=""))

Dataframe  <- data.frame(c(seq(1, (length(Json_File)))))

Dataframe$name <- NA
Dataframe$category <- NA
Dataframe$location <- NA
Dataframe$venueid <- NA
Dataframe$referralid <- NA

l= length(Json_File)
for(i in 1:l){
  if(length(Json_File[[i]][[2]]) != 0){
    Dataframe$name[i] <- as.vector(Json_File[[i]][[2]]['name'])
    Dataframe$category[i] <- as.list(Json_File[[i]][[2]]['categories'])
    Dataframe$location[i] <- as.list(Json_File[[i]][[2]]['location'])
    Dataframe$venueid[i] <- as.vector(Json_File[[i]][[2]]['id'])
    Dataframe$referralid[i] <- as.vector(Json_File[[i]][[2]]['referralId'])
  }
}

Dataframe_clean <-  as.data.frame(Dataframe[!is.na(Dataframe$name),])

Dataframe_final  <- data.frame(c(seq(1, 50000)))

l <- length(Dataframe_clean$name)
n<- 0
for(i in 1:l){
  m <- length(Dataframe_clean$category[[i]])
  for(j in 1:m){
    s <- n+j
    if("name" %in% colnames(Dataframe_clean$category[[i]][[j]])){
      Dataframe_final$categoryname[s] <- as.character(Dataframe_clean$category[[i]][[j]]["name"])
      Dataframe_final$categoryid[s] <- as.character(Dataframe_clean$category[[i]][[j]]["id"])
    }
    else {
      Dataframe_final$categoryname[s] <- NA
      Dataframe_final$categoryid[s] <- NA

    }
  }
  n <-n+m
}


l <- length(Dataframe_clean$name)
n<-0
for(i in 1:l){
  m <- length(Dataframe_clean$name[[i]])
  for(j in 1:m){
    s <- n+j
    Dataframe_final$venuename[s] <- as.character(Dataframe_clean$name[[i]][j])
    Dataframe_final$venueid[s] <- as.character(Dataframe_clean$venueid[[i]][j])
    Dataframe_final$referralid[s] <- as.character(Dataframe_clean$referralid[[i]][j])
  }
  n <-n+m
}



l <- length(Dataframe_clean$name)
n<- 0
for(i in 1:l){
  m <- length(Dataframe_clean$category[[i]])
  for(j in 1:m){
    s <- n+j
    if(is.null(Dataframe_clean$location[[i]][["labeledLatLngs"]][[j]]["lat"])){
      Dataframe_final$lat[s] <- "NA"
      Dataframe_final$lon[s] <- "NA"
    }
    else {
      Dataframe_final$lat[s] <- Dataframe_clean$location[[i]][["labeledLatLngs"]][[j]]["lat"]
      Dataframe_final$lon[s] <- Dataframe_clean$location[[i]][["labeledLatLngs"]][[j]]["lng"]
    }
  }
  n <-n+m
}


Dataframe_final = Dataframe_final[, c("venueid", "venuename", "categoryid",  "categoryname", "lat", "lon")]

Dataframe_final = unique(Dataframe_final)

options(digits = 15) 

Dataframe_final$categoryname <- as.character(Dataframe_final$categoryname)
Dataframe_final$categoryid <- as.character(Dataframe_final$categoryid)
Dataframe_final$lat <- as.numeric(Dataframe_final$lat)
Dataframe_final$lon <- as.numeric(Dataframe_final$lon)
Dataframe_final$venuename <- as.character(Dataframe_final$venuename)
Dataframe_final$venueid <- as.character(Dataframe_final$venueid)

Dataframe_final = Dataframe_final[!is.na(Dataframe_final$lat),]

write.csv(as.data.frame(Dataframe_final), paste(city, "_Foursquarevenues_", venuetype, ".csv", sep = ""), row.names=TRUE)
Dataframe_final = read.csv(paste(city, "_Foursquarevenues_", venuetype, ".csv", sep = ""))

##################################################################################################
######## converting Foursquare CSV file to a spatial dataframe within study extent ###############
##################################################################################################

pkgs <- c("sf", "sp", "rgdal", "spatialEco")
sapply(pkgs, require, character.only = T) #load packages
rm(pkgs)

## projecting the dataset
coordinates(Dataframe_final)= ~lon+lat
crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
proj4string(Dataframe_final)=CRS("+proj=longlat +datum=WGS84") 
Dataframe_final = spTransform(Dataframe_final, CRSobj = crs)

## loading the spatial extent polygon
dsn_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"
extent <- readOGR(dsn=dsn_data ,layer="Amsterdam Diemen Oude Amstel Extent")
extent = spTransform(extent, CRSobj = crs)

## clipping spatial dataset by extent
plot(Dataframe_final) # map before clipping
Dataframe_final <- point.in.poly(Dataframe_final, extent, sp = T)
Dataframe_final <- Dataframe_final[!is.na(Dataframe_final@data$gemeenteco),]
plot(Dataframe_final) # map after clipping

writeOGR(Dataframe_final, dsn=getwd() ,layer= paste(city, "_Foursquarevenues_", venuetype, "_", crs_name, sep = ""),driver="ESRI Shapefile")
Dataframe_final = readOGR(dsn=getwd() ,layer= paste(city, "_Foursquarevenues_", venuetype, "_", crs_name, sep = ""))
readO

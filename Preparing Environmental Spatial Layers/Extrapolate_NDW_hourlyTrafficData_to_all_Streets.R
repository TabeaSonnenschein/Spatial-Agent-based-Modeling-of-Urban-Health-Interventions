#########################
### Load packages #######
#########################
pkgs = c("spatialEco", "readxl","GenSynthPop", "rgdal","sp", "sf", "rgeos" , "ggplot2", "matrixStats",  "raster",  "dplyr")
sapply(pkgs[which(sapply(pkgs, require, character.only = T) == FALSE)], install.packages, character.only = T)
sapply(pkgs, require, character.only = T) #load
rm(pkgs)

#########################
### Parameters ##########
#########################
crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"
city = "Amsterdam"

options(digits = 15)

####################################################
### read data and project in correct CRS ###########
####################################################
# extent
dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"
extent = readOGR(dsn=paste(dataFolder, "/SpatialExtent", sep = "" ),layer="Amsterdam Diemen Oude Amstel Extent")
extent = spTransform(extent, CRSobj = crs)

# NDW data
destination_folder = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Traffic/car traffic/may19-march2020workday"
setwd(destination_folder)
NDW_hourly = read.csv("May2019-Mar2020-workday_onestation_hourscolumn.csv")
NDW_hourly = NDW_hourly[, c("station", "TrafVol0_1", "TrafVol1_2", "TrafVol2_3", "TrafVol3_4" , "TrafVol4_5",
                            "TrafVol5_6","TrafVol6_7","TrafVol7_8","TrafVol8_9"  ,"TrafVol9_10","TrafVol10_11",
                            "TrafVol11_12","TrafVol12_13","TrafVol13_14" ,"TrafVol14_15","TrafVol15_16",
                            "TrafVol16_17","TrafVol17_18","TrafVol18_19" ,"TrafVol19_20","TrafVol20_21",
                            "TrafVol21_22","TrafVol22_23","TrafVol23_24", "TrafVol_tot", "Longitude", 
                            "Latitude", "travel_direction") ]
colnames(NDW_hourly)
coordinates(NDW_hourly)= ~Longitude+Latitude
proj4string(NDW_hourly)=CRS("+proj=longlat+datum=WGS84")
NDW_hourly = spTransform(NDW_hourly, CRSobj = crs)

# AMsterdam open data on Traffic Volume
CarStreets = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/cars", sep = ""),layer="Car Traffic_RDNew")
CarStreets = spTransform(CarStreets, CRSobj = crs)

# Speed limit data
StreetLimits = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/cars", sep = ""),layer="Speedlimit_Amsterdam_RDnew")
StreetLimits = spTransform(StreetLimits, CRSobj = crs)

##################################################
### Plot the data ################################
##################################################

ggplot(data = st_as_sf(StreetLimits)) +
  geom_sf(aes(color = as.numeric(StreetLimits$wettelijke)), size= 0.01)+
  scale_colour_viridis_c(option = "D")
complete_data = StreetLimits[!is.na(StreetLimits$TrV0_1),]

png(filename="NDW_spatial_Data.png", width=5600, height=5000, res = 500)
ggplot(data = st_as_sf(NDW_hourly)) +
  geom_sf(aes(color = as.numeric(NDW_hourly$TrafVol_tot)), size= 0.01)+
  scale_colour_viridis_c(option = "D")
dev.off()


ggplot(data = st_as_sf(CarStreets)) +
  geom_sf(aes(color = as.numeric(CarStreets$etmaal)), size= 0.01)+
  scale_colour_viridis_c(option = "D")

#overlay

plot(StreetLimits, col = "red")
plot(CarStreets, col = "green", add = T)
plot(NDW_hourly, col = "blue", add = T)


####################################################
### joining data to Speed Limit df #################
####################################################
NDW_hourly_buffer = st_buffer(st_as_sf(NDW_hourly), 10)

png(filename="spatial_Data.png", width=5600, height=5000, res = 500)
plot(StreetLimits, col = "red")
plot(NDW_hourly_buffer$geometry, col = "green", add = T)
dev.off()


Street_traffic_inters = st_intersection(st_as_sf(StreetLimits), NDW_hourly_buffer)
?st_buffer

plot(Street_traffic_inters$geometry, col = "red")

Street_traffic_inters = as.data.frame(Street_traffic_inters)
newcolumns = c("TrafVol0_1", "TrafVol1_2", "TrafVol2_3", "TrafVol3_4" , "TrafVol4_5",
               "TrafVol5_6","TrafVol6_7","TrafVol7_8","TrafVol8_9"  ,"TrafVol9_10","TrafVol10_11",
               "TrafVol11_12","TrafVol12_13","TrafVol13_14" ,"TrafVol14_15","TrafVol15_16",
               "TrafVol16_17","TrafVol17_18","TrafVol18_19" ,"TrafVol19_20","TrafVol20_21",
               "TrafVol21_22","TrafVol22_23","TrafVol23_24", "TrafVol_tot")
NDW_hourly_buffer

StreetLimits@data[, newcolumns] = NA

for(street in unique(Street_traffic_inters$fid)){
  StreetLimits@data[which(StreetLimits$fid == street), newcolumns]  = colMeans(Street_traffic_inters[which(Street_traffic_inters$fid == street), newcolumns])
}

StreetLimits@data[!is.na(StreetLimits@data$TrafVol1_2),]
colnames(StreetLimits@data)[which(colnames(StreetLimits@data) %in% newcolumns)] = c("TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
                                                                                    "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
                                                                                     "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
                                                                                      "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
                                                                                       "TrV21_22","TrV22_23","TrV23_24", "TrV_tot")
# 1229 streets have traffic volume data

Street_traffic_inters = st_intersection(st_as_sf(StreetLimits["fid"]), st_as_sf(CarStreets))

plot(Street_traffic_inters$geometry, col = "red")

Street_traffic_inters = as.data.frame(Street_traffic_inters)

colnames(Street_traffic_inters)
newcolumns =  c("etmaal","daglv","avondlv" ,"nachtlv","dagmv","avondmv","nachtmv","dagzv","avondzv",
                "nachtzv","dagbus", "avondbus", "nachtbus", "dagtram", "avondtram", "nachttram", 
                "dagmr","avondmr", "nachtmr")


StreetLimits@data[,newcolumns] = NA
Street_traffic_inters[,newcolumns] <- sapply(Street_traffic_inters[,newcolumns],as.numeric)

for(street in unique(Street_traffic_inters$fid)){
  StreetLimits@data[which(StreetLimits$fid == street),newcolumns]  = colMeans(Street_traffic_inters[which(Street_traffic_inters$fid == street), newcolumns])
}

StreetLimits@data[!is.na(StreetLimits@data$etmaal),]

writeOGR(StreetLimits, dsn=getwd() ,layer= "StreetLimits_traffic",driver="ESRI Shapefile")


 # 6065 streets have open traffic volume data                                                                                                                                      
# 
# .	De dag-periode: 07.00-19.00 uur
# .	De avond-periode: 19.00-23.00 uur 
# .	De nacht-periode: 23.00-07.00 uur 

# a.	categorie lv (lichte motorvoertuigen): motorvoertuigen op drie of meer wielen, met uitzondering van de in categorie mv en categorie zv bedoelde motorvoertuigen;
# b.	categorie mv (middelzware motorvoertuigen): gelede en ongelede autobussen, alsmede andere motorvoertuigen die ongeleed zijn en voorzien van een enkele achteras waarop vier banden zijn gemonteerd;
# c.	categorie zv (zware motorvoertuigen): gelede motorvoertuigen, alsmede motorvoertuigen die zijn voorzien van een dubbele achteras, met uitzondering van autobussen.



#########################################################
### Building Regression Models ##########################
#########################################################

regression_df = as.data.frame(StreetLimits@data[!is.na(StreetLimits@data$TrV0_1) & !is.na(StreetLimits@data$etmaal),])
colnames(regression_df)
regression_df
newcolumns =  c("fid", "wettelijke", "TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
                "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
                "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
                "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
                "TrV21_22","TrV22_23","TrV23_24", "TrV_tot", "etmaal","daglv",
                "avondlv" ,"nachtlv","dagmv","avondmv","nachtmv","dagzv","avondzv",
                "nachtzv","dagbus", "avondbus", "nachtbus", "dagtram", "avondtram", "nachttram", 
                "dagmr","avondmr", "nachtmr")
regression_df = regression_df[, newcolumns]
regression_df[,newcolumns] <- sapply(regression_df[,newcolumns],as.numeric)

# night
lm23_24 = lm(TrV23_24~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm23_24)
lm0_1 = lm(TrV0_1~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm0_1)
lm1_2 = lm(TrV1_2~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm1_2)
lm2_3 = lm(TrV2_3~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm2_3)
lm3_4 = lm(TrV3_4~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm3_4)
lm4_5 = lm(TrV4_5~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm4_5)
lm5_6 = lm(TrV5_6~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm5_6)
lm6_7 = lm(TrV6_7~ wettelijke + nachtlv + nachtmv, regression_df)
summary(lm6_7)

#day
lm7_8 = lm(TrV7_8~ wettelijke + daglv + dagmv, regression_df)
summary(lm7_8)
lm8_9 = lm(TrV8_9~ wettelijke + daglv + dagmv, regression_df)
summary(lm8_9)
lm9_10 = lm(TrV9_10~ wettelijke + daglv + dagmv, regression_df)
summary(lm9_10)
lm10_11 = lm(TrV10_11~ wettelijke + daglv + dagmv, regression_df)
summary(lm10_11)
lm11_12 = lm(TrV11_12~ wettelijke + daglv + dagmv, regression_df)
summary(lm11_12)
lm12_13 = lm(TrV12_13~ wettelijke + daglv + dagmv, regression_df)
summary(lm12_13)
lm13_14 = lm(TrV13_14~ wettelijke + daglv + dagmv, regression_df)
summary(lm13_14)
lm14_15 = lm(TrV14_15~ wettelijke + daglv + dagmv, regression_df)
summary(lm14_15)
lm15_16 = lm(TrV15_16~ wettelijke + daglv + dagmv, regression_df)
summary(lm15_16)
lm16_17 = lm(TrV16_17~ wettelijke + daglv + dagmv, regression_df)
summary(lm16_17)
lm17_18 = lm(TrV17_18~ wettelijke + daglv + dagmv, regression_df)
summary(lm17_18)
lm18_19 = lm(TrV18_19~ wettelijke + daglv + dagmv, regression_df)
summary(lm18_19)

#evening
lm19_20 = lm(TrV19_20~ wettelijke + avondlv + avondmv, regression_df)
summary(lm19_20)
lm20_21 = lm(TrV20_21~ wettelijke + avondlv + avondmv, regression_df)
summary(lm20_21)
lm21_22 = lm(TrV21_22~ wettelijke + avondlv + avondmv, regression_df)
summary(lm21_22)
lm22_23 = lm(TrV22_23~ wettelijke + avondlv + avondmv, regression_df)
summary(lm22_23)

#########################################################
### predicting missing values with regressions ##########
#########################################################
StreetLimits@data[,newcolumns] <- sapply(StreetLimits@data[,newcolumns],as.numeric)


pred_idx = which(is.na(StreetLimits@data$TrV0_1) & !is.na(StreetLimits@data$etmaal))
StreetLimits@data[pred_idx,"TrV0_1"] = predict(lm0_1, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])
StreetLimits@data[pred_idx,"TrV1_2"] = predict(lm1_2, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])
StreetLimits@data[pred_idx,"TrV2_3"] = predict(lm2_3, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])
StreetLimits@data[pred_idx,"TrV3_4"] = predict(lm3_4, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])
StreetLimits@data[pred_idx,"TrV4_5"] = predict(lm4_5, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])
StreetLimits@data[pred_idx,"TrV5_6"] = predict(lm5_6, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])
StreetLimits@data[pred_idx,"TrV6_7"] = predict(lm6_7, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])
StreetLimits@data[pred_idx,"TrV7_8"] = predict(lm7_8, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV8_9"] = predict(lm8_9, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV9_10"] = predict(lm9_10, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV10_11"] = predict(lm10_11, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV11_12"] = predict(lm11_12, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV12_13"] = predict(lm12_13, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV13_14"] = predict(lm13_14, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV14_15"] = predict(lm14_15, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV15_16"] = predict(lm15_16, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV16_17"] = predict(lm16_17, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV17_18"] = predict(lm17_18, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV18_19"] = predict(lm18_19, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "dagmv")])
StreetLimits@data[pred_idx,"TrV19_20"] = predict(lm19_20, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "avondmv")])
StreetLimits@data[pred_idx,"TrV20_21"] = predict(lm20_21, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "avondmv")])
StreetLimits@data[pred_idx,"TrV21_22"] = predict(lm21_22, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "avondmv")])
StreetLimits@data[pred_idx,"TrV22_23"] = predict(lm22_23, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "avondmv")])
StreetLimits@data[pred_idx,"TrV23_24"] = predict(lm23_24, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "nachtmv")])


complete_data = StreetLimits[!is.na(StreetLimits$TrV0_1),]
png(filename="extrapolated_spatial_Data0_1.png", width=5600, height=5000, res = 500)
ggplot(data = st_as_sf(complete_data)) +
  geom_sf(aes(color = as.numeric(complete_data$TrV0_1)), size= 0.01)+
  scale_colour_viridis_c(option = "D")
dev.off()

png(filename="extrapolated_spatial_Data7_8.png", width=5600, height=5000, res = 500)
ggplot(data = st_as_sf(complete_data)) +
  geom_sf(aes(color = as.numeric(complete_data$TrV7_8)), size= 0.01)+
  scale_colour_viridis_c(option = "D")
dev.off()

png(filename="extrapolated_spatial_Data15_16.png", width=5600, height=5000, res = 500)
ggplot(data = st_as_sf(complete_data)) +
  geom_sf(aes(color = as.numeric(complete_data$TrV15_16)), size= 0.01)+
  scale_colour_viridis_c(option = "D")
dev.off()


writeOGR(complete_data, dsn=getwd() ,layer= "TrafficVolume_interpolated",driver="ESRI Shapefile")

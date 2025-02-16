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
dataFolder= "D:/PhD EXPANSE/Data/Amsterdam"
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
proj4string(NDW_hourly) = CRS("+init=EPSG:4326")
NDW_hourly = spTransform(NDW_hourly, CRSobj = crs)

# AMsterdam open data on Traffic Volume
CarStreets = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/cars", sep = ""),layer="Car Traffic_RDNew")
CarStreets = spTransform(CarStreets, CRSobj = crs)

# Speed limit data
StreetLimits = readOGR(dsn=paste(dataFolder, "/Built Environment/Transport Infrastructure/cars", sep = ""),layer="Speedlimit_Amsterdam_RDnew")
StreetLimits = spTransform(StreetLimits, CRSobj = crs)
Streetlimits_all = StreetLimits

# raster
AirPollRaster = readOGR(dsn=paste(dataFolder, "/Air Pollution Determinants", sep = ""), layer = "AirPollDeterm_grid50")
AirPollRaster = spTransform(AirPollRaster, CRSobj = crs)

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
StreetLimits = readOGR( dsn=getwd() ,layer= "StreetLimits_traffic")
StreetLimit_predictall = StreetLimits
 # 6065 streets have open traffic volume data                                                                                                                                      
# 
# .	De dag-periode: 07.00-19.00 uur
# .	De avond-periode: 19.00-23.00 uur 
# .	De nacht-periode: 23.00-07.00 uur 

# a.	categorie lv (lichte motorvoertuigen): motorvoertuigen op drie of meer wielen, met uitzondering van de in categorie mv en categorie zv bedoelde motorvoertuigen;
# b.	categorie mv (middelzware motorvoertuigen): gelede en ongelede autobussen, alsmede andere motorvoertuigen die ongeleed zijn en voorzien van een enkele achteras waarop vier banden zijn gemonteerd;
# c.	categorie zv (zware motorvoertuigen): gelede motorvoertuigen, alsmede motorvoertuigen die zijn voorzien van een dubbele achteras, met uitzondering van autobussen.


#################################################
###### Agggregating in Raster ############
##################################

measures = point.in.poly(NDW_hourly, AirPollRaster, duplicate = T)

plot(measures, col = "red")

measures = as.data.frame(measures)
newcolumns = c("TrafVol0_1", "TrafVol1_2", "TrafVol2_3", "TrafVol3_4" , "TrafVol4_5",
               "TrafVol5_6","TrafVol6_7","TrafVol7_8","TrafVol8_9"  ,"TrafVol9_10","TrafVol10_11",
               "TrafVol11_12","TrafVol12_13","TrafVol13_14" ,"TrafVol14_15","TrafVol15_16",
               "TrafVol16_17","TrafVol17_18","TrafVol18_19" ,"TrafVol19_20","TrafVol20_21",
               "TrafVol21_22","TrafVol22_23","TrafVol23_24", "TrafVol_tot")
NDW_hourly_buffer

AirPollRaster@data[, newcolumns] = NA

for(cell in unique(measures$int_id)){
  AirPollRaster@data[which(AirPollRaster$int_id == cell), newcolumns]  = colMeans(measures[which(measures$int_id == cell), newcolumns])
}

AirPollRaster@data[!is.na(AirPollRaster@data$TrafVol1_2),]
colnames(AirPollRaster@data)[which(colnames(AirPollRaster@data) %in% newcolumns)] = c("TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
                                                                                      "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
                                                                                      "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
                                                                                      "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
                                                                                      "TrV21_22","TrV22_23","TrV23_24", "TrV_tot")
                                                                                  

AirPollRaster_inters = st_intersection(st_as_sf(AirPollRaster["int_id"]), st_as_sf(CarStreets))
plot(AirPollRaster_inters$geometry, col = "red")
AirPollRaster_inters = as.data.frame(AirPollRaster_inters)

colnames(AirPollRaster_inters)
newcolumns =  c("etmaal","daglv","avondlv" ,"nachtlv","dagmv","avondmv","nachtmv","dagzv","avondzv",
                "nachtzv","dagbus", "avondbus", "nachtbus", "dagtram", "avondtram", "nachttram", 
                "dagmr","avondmr", "nachtmr")


AirPollRaster@data[,newcolumns] = NA
AirPollRaster_inters[,newcolumns] <- sapply(AirPollRaster_inters[,newcolumns],as.numeric)

for(cell in unique(AirPollRaster_inters$int_id)){
  AirPollRaster@data[which(AirPollRaster$int_id == cell), newcolumns]  = colMeans(AirPollRaster_inters[which(AirPollRaster_inters$int_id == cell), newcolumns])
}

AirPollRaster@data[!is.na(AirPollRaster@data$etmaal),]


colnames(StreetLimits@data)
StreetLimits = StreetLimits[,c("fid", "wettelijke")]
AirPollRaster_inters = st_intersection(st_as_sf(AirPollRaster["int_id"]), st_as_sf(StreetLimits))
plot(AirPollRaster_inters$geometry, col = "red")
AirPollRaster_inters = as.data.frame(AirPollRaster_inters)


colnames(AirPollRaster_inters)
newcolumns =  c("wettelijke")

AirPollRaster@data[,newcolumns] = NA
AirPollRaster_inters[,newcolumns] <- sapply(AirPollRaster_inters[,newcolumns],as.numeric)

for(cell in unique(AirPollRaster_inters$int_id)){
  AirPollRaster@data[which(AirPollRaster$int_id == cell), newcolumns]  = mean(AirPollRaster_inters[which(AirPollRaster_inters$int_id == cell), newcolumns])
}

AirPollRaster@data[!is.na(AirPollRaster@data$wettelijke),]


#########################################################
### Building Regression Models ##########################
#########################################################
regression_df_Street = regression_df
regression_df = as.data.frame(StreetLimits@data[!is.na(StreetLimits@data$TrV0_1) & !is.na(StreetLimits@data$etmaal),])
regression_df = as.data.frame(AirPollRaster@data[!is.na(AirPollRaster@data$TrV0_1) & !is.na(AirPollRaster@data$etmaal),]
)
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
lm23_24 = lm(TrV23_24~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm23_24)
lm0_1 = lm(TrV0_1~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm0_1)
lm1_2 = lm(TrV1_2~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm1_2)
lm2_3 = lm(TrV2_3~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm2_3)
lm3_4 = lm(TrV3_4~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm3_4)
lm4_5 = lm(TrV4_5~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm4_5)
lm5_6 = lm(TrV5_6~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm5_6)
lm6_7 = lm(TrV6_7~ wettelijke + nachtlv + etmaal, regression_df)
summary(lm6_7)

#day
lm7_8 = lm(TrV7_8~ wettelijke + daglv + etmaal, regression_df)
summary(lm7_8)
lm8_9 = lm(TrV8_9~ wettelijke + daglv + etmaal, regression_df)
summary(lm8_9)
lm9_10 = lm(TrV9_10~ wettelijke + daglv + etmaal, regression_df)
summary(lm9_10)
lm10_11 = lm(TrV10_11~ wettelijke + daglv + etmaal, regression_df)
summary(lm10_11)
lm11_12 = lm(TrV11_12~ wettelijke + daglv + etmaal, regression_df)
summary(lm11_12)
lm12_13 = lm(TrV12_13~ wettelijke + daglv + etmaal, regression_df)
summary(lm12_13)
lm13_14 = lm(TrV13_14~ wettelijke + daglv + etmaal, regression_df)
summary(lm13_14)
lm14_15 = lm(TrV14_15~ wettelijke + daglv + etmaal, regression_df)
summary(lm14_15)

lm15_16 = lm(TrV15_16~ wettelijke + daglv + etmaal, regression_df)
summary(lm15_16)
lm16_17 = lm(TrV16_17~ wettelijke + daglv + etmaal, regression_df)
summary(lm16_17)
lm17_18 = lm(TrV17_18~ wettelijke + daglv + etmaal, regression_df)
summary(lm17_18)
lm18_19 = lm(TrV18_19~ wettelijke + daglv + etmaal, regression_df)
summary(lm18_19)

#evening
lm19_20 = lm(TrV19_20~ wettelijke + avondlv + etmaal, regression_df)
summary(lm19_20)
lm20_21 = lm(TrV20_21~ wettelijke + avondlv + etmaal, regression_df)
summary(lm20_21)
lm21_22 = lm(TrV21_22~ wettelijke + avondlv + etmaal, regression_df)
summary(lm21_22)
lm22_23 = lm(TrV22_23~ wettelijke + avondlv + etmaal, regression_df)
summary(lm22_23)

#########################################################
### predicting missing values with regressions ##########
#########################################################
beforeinterpol = StreetLimits
StreetLimits = beforeinterpol
StreetLimits@data[,newcolumns] <- sapply(StreetLimits@data[,newcolumns],as.numeric)


pred_idx = which(is.na(StreetLimits@data$TrV0_1) & !is.na(StreetLimits@data$etmaal))
StreetLimits@data[pred_idx,"TrV0_1"] = predict(lm0_1, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV1_2"] = predict(lm1_2, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV2_3"] = predict(lm2_3, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV3_4"] = predict(lm3_4, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV4_5"] = predict(lm4_5, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV5_6"] = predict(lm5_6, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV6_7"] = predict(lm6_7, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV7_8"] = predict(lm7_8, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV8_9"] = predict(lm8_9, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV9_10"] = predict(lm9_10, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV10_11"] = predict(lm10_11, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV11_12"] = predict(lm11_12, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV12_13"] = predict(lm12_13, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV13_14"] = predict(lm13_14, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV14_15"] = predict(lm14_15, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV15_16"] = predict(lm15_16, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV16_17"] = predict(lm16_17, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV17_18"] = predict(lm17_18, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV18_19"] = predict(lm18_19, newdata = StreetLimits[pred_idx, c("wettelijke", "daglv", "etmaal")])
StreetLimits@data[pred_idx,"TrV19_20"] = predict(lm19_20, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV20_21"] = predict(lm20_21, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV21_22"] = predict(lm21_22, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV22_23"] = predict(lm22_23, newdata = StreetLimits[pred_idx, c("wettelijke", "avondlv", "etmaal")])
StreetLimits@data[pred_idx,"TrV23_24"] = predict(lm23_24, newdata = StreetLimits[pred_idx, c("wettelijke", "nachtlv", "etmaal")])



minusnumbers = c()
for(x in c("TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
           "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
           "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
           "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
           "TrV21_22","TrV22_23","TrV23_24")){
  print(x)
  print(length(which(StreetLimits@data[,c(x)]< 0)))
  if(length(which(StreetLimits@data[,c(x)]< 0)) > 0){
    minusnumbers= append(minusnumbers, x)
  }
}


i = 17
pred_idx = which(StreetLimits@data[,c(minusnumbers[i])]< 0)
print(minusnumbers[i])
lm = lm(TrV23_24 ~  TrV22_23 , regression_df)
summary(lm)
StreetLimits@data[pred_idx,
                  minusnumbers[i]] = predict(lm, 
                                             newdata = 
                                                 StreetLimits[pred_idx, c("TrV22_23")])


##############
### extrapolating to neighboring streets
beforeextraextra = StreetLimits
StreetLimits2 = beforeextraextra
nodata = unique(StreetLimits$fid[is.na(StreetLimits2$TrV0_1)])
StreetLimits$interpolated_neighb = 0
StreetLimits$interpolated_neighb[which(StreetLimits$fid %in% nodata)] = 1
StreetLimits$hasmeasureddata = 0
StreetLimits$hasmeasureddata[which(StreetLimits$fid %in% unique(regression_df$fid))] = 1
StreetLimits$interpol_aggtrafficspeedlimit = 0
StreetLimits$interpol_aggtrafficspeedlimit[which((StreetLimits$interpolated_neighb == 0) & (StreetLimits$hasmeasureddata == 0))] = 1

street_inters = st_intersection(st_as_sf(StreetLimits["fid"]), st_as_sf(StreetLimits["fid"]))
street_inters = as.data.frame(street_inters)
newcolumns = c("TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
               "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
               "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
               "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
               "TrV21_22","TrV22_23","TrV23_24")

for(street in nodata){
  neighborstreets = street_inters$fid.1[which(street_inters$fid == street)]
  for(x in newcolumns){
    StreetLimits@data[which(StreetLimits$fid == street),x]  = mean(na.omit(StreetLimits@data[which(StreetLimits$fid %in% neighborstreets), x]))
    }
  # StreetLimits@data[which(StreetLimits$fid == street),newcolumns]  = colMeans(StreetLimits@data[which(StreetLimits$fid %in% neighborstreets), newcolumns])
}


################################
### viewing and writing data 
###############################
colnames(complete_data@data) 
complete_data = StreetLimits[!is.na(StreetLimits$TrV0_1),]
colnames(complete_data@data) = c("fid","SpeedLimit" ,"TrV0_1","TrV1_2" , 
                                 "TrV2_3","TrV3_4","TrV4_5","TrV5_6"  ,"TrV6_7",
                                 "TrV7_8"  , "TrV8_9","TrV9_10" , "TrV10_11",
                                 "TrV11_12" , "TrV12_13","TrV13_14" ,"TrV14_15",
                                 "TrV15_16", "TrV16_17","TrV17_18" , "TrV18_19",
                                 "TrV19_20" , "TrV20_21","TrV21_22","TrV22_23",
                                 "TrV23_24", "TrV_tot","etmaal" ,"daglv","avondlv" ,
                                 "nachtlv","dagmv" ,"avondmv","nachtmv"  ,"dagzv",
                                 "avondzv", "nachtzv","dagbus"   ,"avondbus",
                                 "nachtbus"  ,"dagtram","avondtram", "nachttram",
                                 "dagmr", "avondmr","nachtmr","SpatInterp",
                                 "MeasuData","RegInterp")

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

setwd("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Traffic/car traffic/may19-march2020workday/TrafficVolumeRawValuesANDinterpolation")
writeOGR(complete_data, dsn=getwd() ,layer= "TrafficVolume_interpolated_allstreets_clean",driver="ESRI Shapefile")
complete_data = readOGR(getwd(), layer = "TrafficVolume_interpolated_allstreets_clean")
data = as.data.frame(complete_data)
plot(complete_data)


subset = complete_data[which((complete_data$SpeedLimit <= 30) & (complete_data$TrV17_18 > 1000)),]
subset = as.data.frame(subset)
ggplot(data = st_as_sf(subset)) +
  geom_sf(aes(color = as.numeric(subset$TrV15_16)), size= 0.01)+
  scale_colour_viridis_c(option = "D")
overestimations = subset$fid

subset30 = complete_data[which((complete_data$SpeedLimit == 30)),]
subset30 = as.data.frame(subset30)
mean(subset$TrV14_15)

newcolumns = c("TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
               "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
               "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
               "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
               "TrV21_22","TrV22_23","TrV23_24")


complete_data@data[which(complete_data$fid %in% overestimations),newcolumns] = complete_data@data[which(complete_data$fid %in% overestimations),newcolumns] * 0.5

data = as.data.frame(complete_data)

##############################################
#### Aggregating in Air poll raster  TraffV
#####################################
memory.limit(2000000)
cellsize = "50m"
AirPollRaster = readOGR(dsn=paste(dataFolder, "/Air Pollution Determinants", sep = ""), layer = paste0("AirPollDeterm_grid", cellsize))

# TraffVolume
AirPollRaster_inters = st_intersection(st_as_sf(AirPollRaster["int_id"]), st_as_sf(complete_data))
AirPollRaster@data[,newcolumns] = NA
AirPollRaster_inters = as.data.frame(AirPollRaster_inters)
AirPollRaster_inters[,newcolumns] <- sapply(AirPollRaster_inters[,newcolumns],as.numeric)

n.cores <- parallel::detectCores() - 3
my.cluster <- parallel::makeCluster(
  n.cores, 
  type = "PSOCK"
)
print(my.cluster)
doParallel::registerDoParallel(cl = my.cluster)
foreach::getDoParRegistered()
foreach::getDoParWorkers()
clusterExport(my.cluster, varlist = c("AirPollRaster_inters","newcolumns"))

remove(TraffAggr)
TraffAggr = foreach(intid = unique(AirPollRaster_inters$int_id), .combine = 'rbind') %dopar% {
  colMeans(AirPollRaster_inters[which(AirPollRaster_inters$int_id == intid), newcolumns])
}

writeOGR(AirPollRaster, dsn=paste0(dataFolder, "/Air Pollution Determinants"), layer =paste0("AirPollDeterm_grid", cellsize,"_TraffVol"),driver="ESRI Shapefile")
AirPollRaster_data = as.data.frame(AirPollRaster)
write.csv(AirPollRaster_data, paste0("AirPollRaster",cellsize, "_TraffVdata.csv"), row.names = F)

#TraffIntensity
TrIcols = c("TrI0_1", "TrI1_2", "TrI2_3", "TrI3_4" , "TrI4_5", 
               "TrI5_6","TrI6_7","TrI7_8","TrI8_9"  ,"TrI9_10","TrI10_11",
               "TrI11_12","TrI12_13","TrI13_14" ,"TrI14_15","TrI15_16",
               "TrI16_17","TrI17_18","TrI18_19" ,"TrI19_20","TrI20_21",
               "TrI21_22","TrI22_23","TrI23_24")
newcolumns = c("TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
               "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
               "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
               "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
               "TrV21_22","TrV22_23","TrV23_24")
AirPollRaster_inters = st_intersection(st_as_sf(AirPollRaster["int_id"]), st_as_sf(complete_data))
length_per_segment <- st_length(AirPollRaster_inters)
AirPollRaster_inters$length_per_segment <- length_per_segment
AirPollRaster@data[,TrIcols] = NA
AirPollRaster_inters = as.data.frame(AirPollRaster_inters)
AirPollRaster_inters[,newcolumns] <- sapply(AirPollRaster_inters[,newcolumns],as.numeric)
for(i in 1:length(TrIcols)){
  AirPollRaster_inters[,TrIcols[i]] <- AirPollRaster_inters[,newcolumns[i]]*AirPollRaster_inters$length_per_segment
}

for(cell in unique(AirPollRaster_inters$int_id)){
  print(cell)
  AirPollRaster@data[which(AirPollRaster$int_id == cell), TrIcols]  = colSums(AirPollRaster_inters[which(AirPollRaster_inters$int_id == cell), TrIcols])
}

# calculate total street length per cell
AirPollRaster@data[, "StreetLength"] = 0
for(cell in unique(AirPollRaster_inters$int_id)){
  AirPollRaster@data[which(AirPollRaster$int_id == cell), "StreetLength"]  = sum(AirPollRaster_inters$length_per_segment[which(AirPollRaster_inters$int_id == cell)])
}

StreetLength = as.data.frame(AirPollRaster[,c("int_id", "StreetLength")])
write.csv(StreetLength, paste0("StreetLength_",cellsize, ".csv"), row.names = F)


writeOGR(AirPollRaster, dsn=getwd(), layer = paste0("AirPollDeterm_grid", cellsize,"_TraffVol"),driver="ESRI Shapefile")
writeOGR(AirPollRaster, dsn=paste0(dataFolder, "/Air Pollution Determinants"), layer =paste0("AirPollDeterm_grid", cellsize,"_TraffIntensity"),driver="ESRI Shapefile")

ggplot(data = st_as_sf(AirPollRaster)) +
  geom_sf(aes(color = as.numeric(AirPollRaster$TrV15_16)), size= 0.01)+
  scale_colour_viridis_c(option = "D")


setwd(paste(dataFolder, "/Air Pollution Determinants", sep = ""))

AirPollRaster_data = as.data.frame(AirPollRaster)
write.csv(AirPollRaster_data, paste0("AirPollRaster",cellsize, "_TraffIntensdata.csv"), row.names = F)

AirPollDeterm_grid= read.csv("AirPollDeterm_grid50_baselineNO2.csv")
AirPollDeterm_grid = merge(AirPollDeterm_grid, AirPollRaster_data, by = "int_id", all.x = T, all.y = F)

columns = c("int_id", "baseline_NO2", "TrV0_1", "TrV1_2", "TrV2_3", "TrV3_4" , "TrV4_5", 
  "TrV5_6","TrV6_7","TrV7_8","TrV8_9"  ,"TrV9_10","TrV10_11",
  "TrV11_12","TrV12_13","TrV13_14" ,"TrV14_15","TrV15_16",
  "TrV16_17","TrV17_18","TrV18_19" ,"TrV19_20","TrV20_21",
  "TrV21_22","TrV22_23","TrV23_24")

AirPollDeterm_grid = AirPollDeterm_grid[, columns]
AirPollDeterm_grid = AirPollDeterm_grid[!is.na(AirPollDeterm_grid$TrV0_1),]

write.csv(AirPollDeterm_grid, "AirPollDeterm_grid50_baselineNO2TrafficV.csv", row.names = F)

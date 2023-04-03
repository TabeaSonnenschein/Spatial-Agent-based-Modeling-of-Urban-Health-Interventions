
pkgs = c("geojsonsf","mapview", "simecol", "stringr", "maptools","raster", "rgdal","sp", "sf", "jpeg", "data.table", "purrr", "rgeos" , "leaflet", "RColorBrewer",
         "ggplot2", "lattice",  "raster",  "spatialEco", "rjson", "jsonlite","EconGeo", "dplyr",
         "rstan", "boot",  "concaveman", "data.tree", "DiagrammeR", "networkD3", "rgexf", "tidytree", "exactextractr", "terra")
sapply(pkgs, require, character.only = T) #load
rm(pkgs)

 install.packages("simecol")

dataFolder= "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam"

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"


setwd(paste(dataFolder, "/Air Pollution Determinants", sep = ""))
airpoll_grid = readOGR(dsn=getwd(),layer="AirPollDeterm_grid50_clean")
airpoll_grid_raster <- raster("AirPollDeterm_grid.tif")
airpoll_road_data = read.csv("AirPollDeterm_grid50_baselineNO2.csv")
AirPoll_data = read.csv("AirPollgrid50_JulesData.csv")

airpoll_grid_raster = raster::setValues(airpoll_grid_raster, as.numeric(AirPoll_data$baseline_NO2))
raster::writeRaster(airpoll_grid_raster, "baselineNO2.tif", format = "GTiff", overwrite = T)

summary(airpoll_grid_raster@data@values)

ncol(airpoll_grid_raster)
462
nrow(airpoll_grid_raster)
403


rowsidx = c()
for(i in 0:402){
  rowsidx= append(rowsidx, base::rep(i, 462))
}
columnsidx = base::rep(c(0:461), 403)
airpoll_grid_raster@data@values = rowsidx
plot(airpoll_grid_raster)

airpoll_grid_centroids = gCentroid(airpoll_grid, byid= T, id= airpoll_grid$int_id)
airpoll_grid_centroids$int_id = airpoll_grid$int_id
onroad_centroids = airpoll_grid_centroids[which(airpoll_grid_centroids$int_id %in% airpoll_road_data$int_id),]
offroad_centroids = airpoll_grid_centroids[which(!(airpoll_grid_centroids$int_id %in% airpoll_road_data$int_id)),]

airpoll_grid_centroids_sf = st_as_sf(airpoll_grid_centroids)
offroad_centroids_sf = st_as_sf(offroad_centroids)
offroad_centroids_sf <- st_transform(offroad_centroids_sf, 5880) # transform to your desired proj (unit = m)
onroad_centroids_sf = st_as_sf(onroad_centroids)
onroad_centroids_sf <- st_transform(onroad_centroids_sf, 5880) # transform to your desired proj (unit = m)
dist_matrix   <- st_distance(offroad_centroids_sf, onroad_centroids_sf)           # creates a matrix of distances


### Predicting air pollution on street
airpoll_road_data = read.csv("AirPollDeterm_grid50_baselineNO2.csv")

airpoll_grid_df$baseline_NO2 = ((0.03674*airpoll_grid_df$MRDL_50)+(0.0003893*airpoll_grid_df$MRDL_1000)+(0.0000001947*airpoll_grid_df$PORT_5000)
                                      +(0.00000009322*airpoll_grid_df$NATUR_5000)+(0.00002501569856*airpoll_grid_df$WATER_300)+(-0.00000012378*airpoll_grid_df$AGRI_5000)
                                      +(0.0000023913*airpoll_grid_df$WATER_1000)+(0.000000075646*airpoll_grid_df$INDUS_5000)+(0.000001146341*airpoll_grid_df$TRANS_5000)
                                      +(0.0005998852028*airpoll_grid_df$MRDL_500)+(0.000126780269*airpoll_grid_df$AGRI_100)+(0.000003866912*airpoll_grid_df$TRANS_1000)
                                      +(0.000021276669*airpoll_grid_df$INDUS_100)+(-0.000000242883*airpoll_grid_df$AIR_5000)+(0.0001063379026*airpoll_grid_df$POP_1000))

airpoll_road_data$NO2_0_1 = (1.992+(0.03096377438925*airpoll_road_data$TrV0_1)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_1_2 = (1.992+(0.03096377438925*airpoll_road_data$TrV1_2)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_2_3 = (1.992+(0.03096377438925*airpoll_road_data$TrV2_3)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_3_4 = (1.992+(0.03096377438925*airpoll_road_data$TrV3_4)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_4_5 = (1.992+(0.03096377438925*airpoll_road_data$TrV4_5)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_5_6 = (1.992+(0.03096377438925*airpoll_road_data$TrV5_6)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_6_7 = (1.992+(0.03096377438925*airpoll_road_data$TrV6_7)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_7_8 = (1.992+(0.03096377438925*airpoll_road_data$TrV7_8)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_8_9 = (1.992+(0.03096377438925*airpoll_road_data$TrV8_9)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_9_10 = (1.992+(0.03096377438925*airpoll_road_data$TrV9_10)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_10_11 = (1.992+(0.03096377438925*airpoll_road_data$TrV10_11)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_11_12 = (1.992+(0.03096377438925*airpoll_road_data$TrV11_12)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_12_13 = (1.992+(0.03096377438925*airpoll_road_data$TrV12_13)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_13_14 = (1.992+(0.03096377438925*airpoll_road_data$TrV13_14)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_14_15 = (1.992+(0.03096377438925*airpoll_road_data$TrV14_15)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_15_16 = (1.992+(0.03096377438925*airpoll_road_data$TrV15_16)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_16_17 = (1.992+(0.03096377438925*airpoll_road_data$TrV16_17)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_17_18 = (1.992+(0.03096377438925*airpoll_road_data$TrV17_18)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_18_19 = (1.992+(0.03096377438925*airpoll_road_data$TrV18_19)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_19_20 = (1.992+(0.03096377438925*airpoll_road_data$TrV19_20)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_20_21 = (1.992+(0.03096377438925*airpoll_road_data$TrV20_21)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_21_22 = (1.992+(0.03096377438925*airpoll_road_data$TrV21_22)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_22_23 = (1.992+(0.03096377438925*airpoll_road_data$TrV22_23)+ airpoll_road_data$baseline_NO2)
airpoll_road_data$NO2_23_24 = (1.992+(0.03096377438925*airpoll_road_data$TrV23_24)+ airpoll_road_data$baseline_NO2)

AirPoll_data = read.csv("AirPollgrid50_JulesData.csv")
AirPoll_data = AirPoll_data[,c("int_id","ON_ROAD","MRDL_50","MRDL_1000","PORT_5000","NATUR_5000","WATER_300",
                "AGRI_5000","WATER_1000","INDUS_5000", "TRANS_5000", "MRDL_500","AGRI_100",
                "TRANS_1000", "INDUS_100","AIR_5000" ,"POP_1000","GreenCover") ]

AirPoll_data = merge(AirPoll_data, airpoll_road_data, by = "int_id", all = T)

AirPoll_data$rowindex = rowsidx
AirPoll_data$colindex = columnsidx 

####################################################
### Adding off-road measurement data ###############
####################################################

# Palmes Tubes, not hourly
Palmes_OffRoadData <- geojson_sf("D:/PhD EXPANSE/Data/Amsterdam/Air Pollution Determinants/PalmesOffRoadMeasurements/ams_palmes_only_agg_sf.geojson")
colnames(Palmes_OffRoadData)
airpoll_grid_df = as.data.frame(airpoll_grid)
OffRoadData_df = as.data.frame(OffRoadData)
colnames(OffRoadData_df)
OffRoadData_df = OffRoadData_df[,c("int_id", "palmes_no2_20192020_75p")]
joined = merge(airpoll_grid_df, OffRoadData_df, by = "int_id", all = T)
joined_complete = joined[!is.na(joined$palmes_no2_20192020_75p),]
joined_complete_onroad = joined_complete[joined_complete$ON_ROAD == 0,]
colnames(joined_complete_onroad)

# RIVM hourly data
RIVM_hourly_OffRoadData = read.csv2("D:/PhD EXPANSE/Data/Amsterdam/Air Pollution Determinants/RIVMhourlyOffRoadData/2019/2019_NO2.csv")
nl_hourly_rivm_2019_NO2 = RIVM_hourly_OffRoadData[,c(5:ncol(RIVM_hourly_OffRoadData))]
nl_hourly_rivm_2019_NO2_coords = as.data.frame(t(nl_hourly_rivm_2019_NO2[1:2,]))
colnames(nl_hourly_rivm_2019_NO2_coords) = c("Stationsnaam","coords")
nl_hourly_rivm_2019_NO2_coords$stationCode = rownames(nl_hourly_rivm_2019_NO2_coords)
nl_hourly_rivm_2019_NO2_coords= nl_hourly_rivm_2019_NO2_coords[c(2:nrow(nl_hourly_rivm_2019_NO2_coords)),]
class(nl_hourly_rivm_2019_NO2_coords$coords)
rownames(nl_hourly_rivm_2019_NO2_coords) = c(1:nrow(nl_hourly_rivm_2019_NO2_coords))
write.csv(nl_hourly_rivm_2019_NO2_coords, "Stations_RIVM_Data.csv")

nl_hourly_rivm_2019_NO2_coords_sf = nl_hourly_rivm_2019_NO2_coords %>%
  mutate(geom = gsub(coords,pattern="(\\))|(\\()",replacement = ""))%>%
  tidyr::separate(geom,into=c("lon","lat"),sep=",")%>%
  st_as_sf(.,coords=c("lat","lon"),crs=4326)


nl_hourly_rivm_2019_NO2_coords_sf = st_make_valid(nl_hourly_rivm_2019_NO2_coords_sf)
mapview(nl_hourly_rivm_2019_NO2_coords_sf)

nl_hourly_rivm_2019_NO2_coords_sp = as_Spatial(nl_hourly_rivm_2019_NO2_coords_sf)
nl_hourly_rivm_2019_NO2_coords_sp = spTransform(nl_hourly_rivm_2019_NO2_coords_sp, CRSobj = crs)
airpoll_grid = readOGR(dsn=getwd(),layer="AirPollDeterm_grid50_clean")
airpoll_grid_Stationjoin = point.in.poly(nl_hourly_rivm_2019_NO2_coords_sp, airpoll_grid)
airpoll_grid_Stationjoin_df = as.data.frame(airpoll_grid_Stationjoin)
gridjoin_measurements = airpoll_grid_Stationjoin_df[!is.na(airpoll_grid_Stationjoin_df$int_id),c("stationCode", "Stationsnaam", "int_id", "coords.x1", "coords.x2")]
rownames(gridjoin_measurements) = gridjoin_measurements$stationCode


Amsterdam_RIVMdata = nl_hourly_rivm_2019_NO2[8:nrow(nl_hourly_rivm_2019_NO2),c("StationsCode",unique(gridjoin_measurements$stationCode))]
Amsterdam_RIVMdata$hour = str_sub(Amsterdam_RIVMdata$StationsCode, 10, 14)


gridjoin_measurements[, c("yearMeanNO2_0_1")]

for(station in unique(gridjoin_measurements$stationCode)){
  gridjoin_measurements[station, "yearMeanNO2_0_1"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "01:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_1_2"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "02:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_2_3"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "03:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_3_4"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "04:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_4_5"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "05:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_5_6"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "06:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_6_7"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "07:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_7_8"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "08:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_8_9"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "09:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_9_10"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "10:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_10_11"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "11:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_11_12"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "12:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_12_13"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "13:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_13_14"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "14:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_14_15"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "15:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_15_16"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "16:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_16_17"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "17:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_17_18"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "18:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_18_19"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "19:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_19_20"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "20:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_20_21"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "21:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_21_22"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "22:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_22_23"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "23:00", station])))
  gridjoin_measurements[station, "yearMeanNO2_23_24"] = mean(na.omit(as.numeric(Amsterdam_RIVMdata[Amsterdam_RIVMdata$hour == "00:00", station])))
  
}


AirPoll_data$baseline_NO2 = (1.992 + (0.03674*AirPoll_data$MRDL_50)+(0.0003893*AirPoll_data$MRDL_1000)+(0.0000001947*AirPoll_data$PORT_5000)
                                +(0.00000009322*AirPoll_data$NATUR_5000)+(0.00002501569856*AirPoll_data$WATER_300)+(-0.00000012378*AirPoll_data$AGRI_5000)
                                +(0.0000023913*AirPoll_data$WATER_1000)+(0.000000075646*AirPoll_data$INDUS_5000)+(0.000001146341*AirPoll_data$TRANS_5000)
                                +(0.0005998852028*AirPoll_data$MRDL_500)+(0.000126780269*AirPoll_data$AGRI_100)+(0.000003866912*AirPoll_data$TRANS_1000)
                                +(0.000021276669*AirPoll_data$INDUS_100)+(-0.000000242883*AirPoll_data$AIR_5000)+(0.0001063379026*AirPoll_data$POP_1000))

AirPoll_data = read.csv("DispersionModeldata.csv")
AirPoll_data$rowcol = paste0(AirPoll_data$rowindex, " ", AirPoll_data$colindex)
AirPoll_data$rowcol
AirPoll_data = merge(AirPoll_data, gridjoin_measurements, by = "int_id", all = T)
write.csv(AirPoll_data,"DispersionModeldata.csv", row.names = F)
AirPoll_data$rowindex
write.csv(AirPoll_data[,c("baseline_NO2")],"DispersionModel_baselineNO2.csv", row.names = F)
write.csv2(AirPoll_data[!is.na(AirPoll_data$yearMeanNO2_0_1),c("rowcol", "yearMeanNO2_0_1","yearMeanNO2_1_2","yearMeanNO2_2_3","yearMeanNO2_3_4", 
                          "yearMeanNO2_4_5","yearMeanNO2_5_6","yearMeanNO2_6_7","yearMeanNO2_7_8",
                          "yearMeanNO2_8_9","yearMeanNO2_9_10","yearMeanNO2_10_11", "yearMeanNO2_11_12",
                          "yearMeanNO2_12_13","yearMeanNO2_13_14", "yearMeanNO2_14_15", "yearMeanNO2_15_16",
                          "yearMeanNO2_16_17","yearMeanNO2_17_18", "yearMeanNO2_18_19", 
                          "yearMeanNO2_19_20","yearMeanNO2_20_21","yearMeanNO2_21_22", 
                          "yearMeanNO2_22_23", "yearMeanNO2_23_24")],"DispersionModel_OffroadMeasures_rowcol.csv", row.names = F)

write.csv2(AirPoll_data[!is.na(AirPoll_data$NO2_0_1),c("rowcol","NO2_0_1","NO2_1_2","NO2_2_3","NO2_3_4", 
                                                              "NO2_4_5","NO2_5_6","NO2_6_7","NO2_7_8",
                                                              "NO2_8_9","NO2_9_10","NO2_10_11", "NO2_11_12",
                                                              "NO2_12_13","NO2_13_14", "NO2_14_15", "NO2_15_16",
                                                              "NO2_16_17","NO2_17_18", "NO2_18_19", 
                                                              "NO2_19_20","NO2_20_21","NO2_21_22", 
                                                              "NO2_22_23", "NO2_23_24")],"DispersionModel_OnRoadPredictions_rowcol.csv", row.names = F)




######################################################################################################
## Cellular automata
#####################################################################
AirPoll_data$NO2_all_0_1 = AirPoll_data$baseline_NO2
AirPoll_data$NO2_all_0_1[!is.na(AirPoll_data$NO2_0_1)] = AirPoll_data$NO2_0_1[!is.na(AirPoll_data$NO2_0_1)]
airpoll_grid_raster = raster::setValues(airpoll_grid_raster, AirPoll_data$NO2_all_0_1)

BaselineTrafficNO2 = c("NO2_0_1_basetraff","NO2_1_2_basetraff","NO2_2_3_basetraff","NO2_3_4_basetraff", "NO2_4_5_basetraff","NO2_5_6_basetraff","NO2_6_7_basetraff","NO2_7_8_basetraff",
                    "NO2_8_9_basetraff","NO2_9_10_basetraff","NO2_10_11_basetraff", "NO2_11_12_basetraff","NO2_12_13_basetraff","NO2_13_14_basetraff", "NO2_14_15_basetraff", "NO2_15_16_basetraff",
                    "NO2_16_17_basetraff","NO2_17_18_basetraff", "NO2_18_19_basetraff", "NO2_19_20_basetraff","NO2_20_21_basetraff","NO2_21_22_basetraff", 
                    "NO2_22_23_basetraff", "NO2_23_24_basetraff")

TrafficNO2 = c("NO2_0_1","NO2_1_2","NO2_2_3","NO2_3_4", "NO2_4_5","NO2_5_6","NO2_6_7","NO2_7_8",
                       "NO2_8_9","NO2_9_10","NO2_10_11", "NO2_11_12","NO2_12_13","NO2_13_14", "NO2_14_15", "NO2_15_16",
                       "NO2_16_17","NO2_17_18", "NO2_18_19", "NO2_19_20","NO2_20_21","NO2_21_22", 
                       "NO2_22_23", "NO2_23_24")

for(i in 1:24){
  AirPoll_data[,BaselineTrafficNO2[i]] = AirPoll_data$baseline_NO2
  AirPoll_data[!is.na(AirPoll_data[,TrafficNO2[i]]),BaselineTrafficNO2[i]] = AirPoll_data[!is.na(AirPoll_data[,TrafficNO2[i]]), TrafficNO2[i]]
}

AirPoll_data[,c("NO2_0_1_NoNA","NO2_1_2_NoNA","NO2_2_3_NoNA","NO2_3_4_NoNA", "NO2_4_5_NoNA","NO2_5_6_NoNA","NO2_6_7_NoNA","NO2_7_8_NoNA",
                "NO2_8_9_NoNA","NO2_9_10_NoNA","NO2_10_11_NoNA", "NO2_11_12_NoNA","NO2_12_13_NoNA","NO2_13_14_NoNA", "NO2_14_15_NoNA", "NO2_15_16_NoNA",
                "NO2_16_17_NoNA","NO2_17_18_NoNA", "NO2_18_19_NoNA", "NO2_19_20_NoNA","NO2_20_21_NoNA","NO2_21_22_NoNA", 
                "NO2_22_23_NoNA", "NO2_23_24_NoNA")] <- AirPoll_data[,c("NO2_0_1","NO2_1_2","NO2_2_3","NO2_3_4", "NO2_4_5","NO2_5_6","NO2_6_7","NO2_7_8",
                                                                        "NO2_8_9","NO2_9_10","NO2_10_11", "NO2_11_12","NO2_12_13","NO2_13_14", "NO2_14_15", "NO2_15_16",
                                                                        "NO2_16_17","NO2_17_18", "NO2_18_19", "NO2_19_20","NO2_20_21","NO2_21_22", 
                                                                        "NO2_22_23", "NO2_23_24")] %>% replace(is.na(.), 0)



airpoll_grid_raster = raster::setValues(airpoll_grid_raster, AirPoll_data$NO2_0_1_NoNA)
summary(AirPoll_data$NO2_0_1_NoNA)


Eval_df = AirPoll_data[, c("baseline_NO2", "yearMeanNO2_0_1","yearMeanNO2_1_2","yearMeanNO2_2_3","yearMeanNO2_3_4", 
                           "yearMeanNO2_4_5","yearMeanNO2_5_6","yearMeanNO2_6_7","yearMeanNO2_7_8",
                           "yearMeanNO2_8_9","yearMeanNO2_9_10","yearMeanNO2_10_11", "yearMeanNO2_11_12",
                           "yearMeanNO2_12_13","yearMeanNO2_13_14", "yearMeanNO2_14_15", "yearMeanNO2_15_16",
                           "yearMeanNO2_16_17","yearMeanNO2_17_18", "yearMeanNO2_18_19", 
                           "yearMeanNO2_19_20","yearMeanNO2_20_21","yearMeanNO2_21_22", 
                           "yearMeanNO2_22_23", "yearMeanNO2_23_24")]

?focal

hour = 1



TrafficNO2_NoNA = c("NO2_0_1_NoNA","NO2_1_2_NoNA","NO2_2_3_NoNA","NO2_3_4_NoNA", "NO2_4_5_NoNA","NO2_5_6_NoNA","NO2_6_7_NoNA","NO2_7_8_NoNA",
                    "NO2_8_9_NoNA","NO2_9_10_NoNA","NO2_10_11_NoNA", "NO2_11_12_NoNA","NO2_12_13_NoNA","NO2_13_14_NoNA", "NO2_14_15_NoNA", "NO2_15_16_NoNA",
                    "NO2_16_17_NoNA","NO2_17_18_NoNA", "NO2_18_19_NoNA", "NO2_19_20_NoNA","NO2_20_21_NoNA","NO2_21_22_NoNA", 
                    "NO2_22_23_NoNA", "NO2_23_24_NoNA")

BaselineTrafficNO2 = c("NO2_0_1_basetraff","NO2_1_2_basetraff","NO2_2_3_basetraff","NO2_3_4_basetraff", "NO2_4_5_basetraff","NO2_5_6_basetraff","NO2_6_7_basetraff","NO2_7_8_basetraff",
                       "NO2_8_9_basetraff","NO2_9_10_basetraff","NO2_10_11_basetraff", "NO2_11_12_basetraff","NO2_12_13_basetraff","NO2_13_14_basetraff", "NO2_14_15_basetraff", "NO2_15_16_basetraff",
                       "NO2_16_17_basetraff","NO2_17_18_basetraff", "NO2_18_19_basetraff", "NO2_19_20_basetraff","NO2_20_21_basetraff","NO2_21_22_basetraff", 
                       "NO2_22_23_basetraff", "NO2_23_24_basetraff")

include_baseline_in_dispersion = T
prop_rate = 0.9 #propagationrate
nr_repeats = 10
weight_matrix = matrix(prop_rate, nrow= 3, ncol = 3) ## could implement wind here

#function to 

for (prop_rate in c(0.5, 0.6, 0.7, 0.8, 0.9, 1.0)){
  for(hour in 1:24){
    ### set Values for hour
    if (include_baseline_in_dispersion == T){
      airpoll_grid_raster = raster::setValues(airpoll_grid_raster, AirPoll_data[, BaselineTrafficNO2[hour]])
    }
    else{
      airpoll_grid_raster = raster::setValues(airpoll_grid_raster, AirPoll_data[,TrafficNO2_NoNA[hour]])
    }
    ## Cellular Automata
    airpoll_grid_raster_after = airpoll_grid_raster
    for (i in 1:nr_repeats){
      airpoll_grid_raster_after = raster::focal(airpoll_grid_raster_after, w=weight_matrix  , fun=mean)
    }
    
    ## Visual interpretation
    plot(airpoll_grid_raster)
    plot(airpoll_grid_raster_after)
    
    ## Objective function
    Eval_df$Pred_0_1 = airpoll_grid_raster_after@data@values
    Eval_df$difference = (Eval_df$Pred_0_1+ Eval_df$baseline_NO2)- Eval_df$yearMeanNO2_0_1
    print(paste("hour", hour, "propagation rate", prop_rate, "Nr repeats", nr_repeats))
    print(summary(Eval_df$difference ))
    
  }
}






# 
# PuffR   ##Calpuff
# 
# bLSmodelR
# https://github.com/ChHaeni/bLSmodelR/blob/main/Guide2bLSmodelR.r





#####################################################
### Adding dispersion moderator variables
####################################################


# Extract 3D Bag data
# https://docs.3dbag.nl/en/schema/concepts/#level-of-detail-lod
layername = "lod12_2d"
layername = "lod12_3d"
layername = "lod22_2d"
layername = "lod22_3d"
filelist = list.files(path = "D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG")
joinedfile = st_read(paste0("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG/", filelist[1]), layer = layername)
for(file in filelist){
  d = st_read(paste0("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG/", file), layer = layername)
  joinedfile <- rbind(d, joinedfile)
}
joinedfile = unique(joinedfile)
joinedfile_shp = as_Spatial(joinedfile)
writeOGR(joinedfile_shp, dsn="D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG 2D files" ,layer= paste0("BAG3D_", layername),driver="ESRI Shapefile")


########## building height
BAG = readOGR(dsn="D:/PhD EXPANSE/Data/Amsterdam/Built Environment/3D BAG 2D files",layer="BAG3D_lod12_2d")



# o	Distance calculation: centroid of an off-road gridcell distance to closest road identify cell to which it belong. Euclidean distance
# o	Average fraction of Open space between cell and road
# o	(Green space/Nr Trees in between cell and road)
# o	Mode/ Average building height / fraction of building over a specific threshold/ standard deviation
# o	Windspeed and winddirection
# 	Precalculate that
# 	Calculate how much direction of road to cell overlaps with winddirection
# 	Calculate degree of road to cell and subtract

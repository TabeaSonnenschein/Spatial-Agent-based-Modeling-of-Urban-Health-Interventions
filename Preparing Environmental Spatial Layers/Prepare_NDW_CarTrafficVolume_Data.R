pkgs <- c("sf", "sp", "rgdal", "spatialEco", "readxl", "dplyr", "GenSynthPop")
sapply(pkgs, require, character.only = T) #load
rm(pkgs)
library(lubridate)


options(digits = 15)

destination_folder = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Traffic/car traffic/jan-dec2019weekday"
destination_folder = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Traffic/car traffic/jan-dec2019workday"
destination_folder = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Traffic/car traffic/may19-march2020workday"
setwd(destination_folder)


files = list.files(path = destination_folder, pattern = "*.xlsx", all.files = FALSE,
                   full.names = FALSE, recursive = FALSE,
                   ignore.case = FALSE, include.dirs = FALSE, no.. = FALSE)

x = 0
for(file in files){
  if(x == 0){
    stations = read_excel(file, sheet = 1)
    stat_colnames = stations[5,]
    colnames(stations) = stat_colnames
    traffic_intensity = read_excel(file, sheet = 2)
    intens_colnames = traffic_intensity[4,]
    colnames(traffic_intensity) = intens_colnames
    traffic_speed = read_excel(file, sheet = 3)
    speed_colnames = traffic_speed[4,]
    colnames(traffic_speed) = speed_colnames

  }
  else{
    stations_new = read_excel(file, sheet = 1)
    colnames(stations_new) = stat_colnames
    traffic_intensity_new = read_excel(file, sheet = 2)
    if (ncol(traffic_intensity_new)< ncol(traffic_intensity)){
      traffic_intensity_new[,ncol(traffic_intensity_new):(ncol(traffic_intensity_new)+(ncol(traffic_intensity)-ncol(traffic_intensity_new)))] = NA
    }
    colnames(traffic_intensity_new) = intens_colnames
    traffic_speed_new = read_excel(file, sheet = 3)
    if (ncol(traffic_speed_new)< ncol(traffic_speed)){
      traffic_speed_new[,ncol(traffic_speed_new):(ncol(traffic_speed_new)+(ncol(traffic_speed)-ncol(traffic_speed_new)))] = NA
    }
    colnames(traffic_speed_new) = speed_colnames
    stations = rbind(stations, stations_new)
    traffic_intensity = rbind(traffic_intensity, traffic_intensity_new)
    traffic_speed = rbind(traffic_speed, traffic_speed_new)
  }
  x=1
}
remove(stations_new, traffic_intensity_new, traffic_speed_new)


#clean the datasets
stations = stations[!is.na(stations$Naam),]
stations = stations[stations$Volgnummer != "Volgnummer",]


traffic_intensity = traffic_intensity[!is.na(traffic_intensity$Intensiteit),]
traffic_speed = traffic_speed[!is.na(traffic_speed$`Gemiddelde snelheid`),]

int_intensity=0
int_speed = 0
traffic_intensity$station = ""
traffic_speed$station = ""
for(id in stations$ID){
  traffic_intensity$station[(1+int_intensity):(26+int_intensity)] = id
  traffic_speed$station[(1+int_speed):(25+int_speed)] = id
  int_intensity = int_intensity+26
  int_speed = int_speed + 25
}

traffic_intensity = traffic_intensity[!is.na(traffic_intensity$Intensiteit),]
traffic_intensity = traffic_intensity[traffic_intensity$`uur op de dag` != "uur op de dag",]
traffic_speed = traffic_speed[!is.na(traffic_speed$`Gemiddelde snelheid`),]
traffic_speed = traffic_speed[traffic_speed$`uur op de dag` != "uur op de dag",]

## merge the dataframes

traffic_stats = merge(traffic_intensity, traffic_speed, by = c("uur op de dag", "station"), all.x = T)
colnames(stations)[2] = "station"
traffic_stats = merge(traffic_stats, stations, by = "station", all.x = T)
colnames(traffic_stats)[c(2,3,10)] = c("hour", "traffic_volume", "mean_traffic_speed")
traffic_stats = traffic_stats[order(traffic_stats$station, traffic_stats$hour),]
traffic_stats$timespan = "01.01.2019-31.12.2019"
traffic_stats$timespan = "01.05.2019-31.3.2020"
traffic_stats$weekdays = "workdays - Monday to Friday"
traffic_stats$weekdays = "weekdays - Monday to Sunday"
write.csv(traffic_stats, "traffic_stats_jandec2019_weekday.csv")
write.csv(traffic_stats, "traffic_stats_may19mar20_workday.csv")


file2 = read.csv("May2019-Mar2020-workday_hourly_fast4.csv")
colnames(file2)

file2_clean = unique(file2[which(file2$voertuigcategorie == "anyVehicle"),c("id_meetlocatie","start_meetperiode", "eind_meetperiode", "start_locatie_latitude", "start_locatie_longitude", "waarnemingen_intensiteit", "waarnemingen_snelheid","gem_intensiteit" , "gem_snelheid", "rijrichting" )])
remove(file2)
file2_clean$start_meetperiode = as.POSIXct(file2_clean$start_meetperiode, tz="Etc/GMT+2", format = "%Y-%m-%d %H:%M:%OS")
file2_clean$eind_meetperiode = as.POSIXct(file2_clean$eind_meetperiode, tz="Etc/GMT+2", format = "%Y-%m-%d %H:%M:%OS")
file2_clean$date = as.Date(file2_clean$start_meetperiode, tz="Etc/GMT+2")
file2_clean$hour = paste(as.character(format(file2_clean$start_meetperiode, format='%H:%M')),"-",as.character(format(file2_clean$eind_meetperiode, format='%H:%M')))

write.csv(file2_clean,"May2019-Mar2020-workday_hourly_fast4_clean.csv" )


file2_min= file2_clean %>%
  group_by(id_meetlocatie, hour) %>%
  summarise(traffic_volume = as.integer(mean(gem_intensiteit)), mean_traffic_speed = mean(gem_snelheid))


stations = unique(file2_clean[,c("id_meetlocatie", "start_locatie_latitude", "start_locatie_longitude", "rijrichting")])

freq = as.data.frame(table(stations$id_meetlocatie))
colnames(freq) = c("id_meetlocatie", "freq")
stations = merge(stations, freq, by= "id_meetlocatie" )
freq = unique(stations[,c("id_meetlocatie", "rijrichting")])
freq= freq[freq$rijrichting != "",]
stations$has_direction = 0
stations$has_direction[which(stations$id_meetlocatie %in% freq$id_meetlocatie)] = 1
stations = stations[which((stations$freq ==1)|((stations$freq >1)& (stations$has_direction == 1) & (stations$rijrichting != ""))| (stations$has_direction == 0)),]
stations = stations[!duplicated(stations$id_meetlocatie),]
stations = stations[,c("id_meetlocatie", "start_locatie_latitude", "start_locatie_longitude", "rijrichting")]

file2_min = merge(file2_min, stations, by = "id_meetlocatie")
file2_min$timespan = "01.05.2019-31.3.2020"
file2_min$weekdays = "workdays - Monday to Friday"
colnames(file2_min) = c("station","hour","traffic_volume", "mean_traffic_speed","Latitude","Longitude", "travel_direction", "timespan","weekdays")
write.csv(file2_min,"May2019-Mar2020-workday_averagehourly7.csv" , row.names = F)

file1_min = read.csv("May2019-Mar2020-workday_averagehourly1.csv" )
file2_min = read.csv("May2019-Mar2020-workday_averagehourly3.csv" )
file3_min = read.csv("May2019-Mar2020-workday_averagehourly4.csv" )
file4_min = read.csv("May2019-Mar2020-workday_averagehourly5.csv" )
file5_min = read.csv("May2019-Mar2020-workday_averagehourly6.csv" )
file6_min = read.csv("May2019-Mar2020-workday_averagehourly7.csv" )

file2_min = rbind(file1_min, file2_min, file3_min, file4_min, file5_min, file6_min)

traffic_stats = read.csv("traffic_stats_may19mar20_workday.csv" )


tojoin = traffic_stats[,c("station","hour","traffic_volume", "mean_traffic_speed","Breedtegraad","Lengtegraad", "timespan","weekdays")]
tojoin$travel_direction = NA
tojoin = tojoin[,c("station","hour","traffic_volume", "mean_traffic_speed","Breedtegraad","Lengtegraad", "travel_direction", "timespan","weekdays")]
colnames(tojoin) = c("station","hour","traffic_volume", "mean_traffic_speed","Latitude","Longitude", "travel_direction", "timespan","weekdays")
tojoin = tojoin[tojoin$hour != "Totaal",]



hours = as.data.frame(cbind(unique(file2_min$hour), unique(tojoin$hour)))
colnames(hours)= c("hour", "hour_new")
file2_min = merge(file2_min, hours, by = "hour")
colnames(file2_min)[which(colnames(file2_min) == "hour")] = "oldhour"
colnames(file2_min)[which(colnames(file2_min) == "hour_new")] = "hour"
file2_min = file2_min[order(file2_min$station, file2_min$hour), c("station","hour","traffic_volume", "mean_traffic_speed","Latitude","Longitude", "travel_direction", "timespan","weekdays")]

joined = rbind(file2_min, tojoin)

joined = unique(joined)
freq = as.data.frame(table(joined$station))

joined[joined$station == "RWS01_MONICA_10D00A003C0AD0070007",]

?restructure_one_var_marginal

joined2 = restructure_one_var_marginal(joined[, c("station", "hour", "traffic_volume")], "hour", "traffic_volume")
joined3 = restructure_one_var_marginal(joined[, c("station", "hour", "mean_traffic_speed")], "hour", "mean_traffic_speed")

colnames(joined2) = c("station","TrafVol0_1", "TrafVol1_2", "TrafVol2_3", "TrafVol3_4", "TrafVol4_5",
"TrafVol5_6", "TrafVol6_7", "TrafVol7_8", "TrafVol8_9", "TrafVol9_10", "TrafVol10_11","TrafVol11_12", "TrafVol12_13", 
"TrafVol13_14", "TrafVol14_15", "TrafVol15_16","TrafVol16_17", "TrafVol17_18", "TrafVol18_19", "TrafVol19_20", 
"TrafVol20_21","TrafVol21_22", "TrafVol22_23", "TrafVol23_24", "TrafVol_tot")

colnames(joined3) = c("station","TrafSpeed0_1", "TrafSpeed1_2", "TrafSpeed2_3", "TrafSpeed3_4", "TrafSpeed4_5",
                      "TrafSpeed5_6", "TrafSpeed6_7", "TrafSpeed7_8", "TrafSpeed8_9", "TrafSpeed9_10", "TrafSpeed10_11","TrafSpeed11_12", "TrafSpeed12_13", 
                      "TrafSpeed13_14", "TrafSpeed14_15", "TrafSpeed15_16","TrafSpeed16_17", "TrafSpeed17_18", "TrafSpeed18_19", "TrafSpeed19_20", 
                      "TrafSpeed20_21","TrafSpeed21_22", "TrafSpeed22_23", "TrafSpeed23_24", "TrafSpeed_tot")


joined2[, c("TrafSpeed0_1", "TrafSpeed1_2", "TrafSpeed2_3", "TrafSpeed3_4", "TrafSpeed4_5",
            "TrafSpeed5_6", "TrafSpeed6_7", "TrafSpeed7_8", "TrafSpeed8_9", "TrafSpeed9_10", "TrafSpeed10_11","TrafSpeed11_12", "TrafSpeed12_13", 
            "TrafSpeed13_14", "TrafSpeed14_15", "TrafSpeed15_16","TrafSpeed16_17", "TrafSpeed17_18", "TrafSpeed18_19", "TrafSpeed19_20", 
            "TrafSpeed20_21","TrafSpeed21_22", "TrafSpeed22_23", "TrafSpeed23_24")] = joined3[, c("TrafSpeed0_1", "TrafSpeed1_2", "TrafSpeed2_3", "TrafSpeed3_4", "TrafSpeed4_5",
                                                                                                  "TrafSpeed5_6", "TrafSpeed6_7", "TrafSpeed7_8", "TrafSpeed8_9", "TrafSpeed9_10", "TrafSpeed10_11","TrafSpeed11_12", "TrafSpeed12_13", 
                                                                                                  "TrafSpeed13_14", "TrafSpeed14_15", "TrafSpeed15_16","TrafSpeed16_17", "TrafSpeed17_18", "TrafSpeed18_19", "TrafSpeed19_20", 
                                                                                               "TrafSpeed20_21","TrafSpeed21_22", "TrafSpeed22_23", "TrafSpeed23_24")]


joined2 = joined2[!is.na(joined2$TrafVol0_1),]
stations = unique(joined[,c("station", "Longitude", "Latitude", "travel_direction")])
joined2 = merge(joined2, stations, by = "station")

write.csv(joined2,"May2019-Mar2020-workday_onestation_hourscolumn.csv" , row.names = F)



write.csv(tojoin,"May2019-Mar2020-workday_joined.csv" , row.names = F)

write.csv(joined,"May2019-Mar2020-workday_joined.csv" , row.names = F)
tojoin = read.csv("May2019-Mar2020-workday_joined.csv")
joined = rbind(file2_min, tojoin)
write.csv(joined,"May2019-Mar2020-workday_joined.csv" , row.names = F)

remove(file2_clean, file2_min, tojoin, traffic_stats)


## plot station locations
xy = stations[,c(5,4)]
str(xy)
xy$Lengtegraad = as.numeric(as.character(xy$Lengtegraad))
xy$Breedtegraad = as.numeric(as.character(xy$Breedtegraad))
stations = SpatialPointsDataFrame(coords = xy, data = stations,
                       proj4string = CRS("+proj=longlat +datum=WGS84 +ellps=WGS84 +towgs84=0,0,0"))
crs = "+init=EPSG:28992" #Amersfoort / RD New
stations = spTransform(stations, CRSobj = crs)

Amsterdam_Roads = readOGR(dsn="C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure" ,layer="Amsterdam_roads_RDNew")
plot(Amsterdam_Roads, col = "azure4")
plot(stations, add=T, col = "red")

writeOGR(stations, dsn=destination_folder ,layer= "measurementstations",driver="ESRI Shapefile")




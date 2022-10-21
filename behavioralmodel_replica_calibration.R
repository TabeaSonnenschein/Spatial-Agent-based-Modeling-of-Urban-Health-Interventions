#########################
### Load packages #######
#########################
pkgs = c("GA","MetricsWeighted", "bnlearn", "stats", "rgdal","sp", "sf", "rgeos" , "ggplot2", "matrixStats",  "raster",  "dplyr")
sapply(pkgs[which(sapply(pkgs, require, character.only = T) == FALSE)], install.packages, character.only = T)
sapply(pkgs, require, character.only = T) #load
rm(pkgs)


#########################
### read data ###########
#########################
## ODIN
setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/ODIN/2018")
ODIN = read.csv("ODIN2018_Studyarea_PC6_sample.csv")
colnames(ODIN)

dutchnames = c("VerplID", "VertPC", "AankPC", "Hvm", "OPID", "Geslacht", "Leeftijd",
               "Herkomst", "HHAuto", "HHGestInkG",
               "BetWerk", "Opleiding", "HHPers",
               "HHLft1", "HHLft2", "HHLft3", "MotiefV")

englishnames = c("TripID", "orig_postcode", "dest_postcode", "modal_choice", "Person_ID", "sex", "age",
                 "migration_background", "Nr_cars_hh",
                 "income",  "employment_status",
                 "education_level", "HH_size",  "nr_children_yonger6",
                 "nr_child_6_11", "nr_child_12_17", "trip_purpose")

ODIN = ODIN[, c("orig_PC6","dest_PC6",englishnames)]

ODIN$car_access = 0
ODIN$car_access[ODIN$Nr_cars_hh > 0] = 1

mode_names = c("Personenauto",	"Trein",	"Bus",	"Tram",	"Metro",	"Speedpedelec",
"Elektrische fiets",	"Niet-elektrische fiets", "Te voet","Touringcar",
"Bestelauto", "Vrachtwagen","Camper,Taxi/Taxibusje","Landbouwvoertuig",
"Motor","Bromfiets","Snorfiets","Gehandicaptenvervoermiddel met motor",
"Gehandicaptenvervoermiddel zonder motor","Skates/skeelers/step",
"Boot","Anders met motor","Anders zonder motor")

ODIN$mode_name = ODIN$modal_choice
for(i in 1:length(mode_names)){
  ODIN$mode_name[ODIN$mode_name == i] = mode_names[i]
}

table(ODIN$mode_name)


ODIN$modes_simple = ""
ODIN$modes_simple[ODIN$mode_name %in% c("Personenauto", "Bestelauto", "Vrachtwagen", "Landbouwvoertuig", "Gehandicaptenvervoermiddel met motor")] = "car"
ODIN$modes_simple[ODIN$mode_name %in% c("Trein", "Bus", "Tram", "Metro")] = "publicTransport"
ODIN$modes_simple[ODIN$mode_name %in% c("Elektrische fiets","Niet-elektrische fiets")] = "bike"
ODIN$modes_simple[ODIN$mode_name %in% c("Te voet", "Gehandicaptenvervoermiddel zonder motor", "Anders zonder motor")] = "walk"
ODIN$modes_simple[ODIN$mode_name %in% c("Snorfiets", "Bromfiets")] = "scooter"

simple_mode_names = unique(ODIN$modes_simple)
ODIN$WalkTrip = 0
ODIN$WalkTrip[ODIN$modes_simple == "walk"] = 1
ODIN$BikeTrip = 0
ODIN$BikeTrip[ODIN$modes_simple == "bike"] = 1
ODIN$CarTrip = 0
ODIN$CarTrip[ODIN$modes_simple == "car"] = 1
ODIN$PubTransTrip = 0
ODIN$PubTransTrip[ODIN$modes_simple == "publicTransport"] = 1

modes = as.data.frame(unique(ODIN$modes_simple))
modes$modes_int = 1:5
colnames(modes) = c("modes_simple", "modes_int")
ODIN = merge(ODIN, modes, by = "modes_simple", all.x = T)


setwd("D:")
ODIN = read.csv("ODIN2018_Studyarea_PC6.csv")
ODIN = read.csv("ODIN2018_Studyarea_PC61.csv")
ODIN = read.csv("ODIN2018_Studyarea_PC62.csv")

## Environmental Behavior Determinants
setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure")
PC6_env_behav_determ = read.csv("PC6_env_behav_determ.csv")
colnames(PC6_env_behav_determ)
env_behav_colnames = c("PC6", "area", "perimeter", "unqId", "Intid", "popDns", "retaiDns" , "greenCovr", "pubTraDns",
             "RdIntrsDns", "TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV",
             "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout",
             "DistCBD", "retailDiv", "MaxSpeed", "MinSpeed", "MeanSpeed", "NrStrLight",
             "CrimeIncid", "MaxNoisDay", "MxNoisNigh", "OpenSpace", "NrParkSpac",
             "PNonWester", "PWelfarDep", "PrkPricPre", "PrkPricPos", "coords.x1","coords.x2")

PC6_polygon = readOGR(dsn=getwd(),layer="PC6_polygon_behav_determ")
PC6_polygonsf = st_as_sf(PC6_polygon)

crs = "+init=EPSG:28992" #Amersfoort / RD New
crs_name = "RDNew"
CRS_defin = "+towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725"


##################################################
### joining ODIN data with environmental data ####
##################################################
#variables that have to be joined with the trip origin PC6
orig_variables = c("DistCBD", "pubTraDns", "coords.x1","coords.x2")
orig_vardata = PC6_env_behav_determ[,c("PC6", orig_variables)]
colnames(orig_vardata)[2:ncol(orig_vardata)] = paste0(orig_variables,".orig")

#variables that have to be averaged over the trip route
route_variables = c("popDns", "retaiDns" , "greenCovr", "pubTraDns", "RdIntrsDns", "TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV",
                    "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout","retailDiv", "MaxSpeed", "MinSpeed", "MeanSpeed", "NrStrLight",
                    "CrimeIncid", "MaxNoisDay", "MxNoisNigh", "OpenSpace", "PNonWester", "PWelfarDep")

route_variables_later = paste0(route_variables, ".route")

#variables that have to be joined with the trip destination PC6
dest_variables = c("NrParkSpac","coords.x1","coords.x2")
dest_vardata = PC6_env_behav_determ[,c("PC6", dest_variables)]
colnames(dest_vardata)[2:ncol(dest_vardata)] = paste0(dest_variables,".dest")

ODIN_orig = base::merge(ODIN, orig_vardata, by.x = "orig_PC6", by.y = "PC6")
ODIN_orig_dest = base::merge(ODIN_orig, dest_vardata, by.x = "dest_PC6", by.y = "PC6")

ODIN_orig_dest[,route_variables_later] = NA
ODIN_orig_dest$trip_distance = NA
for(x in 1:nrow(ODIN)){
  orig_dest_line = st_as_sf(SpatialLines(list(Lines(Line(list(as.numeric(ODIN_orig_dest[x,c("coords.x1.orig","coords.x1.dest")]), as.numeric(ODIN_orig_dest[x,c("coords.x2.orig","coords.x2.dest")]))), ID = ODIN_orig_dest$TripID[x])), proj4string = CRS(crs)))
  ODIN_orig_dest$trip_distance[x] = st_length(orig_dest_line)
  route_stats = st_intersection(orig_dest_line, PC6_polygonsf) %>%
    st_drop_geometry() %>%
    select(route_variables)
  route_stats <- sapply(route_stats, as.numeric )
  ODIN_orig_dest[x,route_variables_later] = colMeans(route_stats, na.rm = T)
}

plot(PC6_polygon[which(PC6_polygon$PC6 %in% route_stats$PC6),])
plot(orig_dest_line, add = T, col = "red")
st_length(orig_dest_line)


######################################################
### Read environmental trip data ####################
####################################################
setwd("D:/9234_Orig_Dest_TrackProperties_PC6Combinations_1")
file_in    <- file("9234_Orig_Dest_TrackProperties_PC6Combinations_1.csv","r")
chunk_size <- 300000 # choose the best size for you
x          <- readLines(file_in, n=chunk_size)
df = as.data.frame(x)
columnnames = unlist(strsplit(df[1,], ","))
print(x[1])
df = data.frame(do.call("rbind", strsplit(as.character(df[2:nrow(df), "x"]), ",", fixed = TRUE)))
colnames(df) = columnnames
?readLines
trackEnv = read.csv("9234_Orig_Dest_TrackProperties_PC6Combinations_1.csv")
trackEnv = read_delim("9234_Orig_Dest_TrackProperties_PC6Combinations_1.csv", ",", col_names = TRUE)

relev_PC6 = unique(unlist(c(unique(ODIN$orig_PC6), unique(ODIN$dest_PC6))))

df = df[which(df$orig_PC6 %in% relev_PC6),]
df = df[which(df$dest_PC6 %in% relev_PC6),]

new_columns = colnames(df)[colnames(df) %in% c("orig_postcode","orig_PC6","dest_postcode","dest_PC6") == FALSE]

opposite_colums = gsub(".orig", "xxxx", new_columns)
opposite_colums =  gsub(".dest", ".orig", opposite_colums)
opposite_colums =  gsub("xxxx", ".dest", opposite_colums)

print(new_columns)
print(opposite_colums)

ODIN_orig_dest = ODIN
ODIN_orig_dest[,new_columns] = NA
for(i in 1:nrow(ODIN_orig_dest)){
  if(length(which((df$orig_PC6 == ODIN_orig_dest[i,"orig_PC6"]) & (df$dest_PC6 == ODIN_orig_dest[i,"dest_PC6"]))) > 0){
    ODIN_orig_dest[i, new_columns] = df[which((df$orig_PC6 == ODIN_orig_dest[i,"orig_PC6"]) & (df$dest_PC6 == ODIN_orig_dest[i,"dest_PC6"])), new_columns]
  }
  else if(length(which((df$orig_PC6 == ODIN_orig_dest[i,"dest_PC6"]) & (df$dest_PC6 == ODIN_orig_dest[i,"orig_PC6"]))) > 0){
    print("its case 2")
    ODIN_orig_dest[i, opposite_colums] = df[which((df$orig_PC6 == ODIN_orig_dest[i,"dest_PC6"]) & (df$dest_PC6 == ODIN_orig_dest[i,"orig_PC6"])), new_columns]
  }
}



setwd("D:/")
write.csv(ODIN_orig_dest, "ODIN_envjoin.csv", row.names = F)
ODIN_orig_dest= read.csv("ODIN_envjoin.csv")

ODIN_orig_dest = ODIN_orig_dest[!is.na(ODIN_orig_dest$DistCBD.orig),]
##############################################
### make sure all numeric columns are numeric #########
###############################################

str(ODIN_orig_dest)
ODIN_orig_dest[new_columns] <- sapply(ODIN_orig_dest[new_columns],as.numeric)
str(ODIN_orig_dest)

#####################################################
### Initial Regression Exploration ##################
#####################################################

walk_lm <- lm(WalkTrip ~ sex + age +  migration_background +
                Nr_cars_hh +
                income +
                employment_status +
                education_level +
                HH_size +
                nr_children_yonger6 +
                DistCBD.orig +
                pubTraDns.orig +
                NrParkSpac.dest +
                popDns.route +
                retaiDns.route +
                greenCovr.route +
                pubTraDns.route +
                RdIntrsDns.route +
                TrafAccid.route +
                AccidPedes.route +
                NrTrees.route +
                MeanTraffV.route +
                HighwLen.route +
                PedStrWidt.route +
                PedStrLen.route +
                LenBikRout.route +
                retailDiv.route +
                MaxSpeed.route +
                NrStrLight.route +
                CrimeIncid.route +
                MaxNoisDay.route +
                OpenSpace.route +
                PNonWester.route +
                PWelfarDep.route , data = ODIN_orig_dest)

summary(walk_lm)


bike_lm <- lm(BikeTrip ~ sex + age + migration_background +
                Nr_cars_hh +
                income +
                employment_status +
                education_level +
                HH_size +
                nr_children_yonger6 +
                DistCBD.orig +
                pubTraDns.orig +
                NrParkSpac.dest +
                popDns.route +
                retaiDns.route +
                greenCovr.route +
                pubTraDns.route +
                RdIntrsDns.route +
                TrafAccid.route +
                AccidPedes.route +
                NrTrees.route +
                MeanTraffV.route +
                HighwLen.route +
                PedStrWidt.route +
                PedStrLen.route +
                LenBikRout.route +
                retailDiv.route +
                MaxSpeed.route +
                NrStrLight.route +
                CrimeIncid.route +
                MaxNoisDay.route +
                OpenSpace.route +
                PNonWester.route +
                PWelfarDep.route , data = ODIN_orig_dest)

summary(bike_lm)

colnames(ODIN_orig_dest)
car_lm <- lm(CarTrip ~ sex + age + migration_background +
               Nr_cars_hh +
               income +
               employment_status +
               education_level +
               HH_size +
               nr_children_yonger6 +
               DistCBD.orig +
                pubTraDns.orig +
                NrParkSpac.dest +
                popDns.route +
                retaiDns.route +
                greenCovr.route +
                pubTraDns.route +
                RdIntrsDns.route +
                TrafAccid.route +
                AccidPedes.route +
                NrTrees.route +
                MeanTraffV.route +
                HighwLen.route +
                PedStrWidt.route +
                PedStrLen.route +
                LenBikRout.route +
                retailDiv.route +
                MaxSpeed.route +
                NrStrLight.route +
                CrimeIncid.route +
                MaxNoisDay.route +
                OpenSpace.route +
                PNonWester.route +
                PWelfarDep.route , data = ODIN_orig_dest)

summary(car_lm)





############################################
### Behavioral Model Replica ###############
############################################

### with behavior constraints

###########need to subselect based on pre-intervention date
 date < 2019 #April

# data preparation for heterogenous weight calibration
ODIN_orig_dest$age_group = 0
ODIN_orig_dest$age_group[ODIN_orig_dest$age %in% 0:10] = 0
ODIN_orig_dest$age_group[ODIN_orig_dest$age %in% 10:17] = 1
ODIN_orig_dest$age_group[ODIN_orig_dest$age %in% 18:35] = 2
ODIN_orig_dest$age_group[ODIN_orig_dest$age %in% 35:50] = 3
ODIN_orig_dest$age_group[ODIN_orig_dest$age %in% 50:65] = 4
ODIN_orig_dest$age_group[ODIN_orig_dest$age %in% 65:100] = 5
ODIN_orig_dest$trip_distance_km = ODIN_orig_dest$trip_distance/1000

## parameter initialization for calibration
#optional
parking_price_weight_car_income = c(1,2,3)
season (weather)

car_params_nam = c("income_weight_car", 
                   "parking_space_weight_car",
                   "parking_price_weight_car", "children_weight_car",
                   "DistCBD_weight_car")
car_params_simple = c(1,1,1,1,1)

hetero_params_nam = c("trip_dist_weight_car_age", "trip_dist_weight_walk_age", 
                      "trip_dist_weight_bike_age", "trip_dist_weight_transit_age")
hetero_params = list(c(1,2,3,4,5,6),c(1,2,3,4,5,6),c(1,2,3,4,5,6),c(1,2,3,4,5,6))

walk_params_nam = c("DistCBD_weight_walk", "pubTraDns_orig_weight_walk", 
                    "pubTraDns_dest_weight_walk", "popDns_weight_walk", "retaiDns_weight_walk", 
                    "greenCovr_weight_walk", "RdIntrsDns_weight_walk", "TrafAccid_weight_walk", 
                    "AccidPedes_weight_walk", "NrTrees_weight_walk", "MeanTraffV_weight_walk", 
                    "HighwLen_weight_walk", "PedStrWidt_weight_walk", "PedStrLen_weight_walk", 
                    "retailDiv_weight_walk", "MaxSpeed_weight_walk", "NrStrLight_weight_walk", 
                    "CrimeIncid_weight_walk", "MaxNoisDay_weight_walk", "OpenSpace_weight_walk",
                    "PNonWester_weight_walk", "PWelfarDep_weight_walk")

walk_params_simple = c(0.1,0.1,0.2,0.3,0.4,0.2,0.1,0.1,0.1,0.1,0.1,1,1,1,1,1,1,1,1,1,1,1)

bike_params_nam = c("LenBikRout_weight_bike", "popDns_weight_bike ", 
                    "greenCovr_weight_bike", "RdIntrsDns_weight_bike", "TrafAccid_weight_bike", 
                    "DistCBD_weight_bike ", "NrTrees_weight_bike", "MeanTraffV_weight_bike", 
                    "HighwLen_weight_bike", "MaxSpeed_weight_bike", "NrStrLight_weight_bike", 
                    "CrimeIncid_weight_bike", "MaxNoisDay_weight_bike", "OpenSpace_weight_bike", 
                    "PNonWester_weight_bike", "PWelfarDep_weight_bike")
bike_params_simple = c(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)


transit_params_nam = c("age_weight_transit", "income_weight_transit", "DistCBD_weight_transit",
                       "pubTraDns_orig_weight_transit", "pubTraDns_dest_weight_transit", 
                       "popDns_weight_transit", "retaiDns_weight_transit", "retailDiv_weight_transit", 
                       "NrStrLight_weight_transit", "CrimeIncid_weight_transit", "PNonWester_weight_transit", 
                       "PWelfarDep_weight_transit")

transit_params_simple = c(1,1,1,1,1,1,1,1,1,1,1,1)


## modal choice function
calc_modal_choice = function(car_params_simple, walk_params_simple, bike_params_simple, transit_params_simple, hetero_params)
{
  ODIN_orig_dest$driving_utility = (car_params_simple[1] * ODIN_orig_dest$income) +
    (hetero_params[[1]][ODIN_orig_dest$age_group] * ODIN_orig_dest$trip_distance_km) +
    (car_params_simple[2] * ODIN_orig_dest$NrParkSpac.dest) +
    (car_params_simple[3] * ODIN_orig_dest$PrkPricPre.dest) +
    (car_param_simple[4] * ODIN_orig_dest$nr_children_yonger6) +
    (car_params_simple[5] * ODIN_orig_dest$DistCBD.orig)
  ODIN_orig_dest$driving_utility[ODIN_orig_dest$car_access > 0]  = 0
  
  ODIN_orig_dest$walking_utility = (hetero_params[[2]][ODIN_orig_dest$age_group] * ODIN_orig_dest$trip_distance_km) +
    (walk_params_simple[1] * ODIN_orig_dest$DistCBD.orig) +
    (walk_params_simple[2] * ODIN_orig_dest$pubTraDns.orig) +
    (walk_params_simple[3] * ODIN_orig_dest$pubTraDns.dest) +
    (walk_params_simple[4] * ODIN_orig_dest$popDns.route) +
    (walk_params_simple[5] * ODIN_orig_dest$retaiDns.route) +
    (walk_params_simple[6] * ODIN_orig_dest$greenCovr.route) +
    (walk_params_simple[7] * ODIN_orig_dest$RdIntrsDns.route) +
    (walk_params_simple[8] * ODIN_orig_dest$TrafAccid.route) +
    (walk_params_simple[9] * ODIN_orig_dest$AccidPedes.route) +
    (walk_params_simple[10] * ODIN_orig_dest$NrTrees.route) +
    (walk_params_simple[11] * ODIN_orig_dest$MeanTraffV.route) +
    (walk_params_simple[12] * ODIN_orig_dest$HighwLen.route) +
    (walk_params_simple[13] * ODIN_orig_dest$PedStrWidt.route) +
    (walk_params_simple[14] * ODIN_orig_dest$PedStrLen.route) +
    (walk_params_simple[15] * ODIN_orig_dest$retailDiv.route) +
    (walk_params_simple[16] * ODIN_orig_dest$MaxSpeed.route) +
    (walk_params_simple[17] * ODIN_orig_dest$NrStrLight.route) +
    (walk_params_simple[18] * ODIN_orig_dest$CrimeIncid.route) +
    (walk_params_simple[19] * ODIN_orig_dest$MaxNoisDay.route) +
    (walk_params_simple[20] * ODIN_orig_dest$OpenSpace.route) +
    (walk_params_simple[21] * ODIN_orig_dest$PNonWester.route) +
    (walk_params_simple[22] * ODIN_orig_dest$PWelfarDep.route)
  
  ODIN_orig_dest$biking_utility = (hetero_params[[3]][ODIN_orig_dest$age_group]  * ODIN_orig_dest$trip_distance_km) +
    (bike_params_simple[6] * ODIN_orig_dest$DistCBD.orig) +
    (bike_params_simple[2] * ODIN_orig_dest$popDns.route) +
    (bike_params_simple[3] * ODIN_orig_dest$greenCovr.route) +
    (bike_params_simple[4] * ODIN_orig_dest$RdIntrsDns.route) +
    (bike_params_simple[5] * ODIN_orig_dest$TrafAccid.route) +
    (bike_params_simple[1] * ODIN_orig_dest$LenBikRout.route) +
    (bike_params_simple[7] * ODIN_orig_dest$NrTrees.route) +
    (bike_params_simple[8] * ODIN_orig_dest$MeanTraffV.route) +
    (bike_params_simple[9] * ODIN_orig_dest$HighwLen.route) +
    (bike_params_simple[10] * ODIN_orig_dest$MaxSpeed.route) +
    (bike_params_simple[11] * ODIN_orig_dest$NrStrLight.route) +
    (bike_params_simple[12] * ODIN_orig_dest$CrimeIncid.route) +
    (bike_params_simple[13] * ODIN_orig_dest$MaxNoisDay.route) +
    (bike_params_simple[14] * ODIN_orig_dest$OpenSpace.route) +
    (bike_params_simple[15] * ODIN_orig_dest$PNonWester.route) +
    (bike_params_simple[16] * ODIN_orig_dest$PWelfarDep.route)
  
  ODIN_orig_dest$transit_utility = (transit_params_simple[2] * ODIN_orig_dest$income) +
    (transit_params_simple[1]  * ODIN_orig_dest$age) +      
    (hetero_params[[4]][ODIN_orig_dest$age_group] * ODIN_orig_dest$trip_distance_km) +
    (transit_params_simple[3]  * ODIN_orig_dest$DistCBD.orig) +
    (transit_params_simple[4]  * ODIN_orig_dest$pubTraDns.orig) +
    (transit_params_simple[5]  * ODIN_orig_dest$pubTraDns.dest) +
    (transit_params_simple[6]  * ODIN_orig_dest$popDns.route) +
    (transit_params_simple[7]  * ODIN_orig_dest$retaiDns.route) +
    (transit_params_simple[8]  * ODIN_orig_dest$retailDiv.route) +
    (transit_params_simple[9]  * ODIN_orig_dest$NrStrLight.route) +
    (transit_params_simple[10]  * ODIN_orig_dest$CrimeIncid.route) +
    (transit_params_simple[11]  * ODIN_orig_dest$PNonWester.route) +
    (transit_params_simple[12]  * ODIN_orig_dest$PWelfarDep.route)
  
  modechoice = ODIN_orig_dest %>%
    rowwise() %>%
    summarise(
      mode_choice = which.max(c(transit_utility, walking_utility, biking_utility, driving_utility))
    ) 
  modechoice[,c("transit_pred", "walk_pred", "bike_pred", "car_pred")] = 0
  modechoice$transit_pred[which(modechoice$mode_choice == 1)] = 1
  modechoice$walk_pred[which(modechoice$mode_choice == 2)] = 1
  modechoice$bike_pred[which(modechoice$mode_choice == 3)] =1
  modechoice$car_pred[which(modechoice$mode_choice == 4)] = 1
  return(modechoice)
}


modal_split = c(length(which(ODIN_orig_dest$WalkTrip == 1))/nrow(ODIN_orig_dest),
                length(which(ODIN_orig_dest$BikeTrip == 1))/nrow(ODIN_orig_dest),
                length(which(ODIN_orig_dest$CarTrip == 1))/nrow(ODIN_orig_dest),
                length(which(ODIN_orig_dest$PubTransTrip == 1))/nrow(ODIN_orig_dest))
                
## fitness function
fitness = function(x)
{
  # walk_params_simple = x
  if(mode == "bike"){
    bike_params_simple = x[1:length(bike_params_simple)]
    hetero_params[[3]] = x[(length(bike_params_simple)+1):length(x)]
    
   }
  else if(mode == "car"){
    car_params_simple = x[1:length(car_params_simple)]
    hetero_params[[1]] = x[(length(car_params_simple)+1):length(x)]
  }  
  else if(mode == "walk"){
    walk_params_simple = x[1:length(walk_params_simple)]
    hetero_params[[2]] = x[(length(walk_params_simple)+1):length(x)]
  }
  else if(mode == "transit"){
    transit_params_simple = x[1:length(transit_params_simple)]
    hetero_params[[4]] = x[(length(transit_params_simple)+1):length(x)]
  }
  # else if (mode == "complex"){
  #   hetero_params[[1]] = x[1:6]
  #   hetero_params[[2]] = x[7:12]
  #   hetero_params[[3]] = x[13:18]
  #   hetero_params[[4]] = x[19:24]
  # }
  modechoice = calc_modal_choice(car_params_simple = car_params_simple, 
                    walk_params_simple = walk_params_simple,
                    bike_params_simple = bike_params_simple,
                    transit_params_simple = transit_params_simple,
                    hetero_params = hetero_params)
  walk_f1 = f1_score(modechoice$walk_pred,ODIN_orig_dest$WalkTrip)
  if(is.na(walk_f1)){walk_f1 = 0}
  bike_f1 = f1_score(modechoice$bike_pred,ODIN_orig_dest$BikeTrip)
  if(is.na(bike_f1)){bike_f1 = 0}
  car_f1 = f1_score(modechoice$car_pred,ODIN_orig_dest$CarTrip)
  if(is.na(car_f1)){car_f1 = 0}
  transit_f1 = f1_score(modechoice$transit_pred,ODIN_orig_dest$PubTransTrip)
  if(is.na(transit_f1)){transit_f1 = 0}
  weighted_f1 =   (walk_f1 * modal_split[1]) + 
                  (bike_f1 * modal_split[2]) + 
                  (car_f1 * modal_split[3]) + 
                  (transit_f1 * modal_split[4]) 
  print(paste0(mode, " par, F1-scor: walk ", format(round(walk_f1, 2), nsmall = 2), 
               ", car ", format(round(car_f1, 2), nsmall = 2), 
               ", bike ", format(round(bike_f1, 2), nsmall = 2), 
               ", transit ", format(round(transit_f1, 2), nsmall = 2), 
               ", weighted ", weighted_f1))
  return(weighted_f1)
}



mode = "bike"
print(mode)
GA_bike <- ga("real-valued", fitness = fitness,
                  lower = c(rep(0,length(bike_params_simple)+6)), upper = c(rep(3,length(bike_params_simple)+6)), 
                  popSize = 100,  maxiter = 1000, run = 200, seed = 123)
summary(GA_bike)
bike_params_simple = GA_bike@solution[1,][1:length(bike_params_simple)]
hetero_params[[3]] = GA_bike@solution[1,][(length(bike_params_simple)+1):(length(bike_params_simple)+6)]



mode = "walk"
print(mode)
GA_walk <- ga("real-valued", fitness = fitness,
              lower = c(rep(0,length(walk_params_simple)+6)), upper = c(rep(3,length(walk_params_simple)+6)), 
              popSize = 200, maxiter = 1000, run = 200, seed = 123)
summary(GA_walk)
walk_params_simple= GA_walk@solution[1,][1:length(walk_params_simple)]
hetero_params[[2]] = GA_walk@solution[1,][(length(walk_params_simple)+1):(length(walk_params_simple)+6)]



mode = "car"
print(mode)
GA_car <- ga("real-valued", fitness = fitness,
             lower = c(rep(0,length(car_params_simple)+6)), upper = c(rep(10,length(car_params_simple)+6)),
             popSize = 200, maxiter = 1000, run = 200, seed = 123)
summary(GA_car)
car_params_simple= GA_car@solution[1,]


mode = "transit"
print(mode)
GA_transit <- ga("real-valued", fitness = fitness,
                 lower = c(rep(0,length(transit_params_simple)+6)), upper = c(rep(5,length(transit_params_simple)+6)), 
                 popSize = 200,    maxiter = 1000, run = 200, seed = 123)
summary(GA_transit)
transit_params_simple= GA_transit@solution[1,][1:length(transit_params_simple)]
hetero_params[[4]] = GA_hetero@solution[1,][(length(transit_params_simple)+1):(length(transit_params_simple)+6)]




?ga
hill.climbing.search(attributes, eval.fun)
?hill.climbing.search


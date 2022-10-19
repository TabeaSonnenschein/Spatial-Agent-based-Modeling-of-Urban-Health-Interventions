#########################
### Load packages #######
#########################
pkgs = c("GA","bnlearn", "stats", "rgdal","sp", "sf", "rgeos" , "ggplot2", "matrixStats",  "raster",  "dplyr")
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
remove(x)
chunk_size <- 100000 # choose the best size for you
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


## parameters for calibration
income_weight_car = 1
trip_dist_weight_car_age = c(1,2,3,4,5,6)
parking_space_weight_car = 1
car_access_weight = 1   #test as binary or weight
parking_price_weight_car = 1
parking_price_weight_car_income = c(1,2,3)
children_weight_car = 1
DistCBD_weight_car  = 1


trip_dist_weight_walk_age = c(1,2,3,4,5,6)
DistCBD_weight_walk  = 1
pubTraDns_orig_weight_walk  = 1
pubTraDns_dest_weight_walk = 1
popDns_weight_walk  = 1
retaiDns_weight_walk = 1
greenCovr_weight_walk = 1
RdIntrsDns_weight_walk = 1
TrafAccid_weight_walk = 1
AccidPedes_weight_walk = 1
NrTrees_weight_walk = 1
MeanTraffV_weight_walk = 1
HighwLen_weight_walk = 1
PedStrWidt_weight_walk = 1
PedStrLen_weight_walk = 1
retailDiv_weight_walk = 1
MaxSpeed_weight_walk = 1
NrStrLight_weight_walk = 1
CrimeIncid_weight_walk = 1
MaxNoisDay_weight_walk = 1
OpenSpace_weight_walk = 1
PNonWester_weight_walk = 1
PWelfarDep_weight_walk = 1

trip_dist_weight_bike_age = c(1,2,3,4,5,6)
LenBikRout_weight_bike = 1
popDns_weight_bike  = 1
greenCovr_weight_bike = 1
RdIntrsDns_weight_bike = 1
TrafAccid_weight_bike = 1
DistCBD_weight_bike  = 1
NrTrees_weight_bike = 1
MeanTraffV_weight_bike = 1
HighwLen_weight_bike = 1
MaxSpeed_weight_bike = 1
NrStrLight_weight_bike = 1
CrimeIncid_weight_bike = 1
MaxNoisDay_weight_bike = 1
OpenSpace_weight_bike = 1
PNonWester_weight_bike = 1
PWelfarDep_weight_bike = 1

age_weight_transit = 1
income_weight_transit = 1
trip_dist_weight_transit_age = c(1,2,3,4,5,6)
DistCBD_weight_transit  = 1
pubTraDns_orig_weight_transit  = 1
pubTraDns_dest_weight_transit = 1
popDns_weight_transit  = 1
retaiDns_weight_transit = 1
retailDiv_weight_transit = 1
NrStrLight_weight_transit = 1
CrimeIncid_weight_transit = 1
PNonWester_weight_transit = 1
PWelfarDep_weight_transit = 1



ODIN_orig_dest$driving_utility = (income_weight_car * ODIN_orig_dest$income) +
                                 (trip_dist_weight_car_age[ODIN_orig_dest$age_group] * ODIN_orig_dest$trip_distance) +
                                 (parking_space_weight_car * ODIN_orig_dest$NrParkSpac.dest) +
                                 (parking_price_weight_car * ODIN_orig_dest$PrkPricPos.dest) +
                                 (children_weight_car * ODIN_orig_dest$nr_children_yonger6) +
                                 (DistCBD_weight_car * ODIN_orig_dest$DistCBD.orig)


ODIN_orig_dest$driving_utility[ODIN_orig_dest$car_access > 0]  = 0
ODIN_orig_dest$driving_utility

ODIN_orig_dest$walking_utility = (trip_dist_weight_walk_age[ODIN_orig_dest$age_group] * ODIN_orig_dest$trip_distance) +
                                  (DistCBD_weight_walk * ODIN_orig_dest$DistCBD.orig) +
                                  (pubTraDns_orig_weight_walk * ODIN_orig_dest$pubTraDns.orig) +
                                  (pubTraDns_dest_weight_walk * ODIN_orig_dest$pubTraDns.dest) +
                                  (popDns_weight_walk * ODIN_orig_dest$popDns.route) +
                                  (retaiDns_weight_walk * ODIN_orig_dest$retaiDns.route) +
                                  (greenCovr_weight_walk * ODIN_orig_dest$greenCovr.route) +
                                  (RdIntrsDns_weight_walk * ODIN_orig_dest$RdIntrsDns.route) +
                                  (TrafAccid_weight_walk * ODIN_orig_dest$TrafAccid.route) +
                                  (AccidPedes_weight_walk * ODIN_orig_dest$AccidPedes.route) +
                                  (NrTrees_weight_walk * ODIN_orig_dest$NrTrees.route) +
                                  (MeanTraffV_weight_walk * ODIN_orig_dest$MeanTraffV.route) +
                                  (HighwLen_weight_walk * ODIN_orig_dest$HighwLen.route) +
                                  (PedStrWidt_weight_walk * ODIN_orig_dest$PedStrWidt.route) +
                                  (PedStrLen_weight_walk * ODIN_orig_dest$PedStrLen.route) +
                                  (retailDiv_weight_walk * ODIN_orig_dest$retailDiv.route) +
                                  (MaxSpeed_weight_walk * ODIN_orig_dest$MaxSpeed.route) +
                                  (NrStrLight_weight_walk * ODIN_orig_dest$NrStrLight.route) +
                                  (CrimeIncid_weight_walk * ODIN_orig_dest$CrimeIncid.route) +
                                  (MaxNoisDay_weight_walk * ODIN_orig_dest$MaxNoisDay.route) +
                                  (OpenSpace_weight_walk * ODIN_orig_dest$OpenSpace.route) +
                                  (PNonWester_weight_walk * ODIN_orig_dest$PNonWester.route) +
                                  (PWelfarDep_weight_walk * ODIN_orig_dest$PWelfarDep.route)


ODIN_orig_dest$walking_utility

ODIN_orig_dest$biking_utility = (trip_dist_weight_bike_age[ODIN_orig_dest$age_group] * ODIN_orig_dest$trip_distance) +
                                  (DistCBD_weight_bike * ODIN_orig_dest$DistCBD.orig) +
                                  (popDns_weight_bike * ODIN_orig_dest$popDns.route) +
                                  (greenCovr_weight_bike * ODIN_orig_dest$greenCovr.route) +
                                  (RdIntrsDns_weight_bike * ODIN_orig_dest$RdIntrsDns.route) +
                                  (TrafAccid_weight_bike * ODIN_orig_dest$TrafAccid.route) +
                                  (LenBikRout_weight_walk * ODIN_orig_dest$LenBikRout.route) +
                                  (NrTrees_weight_bike * ODIN_orig_dest$NrTrees.route) +
                                  (MeanTraffV_weight_bike * ODIN_orig_dest$MeanTraffV.route) +
                                  (HighwLen_weight_bike * ODIN_orig_dest$HighwLen.route) +
                                  (MaxSpeed_weight_bike * ODIN_orig_dest$MaxSpeed.route) +
                                  (NrStrLight_weight_bike * ODIN_orig_dest$NrStrLight.route) +
                                  (CrimeIncid_weight_bike * ODIN_orig_dest$CrimeIncid.route) +
                                  (MaxNoisDay_weight_bike * ODIN_orig_dest$MaxNoisDay.route) +
                                  (OpenSpace_weight_bike * ODIN_orig_dest$OpenSpace.route) +
                                  (PNonWester_weight_bike * ODIN_orig_dest$PNonWester.route) +
                                  (PWelfarDep_weight_bike * ODIN_orig_dest$PWelfarDep.route)


ODIN_orig_dest$biking_utility



ODIN_orig_dest$transit_utility = (income_weight_car * ODIN_orig_dest$income) +
                                  (age_weight_transit * ODIN_orig_dest$age) +      
                                  (trip_dist_weight_transit_age[ODIN_orig_dest$age_group] * ODIN_orig_dest$trip_distance) +
                                  (DistCBD_weight_transit * ODIN_orig_dest$DistCBD.orig) +
                                  (pubTraDns_orig_weight_transit * ODIN_orig_dest$pubTraDns.orig) +
                                  (pubTraDns_dest_weight_transit * ODIN_orig_dest$pubTraDns.dest) +
                                  (popDns_weight_transit * ODIN_orig_dest$popDns.route) +
                                  (retaiDns_weight_transit * ODIN_orig_dest$retaiDns.route) +
                                  (retailDiv_weight_transit * ODIN_orig_dest$retailDiv.route) +
                                  (NrStrLight_weight_transit * ODIN_orig_dest$NrStrLight.route) +
                                  (CrimeIncid_weight_transit * ODIN_orig_dest$CrimeIncid.route) +
                                  (PNonWester_weight_transit * ODIN_orig_dest$PNonWester.route) +
                                  (PWelfarDep_weight_transit * ODIN_orig_dest$PWelfarDep.route)


ODIN_orig_dest$transit_utility


modechoice = ODIN_orig_dest %>%
  rowwise() %>%
  summarise(
    mode_choice = which.max(c(walking_utility, biking_utility, driving_utility, transit_utility))
  ) 


modechoice



season (weather)



## behavioral model replica

fitness <- function(x)
{
#  f <- -f(x)                         # we need to maximise -f(x)

  
  
  
  
  
    penalty1 <- max(c1(x),0)*pen       # penalisation for 1st inequality constraint
  penalty2 <- max(c2(x),0)*pen       # penalisation for 2nd inequality constraint
  f - penalty1 - penalty2            # fitness function value
}

GA <- ga("real-valued", fitness = fitness,
         lower = c(0,0), upper = c(1,13),
         # selection = GA:::gareal_lsSelection_R,
         maxiter = 1000, run = 200, seed = 123)
summary(GA)

hill.climbing.search(attributes, eval.fun)


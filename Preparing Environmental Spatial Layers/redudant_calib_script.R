income_weight_car = 1
trip_dist_weight_car_age = c(1,2,3,4,5,6)
parking_space_weight_car = 1
car_access_weight = 1   #test as binary or weight
parking_price_weight_car = 1
children_weight_car = 1
DistCBD_weight_car  = 1


trip_dist_weight_walk_age = c(1,2,3,4,5,6)
DistCBD_weight_walk = 1
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


trip_dist_weight_transit_age = c(1,2,3,4,5,6)
age_weight_transit = 1
income_weight_transit = 1
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
  (parking_price_weight_car * ODIN_orig_dest$PrkPricPre.dest) +
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
  (LenBikRout_weight_bike * ODIN_orig_dest$LenBikRout.route) +
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

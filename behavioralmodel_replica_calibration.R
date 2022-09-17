## behavioral model replica


reflex modalchoice when: make_modalchoice = 1 {
  new_route <- 1;
  make_modalchoice <- 0;
  driving_utility <- (affordability_weight * float(affordability["perc_budget_car"]))
  + (traveltime_weight * float(assumed_traveltime["traveltime_car"]))
  + (tripdistance_weight_age_car[agegroup] * tripdistance_weight_BMI_car[weightgroup] * (trip_distance/1000));
  walking_utility <- (affordability_weight * float(affordability["perc_budget_walk"]))
  + (pop_density_weight_walk * float(assumed_quality_infrastructure["pop_density"]))
  + (retail_density_weight_walk * float(assumed_quality_infrastructure["retail_density"]))
  + (greenCoverage_weight_walk * float(assumed_quality_infrastructure["greenCoverage"]))
  + (public_Transport_density_weight_walk * float(assumed_quality_infrastructure["public_Transport_density"]))
  + (road_intersection_density_weight_walk * float(assumed_quality_infrastructure["road_intersection_density"]))
  + (traveltime_weight * float(assumed_traveltime["traveltime_walk"]))
  + (tripdistance_weight_age_walk[agegroup] * tripdistance_weight_BMI_walk[weightgroup] * (trip_distance/1000));
  biking_utility <- (affordability_weight * float(affordability["perc_budget_bike"]))
  + (pop_density_weight_bike * float(assumed_quality_infrastructure["pop_density"]))
  + (retail_density_weight_bike * float(assumed_quality_infrastructure["retail_density"]))
  + (greenCoverage_weight_bike * float(assumed_quality_infrastructure["greenCoverage"]))
  + (public_Transport_density_weight_bike * float(assumed_quality_infrastructure["public_Transport_density"]))
  + (road_intersection_density_weight_bike * float(assumed_quality_infrastructure["road_intersection_density"]))
  + (traveltime_weight * float(assumed_traveltime["traveltime_bike"]))
  + (tripdistance_weight_age_bike[agegroup] * tripdistance_weight_BMI_bike[weightgroup] * (trip_distance/1000));
  if(trip_distance <= distance_willing_travel["walk"]){
    if(car_owner = 1){
      modalchoice <- ["car", "walk", "bike"] at ([driving_utility, walking_utility, biking_utility] index_of  max([driving_utility, walking_utility, biking_utility]));
    }
    else{
      modalchoice <- ["walk", "bike"] at ([walking_utility, biking_utility] index_of  max([walking_utility, biking_utility]));
    }
  }
  else if(trip_distance <= distance_willing_travel["bike"]){
    if(car_owner = 1){
      modalchoice <- ["car","bike"] at ([driving_utility, biking_utility] index_of  max([driving_utility, biking_utility]));
    }
    else{
      modalchoice <- "bike";
    }
  }
  else{
    if(car_owner = 1){
      modalchoice <- "car";
    }
    else{
      modalchoice <- "bike";
    }
  }
  write string(trip_distance) + " " + modalchoice ;
}

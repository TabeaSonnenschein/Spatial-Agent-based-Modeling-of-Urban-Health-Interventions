/**
* Name: TransportAirPollutionExposureModel
* Author: Tabea Sonnenschein
* Tags: 
*/

model TransportAirPollutionExposureModel
  
global skills: [RSkill]{
	/** Insert the global definitions, variables and actions here */
	
//	loading the spatial built environment
	file shape_file_buildings <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp");
	file shape_file_buildings2 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp");
	file shape_file_buildings3 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp");
    file shape_file_streets <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/Car Traffic_RDNew.shp");
    file shape_file_greenspace <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew.shp");
    file shape_file_Residences <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp");    
    file shape_file_Schools <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_schools_RDNew.shp");
    file shape_file_Supermarkets <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp");
    file shape_file_Universities <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_universities_RDNew.shp");
    file shape_file_Kindergardens <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp");
    file shape_file_Restaurants <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_Food_RDNew.shp");
    file shape_file_Entertainment <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew.shp");
    file shape_file_ShopsnServ <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_ShopsServ_RDNew.shp");
    file shape_file_Nightlife <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_Nightlife_RDNew.shp");
    file shape_file_Profess <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_Profess_other_RDNew.shp");
    file spatial_extent <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Amsterdam Diemen Oude Amstel Extent.shp");  
   	geometry shape <- envelope(spatial_extent); 
   	map<string,rgb> color_per_type <- ["streets"::#aqua, "vegetation":: #green, "buildings":: #red];
    
//  loading Environmental Stressor Maps
	file shape_file_NoiseContour_night <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Environmental Stressors/Noise/PDOK_NoiseMap2016_Lnight_RDNew_clipped.shp");
	file shape_file_NoiseContour_day <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Environmental Stressors/Noise/PDOK_NoiseMap2016_Lden_RDNew_clipped.shp");
//    file Tiff_file_PM2_5 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Environmental Stressors/Noise/PM2_5_RDNew_clipped.tif");
    
//  loading routing code
    file Rcode_foot_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM_foot.R");
    file Rcode_car_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM_car.R");
    file Rcode_bike_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM_bike.R");

//  loading agent population attributes
    int nb_humans <- 150;
//    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop.csv", ";", string, true);
    file Rcode_agent_subsetting <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/Subsetting_Synthetic_AgentPop_for_GAMA.R");
    csv_file Synth_Agent_file;
    
    
//    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_100.csv", ";", string, true);
//	text_file schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/mock_schedule.txt");
	text_file kids_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/kids_schedule.txt");
	text_file youngadult_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/youngadult_schedule.txt");
	text_file adult_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/adult_schedule.txt");
	text_file elderly_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/elderly_schedule.txt");

    init  {
        write "setting up the model";
        do startR;
        write R_eval("nb_humans = " + to_R_data(nb_humans));
        loop s over: Rcode_agent_subsetting.contents{
							unknown a <- R_eval(s);
						}
		Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_GAMA.csv", ";", string, true);
		create Homes from: shape_file_Residences with: [Neighborhood:: read('nghb_cd')];
		create Noise_day from: shape_file_NoiseContour_day with: [Decibel :: float(read('bovengrens'))] ;
        create Humans from: Synth_Agent_file with:[Agent_ID :: read('Agent_ID'), Neighborhood :: read('neighb_code'), 
	        age:: int(read('age')), sex :: read('sex'), migrationbackground :: read('migrationbackground'),
	        hh_single :: int(read('hh_single')), is_child:: int(read('is_child')), has_child:: int(read('has_child')), 
        	current_edu:: read('current_education'), absolved_edu:: read('absolved_education'), BMI:: read('BMI'), scheduletype:: read('scheduletype')]; // careful: column 1 is has the index 0 in GAMA      //
    }
    float step <- 1 #mn;  /// #mn minutes #h hours  #sec seconds #day days #week weeks #year years
    date starting_date <- date([2019,1,1,6,0,0]); //correspond the 1st of January 2019, at 6:00:00
    int year;
}

species Homes{
	string Neighborhood;
}


species Noise_day{
	float Decibel;
}

species Humans skills:[moving, RSkill] control: simple_bdi parallel: true{
	 // definition of attributes, actions, behaviors	
	 
/////// declaring variables //////////
	 /// individual characteristics
	string Agent_ID;
	int Agent_index;
	string Neighborhood;
	int age;
	string sex;
	string migrationbackground;
	int hh_single;
	int is_child;
	int has_child;
	string current_edu;
	string absolved_edu;
	string BMI;
	string scheduletype;
	
	/// destination locations
	geometry residence;
	geometry workplace;
	geometry school;
	geometry university;
	geometry kindergarden;
	geometry supermarket;
	
	/// saved routes (for efficiency)
	path homeTOwork;
	string homeTOwork_mode;
	geometry homeTOwork_geometry;
	float homeTOwork_duration;
	path homeTOuni;
	string homeTOuni_mode;
	geometry homeTOuni_geometry;
	float homeTOuni_duration;
	path homeTOschool;
	string homeTOschool_mode;
	geometry homeTOschool_geometry;
	float homeTOschool_duration;	
	
	/// activity variables
	string activity;
	list<string> schedule;
	/// weekday and weekend schedule
	string current_activity;
	string former_activity;
	geometry destination_activity;
	int traveldecision;
	
	/// travel variables
	float track_duration;
	path track_path;
	geometry track_geometry;
	string modalchoice;
	float travelspeed;
	int path_memory;
	int return_dum <- 0;
	geometry route_eucl_line;

	/// exposure variables
	float inhalation_rate_walking <- 25.0;	 //25 breaths per minute
	float inhalation_rate_biking <- 40.0;	 //40 breaths per minute
	float inhalation_rate_normal <- 15.0 ; //15 breaths per minute
	float indoor_Noise_filter <- 0.20; //80% of Noise filtered
	float indoor_AirPollutionFilter <- 0.60; /// 40% of Air POllution filtered
	float bike_exposure;
	float walk_exposure;
	float activity_PM10;
	float hourly_PM10;	
	float daily_PM10;
	float yearly_PM10;
	float hourly_PM2_5;
	float daily_PM2_5;
	float yearly_PM2_5;
	float activity_Noise;
	float hourly_Noise;
	float daily_Noise;
	float yearly_Noise;
	
	//////// TRANSPORT BEHAVIOUR: BDI ///////////////
	/// Transport Behaviour: Desires///
	float convenience;
	float affordability;
	int safety;
	int norm_abidence;
	
	/// Transport Behaviour: Beliefs///
	float assumed_traveltime;
//	float assumed_bikability;
//	float assumed_walkability; 
	predicate assumed_accessibility <- new_predicate("assumed_accessibility");
	predicate assumed_cost <- new_predicate("assumed_cost"); 
	predicate assumed_safety <- new_predicate("assumed_safety");
	predicate own_budget <- new_predicate("own_budget"); 
	predicate social_norms <- new_predicate("social_norms");
	
	/// Transport Behaviour: Emotions ///
	
	
/////// setting up the initial parameters and relations //////////
	init{
		  if(scheduletype = "youngadult"){
		  	schedule <- list(youngadult_schedules_file);
		  }
		  else if (scheduletype = "adult"){
		  	schedule <- list(adult_schedules_file);
		  }
		  else if (scheduletype = "kids"){
		  	schedule <- list(kids_schedules_file);
		  }
		  else if (scheduletype = "elderly"){
		  	schedule <- list(elderly_schedules_file);
		  }
//		  schedule <- list(schedules_file);
		  
		  residence <- one_of(Homes where (each.Neighborhood = self.Neighborhood)) ;
       	  location <- residence.location;
       	  if(schedule contains "work"){
       	  	    workplace <- one_of(shape_file_Profess);
       	  }
       	  if(schedule contains "school"){
       	  		school <- closest_to(shape_file_Schools, self.location);
       	  }
       	  if(schedule contains "university"){
				university <- closest_to(shape_file_Universities, self.location);
       	  }
       	  if(schedule contains "kindergarden"){
				kindergarden <- closest_to(shape_file_Kindergardens, self.location);
       	  }
       	  if(schedule contains "kindergarden"){
				supermarket <-  closest_to(shape_file_Supermarkets, self.location) ;
       	  }       	     	
       	  activity <- "perform_activity";
       	  
       	  do startR;
	}
	
/////// defining the Human transition functions (behaviour and exposure) //////////
	reflex schedule_manager when: ((current_date.minute mod 10) = 0) {
		 current_activity <- schedule[int((current_date.minute/10) + (current_date.hour * 6))];
		 if(int((current_date.minute/10)) != 0){
		 	former_activity <- schedule[int(((current_date.minute/10) + (current_date.hour * 6))-1)];
		 }
		 else{
		 	former_activity <- last(schedule) ;
		 }
		 if(current_activity != former_activity){
		 	if(current_activity = "work"){
				destination_activity <- workplace;
				if(homeTOwork != nil and self.location = residence.location){
					track_path <- homeTOwork;
					track_geometry <- homeTOwork_geometry;
					modalchoice <- homeTOwork_mode;
					track_duration <- homeTOwork_duration;
					path_memory <- 1;
				}		 		
		 	}
		 	else if(current_activity = "school"){
		 		destination_activity <- school;
		 		if(homeTOschool != nil and self.location = residence.location){
					track_path <- homeTOschool;
					track_geometry <- homeTOschool_geometry;
					modalchoice <- homeTOschool_mode;
					track_duration <- homeTOschool_duration;
					path_memory <- 1;
				}		
		 	}
		 	else if(current_activity = "university"){
		 		destination_activity <- university;
		 		if(homeTOuni != nil and self.location = residence.location){
					track_path <- homeTOuni;
					track_geometry <- homeTOuni_geometry;
					track_duration <- homeTOuni_duration;
					modalchoice <- homeTOuni_mode;
					path_memory <- 1;
				}		
		 	}
		 	else if(current_activity = "groceries_shopping"){
		 		destination_activity <- supermarket;
		 	}
		 	else if(current_activity = "kindergarden"){
		 		destination_activity <- kindergarden;
		 	}
		 	else if(current_activity = "sleeping" or current_activity = "at_Home"){
		 		destination_activity <- self.residence;
//		 		if(homeTOwork != nil and self.location = workplace.location){
////		 			container reverse <- reverse(container(geometry_collection(homeTOwork_geometry)));
////		 			track_geometry <- line(reverse) add_point self.residence.location;
////		 			track_path <- path(track_geometry);
////		 			write "HometoWork: "   + homeTOwork_geometry;
////		 			write "reverse: " +   reverse;
////		 			write "Trackpath: "  + track_path;
//					track_path <- homeTOwork;
//					track_geometry <- homeTOwork_geometry;
//					modalchoice <- homeTOwork_mode;
//					track_duration <- homeTOwork_duration;
//					path_memory <- 1;
//					return_dum <- 1;
//		 		}
		 		
		 	}
		 	else if(current_activity = "entertainment" ){
		 		destination_activity <- one_of(shape_file_Entertainment);
		 	}
		 	else if(current_activity = "eat" ){
		 		if (one_of(shape_file_Restaurants inside circle(500, self.location)) != nil){
		 			destination_activity <- one_of(shape_file_Restaurants inside circle(500, self.location));
		 		}
		 		else{
		 			destination_activity <- closest_to(shape_file_Restaurants, self.location);
		 		}
		 	}
		 	else if(current_activity = "social_life" ){
		 		destination_activity <- one_of(shape_file_Residences);
		 	}
		 	write current_activity;
		 	if(destination_activity.location != self.location){
//		 		activity <- "commuting";
		 		route_eucl_line <- line(container(point(self.location), point(destination_activity.location)));
		 		write "Route Line:" + route_eucl_line;
		 		if(path_memory != 1){
		 			traveldecision <- 1;
		 			/// routing through OSRM via R interface
		 			write R_eval("origin = " + to_R_data(container(self.location CRS_transform("EPSG:4326"))));
		 			write R_eval("destination = " + to_R_data(container(destination_activity.location CRS_transform("EPSG:4326"))));	
		 			if((self.location distance_to destination_activity) < 1000){
		 				modalchoice <- "walk";
		 				loop s over: Rcode_foot_routing.contents{
							unknown a <- R_eval(s);
//							write "R>" + a;
						}
						travelspeed <- 1.4; /// meters per seconds 5km/h
		 			}
		 			else if((self.location distance_to destination_activity) < 3000){
		 		 		modalchoice <- "bike";
		 		 		loop s over: Rcode_bike_routing.contents{
							unknown a <- R_eval(s);
						}
						travelspeed <- 3.33; /// meters per seconds 12km/h
		 			}
		 			else{
		 			 	modalchoice <- "car";		
		 			 	loop s over: Rcode_car_routing.contents{
							unknown a <- R_eval(s);
						}
						travelspeed <- 11.11; /// meters per seconds 40km/h 			
		 			}
		 			list<point> track <- list(R_eval("track_points"));
		 			track_geometry <- (to_GAMA_CRS(line(track),  "EPSG:4326")) add_point(destination_activity.location);
					track_path <-  path(track_geometry);     	  
					track_duration <- float(list(R_eval("route$duration"))[0]);  ///minutes
					float track_length <- float(list(R_eval("route$distance"))[0]);	/// meters
					if(current_activity = "work" and self.location = residence.location){
						homeTOwork <- track_path;
						homeTOwork_mode <- modalchoice;
						homeTOwork_geometry <- track_geometry ;
						homeTOwork_duration <- track_duration;
					}
					else if(current_activity = "school" and self.location = residence.location){
						homeTOschool <- track_path;
						homeTOschool_mode <- modalchoice;
						homeTOschool_geometry <- track_geometry ;
						homeTOschool_duration <- track_duration;
					}
					else if(current_activity = "university" and self.location = residence.location){
						homeTOuni <- track_path;
						homeTOuni_mode <- modalchoice;
						homeTOuni_geometry <- track_geometry ;
						homeTOuni_duration <- track_duration;
					}
		 		}
		 		path_memory <- 0;
		 	}
		 	else{
		 		activity <-"perform_activity";
		 		traveldecision <- 0;
		 	}
		 }
	}
//	reflex any_activity when: activity = "perform_activity" and current_activity = "name of activity"{
//		e.g. the activity could have an impact on health (sports...)
//	}
	reflex at_Place_exposure when: activity = "perform_activity"{
		activity_PM10 <- (sum((Environment_stressors overlapping self) collect each.AirPoll_PM10)) * inhalation_rate_normal * indoor_AirPollutionFilter;
		activity_Noise <- (sum((Noise_day overlapping self) collect each.Decibel)) * indoor_Noise_filter;
		hourly_PM10 <- hourly_PM10 + activity_PM10;
		hourly_Noise <- hourly_Noise + activity_Noise;
	}
	
    reflex commuting when: activity = "commuting"{
//		if(self.return_dum = 1){
//				do follow path: self.track_path speed: travelspeed return_path: true;	
//		}
//		else{
			do follow path: self.track_path speed: travelspeed;
//		}
		if(self.location = destination_activity.location){
    		activity <- "perform_activity";
    		if(modalchoice = "bike"){
    			bike_exposure <- bike_exposure + track_duration;
				activity_PM10 <- (sum((Environment_stressors overlapping self.track_geometry) collect each.AirPoll_PM10)/( length(Environment_stressors overlapping self.track_geometry) + 1)) * inhalation_rate_biking * track_duration;
				activity_Noise <- (sum((Noise_day overlapping self.track_geometry) collect each.Decibel)/(length(Noise_day overlapping self.track_geometry) +1) )  * track_duration;
				hourly_PM10 <- hourly_PM10 + activity_PM10;
				hourly_Noise <- hourly_Noise + activity_Noise;
    		}
    		 else if(modalchoice = "walk"){
    			walk_exposure <- walk_exposure + track_duration;
    			activity_PM10 <- (sum((Environment_stressors overlapping self.track_geometry) collect each.AirPoll_PM10)/ (length(Environment_stressors overlapping self.track_geometry)+ 1)) * inhalation_rate_walking * track_duration;
				activity_Noise <- (sum((Noise_day overlapping self.track_geometry) collect each.Decibel)/(length(Noise_day overlapping self.track_geometry) + 1))  * track_duration;
				hourly_PM10 <- hourly_PM10 + activity_PM10;
				hourly_Noise <- hourly_Noise + activity_Noise;
				
    		}
    		else{
    			activity_PM10 <- (sum((Environment_stressors overlapping self.track_geometry) collect each.AirPoll_PM10)/ (length(Environment_stressors overlapping self.track_geometry) +1 )) * inhalation_rate_normal * track_duration * 0.2;
				activity_Noise <- (sum((Noise_day overlapping self.track_geometry) collect each.Decibel)/(length(Noise_day overlapping self.track_geometry) + 1))  * track_duration * 0.3;
				hourly_PM10 <- hourly_PM10 + activity_PM10;
				hourly_Noise <- hourly_Noise + activity_Noise;
				
    		}
//    		if(self.return_dum = 1){
//    			return_dum <- 0;
//    		}
    		
    	}
    }
    perceive Env_Activity_Affordance_Travel target:(Perceivable_Environment where (each intersects route_eucl_line))  when: traveldecision = 1 {
    	myself.activity <- "commuting";
    	myself.traveldecision <- 0;	
    	ask myself{
//    		assumed_bikability <- mean(myself.bikability);
//    		assumed_walkability <- mean(myself.walkability);    		
    		do add_belief(new_predicate("assumed_bikability", ["route_bikability"::mean(myself.bikability)]));
    		do add_belief(new_predicate("assumed_walkability", ["route_walkability"::mean(myself.walkability)])); 
//    		write "route_walkability" + get_predicate(get_belief_with_name("assumed_walkability")).values["route_walkability"];  		
//    		assumed_accessibility <- with_values(assumed_accessibility , ["distance":: 10.0]); 
//    		write "assumed_accessibility" + get_predicate(get_belief_with_name("assumed_accessibility")).values["distance"];  		
    		
    	}
//    	write walkability;
    }
    
    reflex update_exposure when: current_date.minute = 0{
    	daily_PM10 <- daily_PM10 + hourly_PM10;
    	hourly_PM10 <- 0.0;
    }
    reflex acute_exposure_impacts when: current_date.hour = 0{	
    	daily_PM10 <- 0.0;
//		daily_PM2_5
//		daily_Noise
    }
    reflex chronic_exposure_impacts when: current_date.year > year{
//    	yearly_PM10
//		yearly_PM2_5
// 		yearly_Noise
    }
    aspect base {
    	if(activity = "perform_activity"){
    		   draw sphere(30) color: #yellow;
    	}
    	else if(activity = "commuting"){
    		if(modalchoice = "bike"){
    			draw cube(60) color: #blue;
    			
    		}
    		else if(modalchoice =  "walk"){
    			draw cube(60) color: #green;
    			
    		}
    		else{
    			draw cube(60) color: #red;
    		}
    	}
    	
    }
}


grid Environment_stressors cell_width: 100 cell_height: 100  parallel: true{
	float AirPoll_PM2_5 <- gauss({20,2.6});
	float AirPoll_PM10 <- gauss({10,2.6}); /// min: 0.0 max: 100.0;
	float AirPoll_NO2 <- gauss({10,2.6});
	float Noise_Decibel_night;
	float Noise_Decibel_day;
//	rgb color <- #green update: rgb(255 *(AirPoll_PM10/30.0) , 255 * (1 - (AirPoll_PM10/30.0)), 0.0);
//	reflex stressor_adjustment{
//		AirPoll_PM10 <- AirPoll_PM10 * 0.7;
//		diffuse var: AirPoll_PM10 on: Environment_stressors proportion: 0.9 ;
//	}
	
}

grid Perceivable_Environment cell_width: 50 cell_height: 50 parallel: true{
	float bikability <- gauss({20,2.6});
	float walkability <- gauss({10,3.6});
}


experiment TransportAirPollutionExposureModel type: gui {
	/** Insert here the definition of the input and output of the model */
	parameter "Number of human agents" var: nb_humans min: 10 max: 10000 category: "Human attributes" ;
	
	output {
//		layout horizontal([vertical([0::10000])::7000,vertical([1::8000,2::2000])::3000]) tabs: false;
//		layout #split;
		display map type:opengl {
    	graphics background{
    		draw shape color: #black;
    	}
        graphics Buildings{
    		draw shape_file_buildings color: #red;
    		draw shape_file_buildings2 color: #red;
    		draw shape_file_buildings3 color: #red;
		}
		graphics Streets{
    		draw shape_file_streets color: #aqua;
		}
		graphics GreenSpace{
    		draw shape_file_greenspace color: #green;
		}
        species Humans aspect: base ;
//        grid Environment_stressors elevation: AirPoll_PM10 * 3.0 triangulation: true transparency: 0.7;
		graphics Noise transparency: 0.7{
			if(current_date.hour < 4 or current_date.hour > 22){
				draw shape_file_NoiseContour_night color: #purple ;
			}
			else{
				draw shape_file_NoiseContour_day color: #purple ;				
			}
		}
//		graphics AirPollution{
//				draw Tiff_file_PM2_5 color:#forestgreen ;
//		}        
//        
        overlay position: { 5, 5 } size: { 180 #px, 100 #px } background: # black transparency: 0.3 border: #black rounded: true
            {
            	//for each possible type, we draw a square with the corresponding color and we write the name of the type
                float y <- 30#px;
                loop type over: color_per_type.keys
                {
                    draw square(10#px) at: { 20#px, y } color: color_per_type[type] border: #white;
                    draw type at: { 50#px, y + 5#px } color: # white font: font("SansSerif", 16, #bold);
                    y <- y + 25#px;
                }

            }
        
    }
    display stats type: java2D synchronized: true{
//		chart " my_chart " type: histogram {
//			datalist ( distribution_of ( Humans collect each.age , 20 ,0 ,100) at " legend ") 
//				value: ( distribution_of ( Humans collect each.age, 20 ,0 ,100) at " values ");
//		}
//		chart "Age Distribution" type: histogram background: #white size: {0.5,0.5} position: {0, 0.5}{
//				data "age" value: Humans collect each.age;
//		}
		chart "Mean Noise Exposure" type: scatter x_label: "Minutes" y_label: "Decibel" background: #white size: {0.5,0.5} position: {0, 0}{
				data "Noise exposure" value: mean(Humans collect each.activity_Noise) color: #blue marker: false style: line;
		}
		chart "Mean PM10 Exposure" type: scatter x_label: "Minutes" y_label: "µg" background: #white size: {0.5,0.5} position: {0.5, 0}{
				data "PM10 exposure" value: mean(Humans collect each.activity_PM10) color: #blue marker: false style: line;
		}
		chart "Agent Age Distribution" type: histogram background: #white size: {0.5,0.5} position: {0, 0.5} {
				data "0-10" value: Humans count (each.age <= 10) color:#blue;
				data "11-20" value: Humans count ((each.age > 10) and (each.age <= 20)) color:#blue;
				data "21-30" value: Humans count ((each.age > 20) and (each.age <= 30)) color:#blue;
				data "31-40" value: Humans count ((each.age > 30) and (each.age <= 40)) color:#blue;
				data "41-50" value: Humans count ((each.age > 40) and (each.age <= 50)) color:#blue;
				data "51-60" value: Humans count ((each.age > 50) and (each.age <= 60)) color:#blue;
				data "61-70" value: Humans count ((each.age > 60) and (each.age <= 70)) color:#blue;
				data "71-80" value: Humans count ((each.age > 70) and (each.age <= 80)) color:#blue;
				data "81 or" value: Humans count (each.age > 81) color:#blue;
			}
		chart "Agent Sex Distribution" type: histogram background: #white size: {0.5,0.5} position: {0.5, 0.5} {
				data "male" value: Humans count (each.sex = "male") color:#red;
				data "female" value: Humans count (each.sex = "female") color:#red;
			}
			
  	 }
  	 	monitor "time" value: current_date;
//  	 	monitor "activity" value: schedules_file[int((current_date.minute/10) + (current_date.hour * 6))];
  	 	monitor "Number of bikers" value: Humans count (each.modalchoice = "bike" and each.activity = "commuting");
  	 	monitor "Number of pedestrians" value: Humans count (each.modalchoice = "walk" and each.activity = "commuting");
  	 	monitor "Number of drivers" value: Humans count (each.modalchoice = "car" and each.activity = "commuting");
  	 	
    }
}




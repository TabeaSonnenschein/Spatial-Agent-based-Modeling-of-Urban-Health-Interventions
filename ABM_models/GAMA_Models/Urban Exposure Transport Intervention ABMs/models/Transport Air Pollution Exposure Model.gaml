/**
* Name: TransportAirPollutionExposureModel
* Author: Tabea Sonnenschein
* Description:
* Tags: Urban Health; 
*/

model TransportAirPollutionExposureModel
  
global skills: [RSkill]{
	/** Insert the global definitions, variables and actions here */
	
	string path_data <- "C:/Users/Tabea/Documents/PhD EXPANSE/Data/";
	string path_workspace <- "C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/";
	
//	loading the spatial built environment
	file shape_file_buildings <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp");
	file shape_file_buildings2 <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp");
	file shape_file_buildings3 <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp");
// file shape_file_streets <- shape_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/cars/Car Traffic_RDNew.shp");
    file shape_file_streets <- shape_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/Amsterdam_roads_RDNew.shp");
    file shape_file_greenspace <- shape_file(path_data+"Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew_window.shp");
	file shape_file_Residences <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp");    
    file shape_file_Schools <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_schools_RDNew.shp");
    file shape_file_Supermarkets <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp");
    file shape_file_Universities <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_universities_RDNew.shp");
    file shape_file_Kindergardens <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp");
    file shape_file_Restaurants <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Food_RDNew.shp");
    file shape_file_Entertainment <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew.shp");
    file shape_file_ShopsnServ <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_ShopsServ_RDNew.shp");
    file shape_file_Nightlife <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Nightlife_RDNew.shp");
    file shape_file_Profess <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Profess_other_RDNew.shp");
    file spatial_extent <- shape_file(path_data+"Amsterdam/SpatialExtent/Amsterdam Diemen Oude Amstel Extent.shp");  
   	geometry shape <- envelope(spatial_extent); 
   	map<string,rgb> color_per_type <- ["streets"::#aqua, "vegetation":: #green, "buildings":: #firebrick, "noise":: #purple];
   	list<geometry> Restaurants;
   	list<geometry> Entertainment;
    
    //  loading grid with walkability measures
//    file shape_file_walkability <- shape_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/walkability_grid.shp");
    file rasterfile_walkability <- grid_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/walkability_grid.tif");
    csv_file walkability_data <- csv_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/walkability_measures.csv", ",", string); 
    //	columnnames:  "popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "Intid"

    //  loading grid with airpollution determinants
    file airpoll_determ_raster <- grid_file(path_data+"Amsterdam/Air Pollution Determinants/AirPollDeterm_grid.tif");
    csv_file airpoll_determ_data <- csv_file(path_data+"Amsterdam/Air Pollution Determinants/AirPollDeterm_grid50.csv", ",", string); 
    //	columnnames: 

    
//  loading Environmental Stressor Maps
	file shape_file_NoiseContour_night <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Environmental Stressors/Noise/PDOK_NoiseMap2016_Lnight_RDNew_clipped.shp");
	file shape_file_NoiseContour_day <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Environmental Stressors/Noise/PDOK_NoiseMap2016_Lden_RDNew_clipped.shp");
//    file Tiff_file_PM2_5 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Environmental Stressors/Noise/PM2_5_RDNew_clipped.tif");
    bool display_air_poll <- true;
    
    
//  loading routing code
    file Rcode_foot_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/Routing/OSRM_foot.R");
    file Rcode_car_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/Routing/OSRM_car.R");
    file Rcode_bike_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/Routing/OSRM_bike.R");

//  loading agent population attributes
    int nb_humans <- 150;
//    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop.csv", ";", string, true);
    file Rcode_agent_subsetting <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/ABM_models/GAMA_Models/External_Scripts_for_GAMA_Models/Subsetting_Synthetic_AgentPop_for_GAMA.R");
    csv_file Synth_Agent_file;
    
//  loading agent schedules   /// need more robust method for schedules based on HETUS data
	text_file kids_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/kids_schedule.txt");
	text_file youngadult_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/youngadult_schedule.txt");
	text_file adult_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/adult_schedule.txt");
	text_file elderly_schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/elderly_schedule.txt");

// Global variables transport
	map<string, float> travelspeed <- create_map(["walk", "bike", "car"], [1.4, 3.33, 11.11]); /// meters per seconds (5km/h, 12km/h, 40km/h )
	map<string, float> transport_costs<- create_map(["walk", "bike", "car"], [0, 0.01, 0.2 ]);  // Euros per 1km     												// needs robust methodology
	map<string, float> transport_safety <- create_map(["walk", "bike", "car"], [0.05, 0.66, 0.1 ]);  //Percent of serious traffic accidents (SWOV)    				// needs robust methodology
	float per_car_owners	<- 0.5;
	
// Global variables exposure
	map<string, float> inhalation_rate <- create_map(["walk", "bike", "normal"], [25.0, 40.0, 15.0]); /// breaths per minute  										// needs robust methodology
	map<string, float> Noise_Filter <- create_map(["indoor", "car", "walk", "bike"], [0.20, 0.40, 1, 1]); /// percentage of Noise that remains (is not filtered)							// needs robust methodology
	map<string, float> AirPollution_Filter <- create_map(["indoor", "car",  "walk", "bike"], [0.60, 0.80, 1, 1]); /// percentage of Air Pollution that remains (is not filtered)			// needs robust methodology
	
	grid Perceivable_Environment file: rasterfile_walkability{
		int csvindex;
		float pop_density;
		float retail_density;
		float greenCoverage ;
		float public_Transport_density;
		float road_intersection_density;
		list datalist;
	}	

// behaviour model parameters
	float affordability_weight <- 0.7;
	float infrastructure_quality_weight <- 0.8;
	float pop_density_weight_walk <- 0.8;
	float retail_density_weight_walk <- 0.8;
	float greenCoverage_weight_walk <- 0.8;
	float public_Transport_density_weight_walk <- 0.8;
	float road_intersection_density_weight_walk <- 0.8;
	float pop_density_weight_bike <- 0.8;
	float retail_density_weight_bike <- 0.8;
	float greenCoverage_weight_bike <- 0.8;
	float public_Transport_density_weight_bike <- 0.8;
	float road_intersection_density_weight_bike <- 0.8;
	float traveltime_weight <- 0.5;
	map<string,float> tripdistance_weight_age_walk <- create_map(["minor", "teenager", "youngadult", "adult", "senior", "elderly"], [0.3, 3.33, 11.11, 0.4,0.5]);
	map<string,float> tripdistance_weight_age_bike <- create_map(["minor", "teenager", "youngadult", "adult", "senior", "elderly"], [0.3, 3.33, 11.11, 0.4,0.5]);
	map<string,float> tripdistance_weight_age_car <- create_map(["minor", "teenager", "youngadult", "adult", "senior", "elderly"], [0.3, 3.33, 11.11, 0.4,0.5]);
	map<string,float> tripdistance_weight_BMI_walk <- create_map(["normal", "overweight"], [0.3, 3.33]);
	map<string,float> tripdistance_weight_BMI_bike <- create_map(["normal", "overweight"], [0.3, 3.33]);
	map<string,float> tripdistance_weight_BMI_car <- create_map(["normal", "overweight"], [0.3, 3.33]);


    init  {
        write "setting up the model";
        do startR;
        write R_eval("nb_humans = " + to_R_data(nb_humans));
        write R_eval("filename = " + to_R_data("Population/Agent_pop.csv"));
        loop s over: Rcode_agent_subsetting.contents{ 			/// the R code creates a csv file of a random subset of the synthetic agent population of specified size "nb_humans"
							unknown a <- R_eval(s);
						}
		Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_GAMA.csv", ";", string, true); // this is the file that was created by the R code
		Restaurants <- shape_file_Restaurants where (each.location != nil);
		Entertainment <- shape_file_Entertainment where (each.location != nil);	
		create Homes from: shape_file_Residences with: [Neighborhood:: read('nghb_cd')];
		create Noise_day from: shape_file_NoiseContour_day with: [Decibel :: float(read('bovengrens'))] ;
        create Humans from: Synth_Agent_file with:[Agent_ID :: read('Agent_ID'), Neighborhood :: read('neighb_code'), 
	        age:: int(read('age')), sex :: read('sex'), migrationbackground :: read('migrationbackground'),
	        hh_single :: int(read('hh_single')), is_child:: int(read('is_child')), has_child:: int(read('has_child')), 
        	current_edu:: read('current_education'), absolved_edu:: read('absolved_education'), BMI:: read('BMI'), scheduletype:: read('scheduletype')]; // careful: column 1 is has the index 0 in GAMA      //
    	matrix walkability_measures <- matrix(walkability_data);
    	ask Perceivable_Environment{
    		write "id gridvalue: " + int(self.grid_value);
    		datalist <- rows_list(walkability_measures) at (int(self.grid_value)-1);
    		write datalist;
			pop_density <- float(datalist at 1);
			write pop_density;
			retail_density <-  float(datalist at 2);
			greenCoverage <-  float(datalist at 3);
			public_Transport_density <-  float(datalist at 4);
			road_intersection_density <-  float(datalist at 5);
    	}
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
	int age;					// integer age 0- 100
	string sex;  				// female, male
	string migrationbackground; // Dutch, Western, Non-Western
	int hh_single; 				// 1 = yes, 0 = no
	int is_child;				// 1 = yes, 0 = no
	int has_child;				// 1 = yes, 0 = no
	string current_edu;			// "high", "medium", "low", "no_current_edu"
	string absolved_edu;		// "high", "medium", "low", 0
	string BMI; 				//"underweight", "normal_weight", "moderate_overweight", "obese"
	string scheduletype;
	string agegroup;    /// 
	string weightgroup; /// "normal", "overweight"
	string incomegroup; /// "low", "middle", "high"																	// needs robust methodology

	
	/// destination locations
	geometry residence;
	geometry workplace;
	geometry school;
	geometry university;
	geometry kindergarden;
	geometry supermarket;
			
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
	int path_memory;
	int new_route;
	int make_modalchoice;
	geometry route_eucl_line;
	float trip_distance ;

	/// saved routes (for efficiency)
	path homeTOwork;
	string homeTOwork_mode;
	geometry homeTOwork_geometry;
	float homeTOwork_duration;
	path workTOhome;
	geometry workTOhome_geometry;
	path homeTOuni;
	string homeTOuni_mode;
	geometry homeTOuni_geometry;
	float homeTOuni_duration;
	path uniTOhome;
	geometry uniTOhome_geometry;
	path homeTOschool;
	string homeTOschool_mode;
	geometry homeTOschool_geometry;
	float homeTOschool_duration;	
	path schoolTOhome;
	geometry schoolTOhome_geometry;
	path homeTOsuperm;
	string homeTOsuperm_mode;
	geometry homeTOsuperm_geometry;
	float homeTOsuperm_duration;	
	path supermTOhome;
	geometry supermTOhome_geometry;
	path homeTOkinderga;
	string homeTOkinderga_mode;
	geometry homeTOkinderga_geometry;
	float homeTOkinderga_duration;	
	path kindergaTOhome;
	geometry kindergaTOhome_geometry;
	
	/// exposure variables
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
	
	//////// TRANSPORT BEHAVIOUR ///////////////
	bool probabilistic_choice <- true;
	predicate travelTOdestination <- new_predicate("travelTOdestination");
	
	/// Transport Behaviour: Behavioural Factors///
	// there are also convenience and affordability, but they are defined inside the model
	int safety;
	int norm_abidence;
	map<string, float> assumed_traveltime  <- create_map(["traveltime_bike", "traveltime_walk", "traveltime_car"], [0.0, 0.0, 0.0]);
	map<string, float> assumed_quality_infrastructure <- create_map(["pop_density", "retail_density", "greenCoverage", "public_Transport_density", "road_intersection_density"], [0.0, 0.0, 0.0, 0.0, 0.0]);	
	map<string, float> affordability <- create_map(["perc_budget_bike", "perc_budget_walk", "perc_budget_car"], [0.0, 0.0, 0.0]);
	float budget <- rnd (800.0 , 5000.0); // Euros per month   								// needs robust methodology
	
	/// Transport Behaviour: Behavioural Factors Weights///
	float infrastructure_quality_weight <- 0.8;
	float safety_weight;
	float affordability_weight <- 0.7;

	/// Transport Behaviour: Behavioural Constraints///
	int car_owner <- 0;																		// needs robust methodology
	map<string,int> distance_willing_travel  ;												// needs robust methodology
	
	/// Transport Behaviour: Utilities ///
	float driving_utility;
	float biking_utility;
	float walking_utility;
	float public_transport_utility;
	
	
	
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
		  residence <- one_of(Homes where ((each.Neighborhood = self.Neighborhood) and each.location != nil)) ;
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
       	  if(schedule contains "groceries_shopping"){
				supermarket <-  closest_to(shape_file_Supermarkets, self.location) ;
       	  }       	     	
       	  activity <- "perform_activity";
       	  if(age > 20){
       	  	if(flip(per_car_owners)){
       	  		car_owner <- 1;
       	  	}
       	  }
       	  
       	  	if (age < 8){
       	  		agegroup <- "minor";
       	  	}
       	  	else if (age > 8 and age<= 17){
       	  		agegroup <- "teenager";
       	  	}    
       	  	if(age > 8 and age<= 17){
       	  		agegroup <-  "youngadult";
       	  	}
       	  	if(age < 50 and age > 17){
       	  		agegroup <- "adult";
       	  	}
       	  	else if(age >= 50 and age < 70){
       	  		agegroup <- "senior";
       	  	}
       	  	else if(age >= 70){
       	  		agegroup <- "elderly";
       	  	}

			if(BMI = "moderate_overweight" or BMI = "obese" ){
			weightgroup <- "overweight";
			}
			else{
			weightgroup <- "normal";	
			}
			
//			string incomegroup; same for incomegroup


       	  if(BMI != "moderate_overweight" and BMI != "obese"){
       	  	if(age <= 8){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [600, 0, 0 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	  	 if(age > 8 and age<= 17){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1000, 2000, 0 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	  	if(age < 50 and age > 17){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1500, 6000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	  	else if(age >= 50 and age < 70){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1500, 3000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	  	else if(age >= 70){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1000, 2000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	  }
       	  else{
       	  	distance_willing_travel <- create_map(["walk", "bike", "car"], [1000, 2000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  }
       	  do startR;
	}
	
/////// defining the Human transition functions (behaviour and exposure) //////////
	reflex schedule_manager when: (((current_date.minute mod 10) = 0) or (current_date.minute = 0)){
		 current_activity <- schedule[(int((current_date.minute/10) + (current_date.hour * 6)))];
		 if((int(current_date.minute) != 0) or (int(current_date.hour) != 0)){
		 	former_activity <- schedule[int(((current_date.minute/10) + (current_date.hour * 6))-1)];
		 }
		 else{
		 	former_activity <- last(schedule) ;
		 }
		 if(current_activity != former_activity){
		 	if(current_activity = "work"){
				destination_activity <- workplace;
				if(homeTOwork != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOwork;
					track_geometry <- homeTOwork_geometry;
					modalchoice <- homeTOwork_mode;
					track_duration <- homeTOwork_duration;
					path_memory <- 1;
					write "saved pathway";
				}		 		
		 	}
		 	else if(current_activity = "school"){
		 		destination_activity <- school;
		 		if(homeTOschool != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOschool;
					track_geometry <- homeTOschool_geometry;
					modalchoice <- homeTOschool_mode;
					track_duration <- homeTOschool_duration;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "university"){
		 		destination_activity <- university;
		 		if(homeTOuni != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOuni;
					track_geometry <- homeTOuni_geometry;
					track_duration <- homeTOuni_duration;
					modalchoice <- homeTOuni_mode;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "groceries_shopping"){
		 		destination_activity <- supermarket;
		 		if(homeTOsuperm != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOsuperm;
					track_geometry <- homeTOsuperm_geometry;
					track_duration <- homeTOsuperm_duration;
					modalchoice <- homeTOsuperm_mode;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "kindergarden"){
		 		destination_activity <- kindergarden;
		 		if(homeTOkinderga != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOkinderga;
					track_geometry <- homeTOkinderga_geometry;
					track_duration <- homeTOkinderga_duration;
					modalchoice <- homeTOkinderga_mode;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "sleeping" or current_activity = "at_Home"){
		 		destination_activity <- self.residence.location;
		 		if(workTOhome != nil and former_activity = "work"){
					track_path <- workTOhome;
					track_geometry <- workTOhome_geometry;
					modalchoice <- homeTOwork_mode;
					track_duration <- homeTOwork_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(schoolTOhome != nil and former_activity = "school"){
					track_path <- schoolTOhome;
					track_geometry <- schoolTOhome_geometry;
					modalchoice <- homeTOschool_mode;
					track_duration <- homeTOschool_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(uniTOhome != nil and self.location = university.location){
					track_path <- uniTOhome;
					track_geometry <- uniTOhome_geometry;
					modalchoice <- homeTOuni_mode;
					track_duration <- homeTOuni_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(supermTOhome != nil and self.location = supermarket.location){
					track_path <- supermTOhome;
					track_geometry <- supermTOhome_geometry;
					modalchoice <- homeTOsuperm_mode;
					track_duration <- homeTOsuperm_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(kindergaTOhome != nil and self.location = supermarket.location){
					track_path <- kindergaTOhome;
					track_geometry <- kindergaTOhome_geometry;
					modalchoice <- homeTOkinderga_mode;
					track_duration <- homeTOkinderga_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 	}
		 	else if(current_activity = "entertainment" ){
		 		destination_activity <- one_of(Entertainment);
		 		loop while: destination_activity = nil {
		 			destination_activity <- one_of(Entertainment);
		 		}
		 	}
		 	else if(current_activity = "eat" ){
		 		if (one_of(Restaurants inside circle(500, self.location)) != nil){
		 			destination_activity <- one_of(Restaurants inside circle(500, self.location));
		 		}
		 		else{
		 			destination_activity <- closest_to(Restaurants, self.location);
		 		}
		 		loop while: destination_activity = nil {
		 			destination_activity <- one_of(Restaurants);
		 		}
		 	}
		 	else if(current_activity = "social_life" ){
		 		destination_activity <- one_of(shape_file_Residences);
		 	}
		 	write "Current Activity: " + current_activity + "; Former Activity: " + former_activity;
		 	if(point(destination_activity.location) != point(self.location)){
		 		route_eucl_line <- line(container(point(self.location), point(destination_activity.location)));
		 		trip_distance <- (self.location distance_to destination_activity);
		 		if(path_memory != 1){
		 			traveldecision <- 1;
		 		}
		 		else if(path_memory = 1){
		 			 activity <- "commuting";
		 			 track_path <-  path((track_geometry add_point(point(destination_activity))));  
		 		}
		 		path_memory <- 0;
		 	}		 
		 	else{
		 		activity <-"perform_activity";
		 		traveldecision <- 0;
		 	}
		 }
	}
	perceive Env_Activity_Affordance_Travel target:(Perceivable_Environment where (each intersects route_eucl_line))  when: traveldecision = 1 {
    	myself.traveldecision <- 0;	
    	myself.make_modalchoice <- 1;
    	ask myself{
	   		assumed_quality_infrastructure <- (["pop_density"::mean(myself.pop_density), "retail_density"::mean(myself.retail_density), 
	   			"greenCoverage"::mean(myself.greenCoverage), "public_Transport_density"::mean(myself.public_Transport_density), 
	   			"road_intersection_density"::mean(myself.road_intersection_density)]);
			affordability <-["perc_budget_bike":: ((transport_costs["bike"] * (trip_distance/1000) )/((budget/31)-20)), 
	   		"perc_budget_walk"::((transport_costs["walk"] * (trip_distance/1000) )/((budget/31)-20)),
	   		"perc_budget_car":: ((transport_costs["car"] * (trip_distance/1000) )/((budget/31)-20))]; 
	   		assumed_traveltime <- ["traveltime_bike"::(trip_distance/travelspeed["bike"]), "traveltime_walk"::(trip_distance/travelspeed["walk"]), "traveltime_car"::(trip_distance/travelspeed["car"])]; 
	   	}    	
    }
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
	reflex routing when:  new_route = 1  {
		  activity <- "commuting";
		  new_route <- 0;
		/// routing through OSRM via R interface
		unknown a <-  R_eval("origin = " + to_R_data(container(self.location CRS_transform("EPSG:4326"))));
		unknown a <-  R_eval("destination = " + to_R_data(container(point(destination_activity.location) CRS_transform("EPSG:4326"))));	
		if(modalchoice = "walk"){
		 	loop s over: Rcode_foot_routing.contents{
				unknown a <- R_eval(s);
//							write "R>" + a;
			}
		 	}
		else if(modalchoice = "bike"){
		 	loop s over: Rcode_bike_routing.contents{
				unknown a <- R_eval(s);
			}
		 	}
		else if(modalchoice = "car") {
		 	loop s over: Rcode_car_routing.contents{
				unknown a <- R_eval(s);
			}
		 }
		list<point> track <- list(R_eval("track_points"));
		track_geometry <- to_GAMA_CRS(line(track),  "EPSG:4326") add_point(point(destination_activity));
		track_path <-  path(track_geometry);     	  
//		write "trackgeom:"+ track_geometry + "destination: " + destination_activity;
		track_duration <- float(list(R_eval("route$duration"))[0]);  ///minutes
		float track_length <- float(list(R_eval("route$distance"))[0]);	/// meters
		if(current_activity = "work" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOwork <- track_path;
				homeTOwork_mode <- modalchoice;
				homeTOwork_geometry <- track_geometry ;
				homeTOwork_duration <- track_duration;
				workTOhome_geometry <- line(reverse(container(geometry_collection(homeTOwork_geometry)))) add_point(residence.location);
				workTOhome <- path(workTOhome_geometry);
				}
		else if(current_activity = "school" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOschool <- track_path;
				homeTOschool_mode <- modalchoice;
				homeTOschool_geometry <- track_geometry ;
				homeTOschool_duration <- track_duration;
				schoolTOhome_geometry <- line(reverse(container(geometry_collection(homeTOschool_geometry)))) add_point(residence.location);
				schoolTOhome <- path(schoolTOhome_geometry);
			}
		else if(current_activity = "university" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOuni <- track_path;
				homeTOuni_mode <- modalchoice;
				homeTOuni_geometry <- track_geometry ;
				homeTOuni_duration <- track_duration;
				uniTOhome_geometry <- line(reverse(container(geometry_collection(homeTOuni_geometry)))) add_point(residence.location);
				uniTOhome <- path(uniTOhome_geometry);
			}
		else if(current_activity = "kindergarden" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOkinderga <- track_path;
				homeTOkinderga_mode <- modalchoice;
				homeTOkinderga_geometry <- track_geometry ;
				homeTOkinderga_duration <- track_duration;
				kindergaTOhome_geometry <- line(reverse(container(geometry_collection(homeTOkinderga_geometry)))) add_point(residence.location);
				kindergaTOhome <- path(kindergaTOhome_geometry);
			}
		else if(current_activity = "groceries_shopping" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOsuperm <- track_path;
				homeTOsuperm_mode <- modalchoice;
				homeTOsuperm_geometry <- track_geometry ;
				homeTOsuperm_duration <- track_duration;
				supermTOhome_geometry <- line(reverse(container(geometry_collection(homeTOsuperm_geometry)))) add_point(self.residence.location);
				supermTOhome <- path(supermTOhome_geometry);
		}			
	}
//	reflex any_activity when: activity = "perform_activity" and current_activity = "name of activity"{
//		e.g. the activity could have an impact on health (sports...)
//	}
	reflex at_Place_exposure when: activity = "perform_activity"{
		activity_PM10 <- (sum((Environment_stressors overlapping self) collect each.AirPoll_PM10)) * inhalation_rate["normal"] * AirPollution_Filter["indoor"];
		activity_Noise <- (sum((Noise_day overlapping self) collect each.Decibel)) * Noise_Filter["indoor"];
		hourly_PM10 <- hourly_PM10 + activity_PM10;
		hourly_Noise <- hourly_Noise + activity_Noise;
	}
	
    reflex commuting when: activity = "commuting"{
		do follow path: self.track_path speed: travelspeed[modalchoice];
		if((self.location = self.destination_activity.location)){
			self.location <- destination_activity.location;
//			write "arrived";
			activity <- "perform_activity";
    		activity_PM10 <- (sum((Environment_stressors overlapping self.track_geometry) collect each.AirPoll_PM10)/( length(Environment_stressors overlapping self.track_geometry) + 1)) * inhalation_rate[modalchoice] * track_duration * AirPollution_Filter[modalchoice];
			activity_Noise <- (sum((Noise_day overlapping self.track_geometry) collect each.Decibel)/(length(Noise_day overlapping self.track_geometry) +1) )  * track_duration * Noise_Filter[modalchoice];
    		hourly_PM10 <- hourly_PM10 + activity_PM10;
			hourly_Noise <- hourly_Noise + activity_Noise;
    		if(modalchoice = "bike"){
    			bike_exposure <- bike_exposure + track_duration;
    		}
    		 else if(modalchoice = "walk"){
    			walk_exposure <- walk_exposure + track_duration;
    		}
    		if(modalchoice = "car"){
    			ask (Environment_stressors overlapping track_geometry) {
					AirPoll_PM2_5 <- AirPoll_PM2_5 + 10.0;
				}
    		}
    	}
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
    		else if(modalchoice =  "car"){
    			draw cube(60) color: #fuchsia;
    		}
    	}
    	
    }
}


grid Environment_stressors cell_width: 100 cell_height: 100  parallel: true{
	float AirPoll_PM2_5 <- 0.0;
	float AirPoll_PM10 <- 0.0;
	float AirPoll_NO2 <- 0.0;
	float Noise_Decibel_night;
	float Noise_Decibel_day;
	init{
		if(flip(0.5)){
				AirPoll_PM2_5 <- gauss({20,6.6});
				AirPoll_PM10 <- gauss({20,5.6}); 
				AirPoll_NO2 <- gauss({10,2.6});
		}
	}
	
//	rgb color <- #green update: rgb(255 *(AirPoll_PM10/30.0) , 255 * (1 - (AirPoll_PM10/30.0)), 0.0);
	reflex atmospheric_dispersion when: (((current_date.minute mod 10) = 0) or (current_date.minute = 0)){
		if(AirPoll_PM2_5 != 0){
			diffuse var: AirPoll_PM2_5 on: Environment_stressors proportion: 0.3 radius: 1;
			AirPoll_PM2_5 <- AirPoll_PM2_5 * 0.3;
		}
	}
	
}

//grid Perceivable_Environment cell_width: 100 cell_height: 100 parallel: true{
//	float bikability <- gauss({10,3.6});
//	float walkability <- gauss({10,3.6});
//	float drivability <- gauss({10,3.6});
//}


experiment TransportAirPollutionExposureModel type: gui {
	/** Insert here the definition of the input and output of the model */
	parameter "Number of human agents" var: nb_humans min: 10 max: 10000  category: "Human attributes";
	parameter "Share of adult car owners" var: per_car_owners min: 0.0 max: 1.0 category: "Human attributes";	
//	parameter "Visualize Air Pollution Field" var:display_air_poll among: [true, false] type:bool;
	
	output {
		layout horizontal([1::6000,0::4000]) tabs: false;
	
    	display stats type: java2D synchronized: true {
        	overlay position: {0, 0} size: {1, 0.05} background: #black  border: #black {
    	  	  		draw "Model Time: " + current_date color: #white font: font("SansSerif", 17) at: {40#px, 30#px};
				}
  	      chart "Transport Mode distribution" type: histogram background: #black color: #white axes: #white size: {0.5,0.5} position: {0.5, 0.5} label_font: font("SansSerif", 12){
 		       	data "walk" value: Humans count (each.modalchoice = "walk" and each.activity = "commuting") color:#green;
	        	data "bike" value: Humans count (each.modalchoice = "bike" and each.activity = "commuting") color:#blue;
   		     	data "car" value: Humans count (each.modalchoice = "car" and each.activity = "commuting") color:#fuchsia;
   		     	data "not travelling" value: Humans count (each.activity = "perform_activity") color:#yellow;
     	   }
			chart "Mean Noise Exposure" type: scatter x_label: (string(int(step/60))) + " Minute Steps"  y_label: "Decibel" background: #black color: #white axes: #white size: {0.5,0.45} position: {0, 0.05} label_font: font("SansSerif", 12){
					data "Noise exposure" value: mean(Humans collect each.activity_Noise) color: #red marker: false style: line;
			}
			chart "Mean PM10 Exposure" type: scatter x_label: (string(int(step/60))) + " Minute Steps" y_label: "µg" background: #black color: #white axes: #white size: {0.5,0.45} position: {0.5, 0.05} label_font: font("SansSerif", 12){
					data "PM10 exposure" value: mean(Humans collect each.activity_PM10) color: #red marker: false style: line;
			}
			chart "Agent Age Distribution" type: histogram background: #black color: #white axes: #white size: {0.5,0.25} position: {0, 0.5} {
				data "0-10" value: Humans count (each.age <= 10) color:#teal;
				data "11-20" value: Humans count ((each.age > 10) and (each.age <= 20)) color:#teal;
				data "21-30" value: Humans count ((each.age > 20) and (each.age <= 30)) color:#teal;
				data "31-40" value: Humans count ((each.age > 30) and (each.age <= 40)) color:#teal;
				data "41-50" value: Humans count ((each.age > 40) and (each.age <= 50)) color:#teal;
				data "51-60" value: Humans count ((each.age > 50) and (each.age <= 60)) color:#teal;
				data "61-70" value: Humans count ((each.age > 60) and (each.age <= 70)) color:#teal;
				data "71-80" value: Humans count ((each.age > 70) and (each.age <= 80)) color:#teal;
				data "81 or" value: Humans count (each.age > 81) color:#teal;
			}
			chart "Agent Sex Distribution" type: histogram background: #black color: #white axes: #white size: {0.5,0.25} position: {0, 0.75} label_font: font("SansSerif", 12){
				data "male" value: Humans count (each.sex = "male") color:#teal;
				data "female" value: Humans count (each.sex = "female") color:#teal ;
			}
			
  		 }
  		 display map type:opengl {
   		 	graphics background refresh: false{
    			draw shape color: #black;
    		}
       		graphics Buildings refresh: false{
    			draw shape_file_buildings color: #firebrick;
    			draw shape_file_buildings2 color: #firebrick;
    			draw shape_file_buildings3 color: #firebrick;
			}
			graphics Streets refresh: false{
    			draw shape_file_streets color: #aqua;
			}
			graphics GreenSpace refresh: false{
    			draw shape_file_greenspace color: #green;
			}
       		species Humans aspect: base ;
//     	  	grid Environment_stressors elevation: (AirPoll_PM2_5 * 20.0) grayscale: true triangulation: true transparency: 0.7;
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
        	 overlay position: {0, 0, 0} size: {180 #px, 130#px} background: #black rounded: false transparency: 0.0 {
                float y <- 30#px;
                loop type over: color_per_type.keys  {   
                	draw square(10#px) at: { 20#px, y} color: color_per_type[type] border: #white;
                	draw square(10#px) at: { 20#px, y} color: color_per_type[type] border: #white;
                	draw square(10#px) at: { 20#px, y} color: color_per_type[type] border: #white;
                	draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);		// this might look confusing. Unfortunately overlay transparency is automatically set at 0.75 (highly transparent) and that cannot be changed.
                    draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);		// this makes a legend hardly readable. Therefore I draw it multiple times above each other for stronger colors).
                    draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);
                    draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);
                    y <- y + 25#px;
                }
            }    
   		 }
    }
}




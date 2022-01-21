/**
* Name: TransportAirPollutionExposureModel
* Author: Tabea Sonnenschein
* Description:
* Tags: Urban Health; 
*/

model TransportAirPollutionExposureModel

import "Transport Air Pollution Exposure Model_calibration.gaml"
  
global skills: [RSkill]{
	/** Insert the global definitions, variables and actions here */
	float affordability_weight <- 0.7;
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
	
	// objective function and metrics
	int n_diff_modal_choices <- 0;
	float n_displacements_calibration <- 0.001;	// better something small to avoid division by zero
	matrix<float> confusion_matrix <- matrix ([[0.001, 0.001, 0.001], [0.001, 0.001, 0.001], [0.001, 0.001, 0.001]]) ;
   	list<float> precision <- [0.0, 0.0, 0.0];
   	list<float> recall <- [0.0, 0.0, 0.0];
   	list<float> f1 <- [0.0, 0.0, 0.0];
   	float weightedf1 <- 0.0;
   	list<int> n_sample <- [0, 0, 0];
		
	string path_data <- "C:/Users/Marco/Documents/ABM_thesis/Data/";
	string path_workspace <- "C:/Users/Marco/Documents/ABM_thesis/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/";
//	string path_data <- "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Calibration/";
//	string path_workspace <- "C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/";
			
	//	loading the spatial built environment
	file shape_file_buildings <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp");
	file shape_file_buildings2 <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp");
	file shape_file_buildings3 <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp");
	// file shape_file_streets <- shape_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/cars/Car Traffic_RDNew.shp");
    file shape_file_streets <- shape_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/Amsterdam_roads_RDNew.shp");
    file shape_file_greenspace <- shape_file(path_data+"Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew_window.shp");
	// file shape_file_Residences <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp");    
    file shape_file_Residences <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Residences_PC4_RDNew.shp");    
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
    file rasterfile_walkability <- grid_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/walkability_grid.tif");
    csv_file walkability_data <- csv_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/walkability_measures.csv", ",", string); 
    //	columnnames:  "popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "Intid"
    
    
	//  loading routing code
    file Rcode_foot_routing <- text_file(path_workspace+"OSRM_foot.R");
    file Rcode_car_routing <- text_file(path_workspace+"OSRM_car.R");
    file Rcode_bike_routing <- text_file(path_workspace+"OSRM_bike.R");    
	
	// Global variables transport
	map<string, float> travelspeed <- create_map(["walk", "bike", "car"], [1.4, 3.33, 11.11]); /// meters per seconds (5km/h, 12km/h, 40km/h )
	map<string, float> transport_costs<- create_map(["walk", "bike", "car"], [0, 0.01, 0.2 ]);  // Euros per 1km     												// needs robust methodology
	map<string, float> transport_safety <- create_map(["walk", "bike", "car"], [0.05, 0.66, 0.1 ]);  //Percent of serious traffic accidents (SWOV)    				// needs robust methodology
	float per_car_owners	<- 0.5;
	
	grid Perceivable_Environment file: rasterfile_walkability{
		int csvindex;
		float pop_density;
		float retail_density;
		float greenCoverage ;
		float public_Transport_density;
		float road_intersection_density;
		list datalist;
	}	
	
	float seed_value <- int(self) + 1.0;
	int nb_humans <- 1000;	// make sure it's the same size of the subset ODiN pop!
	
	csv_file file_subset_ODiN <- csv_file(path_data+"Amsterdam/Calibration/Subset_ODiN.csv", ";", string, true);
	file pc4_AMS_file <- shape_file(path_data+"Amsterdam/Calibration/AMS-PC4_polygons/AMS-PC4_polygons.shp");	// loading Amsterdam locations for moving the agents
    float start_time <- machine_time;
   	
   	list results;
	
    init  {
        write "setting up the model";
		
		// import the agentified elements
		Restaurants <- shape_file_Restaurants where (each.location != nil);
		Entertainment <- shape_file_Entertainment where (each.location != nil);		
		create Homes from: shape_file_Residences with: [Neighborhood:: read('PC4')];
		
		// polygons for displacements
        create PC4_polygons from: pc4_AMS_file with: [Neighborhood:: read('PC4')];	
        	
	    // humans for calibration
	    create Humans from: file_subset_ODiN with:[Agent_ID :: string(read('agent_ID')),
	    	Neighborhood :: read('postcode_home'),
	    	hh_single :: int(read('hh_single')),
	    	has_child:: int(read('havechild')), 
	        absolved_edu:: read('absolved_edu'),
	        ODIN_locations_str:: string(read('lookup')),
	        ODIN_modal_choices_str:: string(read('modal_choices')),
	        BMI:: string(read('BMI')),
	        income_household:: int(read('income_household'))
	        ]; // careful: column 1 is has the index 0 in GAMA      //
		
		matrix walkability_measures <- matrix(walkability_data);
    	ask Perceivable_Environment{
    		//write "id gridvalue: " + int(self.grid_value);
    		datalist <- rows_list(walkability_measures) at (int(self.grid_value)-1);
    		//write datalist;
			pop_density <- float(datalist at 1);
			//write pop_density;
			retail_density <-  float(datalist at 2);
			greenCoverage <-  float(datalist at 3);
			public_Transport_density <-  float(datalist at 4);
			road_intersection_density <-  float(datalist at 5);
    	}
    }
    float step <- 10 #mn;  /// #mn minutes #h hours  #sec seconds #day days #week weeks #year years
    //date starting_date <- date([2019,1,1,6,0,0]); //correspond the 1st of January 2019, at 6:00:00
    date starting_date <- date([2019,1,1,0,0,0]); //correspond the 1st of January 2019, at 00:00:00
    int year;
}

species PC4_polygons {
	string Neighborhood;
}


species Homes{
	string Neighborhood;
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
	string agegroup;    /// 
	string weightgroup; /// "normal", "overweight"
	int income_household;
	string incomegroup; /// "low", "middle", "high"
	
	/// calibration variables
	string ODIN_locations_str;
	list<string> ODIN_locations;
	string ODIN_modal_choices_str;
	list<string> ODIN_modal_choices;
	string current_location;
	string former_location;		
	int counter_modal_choice <- -1;	// to iterate through the list of modal choices, retrieving the one matching the current displacement
	
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
		// postcode schedule 10 mins: convert the postcodes string into a list of postcodes
		string cs <- "";
		loop s over:list(self.ODIN_locations_str) {
			if s!='-' {cs <- cs+s;}
			else {self.ODIN_locations <+ cs; cs <- "";}
		}
		self.ODIN_locations <+ cs;
		
		// initialise the location
		int index_min;
		if (int(current_date.minute)=0) {
			index_min <- 0;
		} else {
			index_min <- int(current_date.minute)/10;
		}
		int index <- int(current_date.hour)*6 + index_min;
		self.former_location<-self.ODIN_locations[index];
		self.current_location<-self.ODIN_locations[index];
		if (self.former_location='outsideAMS'){	// if agent start outside Amsterdam it is initialised with the home postcode instead
			self.location<-(PC4_polygons where (each.Neighborhood = self.Neighborhood))[0].shape;
		} else {
			self.location<-(PC4_polygons where (each.Neighborhood = self.former_location))[0].shape;
		}

		
		// modal choices: convert the string into list
		cs <- "";
		loop s over:list(self.ODIN_modal_choices_str) {
			if s!='-' {cs <- cs+s;}
			else {self.ODIN_modal_choices <+ cs; cs <- "";}
		}
		self.ODIN_modal_choices <+ cs;
		
		activity <- "perform_activity";
		if(age > 20){
			if(flip(per_car_owners)){
				car_owner <- 1;
       	  	}
       	}
       	
       	// old distance_willing_travel TO DELETE
       	if(BMI != "moderate_overweight" and BMI != "obese"){
       		if(age <= 8){
       			distance_willing_travel <- create_map(["walk", "bike", "car"], [600, 0, 0 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	  	if(age > 8 and age<= 17){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1000, 2000, 0 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	  	if(age < 50 and age > 17){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1500, 6000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}else if(age >= 50 and age < 70){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1500, 3000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}else if(age >= 70){
       	  		distance_willing_travel <- create_map(["walk", "bike", "car"], [1000, 2000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	  	}
       	}else{
       	  	distance_willing_travel <- create_map(["walk", "bike", "car"], [1000, 2000, 20000 ]);  //meters, need to derive from ODIN..    				// needs robust methodology
       	}
       	

       	// assign age group based on actual age
       	if (self.age<=8){
       		self.agegroup <- "minor";
       	} else if (self.age>=9 and self.age<= 17){
       		self.agegroup <-  "youngadult";
       	} else if(self.age>=18 and self.age<=49){
       		self.agegroup <- "adult";
       	} else if (self.age>=50 and self.age<=69){
       		self.agegroup <- "senior";
       	} else if(self.age>=70){
       		self.agegroup <- "elderly";
       	}
		
		// assign weight group based on BMI
		if(self.BMI="moderate_overweight" or self.BMI="obese" ){
			self.weightgroup <- "overweight";
		} else {
			self.weightgroup <- "normal";	
		}
		
	    // assign bigger income group based on more precise income group
       	if (self.income_household<=2){
       		self.incomegroup <- "low";
       	} else if (self.income_household>=3 and self.income_household<= 5){
       		self.incomegroup <-  "middle";
       	} else if(self.income_household>=6){
       		self.incomegroup <- "high";
       	}
       	
       	do startR;
	}
	
	
	reflex location_manager when: (((current_date.minute mod 10) = 0) or (current_date.minute = 0)){
		// executed every 10 minutes

		// calculate the index to then retrieve	the postcode from the schedule	
		int index_min;
		if (int(current_date.minute)=0) {
			index_min <- 0;
		} else {
			index_min <- int(current_date.minute)/10;
		}
		int index <- int(current_date.hour)*6 + index_min;
		
		// update location variables
		self.current_location <- self.ODIN_locations[index];	// retrieve new location
		if (index!=0) {	// if 00:00 there is no previous yet
			self.former_location <- self.ODIN_locations[index-1];
		}
		
		// displacement management
		if (self.current_location != self.former_location) {	// when there is a location change
			if ((self.current_location != 'outsideAMS') and (self.former_location != 'outsideAMS')) {	// if in Amsterdam -> new trip
				destination_activity <- (PC4_polygons where (each.Neighborhood = self.current_location))[0].shape;	// cast into individual geometry
				traveldecision <- 1; // flag that a new travel decision has to be made
			 	route_eucl_line <- line(container(point(self.location), point(destination_activity.location)));	// calculate trip to new location
			 	trip_distance <- (self.location distance_to destination_activity); // calculate distance to new location
			 	self.counter_modal_choice <- self.counter_modal_choice + 1;	// increment the modal choice counter for the extraction
			} else if ((self.former_location='outsideAMS') and (self.current_location != 'outsideAMS')) {	// if the agent returns from outside Amsterdam, I just update with the new location (no trip)
				self.location <- (PC4_polygons where (each.Neighborhood = self.current_location))[0].shape.location;
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
			
		// filter possible modal choice				
		if(trip_distance <= distance_willing_travel["walk"]){
			if(car_owner = 1){
				modalchoice <- ["car", "walk", "bike"] at ([driving_utility, walking_utility, biking_utility] index_of  max([driving_utility, walking_utility, biking_utility]));	
			}
			else{
				modalchoice <- ["walk", "bike"] at ([walking_utility, biking_utility] index_of  max([walking_utility, biking_utility]));			
			}
		} else if(trip_distance <= distance_willing_travel["bike"]){
			if(car_owner = 1){
				modalchoice <- ["car","bike"] at ([driving_utility, biking_utility] index_of  max([driving_utility, biking_utility]));	
			} else{
				modalchoice <- "bike";	
			}				
		} else{
			if(car_owner = 1){
			 	modalchoice <- "car";
			} else{
				modalchoice <- "bike";	
			}
		}
		
		// calibration		
		if (self.ODIN_modal_choices[counter_modal_choice] in ['walk', 'bike', 'car']) {	// it does not make sense to calibrate on a modal choice not implemented
			n_displacements_calibration <- n_displacements_calibration + 1;
			if (modalchoice = self.ODIN_modal_choices[counter_modal_choice]) {
				// correct prediction
				if (modalchoice='walk') {
					put (confusion_matrix[0, 0]+1) at: {0, 0} in: confusion_matrix;
					n_sample[0] <- n_sample[0]+1;
				} else if (modalchoice='bike') {
					put (confusion_matrix[1,1]+1) at: {1, 1} in: confusion_matrix;
					n_sample[1] <- n_sample[1]+1;
				} else {
					put (confusion_matrix[2, 2]+1) at: {2, 2} in: confusion_matrix;
					n_sample[2] <- n_sample[2]+1;
				}
				write('modal choice correctly predicted');
			} else {
				// wrong prediction
				if (modalchoice='walk') {
					if (self.ODIN_modal_choices[counter_modal_choice]='bike') {
						put (confusion_matrix[1, 0]+1) at: {1, 0} in: confusion_matrix;
						n_sample[1] <- n_sample[1]+1;
					} else { // car
						put (confusion_matrix[2, 0]+1) at: {2, 0} in: confusion_matrix;
						n_sample[2] <- n_sample[2]+1;
					}
				} else if (modalchoice='bike') {
					if (self.ODIN_modal_choices[counter_modal_choice]='walk') {
						put (confusion_matrix[0, 1]+1) at: {0, 1} in: confusion_matrix;
						n_sample[0] <- n_sample[0]+1;
					} else { // car
						put (confusion_matrix[2, 1]+1) at: {2, 1} in: confusion_matrix;
						n_sample[2] <- n_sample[2]+1;
					}
				} else { // modalchoice='car'
					if (self.ODIN_modal_choices[counter_modal_choice]='walk') {
						put (confusion_matrix[0, 2]+1) at: {0, 2} in: confusion_matrix;
						n_sample[0] <- n_sample[0]+1;
					} else { // bike
						put (confusion_matrix[1, 2]+1) at: {1, 2} in: confusion_matrix;
						n_sample[1] <- n_sample[1]+1;
					}
				}
				write("wrong modal choice predicted. Predicted: "+modalchoice+". True label: "+self.ODIN_modal_choices[counter_modal_choice]);
				n_diff_modal_choices <- n_diff_modal_choices + 1;

				precision[0] <- confusion_matrix[0, 0]/(confusion_matrix[0, 0]+confusion_matrix[1, 0]+confusion_matrix[2, 0]);
				precision[1] <- confusion_matrix[1, 1]/(confusion_matrix[0, 1]+confusion_matrix[1, 1]+confusion_matrix[2, 1]);
				precision[2] <- confusion_matrix[2, 2]/(confusion_matrix[0, 2]+confusion_matrix[1, 2]+confusion_matrix[2, 2]);
				
				recall[0] <- confusion_matrix[0, 0]/(confusion_matrix[0, 0]+confusion_matrix[0, 1]+confusion_matrix[0, 2]);
				recall[1] <- confusion_matrix[1, 1]/(confusion_matrix[1, 0]+confusion_matrix[1, 1]+confusion_matrix[1, 2]);
				recall[2] <- confusion_matrix[2, 2]/(confusion_matrix[2, 0]+confusion_matrix[2, 1]+confusion_matrix[2, 2]);
				
				f1[0] <- 2*(precision[0]*recall[0])/(precision[0]+recall[0]);
				f1[1] <- 2*(precision[1]*recall[1])/(precision[1]+recall[1]);
				f1[2] <- 2*(precision[2]*recall[2])/(precision[2]+recall[2]);
				
				weightedf1 <- (f1[0]*n_sample[0] + f1[1]*n_sample[1] + f1[2]*n_sample[2])/(n_sample[0]+n_sample[1]+n_sample[2]);
				//write(confusion_matrix);
				//write('f1: '+weightedf1);
			}
		}
		
		//write string(trip_distance) + " " + modalchoice ;
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
	
    reflex commuting when: activity = "commuting"{
		do follow path: self.track_path speed: travelspeed[modalchoice];
		if((self.location = self.destination_activity.location)){
			self.location <- destination_activity.location;
			activity <- "perform_activity";
    	}
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

experiment HillClimbing type: batch repeat: 1 keep_seed: true until: (current_date.hour=23) and (current_date.minute=50) {
	parameter 'Affordability:' var: affordability_weight min: 0.0 max: 1.0 unit: 'rate every cycle (1.0 means 100%) ' step: 0.1;
	parameter 'Travel time' var: traveltime_weight min: 0.0 max: 1.0 unit: 'rate every cycle (1.0 means 100%) ' step: 0.1;
	method hill_climbing iter_max: 50 maximize: weightedf1;
	
	reflex end_of_runs{
		ask simulations{
			add [affordability_weight, traveltime_weight, weightedf1, (machine_time-start_time), (1-(n_diff_modal_choices/n_displacements_calibration))] to: results;
			write(results);
		}
		save results type: csv to: path_data+"/Amsterdam/Calibration/calibration_results/hill_climbing.csv" rewrite:false;
	}
}

experiment SimulatedAnnealing type: batch repeat: 1 keep_seed: true until: (current_date.hour=23) and (current_date.minute=50) {
	parameter 'Affordability:' var: affordability_weight min: 0.5 max: 0.9 unit: 'rate every cycle (1.0 means 100%) ' step: 0.1;
	parameter 'Travel time' var: traveltime_weight min: 0.5 max: 0.9 unit: 'rate every cycle (1.0 means 100%) ' step: 0.1;
	method annealing temp_init: 100 temp_end: 1 temp_decrease: 0.5 nb_iter_cst_temp: 1 maximize: weightedf1;	
	
	reflex end_of_runs{
		ask simulations{
			add [affordability_weight, traveltime_weight, weightedf1, (machine_time-start_time), (1-(n_diff_modal_choices/n_displacements_calibration))] to: results;
			write(results);
		}
		save results type: csv to: path_data+"/Amsterdam/Calibration/calibration_results/simulated_annealing.csv" rewrite:false;
	}
}

experiment GenericAlgorithm type: batch repeat: 1 keep_seed: true until: (current_date.hour=23) and (current_date.minute=50) {
	parameter 'Affordability:' var: affordability_weight min: 0.5 max: 0.9 unit: 'rate every cycle (1.0 means 100%) ' step: 0.1;
	parameter 'Travel time' var: traveltime_weight min: 0.5 max: 0.9 unit: 'rate every cycle (1.0 means 100%) ' step: 0.1;
	method genetic maximize: weightedf1 pop_dim: 2 crossover_prob: 0.7 mutation_prob: 0.1 nb_prelim_gen: 1 max_gen: 20;
	
	reflex end_of_runs{
		ask simulations{
			add [affordability_weight, traveltime_weight, weightedf1, (machine_time-start_time), (1-(n_diff_modal_choices/n_displacements_calibration))] to: results;
			write(results);
		}
		save results type: csv to: path_data+"/Amsterdam/Calibration/calibration_results/genetic_algorithm.csv" rewrite:false;
	}
}



experiment TransportAirPollutionExposureModel type: gui {
	/** Insert here the definition of the input and output of the model */
	parameter "Number of human agents" var: nb_humans min: 1 max: 10000  category: "Human attributes";
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

        /* 
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
            */
   		 }
   		 
    } 
    
    
    
}



